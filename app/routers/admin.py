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
from app.services.activity_tracker import activity_tracker
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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


# ==================== 用户行为分析API ====================

@router.get("/analytics/users")
async def get_user_activity_stats(
    days: int = Query(30, ge=7, le=365, description="统计天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户活跃度统计
    
    - DAU趋势（最近N天）
    - MAU（月活跃用户数）
    - 用户参与度分布
    """
    try:
        # DAU趋势
        dau_trend = activity_tracker.get_dau_trend(db, days=days)
        
        # 当前MAU
        now = datetime.utcnow()
        mau = activity_tracker.get_monthly_active_users(db, now.year, now.month)
        
        # 当前DAU
        dau = activity_tracker.get_daily_active_users(db)
        
        # 获取总注册用户数
        from app.models import User
        total_users = db.query(User).count()
        
        # 计算活跃用户占比
        active_users = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
            UserActivity.created_at >= datetime.utcnow() - timedelta(days=days)
        ).scalar() or 0
        
        # 计算次日留存率（最近7天）
        retention_rates = []
        for i in range(7):
            cohort_date = (datetime.utcnow() - timedelta(days=i+1)).date()
            retention = activity_tracker.get_retention_rate(db, cohort_date)
            retention_rates.append({
                'date': cohort_date.isoformat(),
                'retention_rate': retention
            })
        
        return {
            "success": True,
            "data": {
                "dau": dau,
                "mau": mau,
                "total_users": total_users,
                "active_users_in_period": active_users,
                "active_user_ratio": round(active_users / total_users * 100, 2) if total_users > 0 else 0,
                "dau_trend": dau_trend,
                "retention_rates": retention_rates
            }
        }
    except Exception as e:
        logger.error(f"获取用户活跃度统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/analytics/features")
async def get_feature_usage_stats(
    days: int = Query(30, ge=7, le=365, description="统计天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取功能使用统计
    
    返回各功能的总使用次数和独立用户数
    """
    try:
        from app.models import UserActivity
        
        # 功能使用次数统计
        feature_usage = activity_tracker.get_feature_usage(db, days=days)
        
        # 按功能分组统计独立用户数
        feature_users = {}
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            UserActivity.action,
            func.count(func.distinct(UserActivity.user_id)).label('user_count')
        ).filter(
            UserActivity.created_at >= start_date
        ).group_by(
            UserActivity.action
        ).all()
        
        for r in results:
            feature_users[r.action] = r.user_count
        
        # 构建完整数据
        features_data = []
        for action, count in feature_usage.items():
            features_data.append({
                'action': action,
                'usage_count': count,
                'unique_users': feature_users.get(action, 0)
            })
        
        # 按使用次数排序
        features_data.sort(key=lambda x: x['usage_count'], reverse=True)
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_events": sum(feature_usage.values()),
                "features": features_data
            }
        }
    except Exception as e:
        logger.error(f"获取功能使用统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/analytics/retention")
async def get_retention_stats(
    days: int = Query(30, ge=7, le=90, description="分析天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取留存率统计
    
    返回每日 cohort 的次日、7日、30日留存率
    """
    try:
        retention_data = []
        
        for i in range(days):
            cohort_date = (datetime.utcnow() - timedelta(days=i+1)).date()
            
            # 获取该日注册用户数
            from app.models import User
            cohort_start = datetime.combine(cohort_date, datetime.min.time())
            cohort_end = datetime.combine(cohort_date, datetime.max.time())
            
            new_users_count = db.query(func.count(User.id)).filter(
                and_(
                    User.created_at >= cohort_start,
                    User.created_at <= cohort_end
                )
            ).scalar() or 0
            
            if new_users_count == 0:
                continue
            
            # 次日留存
            day1_retention = activity_tracker.get_retention_rate(db, cohort_date)
            
            # 7日留存
            day7_cohort = cohort_date - timedelta(days=7)
            day7_users = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
                and_(
                    UserActivity.user_id.in_(
                        db.query(User.id).filter(
                            and_(
                                User.created_at >= cohort_start,
                                User.created_at <= cohort_end
                            )
                        )
                    ),
                    func.date(UserActivity.created_at) == day7_cohort
                )
            ).scalar() or 0
            day7_rate = round(day7_users / new_users_count, 4) if new_users_count > 0 else 0
            
            retention_data.append({
                'cohort_date': cohort_date.isoformat(),
                'new_users': new_users_count,
                'day1_retention': round(day1_retention * 100, 2),
                'day7_retention': round(day7_rate * 100, 2)
            })
        
        # 按日期倒序
        retention_data.sort(key=lambda x: x['cohort_date'], reverse=True)
        
        return {
            "success": True,
            "data": {
                "retention_data": retention_data[:30],  # 最多返回30天
                "average_day1_retention": round(
                    sum(r['day1_retention'] for r in retention_data) / len(retention_data), 2
                ) if retention_data else 0,
                "average_day7_retention": round(
                    sum(r['day7_retention'] for r in retention_data) / len(retention_data), 2
                ) if retention_data else 0
            }
        }
    except Exception as e:
        logger.error(f"获取留存率统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/analytics/funnel")
async def get_conversion_funnel_stats(
    days: int = Query(30, ge=7, le=365, description="统计天数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取转化漏斗统计
    
    从注册到付费的转化路径分析
    """
    try:
        from app.models import User, UserActivity
        
        # 获取转化漏斗数据
        funnel_data = activity_tracker.get_conversion_funnel(db, days=days)
        
        # 计算转化率
        steps = ['register', 'login', 'upload', 'view_dashboard', 'generate_report']
        funnel_with_conversion = []
        
        prev_count = None
        for step in steps:
            count = funnel_data.get(step, 0)
            conversion_rate = 100.0
            
            if prev_count is not None and prev_count > 0:
                conversion_rate = round(count / prev_count * 100, 2)
            elif step == 'register':
                # 注册作为漏斗入口，使用注册用户总数
                from app.models import User
                start_date = datetime.utcnow() - timedelta(days=days)
                total_registered = db.query(func.count(User.id)).filter(
                    User.created_at >= start_date
                ).scalar() or 0
                prev_count = total_registered
                count = total_registered
            
            funnel_with_conversion.append({
                'step': step,
                'step_name': _get_step_name(step),
                'users': count,
                'conversion_from_previous': conversion_rate
            })
            
            if step != 'register':
                prev_count = count
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "funnel": funnel_with_conversion,
                "overall_conversion": round(
                    funnel_data.get('generate_report', 0) / prev_count * 100, 2
                ) if prev_count and prev_count > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"获取转化漏斗统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


def _get_step_name(step: str) -> str:
    """获取步骤显示名称"""
    names = {
        'register': '注册',
        'login': '登录',
        'upload': '上传数据',
        'view_dashboard': '查看仪表盘',
        'generate_report': '生成报告',
        'subscribe': '订阅付费'
    }
    return names.get(step, step)


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        
        logger.info(f"管理员ID {current_user.get('id')} {'添加' if user.is_whitelisted else '移除'}用户ID {user.id} 的白名单权限")
        
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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")

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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


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
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/reminder/stats")
async def get_reminder_stats(
    current_user: dict = Depends(require_admin)
):
    """
    获取订阅到期提醒发送统计
    """
    try:
        from app.services.report_generator import get_reminder_stats as _get_stats
        
        stats = _get_stats()
        
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        
        return {
            "success": True,
            "data": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取提醒统计失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/reminder/test")
async def test_reminder_email(
    user_id: int = Query(..., description="用户ID"),
    reminder_type: str = Query("sub_3day", description="提醒类型: sub_3day, sub_1day, sub_recall, trial_3day, trial_1day, trial_recall"),
    current_user: dict = Depends(require_admin)
):
    """
    测试发送提醒邮件给指定用户
    """
    try:
        from app.services.report_generator import test_reminder_email as _test_email
        
        success, message = _test_email(user_id, reminder_type)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试提醒邮件失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/reminder/reset")
async def reset_user_reminders(
    user_id: int = Query(..., description="用户ID"),
    is_trial: bool = Query(False, description="是否为试用期用户"),
    current_user: dict = Depends(require_admin)
):
    """
    重置用户提醒标志（用于测试或在续费后调用）
    """
    try:
        from app.services.report_generator import reset_user_reminder_flags as _reset_flags
        
        success, message = _reset_flags(user_id, is_trial)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置提醒标志失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/reminder/trigger")
async def trigger_reminder_check(
    current_user: dict = Depends(require_admin)
):
    """
    手动触发订阅到期提醒检查（管理员功能）
    """
    try:
        from app.services.report_generator import check_subscription_expiry
        
        # 在后台异步执行
        import asyncio
        asyncio.create_task(asyncio.to_thread(check_subscription_expiry))
        
        return {"success": True, "message": "提醒检查任务已触发，将在后天执行"}
    except Exception as e:
        logger.error(f"触发提醒检查失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


# ==================== 推荐系统监控接口 ====================

@router.get("/referral/stats")
async def get_referral_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取推荐系统总览统计
    """
    try:
        from app.models import User
        from app.database import UserRepository
        
        user_repo = UserRepository(db)
        
        # 总注册用户数
        total_users = db.query(User).count()
        
        # 有推荐人的用户数
        users_with_referrer = db.query(User).filter(
            User.referred_by.isnot(None)
        ).count()
        
        # 有待发放奖励的用户数
        pending_rewards = db.query(User).filter(
            User.referral_reward_pending == True
        ).count()
        
        # 已发放奖励的用户数
        rewarded_users = db.query(User).filter(
            User.referral_rewarded_at.isnot(None)
        ).count()
        
        # 被暂停的推荐码数
        suspended_codes = db.query(User).filter(
            User.referral_suspended == True,
            User.referral_code.isnot(None)
        ).count()
        
        # 按推荐码统计使用次数（Top 10）
        referral_usage = db.query(
            User.referred_by,
            func.count(User.id).label('usage_count')
        ).filter(
            User.referred_by.isnot(None)
        ).group_by(User.referred_by).order_by(
            desc('usage_count')
        ).limit(10).all()
        
        # 补充推荐人信息
        top_referrers = []
        for code, count in referral_usage:
            referrer = user_repo.get_by_referral_code(code)
            if referrer:
                monthly_rewards = user_repo.get_monthly_referral_rewards(referrer.id)
                top_referrers.append({
                    'referral_code': code,
                    'referrer_email': referrer.email,
                    'total_uses': count,
                    'monthly_rewards': monthly_rewards,
                    'monthly_limit': 5,
                    'is_suspended': referrer.referral_suspended
                })
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "users_with_referrer": users_with_referrer,
                "pending_rewards": pending_rewards,
                "rewarded_users": rewarded_users,
                "suspended_codes": suspended_codes,
                "conversion_rate": round(users_with_referrer / total_users * 100, 2) if total_users > 0 else 0,
                "top_referrers": top_referrers
            }
        }
    except Exception as e:
        logger.error(f"获取推荐系统统计失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/referral/suspicious")
async def get_suspicious_referrals(
    days: int = Query(7, ge=1, le=30, description="统计天数范围"),
    min_uses: int = Query(3, ge=1, le=20, description="最小使用次数"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取可疑推荐列表
    """
    try:
        from app.models import User
        from app.database import UserRepository
        from datetime import timedelta
        
        user_repo = UserRepository(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取指定时间内注册的用户（按推荐码分组）
        recent_referrals = db.query(
            User.referred_by,
            func.count(User.id).label('recent_count')
        ).filter(
            User.referred_by.isnot(None),
            User.created_at >= start_date
        ).group_by(User.referred_by).having(
            func.count(User.id) >= min_uses
        ).order_by(desc('recent_count')).all()
        
        suspicious_list = []
        for code, count in recent_referrals:
            referrer = user_repo.get_by_referral_code(code)
            if referrer:
                total_count = user_repo.get_total_referral_usage(code)
                suspicious_list.append({
                    'referral_code': code,
                    'referrer_email': referrer.email,
                    'recent_uses': count,
                    'total_uses': total_count,
                    'is_suspended': referrer.referral_suspended,
                })
        
        return {
            "success": True,
            "data": {
                "query_days": days,
                "min_uses": min_uses,
                "suspicious_count": len(suspicious_list),
                "suspicious_list": suspicious_list
            }
        }
    except Exception as e:
        logger.error(f"获取可疑推荐列表失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/referral/{user_id}/suspend")
async def suspend_user_referral(
    user_id: int,
    suspend: bool = Query(True, description="是否暂停推荐码"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    暂停或恢复用户的推荐码
    """
    try:
        from app.database import UserRepository
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if not user.referral_code:
            raise HTTPException(status_code=400, detail="该用户没有推荐码")
        
        user_repo.suspend_referral_code(user_id, suspend)
        
        action = "暂停" if suspend else "恢复"
        return {
            "success": True,
            "message": f"推荐码 {user.referral_code} 已{action}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"操作推荐码失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/referral/check-now")
async def trigger_referral_check(
    current_user: dict = Depends(require_admin)
):
    """
    手动触发推荐系统异常检测
    """
    try:
        from app.services.report_generator import check_suspicious_referral_activity
        
        result = check_suspicious_referral_activity()
        
        return {
            "success": True,
            "message": "检测完成",
            "data": result
        }
    except Exception as e:
        logger.error(f"触发推荐检测失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")
# ==================== 缓存管理API ====================

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: dict = Depends(require_admin)
):
    """
    获取缓存统计信息
    
    返回缓存命中率、大小、内存使用等统计
    """
    try:
        from app.services.cache import get_cache
        
        cache = get_cache()
        stats = cache.get_stats()
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/cache/clear")
async def clear_all_cache(
    current_user: dict = Depends(require_admin)
):
    """
    清空所有缓存
    
    谨慎使用！这会影响所有用户的缓存
    """
    try:
        from app.services.cache import get_cache
        
        cache = get_cache()
        stats_before = cache.get_stats()
        cache.clear()
        
        logger.warning(f"[Admin] 用户ID {current_user.get('id')} 清空了所有缓存 (清除了 {stats_before.get('size', 0)} 条)")
        
        return {
            "success": True,
            "message": "所有缓存已清空",
            "cleared_entries": stats_before.get('size', 0)
        }
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/cache/clear-user/{user_id}")
async def clear_user_cache(
    user_id: int,
    current_user: dict = Depends(require_admin)
):
    """
    清除指定用户的缓存
    
    Args:
        user_id: 要清除缓存的用户ID
    """
    try:
        from app.services.cache import get_cache
        
        cache = get_cache()
        
        # 清除该用户相关的所有缓存
        patterns = [
            f"dashboard:*:user_{user_id}*",
            f"insights:*:user_{user_id}*",
            f"user_{user_id}_*"
        ]
        
        total_cleared = 0
        for pattern in patterns:
            count = cache.delete_pattern(pattern)
            total_cleared += count
        
        logger.info(f"[Admin] 用户ID {current_user.get('id')} 清除了用户 {user_id} 的 {total_cleared} 条缓存")
        
        return {
            "success": True,
            "message": f"已清除用户 {user_id} 的缓存",
            "cleared_entries": total_cleared
        }
    except Exception as e:
        logger.error(f"清除用户缓存失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/cache/clear-pattern")
async def clear_cache_by_pattern(
    pattern: str = Query(..., description="缓存键模式，如 'dashboard:*' 或 '*user_123*'"),
    current_user: dict = Depends(require_admin)
):
    """
    按模式清除缓存
    
    Args:
        pattern: 缓存键模式，支持通配符 * 和 ?
    """
    try:
        from app.services.cache import get_cache
        
        cache = get_cache()
        count = cache.delete_pattern(pattern)
        
        logger.info(f"[Admin] 用户ID {current_user.get('id')} 按模式 '{pattern}' 清除了 {count} 条缓存")
        
        return {
            "success": True,
            "message": f"模式 '{pattern}' 匹配删除了 {count} 条缓存",
            "cleared_entries": count
        }
    except Exception as e:
        logger.error(f"按模式清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")
