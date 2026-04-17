"""
推广卡片统计 API
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import PromoCardStat, User

router = APIRouter(
    prefix="/api/promo-card",
    tags=["promo-card"]
)


@router.post("/stats")
async def save_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    保存推广卡片生成统计
    """
    try:
        data = await request.json()
        
        # 提取数据
        card_title = data.get("cardTitle", "")
        card_subtitle = data.get("cardSubtitle", "")
        card_intro = data.get("cardIntro", "")
        card_footer = data.get("cardFooter", "")
        style = data.get("style", "grid")
        color = data.get("color", "purple")
        products = data.get("products", [])
        action = data.get("action", "generate")
        session_id = data.get("sessionId")
        
        # 提取产品链接
        product_links = [p.get("link", "") for p in products if p.get("link")]
        
        # 获取用户ID（如果已登录）
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # 这里简化处理，实际应该验证token
            # user = verify_token(token)
            # if user:
            #     user_id = user.id
        
        # 获取IP地址
        ip_address = request.client.host if request.client else None
        
        # 创建统计记录
        stat = PromoCardStat(
            card_title=card_title[:255] if card_title else None,
            card_subtitle=card_subtitle[:255] if card_subtitle else None,
            card_intro=card_intro,
            card_footer=card_footer,
            style=style,
            color=color,
            product_count=len(products),
            product_links=json.dumps(product_links) if product_links else None,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            action=action
        )
        
        db.add(stat)
        db.commit()
        db.refresh(stat)
        
        return {
            "success": True,
            "message": "统计已保存",
            "stat_id": stat.id
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/stats/overview")
async def get_stats_overview(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取统计数据概览
    """
    try:
        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 总生成次数
        total_count = db.query(func.count(PromoCardStat.id)).filter(
            PromoCardStat.created_at >= start_date
        ).scalar()
        
        # 按样式分组统计
        style_stats = db.query(
            PromoCardStat.style,
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(PromoCardStat.style).all()
        
        # 按配色分组统计
        color_stats = db.query(
            PromoCardStat.color,
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(PromoCardStat.color).all()
        
        # 按操作类型统计
        action_stats = db.query(
            PromoCardStat.action,
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(PromoCardStat.action).all()
        
        # 每日生成趋势
        daily_stats = db.query(
            func.date(PromoCardStat.created_at).label("date"),
            func.count(PromoCardStat.id).label("count")
        ).filter(
            PromoCardStat.created_at >= start_date
        ).group_by(func.date(PromoCardStat.created_at)).order_by(
            func.date(PromoCardStat.created_at)
        ).all()
        
        return {
            "success": True,
            "data": {
                "total_count": total_count,
                "period_days": days,
                "style_distribution": [{"style": s.style, "count": s.count} for s in style_stats],
                "color_distribution": [{"color": c.color, "count": c.count} for c in color_stats],
                "action_distribution": [{"action": a.action, "count": a.count} for a in action_stats],
                "daily_trend": [{"date": str(d.date), "count": d.count} for d in daily_stats]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/stats/recent")
async def get_recent_stats(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取最近的生成记录
    """
    try:
        stats = db.query(PromoCardStat).order_by(
            PromoCardStat.created_at.desc()
        ).limit(limit).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": s.id,
                    "card_title": s.card_title,
                    "style": s.style,
                    "color": s.color,
                    "product_count": s.product_count,
                    "action": s.action,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in stats
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
