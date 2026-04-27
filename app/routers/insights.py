"""
AI洞察路由 - 提供AI洞察相关API
使用内存缓存层提升性能，AI洞察结果缓存30分钟
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Response
from pydantic import BaseModel
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging
import time

from app.database import get_db_context, get_db, ProductDataRepository, UserRepository
from app.services.analytics import AnalyticsService
from app.services.insights import insights_service
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription, is_whitelisted
from app.services.activity_tracker import activity_tracker
from app.services.cache import get_cache
from app.core.rate_limiter import check_tiered_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/insights", tags=["AI洞察"])

# AI洞察缓存 TTL（秒）- 30分钟，AI计算较耗时应缓存
INSIGHT_CACHE_TTL = 1800


def check_subscription_required(user_id: int, user_email: str = None) -> bool:
    """检查用户是否需要订阅才能使用AI洞察
    
    白名单用户自动通过
    """
    with get_db_context() as db:
        # 白名单用户跳过检查
        if user_email and is_whitelisted(user_email, db):
            return True
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if user and (user.is_subscribed or is_whitelisted(user.email, db)):
            return True
        return False


class DashboardInsightsRequest(BaseModel):
    """仪表盘洞察请求"""
    language: str = 'zh'


class DiagnosisInsightsRequest(BaseModel):
    """诊断洞察请求"""
    language: str = 'zh'


class CompareInsightsRequest(BaseModel):
    """对比洞察请求"""
    dataset_ids: List[int]
    language: str = 'zh'


def _product_to_dict(p) -> dict:
    """将产品对象转换为字典"""
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


def _get_products_from_request(user_id: int = None, dataset_id: Optional[int] = None) -> List[Dict]:
    """从请求中获取产品数据"""
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        
        if dataset_id:
            products = repo.get_by_dataset(dataset_id)
        else:
            products = repo.get_all(user_id=user_id)
        
        return [_product_to_dict(p) for p in products]


def _get_datasets_from_request(user_id: int = None) -> List[Dict]:
    """获取数据集列表"""
    from app.models import Dataset
    from app.database import DatasetRepository
    
    with get_db_context() as db:
        repo = DatasetRepository(db)
        datasets = repo.get_all(user_id=user_id)
        return [
            {
                'id': d.id,
                'name': d.name,
                'upload_time': d.upload_time.isoformat() if d.upload_time else None,
                'record_count': d.record_count
            }
            for d in datasets
        ]


@router.post("/dashboard")
async def generate_dashboard_insights(
    request: Request,
    response: Response,
    req: DashboardInsightsRequest = None,
    current_user: dict = Depends(require_subscription)
):
    """
    生成仪表盘AI洞察（分层限流：free=5/hour, pro=30/hour）
    
    分析总体销售趋势、Top产品表现、核心指标异常
    缓存：30分钟（TTL=1800秒）
    
    注意：此功能需要订阅才能使用
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("insights", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    start_time = time.time()
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    
    # 获取语言参数
    language = req.language if req and hasattr(req, 'language') else 'zh'
    
    # 构建缓存键（包含语言参数）
    cache = get_cache()
    cache_key = f"insights:dashboard:user_{user_id}:lang_{language}"
    
    # 检查订阅状态（白名单用户自动通过）
    if not check_subscription_required(user_id, user_email):
        response.headers["X-Cache"] = "MISS"
        return {
            "success": False,
            "error": "subscription_required",
            "message": "此功能需要订阅才能使用",
            "insight": "⚠️ AI洞察功能需要订阅才能使用，请前往 /pricing 订阅"
        }
    
    # 尝试获取缓存
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {user_email} 生成仪表盘洞察 - 完成(缓存) 耗时: {elapsed:.3f}s")
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    logger.info(f"[API] 用户 {user_email} 生成仪表盘洞察 - 开始")
    
    # 记录查看洞察行为
    activity_tracker.log_activity(None, user_id, 'view_insights', metadata={'insight_type': 'dashboard', 'language': language})
    
    try:
        # 获取产品数据
        product_dicts = _get_products_from_request(user_id=user_id)
        
        if not product_dicts:
            no_data_msg = "暂无数据可分析，请先上传产品数据" if language == 'zh' else "No data to analyze, please upload product data first"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 计算汇总指标
        analytics = AnalyticsService(product_dicts)
        summary = analytics.get_summary_metrics()
        
        # 获取Top产品
        top_products = analytics.get_top_products(limit=10, metric='profit')
        
        # 生成洞察
        insight = await insights_service.generate_dashboard_insights(summary, top_products, language)
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 生成仪表盘洞察 - 完成 耗时: {elapsed:.3f}s")
        
        result = {
            "success": True,
            "insight": insight,
            "is_offline": not insights_service.is_configured(),
            "data": {
                "summary": summary,
                "top_products_count": len(top_products)
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, ttl=INSIGHT_CACHE_TTL)
        response.headers["X-Cache"] = "MISS"
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 生成仪表盘洞察 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "insight": "⚠️ 生成洞察时发生错误，请稍后重试",
            "is_offline": True
        }


@router.post("/diagnosis")
async def generate_diagnosis_insights(
    request: Request,
    response: Response,
    req: DiagnosisInsightsRequest = None,
    current_user: dict = Depends(require_subscription)
):
    """
    生成诊断AI洞察（分层限流：free=10/hour, pro=60/hour）
    
    分析销售诊断、流量漏斗、异常检测
    缓存：30分钟（TTL=1800秒）
    
    注意：此功能需要订阅才能使用
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("diagnosis", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    start_time = time.time()
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    
    # 获取语言参数
    language = req.language if req and hasattr(req, 'language') else 'zh'
    
    # 构建缓存键
    cache = get_cache()
    cache_key = f"insights:diagnosis:user_{user_id}:lang_{language}"
    
    # 检查订阅状态（白名单用户自动通过）
    if not check_subscription_required(user_id, user_email):
        response.headers["X-Cache"] = "MISS"
        return {
            "success": False,
            "error": "subscription_required",
            "message": "此功能需要订阅才能使用",
            "insight": "⚠️ AI洞察功能需要订阅才能使用，请前往 /pricing 订阅"
        }
    
    # 尝试获取缓存
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {user_email} 生成诊断洞察 - 完成(缓存) 耗时: {elapsed:.3f}s")
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    logger.info(f"[API] 用户 {user_email} 生成诊断洞察 - 开始")
    
    try:
        # 获取产品数据
        product_dicts = _get_products_from_request(user_id=user_id)
        
        if not product_dicts:
            no_data_msg = "暂无数据可诊断，请先上传产品数据" if language == 'zh' else "No data to diagnose, please upload product data first"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 计算分析数据
        analytics = AnalyticsService(product_dicts)
        
        # 销售诊断数据
        summary = analytics.get_summary_metrics()
        sales_diagnosis = {
            'total_sales': summary.get('total_sales', 0),
            'total_profit': summary.get('total_profit', 0),
            'avg_profit_margin': analytics.get_avg_profit_margin(),
            'visible_count': summary.get('visible_products', 0),
            'hidden_count': summary.get('hidden_products', 0),
        }
        
        # 漏斗数据
        funnel_data = analytics.get_conversion_funnel()
        
        # 异常检测
        anomalies = analytics.detect_sales_anomalies()
        
        # 生成洞察
        insight = await insights_service.generate_diagnosis_insights(
            sales_diagnosis, funnel_data, anomalies, language
        )
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 生成诊断洞察 - 完成 耗时: {elapsed:.3f}s")
        
        result = {
            "success": True,
            "insight": insight,
            "is_offline": not insights_service.is_configured(),
            "data": {
                "sales_diagnosis": sales_diagnosis,
                "funnel_data": funnel_data,
                "anomalies_count": len(anomalies)
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, ttl=INSIGHT_CACHE_TTL)
        response.headers["X-Cache"] = "MISS"
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_detail = f"{type(e).__name__}: {str(e)}"
        logger.error(f"[API] 用户 {current_user.get('email')} 生成诊断洞察 - 失败 耗时: {elapsed:.3f}s 错误: {error_detail}", exc_info=True)
        return {
            "success": False,
            "error": error_detail,
            "insight": f"⚠️ 生成洞察时发生错误: {error_detail}",
            "is_offline": True
        }


@router.post("/compare")
async def generate_compare_insights(
    request: Request,
    response: Response,
    req: CompareInsightsRequest,
    current_user: dict = Depends(require_subscription)
):
    """
    生成对比AI洞察（分层限流：free=10/hour, pro=60/hour）
    
    分析多数据集对比结论、排名变化、趋势总结
    缓存：30分钟（TTL=1800秒）
    
    注意：此功能需要订阅才能使用
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("compare", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    start_time = time.time()
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    
    # 获取语言参数
    language = req.language if hasattr(req, 'language') else 'zh'
    
    # 构建缓存键（基于数据集ID列表）
    dataset_ids_str = "_".join(sorted(map(str, req.dataset_ids)))
    cache = get_cache()
    cache_key = f"insights:compare:user_{user_id}:datasets_{dataset_ids_str}:lang_{language}"
    
    # 检查订阅状态（白名单用户自动通过）
    if not check_subscription_required(user_id, user_email):
        response.headers["X-Cache"] = "MISS"
        return {
            "success": False,
            "error": "subscription_required",
            "message": "此功能需要订阅才能使用",
            "insight": "⚠️ AI洞察功能需要订阅才能使用，请前往 /pricing 订阅"
        }
    
    # 尝试获取缓存
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {user_email} 生成对比洞察 - 完成(缓存) 耗时: {elapsed:.3f}s")
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    logger.info(f"[API] 用户 {user_email} 生成对比洞察 - 开始 数据集: {req.dataset_ids}")
    
    try:
        if len(req.dataset_ids) < 2:
            no_data_msg = "请至少选择2个数据集进行对比" if language == 'zh' else "Please select at least 2 datasets to compare"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 获取各数据集信息
        datasets = []
        all_products = {}
        
        with get_db_context() as db:
            from app.models import Dataset, ProductData
            from app.database import DatasetRepository
            
            dataset_repo = DatasetRepository(db)
            
            for ds_id in req.dataset_ids:
                dataset = dataset_repo.get_by_id(ds_id)
                if dataset:
                    # 数据隔离：检查数据集是否属于当前用户
                    if dataset.user_id != user_id:
                        continue
                    
                    # 获取产品数据
                    repo = ProductDataRepository(db)
                    products = repo.get_by_dataset(ds_id)
                    product_dicts = [_product_to_dict(p) for p in products]
                    
                    # 计算数据集指标
                    analytics = AnalyticsService(product_dicts) if product_dicts else None
                    summary = analytics.get_summary_metrics() if analytics else {}
                    
                    datasets.append({
                        'id': dataset.id,
                        'name': dataset.name,
                        'upload_time': dataset.upload_time.isoformat() if dataset.upload_time else None,
                        'total_sales': summary.get('total_sales', 0),
                        'total_profit': summary.get('total_profit', 0),
                        'product_count': len(product_dicts),
                        'products': product_dicts
                    })
                    
                    # 保存产品用于排名比较
                    for p in product_dicts:
                        pid = p['product_id']
                        if pid not in all_products:
                            all_products[pid] = {}
                        all_products[pid][dataset.id] = p
        
        if len(datasets) < 2:
            no_data_msg = "有效数据集不足，无法进行对比" if language == 'zh' else "Insufficient valid datasets for comparison"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 计算指标对比
        metrics_comparison = _calculate_metrics_comparison(datasets)
        
        # 计算排名变化
        rank_changes = _calculate_rank_changes(datasets)
        
        # 生成洞察
        insight = await insights_service.generate_compare_insights(
            datasets, metrics_comparison, rank_changes, language
        )
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} 生成对比洞察 - 完成 耗时: {elapsed:.3f}s")
        
        result = {
            "success": True,
            "insight": insight,
            "is_offline": not insights_service.is_configured(),
            "data": {
                "datasets_count": len(datasets),
                "metrics_comparison": metrics_comparison,
                "rank_changes_summary": {
                    'improved': len(rank_changes.get('improved', [])),
                    'declined': len(rank_changes.get('declined', [])),
                    'new_entries': len(rank_changes.get('new_entries', []))
                }
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, ttl=INSIGHT_CACHE_TTL)
        response.headers["X-Cache"] = "MISS"
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} 生成对比洞察 - 失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "insight": "⚠️ 生成洞察时发生错误，请稍后重试",
            "is_offline": True
        }


@router.post("/clear-cache")
async def clear_insights_cache(
    response: Response,
    current_user: dict = Depends(require_subscription)
):
    """清除当前用户的AI洞察缓存"""
    user_id = current_user.get('id')
    cache = get_cache()
    
    # 清除该用户的所有洞察缓存
    count = cache.delete_pattern(f"insights:*:user_{user_id}*")
    
    logger.info(f"[API] 用户 {current_user.get('email')} 清除洞察缓存 - 删除了 {count} 条")
    response.headers["X-Cache"] = "MISS"
    
    return {
        "success": True,
        "message": f"已清除 {count} 条洞察缓存"
    }


def _calculate_metrics_comparison(datasets: List[Dict]) -> Dict:
    """计算指标对比变化"""
    if len(datasets) < 2:
        return {}
    
    # 按上传时间排序
    datasets_sorted = sorted(datasets, key=lambda x: x.get('upload_time', '') or '')
    
    first = datasets_sorted[0]
    last = datasets_sorted[-1]
    
    comparison = {}
    
    for metric in ['total_sales', 'total_profit', 'product_count']:
        first_val = first.get(metric, 0)
        last_val = last.get(metric, 0)
        
        if first_val > 0:
            change = ((last_val - first_val) / first_val) * 100
        else:
            change = 0 if last_val == 0 else 100
        
        comparison[metric] = {
            'first': first_val,
            'last': last_val,
            'change': change
        }
    
    return comparison


def _calculate_rank_changes(datasets: List[Dict]) -> Dict:
    """计算排名变化"""
    if len(datasets) < 2:
        return {}
    
    # 按上传时间排序
    datasets_sorted = sorted(datasets, key=lambda x: x.get('upload_time', '') or '')
    
    first_dataset = datasets_sorted[0]
    last_dataset = datasets_sorted[-1]
    
    # 计算各数据集的产品排名
    def get_ranking(products: List[Dict]) -> Dict:
        """获取产品排名字典 {product_id: rank}"""
        sorted_products = sorted(products, key=lambda x: x.get('profit', 0), reverse=True)
        return {p['product_id']: i+1 for i, p in enumerate(sorted_products[:20])}
    
    first_ranking = get_ranking(first_dataset.get('products', []))
    last_ranking = get_ranking(last_dataset.get('products', []))
    
    all_product_ids = set(first_ranking.keys()) | set(last_ranking.keys())
    
    improved = []
    declined = []
    new_entries = []
    dropped = []
    
    top_limit = 10
    
    for pid in all_product_ids:
        first_rank = first_ranking.get(pid)
        last_rank = last_ranking.get(pid)
        
        # 获取产品名称
        product_name = None
        for ds in datasets_sorted:
            for p in ds.get('products', []):
                if p['product_id'] == pid:
                    product_name = p.get('product_name', pid)
                    break
        
        product_info = {
            'product_id': pid,
            'product_name': product_name or pid,
            'first_rank': first_rank,
            'last_rank': last_rank
        }
        
        if first_rank and last_rank:
            # 排名都存在
            if last_rank < first_rank:  # 排名上升（数字变小）
                product_info['change'] = first_rank - last_rank
                if last_rank <= top_limit or first_rank <= top_limit:
                    improved.append(product_info)
            elif last_rank > first_rank:  # 排名下降
                product_info['change'] = last_rank - first_rank
                if last_rank <= top_limit or first_rank <= top_limit:
                    declined.append(product_info)
        elif last_rank and not first_rank:
            # 新进入
            if last_rank <= top_limit:
                new_entries.append(product_info)
        elif first_rank and not last_rank:
            # 退出
            if first_rank <= top_limit:
                dropped.append(product_info)
    
    # 按变化幅度排序
    improved.sort(key=lambda x: x.get('change', 0), reverse=True)
    declined.sort(key=lambda x: x.get('change', 0), reverse=True)
    
    return {
        'improved': improved[:10],
        'declined': declined[:10],
        'new_entries': new_entries[:10],
        'dropped': dropped[:10]
    }


@router.post("/seo-names")
@limiter.limit("60/minute")  # SEO分析：60次/分钟
async def generate_seo_name_insights(
    request: Request,
    response: Response,
    current_user: dict = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """
    生成产品名称 SEO 优化建议（速率限制：60次/分钟）
    
    分析上传数据中的产品名称，根据 SEO 最佳实践给出优化建议
    缓存：30分钟（TTL=1800秒）
    """
    start_time = time.time()
    
    # 获取语言设置
    body = await request.json() if request.headers.get("content-length") else {}
    language = body.get('language', 'zh')
    
    # 构建缓存键
    cache = get_cache()
    cache_key = f"insights:seo:user_{current_user.get('id')}:lang_{language}"
    
    logger.info(f"[API] 用户 {current_user.get('email')} 请求 SEO 名称分析")
    
    # 尝试获取缓存
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} SEO 名称分析 - 完成(缓存) 耗时: {elapsed:.3f}s")
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    try:
        # 获取用户数据集
        from app.database import Dataset, ProductData
        datasets = db.query(Dataset).filter(
            Dataset.user_id == current_user['id']
        ).order_by(Dataset.upload_time.desc()).all()
        
        if not datasets:
            no_data_msg = "📝 请先上传 XML 数据以获取 SEO 分析" if language == 'zh' else "📝 Please upload XML data first for SEO analysis"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 获取最新数据集的产品数据
        latest_dataset = datasets[0]
        products = db.query(ProductData).filter(
            ProductData.dataset_id == latest_dataset.id
        ).all()
        
        if not products:
            no_data_msg = "📝 数据集中暂无产品数据" if language == 'zh' else "📝 No product data in dataset"
            result = {
                "success": True,
                "insight": no_data_msg,
                "is_offline": True
            }
            response.headers["X-Cache"] = "MISS"
            return result
        
        # 转换为字典列表
        products_data = []
        for p in products:
            products_data.append({
                'product_id': p.product_id,
                'product_name': p.product_name,
                'total_sales': (p.direct_sales or 0) + (p.indirect_sales or 0) + (p.promoted_sales or 0),
                'profit': p.profit or 0
            })
        
        # 调用 SEO 分析服务
        insight = await insights_service.generate_seo_name_insights(products_data, language)
        
        elapsed = time.time() - start_time
        logger.info(f"[API] 用户 {current_user.get('email')} SEO 名称分析完成 耗时: {elapsed:.3f}s")
        
        result = {
            "success": True,
            "insight": insight,
            "is_offline": not insights_service.is_configured(),
            "metadata": {
                "total_products": len(products_data),
                "dataset_name": latest_dataset.name,
                "language": language
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, ttl=INSIGHT_CACHE_TTL)
        response.headers["X-Cache"] = "MISS"
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[API] 用户 {current_user.get('email')} SEO 名称分析失败 耗时: {elapsed:.3f}s 错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "insight": "⚠️ SEO 分析时发生错误，请稍后重试",
            "is_offline": True
        }
