"""
数据分析服务 - 核心数据分析逻辑
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import traceback

import config

logger = logging.getLogger(__name__)


class AnalyticsService:
    """数据分析服务"""
    
    def __init__(self, products: List[Dict]):
        """
        初始化分析服务
        
        Args:
            products: 产品数据列表
        """
        try:
            self.df = pd.DataFrame(products)
            self._sales_calculated = False  # 标记是否已计算total_sales
            
            if not self.df.empty:
                # 确保数值列是正确的数据类型
                numeric_cols = ['price', 'profit', 'direct_sales', 'indirect_sales',
                              'promoted_sales', 'cart_adds', 'wishlist_adds',
                              'organic_impressions', 'paid_impressions']
                for col in numeric_cols:
                    if col in self.df.columns:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
                        
                logger.debug(f"AnalyticsService 初始化成功，共 {len(self.df)} 条数据")
        except Exception as e:
            logger.error(f"AnalyticsService 初始化失败: {str(e)}")
            self.df = pd.DataFrame()
    
    def _calculate_total_sales(self):
        """统一计算总销售额（避免重复计算）"""
        if not self._sales_calculated and not self.df.empty:
            self.df['total_sales'] = (
                self.df['direct_sales'].fillna(0) + 
                self.df['indirect_sales'].fillna(0) + 
                self.df['promoted_sales'].fillna(0)
            )
            self._sales_calculated = True
    
    def _ensure_numeric(self, col: str, default=0):
        """确保列是数值类型"""
        if col not in self.df.columns:
            return default
        return pd.to_numeric(self.df[col], errors='coerce').fillna(default)
    
    # ==================== 核心指标 ====================
    
    def get_summary_metrics(self) -> Dict:
        """获取汇总指标"""
        if self.df.empty:
            return {
                'direct_sales': 0,
                'indirect_sales': 0,
                'promoted_sales': 0,
                'total_sales': 0,
                'total_profit': 0,
                'total_products': 0,
                'visible_products': 0,
                'hidden_products': 0,
            }
        
        try:
            # 计算各项销售总和
            direct_sales = int(self.df['direct_sales'].sum())
            indirect_sales = int(self.df['indirect_sales'].sum())
            promoted_sales = int(self.df['promoted_sales'].sum())
            total_sales = direct_sales + indirect_sales  # 总销售数量 = 直接 + 间接
            
            return {
                'direct_sales': direct_sales,
                'indirect_sales': indirect_sales,
                'promoted_sales': promoted_sales,
                'total_sales': total_sales,
                'total_profit': round(self.df['profit'].sum(), 2),
                'total_products': len(self.df),
                'visible_products': len(self.df[self.df['visible'] == 'Y']),
                'hidden_products': len(self.df[self.df['visible'] == 'N']),
            }
        except Exception as e:
            logger.error(f"get_summary_metrics 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {
                'direct_sales': 0,
                'indirect_sales': 0,
                'promoted_sales': 0,
                'total_sales': 0,
                'total_profit': 0,
                'total_products': 0,
                'visible_products': 0,
                'hidden_products': 0,
            }
    
    # ==================== Top/Bottom产品 ====================
    
    def get_top_products(self, limit: int = 10, metric: str = 'profit') -> List[Dict]:
        """
        获取Top N产品
        
        Args:
            limit: 返回数量
            metric: 排序指标 (profit/sales/price)
        """
        if self.df.empty:
            return []
        
        try:
            # 使用统一的计算方法
            self._calculate_total_sales()
            
            # 计算利润率
            self.df['profit_margin'] = self.df.apply(
                lambda x: (x['profit'] / x['price'] * 100) if x['price'] > 0 else 0, axis=1
            )
            
            sort_col = metric if metric in self.df.columns else 'profit'
            top_df = self.df.nlargest(limit, sort_col)
            
            return self._format_product_list(top_df)
        except Exception as e:
            logger.error(f"get_top_products 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    def get_bottom_products(self, limit: int = 10, metric: str = 'profit') -> List[Dict]:
        """获取Bottom N产品（表现最差）"""
        if self.df.empty:
            return []
        
        try:
            self._calculate_total_sales()
            
            sort_col = metric if metric in self.df.columns else 'profit'
            bottom_df = self.df.nsmallest(limit, sort_col)
            
            return self._format_product_list(bottom_df)
        except Exception as e:
            logger.error(f"get_bottom_products 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    def _format_product_list(self, df: pd.DataFrame) -> List[Dict]:
        """格式化产品列表为字典"""
        return df.to_dict('records')
    
    # ==================== 可见性分析 ====================
    
    def get_visibility_analysis(self) -> Dict:
        """获取可见/不可见产品对比"""
        if self.df.empty:
            return {}
        
        try:
            self._calculate_total_sales()
            
            visible_df = self.df[self.df['visible'] == 'Y']
            hidden_df = self.df[self.df['visible'] == 'N']
            
            return {
                'visible': {
                    'count': len(visible_df),
                    'total_sales': round(visible_df['total_sales'].sum(), 2),
                    'total_profit': round(visible_df['profit'].sum(), 2),
                    'avg_price': round(visible_df['price'].mean(), 2) if len(visible_df) > 0 else 0,
                },
                'hidden': {
                    'count': len(hidden_df),
                    'total_sales': round(hidden_df['total_sales'].sum(), 2),
                    'total_profit': round(hidden_df['profit'].sum(), 2),
                    'avg_price': round(hidden_df['price'].mean(), 2) if len(hidden_df) > 0 else 0,
                }
            }
        except Exception as e:
            logger.error(f"get_visibility_analysis 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {}
    
    # ==================== 流量分析 ====================
    
    def get_traffic_analysis(self) -> Dict:
        """获取自然流量 vs 付费流量分析"""
        if self.df.empty:
            return {}
        
        try:
            organic_sum = self.df['organic_impressions'].sum()
            paid_sum = self.df['paid_impressions'].sum()
            total_impressions = organic_sum + paid_sum
            
            return {
                'organic': {
                    'total_impressions': int(organic_sum),
                    'avg_impressions': round(self.df['organic_impressions'].mean(), 2),
                    'max_impressions': int(self.df['organic_impressions'].max()),
                },
                'paid': {
                    'total_impressions': int(paid_sum),
                    'avg_impressions': round(self.df['paid_impressions'].mean(), 2),
                    'max_impressions': int(self.df['paid_impressions'].max()),
                },
                'ratio': {
                    'organic_pct': round((organic_sum / total_impressions * 100) if total_impressions > 0 else 0, 2),
                    'paid_pct': round((paid_sum / total_impressions * 100) if total_impressions > 0 else 0, 2),
                }
            }
        except Exception as e:
            logger.error(f"get_traffic_analysis 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {}
    
    # ==================== 销售诊断 ====================
    
    def get_price_range_analysis(self) -> List[Dict]:
        """价格区间分析"""
        if self.df.empty:
            return []
        
        try:
            self._calculate_total_sales()
            
            # 定义价格区间
            bins = [0, 100, 500, 1000, 5000, float('inf')]
            labels = ['0-100', '101-500', '501-1000', '1001-5000', '5000+']
            
            self.df['price_range'] = pd.cut(self.df['price'], bins=bins, labels=labels)
            
            result = self.df.groupby('price_range', observed=True).agg({
                'product_id': 'count',
                'total_sales': 'sum',
                'profit': 'sum',
            }).reset_index()
            
            result.columns = ['range', 'count', 'total_sales', 'total_profit']
            result['avg_sales'] = result['total_sales'] / result['count']
            result['avg_profit'] = result['total_profit'] / result['count']
            
            return result.to_dict('records')
        except Exception as e:
            logger.error(f"get_price_range_analysis 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    def get_conversion_funnel(self) -> Dict:
        """转化漏斗分析"""
        if self.df.empty:
            return {}
        
        try:
            self._calculate_total_sales()
            
            total_impressions = (
                self.df['organic_impressions'].sum() + 
                self.df['paid_impressions'].sum()
            )
            total_cart = self.df['cart_adds'].sum()
            total_wishlist = self.df['wishlist_adds'].sum()
            total_sales = self.df['total_sales'].sum()
            
            # 计算转化率
            impression_to_cart = (total_cart / total_impressions * 100) if total_impressions > 0 else 0
            cart_to_wishlist = (total_wishlist / total_cart * 100) if total_cart > 0 else 0
            wishlist_to_sales = (total_sales / total_wishlist * 100) if total_wishlist > 0 else 0
            
            return {
                'impressions': int(total_impressions),
                'cart_adds': int(total_cart),
                'wishlist_adds': int(total_wishlist),
                'sales': round(total_sales, 2),
                'impression_to_cart_rate': round(impression_to_cart, 4),
                'cart_to_wishlist_rate': round(cart_to_wishlist, 4),
                'wishlist_to_sales_rate': round(wishlist_to_sales, 4),
                'overall_conversion_rate': round((total_sales / total_impressions * 100) if total_impressions > 0 else 0, 4),
            }
        except Exception as e:
            logger.error(f"get_conversion_funnel 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {}
    
    def get_high_profit_products(self, margin_threshold: float = None) -> List[Dict]:
        """识别高利润产品"""
        if self.df.empty:
            return []
        
        try:
            if margin_threshold is None:
                margin_threshold = config.HIGH_PROFIT_MARGIN
            
            self.df['profit_margin'] = self.df.apply(
                lambda x: (x['profit'] / x['price']) if x['price'] > 0 else 0, axis=1
            )
            
            high_profit_df = self.df[self.df['profit_margin'] >= margin_threshold]
            
            return self._format_product_list(high_profit_df.sort_values('profit_margin', ascending=False))
        except Exception as e:
            logger.error(f"get_high_profit_products 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    # ==================== 用户行为诊断 ====================
    
    def get_user_behavior_analysis(self) -> Dict:
        """用户行为转化分析"""
        if self.df.empty:
            return {}
        
        try:
            self._calculate_total_sales()
            
            # 计算各项转化率
            total_cart = self.df['cart_adds'].sum()
            total_wishlist = self.df['wishlist_adds'].sum()
            total_sales = self.df['total_sales'].sum()
            
            return {
                'cart_to_sales_rate': round((total_sales / total_cart * 100) if total_cart > 0 else 0, 4),
                'cart_to_wishlist_rate': round((total_wishlist / total_cart * 100) if total_cart > 0 else 0, 4),
                'wishlist_to_sales_rate': round((total_sales / total_wishlist * 100) if total_wishlist > 0 else 0, 4),
            }
        except Exception as e:
            logger.error(f"get_user_behavior_analysis 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {}
    
    def get_low_conversion_alerts(self, threshold: float = None) -> List[Dict]:
        """高加购低转化产品预警"""
        if self.df.empty:
            return []
        
        try:
            if threshold is None:
                threshold = config.LOW_CONVERSION_THRESHOLD
            
            self._calculate_total_sales()
            
            # 计算转化率
            self.df['conversion_rate'] = self.df.apply(
                lambda x: (x['total_sales'] / x['cart_adds']) if x['cart_adds'] > 0 else 0, axis=1
            )
            
            # 筛选高加购（>中位数）但低转化（<阈值）的产品
            median_cart = self.df['cart_adds'].median()
            alerts_df = self.df[
                (self.df['cart_adds'] > median_cart) & 
                (self.df['conversion_rate'] < threshold)
            ].sort_values('conversion_rate')
            
            return self._format_product_list(alerts_df)
        except Exception as e:
            logger.error(f"get_low_conversion_alerts 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    # ==================== 异常检测 ====================
    
    def detect_sales_anomalies(self, threshold: float = None) -> List[Dict]:
        """
        销量异常波动检测（基于统计方法）
        
        Args:
            threshold: 标准差倍数阈值
            
        Returns:
            异常产品列表
        """
        if self.df.empty or len(self.df) < 3:
            return []
        
        try:
            if threshold is None:
                threshold = config.SALES_ANOMALY_THRESHOLD
            
            self._calculate_total_sales()
            
            # 计算Z-score
            mean_sales = self.df['total_sales'].mean()
            std_sales = self.df['total_sales'].std()
            
            if std_sales == 0:
                return []
            
            self.df['z_score'] = (self.df['total_sales'] - mean_sales) / std_sales
            
            # 找出异常值
            anomalies_df = self.df[
                (self.df['z_score'].abs() > threshold)
            ].copy()
            
            anomalies_df['anomaly_type'] = anomalies_df['z_score'].apply(
                lambda x: '异常高' if x > 0 else '异常低'
            )
            
            return self._format_product_list(anomalies_df)
        except Exception as e:
            logger.error(f"detect_sales_anomalies 执行失败: {str(e)}\n{traceback.format_exc()}")
            return []
    
    # ==================== ROI分析 ====================
    
    def get_roi_analysis(self) -> Dict:
        """ROI分析（基于流量和转化）"""
        if self.df.empty:
            return {}
        
        try:
            # 付费流量的效果分析
            paid_df = self.df[self.df['paid_impressions'] > 0]
            
            if len(paid_df) == 0:
                return {'message': '没有付费流量数据'}
            
            self._calculate_total_sales()
            
            # 计算各项指标
            total_paid_impressions = self.df['paid_impressions'].sum()
            total_organic_impressions = self.df['organic_impressions'].sum()
            total_sales = self.df['total_sales'].sum()
            
            # 假设推广成本为付费展示的10%（简化计算）
            estimated_paid_cost = total_paid_impressions * 0.1
            organic_revenue = self.df[self.df['paid_impressions'] == 0]['total_sales'].sum()
            paid_revenue = total_sales - organic_revenue
            
            return {
                'total_organic_revenue': round(organic_revenue, 2),
                'total_paid_revenue': round(paid_revenue, 2),
                'estimated_paid_cost': round(estimated_paid_cost, 2),
                'estimated_roi': round(((paid_revenue - estimated_paid_cost) / estimated_paid_cost * 100) 
                                       if estimated_paid_cost > 0 else 0, 2),
                'organic_vs_paid_ratio': round((total_organic_impressions / total_paid_impressions)
                                               if total_paid_impressions > 0 else 0, 2),
            }
        except Exception as e:
            logger.error(f"get_roi_analysis 执行失败: {str(e)}\n{traceback.format_exc()}")
            return {}
