"""
邮件发送服务 - 支持 Resend API 和 SMTP
优先使用 Resend (推荐 Railway 免费版)
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
    """邮件发送服务 - 支持 Resend 和 SMTP"""
    
    def __init__(self):
        """初始化邮件服务"""
        self.resend_api_key = config.RESEND_API_KEY
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.use_tls = config.SMTP_USE_TLS
        self.from_email = config.EMAIL_FROM
        
        # 判断使用哪种方式
        self.use_resend = bool(self.resend_api_key)
    
    def send_report(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        attachments: List[str] = None
    ) -> tuple:
        """
        发送报告邮件
        
        优先使用 Resend API，如果未配置则尝试 SMTP
        
        Args:
            to_emails: 收件人邮箱列表
            subject: 邮件主题
            html_content: HTML格式的邮件内容
            attachments: 附件文件路径列表
            
        Returns:
            (success, message)
        """
        if not to_emails:
            return False, "没有收件人地址"
        
        # 优先使用 Resend
        if self.use_resend:
            return self._send_via_resend(to_emails, subject, html_content, attachments)
        
        # 回退到 SMTP
        if self.smtp_user and self.smtp_password:
            return self._send_via_smtp(to_emails, subject, html_content, attachments)
        
        logger.warning("邮件服务未配置 (Resend 或 SMTP)")
        return False, "邮件服务未配置，请联系管理员配置 RESEND_API_KEY"
    
    def _send_via_resend(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        attachments: List[str] = None
    ) -> tuple:
        """使用 Resend API 发送邮件"""
        try:
            import resend
            
            resend.api_key = self.resend_api_key
            
            # 构建发送参数
            params = {
                "from": self.from_email or "IMVU Analytics <onboarding@resend.dev>",
                "to": to_emails,
                "subject": subject,
                "html": html_content,
            }
            
            # 发送邮件
            email = resend.Emails.send(params)
            
            logger.info(f"Resend 邮件发送成功: {subject} -> {to_emails}, ID: {email.get('id')}")
            return True, "邮件发送成功"
            
        except ImportError:
            logger.error("resend 包未安装，请运行: pip install resend")
            return False, "邮件服务配置错误"
        except Exception as e:
            logger.error(f"Resend 邮件发送失败: {e}")
            return False, f"邮件发送失败: {str(e)}"
    
    def _send_via_smtp(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        attachments: List[str] = None
    ) -> tuple:
        """使用 SMTP 发送邮件"""
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
            try:
                # 尝试使用 SSL 端口 465
                if self.smtp_port == 465:
                    with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as server:
                        server.login(self.smtp_user, self.smtp_password)
                        server.sendmail(self.from_email, to_emails, msg.as_string())
                else:
                    # 使用 TLS 端口 587
                    with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                        server.ehlo()
                        if self.use_tls:
                            server.starttls()
                            server.ehlo()
                        server.login(self.smtp_user, self.smtp_password)
                        server.sendmail(self.from_email, to_emails, msg.as_string())
            except Exception as conn_err:
                logger.error(f"SMTP连接失败: {conn_err}")
                # 如果 587 失败，尝试 465
                if self.smtp_port != 465:
                    logger.info("尝试使用 SSL 端口 465...")
                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
                            server.login(self.smtp_user, self.smtp_password)
                            server.sendmail(self.from_email, to_emails, msg.as_string())
                    except Exception as e:
                        raise e
                else:
                    raise conn_err
            
            logger.info(f"SMTP 邮件发送成功: {subject} -> {to_emails}")
            return True, "邮件发送成功"
            
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
        recipients: List[str] = None,
        download_url: str = None
    ) -> tuple:
        """
        发送每日报告
        
        Args:
            report_data: 报告数据字典
            recipients: 收件人列表（为空则使用配置的默认收件人）
            download_url: 带token的下载链接（可选）
            
        Returns:
            (success, message)
        """
        if recipients is None:
            recipients = [e.strip() for e in config.EMAIL_TO.split(',') if e.strip()]
        
        if not recipients:
            return False, "没有配置收件人"
        
        subject = f"📊 {config.APP_NAME} - 每日营销报告 {datetime.now().strftime('%Y-%m-%d')}"
        html_content = self._generate_daily_report_html(report_data, download_url)
        
        return self.send_report(recipients, subject, html_content)
    
    def _generate_daily_report_html(self, data: dict, download_url: str = None) -> str:
        """生成每日报告HTML"""
        summary = data.get('summary', {})
        top_products = data.get('top_products', [])[:5]
        bottom_products = data.get('bottom_products', [])[:5]
        anomalies = data.get('anomalies', [])
        
        # 辅助函数：计算总销量
        def get_total_sales(p):
            return (p.get('direct_sales') or 0) + (p.get('indirect_sales') or 0) + (p.get('promoted_sales') or 0)
        
        # 下载链接按钮
        download_section = ""
        if download_url:
            download_section = f"""
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{download_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        📥 查看完整报告
                    </a>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">链接24小时内有效</p>
                </div>
            """
        
        # 格式化异常数据
        anomaly_html = ""
        if anomalies:
            anomaly_items = []
            for a in anomalies[:5]:
                product_id = a.get('product_id', 'N/A')
                product_name = (a.get('product_name') or 'N/A')[:25]
                anomaly_type = a.get('anomaly_type') or '异常'
                z_score = abs(a.get('z_score') or 0)
                anomaly_items.append(f'<div class="anomaly"><strong>{product_id}</strong> - {product_name}...<br><small>{anomaly_type} (Z-score: {z_score:.2f})</small></div>')
            anomaly_html = f'<h2>⚠️ 异常检测 ({len(anomalies)} 个)</h2>' + "".join(anomaly_items)
        
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
                .metric-label {{ font-size: 12px; color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background: #f8f9fa; }}
                .anomaly {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 {config.APP_NAME}</h1>
                    <p>每日营销数据报告 - {datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('total_sales', 0):,}</div>
                        <div class="metric-label">总销量</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${(summary.get('total_profit_usd') or summary.get('total_profit') or 0):,.2f}</div>
                        <div class="metric-label">总利润</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('total_products', 0)}</div>
                        <div class="metric-label">产品总数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('visible_products', 0)}</div>
                        <div class="metric-label">可见产品</div>
                    </div>
                </div>
                
                <h2>🏆 Top 5 热销产品</h2>
                <table>
                    <tr><th>产品ID</th><th>产品名称</th><th>销量</th><th>利润</th></tr>
                    {"".join(f"<tr><td>{p.get('product_id', '')}</td><td>{(p.get('product_name') or '')[:30]}</td><td>{get_total_sales(p)} 个</td><td>${(p.get('profit') or 0):,.2f}</td></tr>" for p in top_products)}
                </table>
                
                {anomaly_html}
                
                {download_section}
                
                <p style="text-align: center; color: #666; margin-top: 30px;">
                    此报告由 <a href="{config.APP_BASE_URL}" style="color: #667eea;">{config.APP_NAME}</a> 自动生成
                </p>
            </div>
        </body>
        </html>
        """
        return html


# 全局邮件服务实例
email_service = EmailService()


def send_contact_email(
    to_email: str,
    subject: str,
    html_content: str,
    user_email: str = None,
    user_name: str = None,
    attachments: list = None
) -> tuple:
    """
    发送联系表单邮件
    
    Args:
        to_email: 收件人邮箱（客服邮箱）
        subject: 邮件主题
        html_content: HTML格式的邮件内容
        user_email: 用户邮箱（用于回复）
        user_name: 用户姓名
        attachments: 附件文件路径列表
        
    Returns:
        (success, message)
    """
    return email_service.send_report(
        to_emails=[to_email],
        subject=subject,
        html_content=html_content,
        attachments=attachments
    )



def send_referral_reward_notification(
    to_email: str,
    username: str,
    days: int = 7
) -> tuple:
    """
    发送推荐奖励通知邮件
    
    Args:
        to_email: 收件人邮箱
        username: 用户名
        days: 奖励天数
    
    Returns:
        (success, message)
    """
    try:
        subject = f"🎉 您的推荐奖励已到账！+{days}天 Pro 权限"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .reward-box {{ background: white; border-radius: 10px; padding: 30px; text-align: center; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .reward-amount {{ font-size: 48px; font-weight: bold; color: #667eea; }}
                .btn {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 推荐奖励到账！</h1>
            </div>
            <div class="content">
                <p>亲爱的 <strong>{username}</strong>：</p>
                <p>感谢您推荐新用户加入 IMVU Analytics！</p>
                
                <div class="reward-box">
                    <p style="font-size: 18px; color: #666;">您已获得</p>
                    <div class="reward-amount">+{days}天</div>
                    <p style="font-size: 18px; color: #666;">Pro 权限</p>
                </div>
                
                <p>您推荐的用户已完成首次数据上传，按照我们的推荐计划，您获得了 <strong>+{days}天 Pro 权限</strong>奖励！</p>
                
                <p style="text-align: center;">
                    <a href="{config.SITE_URL}/profile" class="btn">查看我的账户</a>
                </p>
                
                <div class="footer">
                    <p>继续推荐更多好友，获得更多奖励！</p>
                    <p style="margin-top: 20px;">此邮件由 {config.APP_NAME} 自动发送</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"发送推荐奖励通知邮件失败: {e}")
        return False, str(e)