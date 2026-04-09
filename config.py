"""
配置文件 - 包含所有可配置的参数
支持环境变量覆盖
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 应用配置 ====================
APP_NAME = "IMVU Analytics Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ==================== 服务器配置 ====================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ==================== 数据库配置 ====================
# Railway PostgreSQL 或 SQLite
import os
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 如果没有配置DATABASE_URL，使用SQLite
if not DATABASE_URL:
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DATABASE_URL = f"sqlite:///{DATA_DIR}/marketing_analytics.db"

# Railway PostgreSQL URL 格式转换 (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==================== 邮件配置 ====================
# SMTP服务器设置
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

# 邮件发送者
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)

# 邮件接收者列表（逗号分隔）
EMAIL_TO = os.getenv("EMAIL_TO", "")

# ==================== 报告配置 ====================
# 自动报告生成时间（UTC时间，转换为北京时间需+8小时）
# 默认每天早上9点生成报告 (UTC 1:00)
REPORT_CRON_HOUR = int(os.getenv("REPORT_CRON_HOUR", "1"))
REPORT_CRON_MINUTE = int(os.getenv("REPORT_CRON_MINUTE", "0"))

# 报告保存路径
REPORT_DIR = os.getenv("REPORT_DIR", "./reports")

# ==================== 数据配置 ====================
# 允许的最大上传文件大小 (MB)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "50"))

# XML数据字段映射
XML_FIELD_MAPPING = {
    'product_id': 'Product Id',
    'product_name': 'Product Name',
    'price': 'Wholesale Price',
    'profit': 'Profit',
    'visible': 'Visible',
    'direct_sales': 'Direct Sales',
    'indirect_sales': 'Indirect Sales',
    'promoted_sales': 'Sales While Promoted',
    'cart_adds': 'Adds to Cart',
    'wishlist_adds': 'Adds to Wishlist',
    'organic_impressions': 'Organic Impressions',
    'paid_impressions': 'Paid Impressions',
}

# ==================== 异常检测阈值 ====================
# 销量异常波动阈值（标准差的倍数）
SALES_ANOMALY_THRESHOLD = float(os.getenv("SALES_ANOMALY_THRESHOLD", "2.0"))

# 高利润产品利润率阈值
HIGH_PROFIT_MARGIN = float(os.getenv("HIGH_PROFIT_MARGIN", "0.3"))

# 低转化率阈值
LOW_CONVERSION_THRESHOLD = float(os.getenv("LOW_CONVERSION_THRESHOLD", "0.01"))

# ==================== DeepSeek API 配置 ====================
# AI洞察功能需要配置DeepSeek API Key
# 获取方式: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
