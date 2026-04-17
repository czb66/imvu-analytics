"""
推广卡片统计 API
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json
import logging

from app.database import get_db
from app.models import PromoCardStat, PromoCardClick, User

router = APIRouter(
    prefix="/api/promo-card",
    tags=["promo-card"]
)

logger = logging.getLogger(__name__)


@router.post("/stats")
async def save_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    保存推广卡片生成统计，返回 stat_id 用于追踪链接
    """
    try:
        data = await request.json()
        
        # 提取数据
        products = data.get("products", [])
        
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
        )
        
        db.add(stat)
        db.commit()
        db.refresh(stat)
        
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
async def track_click(
    stat_id: int,
    product_index: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    追踪点击并重定向到实际商品链接
    这是生成的HTML中的链接会指向的地址
    """
    try:
        # 查找卡片统计记录
        stat = db.query(PromoCardStat).filter(PromoCardStat.id == stat_id).first()
        
        if not stat:
            # 如果找不到记录，重定向到IMVU首页
            return RedirectResponse(url="https://www.imvu.com", status_code=302)
        
        # 获取产品信息
        products = json.loads(stat.products_json) if stat.products_json else []
        
        if product_index < 0 or product_index >= len(products):
            # 产品索引无效，重定向到IMVU首页
            return RedirectResponse(url="https://www.imvu.com", status_code=302)
        
        product = products[product_index]
        original_link = product.get("link", "https://www.imvu.com")
        product_name = product.get("name", "")
        
        # 记录点击
        click = PromoCardClick(
            stat_id=stat_id,
            product_index=product_index,
            product_name=product_name[:255],
            original_link=original_link[:500],
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")[:500],
            referrer=request.headers.get("referer", "")[:500]
        )
        
        db.add(click)
        
        # 更新卡片统计
        stat.total_clicks = (stat.total_clicks or 0) + 1
        stat.last_click_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Promo click tracked: stat_id={stat_id}, product={product_name}, link={original_link}")
        
        # 重定向到实际链接
        return RedirectResponse(url=original_link, status_code=302)
        
    except Exception as e:
        logger.error(f"Track click error: {e}")
        db.rollback()
        # 出错也重定向到IMVU首页
        return RedirectResponse(url="https://www.imvu.com", status_code=302)


@router.get("/stats/overview")
async def get_stats_overview(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取统计数据概览
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 总生成次数
        total_cards = db.query(func.count(PromoCardStat.id)).filter(
            PromoCardStat.created_at >= start_date
        ).scalar()
        
        # 总点击次数
        total_clicks = db.query(func.count(PromoCardClick.id)).filter(
            PromoCardClick.clicked_at >= start_date
        ).scalar()
        
        # 热门卡片（按点击量排序）
        top_cards = db.query(
            PromoCardStat.id,
            PromoCardStat.card_title,
            PromoCardStat.total_clicks,
            PromoCardStat.created_at
        ).filter(
            PromoCardStat.created_at >= start_date
        ).order_by(
            PromoCardStat.total_clicks.desc()
        ).limit(10).all()
        
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
        
        return {
            "success": True,
            "data": {
                "total_cards": total_cards,
                "total_clicks": total_clicks,
                "period_days": days,
                "top_cards": [
                    {
                        "id": c.id,
                        "title": c.card_title,
                        "clicks": c.total_clicks or 0,
                        "created_at": c.created_at.isoformat() if c.created_at else None
                    }
                    for c in top_cards
                ],
                "daily_cards": [{"date": str(d.date), "count": d.count} for d in daily_cards],
                "daily_clicks": [{"date": str(d.date), "count": d.count} for d in daily_clicks]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/stats/{stat_id}")
async def get_card_stats(
    stat_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个卡片的详细统计
    """
    try:
        stat = db.query(PromoCardStat).filter(PromoCardStat.id == stat_id).first()
        
        if not stat:
            return {"success": False, "error": "Card not found"}
        
        # 获取该卡片的点击记录
        clicks = db.query(PromoCardClick).filter(
            PromoCardClick.stat_id == stat_id
        ).order_by(PromoCardClick.clicked_at.desc()).limit(100).all()
        
        # 按产品统计点击
        products = json.loads(stat.products_json) if stat.products_json else []
        product_clicks = {}
        for click in clicks:
            idx = click.product_index
            if idx not in product_clicks:
                product_clicks[idx] = 0
            product_clicks[idx] += 1
        
        return {
            "success": True,
            "data": {
                "id": stat.id,
                "title": stat.card_title,
                "style": stat.style,
                "color": stat.color,
                "product_count": stat.product_count,
                "total_clicks": stat.total_clicks or 0,
                "created_at": stat.created_at.isoformat() if stat.created_at else None,
                "last_click_at": stat.last_click_at.isoformat() if stat.last_click_at else None,
                "products": [
                    {
                        "name": p.get("name", ""),
                        "clicks": product_clicks.get(i, 0)
                    }
                    for i, p in enumerate(products)
                ],
                "recent_clicks": [
                    {
                        "product_name": c.product_name,
                        "clicked_at": c.clicked_at.isoformat() if c.clicked_at else None
                    }
                    for c in clicks[:20]
                ]
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
                    "total_clicks": s.total_clicks or 0,
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
