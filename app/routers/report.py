"""
报告路由 - 报告生成和管理
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
import json
from datetime import datetime

import config
from app.database import get_db_context, ProductDataRepository, ReportHistoryRepository
from app.services.analytics import AnalyticsService
from app.services.email_service import email_service
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription
from app.services.download_token import generate_download_token, verify_download_token
from app.services.activity_tracker import activity_tracker
from app.core.rate_limiter import check_tiered_rate_limit
import html as html_module

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/report", tags=["报告"])


class ReportRequest(BaseModel):
    """报告生成请求"""
    include_anomalies: bool = True
    include_top_bottom: bool = True
    top_limit: int = 10
    send_email: bool = False
    email_recipients: Optional[List[str]] = None


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


@router.get("/generate")
async def generate_report_html(
    request: Request,
    current_user: dict = Depends(require_subscription)
):
    """
    生成HTML报告（分层限流：free=3/day, pro=20/day）
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("report", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    
    user_id = current_user.get('id')
    
    try:
        with get_db_context() as db:
            # 记录生成报告行为
            activity_tracker.log_activity(db, user_id, 'generate_report')
            
            repo = ProductDataRepository(db)
            products = repo.get_all(user_id=user_id)
            
            if not products:
                return HTMLResponse(
                    content="<html><body><h1>暂无数据</h1><p>请先上传数据。</p></body></html>",
                    status_code=200
                )
            
            product_dicts = [_product_to_dict(p) for p in products]
            analytics = AnalyticsService(product_dicts)
            
            # 收集所有数据
            summary = analytics.get_summary_metrics()
            top_products = analytics.get_top_products(10, metric='sales')
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
    except Exception as e:
        import traceback
        logger.error(f"生成报告失败: {str(e)}\n{traceback.format_exc()}")
        return HTMLResponse(
            content=f"<html><body><h1>生成报告失败</h1><p>错误: {str(e)}</p><pre>{traceback.format_exc()}</pre></body></html>",
            status_code=500
        )


@router.post("/generate")
async def create_report(
    request: ReportRequest, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_subscription)
):
    """
    创建报告（可配置）
    
    - **include_anomalies**: 包含异常检测
    - **include_top_bottom**: 包含Top/Bottom产品
    - **top_limit**: Top产品数量
    - **send_email**: 发送邮件
    - **email_recipients**: 邮件收件人列表
    """
    user_id = current_user.get('id')
    try:
        with get_db_context() as db:
            repo = ProductDataRepository(db)
            report_repo = ReportHistoryRepository(db)
            products = repo.get_all(user_id=user_id)
            
            if not products:
                raise HTTPException(status_code=400, detail="暂无数据")
            
            product_dicts = [_product_to_dict(p) for p in products]
            analytics = AnalyticsService(product_dicts)
            
            # 收集数据
            summary = analytics.get_summary_metrics()
            top_products = analytics.get_top_products(request.top_limit, metric='sales') if request.include_top_bottom else []
            bottom_products = analytics.get_bottom_products(request.top_limit) if request.include_top_bottom else []
            anomalies = analytics.detect_sales_anomalies() if request.include_anomalies else []
            
            # 保存报告记录
            report_record = report_repo.create({
                'report_type': 'manual',
                'content_preview': f"总销量: {(summary or {}).get('total_sales', 0)} 个",
                'status': 'pending'
            }, user_id=user_id)
            # 保存 report_id，避免 session 关闭后无法访问
            report_id = report_record.id
        
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
        with get_db_context() as db:
            report_repo = ReportHistoryRepository(db)
            report_repo.update_status(
                report_id,
                'completed',
                file_path=report_path
            )
        
        # 生成临时下载 token（有效期24小时）
        download_token = generate_download_token(report_filename, user_id)
        
        # 发送邮件
        email_sent = False
        if request.send_email:
            recipients = request.email_recipients or [e.strip() for e in config.EMAIL_TO.split(',') if e.strip()]
            logger.info(f"准备发送邮件，收件人: {recipients}")
            if recipients:
                # 构建带 token 的下载链接
                download_url = f"{config.APP_BASE_URL}/api/report/download-public?token={download_token}"
                
                success, message = email_service.send_daily_report(
                    {
                        'summary': summary,
                        'top_products': top_products,
                        'bottom_products': bottom_products,
                        'anomalies': anomalies
                    },
                    recipients,
                    download_url=download_url
                )
                email_sent = success
                logger.info(f"邮件发送结果: success={success}, message={message}")
                if success:
                    with get_db_context() as db:
                        report_repo = ReportHistoryRepository(db)
                        report_repo.update_status(
                            report_id,
                            'completed',
                            sent_to=','.join(recipients)
                        )
            else:
                logger.warning("没有收件人地址，跳过邮件发送")
        
        return {
            "success": True,
            "data": {
                "report_id": report_id,
                "file_path": report_filename,
                "email_sent": email_sent,
                "download_url": f"/api/report/download/{report_filename}"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"创建报告失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.get("/download/{filename}")
async def download_report(
    filename: str,
    current_user: dict = Depends(require_subscription)
):
    """下载报告文件（需要登录）"""
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


@router.get("/download-public")
async def download_report_public(token: str):
    """
    通过临时 token 下载报告（无需登录）
    
    Token 有效期 24 小时，用于邮件中的下载链接
    """
    # 验证 token
    token_data = verify_download_token(token)
    
    if not token_data:
        raise HTTPException(status_code=403, detail="下载链接无效或已过期")
    
    # 获取文件信息
    filename = token_data["filename"]
    safe_name = os.path.basename(filename)
    file_path = os.path.join(config.REPORT_DIR, safe_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    logger.info(f"Token 下载: user_id={token_data['user_id']}, filename={filename}")
    
    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type='text/html'
    )


@router.get("/history")
async def get_report_history(
    limit: int = 10,
    current_user: dict = Depends(require_subscription)
):
    """获取报告历史"""
    user_id = current_user.get('id')
    with get_db_context() as db:
        repo = ReportHistoryRepository(db)
        reports = repo.get_recent(limit, user_id=user_id)
        
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
    
    # 转化漏斗
    funnel = conversion_funnel
    
    # 准备图表数据（转换为JSON安全格式）
    top_product_names = json.dumps([(p.get('product_name', 'N/A') or 'N/A')[:12] for p in (top_products[:10] or [])])
    top_product_sales = json.dumps([(p.get('direct_sales', 0) or 0) + (p.get('indirect_sales', 0) or 0) + (p.get('promoted_sales', 0) or 0) for p in (top_products[:10] or [])])
    price_ranges = json.dumps([str(p.get('range', 'N/A') or 'N/A') for p in (price_range or [])])
    price_counts = json.dumps([int(p.get('count', 0) or 0) for p in (price_range or [])])
    
    # 辅助函数：HTML转义
    def escape_html(text):
        return html_module.escape(str(text)) if text else 'N/A'
    
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
                <div class="label">直接销售</div>
                <div class="value">{(summary or {{}}).get('direct_sales', 0):,} 个</div>
            </div>
            <div class="metric-card">
                <div class="label">间接销售</div>
                <div class="value">{(summary or {{}}).get('indirect_sales', 0):,} 个</div>
            </div>
            <div class="metric-card">
                <div class="label">推广销售</div>
                <div class="value">{(summary or {{}}).get('promoted_sales', 0):,} 个</div>
            </div>
            <div class="metric-card">
                <div class="label">总销售数量</div>
                <div class="value">{(summary or {{}}).get('total_sales', 0):,} 个</div>
            </div>
            <div class="metric-card">
                <div class="label">总利润 (Credits)</div>
                <div class="value green">{(summary or {{}}).get('total_profit', 0):,.0f} c</div>
            </div>
            <div class="metric-card">
                <div class="label">总利润 (USD)</div>
                <div class="value green">${((summary or {{}}).get('total_profit_usd', 0) or 0):,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="label">可见产品</div>
                <div class="value">{(summary or {{}}).get('visible_products', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">隐藏产品</div>
                <div class="value red">{(summary or {{}}).get('hidden_products', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">总产品数</div>
                <div class="value">{(summary or {{}}).get('total_products', 0)}</div>
            </div>
        </div>
        
        <!-- 图表区 -->
        <div class="section">
            <div class="section-title">数据可视化</div>
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
            <div class="section-title">转化漏斗</div>
            <div class="funnel-container">
                <div class="funnel-step">
                    <div class="num">{(funnel or {{}}).get('impressions', 0):,}</div>
                    <div class="label">展示次数</div>
                </div>
                <div class="funnel-arrow">-&gt;</div>
                <div class="funnel-step">
                    <div class="num">{(funnel or {{}}).get('cart_adds', 0):,}</div>
                    <div class="label">加购数</div>
                </div>
                <div class="funnel-arrow">-&gt;</div>
                <div class="funnel-step">
                    <div class="num">{(funnel or {{}}).get('wishlist_adds', 0):,}</div>
                    <div class="label">收藏数</div>
                </div>
                <div class="funnel-arrow">-&gt;</div>
                <div class="funnel-step">
                    <div class="num">{(funnel or {{}}).get('sales', 0):,.0f} 个</div>
                    <div class="label">销售数</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; color: #666;">
                <span>转化率: 展示-&gt;加购 {(funnel or {{}}).get('impression_to_cart_rate', 0):.2f}% | 加购-&gt;收藏 {(funnel or {{}}).get('cart_to_wishlist_rate', 0):.2f}% | 收藏-&gt;下单 {(funnel or {{}}).get('wishlist_to_sales_rate', 0):.2f}%</span>
            </div>
        </div>
        
        <!-- Top产品 -->
        <div class="section">
            <div class="section-title">Top 10 产品（按销量）</div>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>产品ID</th>
                        <th>产品名称</th>
                        <th>销量</th>
                        <th>价格</th>
                        <th>利润</th>
                        <th>可见性</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{p.get("product_id") or "N/A"}</td><td>{escape_html(p.get("product_name") or "N/A")[:40]}...</td><td>{(p.get("direct_sales") or 0) + (p.get("indirect_sales") or 0) + (p.get("promoted_sales") or 0)} 个</td><td>{(p.get("price") or 0):,.0f} c</td><td>{(p.get("profit") or 0):,.0f} c</td><td>{"可见" if p.get("visible") == "Y" else "隐藏"}</td></tr>' for i, p in enumerate(top_products[:10])])}
                </tbody>
            </table>
        </div>
        
        <!-- Bottom产品 -->
        <div class="section">
            <div class="section-title">Bottom 10 产品（按利润）</div>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>产品ID</th>
                        <th>产品名称</th>
                        <th>销量</th>
                        <th>价格</th>
                        <th>利润</th>
                        <th>可见性</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{p.get("product_id") or "N/A"}</td><td>{escape_html(p.get("product_name") or "N/A")[:40]}...</td><td>{(p.get("direct_sales") or 0) + (p.get("indirect_sales") or 0) + (p.get("promoted_sales") or 0)} 个</td><td>{(p.get("price") or 0):,.0f} c</td><td>{(p.get("profit") or 0):,.0f} c</td><td>{"可见" if p.get("visible") == "Y" else "隐藏"}</td></tr>' for i, p in enumerate(bottom_products[:10])])}
                </tbody>
            </table>
        </div>
        
        <!-- 异常预警 -->
        {f'''
        <div class="section">
            <div class="section-title">异常检测 ({len(anomalies)} 个问题)</div>
            <div class="alert-box danger">
                <div class="alert-title">销量异常产品</div>
                <p>检测到以下产品的销量存在异常波动：</p>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    {''.join([f'<li><strong>{p.get("product_id") or "N/A"}</strong> ({escape_html(p.get("product_name") or "N/A")[:30]}...): {p.get("anomaly_type") or "未知"} (Z-score: {(abs(p.get("z_score") or 0)):.2f})</li>' for p in anomalies[:10]])}
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
            // 销量Top10图表
            var salesChart = echarts.init(document.getElementById('chart-sales'));
            salesChart.setOption({{
                title: {{ text: 'Top 10 产品销量', left: 'center' }},
                tooltip: {{ trigger: 'axis' }},
                xAxis: {{ type: 'category', data: {top_product_names} }},
                yAxis: {{ type: 'value' }},
                series: [{{
                    name: '销量',
                    type: 'bar',
                    data: {top_product_sales},
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {{ offset: 0, color: '#667eea' }},
                            {{ offset: 1, color: '#764ba2' }}
                        ])
                    }}
                }}]
            }});
            
            // 可见性图表
            var visibilityChart = echarts.init(document.getElementById('chart-visibility'));
            visibilityChart.setOption({{
                title: {{ text: '可见性分析', left: 'center' }},
                tooltip: {{ trigger: 'item' }},
                series: [{{
                    name: '产品数量',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: [
                        {{ value: {(visible_data or {{}}).get('count', 0)}, name: '可见产品' }},
                        {{ value: {(hidden_data or {{}}).get('count', 0)}, name: '隐藏产品' }}
                    ],
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}]
            }});
            
            // 流量分析图表
            var trafficChart = echarts.init(document.getElementById('chart-traffic'));
            trafficChart.setOption({{
                title: {{ text: '流量分析', left: 'center' }},
                tooltip: {{ trigger: 'axis' }},
                legend: {{ data: ['自然流量', '付费流量'], top: 30 }},
                xAxis: {{ type: 'value' }},
                yAxis: {{ type: 'category', data: ['展示次数', '加购数', '收藏数'] }},
                series: [
                    {{
                        name: '自然流量',
                        type: 'bar',
                        stack: '总量',
                        data: [{(organic_data or {{}}).get('impressions', 0)}, {(organic_data or {{}}).get('cart_adds', 0)}, {(organic_data or {{}}).get('wishlist_adds', 0)}]
                    }},
                    {{
                        name: '付费流量',
                        type: 'bar',
                        stack: '总量',
                        data: [{(paid_data or {{}}).get('impressions', 0)}, {(paid_data or {{}}).get('cart_adds', 0)}, {(paid_data or {{}}).get('wishlist_adds', 0)}]
                    }}
                ]
            }});
            
            // 价格区间图表
            var priceChart = echarts.init(document.getElementById('chart-price-range'));
            priceChart.setOption({{
                title: {{ text: '价格区间分布', left: 'center' }},
                tooltip: {{ trigger: 'axis' }},
                xAxis: {{ type: 'category', data: {price_ranges} }},
                yAxis: {{ type: 'value' }},
                series: [{{
                    name: '产品数量',
                    type: 'bar',
                    data: {price_counts},
                    itemStyle: {{
                        color: function(params) {{
                            var colorList = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140'];
                            return colorList[params.dataIndex % colorList.length];
                        }}
                    }}
                }}]
            }});
            
            // 响应式调整
            window.addEventListener('resize', function() {{
                salesChart.resize();
                visibilityChart.resize();
                trafficChart.resize();
                priceChart.resize();
            }});
        }});
    </script>
</body>
</html>
"""
    return html
