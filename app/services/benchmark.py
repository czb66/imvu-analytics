"""
行业基准服务 - 计算和提供行业基准数据
用于竞品分析功能，让用户了解自己在行业中的位置
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
import logging
import traceback

from app.database import get_db_context
from app.models import User, Dataset, ProductData, IndustryBenchmark

logger = logging.getLogger(__name__)

# 最小样本数（隐私保护）
MIN_SAMPLE_SIZE = 5

# 支持的指标类型
METRIC_TYPES = [
    'avg_sales',           # 平均销量
    'median_sales',        # 中位销量
    'avg_profit',          # 平均利润
    'median_profit',       # 中位利润
    'avg_profit_margin',   # 平均利润率
    'median_profit_margin', # 中位利润率
    'avg_price',           # 平均价格
    'median_price',        # 中位价格
    'total_products',      # 平均产品数量
]


class BenchmarkService:
    """行业基准计算服务"""
    
    def __init__(self):
        self.min_sample_size = MIN_SAMPLE_SIZE
    
    def _classify_product(self, product: ProductData) -> str:
        """
        根据产品特征分类
        这里使用简单的规则分类，实际可以基于产品名称关键词
        """
        name = (product.product_name or '').lower()
        
        # 基于价格分类
        if product.price is not None:
            if product.price < 100:
                return 'budget'  # 低价产品
            elif product.price > 1000:
                return 'premium'  # 高价产品
        
        # 基于销量分类（高销量通常是热门/刚需产品）
        total_sales = (product.direct_sales or 0) + (product.indirect_sales or 0)
        if total_sales > 100:
            return 'popular'  # 热门产品
        
        # 默认分类
        return 'general'
    
    def _calculate_product_metrics(self, product: ProductData) -> Dict[str, float]:
        """计算单个产品的各项指标"""
        total_sales = (product.direct_sales or 0) + (product.indirect_sales or 0)
        price = product.price or 0
        profit = product.profit or 0
        
        # 利润率
        profit_margin = (profit / price * 100) if price > 0 else 0
        
        return {
            'sales': total_sales,
            'profit': profit,
            'profit_margin': profit_margin,
            'price': price,
        }
    
    def calculate_benchmarks(self, db: Session) -> Dict[str, Any]:
        """
        计算所有类别的行业基准
        
        Returns:
            计算结果统计
        """
        try:
            # 获取所有未opt-out的用户
            active_users = db.query(User).filter(
                User.opt_out_benchmark == False,
                User.is_active == True
            ).all()
            
            if not active_users:
                logger.warning("没有找到符合条件的用户来计算行业基准")
                return {'status': 'no_users', 'categories_processed': 0}
            
            user_ids = [u.id for u in active_users]
            logger.info(f"开始计算行业基准，参与用户数: {len(user_ids)}")
            
            # 收集所有产品数据
            products = db.query(ProductData).join(
                Dataset, ProductData.dataset_id == Dataset.id
            ).filter(
                Dataset.user_id.in_(user_ids),
                Dataset.user_id != None
            ).all()
            
            if not products:
                logger.warning("没有找到产品数据来计算行业基准")
                return {'status': 'no_products', 'categories_processed': 0}
            
            # 按类别分组
            category_products: Dict[str, List[Dict]] = {}
            for product in products:
                category = self._classify_product(product)
                metrics = self._calculate_product_metrics(product)
                metrics['product_id'] = product.product_id
                metrics['user_id'] = product.dataset.user_id if product.dataset else None
                
                if category not in category_products:
                    category_products[category] = []
                category_products[category].append(metrics)
            
            logger.info(f"产品分为 {len(category_products)} 个类别")
            
            # 计算每个类别的基准
            categories_processed = 0
            for category, product_list in category_products.items():
                sample_size = len(product_list)
                
                if sample_size < self.min_sample_size:
                    logger.info(f"类别 '{category}' 样本数 {sample_size} < {self.min_sample_size}，跳过")
                    continue
                
                # 提取各项指标
                sales_values = [p['sales'] for p in product_list]
                profit_values = [p['profit'] for p in product_list]
                profit_margin_values = [p['profit_margin'] for p in product_list]
                price_values = [p['price'] for p in product_list]
                
                # 计算统计指标
                metrics_data = [
                    ('avg_sales', np.mean(sales_values)),
                    ('median_sales', np.median(sales_values)),
                    ('avg_profit', np.mean(profit_values)),
                    ('median_profit', np.median(profit_values)),
                    ('avg_profit_margin', np.mean(profit_margin_values)),
                    ('median_profit_margin', np.median(profit_margin_values)),
                    ('avg_price', np.mean(price_values)),
                    ('median_price', np.median(price_values)),
                    ('total_products', sample_size),
                ]
                
                # 更新数据库
                for metric_name, value in metrics_data:
                    existing = db.query(IndustryBenchmark).filter(
                        IndustryBenchmark.category == category,
                        IndustryBenchmark.metric == metric_name
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.value = round(value, 2)
                        existing.percentile_25 = round(float(np.percentile(
                            sales_values if 'sales' in metric_name else 
                            profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                            profit_margin_values if 'margin' in metric_name else
                            price_values, 25
                        ), 2))
                        existing.percentile_50 = round(float(np.percentile(
                            sales_values if 'sales' in metric_name else 
                            profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                            profit_margin_values if 'margin' in metric_name else
                            price_values, 50
                        ), 2))
                        existing.percentile_75 = round(float(np.percentile(
                            sales_values if 'sales' in metric_name else 
                            profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                            profit_margin_values if 'margin' in metric_name else
                            price_values, 75
                        ), 2))
                        existing.percentile_90 = round(float(np.percentile(
                            sales_values if 'sales' in metric_name else 
                            profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                            profit_margin_values if 'margin' in metric_name else
                            price_values, 90
                        ), 2))
                        existing.sample_size = sample_size
                        existing.is_sufficient = True
                        existing.updated_at = datetime.utcnow()
                    else:
                        # 创建新记录
                        new_benchmark = IndustryBenchmark(
                            category=category,
                            metric=metric_name,
                            value=round(value, 2),
                            percentile_25=round(float(np.percentile(
                                sales_values if 'sales' in metric_name else 
                                profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                                profit_margin_values if 'margin' in metric_name else
                                price_values, 25
                            )), 2),
                            percentile_50=round(float(np.percentile(
                                sales_values if 'sales' in metric_name else 
                                profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                                profit_margin_values if 'margin' in metric_name else
                                price_values, 50
                            )), 2),
                            percentile_75=round(float(np.percentile(
                                sales_values if 'sales' in metric_name else 
                                profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                                profit_margin_values if 'margin' in metric_name else
                                price_values, 75
                            )), 2),
                            percentile_90=round(float(np.percentile(
                                sales_values if 'sales' in metric_name else 
                                profit_values if 'profit' in metric_name and 'margin' not in metric_name else
                                profit_margin_values if 'margin' in metric_name else
                                price_values, 90
                            )), 2),
                            sample_size=sample_size,
                            is_sufficient=True,
                            updated_at=datetime.utcnow()
                        )
                        db.add(new_benchmark)
                
                categories_processed += 1
            
            db.commit()
            logger.info(f"行业基准计算完成，共处理 {categories_processed} 个类别")
            
            return {
                'status': 'success',
                'categories_processed': categories_processed,
                'total_products': len(products),
                'total_users': len(user_ids)
            }
            
        except Exception as e:
            logger.error(f"计算行业基准失败: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            return {'status': 'error', 'message': str(e)}
    
    def get_category_overview(self, db: Session, category: str = None) -> Dict[str, Any]:
        """
        获取类别的行业概览
        
        Args:
            category: 类别名称，None则返回所有类别
            
        Returns:
            类别基准数据
        """
        try:
            query = db.query(IndustryBenchmark)
            
            if category:
                query = query.filter(IndustryBenchmark.category == category)
            
            benchmarks = query.all()
            
            if not benchmarks:
                return {
                    'success': False,
                    'message': '暂无行业基准数据',
                    'categories': []
                }
            
            # 按类别分组
            categories_data = {}
            for b in benchmarks:
                if b.category not in categories_data:
                    categories_data[b.category] = {
                        'category': b.category,
                        'sample_size': b.sample_size,
                        'is_sufficient': b.is_sufficient,
                        'updated_at': b.updated_at.isoformat() if b.updated_at else None,
                        'metrics': {}
                    }
                
                categories_data[b.category]['metrics'][b.metric] = {
                    'value': b.value,
                    'percentile_25': b.percentile_25,
                    'percentile_50': b.percentile_50,
                    'percentile_75': b.percentile_75,
                    'percentile_90': b.percentile_90,
                }
            
            # 计算汇总信息
            total_categories = len(categories_data)
            sufficient_categories = sum(1 for c in categories_data.values() if c['is_sufficient'])
            
            return {
                'success': True,
                'total_categories': total_categories,
                'sufficient_categories': sufficient_categories,
                'categories': list(categories_data.values()),
                'sample_phrase': self._get_sample_phrase(len(benchmarks) // len(categories_data) if categories_data else 0)
            }
            
        except Exception as e:
            logger.error(f"获取类别概览失败: {str(e)}\n{traceback.format_exc()}")
            return {'success': False, 'message': str(e)}
    
    def _get_sample_phrase(self, sample_size: int) -> str:
        """生成样本数描述短语（不暴露具体数字）"""
        if sample_size < 5:
            return "数据不足"
        elif sample_size < 20:
            return "基于 N+ 用户的数据"
        elif sample_size < 50:
            return "基于数十位用户的数据"
        elif sample_size < 100:
            return "基于近百位用户的数据"
        else:
            return "基于数百位用户的数据"
    
    def get_product_ranking(self, db: Session, user_id: int, product_data: Dict) -> Dict[str, Any]:
        """
        获取产品在行业中的排名
        
        Args:
            user_id: 用户ID
            product_data: 产品数据字典，包含 price, profit, direct_sales, indirect_sales 等
            
        Returns:
            排名信息
        """
        try:
            # 分类用户产品
            category = self._classify_product_from_data(product_data)
            
            # 获取该类别基准
            benchmarks = db.query(IndustryBenchmark).filter(
                IndustryBenchmark.category == category
            ).all()
            
            if not benchmarks:
                return {
                    'success': False,
                    'message': '该类别暂无足够的行业数据',
                    'category': category
                }
            
            # 构建基准数据
            benchmark_dict = {b.metric: b for b in benchmarks}
            
            # 计算用户产品的各项指标
            total_sales = (product_data.get('direct_sales', 0) or 0) + (product_data.get('indirect_sales', 0) or 0)
            price = product_data.get('price', 0) or 0
            profit = product_data.get('profit', 0) or 0
            profit_margin = (profit / price * 100) if price > 0 else 0
            
            # 计算百分位排名
            ranking = {
                'success': True,
                'category': category,
                'product_name': product_data.get('product_name', 'Unknown'),
                'product_id': product_data.get('product_id', ''),
                'rankings': {
                    'sales': self._calculate_percentile(total_sales, benchmark_dict.get('avg_sales')),
                    'profit': self._calculate_percentile(profit, benchmark_dict.get('avg_profit')),
                    'profit_margin': self._calculate_percentile(profit_margin, benchmark_dict.get('avg_profit_margin')),
                    'price': self._calculate_percentile(price, benchmark_dict.get('avg_price')),
                },
                'your_values': {
                    'sales': total_sales,
                    'profit': round(profit, 2),
                    'profit_margin': round(profit_margin, 2),
                    'price': round(price, 2),
                },
                'benchmarks': {
                    'sales': self._metric_to_dict(benchmark_dict.get('avg_sales')),
                    'profit': self._metric_to_dict(benchmark_dict.get('avg_profit')),
                    'profit_margin': self._metric_to_dict(benchmark_dict.get('avg_profit_margin')),
                    'price': self._metric_to_dict(benchmark_dict.get('avg_price')),
                }
            }
            
            return ranking
            
        except Exception as e:
            logger.error(f"获取产品排名失败: {str(e)}\n{traceback.format_exc()}")
            return {'success': False, 'message': str(e)}
    
    def _classify_product_from_data(self, product_data: Dict) -> str:
        """根据产品数据分类"""
        name = (product_data.get('product_name') or '').lower()
        price = product_data.get('price') or 0
        direct_sales = product_data.get('direct_sales') or 0
        indirect_sales = product_data.get('indirect_sales') or 0
        total_sales = direct_sales + indirect_sales
        
        if price < 100:
            return 'budget'
        elif price > 1000:
            return 'premium'
        elif total_sales > 100:
            return 'popular'
        return 'general'
    
    def _calculate_percentile(self, value: float, benchmark: IndustryBenchmark) -> int:
        """计算值在基准中的百分位排名"""
        if not benchmark or not benchmark.is_sufficient:
            return None
        
        p25 = benchmark.percentile_25 or 0
        p50 = benchmark.percentile_50 or 0
        p75 = benchmark.percentile_75 or 0
        
        if value <= p25:
            return 25  # 超过25%的同类产品
        elif value <= p50:
            return 50  # 超过50%的同类产品
        elif value <= p75:
            return 75  # 超过75%的同类产品
        else:
            return 90  # 超过90%的同类产品
    
    def _metric_to_dict(self, benchmark: IndustryBenchmark) -> Optional[Dict]:
        """将基准对象转为字典"""
        if not benchmark:
            return None
        return {
            'value': benchmark.value,
            'percentile_25': benchmark.percentile_25,
            'percentile_50': benchmark.percentile_50,
            'percentile_75': benchmark.percentile_75,
            'percentile_90': benchmark.percentile_90,
        }
    
    def get_competitive_insights(self, db: Session, user_id: int, products: List[Dict], language: str = 'zh') -> List[Dict]:
        """
        生成竞争洞察建议
        
        Args:
            user_id: 用户ID
            products: 用户产品列表
            language: 语言 'zh' or 'en'
            
        Returns:
            洞察建议列表
        """
        insights = []
        
        # 多语言支持
        i18n = {
            'zh': {
                'low_sales_title': '销量提升建议',
                'low_sales_desc': '您的销量低于行业中位数，建议优化产品描述和标签',
                'high_price_title': '定价策略建议',
                'high_price_desc': '您的定价高于75%的同类产品，但销量仍在75分位以上，说明您的品牌溢价能力较强',
                'high_margin_title': '利润率分析',
                'high_margin_desc': '您的利润率高于行业平均水平，继续保持',
                'low_margin_title': '成本优化建议',
                'low_margin_desc': '您的利润率低于行业平均，建议优化成本结构或调整定价',
                'general_title': '整体表现',
                'general_desc': '您的表现在行业中处于中等水平，有较大提升空间',
            },
            'en': {
                'low_sales_title': 'Sales Improvement Suggestion',
                'low_sales_desc': 'Your sales are below industry median. Consider optimizing product descriptions and tags.',
                'high_price_title': 'Pricing Strategy',
                'high_price_desc': 'Your price is higher than 75% of similar products, but sales remain above 75th percentile - strong brand premium.',
                'high_margin_title': 'Profit Margin Analysis',
                'high_margin_desc': 'Your profit margin is above industry average. Keep it up!',
                'low_margin_title': 'Cost Optimization',
                'low_margin_desc': 'Your profit margin is below industry average. Consider optimizing costs or adjusting pricing.',
                'general_title': 'Overall Performance',
                'general_desc': 'Your performance is at mid-level in the industry, with room for improvement.',
            }
        }
        
        texts = i18n.get(language, i18n['zh'])
        
        try:
            # 获取用户所有产品的分类统计
            user_sales = []
            user_prices = []
            user_margins = []
            
            for product in products:
                total_sales = (product.get('direct_sales', 0) or 0) + (product.get('indirect_sales', 0) or 0)
                price = product.get('price', 0) or 0
                profit = product.get('profit', 0) or 0
                margin = (profit / price * 100) if price > 0 else 0
                
                user_sales.append(total_sales)
                user_prices.append(price)
                user_margins.append(margin)
            
            if not user_sales:
                return [{'title': texts['general_title'], 'description': texts['general_desc'], 'type': 'info'}]
            
            avg_sales = sum(user_sales) / len(user_sales)
            avg_margin = sum(user_margins) / len(user_margins) if user_margins else 0
            
            # 获取各分类基准
            for category in ['general', 'popular', 'budget', 'premium']:
                benchmarks = db.query(IndustryBenchmark).filter(
                    IndustryBenchmark.category == category,
                    IndustryBenchmark.is_sufficient == True
                ).first()
                
                if not benchmarks:
                    continue
                
                # 销量洞察
                if avg_sales < (benchmarks.percentile_50 or 0):
                    insights.append({
                        'title': texts['low_sales_title'],
                        'description': texts['low_sales_desc'],
                        'type': 'warning',
                        'category': category
                    })
                    break
            
            # 利润率洞察
            margin_benchmark = db.query(IndustryBenchmark).filter(
                IndustryBenchmark.metric == 'avg_profit_margin',
                IndustryBenchmark.is_sufficient == True
            ).first()
            
            if margin_benchmark:
                if avg_margin > (margin_benchmark.percentile_75 or 0):
                    insights.append({
                        'title': texts['high_margin_title'],
                        'description': texts['high_margin_desc'],
                        'type': 'success'
                    })
                elif avg_margin < (margin_benchmark.percentile_25 or 0):
                    insights.append({
                        'title': texts['low_margin_title'],
                        'description': texts['low_margin_desc'],
                        'type': 'warning'
                    })
            
            # 如果没有特殊洞察，添加一般性洞察
            if not insights:
                insights.append({
                    'title': texts['general_title'],
                    'description': texts['general_desc'],
                    'type': 'info'
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"生成竞争洞察失败: {str(e)}\n{traceback.format_exc()}")
            return [{'title': 'Error', 'description': str(e), 'type': 'error'}]


# 全局服务实例
benchmark_service = BenchmarkService()
