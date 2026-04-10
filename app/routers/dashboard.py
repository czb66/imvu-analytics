"""
仪表盘路由 - 提供仪表盘数据
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
import logging
import time
from functools import lru_cache

from app.database import get_db_context, ProductDataRepository
from app.services.analytics import AnalyticsService
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])

# 缓存相关（按用户ID隔离）
_dashboard_cache = {}


def _product_to_dict(p) -> dict:
    """将ProductData对象转换为字典"""
    return {
        'product_id': p.product_id,
        'product_name': p.product_name,
        'price': p.price or 0,
        'profit': p.profit or 0,
        'visible': p.visible or 'N',
        'direct_sales': p.direct_sales or 0,
        'indirect_sales': p.indirect_sales or 0,
        'promoted_sales': p.promoted_sales or 0,
        'cart_adds': p.cart_adds or 0,
        'wishlist_adds': p.wishlist_adds or 0,
        'organic_impressions': p.organic_impressions or 0,
        'paid_impressions': p.paid_impressions or 0,
    }


def _get_cached_products(user_id: int = None):
    """获取产品数据（带缓存，按用户隔离）"""
    cache_key = str(user_id) if user_id else "anonymous"
    current_time = time.time()
    
    # 检查缓存是否有效
    if cache_key in _dashboard_cache:
        cache_entry = _dashboard_cache[cache_key]
        if cache_entry["data"] is not None:
            if current_time - cache_entry["timestamp"] < cache_entry["ttl"]:
                logger.debug(f"用户 {cache_key} 使用缓存的产品数据")
                return cache_entry["data"]
    
    # 从数据库获取
    logger.info(f"用户 {cache_key} 从数据库加载产品数据")
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            _dashboard_cache[cache_key] = {
                "data": [],
                "timestamp": current_time,
                "ttl": 60
            }
            return []
        
        product_dicts = [_product_to_dict(p) for p in products]
    
    # 更新缓存
    _dashboard_cache[cache_key] = {
        "data": product_dicts,
        "timestamp": current_time,
        "ttl": 60
    }
    logger.info(f"用户 {cache_key} 已缓存 {len(product_dicts)} 个产品数据")
    
    return product_dicts


def _clear_cache():
    """清除缓存（所有用户）"""
    global _dashboard_cache
    _dashboard_cache = {}
    logger.debug("仪表盘所有缓存已清除")


def _clear_user_cache(user_id: int = None):
    """清除指定用户的缓存"""
    cache_key = str(user_id) if user_id else "anonymous"
    if cache_key in _dashboard_cache:
        del _dashboard_cache[cache_key]
    logger.debug(f"用户 {cache_key} 的仪表盘缓存已清除")


@router.get("/summary")
async def get_summary(current_user: dict = Depends(require_subscription)):
    """获取核心指标汇总"""
    start_time = time.time()
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 获取汇总数据 - 开始")
    
    try:
        product_dicts = _get_cached_products(user_id=user_id)
        
        if not product_dicts:
            elapsed = time.time() - start_time
            logger.info(f"[API] 用户 {current_user.get('email')} 获取汇总数据 - 完成(无数据) 耗时: {elapsed:.3f}s")
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
        
        analytics = AnalyticsService(product_dicts)
        summary = analytics.get_summary_metrics()
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 获取汇总数据 - 成功 耗时: {elapsed:.3f}s")
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 获取汇总数据 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
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


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    metric: str = Query("profit", regex="^(profit|sales|price)$"),
    current_user: dict = Depends(require_subscription)
):
    """
    获取Top产品列表
    
    - **limit**: 返回数量（默认10）
    - **metric**: 排序指标（profit/sales/price）
    """
    start_time = time.time()
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 获取Top产品 limit={limit} metric={metric} - 开始")
    
    try:
        product_dicts = _get_cached_products(user_id=user_id)
        
        if not product_dicts:
            elapsed = time.time() - start_time
            logger.info(f"[API] 用户 {current_user.get('email')} 获取Top产品 - 完成(无数据) 耗时: {elapsed:.3f}s")
            return {"success": True, "data": []}
        
        analytics = AnalyticsService(product_dicts)
        top_products = analytics.get_top_products(limit, metric)
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 获取Top产品 - 成功 返回:{len(top_products)} 耗时: {elapsed:.3f}s")
        
        return {
            "success": True,
            "data": top_products
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 获取Top产品 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e), "data": []}


@router.get("/visibility")
async def get_visibility_analysis(current_user: dict = Depends(require_subscription)):
    """获取可见性分析（可见 vs 不可见产品对比）"""
    start_time = time.time()
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 获取可见性分析 - 开始")
    
    try:
        product_dicts = _get_cached_products(user_id=user_id)
        
        if not product_dicts:
            elapsed = time.time() - start_time
            logger.info(f"[API] 用户 {current_user.get('email')} 获取可见性分析 - 完成(无数据) 耗时: {elapsed:.3f}s")
            return {"success": True, "data": {}}
        
        analytics = AnalyticsService(product_dicts)
        result = analytics.get_visibility_analysis()
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 获取可见性分析 - 成功 耗时: {elapsed:.3f}s")
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 获取可见性分析 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e), "data": {}}


@router.get("/traffic")
async def get_traffic_analysis(current_user: dict = Depends(require_subscription)):
    """获取流量分析（自然流量 vs 付费流量）"""
    start_time = time.time()
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 获取流量分析 - 开始")
    
    try:
        product_dicts = _get_cached_products(user_id=user_id)
        
        if not product_dicts:
            elapsed = time.time() - start_time
            logger.info(f"[API] 用户 {current_user.get('email')} 获取流量分析 - 完成(无数据) 耗时: {elapsed:.3f}s")
            return {"success": True, "data": {}}
        
        analytics = AnalyticsService(product_dicts)
        result = analytics.get_traffic_analysis()
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 获取流量分析 - 成功 耗时: {elapsed:.3f}s")
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 获取流量分析 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e), "data": {}}


@router.get("/products")
async def get_products(
    visible: Optional[str] = Query(None, regex="^(Y|N)$"),
    product_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_subscription)
):
    """
    获取产品列表（支持筛选）
    
    - **visible**: 筛选可见性（Y/N）
    - **product_id**: 筛选产品ID
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    start_time = time.time()
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 获取产品列表 visible={visible} product_id={product_id} limit={limit} offset={offset} - 开始")
    
    try:
        with get_db_context() as db:
            repo = ProductDataRepository(db)
            
            if product_id:
                product = repo.get_by_id(product_id)
                products = [product] if product else []
            elif visible:
                products = repo.get_visible_products(visible, user_id=user_id)
            else:
                products = repo.get_all(user_id=user_id)
        
        # 分页
        total = len(products)
        products = products[offset:offset + limit]
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 获取产品列表 - 成功 总数:{total} 返回:{len(products)} 耗时: {elapsed:.3f}s")
        
        return {
            "success": True,
            "data": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "products": [_product_to_dict(p) for p in products]
            }
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 获取产品列表 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": {
                "total": 0,
                "limit": limit,
                "offset": offset,
                "products": []
            }
        }


@router.post("/refresh")
async def refresh_cache(current_user: dict = Depends(require_subscription)):
    """刷新仪表盘缓存"""
    logger.info(f"[API] 用户 {current_user.get('email')} 刷新仪表盘缓存 - 开始")
    _clear_user_cache(user_id=current_user.get('id'))
    logger.info(f"[API] 用户 {current_user.get('email')} 刷新仪表盘缓存 - 完成")
    return {"success": True, "message": "缓存已刷新"}
