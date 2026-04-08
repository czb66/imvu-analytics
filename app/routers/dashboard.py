"""
仪表盘路由 - 提供仪表盘数据
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from app.database import get_db, ProductDataRepository
from app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/summary")
async def get_summary():
    """获取核心指标汇总"""
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all()
        
        if not products:
            return {
                "success": True,
                "data": {
                    "total_sales": 0,
                    "total_profit": 0,
                    "total_orders": 0,
                    "avg_conversion_rate": 0,
                    "total_products": 0,
                    "visible_products": 0,
                    "hidden_products": 0,
                }
            }
        
        # 转换为字典列表
        product_dicts = [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'price': p.price,
                'profit': p.profit,
                'visible': p.visible,
                'direct_sales': p.direct_sales,
                'indirect_sales': p.indirect_sales,
                'promoted_sales': p.promoted_sales,
                'cart_adds': p.cart_adds,
                'wishlist_adds': p.wishlist_adds,
                'organic_impressions': p.organic_impressions,
                'paid_impressions': p.paid_impressions,
            }
            for p in products
        ]
        
        analytics = AnalyticsService(product_dicts)
        summary = analytics.get_summary_metrics()
        
        return {
            "success": True,
            "data": summary
        }


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    metric: str = Query("profit", regex="^(profit|sales|price)$")
):
    """
    获取Top产品列表
    
    - **limit**: 返回数量（默认10）
    - **metric**: 排序指标（profit/sales/price）
    """
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all()
        
        if not products:
            return {"success": True, "data": []}
        
        product_dicts = [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'price': p.price,
                'profit': p.profit,
                'visible': p.visible,
                'direct_sales': p.direct_sales,
                'indirect_sales': p.indirect_sales,
                'promoted_sales': p.promoted_sales,
                'cart_adds': p.cart_adds,
                'wishlist_adds': p.wishlist_adds,
                'organic_impressions': p.organic_impressions,
                'paid_impressions': p.paid_impressions,
            }
            for p in products
        ]
        
        analytics = AnalyticsService(product_dicts)
        top_products = analytics.get_top_products(limit, metric)
        
        return {
            "success": True,
            "data": top_products
        }


@router.get("/visibility")
async def get_visibility_analysis():
    """获取可见性分析（可见 vs 不可见产品对比）"""
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all()
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_visibility_analysis()
        }


@router.get("/traffic")
async def get_traffic_analysis():
    """获取流量分析（自然流量 vs 付费流量）"""
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all()
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_traffic_analysis()
        }


@router.get("/products")
async def get_products(
    visible: Optional[str] = Query(None, regex="^(Y|N)$"),
    product_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    获取产品列表（支持筛选）
    
    - **visible**: 筛选可见性（Y/N）
    - **product_id**: 筛选产品ID
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        
        if product_id:
            product = repo.get_by_id(product_id)
            products = [product] if product else []
        elif visible:
            products = repo.get_visible_products(visible)
        else:
            products = repo.get_all()
        
        # 分页
        total = len(products)
        products = products[offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "products": [_product_to_dict(p) for p in products]
            }
        }


def _product_to_dict(p) -> dict:
    """将产品对象转换为字典"""
    return {
        'product_id': p.product_id,
        'product_name': p.product_name,
        'price': p.price,
        'profit': p.profit,
        'visible': p.visible,
        'direct_sales': p.direct_sales,
        'indirect_sales': p.indirect_sales,
        'promoted_sales': p.promoted_sales,
        'cart_adds': p.cart_adds,
        'wishlist_adds': p.wishlist_adds,
        'organic_impressions': p.organic_impressions,
        'paid_impressions': p.paid_impressions,
    }
