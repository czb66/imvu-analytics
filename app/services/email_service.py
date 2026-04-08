"""
邮件发送服务 - 发送分析报告邮件
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import logging
from datetime import datetime

import config

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""
    
    def __init__(self):
        """初始化邮件服务"""
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.use_tls = config.SMTP_USE_TLS
        self.from_email = config.EMAIL_FROM
    
    def send_report(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        attachments: List[str] = None
    ) -> tuple:
        """
        发送报告邮件
        
        Args:
            to_emails: 收件人邮箱列表
            subject: 邮件主题
            html_content: HTML格式的邮件内容
            attachments: 附件文件路径列表
            
        Returns:
            (success, message)
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP未配置，跳过邮件发送")
            return False, "SMTP未配置"
        
        if not to_emails:
            return False, "没有收件人地址"
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            filename = os.path.basename(file_path)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{filename}"'
                            )
                            msg.attach(part)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_emails, msg.as_string())
            
            logger.info(f"邮件发送成功: {subject} -> {to_emails}")
            return True, f"邮件发送成功"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP认证失败，请检查用户名和密码"
            logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP发送失败: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"邮件发送异常: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_daily_report(
        self,
        report_data: dict,
        recipients: List[str] = None
    ) -> tuple:
        """
        发送每日报告
        
        Args:
            report_data: 报告数据字典
            recipients: 收件人列表（为空则使用配置的默认收件人）
            
        Returns:
            (success, message)
        """
        if recipients is None:
            recipients = [e.strip() for e in config.EMAIL_TO.split(',') if e.strip()]
        
        if not recipients:
            return False, "没有配置收件人"
        
        subject = f"📊 {config.APP_NAME} - 每日营销报告 {datetime.now().strftime('%Y-%m-%d')}"
        html_content = self._generate_daily_report_html(report_data)
        
        return self.send_report(recipients, subject, html_content)
    
    def _generate_daily_report_html(self, data: dict) -> str:
        """生成每日报告HTML"""
        summary = data.get('summary', {})
        top_products = data.get('top_products', [])[:5]
        bottom_products = data.get('bottom_products', [])[:5]
        anomalies = data.get('anomalies', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .metric-label {{ color: #666; font-size: 12px; }}
                .section {{ margin: 20px 0; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f8f9fa; }}
                .alert {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{config.APP_NAME}</h1>
                    <p>每日营销数据报告 - {datetime.now().strftime('%Y年%m月%d日')}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">¥{summary.get('total_sales', 0):,.2f}</div>
                        <div class="metric-label">总销售额</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">¥{summary.get('total_profit', 0):,.2f}</div>
                        <div class="metric-label">总利润</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('total_orders', 0):,}</div>
                        <div class="metric-label">总订单</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('avg_conversion_rate', 0):.4f}%</div>
                        <div class="metric-label">平均转化率</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">📈 Top 5 产品（按利润）</div>
                    <table>
                        <tr>
                            <th>产品ID</th>
                            <th>产品名称</th>
                            <th>价格</th>
                            <th>利润</th>
                        </tr>
                        {self._generate_product_rows(top_products)}
                    </table>
                </div>
                
                <div class="section">
                    <div class="section-title">📉 Bottom 5 产品（按利润）</div>
                    <table>
                        <tr>
                            <th>产品ID</th>
                            <th>产品名称</th>
                            <th>价格</th>
                            <th>利润</th>
                        </tr>
                        {self._generate_product_rows(bottom_products)}
                    </table>
                </div>
                
                {self._generate_anomaly_section(anomalies)}
                
                <div class="footer">
                    <p>本报告由 {config.APP_NAME} 自动生成</p>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_product_rows(self, products: List[dict]) -> str:
        """生成产品表格行"""
        rows = ""
        for p in products:
            rows += f"""
            <tr>
                <td>{p.get('product_id', 'N/A')}</td>
                <td>{p.get('product_name', 'N/A')[:50]}...</td>
                <td>¥{p.get('price', 0):,.2f}</td>
                <td>¥{p.get('profit', 0):,.2f}</td>
            </tr>
            """
        return rows if rows else "<tr><td colspan='4'>无数据</td></tr>"
    
    def _generate_anomaly_section(self, anomalies: List[dict]) -> str:
        """生成异常提醒区块"""
        if not anomalies:
            return ""
        
        anomaly_html = """
        <div class="section">
            <div class="section-title">⚠️ 异常提醒</div>
            <div class="alert">
                <strong>检测到 {} 个销量异常的产品：</strong>
                <ul>
        """.format(len(anomalies))
        
        for a in anomalies[:5]:
            anomaly_type = a.get('anomaly_type', '未知')
            product_name = a.get('product_name', 'N/A')[:30]
            product_id = a.get('product_id', 'N/A')
            z_score = abs(a.get('z_score', 0))
            anomaly_html += f"<li><strong>{product_id}</strong> ({product_name}): {anomaly_type} (Z-score: {z_score:.2f})</li>"
        
        anomaly_html += """
                </ul>
            </div>
        </div>
        """
        return anomaly_html


# 全局邮件服务实例
email_service = EmailService()
