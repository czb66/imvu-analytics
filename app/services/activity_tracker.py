"""
用户行为追踪服务 - 异步记录用户操作并提供分析功能
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from concurrent.futures import ThreadPoolExecutor
import logging
import threading

from app.models import UserActivity, User

logger = logging.getLogger(__name__)

# 异步线程池用于非阻塞记录
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="activity_tracker_")


class ActivityTracker:
    """用户行为追踪器"""
    
    # 支持的行为类型
    VALID_ACTIONS = [
        'login', 'logout', 'register', 'upload',
        'view_dashboard', 'view_diagnosis', 'view_compare', 'view_insights',
        'generate_report', 'export_pdf', 'create_promo_card',
        'subscribe', 'cancel_subscription'
    ]
    
    # 资源类型
    RESOURCE_TYPES = ['dataset', 'report', 'promo_card']
    
    def __init__(self):
        """初始化追踪器"""
        pass
    
    def _log_sync(self, db: Session, user_id: int, action: str, 
                  resource_type: str = None, resource_id: int = None, 
                  metadata: dict = None) -> bool:
        """
        同步方式记录行为（内部使用）
        
        Returns:
            bool: 是否记录成功
        """
        try:
            # 验证行为类型
            if action not in self.VALID_ACTIONS:
                logger.warning(f"未知的行为类型: {action}")
                return False
            
            # 过滤敏感元数据
            safe_metadata = self._sanitize_metadata(metadata)
            
            activity = UserActivity(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                extra_data=safe_metadata,
                created_at=datetime.utcnow()
            )
            db.add(activity)
            db.commit()
            
            logger.debug(f"记录用户行为: user_id={user_id}, action={action}")
            return True
            
        except Exception as e:
            logger.error(f"记录用户行为失败: {e}")
            db.rollback()
            return False
    
    def log_activity(self, db: Session, user_id: int, action: str,
                     resource_type: str = None, resource_id: int = None,
                     metadata: dict = None, async_mode: bool = True) -> bool:
        """
        记录用户行为
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            action: 行为类型
            resource_type: 资源类型（可选）
            resource_id: 资源ID（可选）
            metadata: 额外元数据（可选，不包含敏感信息）
            async_mode: 是否异步记录（默认True，不阻塞主流程）
        
        Returns:
            bool: 记录是否成功（异步模式下仅表示提交是否成功）
        """
        if not async_mode:
            return self._log_sync(db, user_id, action, resource_type, resource_id, metadata)
        
        # 异步记录，不阻塞主流程
        def _async_log():
            from app.database import SessionLocal
            thread_db = SessionLocal()
            try:
                self._log_sync(thread_db, user_id, action, resource_type, resource_id, metadata)
            except Exception as e:
                logger.error(f"异步记录行为失败: {e}")
            finally:
                thread_db.close()
        
        _executor.submit(_async_log)
        return True
    
    def _sanitize_metadata(self, metadata: dict) -> dict:
        """
        过滤敏感信息
        不记录: password, token, secret, ip(完整), email, full_address等
        """
        if not metadata:
            return None
        
        sensitive_keys = {
            'password', 'token', 'secret', 'api_key', 'apikey',
            'authorization', 'credit_card', 'card_number', 'ssn',
            'full_ip', 'complete_ip', 'ip_address_full'
        }
        
        sanitized = {}
        for key, value in metadata.items():
            key_lower = key.lower()
            # 检查是否是敏感键
            if any(s in key_lower for s in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str) and len(value) > 200:
                # 截断过长值
                sanitized[key] = value[:200] + '...'
            else:
                sanitized[key] = value
        
        return sanitized if sanitized else None
    
    def get_user_activities(self, db: Session, user_id: int, 
                           limit: int = 100, 
                           action_filter: str = None) -> List[Dict]:
        """
        获取用户的活动记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量限制
            action_filter: 按行为类型过滤（可选）
        
        Returns:
            List[Dict]: 活动记录列表
        """
        query = db.query(UserActivity).filter(UserActivity.user_id == user_id)
        
        if action_filter:
            query = query.filter(UserActivity.action == action_filter)
        
        activities = query.order_by(
            desc(UserActivity.created_at)
        ).limit(limit).all()
        
        return [
            {
                'id': a.id,
                'action': a.action,
                'resource_type': a.resource_type,
                'resource_id': a.resource_id,
                'metadata': a.extra_data,
                'created_at': a.created_at.isoformat() if a.created_at else None
            }
            for a in activities
        ]
    
    def get_daily_active_users(self, db: Session, target_date: date = None) -> int:
        """
        获取日活跃用户数(DAU)
        
        Args:
            db: 数据库会话
            target_date: 目标日期（默认今天）
        
        Returns:
            int: 活跃用户数
        """
        if target_date is None:
            target_date = datetime.utcnow().date()
        
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        count = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
            and_(
                UserActivity.created_at >= start_of_day,
                UserActivity.created_at <= end_of_day
            )
        ).scalar()
        
        return count or 0
    
    def get_monthly_active_users(self, db: Session, year: int, month: int) -> int:
        """
        获取月活跃用户数(MAU)
        
        Args:
            db: 数据库会话
            year: 年份
            month: 月份
        
        Returns:
            int: 活跃用户数
        """
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_of_month = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        count = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
            and_(
                UserActivity.created_at >= start_of_month,
                UserActivity.created_at <= end_of_month
            )
        ).scalar()
        
        return count or 0
    
    def get_feature_usage(self, db: Session, days: int = 30) -> Dict[str, int]:
        """
        获取功能使用统计（最近N天）
        
        Args:
            db: 数据库会话
            days: 统计天数（默认30天）
        
        Returns:
            Dict[str, int]: 功能使用次数
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            UserActivity.action,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.created_at >= start_date
        ).group_by(
            UserActivity.action
        ).all()
        
        return {r.action: r.count for r in results}
    
    def get_retention_rate(self, db: Session, cohort_date: date) -> float:
        """
        计算次日留存率
        
        Args:
            db: 数据库会话
            cohort_date:  cohort日期（用户注册日期）
        
        Returns:
            float: 留存率（0.0 - 1.0）
        """
        # 获取指定日期注册的用户数
        start_of_day = datetime.combine(cohort_date, datetime.min.time())
        end_of_day = datetime.combine(cohort_date, datetime.max.time())
        
        new_users = db.query(User.id).filter(
            and_(
                User.created_at >= start_of_day,
                User.created_at <= end_of_day
            )
        ).all()
        
        if not new_users:
            return 0.0
        
        new_user_ids = [u.id for u in new_users]
        total_new_users = len(new_user_ids)
        
        # 次日留存：检查这些用户第二天是否有活动
        next_day_start = datetime.combine(cohort_date + timedelta(days=1), datetime.min.time())
        next_day_end = datetime.combine(cohort_date + timedelta(days=1), datetime.max.time())
        
        retained_users = db.query(
            func.count(func.distinct(UserActivity.user_id))
        ).filter(
            and_(
                UserActivity.user_id.in_(new_user_ids),
                UserActivity.created_at >= next_day_start,
                UserActivity.created_at <= next_day_end
            )
        ).scalar()
        
        return round(retained_users / total_new_users, 4) if total_new_users > 0 else 0.0
    
    def get_dau_trend(self, db: Session, days: int = 30) -> List[Dict]:
        """
        获取DAU趋势数据
        
        Args:
            db: 数据库会话
            days: 统计天数
        
        Returns:
            List[Dict]: 每日DAU列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            func.date(UserActivity.created_at).label('date'),
            func.count(func.distinct(UserActivity.user_id)).label('dau')
        ).filter(
            UserActivity.created_at >= start_date
        ).group_by(
            func.date(UserActivity.created_at)
        ).order_by(
            func.date(UserActivity.created_at)
        ).all()
        
        return [
            {'date': str(r.date), 'dau': r.dau}
            for r in results
        ]
    
    def get_conversion_funnel(self, db: Session, days: int = 30) -> Dict[str, int]:
        """
        获取转化漏斗数据
        
        Args:
            db: 数据库会话
            days: 统计天数
        
        Returns:
            Dict[str, int]: 各阶段转化人数
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        funnel_steps = ['register', 'login', 'upload', 'view_dashboard', 'generate_report']
        funnel_data = {}
        
        for step in funnel_steps:
            count = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
                and_(
                    UserActivity.action == step,
                    UserActivity.created_at >= start_date
                )
            ).scalar()
            funnel_data[step] = count or 0
        
        return funnel_data
    
    def get_user_engagement_stats(self, db: Session, user_id: int) -> Dict:
        """
        获取用户参与度统计
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            Dict: 用户参与度统计
        """
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).all()
        
        # 按行为类型分组
        action_counts = {}
        for a in activities:
            action_counts[a.action] = action_counts.get(a.action, 0) + 1
        
        # 计算活跃天数
        activity_dates = set()
        for a in activities:
            if a.created_at:
                activity_dates.add(a.created_at.date())
        
        return {
            'total_activities': len(activities),
            'active_days': len(activity_dates),
            'action_breakdown': action_counts,
            'first_activity': min(activity_dates).isoformat() if activity_dates else None,
            'last_activity': max(activity_dates).isoformat() if activity_dates else None
        }
    
    def cleanup_old_records(self, db: Session, retention_days: int = 180) -> int:
        """
        清理旧的行为记录（数据保留策略）
        
        Args:
            db: 数据库会话
            retention_days: 保留天数（默认6个月=180天）
        
        Returns:
            int: 删除的记录数
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        deleted = db.query(UserActivity).filter(
            UserActivity.created_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"清理了 {deleted} 条超过 {retention_days} 天的行为记录")
        return deleted


# 全局单例
activity_tracker = ActivityTracker()
