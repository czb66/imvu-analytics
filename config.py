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

# 网站配置 ====================
SITE_URL = os.getenv("SITE_URL", "https://imvucreators.com")
SITE_NAME = "IMVU Analytics"
SITE_DESCRIPTION = "IMVU营销数据分析平台 - 专业的产品销售数据追踪、分析和报告工具"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://imvucreators.com,https://www.imvucreators.com").split(",")

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

# ==================== JWT 认证配置 ====================
# JWT密钥（重要：生产环境必须设置复杂的随机密钥）
import secrets
_jwt_key = os.getenv("JWT_SECRET_KEY")
if not _jwt_key:
    import warnings
    warnings.warn("JWT_SECRET_KEY 未设置，使用随机生成的临时密钥。请在生产环境中设置此环境变量。")
    _jwt_key = secrets.token_urlsafe(64)
JWT_SECRET_KEY = _jwt_key
# JWT算法
JWT_ALGORITHM = "HS256"
# Token有效期（分钟）
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 默认7天
# 记住我 Token有效期（分钟）
JWT_REMEMBER_EXPIRE_MINUTES = int(os.getenv("JWT_REMEMBER_EXPIRE_MINUTES", "43200"))  # 默认30天

# ==================== 邮件配置 ====================
# Resend API (推荐，支持 Railway 免费版)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# SMTP服务器设置 (需要 Railway Pro 版本)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

# 邮件发送者
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER or "onboarding@resend.dev")

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

# ==================== Stripe 订阅配置 ====================
# Stripe API Keys - 动态获取函数（确保每次调用时都读取最新环境变量）
def get_stripe_secret_key():
    return os.getenv("STRIPE_SECRET_KEY", "")

def get_stripe_publishable_key():
    return os.getenv("STRIPE_PUBLISHABLE_KEY", "")

def get_stripe_webhook_secret():
    return os.getenv("STRIPE_WEBHOOK_SECRET", "")

def get_stripe_price_id():
    return os.getenv("STRIPE_PRICE_ID", "")

def get_stripe_product_id():
    return os.getenv("STRIPE_PRODUCT_ID", "")

# 订阅价格（美元/月）
SUBSCRIPTION_PRICE = 12.00

# 应用基础URL（用于Stripe回调）
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://imvucreators.com")

# 白名单邮箱列表 - 统一管理
WHITELIST_EMAILS = [
    "whitelist@imvu-analytics.com",
    "nlfd8910@gmail.com"
]

def is_email_whitelisted(email: str) -> bool:
    """检查邮箱是否在白名单中"""
    return email.lower() in [e.lower() for e in WHITELIST_EMAILS]