"""
Stripe 订阅路由 - 处理订阅创建、Webhook回调、状态查询等功能
"""

import stripe
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

import config
from app.database import get_db, UserRepository
from app.services.auth import get_current_user
from app.services.activity_tracker import activity_tracker

# 配置日志
logger = logging.getLogger(__name__)

# 不在模块级别设置，改为动态获取
# stripe.api_key = config.STRIPE_SECRET_KEY

router = APIRouter(prefix="/api/subscription", tags=["订阅"])


def ensure_stripe_api_key():
    """确保 Stripe API Key 已设置"""
    import os
    api_key = os.getenv("STRIPE_SECRET_KEY", "")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STRIPE_SECRET_KEY 环境变量未配置"
        )
    
    # 直接设置 stripe 模块的 api_key
    stripe.api_key = api_key
    stripe.api_version = "2023-10-16"
    
    # 验证设置成功
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="设置 Stripe API Key 失败"
        )
    
    logger.info(f"Stripe API Key 已设置: {stripe.api_key[:20]}...")
    return stripe.api_key


# ==================== 请求/响应模型 ====================

class CreateCheckoutRequest(BaseModel):
    """创建Checkout会话请求"""
    price_id: str = None  # 可选，如不提供则使用默认价格


class SubscriptionStatusResponse(BaseModel):
    """订阅状态响应"""
    success: bool
    message: str
    data: dict = None


class WebhookResponse(BaseModel):
    """Webhook响应"""
    received: bool
    message: str


# ==================== 辅助函数 ====================

def get_or_create_stripe_customer(user_email: str, user_id: int, existing_customer_id: str = None) -> str:
    """
    获取或创建 Stripe 客户
    
    Args:
        user_email: 用户邮箱
        user_id: 用户ID
        existing_customer_id: 已有的Stripe客户ID
    
    Returns:
        Stripe客户ID
    """
    # 确保 API Key 已设置
    ensure_stripe_api_key()
    
    try:
        # 如果已有客户ID，直接返回
        if existing_customer_id:
            return existing_customer_id
        
        # 创建新客户
        customer = stripe.Customer.create(
            email=user_email,
            metadata={
                "user_id": str(user_id),
                "platform": "imvu_analytics"
            }
        )
        return customer.id
    except stripe.error.StripeError as e:
        logger.error(f"创建Stripe客户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付客户失败: {str(e)}"
        )


def map_stripe_status(stripe_status: str) -> str:
    """
    将Stripe订阅状态映射为应用状态
    
    Stripe状态 -> 应用状态:
    - active -> active
    - trialing -> active
    - past_due -> past_due
    - canceled -> canceled
    - unpaid -> expired
    - incomplete -> none
    """
    status_mapping = {
        "active": "active",
        "trialing": "active",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "expired",
        "incomplete": "none",
        "incomplete_expired": "none"
    }
    return status_mapping.get(stripe_status, "none")


def update_user_subscription(db: Session, user_id: int, subscription_data: dict):
    """
    更新用户订阅信息
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        subscription_data: 包含 subscription_id, status, end_date 等字段的字典
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if user:
        subscription_renewed = False  # 标记是否是新订阅/续费
        
        if "subscription_id" in subscription_data:
            # 如果订阅ID变化（新订阅或续费），重置提醒标志
            if user.subscription_id != subscription_data["subscription_id"]:
                subscription_renewed = True
            user.subscription_id = subscription_data["subscription_id"]
        if "status" in subscription_data:
            # 状态变为 active 视为续费成功
            if subscription_data["status"] == "active" and user.subscription_status != "active":
                subscription_renewed = True
            user.subscription_status = subscription_data["status"]
        if "end_date" in subscription_data:
            # 到期时间延长视为续费成功
            if user.subscription_end_date and subscription_data["end_date"]:
                if subscription_data["end_date"] > user.subscription_end_date:
                    subscription_renewed = True
            user.subscription_end_date = subscription_data["end_date"]
        if "customer_id" in subscription_data:
            user.stripe_customer_id = subscription_data["customer_id"]
        
        # 续费后重置提醒标志
        if subscription_renewed:
            user.reminder_3day_sent = False
            user.reminder_1day_sent = False
            user.reminder_recall_sent = False
            user.last_reminder_sent = None
            logger.info(f"用户 {user_id} 续费成功，已重置提醒标志")
        
        db.commit()
        logger.info(f"用户 {user_id} 订阅状态已更新: {subscription_data}")


# ==================== API路由 ====================

@router.get("/config")
async def get_stripe_config():
    """
    获取Stripe公开配置（前端使用）
    """
    import os
    return {
        "publishable_key": config.get_stripe_publishable_key(),
        "price_id": config.get_stripe_price_id(),
        "price_amount": int(config.SUBSCRIPTION_PRICE * 100),  # 转换为分
        "currency": "usd",
        # 年付选项
        "yearly_price_id": os.getenv("STRIPE_YEARLY_PRICE_ID", ""),
        "yearly_price": 99.00,
        "yearly_price_monthly": 8.25,
        "yearly_savings": 45.00,
        "yearly_savings_percent": 31
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建Stripe Checkout会话
    
    用户点击订阅按钮后，调用此接口创建Checkout会话并重定向到Stripe支付页面
    """
    import os
    
    # 直接设置 API Key
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    stripe.api_version = "2023-10-16"
    
    # 设置 Stripe 请求超时
    stripe.request_timeout = 30
    
    if not stripe.api_key:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Stripe API Key 未配置"}
        )
    
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(current_user["id"])
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )
        
        # 检查是否已有活跃订阅
        if user.subscription_status == "active":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "您已有有效订阅"}
            )
        
        # 获取或创建Stripe客户
        customer_id = user.stripe_customer_id
        if not customer_id:
            try:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": str(user.id)}
                )
                customer_id = customer.id
                user.stripe_customer_id = customer_id
                db.commit()
            except stripe.error.StripeError as e:
                logger.error(f"创建Stripe客户失败: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": f"创建支付客户失败: {str(e)}"}
                )
        
        # 使用请求中的price_id或默认配置
        price_id = request.price_id or config.get_stripe_price_id()
        
        # 创建Checkout会话
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            mode="subscription",
            success_url=f"{config.APP_BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{config.APP_BASE_URL}/pricing",
            subscription_data={
                "metadata": {
                    "user_id": str(user.id)
                }
            },
            metadata={
                "user_id": str(user.id)
            },
            allow_promotion_codes=True,
            billing_address_collection="required"
        )
        
        logger.info(f"为用户 {user.id} 创建Checkout会话: {checkout_session.id}")
        
        return {
            "success": True,
            "message": "Checkout会话创建成功",
            "data": {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"创建Checkout会话失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"创建支付会话失败: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"创建Checkout会话异常: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"服务器错误: {str(e)}"}
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    处理Stripe Webhook回调
    
    重要：此接口需要在Stripe Dashboard中配置Webhook URL:
    https://imvu-analytics-production.up.railway.app/api/subscription/webhook
    
    需要监听的事件:
    - checkout.session.completed
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    # 确保 API Key 已设置
    ensure_stripe_api_key()
    
    payload = await request.body()
    sig_header = stripe_signature
    
    # 强制要求 Webhook 签名验证（生产环境必须配置 STRIPE_WEBHOOK_SECRET）
    webhook_secret = config.get_stripe_webhook_secret()
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET 未配置，拒绝处理 Webhook 请求")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"received": False, "message": "服务器配置错误：STRIPE_WEBHOOK_SECRET 未配置"}
        )
    
    # 验证 Webhook 签名
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook签名验证失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"received": False, "message": "签名验证失败"}
        )
    except Exception as e:
        logger.error(f"解析Webhook事件失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"received": False, "message": f"无效的请求: {str(e)}"}
        )
    
    # 处理不同类型的事件
    event_type = event.type
    data_object = event.data.object
    
    logger.info(f"收到Stripe Webhook: {event_type}, ID: {event.id}")
    
    try:
        from app.database import get_db_context
        
        if event_type == "checkout.session.completed":
            # 支付会话完成
            await handle_checkout_completed(data_object)
            
        elif event_type == "customer.subscription.updated":
            # 订阅更新
            await handle_subscription_updated(data_object)
            
        elif event_type == "customer.subscription.deleted":
            # 订阅取消/删除
            await handle_subscription_deleted(data_object)
            
        elif event_type == "invoice.payment_succeeded":
            # 支付成功（续费）
            await handle_payment_succeeded(data_object)
            
        elif event_type == "invoice.payment_failed":
            # 支付失败
            await handle_payment_failed(data_object)
            
        else:
            logger.info(f"未处理的事件类型: {event_type}")
        
        return {"received": True, "message": "处理成功"}
        
    except Exception as e:
        logger.error(f"处理Webhook事件失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"received": False, "message": f"处理失败: {str(e)}"}
        )


async def handle_checkout_completed(session):
    """处理Checkout会话完成事件"""
    with get_db_context() as db:
        user_id = session.metadata.get("user_id")
        subscription_id = session.get("subscription")
        
        if not user_id:
            logger.error("Checkout会话缺少user_id元数据")
            return
        
        # 获取订阅详情
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            current_period_end = datetime.utcfromtimestamp(subscription.current_period_end)
            
            update_user_subscription(db, int(user_id), {
                "subscription_id": subscription_id,
                "status": map_stripe_status(subscription.status),
                "end_date": current_period_end,
                "customer_id": session.customer
            })
            
            # 记录用户订阅成功行为
            activity_tracker.log_activity(
                db, int(user_id), 'subscribe',
                metadata={'subscription_id': subscription_id, 'plan': 'pro'}
            )
            
            logger.info(f"用户 {user_id} 订阅激活成功，订阅ID: {subscription_id}")
        else:
            logger.warning(f"Checkout会话 {session.id} 没有subscription_id")


async def handle_subscription_updated(subscription):
    """处理订阅更新事件"""
    from app.models import User
    
    with get_db_context() as db:
        user_id = subscription.metadata.get("user_id")
        
        if not user_id:
            # 尝试通过客户ID查找用户
            customer_id = subscription.customer
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            
            if not user:
                logger.warning(f"无法找到订阅 {subscription.id} 对应的用户")
                return
            user_id = user.id
        
        current_period_end = datetime.utcfromtimestamp(subscription.current_period_end)
        
        update_user_subscription(db, int(user_id), {
            "subscription_id": subscription.id,
            "status": map_stripe_status(subscription.status),
            "end_date": current_period_end
        })
        
        logger.info(f"用户 {user_id} 订阅已更新，状态: {subscription.status}")


async def handle_subscription_deleted(subscription):
    """处理订阅删除/取消事件"""
    with get_db_context() as db:
        customer_id = subscription.customer
        
        from app.database import User
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        
        if user:
            update_user_subscription(db, user.id, {
                "subscription_id": None,
                "status": "canceled",
                "end_date": datetime.utcfromtimestamp(subscription.current_period_end)
            })
            
            # 记录用户取消订阅行为
            activity_tracker.log_activity(
                db, user.id, 'cancel_subscription',
                metadata={'reason': 'user_initiated'}
            )
            
            logger.info(f"用户 {user.id} 订阅已取消")


async def handle_payment_succeeded(invoice):
    """处理支付成功事件（续费）"""
    with get_db_context() as db:
        customer_id = invoice.customer
        subscription_id = invoice.subscription
        
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            current_period_end = datetime.utcfromtimestamp(subscription.current_period_end)
            
            from app.database import User
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            
            if user:
                update_user_subscription(db, user.id, {
                    "subscription_id": subscription_id,
                    "status": "active",
                    "end_date": current_period_end
                })
                logger.info(f"用户 {user.id} 续费成功，到期时间: {current_period_end}")


async def handle_payment_failed(invoice):
    """处理支付失败事件"""
    with get_db_context() as db:
        customer_id = invoice.customer
        
        from app.database import User
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        
        if user:
            update_user_subscription(db, user.id, {
                "status": "past_due"
            })
            logger.warning(f"用户 {user.id} 支付失败，订阅状态更新为 past_due")


@router.get("/status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询当前用户的订阅状态
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(current_user["id"])
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )
        
        # 构建订阅状态数据（只使用数据库数据，不调用 Stripe API）
        from datetime import datetime
        trial_days_left = 0
        is_in_trial = False
        
        if user.trial_end_date:
            now = datetime.utcnow()
            if user.trial_end_date > now:
                delta = user.trial_end_date - now
                trial_days_left = delta.days
                if delta.seconds > 0:
                    trial_days_left += 1  # 不足一天算一天
                is_in_trial = True
        
        subscription_data = {
            "is_subscribed": user.is_subscribed,
            "status": user.subscription_status or "none",
            "subscription_id": user.subscription_id,
            "end_date": user.subscription_end_date.strftime("%Y-%m-%d %H:%M:%S") if user.subscription_end_date else None,
            "price": config.SUBSCRIPTION_PRICE,
            "currency": "usd",
            # 试用期信息
            "trial_end_date": user.trial_end_date.strftime("%Y-%m-%d %H:%M:%S") if user.trial_end_date else None,
            "trial_days_left": trial_days_left,
            "is_in_trial": is_in_trial,
            "has_premium_access": user.has_premium_access,
            # 年付选项
            "yearly_price_id": os.getenv("STRIPE_YEARLY_PRICE_ID", ""),
            "yearly_price": 99.00,
            "yearly_price_monthly": 8.25,
            "yearly_savings": 45.00,
            "yearly_savings_percent": 31
        }
        
        return {
            "success": True,
            "message": "获取成功",
            "data": subscription_data
        }
        
    except Exception as e:
        logger.error(f"获取订阅状态失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"获取订阅状态失败: {str(e)}"}
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消订阅（仅在周期结束时取消，不立即终止）
    """
    # 确保 API Key 已设置
    ensure_stripe_api_key()
    
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(current_user["id"])
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )
        
        if not user.subscription_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "当前没有订阅"}
            )
        
        # 在Stripe中设置周期结束时分取消
        subscription = stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=True
        )
        
        logger.info(f"用户 {user.id} 订阅将在 {subscription.current_period_end} 取消")
        
        return {
            "success": True,
            "message": "订阅已设置取消，将在当前周期结束后生效",
            "data": {
                "cancel_at": datetime.utcfromtimestamp(subscription.current_period_end).strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"取消订阅失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"取消订阅失败: {str(e)}"}
        )


@router.post("/reactivate")
async def reactivate_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重新激活已设置取消的订阅
    """
    # 确保 API Key 已设置
    ensure_stripe_api_key()
    
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(current_user["id"])
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )
        
        if not user.subscription_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "当前没有订阅"}
            )
        
        # 取消周期结束时的取消设置
        subscription = stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=False
        )
        
        logger.info(f"用户 {user.id} 订阅已重新激活")
        
        return {
            "success": True,
            "message": "订阅已重新激活",
            "data": {
                "status": subscription.status
            }
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"重新激活订阅失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"重新激活订阅失败: {str(e)}"}
        )


@router.get("/portal")
async def create_customer_portal(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建Stripe客户门户链接，用于管理订阅（查看账单、取消订阅等）
    """
    # 确保 API Key 已设置
    ensure_stripe_api_key()
    
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(current_user["id"])
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )
        
        if not user.stripe_customer_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "未找到支付账户，请先订阅"}
            )
        
        # 创建客户门户会话
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{config.APP_BASE_URL}/profile"
        )
        
        return {
            "success": True,
            "message": "客户门户链接创建成功",
            "data": {
                "portal_url": portal_session.url
            }
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"创建客户门户失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"创建客户门户失败: {str(e)}"}
        )