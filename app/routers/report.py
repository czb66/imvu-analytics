"""
报告路由 - 报告生成和管理
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from datetime import datetime

import config
from app.database import get_db, ProductDataRepository, ReportHistoryRepository
from app.services.analytics import AnalyticsService
from app.services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/report", tags=["报告"])


class ReportRequest(BaseModel):
    """报告生成请求"""
    include_anomalies: bool = True
    include_top_bottom: bool = True
    top_limit: int = 10
    send_email: bool = False
    email_recipients: Optional[List[str]] = None


@router.get("/generate")
async def generate_report_html():
    """生成HTML报告"""
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        products = repo.get_all()
        
        if not products:
            return HTMLResponse(
                content="<html><body><h1>暂无数据</h1><p>请先上传数据。</p></body></html>",
                status_code=200
            )
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        # 收集所有数据
        summary = analytics.get_summary_metrics()
        top_products = analytics.get_top_products(10)
        bottom_products = analytics.get_bottom_products(10)
        visibility = analytics.get_visibility_analysis()
        traffic = analytics.get_traffic_analysis()
        conversion_funnel = analytics.get_conversion_funnel()
        anomalies = analytics.detect_sales_anomalies()
        price_range = analytics.get_price_range_analysis()
        
        # 生成HTML
        html = _generate_report_html(
            summary=summary,
            top_products=top_products,
            bottom_products=bottom_products,
            visibility=visibility,
            traffic=traffic,
            conversion_funnel=conversion_funnel,
            anomalies=anomalies,
            price_range=price_range
        )
        
        return HTMLResponse(content=html, status_code=200)


@router.post("/generate")
async def create_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    创建报告（可配置）
    
    - **include_anomalies**: 包含异常检测
    - **include_top_bottom**: 包含Top/Bottom产品
    - **top_limit**: Top产品数量
    - **send_email**: 发送邮件
    - **email_recipients**: 邮件收件人列表
    """
    with get_db_context() as db:
        repo = ProductDataRepository(db)
        report_repo = ReportHistoryRepository(db)
        products = repo.get_all()
        
        if not products:
            raise HTTPException(status_code=400, detail="暂无数据")
        
        product_dicts = [_product_to_dict(p) for p in products]
        analytics = AnalyticsService(product_dicts)
        
        # 收集数据
        summary = analytics.get_summary_metrics()
        top_products = analytics.get_top_products(request.top_limit) if request.include_top_bottom else []
        bottom_products = analytics.get_bottom_products(request.top_limit) if request.include_top_bottom else []
        anomalies = analytics.detect_sales_anomalies() if request.include_anomalies else []
        
        # 保存报告记录
        report_record = report_repo.create({
            'report_type': 'manual',
            'content_preview': f"总销售额: {summary.get('total_sales', 0)}",
            'status': 'pending'
        })
        
        # 生成报告文件
        os.makedirs(config.REPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.html"
        report_path = os.path.join(config.REPORT_DIR, report_filename)
        
        # 生成HTML
        html = _generate_report_html(
            summary=summary,
            top_products=top_products,
            bottom_products=bottom_products,
            visibility=analytics.get_visibility_analysis(),
            traffic=analytics.get_traffic_analysis(),
            conversion_funnel=analytics.get_conversion_funnel(),
            anomalies=anomalies,
            price_range=analytics.get_price_range_analysis()
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # 更新记录
        report_repo.update_status(
            report_record.id,
            'completed',
            file_path=report_path
        )
        
        # 发送邮件
        email_sent = False
        if request.send_email:
            recipients = request.email_recipients or [e.strip() for e in config.EMAIL_TO.split(',') if e.strip()]
            if recipients:
                success, message = email_service.send_daily_report(
                    {
                        'summary': summary,
                        'top_products': top_products,
                        'bottom_products': bottom_products,
                        'anomalies': anomalies
                    },
                    recipients
                )
                email_sent = success
                if success:
                    report_repo.update_status(
                        report_record.id,
                        'completed',
                        sent_to=','.join(recipients)
                    )
        
        return {
            "success": True,
            "data": {
                "report_id": report_record.id,
                "file_path": report_filename,
                "email_sent": email_sent,
                "download_url": f"/api/report/download/{report_filename}"
            }
        }


@router.get("/download/{filename}")
async def download_report(filename: str):
    """下载报告文件"""
    # 安全检查：只允许下载reports目录下的文件
    safe_name = os.path.basename(filename)
    file_path = os.path.join(config.REPORT_DIR, safe_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type='text/html'
    )


@router.get("/history")
async def get_report_history(limit: int = 10):
    """获取报告历史"""
    with get_db_context() as db:
        repo = ReportHistoryRepository(db)
        reports = repo.get_recent(limit)
        
        return {
            "success": True,
            "data": [
                {
                    "id": r.id,
                    "type": r.report_type,
                    "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                    "status": r.status,
                    "file_path": r.file_path,
                    "sent_to": r.sent_to
                }
                for r in reports
            ]
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


def _generate_report_html(
    summary: dict,
    top_products: list,
    bottom_products: list,
    visibility: dict,
    traffic: dict,
    conversion_funnel: dict,
    anomalies: list,
    price_range: list
) -> str:
    """生成完整的HTML报告"""
    
    # 可见性数据
    visible_data = visibility.get('visible', {})
    hidden_data = visibility.get('hidden', {})
    
    # 流量数据
    organic_data = traffic.get('organic', {})
    paid_data = traffic.get('paid', {})
    ratio_data = traffic.get('ratio', {})
    
    # 转化漏斗
    funnel = conversion_funnel
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.APP_NAME} - 营销分析报告</title>
    <script src="/static/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #f5f7fa; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        /* 头部 */
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 14px; }}
        
        /* 指标卡片 */
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .metric-card .label {{ color: #666; font-size: 13px; margin-bottom: 8px; }}
        .metric-card .value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .metric-card .value.green {{ color: #52c41a; }}
        .metric-card .value.red {{ color: #ff4d4f; }}
        
        /* 区块 */
        .section {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        
        /* 图表容器 */
        .chart-container {{ width: 100%; height: 400px; }}
        .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        
        /* 表格 */
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #555; }}
        tr:hover {{ background: #fafafa; }}
        
        /* 预警 */
        .alert-box {{ background: #fffbe6; border: 1px solid #ffe58f; border-radius: 8px; padding: 15px; margin: 10px 0; }}
        .alert-box.danger {{ background: #fff1f0; border-color: #ffa39e; }}
        .alert-title {{ font-weight: bold; margin-bottom: 8px; color: #d48806; }}
        .alert-box.danger .alert-title {{ color: #cf1322; }}
        
        /* 页脚 */
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding: 20px; }}
        
        /* 漏斗 */
        .funnel-container {{ display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .funnel-step {{ text-align: center; padding: 15px 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; min-width: 150px; }}
        .funnel-step .num {{ font-size: 24px; font-weight: bold; }}
        .funnel-step .label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
        .funnel-arrow {{ font-size: 24px; color: #999; }}
        
        /* 价格区间 */
        .price-range-item {{ display: flex; align-items: center; margin-bottom: 10px; }}
        .price-range-bar {{ height: 30px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; min-width: 50px; text-align: center; color: white; line-height: 30px; font-size: 12px; }}
        
        @media (max-width: 768px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{config.APP_NAME}</h1>
            <div class="subtitle">营销数据分析报告 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <!-- 核心指标 -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="label">总销售额</div>
                <div class="value">¥{summary.get('total_sales', 0):,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="label">总利润</div>
                <div class="value green">¥{summary.get('total_profit', 0):,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="label">总订单（估算）</div>
                <div class="value">{summary.get('total_orders', 0):,}</div>
            </div>
            <div class="metric-card">
                <div class="label">平均转化率</div>
                <div class="value">{summary.get('avg_conversion_rate', 0):.4f}%</div>
            </div>
            <div class="metric-card">
                <div class="label">可见产品</div>
                <div class="value">{summary.get('visible_products', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">隐藏产品</div>
                <div class="value red">{summary.get('hidden_products', 0)}</div>
            </div>
        </div>
        
        <!-- 图表区 -->
        <div class="section">
            <div class="section-title">📊 数据可视化</div>
            <div class="chart-row">
                <div id="chart-sales" class="chart-container"></div>
                <div id="chart-visibility" class="chart-container"></div>
            </div>
            <div class="chart-row" style="margin-top: 20px;">
                <div id="chart-traffic" class="chart-container"></div>
                <div id="chart-price-range" class="chart-container"></div>
            </div>
        </div>
        
        <!-- 转化漏斗 -->
        <div class="section">
            <div class="section-title">🔍 转化漏斗</div>
            <div class="funnel-container">
                <div class="funnel-step">
                    <div class="num">{funnel.get('impressions', 0):,}</div>
                    <div class="label">展示次数</div>
                </div>
                <div class="funnel-arrow">→</div>
                <div class="funnel-step">
                    <div class="num">{funnel.get('cart_adds', 0):,}</div>
                    <div class="label">加购数</div>
                </div>
                <div class="funnel-arrow">→</div>
                <div class="funnel-step">
                    <div class="num">{funnel.get('wishlist_adds', 0):,}</div>
                    <div class="label">收藏数</div>
                </div>
                <div class="funnel-arrow">→</div>
                <div class="funnel-step">
                    <div class="num">¥{funnel.get('sales', 0):,.0f}</div>
                    <div class="label">销售额</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; color: #666;">
                <span>转化率: 展示→加购 {funnel.get('impression_to_cart_rate', 0):.2f}% | 加购→收藏 {funnel.get('cart_to_wishlist_rate', 0):.2f}% | 收藏→下单 {funnel.get('wishlist_to_sales_rate', 0):.2f}%</span>
            </div>
        </div>
        
        <!-- Top产品 -->
        <div class="section">
            <div class="section-title">🏆 Top 10 产品（按利润）</div>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>产品ID</th>
                        <th>产品名称</th>
                        <th>价格</th>
                        <th>利润</th>
                        <th>利润率</th>
                        <th>可见性</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td>{i+1}</td>
                        <td>{{p['product_id']}}</td>
                        <td>{{p.get('product_name', 'N/A')[:40]}}...</td>
                        <td>¥{{p.get('price', 0):,.2f}}</td>
                        <td>¥{{p.get('profit', 0):,.2f}}</td>
                        <td>{{(p.get('profit', 0) / p.get('price', 1) * 100):.1f}}%</td>
                        <td>{{'✅' if p.get('visible') == 'Y' else '❌'}}</td>
                    </tr>''' for i, p in enumerate(top_products[:10])])}
                </tbody>
            </table>
        </div>
        
        <!-- Bottom产品 -->
        <div class="section">
            <div class="section-title">📉 Bottom 10 产品（按利润）</div>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>产品ID</th>
                        <th>产品名称</th>
                        <th>价格</th>
                        <th>利润</th>
                        <th>利润率</th>
                        <th>可见性</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td>{i+1}</td>
                        <td>{{p['product_id']}}</td>
                        <td>{{p.get('product_name', 'N/A')[:40]}}...</td>
                        <td>¥{{p.get('price', 0):,.2f}}</td>
                        <td>¥{{p.get('profit', 0):,.2f}}</td>
                        <td>{{(p.get('profit', 0) / p.get('price', 1) * 100):.1f}}%</td>
                        <td>{{'✅' if p.get('visible') == 'Y' else '❌'}}</td>
                    </tr>''' for i, p in enumerate(bottom_products[:10])])}
                </tbody>
            </table>
        </div>
        
        <!-- 异常预警 -->
        {f'''
        <div class="section">
            <div class="section-title">⚠️ 异常检测 ({len(anomalies)} 个问题)</div>
            <div class="alert-box danger">
                <div class="alert-title">销量异常产品</div>
                <p>检测到以下产品的销量存在异常波动：</p>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    {''.join([f"<li><strong>{{p['product_id']}}</strong> ({{p.get('product_name', 'N/A')[:30]}}...): {{p.get('anomaly_type', '未知')}} (Z-score: {{abs(p.get('z_score', 0)):.2f}})</li>" for p in anomalies[:10]])}
                </ul>
            </div>
        </div>
        ''' if anomalies else ''}
        
        <!-- 页脚 -->
        <div class="footer">
            <p>{config.APP_NAME} v{config.APP_VERSION}</p>
            <p>本报告由系统自动生成</p>
        </div>
    </div>
    
    <script>
        // 初始化图表
        document.addEventListener('DOMContentLoaded', function() {{
            // 销售额Top10图表
            var salesChart = echarts.init(document.getElementById('chart-sales'));
            salesChart.setOption({{
                title: {{ text: 'Top 10 产品利润', left: 'center' }},
                tooltip: {{ trigger: 'axis' }},
                xAxis: {{ type: 'category', data: {top_products[:10] and [p['product_id'][:8] for p in top_products[:10]] or []}, axisLabel: {{ rotate: 30 }} }},
                yAxis: {{ type: 'value', name: '利润' }},
                series: [{{
                    type: 'bar',
                    data: {top_products[:10] and [p.get('profit', 0) for p in top_products[:10]] or []},
                    itemStyle: {{ color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: '#667eea' }},
                        {{ offset: 1, color: '#764ba2' }}
                    ])}},
                    barWidth: '50%'
                }}]
            }});
            
            // 可见性对比
            var visibilityChart = echarts.init(document.getElementById('chart-visibility'));
            visibilityChart.setOption({{
                title: {{ text: '可见 vs 隐藏产品', left: 'center' }},
                tooltip: {{ trigger: 'item' }},
                series: [{{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: [
                        {{ value: {visible_data.get('count', 0)}, name: '可见产品' }},
                        {{ value: {hidden_data.get('count', 0)}, name: '隐藏产品' }}
                    ]
                }}]
            }});
            
            // 流量对比
            var trafficChart = echarts.init(document.getElementById('chart-traffic'));
            trafficChart.setOption({{
                title: {{ text: '自然流量 vs 付费流量', left: 'center' }},
                tooltip: {{ trigger: 'item' }},
                series: [{{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: [
                        {{ value: {organic_data.get('total_impressions', 0)}, name: '自然流量' }},
                        {{ value: {paid_data.get('total_impressions', 0)}, name: '付费流量' }}
                    ]
                }}]
            }});
            
            // 价格区间
            var priceRangeChart = echarts.init(document.getElementById('chart-price-range'));
            priceRangeChart.setOption({{
                title: {{ text: '价格区间产品分布', left: 'center' }},
                tooltip: {{ trigger: 'axis' }},
                xAxis: {{ type: 'category', data: {[p['range'] for p in price_range] or []} }},
                yAxis: {{ type: 'value', name: '产品数量' }},
                series: [{{
                    type: 'bar',
                    data: {[p['count'] for p in price_range] or []},
                    itemStyle: {{ color: '#667eea' }}
                }}]
            }});
            
            // 响应式
            window.addEventListener('resize', function() {{
                salesChart.resize();
                visibilityChart.resize();
                trafficChart.resize();
                priceRangeChart.resize();
            }});
        }});
    </script>
</body>
</html>
    """
    return html
