"""
催款服务 - 处理支付失败挽回流程
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

import config
from app.database import UserRepository, get_db_context
from app.services.email_service import email_service
from app.services.activity_tracker import activity_tracker

logger = logging.getLogger(__name__)


def handle_payment_failed(user_id: int, db: Session) -> dict:
    """
    处理支付失败事件
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        dict: 包含处理结果和状态信息
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        logger.error(f"支付失败处理失败：用户 {user_id} 不存在")
        return {"success": False, "message": "User not found"}
    
    # 更新催款状态
    user.dunning_status = 'past_due'
    
    # 设置催款开始时间（如果是第一次进入催款状态）
    if user.dunning_started_at is None:
        user.dunning_started_at = datetime.utcnow()
    
    # 增加支付失败计数
    user.payment_failed_count += 1
    
    # 根据失败次数设置流失风险等级
    if user.payment_failed_count >= 3:
        user.churn_risk_level = 'high'
    elif user.payment_failed_count >= 2:
        user.churn_risk_level = 'medium'
    else:
        user.churn_risk_level = 'low'
    
    # 设置下次重试时间（7天后）
    user.payment_retry_at = datetime.utcnow() + timedelta(days=7)
    
    # 更新订阅状态为 past_due
    user.subscription_status = 'past_due'
    
    db.commit()
    
    logger.info(
        f"用户 {user_id} 支付失败处理完成: "
        f"dunning_status={user.dunning_status}, "
        f"payment_failed_count={user.payment_failed_count}, "
        f"churn_risk_level={user.churn_risk_level}"
    )
    
    # 记录用户行为
    activity_tracker.log_activity(
        db, user_id, 'payment_failed',
        metadata={
            'failed_count': user.payment_failed_count,
            'churn_risk': user.churn_risk_level
        }
    )
    
    # 触发催款邮件发送
    try:
        send_dunning_email(user_id, db)
    except Exception as e:
        logger.error(f"发送催款邮件失败: {e}")
    
    return {
        "success": True,
        "dunning_status": user.dunning_status,
        "payment_failed_count": user.payment_failed_count,
        "churn_risk_level": user.churn_risk_level,
        "payment_retry_at": user.payment_retry_at.isoformat() if user.payment_retry_at else None
    }


def handle_payment_success(user_id: int, db: Session) -> dict:
    """
    支付成功后重置催款状态
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        dict: 包含处理结果
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        logger.error(f"支付成功处理失败：用户 {user_id} 不存在")
        return {"success": False, "message": "User not found"}
    
    # 只有在用户处于催款状态时才处理
    if user.dunning_status == 'active':
        logger.info(f"用户 {user_id} 不在催款状态，无需重置")
        return {"success": True, "message": "No dunning status to reset"}
    
    # 重置催款状态
    old_status = user.dunning_status
    user.dunning_status = 'active'
    user.dunning_started_at = None
    user.payment_failed_count = 0
    user.payment_retry_at = None
    user.churn_risk_level = 'low'
    
    # 更新订阅状态为 active
    user.subscription_status = 'active'
    
    db.commit()
    
    logger.info(f"用户 {user_id} 催款状态已重置: {old_status} -> active")
    
    # 记录用户行为
    activity_tracker.log_activity(
        db, user_id, 'payment_recovered',
        metadata={
            'previous_status': old_status,
            'failed_count_reset': True
        }
    )
    
    return {
        "success": True,
        "message": "Dunning status reset successfully",
        "previous_status": old_status
    }


def send_dunning_email(user_id: int, db: Session) -> bool:
    """
    发送催款邮件
    
    根据失败次数选择不同的邮件模板:
    - 第1次失败：温和提醒
    - 第2次失败：紧迫提醒
    - 第3次失败：最后通牒+优惠挽回
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        bool: 是否发送成功
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        logger.error(f"催款邮件发送失败：用户 {user_id} 不存在")
        return False
    
    # 确定邮件模板
    failed_count = user.payment_failed_count
    if failed_count >= 3:
        template = 'email/dunning_3.html'
        subject = "Important: Your IMVU Analytics subscription needs attention"
    elif failed_count >= 2:
        template = 'email/dunning_2.html'
        subject = "Action Required: Your IMVU Analytics subscription will expire soon"
    else:
        template = 'email/dunning_1.html'
        subject = "Payment Update Needed - IMVU Analytics"
    
    # 构建邮件内容
    context = {
        'user_email': user.email,
        'username': user.username or user.email.split('@')[0],
        'failed_count': failed_count,
        'retry_date': (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'app_name': config.APP_NAME,
        'app_url': config.APP_BASE_URL,
        'subscription_end_date': user.subscription_end_date.strftime('%Y-%m-%d') if user.subscription_end_date else None,
        # 第3次失败提供8折优惠
        'discount_code': 'RENEW20' if failed_count >= 3 else None,
        'discount_percent': 20 if failed_count >= 3 else None,
    }
    
    try:
        email_service.send_email(
            to_email=user.email,
            subject=subject,
            template_name=template,
            context=context
        )
        logger.info(f"催款邮件已发送至用户 {user_id}，失败次数: {failed_count}")
        return True
    except Exception as e:
        logger.error(f"催款邮件发送失败: {e}")
        return False


def check_expired_dunning(db: Session) -> dict:
    """
    检查超过7天仍支付失败的用户，标记为 canceled
    
    这个函数应该被定时任务调用（例如每天执行一次）
    
    Args:
        db: 数据库会话
    
    Returns:
        dict: 检查结果统计
    """
    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=7)
    
    # 查找超过7天仍处于 past_due 状态的用户
    expired_users = db.query(UserRepository(db).db.query(
        __import__('app.models', fromlist=['User']).User
    )).filter(
        __import__('app.models', fromlist=['User']).User.dunning_status == 'past_due',
        __import__('app.models', fromlist=['User']).User.dunning_started_at < cutoff_date
    ).all()
    
    canceled_count = 0
    for user in expired_users:
        user.dunning_status = 'canceled'
        user.churn_risk_level = 'high'
        canceled_count += 1
        
        # 记录行为
        activity_tracker.log_activity(
            db, user.id, 'dunning_expired',
            metadata={
                'days_in_dunning': (now - user.dunning_started_at).days if user.dunning_started_at else 0,
                'total_payment_failures': user.payment_failed_count
            }
        )
        
        logger.warning(f"用户 {user.id} 催款超时，状态已更新为 canceled")
    
    if canceled_count > 0:
        db.commit()
    
    return {
        "checked_at": now.isoformat(),
        "expired_count": canceled_count,
        "message": f"Processed {canceled_count} expired dunning users"
    }


def get_user_dunning_status(user_id: int, db: Session) -> dict:
    """
    获取用户的催款状态信息
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        dict: 催款状态信息
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return {"exists": False}
    
    return {
        "exists": True,
        "dunning_status": user.dunning_status or 'active',
        "payment_failed_count": user.payment_failed_count or 0,
        "churn_risk_level": user.churn_risk_level or 'low',
        "dunning_started_at": user.dunning_started_at.isoformat() if user.dunning_started_at else None,
        "payment_retry_at": user.payment_retry_at.isoformat() if user.payment_retry_at else None,
        "is_at_risk": user.dunning_status in ['past_due'] or user.churn_risk_level in ['medium', 'high'],
        "needs_attention": user.dunning_status == 'past_due'
    }


def schedule_dunning_check():
    """
    设置定时任务检查过期的催款状态
    
    应该在应用启动时调用
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.database import get_db_context
    
    scheduler = BackgroundScheduler()
    
    def run_check():
        with get_db_context() as db:
            try:
                result = check_expired_dunning(db)
                logger.info(f"催款状态检查完成: {result['message']}")
            except Exception as e:
                logger.error(f"催款状态检查失败: {e}")
    
    # 每天凌晨2点执行
    scheduler.add_job(run_check, 'cron', hour=2, minute=0)
    scheduler.start()
    
    logger.info("催款状态定时检查任务已启动")
    return scheduler
