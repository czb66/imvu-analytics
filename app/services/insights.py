"""
AI洞察服务 - 使用DeepSeek API生成智能分析
"""

import httpx
import logging
from typing import Dict, List, Optional
import json
import re

import config

logger = logging.getLogger(__name__)

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 60


class InsightsService:
    """AI洞察服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化洞察服务
        
        Args:
            api_key: DeepSeek API密钥
        """
        self.api_key = api_key or config.DEEPSEEK_API_KEY if hasattr(config, 'DEEPSEEK_API_KEY') else None
    
    def is_configured(self) -> bool:
        """检查是否已配置API Key"""
        return bool(self.api_key and self.api_key.strip())
    
    async def generate_dashboard_insights(self, summary: Dict, top_products: List[Dict]) -> str:
        """
        生成仪表盘洞察
        
        Args:
            summary: 汇总指标数据
            top_products: Top产品列表
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_dashboard_insights(summary, top_products)
        
        prompt = self._build_dashboard_prompt(summary, top_products)
        return await self._call_deepseek(prompt)
    
    async def generate_diagnosis_insights(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict]
    ) -> str:
        """
        生成诊断洞察
        
        Args:
            sales_diagnosis: 销售诊断数据
            funnel_data: 漏斗数据
            anomalies: 异常数据列表
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_diagnosis_insights(sales_diagnosis, funnel_data, anomalies)
        
        prompt = self._build_diagnosis_prompt(sales_diagnosis, funnel_data, anomalies)
        return await self._call_deepseek(prompt)
    
    async def generate_compare_insights(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict
    ) -> str:
        """
        生成对比洞察
        
        Args:
            datasets: 数据集列表
            metrics_comparison: 指标对比数据
            rank_changes: 排名变化数据
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_compare_insights(datasets, metrics_comparison, rank_changes)
        
        prompt = self._build_compare_prompt(datasets, metrics_comparison, rank_changes)
        return await self._call_deepseek(prompt)
    
    def _build_dashboard_prompt(self, summary: Dict, top_products: List[Dict]) -> str:
        """构建仪表盘洞察的prompt"""
        
        # 格式化数字
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        # Top 5 产品信息
        top_5 = top_products[:5] if top_products else []
        top_products_str = ""
        if top_5:
            top_products_str = "\n".join([
                f"- {p.get('product_name', 'Unknown')} (ID: {p.get('product_id', 'N/A')}): "
                f"销量={fmt(p.get('total_sales', 0))}, 利润={fmt(p.get('profit', 0))}"
                for p in top_5
            ])
        else:
            top_products_str = "暂无产品数据"
        
        prompt = f"""你是一位专业的IMVU Creator数据分析助手。请分析以下营销数据仪表盘，并生成3-5条简洁的中文洞察。

## 核心指标汇总
- 直接销量 (Direct Sales): {fmt(summary.get('direct_sales', 0))}
- 间接销量 (Indirect Sales): {fmt(summary.get('indirect_sales', 0))}
- 推广销量 (Promoted Sales): {fmt(summary.get('promoted_sales', 0))}
- 总销量 (Total Sales): {fmt(summary.get('total_sales', 0))}
- 总利润 (Credits): {fmt(summary.get('total_profit', 0))}
- 总利润 (USD): ${summary.get('total_profit_usd', 0):.2f}
- 总产品数: {fmt(summary.get('total_products', 0))}
- 可见产品: {fmt(summary.get('visible_products', 0))}
- 隐藏产品: {fmt(summary.get('hidden_products', 0))}

## Top 5 产品
{top_products_str}

## 要求
1. 分析总体销售趋势，关注环比变化和异常波动
2. 点评Top产品的表现亮点
3. 指出需要关注的问题（如隐藏产品过多等）
4. 用中文输出，简洁有条理，每条洞察控制在50字以内
5. 如果发现异常（如某个指标明显偏低或偏高），重点标注

请按以下格式输出：
💡 **趋势概览**：...
🌟 **明星产品**：...
⚠️ **关注重点**：...
📊 **综合建议**：..."""
        
        return prompt
    
    def _build_diagnosis_prompt(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict]
    ) -> str:
        """构建诊断洞察的prompt"""
        
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        # 销售诊断摘要
        sales_summary = f"""- 总销售额: {fmt(sales_diagnosis.get('total_sales', 0))}
- 总利润: {fmt(sales_diagnosis.get('total_profit', 0))} Credits
- 平均利润率: {sales_diagnosis.get('avg_profit_margin', 0):.1f}%
- 可见产品数: {fmt(sales_diagnosis.get('visible_count', 0))}
- 隐藏产品数: {fmt(sales_diagnosis.get('hidden_count', 0))}"""
        
        # 漏斗分析
        funnel_summary = ""
        if funnel_data:
            funnel_summary = f"""- 曝光量 (Impressions): {fmt(funnel_data.get('total_impressions', 0))}
- 加购数 (Cart Adds): {fmt(funnel_data.get('cart_adds', 0))}
- 收藏数 (Wishlist Adds): {fmt(funnel_data.get('wishlist_adds', 0))}
- 销量 (Sales): {fmt(funnel_data.get('sales', 0))}
- 曝光→加购转化率: {funnel_data.get('impression_to_cart_rate', 0):.2f}%
- 加购→收藏转化率: {funnel_data.get('cart_to_wishlist_rate', 0):.2f}%
- 收藏→购买转化率: {funnel_data.get('wishlist_to_sales_rate', 0):.2f}%"""
        
        # 异常产品
        anomalies_str = ""
        if anomalies:
            anomalies_str = "\n".join([
                f"- {a.get('product_name', 'Unknown')} (ID: {a.get('product_id', 'N/A')}): "
                f"销量={fmt(a.get('total_sales', 0))}, Z-score={a.get('z_score', 0):.2f}"
                for a in anomalies[:5]
            ])
        else:
            anomalies_str = "未检测到明显异常"
        
        prompt = f"""你是一位专业的IMVU Creator数据诊断专家。请深度分析以下数据，识别问题并给出诊断结论。

## 销售诊断摘要
{sales_summary}

## 漏斗转化分析
{funnel_summary}

## 异常检测结果
{anomalies_str}

## 要求
1. 分析销售下滑或增长的可能原因
2. 诊断流量转化漏斗的问题环节
3. 解释检测到的异常产品的可能原因
4. 用中文输出，条理清晰，专业但易懂
5. 给出具体的改进建议（如果适用）

请按以下格式输出：
🔍 **销售诊断**：
...

🎯 **漏斗分析**：
...

⚡ **异常解读**：
...

💪 **改进建议**：
..."""
        
        return prompt
    
    def _build_compare_prompt(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict
    ) -> str:
        """构建对比洞察的prompt"""
        
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        # 数据集概览
        datasets_info = "\n".join([
            f"- {d.get('name', 'Dataset')}: 总销量={fmt(d.get('total_sales', 0))}, "
            f"总利润={fmt(d.get('total_profit', 0))}, 产品数={fmt(d.get('product_count', 0))}"
            for d in datasets
        ])
        
        # 指标对比变化
        changes_str = ""
        if metrics_comparison:
            for metric, data in metrics_comparison.items():
                change = data.get('change', 0)
                direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                changes_str += f"- {metric}: {change:+.1f}% {direction}\n"
        
        # 排名变化
        rank_changes_str = ""
        if rank_changes:
            improved = rank_changes.get('improved', [])
            declined = rank_changes.get('declined', [])
            new_entries = rank_changes.get('new_entries', [])
            dropped = rank_changes.get('dropped', [])
            
            if improved:
                rank_changes_str += f"📈 排名上升: {', '.join([p.get('product_name', '')[:20] for p in improved[:3]])}\n"
            if declined:
                rank_changes_str += f"📉 排名下降: {', '.join([p.get('product_name', '')[:20] for p in declined[:3]])}\n"
            if new_entries:
                rank_changes_str += f"🆕 新晋Top: {', '.join([p.get('product_name', '')[:20] for p in new_entries[:3]])}\n"
        
        prompt = f"""你是一位专业的IMVU Creator数据对比分析师。请分析多个时期的数据变化，生成对比洞察。

## 数据集概览
{datasets_info}

## 指标变化趋势
{changes_str if changes_str else "暂无详细变化数据"}

## 排名变化
{rank_changes_str if rank_changes_str else "暂无排名变化数据"}

## 要求
1. 总结多数据集的对比结论
2. 分析排名变化的产品及原因
3. 识别增长或下滑的趋势
4. 用中文输出，简洁有力，突出重点

请按以下格式输出：
📊 **整体对比结论**：
...

🏆 **排名变化分析**：
...

📈 **趋势总结**：
...

🎯 **行动建议**：
..."""
        
        return prompt
    
    async def _call_deepseek(self, prompt: str) -> str:
        """调用DeepSeek API"""
        if not self.api_key:
            return "⚠️ 请先在设置页面配置 DeepSeek API Key"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    # 清理输出
                    content = self._clean_response(content)
                    return content
                elif response.status_code == 401:
                    return "❌ API Key无效，请检查配置"
                elif response.status_code == 429:
                    return "⏳ 请求过于频繁，请稍后再试"
                else:
                    logger.error(f"DeepSeek API错误: {response.status_code} - {response.text}")
                    return f"⚠️ API调用失败 (错误码: {response.status_code})"
                    
        except httpx.TimeoutException:
            logger.error("DeepSeek API请求超时")
            return "⏱️ 请求超时，请检查网络连接后重试"
        except httpx.ConnectError:
            logger.error("无法连接到DeepSeek API")
            return "🔌 无法连接API服务，请检查网络"
        except Exception as e:
            logger.error(f"DeepSeek API异常: {str(e)}")
            return f"⚠️ 发生错误: {str(e)}"
    
    def _clean_response(self, content: str) -> str:
        """清理AI响应"""
        if not content:
            return "暂无洞察内容"
        
        # 移除多余的空白
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 限制长度
        if len(content) > 2000:
            content = content[:2000] + "\n\n...(内容已截断)"
        
        return content.strip()
    
    # ==================== 离线模式（无API时） ====================
    
    def _generate_offline_dashboard_insights(self, summary: Dict, top_products: List[Dict]) -> str:
        """生成离线模式的仪表盘洞察（基于规则）"""
        insights = []
        
        # 趋势概览
        total_sales = summary.get('total_sales', 0)
        total_profit = summary.get('total_profit', 0)
        hidden_ratio = summary.get('hidden_products', 0) / max(summary.get('total_products', 1), 1) * 100
        
        if total_sales > 1000:
            insights.append("💡 **趋势概览**：销售表现活跃，总销量达到较高水平")
        elif total_sales > 0:
            insights.append("💡 **趋势概览**：当前销量偏低，建议优化产品推广策略")
        else:
            insights.append("💡 **趋势概览**：暂无销售数据，请先上传XML数据")
        
        # Top产品
        if top_products:
            top_name = top_products[0].get('product_name', 'Unknown')[:20]
            insights.append(f"🌟 **明星产品**：{top_name} 表现最佳，建议持续关注")
        else:
            insights.append("🌟 **明星产品**：暂无产品数据")
        
        # 隐藏产品风险
        if hidden_ratio > 30:
            insights.append(f"⚠️ **关注重点**：隐藏产品占比 {hidden_ratio:.0f}%，可能影响曝光")
        elif hidden_ratio > 0:
            insights.append(f"⚠️ **关注重点**：有 {summary.get('hidden_products', 0)} 个隐藏产品，建议评估是否上架")
        else:
            insights.append("✅ **状态良好**：所有产品均已上架展示")
        
        # 综合建议
        if total_profit > 50000:
            insights.append("💰 **综合建议**：利润表现优秀，可考虑扩展产品线")
        elif total_profit > 0:
            insights.append("💰 **综合建议**：利润空间有待提升，建议优化定价策略")
        else:
            insights.append("💰 **综合建议**：请上传数据后获取详细建议")
        
        return "\n\n".join(insights)
    
    def _generate_offline_diagnosis_insights(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict]
    ) -> str:
        """生成离线模式的诊断洞察"""
        insights = []
        
        # 销售诊断
        total_sales = sales_diagnosis.get('total_sales', 0)
        visible_ratio = sales_diagnosis.get('visible_count', 0) / max(
            sales_diagnosis.get('visible_count', 0) + sales_diagnosis.get('hidden_count', 0), 1
        ) * 100
        
        if total_sales > 0:
            insights.append("🔍 **销售诊断**：数据已加载，正在进行深度分析...")
        else:
            insights.append("🔍 **销售诊断**：暂无销售数据可供诊断")
        
        # 漏斗分析
        if funnel_data:
            cart_rate = funnel_data.get('impression_to_cart_rate', 0)
            if cart_rate > 5:
                insights.append(f"🎯 **漏斗分析**：曝光→加购转化率 {cart_rate:.2f}%，表现良好")
            elif cart_rate > 0:
                insights.append(f"🎯 **漏斗分析**：曝光→加购转化率 {cart_rate:.2f}%，建议优化产品展示")
            else:
                insights.append("🎯 **漏斗分析**：暂无转化数据")
        else:
            insights.append("🎯 **漏斗分析**：请上传数据后查看漏斗分析")
        
        # 异常检测
        if anomalies:
            insights.append(f"⚡ **异常解读**：检测到 {len(anomalies)} 个异常产品，建议重点关注")
        else:
            insights.append("⚡ **异常解读**：未检测到明显异常")
        
        # 改进建议
        if visible_ratio < 70:
            insights.append("💪 **改进建议**：增加可见产品数量可提升整体曝光")
        else:
            insights.append("💪 **改进建议**：产品可见性良好，继续保持")
        
        return "\n\n".join(insights)
    
    def _generate_offline_compare_insights(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict
    ) -> str:
        """生成离线模式的对比洞察"""
        insights = []
        
        if len(datasets) < 2:
            insights.append("📊 **整体对比**：请至少选择两个数据集进行对比")
        else:
            insights.append(f"📊 **整体对比**：已选择 {len(datasets)} 个数据集进行对比")
        
        # 排名变化
        improved = rank_changes.get('improved', []) if rank_changes else []
        declined = rank_changes.get('declined', []) if rank_changes else []
        
        if improved:
            count = len(improved)
            insights.append(f"🏆 **排名变化**：{count} 个产品排名上升，表现积极")
        else:
            insights.append("🏆 **排名变化**：暂无排名上升的产品")
        
        if declined:
            count = len(declined)
            insights.append(f"📉 **趋势变化**：{count} 个产品排名下降，需要关注")
        
        # 行动建议
        if improved and declined:
            insights.append("🎯 **行动建议**：关注排名下降产品，同时保持排名上升产品的优势")
        elif improved:
            insights.append("🎯 **行动建议**：继续保持当前策略，扩大优势")
        else:
            insights.append("🎯 **行动建议**：上传更多数据以获取详细对比分析")
        
        return "\n\n".join(insights)


# 全局服务实例
insights_service = InsightsService()
