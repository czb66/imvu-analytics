"""
后台管理路由 - 提供管理员功能
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db, UserRepository
from app.services.admin import require_admin
from app.services.auth import get_current_user
import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["后台管理"])


@router.get("/promo-cards/stats")
async def get_promo_card_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取推广卡片统计数据
    """
    try:
        from app.models import PromoCardStat, PromoCardClick
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 总生成卡片数
        total_cards = db.query(PromoCardStat).filter(
            PromoCardStat.created_at >= start_date
        ).count()
        
        # 总点击次数
        total_clicks = db.query(PromoCardClick).filter(
            PromoCardClick.clicked_at >= start_date
        ).count()
        
        # 活跃卡片数（有点击的）
        active_cards = db.query(PromoCardStat).filter(
            PromoCardStat.created_at >= start_date,
            PromoCardStat.total_clicks > 0
        ).count()
        
        # 热门卡片 TOP 10
        top_cards = db.query(PromoCardStat).filter(
            PromoCardStat.created_at >= start_date
        ).order_by(desc(PromoCardStat.total_clicks)).limit(10).all()
        
        # 每日生成趋势
        daily_cards = db.query(
            func.date(PromoCardStat.created_at).label("date"),
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(func.date(PromoCardStat.created_at)).order_by(
            func.date(PromoCardStat.created_at)
        ).all()
        
        # 每日点击趋势
        daily_clicks = db.query(
            func.date(PromoCardClick.clicked_at).label("date"),
            func.count(PromoCardClick.id).label("count")
        ).filter(
            PromoCardClick.clicked_at >= start_date
        ).group_by(func.date(PromoCardClick.clicked_at)).order_by(
            func.date(PromoCardClick.clicked_at)
        ).all()
        
        # 样式分布
        style_dist = db.query(
            PromoCardStat.style,
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(PromoCardStat.style).all()
        
        # 配色分布
        color_dist = db.query(
            PromoCardStat.color,
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(PromoCardStat.color).all()
        
        return {
            "success": True,
            "data": {
                "total_cards": total_cards,
                "total_clicks": total_clicks,
                "active_cards": active_cards,
                "click_rate": round(total_clicks / total_cards, 2) if total_cards > 0 else 0,
                "top_cards": [
                    {
                        "id": c.id,
                        "title": c.card_title,
                        "style": c.style,
                        "color": c.color,
                        "clicks": c.total_clicks or 0,
                        "products": c.product_count,
                        "created_at": c.created_at.isoformat() if c.created_at else None
                    }
                    for c in top_cards
                ],
                "daily_cards": [{"date": str(d.date), "count": d.count} for d in daily_cards],
                "daily_clicks": [{"date": str(d.date), "count": d.count} for d in daily_clicks],
                "style_distribution": [{"style": s.style, "count": s.count} for s in style_dist],
                "color_distribution": [{"color": c.color, "count": c.count} for c in color_dist]
            }
        }
    except Exception as e:
        logger.error(f"获取推广卡片统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/promo-cards/list")
async def get_promo_cards_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取推广卡片列表
    """
    try:
        from app.models import PromoCardStat
        
        total = db.query(PromoCardStat).count()
        offset = (page - 1) * page_size
        
        cards = db.query(PromoCardStat).order_by(
            desc(PromoCardStat.created_at)
        ).offset(offset).limit(page_size).all()
        
        return {
            "success": True,
            "data": {
                "cards": [
                    {
                        "id": c.id,
                        "title": c.card_title,
                        "style": c.style,
                        "color": c.color,
                        "products": c.product_count,
                        "clicks": c.total_clicks or 0,
                        "last_click": c.last_click_at.isoformat() if c.last_click_at else None,
                        "created_at": c.created_at.isoformat() if c.created_at else None
                    }
                    for c in cards
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"获取推广卡片列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.get("/promo-cards/{card_id}")
async def get_promo_card_detail(
    card_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取单个推广卡片详情
    """
    try:
        from app.models import PromoCardStat, PromoCardClick
        import json
        
        card = db.query(PromoCardStat).filter(PromoCardStat.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="卡片不存在")
        
        # 获取点击记录
        clicks = db.query(PromoCardClick).filter(
            PromoCardClick.stat_id == card_id
        ).order_by(desc(PromoCardClick.clicked_at)).limit(50).all()
        
        # 解析产品信息
        products = json.loads(card.products_json) if card.products_json else []
        
        # 按产品统计点击
        product_clicks = {}
        for click in clicks:
            idx = click.product_index
            if idx not in product_clicks:
                product_clicks[idx] = {"count": 0, "name": click.product_name}
            product_clicks[idx]["count"] += 1
        
        return {
            "success": True,
            "data": {
                "id": card.id,
                "title": card.card_title,
                "subtitle": card.card_subtitle,
                "intro": card.card_intro,
                "footer": card.card_footer,
                "style": card.style,
                "color": card.color,
                "products": products,
                "product_clicks": product_clicks,
                "total_clicks": card.total_clicks or 0,
                "created_at": card.created_at.isoformat() if card.created_at else None,
                "last_click_at": card.last_click_at.isoformat() if card.last_click_at else None,
                "recent_clicks": [
                    {
                        "product_name": c.product_name,
                        "product_index": c.product_index,
                        "ip": c.ip_address,
                        "referrer": c.referrer,
                        "target_link": c.original_link,
                        "clicked_at": c.clicked_at.isoformat() if c.clicked_at else None
                    }
                    for c in clicks[:20]
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取推广卡片详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")


@router.get("/stats")
async def get_admin_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取管理后台统计数据
    - 总用户数
    - 已订阅用户数
    - 本周新增用户数
    - DAU (日活跃用户数)
    - MAU (月活跃用户数)
    """
    try:
        from app.models import User
        
        # 总用户数
        total_users = db.query(User).count()
        
        # 已订阅用户数 (active subscription)
        subscribed_users = db.query(User).filter(
            User.subscription_status == 'active'
        ).count()
        
        # 本周新增用户数
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_new_users = db.query(User).filter(
            User.created_at >= week_ago
        ).count()
        
        # DAU - 日活跃用户数（今天登录过的用户）
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        dau = db.query(User).filter(
            User.last_login >= today_start
        ).count()
        
        # MAU - 月活跃用户数（最近30天登录过的用户）
        month_ago = datetime.utcnow() - timedelta(days=30)
        mau = db.query(User).filter(
            User.last_login >= month_ago
        ).count()
        
        # 用户粘性 (DAU/MAU)
        stickiness = round(dau / mau * 100, 1) if mau > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "subscribed_users": subscribed_users,
                "weekly_new_users": weekly_new_users,
                "dau": dau,
                "mau": mau,
                "stickiness": stickiness
            }
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/users")
async def get_admin_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（邮箱或用户名）"),
    subscription_status: Optional[str] = Query(None, description="订阅状态过滤"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）
    """
    try:
        from app.models import User
        
        query = db.query(User)
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern)
                )
            )
        
        # 订阅状态过滤
        if subscription_status:
            if subscription_status == 'subscribed':
                query = query.filter(User.subscription_status == 'active')
            elif subscription_status == 'not_subscribed':
                query = query.filter(User.subscription_status != 'active')
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
        
        # 转换数据
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "subscription_status": user.subscription_status,
                "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                "is_subscribed": user.is_subscribed
            })
        
        return {
            "success": True,
            "data": {
                "users": user_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.post("/users/{user_id}/toggle-subscription")
async def toggle_user_subscription(
    user_id: int,
    action: str = Query(..., description="操作：activate 或 deactivate"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    手动开启/关闭用户订阅
    """
    try:
        from app.models import User
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if action == "activate":
            user.subscription_status = 'active'
            user.subscription_end_date = datetime.utcnow() + timedelta(days=30)  # 默认30天
            message = "订阅已激活"
        elif action == "deactivate":
            user.subscription_status = 'canceled'
            user.subscription_end_date = datetime.utcnow()
            message = "订阅已取消"
        else:
            raise HTTPException(status_code=400, detail="无效的操作")
        
        db.commit()
        
        return {
            "success": True,
            "message": message,
            "data": {
                "user_id": user.id,
                "subscription_status": user.subscription_status,
                "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换订阅状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    切换用户管理员权限
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 防止取消自己的管理员权限
        if user.id == current_user["id"]:
            raise HTTPException(status_code=400, detail="不能修改自己的管理员权限")
        
        user.is_admin = not user.is_admin
        db.commit()
        
        return {
            "success": True,
            "message": f"管理员权限已{'授予' if user.is_admin else '撤销'}",
            "data": {
                "user_id": user.id,
                "is_admin": user.is_admin
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换管理员权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/users/{user_id}/toggle-whitelist")
async def toggle_user_whitelist(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    切换用户白名单状态
    
    白名单用户可以跳过订阅检查，免费使用所有功能
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user.is_whitelisted = not user.is_whitelisted
        db.commit()
        
        logger.info(f"管理员 {current_user.get('email')} {'添加' if user.is_whitelisted else '移除'}用户 {user.email} 的白名单权限")
        
        return {
            "success": True,
            "message": f"白名单权限已{'授予' if user.is_whitelisted else '撤销'}",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "is_whitelisted": user.is_whitelisted
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换白名单权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

# =====================================================
# 页面访问统计 API
# =====================================================

@router.get("/page-views")
async def get_page_view_stats(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取页面访问统计数据
    - 今日访问量 (PV)
    - 总访问量
    - 独立访客数 (UV)
    - 页面访问排行
    - 访问趋势（最近N天）
    """
    try:
        from app.models import PageView
        from sqlalchemy import func
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今日访问量
        today_pv = db.query(PageView).filter(
            PageView.created_at >= today_start
        ).count()
        
        # 总访问量
        total_pv = db.query(PageView).count()
        
        # 今日独立IP数（UV近似）
        today_uv = db.query(PageView.ip_address).filter(
            PageView.created_at >= today_start
        ).distinct().count()
        
        # 页面访问排行（Top 10）
        top_pages = db.query(
            PageView.path,
            func.count(PageView.id).label('count')
        ).group_by(PageView.path).order_by(desc('count')).limit(10).all()
        
        # 访问趋势（最近N天）
        trend_data = []
        for i in range(days - 1, -1, -1):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_pv = db.query(PageView).filter(
                PageView.created_at >= day_start,
                PageView.created_at < day_end
            ).count()
            
            day_uv = db.query(PageView.ip_address).filter(
                PageView.created_at >= day_start,
                PageView.created_at < day_end
            ).distinct().count()
            
            trend_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "pv": day_pv,
                "uv": day_uv
            })
        
        return {
            "success": True,
            "data": {
                "today_pv": today_pv,
                "total_pv": total_pv,
                "today_uv": today_uv,
                "top_pages": [{"path": p[0], "count": p[1]} for p in top_pages],
                "trend": trend_data
            }
        }
    except Exception as e:
        logger.error(f"获取页面访问统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/page-views/recent")
async def get_recent_page_views(
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取最近访问记录
    """
    try:
        from app.models import PageView
        
        recent = db.query(PageView).order_by(
            desc(PageView.created_at)
        ).limit(limit).all()
        
        return {
            "success": True,
            "data": [{
                "id": pv.id,
                "path": pv.path,
                "ip_address": pv.ip_address,
                "user_agent": pv.user_agent[:100] if pv.user_agent else None,
                "referrer": pv.referrer,
                "created_at": pv.created_at.isoformat() if pv.created_at else None
            } for pv in recent]
        }
    except Exception as e:
        logger.error(f"获取最近访问记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取访问记录失败: {str(e)}")
