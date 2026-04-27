"""
数据对比路由 - 多数据集对比分析
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db_context, ProductDataRepository, DatasetRepository
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription
from app.services.activity_tracker import activity_tracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/compare", tags=["数据对比"])


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


def _calculate_metrics(products: list) -> dict:
    """计算产品列表的核心指标"""
    if not products:
        return {
            'total_sales': 0,
            'total_profit': 0,
            'total_products': 0,
            'visible_products': 0,
            'hidden_products': 0,
            'total_cart_adds': 0,
            'total_wishlist_adds': 0,
            'total_impressions': 0,
        }
    
    total_sales = sum(p.get('direct_sales', 0) + p.get('indirect_sales', 0) + p.get('promoted_sales', 0) for p in products)
    total_profit = sum(p.get('profit', 0) for p in products)
    visible_products = sum(1 for p in products if p.get('visible') == 'Y')
    total_cart_adds = sum(p.get('cart_adds', 0) for p in products)
    total_wishlist_adds = sum(p.get('wishlist_adds', 0) for p in products)
    total_impressions = sum(p.get('organic_impressions', 0) + p.get('paid_impressions', 0) for p in products)
    
    return {
        'total_sales': round(total_sales, 2),
        'total_profit': round(total_profit, 2),
        'total_products': len(products),
        'visible_products': visible_products,
        'hidden_products': len(products) - visible_products,
        'total_cart_adds': round(total_cart_adds, 2),
        'total_wishlist_adds': round(total_wishlist_adds, 2),
        'total_impressions': round(total_impressions, 2),
    }


def _calculate_change(current: float, previous: float) -> dict:
    """计算变化百分比"""
    if previous == 0:
        if current == 0:
            return {'absolute': 0, 'percentage': 0, 'direction': 'unchanged'}
        return {'absolute': current, 'percentage': 100, 'direction': 'up'}
    
    change = current - previous
    percentage = (change / previous) * 100
    
    if change > 0:
        direction = 'up'
    elif change < 0:
        direction = 'down'
    else:
        direction = 'unchanged'
    
    return {
        'absolute': round(change, 2),
        'percentage': round(percentage, 2),
        'direction': direction
    }


def _get_top_products(products: list, limit: int = 10) -> list:
    """获取Top产品（按总销量排序）"""
    # 计算总销量
    for p in products:
        p['total_sales'] = p.get('direct_sales', 0) + p.get('indirect_sales', 0) + p.get('promoted_sales', 0)
    sorted_products = sorted(products, key=lambda x: x.get('total_sales', 0), reverse=True)
    return sorted_products[:limit]


def _compare_rankings(current_products: list, previous_products: list, limit: int = 10) -> dict:
    """比较产品排名变化"""
    current_top = {p['product_id']: {'rank': i+1, 'product': p} 
                   for i, p in enumerate(_get_top_products(current_products, limit))}
    previous_top = {p['product_id']: {'rank': i+1, 'product': p} 
                    for i, p in enumerate(_get_top_products(previous_products, limit))}
    
    current_ids = set(current_top.keys())
    previous_ids = set(previous_top.keys())
    
    # 新进入 Top 10 的产品
    new_entries = []
    for pid in current_ids - previous_ids:
        new_entries.append({
            'product_id': pid,
            'product_name': current_top[pid]['product']['product_name'],
            'sales': current_top[pid]['product'].get('total_sales', 0),
            'rank': current_top[pid]['rank']
        })
    
    # 退出 Top 10 的产品
    dropped_out = []
    for pid in previous_ids - current_ids:
        dropped_out.append({
            'product_id': pid,
            'product_name': previous_top[pid]['product']['product_name'],
            'old_rank': previous_top[pid]['rank']
        })
    
    # 排名上升的产品 (improved)
    improved = []
    for pid in current_ids & previous_ids:
        old_rank = previous_top[pid]['rank']
        new_rank = current_top[pid]['rank']
        if new_rank < old_rank:
            improved.append({
                'product_id': pid,
                'product_name': current_top[pid]['product']['product_name'],
                'sales': current_top[pid]['product'].get('total_sales', 0),
                'profit': current_top[pid]['product'].get('profit', 0),
                'old_rank': old_rank,
                'new_rank': new_rank,
                'change': old_rank - new_rank
            })
    
    # 排名下降的产品 (declined)
    declined = []
    for pid in current_ids & previous_ids:
        old_rank = previous_top[pid]['rank']
        new_rank = current_top[pid]['rank']
        if new_rank > old_rank:
            declined.append({
                'product_id': pid,
                'product_name': current_top[pid]['product']['product_name'],
                'sales': current_top[pid]['product'].get('total_sales', 0),
                'profit': current_top[pid]['product'].get('profit', 0),
                'old_rank': old_rank,
                'new_rank': new_rank,
                'change': new_rank - old_rank
            })
    
    # 同时保留旧格式以兼容现有代码
    return {
        'improved': improved,
        'declined': declined,
        'new_entries': new_entries,
        'dropped_out': dropped_out,
        # 兼容旧格式
        'rank_up': sorted(improved, key=lambda x: x['change'], reverse=True)[:5],
        'rank_down': sorted(declined, key=lambda x: x['change'], reverse=True)[:5],
        'new_in_top': [{'product_id': e['product_id'], 'rank': e['rank'], 'product': current_top.get(e['product_id'], {}).get('product', {})} for e in new_entries[:5]],
        'exited_top': [{'product_id': d['product_id'], 'old_rank': d['old_rank'], 'product': previous_top.get(d['product_id'], {}).get('product', {})} for d in dropped_out[:5]]
    }


@router.get("/datasets")
async def get_datasets(current_user: dict = Depends(require_subscription)):
    """获取所有数据集列表"""
    user_id = current_user.get('id')
    try:
        with get_db_context() as db:
            repo = DatasetRepository(db)
            datasets = repo.get_all(user_id=user_id)
            
            return {
                "success": True,
                "data": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "upload_time": d.upload_time.isoformat() if d.upload_time else None,
                        "record_count": d.record_count
                    }
                    for d in datasets
                ]
            }
    except Exception as e:
        logger.error(f"获取数据集列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def compare_datasets(
    dataset_ids: List[int] = Query(..., min_length=2, max_length=10),
    current_user: dict = Depends(require_subscription)
):
    """
    对比多个数据集
    
    - **dataset_ids**: 数据集ID列表（2-10个）
    """
    user_id = current_user.get('id')
    
    # 记录查看对比行为
    activity_tracker.log_activity(None, user_id, 'view_compare', metadata={'dataset_count': len(dataset_ids)})
    
    if len(dataset_ids) < 2 or len(dataset_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="请选择2-10个数据集进行对比"
        )
    
    try:
        with get_db_context() as db:
            dataset_repo = DatasetRepository(db)
            product_repo = ProductDataRepository(db)
            
            # 获取数据集信息（仅获取属于当前用户的数据集）
            datasets = []
            dataset_products = {}
            
            for ds_id in dataset_ids:
                dataset = dataset_repo.get_by_id(ds_id)
                if not dataset:
                    raise HTTPException(
                        status_code=404,
                        detail=f"数据集 {ds_id} 不存在"
                    )
                
                # 数据隔离：检查数据集是否属于当前用户
                if dataset.user_id != user_id:
                    raise HTTPException(
                        status_code=403,
                        detail="无权访问该数据集"
                    )
                
                products = product_repo.get_by_dataset(ds_id)
                product_dicts = [_product_to_dict(p) for p in products]
                
                datasets.append({
                    "id": dataset.id,
                    "name": dataset.name,
                    "upload_time": dataset.upload_time.isoformat() if dataset.upload_time else None,
                    "record_count": len(product_dicts)
                })
                dataset_products[ds_id] = product_dicts
            
            # 计算每个数据集的核心指标
            metrics_comparison = []
            for ds_id in dataset_ids:
                metrics = _calculate_metrics(dataset_products[ds_id])
                metrics_comparison.append({
                    "dataset_id": ds_id,
                    "metrics": metrics
                })
            
            # 计算变化趋势（如果有多个数据集）
            trends = []
            for i in range(1, len(dataset_ids)):
                prev_metrics = _calculate_metrics(dataset_products[dataset_ids[i-1]])
                curr_metrics = _calculate_metrics(dataset_products[dataset_ids[i]])
                
                trends.append({
                    "from_dataset": datasets[i-1]['name'],
                    "to_dataset": datasets[i]['name'],
                    "sales_change": _calculate_change(curr_metrics['total_sales'], prev_metrics['total_sales']),
                    "profit_change": _calculate_change(curr_metrics['total_profit'], prev_metrics['total_profit']),
                    "products_change": _calculate_change(curr_metrics['total_products'], prev_metrics['total_products']),
                })
            
            # 每个数据集的 Top 10 产品列表
            datasets_top_products = []
            for ds_id in dataset_ids:
                top_products = _get_top_products(dataset_products[ds_id], 10)
                datasets_top_products.append({
                    "dataset_id": ds_id,
                    "top_products": [
                        {
                            "product_id": p['product_id'],
                            "product_name": p['product_name'],
                            "sales": p.get('total_sales', 0),
                            "profit": p.get('profit', 0),
                            "rank": i + 1
                        }
                        for i, p in enumerate(top_products)
                    ]
                })
            
            # 排名变化分析
            ranking_changes = []
            if len(dataset_ids) >= 2:
                comparison = _compare_rankings(
                    dataset_products[dataset_ids[-1]],  # 最新数据
                    dataset_products[dataset_ids[0]]    # 最早数据
                )
                ranking_changes = comparison
            
            # 趋势图表数据
            trend_chart_data = {
                "labels": [d["name"] for d in datasets],
                "sales": [_calculate_metrics(dataset_products[ds_id])["total_sales"] for ds_id in dataset_ids],
                "profit": [_calculate_metrics(dataset_products[ds_id])["total_profit"] for ds_id in dataset_ids],
                "products": [_calculate_metrics(dataset_products[ds_id])["total_products"] for ds_id in dataset_ids],
            }
            
            return {
                "success": True,
                "data": {
                    "datasets": datasets,
                    "datasets_top_products": datasets_top_products,
                    "metrics_comparison": metrics_comparison,
                    "trends": trends,
                    "ranking_changes": ranking_changes,
                    "trend_chart_data": trend_chart_data
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据对比失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trends(
    limit: int = Query(10, ge=2, le=20),
    current_user: dict = Depends(get_current_user)
):
    """
    获取趋势分析数据
    
    - **limit**: 返回的数据集数量（默认10）
    """
    user_id = current_user.get('id')
    try:
        with get_db_context() as db:
            dataset_repo = DatasetRepository(db)
            product_repo = ProductDataRepository(db)
            
            datasets = dataset_repo.get_latest(limit, user_id=user_id)
            
            if len(datasets) < 2:
                return {
                    "success": True,
                    "data": {
                        "message": "数据不足，至少需要2个数据集才能进行趋势分析",
                        "datasets": [],
                        "trend_data": []
                    }
                }
            
            # 获取每个数据集的指标
            trend_data = []
            for dataset in datasets:
                products = product_repo.get_by_dataset(dataset.id)
                product_dicts = [_product_to_dict(p) for p in products]
                metrics = _calculate_metrics(product_dicts)
                
                trend_data.append({
                    "dataset_id": dataset.id,
                    "dataset_name": dataset.name,
                    "upload_time": dataset.upload_time.isoformat() if dataset.upload_time else None,
                    "metrics": metrics
                })
            
            # 反转顺序，使最早的在前
            trend_data.reverse()
            
            # 计算每个数据集相对于前一个的变化
            enriched_trend = []
            for i, td in enumerate(trend_data):
                change = None
                if i > 0:
                    prev = trend_data[i-1]['metrics']
                    curr = td['metrics']
                    change = {
                        "sales_change": _calculate_change(curr['total_sales'], prev['total_sales']),
                        "profit_change": _calculate_change(curr['total_profit'], prev['total_profit']),
                    }
                
                enriched_trend.append({
                    **td,
                    "change": change
                })
            
            return {
                "success": True,
                "data": {
                    "datasets": [
                        {"id": d.id, "name": d.name, "upload_time": d.upload_time.isoformat() if d.upload_time else None}
                        for d in reversed(datasets)
                    ],
                    "trend_data": enriched_trend
                }
            }
            
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dataset/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除指定数据集"""
    user_id = current_user.get('id')
    try:
        with get_db_context() as db:
            dataset_repo = DatasetRepository(db)
            dataset = dataset_repo.get_by_id(dataset_id)
            
            if not dataset:
                raise HTTPException(
                    status_code=404,
                    detail=f"数据集 {dataset_id} 不存在"
                )
            
            # 数据隔离：检查数据集是否属于当前用户
            if dataset.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="无权删除该数据集"
                )
            
            dataset_repo.delete(dataset_id)
            
            return {
                "success": True,
                "message": f"数据集 '{dataset.name}' 已删除"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除数据集失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
