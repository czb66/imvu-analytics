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
    """AI洞察服务 - API Key由服务端统一管理，不暴露给前端"""
    
    def __init__(self):
        """初始化洞察服务，使用服务端固定的API Key"""
        self.api_key = config.DEEPSEEK_API_KEY
    
    def is_configured(self) -> bool:
        """检查是否已配置API Key"""
        return bool(self.api_key and self.api_key.strip())
    
    async def generate_dashboard_insights(self, summary: Dict, top_products: List[Dict], language: str = 'zh') -> str:
        """
        生成仪表盘洞察
        
        Args:
            summary: 汇总指标数据
            top_products: Top产品列表
            language: 语言 'zh' 或 'en'
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_dashboard_insights(summary, top_products, language)
        
        prompt = self._build_dashboard_prompt(summary, top_products, language)
        return await self._call_deepseek(prompt)
    
    async def generate_diagnosis_insights(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict],
        language: str = 'zh'
    ) -> str:
        """
        生成诊断洞察
        
        Args:
            sales_diagnosis: 销售诊断数据
            funnel_data: 漏斗数据
            anomalies: 异常数据列表
            language: 语言 'zh' 或 'en'
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_diagnosis_insights(sales_diagnosis, funnel_data, anomalies, language)
        
        prompt = self._build_diagnosis_prompt(sales_diagnosis, funnel_data, anomalies, language)
        return await self._call_deepseek(prompt)
    
    async def generate_compare_insights(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict,
        language: str = 'zh'
    ) -> str:
        """
        生成对比洞察
        
        Args:
            datasets: 数据集列表
            metrics_comparison: 指标对比数据
            rank_changes: 排名变化数据
            language: 语言 'zh' 或 'en'
        
        Returns:
            洞察文本
        """
        if not self.is_configured():
            return self._generate_offline_compare_insights(datasets, metrics_comparison, rank_changes, language)
        
        prompt = self._build_compare_prompt(datasets, metrics_comparison, rank_changes, language)
        return await self._call_deepseek(prompt)
    
    async def generate_seo_name_insights(
        self,
        products: List[Dict],
        language: str = 'zh'
    ) -> str:
        """
        生成产品名称 SEO 优化建议
        
        Args:
            products: 产品列表（包含 product_id, product_name, sales 等信息）
            language: 语言 'zh' 或 'en'
        
        Returns:
            SEO 优化建议文本
        """
        if not self.is_configured():
            return self._generate_offline_seo_insights(products, language)
        
        prompt = self._build_seo_name_prompt(products, language)
        return await self._call_deepseek(prompt)
    
    def _build_dashboard_prompt(self, summary: Dict, top_products: List[Dict], language: str = 'zh') -> str:
        """构建仪表盘洞察的prompt"""
        
        # 格式化数字
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        # Top 5 产品信息
        top_5 = top_products[:5] if top_products else []
        
        if language == 'zh':
            # 中文版本
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
        else:
            # 英文版本
            if top_5:
                top_products_str = "\n".join([
                    f"- {p.get('product_name', 'Unknown')} (ID: {p.get('product_id', 'N/A')}): "
                    f"Sales={fmt(p.get('total_sales', 0))}, Profit={fmt(p.get('profit', 0))}"
                    for p in top_5
                ])
            else:
                top_products_str = "No product data available"
            
            prompt = f"""You are a professional IMVU Creator data analysis assistant. Please analyze the following marketing data dashboard and generate 3-5 concise insights in English.

## Key Metrics Summary
- Direct Sales: {fmt(summary.get('direct_sales', 0))}
- Indirect Sales: {fmt(summary.get('indirect_sales', 0))}
- Promoted Sales: {fmt(summary.get('promoted_sales', 0))}
- Total Sales: {fmt(summary.get('total_sales', 0))}
- Total Profit (Credits): {fmt(summary.get('total_profit', 0))}
- Total Profit (USD): ${summary.get('total_profit_usd', 0):.2f}
- Total Products: {fmt(summary.get('total_products', 0))}
- Visible Products: {fmt(summary.get('visible_products', 0))}
- Hidden Products: {fmt(summary.get('hidden_products', 0))}

## Top 5 Products
{top_products_str}

## Requirements
1. Analyze overall sales trends, focusing on period-over-period changes and anomalies
2. Highlight the performance of top products
3. Point out issues that need attention (e.g., too many hidden products)
4. Output in English, concise and organized, each insight under 50 characters
5. If anomalies are detected (e.g., certain metrics are unusually low or high), highlight them

Please use the following format:
💡 **Trend Overview**: ...
🌟 **Top Products**: ...
⚠️ **Key Concerns**: ...
📊 **Recommendations**: ..."""
        
        return prompt
    
    def _build_diagnosis_prompt(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict],
        language: str = 'zh'
    ) -> str:
        """构建诊断洞察的prompt"""
        
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        if language == 'zh':
            # 中文版本
            sales_summary = f"""- 总销售额: {fmt(sales_diagnosis.get('total_sales', 0))}
- 总利润: {fmt(sales_diagnosis.get('total_profit', 0))} Credits
- 平均利润率: {sales_diagnosis.get('avg_profit_margin', 0):.1f}%
- 可见产品数: {fmt(sales_diagnosis.get('visible_count', 0))}
- 隐藏产品数: {fmt(sales_diagnosis.get('hidden_count', 0))}"""
            
            funnel_summary = ""
            if funnel_data:
                funnel_summary = f"""- 曝光量: {fmt(funnel_data.get('total_impressions', 0))}
- 加购数: {fmt(funnel_data.get('cart_adds', 0))}
- 收藏数: {fmt(funnel_data.get('wishlist_adds', 0))}
- 销量: {fmt(funnel_data.get('sales', 0))}
- 曝光→加购转化率: {funnel_data.get('impression_to_cart_rate', 0):.2f}%
- 加购→收藏转化率: {funnel_data.get('cart_to_wishlist_rate', 0):.2f}%
- 收藏→购买转化率: {funnel_data.get('wishlist_to_sales_rate', 0):.2f}%"""
            
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
        else:
            # 英文版本
            sales_summary = f"""- Total Sales: {fmt(sales_diagnosis.get('total_sales', 0))}
- Total Profit: {fmt(sales_diagnosis.get('total_profit', 0))} Credits
- Avg Profit Margin: {sales_diagnosis.get('avg_profit_margin', 0):.1f}%
- Visible Products: {fmt(sales_diagnosis.get('visible_count', 0))}
- Hidden Products: {fmt(sales_diagnosis.get('hidden_count', 0))}"""
            
            funnel_summary = ""
            if funnel_data:
                funnel_summary = f"""- Impressions: {fmt(funnel_data.get('total_impressions', 0))}
- Cart Adds: {fmt(funnel_data.get('cart_adds', 0))}
- Wishlist Adds: {fmt(funnel_data.get('wishlist_adds', 0))}
- Sales: {fmt(funnel_data.get('sales', 0))}
- Impression → Cart Rate: {funnel_data.get('impression_to_cart_rate', 0):.2f}%
- Cart → Wishlist Rate: {funnel_data.get('cart_to_wishlist_rate', 0):.2f}%
- Wishlist → Order Rate: {funnel_data.get('wishlist_to_sales_rate', 0):.2f}%"""
            
            anomalies_str = ""
            if anomalies:
                anomalies_str = "\n".join([
                    f"- {a.get('product_name', 'Unknown')} (ID: {a.get('product_id', 'N/A')}): "
                    f"Sales={fmt(a.get('total_sales', 0))}, Z-score={a.get('z_score', 0):.2f}"
                    for a in anomalies[:5]
                ])
            else:
                anomalies_str = "No significant anomalies detected"
            
            prompt = f"""You are a professional IMVU Creator data diagnosis expert. Please deeply analyze the following data, identify issues, and provide diagnostic conclusions.

## Sales Diagnosis Summary
{sales_summary}

## Funnel Conversion Analysis
{funnel_summary}

## Anomaly Detection Results
{anomalies_str}

## Requirements
1. Analyze possible reasons for sales decline or growth
2. Diagnose problem areas in the traffic conversion funnel
3. Explain possible reasons for detected anomaly products
4. Output in English, clear and professional but easy to understand
5. Provide specific improvement suggestions (if applicable)

Please use the following format:
🔍 **Sales Diagnosis**:
...

🎯 **Funnel Analysis**:
...

⚡ **Anomaly Explanation**:
...

💪 **Improvement Suggestions**：
..."""
        
        return prompt
    
    def _build_compare_prompt(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict,
        language: str = 'zh'
    ) -> str:
        """构建对比洞察的prompt"""
        
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        if language == 'zh':
            # 中文版本
            datasets_info = "\n".join([
                f"- {d.get('name', 'Dataset')}: 总销量={fmt(d.get('total_sales', 0))}, "
                f"总利润={fmt(d.get('total_profit', 0))}, 产品数={fmt(d.get('product_count', 0))}"
                for d in datasets
            ])
            
            changes_str = ""
            if metrics_comparison:
                for metric, data in metrics_comparison.items():
                    change = data.get('change', 0)
                    direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                    changes_str += f"- {metric}: {change:+.1f}% {direction}\n"
            
            rank_changes_str = ""
            if rank_changes:
                improved = rank_changes.get('improved', [])
                declined = rank_changes.get('declined', [])
                new_entries = rank_changes.get('new_entries', [])
                
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
        else:
            # 英文版本
            datasets_info = "\n".join([
                f"- {d.get('name', 'Dataset')}: Total Sales={fmt(d.get('total_sales', 0))}, "
                f"Total Profit={fmt(d.get('total_profit', 0))}, Products={fmt(d.get('product_count', 0))}"
                for d in datasets
            ])
            
            changes_str = ""
            if metrics_comparison:
                for metric, data in metrics_comparison.items():
                    change = data.get('change', 0)
                    direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                    changes_str += f"- {metric}: {change:+.1f}% {direction}\n"
            
            rank_changes_str = ""
            if rank_changes:
                improved = rank_changes.get('improved', [])
                declined = rank_changes.get('declined', [])
                new_entries = rank_changes.get('new_entries', [])
                
                if improved:
                    rank_changes_str += f"📈 Rank Improved: {', '.join([p.get('product_name', '')[:20] for p in improved[:3]])}\n"
                if declined:
                    rank_changes_str += f"📉 Rank Declined: {', '.join([p.get('product_name', '')[:20] for p in declined[:3]])}\n"
                if new_entries:
                    rank_changes_str += f"🆕 New Top Entries: {', '.join([p.get('product_name', '')[:20] for p in new_entries[:3]])}\n"
            
            prompt = f"""You are a professional IMVU Creator data comparison analyst. Please analyze data changes across multiple periods and generate comparison insights.

## Dataset Overview
{datasets_info}

## Metrics Change Trend
{changes_str if changes_str else "No detailed change data available"}

## Ranking Changes
{rank_changes_str if rank_changes_str else "No ranking change data"}

## Requirements
1. Summarize comparison conclusions across multiple datasets
2. Analyze products with ranking changes and reasons
3. Identify growth or decline trends
4. Output in English, concise and impactful, highlighting key points

Please use the following format:
📊 **Overall Comparison Conclusion**:
...

🏆 **Ranking Change Analysis**:
...

📈 **Trend Summary**:
...

🎯 **Action Recommendations**：
..."""
        
        return prompt
    
    def _build_seo_name_prompt(self, products: List[Dict], language: str = 'zh') -> str:
        """构建产品名称 SEO 优化的 prompt"""
        
        def fmt(val):
            if isinstance(val, (int, float)):
                return f"{val:,}"
            return str(val)
        
        # 取前 20 个产品进行分析
        analysis_products = products[:20] if products else []
        
        if language == 'zh':
            # 中文版本
            products_info = "\n".join([
                f"- [{p.get('product_id', 'N/A')}] {p.get('product_name', 'Unknown')[:60]} (销量: {fmt(p.get('total_sales', 0))})"
                for p in analysis_products
            ]) if analysis_products else "暂无产品数据"
            
            prompt = f"""你是一位专业的 IMVU 产品 SEO 优化专家。请根据 SEO 最佳实践，分析以下产品名称，并给出优化建议。

## 产品名称列表（前20个）
{products_info}

## IMVU 产品名称 SEO 优化规则
1. **关键词优化**：
   - 产品名称应包含目标用户可能搜索的关键词
   - 避免使用过于模糊或泛泛的名称
   - 建议包含：产品类型、风格、颜色、特征等描述性词汇

2. **命名结构建议**：
   - 推荐格式：[风格/主题] + [产品类型] + [关键特征]
   - 例如："Elegant Gothic Black Lace Dress" 比 "Dress 123" 更利于搜索
   - 名称长度建议控制在 3-8 个有效词汇

3. **避免的问题**：
   - ❌ 纯数字或无意义字符（如 "Product 123"）
   - ❌ 过长的名称（超过 100 字符可能被截断）
   - ❌ 重复的关键词堆砌
   - ❌ 与产品内容不相关的误导性名称

4. **优化目标**：
   - 提高搜索可见性
   - 增加点击率
   - 提升转化率

## 要求
1. 逐个分析产品名称的 SEO 问题
2. 指出每个名称的优缺点
3. 给出具体的优化建议（包含建议的新名称）
4. 优先分析销量较低的产品名称问题
5. 用中文输出，条理清晰，建议具体可执行

请按以下格式输出：

📝 **SEO 问题诊断**：
（列出 3-5 个问题最严重的名称）

🔄 **优化建议**：
（针对每个问题名称给出优化方案）

💡 **通用优化技巧**：
（给出整体性的 SEO 优化建议）

⚠️ **特别提醒**：
（需要注意的 SEO 禁忌或风险）"""
        else:
            # 英文版本
            products_info = "\n".join([
                f"- [{p.get('product_id', 'N/A')}] {p.get('product_name', 'Unknown')[:60]} (Sales: {fmt(p.get('total_sales', 0))})"
                for p in analysis_products
            ]) if analysis_products else "No product data available"
            
            prompt = f"""You are a professional IMVU product SEO optimization expert. Please analyze the following product names based on SEO best practices and provide optimization suggestions.

## Product Names List (Top 20)
{products_info}

## IMVU Product Name SEO Optimization Rules
1. **Keyword Optimization**:
   - Product names should include keywords that target users might search for
   - Avoid using vague or generic names
   - Include: product type, style, color, features and other descriptive words

2. **Naming Structure Recommendations**:
   - Recommended format: [Style/Theme] + [Product Type] + [Key Features]
   - Example: "Elegant Gothic Black Lace Dress" is better than "Dress 123" for search
   - Name length should be controlled to 3-8 effective words

3. **Issues to Avoid**:
   - ❌ Pure numbers or meaningless characters (e.g., "Product 123")
   - ❌ Overly long names (may be truncated beyond 100 characters)
   - ❌ Repetitive keyword stuffing
   - ❌ Misleading names unrelated to product content

4. **Optimization Goals**:
   - Improve search visibility
   - Increase click-through rate
   - Boost conversion rate

## Requirements
1. Analyze each product name for SEO issues
2. Point out pros and cons of each name
3. Provide specific optimization suggestions (include suggested new names)
4. Prioritize analyzing product names with lower sales
5. Output in English, well-organized and actionable

Please use the following format:

📝 **SEO Issue Diagnosis**:
(List 3-5 names with the most serious issues)

🔄 **Optimization Suggestions**:
(Provide optimization plans for each problematic name)

💡 **General Optimization Tips**:
(Provide overall SEO optimization advice)

⚠️ **Special Reminders**:
(SEO taboos or risks to be aware of)"""
        
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
            "max_tokens": 4000
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
        
        # 限制长度（SEO分析需要更长输出，提升到8000字符）
        if len(content) > 8000:
            content = content[:8000] + "\n\n...(内容已截断)"
        
        return content.strip()
    
    # ==================== 离线模式（无API时） ====================
    
    def _generate_offline_dashboard_insights(self, summary: Dict, top_products: List[Dict], language: str = 'zh') -> str:
        """生成离线模式的仪表盘洞察（基于规则）"""
        insights = []
        
        # 趋势概览
        total_sales = summary.get('total_sales', 0)
        total_profit = summary.get('total_profit', 0)
        hidden_ratio = summary.get('hidden_products', 0) / max(summary.get('total_products', 1), 1) * 100
        
        if language == 'zh':
            # 中文版本
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
        else:
            # 英文版本
            if total_sales > 1000:
                insights.append("💡 **Trend Overview**: Sales performance is active, total sales reached a high level")
            elif total_sales > 0:
                insights.append("💡 **Trend Overview**: Current sales are low, consider optimizing product promotion strategy")
            else:
                insights.append("💡 **Trend Overview**: No sales data available, please upload XML data first")
            
            # Top产品
            if top_products:
                top_name = top_products[0].get('product_name', 'Unknown')[:20]
                insights.append(f"🌟 **Top Product**: {top_name} is the best performer, continue monitoring")
            else:
                insights.append("🌟 **Top Product**: No product data available")
            
            # 隐藏产品风险
            if hidden_ratio > 30:
                insights.append(f"⚠️ **Key Concern**: Hidden products account for {hidden_ratio:.0f}%, may affect exposure")
            elif hidden_ratio > 0:
                insights.append(f"⚠️ **Key Concern**: {summary.get('hidden_products', 0)} hidden products, consider listing evaluation")
            else:
                insights.append("✅ **Status Good**: All products are listed and displayed")
            
            # 综合建议
            if total_profit > 50000:
                insights.append("💰 **Recommendation**: Excellent profit performance, consider expanding product line")
            elif total_profit > 0:
                insights.append("💰 **Recommendation**: Profit margin needs improvement, suggest optimizing pricing strategy")
            else:
                insights.append("💰 **Recommendation**: Upload data for detailed recommendations")
        
        return "\n\n".join(insights)
    
    def _generate_offline_diagnosis_insights(
        self, 
        sales_diagnosis: Dict,
        funnel_data: Dict,
        anomalies: List[Dict],
        language: str = 'zh'
    ) -> str:
        """生成离线模式的诊断洞察"""
        insights = []
        
        # 销售诊断
        total_sales = sales_diagnosis.get('total_sales', 0)
        visible_ratio = sales_diagnosis.get('visible_count', 0) / max(
            sales_diagnosis.get('visible_count', 0) + sales_diagnosis.get('hidden_count', 0), 1
        ) * 100
        
        if language == 'zh':
            # 中文版本
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
        else:
            # 英文版本
            if total_sales > 0:
                insights.append("🔍 **Sales Diagnosis**: Data loaded, conducting deep analysis...")
            else:
                insights.append("🔍 **Sales Diagnosis**: No sales data available for diagnosis")
            
            # 漏斗分析
            if funnel_data:
                cart_rate = funnel_data.get('impression_to_cart_rate', 0)
                if cart_rate > 5:
                    insights.append(f"🎯 **Funnel Analysis**: Impression → Cart rate {cart_rate:.2f}%, good performance")
                elif cart_rate > 0:
                    insights.append(f"🎯 **Funnel Analysis**: Impression → Cart rate {cart_rate:.2f}%, suggest optimizing product display")
                else:
                    insights.append("🎯 **Funnel Analysis**: No conversion data available")
            else:
                insights.append("🎯 **Funnel Analysis**: Upload data to view funnel analysis")
            
            # 异常检测
            if anomalies:
                insights.append(f"⚡ **Anomaly Explanation**: Detected {len(anomalies)} anomaly products, suggest close monitoring")
            else:
                insights.append("⚡ **Anomaly Explanation**: No significant anomalies detected")
            
            # 改进建议
            if visible_ratio < 70:
                insights.append("💪 **Improvement Suggestions**: Increasing visible products can improve overall exposure")
            else:
                insights.append("💪 **Improvement Suggestions**: Product visibility is good, keep it up")
        
        return "\n\n".join(insights)
    
    def _generate_offline_compare_insights(
        self,
        datasets: List[Dict],
        metrics_comparison: Dict,
        rank_changes: Dict,
        language: str = 'zh'
    ) -> str:
        """生成离线模式的对比洞察"""
        insights = []
        
        if language == 'zh':
            # 中文版本
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
        else:
            # 英文版本
            if len(datasets) < 2:
                insights.append("📊 **Overall Comparison**: Please select at least two datasets to compare")
            else:
                insights.append(f"📊 **Overall Comparison**: Selected {len(datasets)} datasets for comparison")
            
            # 排名变化
            improved = rank_changes.get('improved', []) if rank_changes else []
            declined = rank_changes.get('declined', []) if rank_changes else []
            
            if improved:
                count = len(improved)
                insights.append(f"🏆 **Ranking Changes**: {count} products moved up, positive performance")
            else:
                insights.append("🏆 **Ranking Changes**: No products with improved ranking")
            
            if declined:
                count = len(declined)
                insights.append(f"📉 **Trend Changes**: {count} products moved down, needs attention")
            
            # 行动建议
            if improved and declined:
                insights.append("🎯 **Action Recommendations**: Focus on declining products while maintaining advantages of rising products")
            elif improved:
                insights.append("🎯 **Action Recommendations**: Continue current strategy, expand advantages")
            else:
                insights.append("🎯 **Action Recommendations**: Upload more data for detailed comparison analysis")
        
        return "\n\n".join(insights)
    
    def _generate_offline_seo_insights(self, products: List[Dict], language: str = 'zh') -> str:
        """生成离线模式的 SEO 名称分析"""
        insights = []
        
        if not products:
            if language == 'zh':
                return "📝 **SEO 分析**：暂无产品数据，请先上传 XML 数据"
            else:
                return "📝 **SEO Analysis**: No product data available, please upload XML data first"
        
        # 分析产品名称
        problem_names = []
        for p in products[:20]:
            name = p.get('product_name', '')
            pid = p.get('product_id', '')
            sales = p.get('total_sales', 0)
            
            # 检测常见问题
            issues = []
            if not name or name.strip() == '':
                issues.append("空名称")
            elif name.isdigit():
                issues.append("纯数字名称")
            elif len(name) < 3:
                issues.append("名称过短")
            elif len(name) > 100:
                issues.append("名称过长")
            elif name.lower().startswith('product') or name.lower().startswith('item'):
                issues.append("默认名称前缀")
            
            if issues:
                problem_names.append({
                    'id': pid,
                    'name': name,
                    'issues': issues,
                    'sales': sales
                })
        
        if language == 'zh':
            # 中文版本
            insights.append(f"📝 **SEO 问题诊断**：分析了 {len(products[:20])} 个产品名称")
            
            if problem_names:
                insights.append(f"🔍 **发现问题**：{len(problem_names)} 个产品名称需要优化")
                for p in problem_names[:5]:
                    insights.append(f"  - [{p['id']}] {p['name'][:30]}: {', '.join(p['issues'])}")
            else:
                insights.append("✅ **状态良好**：未发现明显的 SEO 问题")
            
            insights.append("💡 **优化建议**：")
            insights.append("  1. 使用描述性关键词（风格、类型、颜色）")
            insights.append("  2. 避免纯数字或默认名称")
            insights.append("  3. 控制名称长度在 3-8 个有效词")
            insights.append("  4. 确保名称与产品内容相关")
            
            insights.append("⚠️ **特别提醒**：配置 DeepSeek API 可获得更详细的 SEO 分析")
        else:
            # 英文版本
            insights.append(f"📝 **SEO Issue Diagnosis**: Analyzed {len(products[:20])} product names")
            
            if problem_names:
                insights.append(f"🔍 **Issues Found**: {len(problem_names)} product names need optimization")
                for p in problem_names[:5]:
                    insights.append(f"  - [{p['id']}] {p['name'][:30]}: {', '.join(p['issues'])}")
            else:
                insights.append("✅ **Status Good**: No obvious SEO issues found")
            
            insights.append("💡 **Optimization Suggestions**:")
            insights.append("  1. Use descriptive keywords (style, type, color)")
            insights.append("  2. Avoid pure numbers or default names")
            insights.append("  3. Control name length to 3-8 effective words")
            insights.append("  4. Ensure names are relevant to product content")
            
            insights.append("⚠️ **Note**: Configure DeepSeek API for more detailed SEO analysis")
        
        return "\n\n".join(insights)


# 全局服务实例
insights_service = InsightsService()
