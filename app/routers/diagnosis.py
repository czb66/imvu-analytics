"""
诊断路由 - 提供深度诊断数据
"""

from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Optional
import logging

from app.database import get_db_context, ProductDataRepository
from app.services.analytics import AnalyticsService
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription
from app.services.activity_tracker import activity_tracker
from app.core.rate_limiter import check_tiered_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/diagnosis", tags=["诊断"])


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


@router.get("/price-range")
async def get_price_range_analysis(
    request: Request,
    current_user: dict = Depends(require_subscription)
):
    """
    价格区间分析（分层限流：free=10/hour, pro=60/hour）
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("diagnosis", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    
    user_id = current_user.get('id')
    
    # 记录查看诊断行为
    activity_tracker.log_activity(None, user_id, 'view_diagnosis', metadata={'analysis_type': 'price_range'})
    
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": []}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_price_range_analysis()
        }


@router.get("/conversion-funnel")
async def get_conversion_funnel(current_user: dict = Depends(require_subscription)):
    """转化漏斗分析"""
    user_id = current_user.get('id')
    
    # 记录查看诊断行为
    activity_tracker.log_activity(None, user_id, 'view_diagnosis', metadata={'analysis_type': 'conversion_funnel'})
    
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_conversion_funnel()
        }


@router.get("/high-profit")
async def get_high_profit_products(
    margin_threshold: Optional[float] = Query(None, ge=0, le=1),
    current_user: dict = Depends(require_subscription)
):
    """
    高利润产品识别
    
    - **margin_threshold**: 利润率阈值（默认0.3，即30%）
    """
    user_id = current_user.get('id')
    
    # 记录查看诊断行为
    activity_tracker.log_activity(None, user_id, 'view_diagnosis', metadata={'analysis_type': 'high_profit'})
    
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": []}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_high_profit_products(margin_threshold)
        }


@router.get("/traffic-comparison")
async def get_traffic_comparison(current_user: dict = Depends(require_subscription)):
    """自然流量 vs 付费流量效果对比"""
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_traffic_analysis()
        }


@router.get("/roi")
async def get_roi_analysis(current_user: dict = Depends(require_subscription)):
    """ROI分析"""
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_roi_analysis()
        }


@router.get("/user-behavior")
async def get_user_behavior_analysis(current_user: dict = Depends(require_subscription)):
    """用户行为转化分析"""
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": {}}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_user_behavior_analysis()
        }


@router.get("/low-conversion-alerts")
async def get_low_conversion_alerts(
    threshold: Optional[float] = Query(None, ge=0),
    current_user: dict = Depends(require_subscription)
):
    """
    高加购低转化产品预警
    
    - **threshold**: 转化率阈值
    """
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": []}
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.get_low_conversion_alerts(threshold)
        }


@router.get("/anomalies")
async def detect_anomalies(
    threshold: Optional[float] = Query(None, ge=1),
    current_user: dict = Depends(require_subscription)
):
    """
    销量异常检测
    
    - **threshold**: 标准差倍数阈值（默认2.0）
    """
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {"success": True, "data": []}
        
        if len(products) < 3:
            return {
                "success": True,
                "data": [],
                "message": "数据量少于3条，无法进行异常检测"
            }
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": analytics.detect_sales_anomalies(threshold)
        }


@router.get("/full-report")
async def get_full_diagnosis_report(current_user: dict = Depends(require_subscription)):
    """获取完整诊断报告"""
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {
                "success": True,
                "data": {
                    "summary": {},
                    "price_range": [],
                    "conversion_funnel": {},
                    "high_profit": [],
                    "roi": {},
                    "anomalies": [],
                    "low_conversion_alerts": []
                }
            }
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        return {
            "success": True,
            "data": {
                "summary": analytics.get_summary_metrics(),
                "price_range": analytics.get_price_range_analysis(),
                "conversion_funnel": analytics.get_conversion_funnel(),
                "high_profit": analytics.get_high_profit_products(),
                "roi": analytics.get_roi_analysis(),
                "anomalies": analytics.detect_sales_anomalies(),
                "low_conversion_alerts": analytics.get_low_conversion_alerts(),
                "visibility": analytics.get_visibility_analysis(),
                "traffic": analytics.get_traffic_analysis(),
            }
        }
