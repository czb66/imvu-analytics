"""
推广卡片统计 API - 支持速率限制和可选认证
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
import logging

from app.database import get_db
from app.models import PromoCardStat, PromoCardClick, User
from app.core.limiter import limiter
from app.services.activity_tracker import activity_tracker

router = APIRouter(
    prefix="/api/promo-card",
    tags=["promo-card"]
)

logger = logging.getLogger(__name__)


# ==================== 辅助函数 ====================

def get_optional_user(request: Request, db: Session) -> Optional[dict]:
    """
    获取可选的用户信息（如果已认证）
    如果没有认证，返回None但不阻止请求
    """
    try:
        from app.services.auth import decode_access_token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_access_token(token)
            if payload:
                user_repo = User
                user_id = payload.get("sub")
                if user_id:
                    user = db.query(User).filter(User.id == int(user_id)).first()
                    if user and user.is_active:
                        return {
                            "id": user.id,
                            "email": user.email,
                            "is_subscribed": getattr(user, 'is_subscribed', False)
                        }
    except Exception as e:
        logger.debug(f"获取可选用户信息失败: {e}")
    return None


# ==================== 请求/响应模型 ====================

class PromoCardStatsRequest(BaseModel):
    """推广卡片统计请求"""
    creator_id: Optional[str] = Field(None, description="创作者ID")
    product_id: Optional[str] = Field(None, description="产品ID")


class PromoCardStatsResponse(BaseModel):
    """推广卡片统计响应"""
    success: bool
    message: str
    data: dict = None


# ==================== API路由 ====================

@router.post("/stats")
@limiter.limit("10/minute")  # 统计接口：10次/分钟
async def save_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    保存推广卡片生成统计（速率限制：10次/分钟）
    返回 stat_id 用于追踪链接
    
    支持可选认证 - 如果登录则关联用户身份
    """
    try:
        data = await request.json()
        
        # 提取数据
        products = data.get("products", [])
        
        # 获取可选用户信息
        user_info = get_optional_user(request, db)
        
        # 获取IP地址
        ip_address = request.client.host if request.client else None
        
        # 创建统计记录
        stat = PromoCardStat(
            card_title=data.get("cardTitle", "")[:255],
            card_subtitle=data.get("cardSubtitle", "")[:255],
            card_intro=data.get("cardIntro", ""),
            card_footer=data.get("cardFooter", ""),
            style=data.get("style", "grid"),
            color=data.get("color", "purple"),
            product_count=len(products),
            products_json=json.dumps(products) if products else None,
            session_id=data.get("sessionId"),
            ip_address=ip_address,
            user_id=user_info["id"] if user_info else None,
        )
        
        db.add(stat)
        db.commit()
        db.refresh(stat)
        
        # 记录创建推广卡片行为
        if user_info:
            activity_tracker.log_activity(
                db, user_info["id"], 'create_promo_card',
                resource_type='promo_card',
                resource_id=stat.id,
                metadata={'product_count': len(products), 'style': data.get("style", "grid")}
            )
        
        logger.info(f"推广卡片统计 - 用户: {user_info['email'] if user_info else '匿名'}, stat_id: {stat.id}")
        
        return {
            "success": True,
            "stat_id": stat.id,
            "message": "统计已保存"
        }
        
    except Exception as e:
        logger.error(f"Save stats error: {e}")
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/track/{stat_id}/{product_index}")
@limiter.limit("30/minute")  # 追踪接口：30次/分钟
async def track_click(
    stat_id: int,
    product_index: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    追踪推广卡片点击（速率限制：30次/分钟）
    
    支持可选认证 - 如果登录则关联用户身份
    """
    try:
        # 获取可选用户信息
        user_info = get_optional_user(request, db)
        
        # 获取IP和User-Agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # 记录点击
        click = PromoCardClick(
            stat_id=stat_id,
            product_index=product_index,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,
            user_id=user_info["id"] if user_info else None,
        )
        
        db.add(click)
        db.commit()
        
        logger.info(f"推广卡片点击 - 用户: {user_info['email'] if user_info else '匿名'}, stat: {stat_id}, product: {product_index}")
        
        # 重定向到产品页面
        stat = db.query(PromoCardStat).filter(PromoCardStat.id == stat_id).first()
        if stat and stat.products_json:
            try:
                products = json.loads(stat.products_json)
                if 0 <= product_index < len(products):
                    product = products[product_index]
                    if product.get("product_url"):
                        return RedirectResponse(url=product["product_url"])
            except json.JSONDecodeError:
                pass
        
        return {"success": True, "message": "点击已记录"}
        
    except Exception as e:
        logger.error(f"Track click error: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}


@router.get("/stats/{stat_id}")
async def get_stats(
    stat_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取特定推广卡片的统计数据
    """
    try:
        stat = db.query(PromoCardStat).filter(PromoCardStat.id == stat_id).first()
        
        if not stat:
            return {"success": False, "error": "统计不存在"}
        
        # 获取点击统计
        clicks_count = db.query(func.count(PromoCardClick.id)).filter(
            PromoCardClick.stat_id == stat_id
        ).scalar()
        
        # 按产品分组统计
        clicks_by_product = db.query(
            PromoCardClick.product_index,
            func.count(PromoCardClick.id).label("count")
        ).filter(
            PromoCardClick.stat_id == stat_id
        ).group_by(PromoCardClick.product_index).all()
        
        return {
            "success": True,
            "data": {
                "stat_id": stat.id,
                "card_title": stat.card_title,
                "product_count": stat.product_count,
                "created_at": stat.created_at.isoformat() if stat.created_at else None,
                "total_clicks": clicks_count,
                "clicks_by_product": [
                    {"product_index": p.product_index, "clicks": p.count}
                    for p in clicks_by_product
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/stats-query")
@limiter.limit("10/minute")  # 查询接口：10次/分钟
async def query_stats(
    request: Request,
    stats_request: PromoCardStatsRequest,
    db: Session = Depends(get_db)
):
    """
    查询推广卡片统计数据（速率限制：10次/分钟）
    
    支持可选认证 - 如果登录则关联用户身份
    """
    try:
        # 获取可选用户信息
        user_info = get_optional_user(request, db)
        
        stats_data = {
            "creator_id": stats_request.creator_id,
            "product_id": stats_request.product_id,
            "total_views": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "user_id": user_info["id"] if user_info else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"推广卡片统计查询 - 用户: {user_info['email'] if user_info else '匿名'}, creator: {stats_request.creator_id}")
        
        return {
            "success": True,
            "message": "获取成功",
            "data": stats_data
        }
    except Exception as e:
        logger.error(f"查询推广卡片统计失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"获取统计失败: {str(e)}"}
        )


@router.post("/track-event")
@limiter.limit("30/minute")  # 追踪接口：30次/分钟
async def track_event(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    追踪推广卡片事件（速率限制：30次/分钟）
    
    支持可选认证 - 如果登录则关联用户身份
    """
    try:
        data = await request.json()
        
        # 获取可选用户信息
        user_info = get_optional_user(request, db)
        
        # 验证事件类型
        event_type = data.get("event_type", "view")
        valid_events = ["view", "click", "convert"]
        if event_type not in valid_events:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"无效的事件类型: {event_type}"}
            )
        
        card_id = data.get("card_id")
        ip_address = request.client.host if request.client else None
        
        logger.info(f"推广卡片事件追踪 - 类型: {event_type}, 用户: {user_info['email'] if user_info else '匿名'}, card: {card_id}")
        
        return {
            "success": True,
            "message": "追踪成功",
            "data": {
                "card_id": card_id,
                "event_type": event_type,
                "user_id": user_info["id"] if user_info else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"追踪推广卡片事件失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"追踪失败: {str(e)}"}
        )


@router.get("/health")
async def promo_card_health():
    """
    推广卡片服务健康检查
    """
    return {"status": "healthy", "service": "promo-card"}
