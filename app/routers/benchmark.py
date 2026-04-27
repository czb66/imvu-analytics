"""
竞品分析路由 - 提供行业基准和排名相关API
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import logging

from app.database import get_db, ProductDataRepository, get_db_context
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription
from app.services.benchmark import benchmark_service
from app.services.activity_tracker import activity_tracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/benchmark", tags=["竞品分析"])


class ProductRankingRequest(BaseModel):
    """产品排名请求"""
    product_id: str
    product_name: Optional[str] = None
    price: float = 0
    profit: float = 0
    direct_sales: float = 0
    indirect_sales: float = 0
    visible: str = 'N'


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
    }


@router.get("/overview")
async def get_category_overview(
    category: Optional[str] = Query(None, description="产品类别"),
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    获取行业概览
    
    返回所有类别的行业基准数据
    """
    try:
        # 记录活动
        activity_tracker.log_activity(
            db, current_user.get('id'), 'view_benchmark_overview',
            metadata={'category': category}
        )
        
        result = benchmark_service.get_category_overview(db, category)
        return result
        
    except Exception as e:
        logger.error(f"获取行业概览失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/product-ranking")
async def get_product_ranking(
    request: ProductRankingRequest,
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    获取单个产品在行业中的排名
    
    返回该产品相对于行业基准的各项指标百分位排名
    """
    try:
        # 记录活动
        activity_tracker.log_activity(
            db, current_user.get('id'), 'view_product_ranking',
            resource_type='product',
            metadata={'product_id': request.product_id}
        )
        
        product_data = request.dict()
        result = benchmark_service.get_product_ranking(
            db=db,
            user_id=current_user.get('id'),
            product_data=product_data
        )
        
        if not result.get('success', False):
            return result
        
        return result
        
    except Exception as e:
        logger.error(f"获取产品排名失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/product-rankings")
async def get_all_product_rankings(
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    获取用户所有产品的行业排名
    
    返回所有产品相对于行业基准的各项指标百分位排名
    """
    try:
        user_id = current_user.get('id')
        
        # 获取用户所有产品
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {
                'success': False,
                'message': '暂无产品数据',
                'products': []
            }
        
        # 计算每个产品的排名
        rankings = []
        for product in products:
            product_data = _product_to_dict(product)
            ranking = benchmark_service.get_product_ranking(
                db=db,
                user_id=user_id,
                product_data=product_data
            )
            if ranking.get('success', False):
                rankings.append(ranking)
        
        return {
            'success': True,
            'total_products': len(products),
            'ranked_products': len(rankings),
            'products': rankings
        }
        
    except Exception as e:
        logger.error(f"获取所有产品排名失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/insights")
async def get_competitive_insights(
    language: str = Query('zh', description="语言: zh/en"),
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    获取竞争洞察建议
    
    基于用户产品与行业基准的对比，生成优化建议
    """
    try:
        user_id = current_user.get('id')
        
        # 获取用户所有产品
        repo = ProductDataRepository(db)
        products = repo.get_all(user_id=user_id)
        
        if not products:
            return {
                'success': False,
                'message': '暂无产品数据',
                'insights': []
            }
        
        # 转换为字典列表
        product_dicts = [_product_to_dict(p) for p in products]
        
        # 生成洞察
        insights = benchmark_service.get_competitive_insights(
            db=db,
            user_id=user_id,
            products=product_dicts,
            language=language
        )
        
        # 记录活动
        activity_tracker.log_activity(
            db, user_id, 'view_competitive_insights',
            metadata={'insights_count': len(insights)}
        )
        
        return {
            'success': True,
            'total_products': len(products),
            'insights': insights
        }
        
    except Exception as e:
        logger.error(f"获取竞争洞察失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.post("/calculate")
async def trigger_benchmark_calculation(
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    手动触发行业基准计算（仅管理员）
    """
    try:
        # 检查是否是管理员
        from app.models import User
        user = db.query(User).filter(User.id == current_user.get('id')).first()
        
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="仅管理员可以手动触发计算")
        
        result = benchmark_service.calculate_benchmarks(db)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手动触发基准计算失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")


@router.get("/categories")
async def get_available_categories(
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    获取可用的产品类别列表
    """
    try:
        categories = [
            {'id': 'general', 'name_zh': '通用', 'name_en': 'General'},
            {'id': 'popular', 'name_zh': '热门', 'name_en': 'Popular'},
            {'id': 'budget', 'name_zh': '低价', 'name_en': 'Budget'},
            {'id': 'premium', 'name_zh': '高端', 'name_en': 'Premium'},
        ]
        
        # 获取每个类别的数据是否足够
        for cat in categories:
            overview = benchmark_service.get_category_overview(db, cat['id'])
            cat['has_data'] = overview.get('success', False) and overview.get('categories', [])
            if cat['has_data']:
                cat['sample_size'] = overview['categories'][0].get('sample_size', 0) if overview['categories'] else 0
        
        return {
            'success': True,
            'categories': categories
        }
        
    except Exception as e:
        logger.error(f"获取类别列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")
