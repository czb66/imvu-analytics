"""
FastAPI 主应用入口
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import logging
import os

import config
from app.database import init_db, engine
from app.routers import upload, dashboard, diagnosis, report, compare, insights, auth, subscription, admin, contact, promo_card, benchmark, user, export, blog, feedback
from app.services.email_service import email_service
from app.services.report_generator import scheduler, start_scheduler, stop_scheduler
from app.services.cache import init_cache, get_cache
from app.core.limiter import limiter

# 配置日志
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 环境配置
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
IS_DEVELOPMENT = ENVIRONMENT == "development"

# 创建FastAPI应用
# 仅在开发环境启用 API 文档
app_kwargs = {
    "title": config.APP_NAME,
    "version": config.APP_VERSION,
    "description": "营销数据分析平台 - 支持XML数据上传、多维度分析和自动化报告"
}

if not IS_DEVELOPMENT:
    # 生产环境关闭 Swagger/Docs
    app_kwargs["docs_url"] = None
    app_kwargs["redoc_url"] = None
    app_kwargs["openapi_url"] = None
    logger.info("生产环境：API文档已关闭")
else:
    logger.info("开发环境：API文档已启用")

app = FastAPI(**app_kwargs)

# 添加速率限制状态到 app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-DeepSeek-Key"],
)

# 挂载静态文件
if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(subscription.router)  # 订阅路由
app.include_router(user.router)  # 用户配额路由
app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(diagnosis.router)
app.include_router(report.router)
app.include_router(compare.router)
app.include_router(insights.router)
app.include_router(benchmark.router)  # 竞品分析路由
app.include_router(promo_card.router)  # 推广卡片路由
app.include_router(admin.router)  # 后台管理路由
app.include_router(contact.router)  # 联系我们路由
app.include_router(export.router)  # 数据导出路由
app.include_router(blog.router)  # 博客路由
app.include_router(feedback.router)  # 反馈和NPS路由
app.include_router(feedback.admin_router)  # 反馈管理路由


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"启动 {config.APP_NAME} v{config.APP_VERSION}")
    
    try:
        # 初始化缓存服务
        cache = init_cache(max_size=500, default_ttl=300)
        app.state.cache = cache
        logger.info("缓存服务初始化完成")
    except Exception as e:
        logger.warning(f"缓存服务初始化失败: {e}")
    
    try:
        # 初始化数据库
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 不抛出异常，允许应用启动
    
    try:
        # 确保报告目录存在
        os.makedirs(config.REPORT_DIR, exist_ok=True)
    except Exception as e:
        logger.warning(f"创建报告目录失败: {e}")
    
    try:
        # 启动定时任务
        start_scheduler()
    except Exception as e:
        logger.warning(f"启动定时任务失败: {e}")
    
    try:
        # 创建博客种子数据
        from scripts.seed_blog import create_seed_posts
        create_seed_posts()
        logger.info("博客种子数据初始化完成")
    except Exception as e:
        logger.warning(f"博客种子数据初始化失败: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("正在关闭应用...")
    stop_scheduler()


@app.get("/")
async def root(request: Request):
    """首页 - 显示落地页（未登录用户）或跳转仪表盘（已登录用户）"""
    # 检查用户是否已登录
    token = request.cookies.get("access_token")
    if token:
        # 已登录用户跳转到仪表盘
        return RedirectResponse(url="/dashboard")
    # 未登录用户显示落地页
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/health/db")
async def db_health_check():
    """数据库健康检查"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": "Database connection failed"}



@app.get("/health")
async def health_check():
    """健康检查端点 - 用于Railway健康检查"""
    return {"status": "healthy", "service": config.APP_NAME, "version": config.APP_VERSION}


@app.get("/promo-card", response_class=HTMLResponse)
async def promo_card_generator(request: Request):
    """产品推广卡片生成器 - 独立工具页面"""
    return templates.TemplateResponse("promo_card.html", {"request": request})


@app.get("/benchmark", response_class=HTMLResponse)
async def benchmark_page(request: Request):
    """竞品分析页面"""
    return templates.TemplateResponse("benchmark.html", {"request": request})


@app.get("/api/status")
async def api_status():
    """API状态端点"""
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "endpoints": {
            "auth": "/api/auth/",
            "upload": "/api/upload/",
            "dashboard": "/api/dashboard/",
            "diagnosis": "/api/diagnosis/",
            "report": "/api/report/",
            "compare": "/api/compare/",
            "insights": "/api/insights/",
            "benchmark": "/api/benchmark/",
            "docs": "/docs"
        }
    }


# Base URL for SEO - 从环境变量读取，避免硬编码
BASE_URL = config.APP_BASE_URL
APP_DESCRIPTION = "IMVU营销数据分析平台 - 专业的产品销售数据追踪、分析和报告工具"
APP_KEYWORDS = "IMVU,数据分析,营销,销售报告,产品追踪,商业智能"

def get_seo_context(page_title, page_path, meta_description=None):
    """生成SEO上下文"""
    return {
        "base_url": BASE_URL,
        "page_title": page_title,
        "page_path": page_path,
        "meta_description": meta_description or f"{page_title} - IMVU Analytics - {APP_DESCRIPTION}",
        "meta_keywords": APP_KEYWORDS,
        "canonical_url": f"{BASE_URL}{page_path}",
        "app_name": config.APP_NAME
    }


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    ctx = get_seo_context("用户登录", "/login", "登录IMVU Analytics，开始您的产品销售数据分析之旅")
    return templates.TemplateResponse("login.html", {"request": request, **ctx})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """忘记密码页面"""
    return templates.TemplateResponse("forgot-password.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """重置密码页面"""
    return templates.TemplateResponse("reset-password.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """仪表盘页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/diagnosis", response_class=HTMLResponse)
async def diagnosis_page(request: Request):
    """诊断页面"""
    return templates.TemplateResponse("diagnosis.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    """对比页面"""
    return templates.TemplateResponse("compare.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    """报告页面"""
    ctx = get_seo_context("销售报告", "/report", "生成和下载IMVU产品销售分析报告，支持PDF和Excel格式")
    return templates.TemplateResponse("report.html", {"request": request, **ctx})


@app.get("/insights", response_class=HTMLResponse)
async def insights_page(request: Request):
    """AI洞察页面"""
    return templates.TemplateResponse("insights.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """上传页面"""
    return templates.TemplateResponse("upload.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """后台管理页面"""
    return templates.TemplateResponse("admin.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/admin/promo-cards", response_class=HTMLResponse)
async def admin_promo_cards_page(request: Request):
    """后台推广卡片统计页面"""
    return templates.TemplateResponse("admin_promo_cards.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """个人中心页面"""
    ctx = get_seo_context("个人中心", "/profile", "查看和管理您的IMVU Analytics个人资料和使用情况")
    return templates.TemplateResponse("profile.html", {"request": request, **ctx})


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """定价页面"""
    return templates.TemplateResponse("pricing.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/guide", response_class=HTMLResponse)
async def guide_page(request: Request):
    """使用指南页面 - 无需登录"""
    return templates.TemplateResponse("guide.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """服务条款页面 - 无需登录"""
    ctx = get_seo_context("Terms of Service", "/terms", "IMVU Analytics Terms of Service - Rules and guidelines for using our platform")
    return templates.TemplateResponse("terms.html", {"request": request, **ctx})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """隐私政策页面 - 无需登录"""
    ctx = get_seo_context("Privacy Policy", "/privacy", "IMVU Analytics Privacy Policy - How we collect, use and protect your data")
    return templates.TemplateResponse("privacy.html", {"request": request, **ctx})


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    """支付成功页面"""
    return templates.TemplateResponse("success.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/cancel", response_class=HTMLResponse)
async def cancel_page(request: Request):
    """支付取消页面"""
    return templates.TemplateResponse("cancel.html", {"request": request, "app_name": config.APP_NAME})


# ========== SEO 相关路由 ==========

@app.get("/sitemap.xml", tags=["SEO"])
async def sitemap_xml():
    """Sitemap XML - 供搜索引擎爬取"""
    with open("app/templates/sitemap.xml", "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content=content, media_type="application/xml")


@app.get("/robots.txt", tags=["SEO"])
async def robots_txt():
    """Robots.txt - 爬虫指令文件"""
    with open("app/templates/robots.txt", "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content=content, media_type="text/plain")


# 使用 report_generator 模块中的调度器
# scheduler, start_scheduler, stop_scheduler 已从 report_generator 导入


# =====================================================
# 页面访问统计中间件
# =====================================================
from starlette.middleware.base import BaseHTTPMiddleware

class PageViewMiddleware(BaseHTTPMiddleware):
    """页面访问统计中间件"""
    
    # 排除的路径（不记录统计）
    EXCLUDED_PATHS = [
        '/static/',       # 静态资源
        '/health',        # 健康检查
        '/health/db',     # 数据库健康检查
        '/api/status',    # API状态
        '/favicon.ico',   # 图标
        '/docs',          # API文档
        '/openapi.json',  # OpenAPI规范
        '/redoc',         # ReDoc文档
    ]
    
    # 排除的路径前缀
    EXCLUDED_PREFIXES = [
        '/api/',          # API请求
        '/_next/',        # Next.js 静态资源
    ]
    
    async def dispatch(self, request, call_next):
        path = request.url.path
        
        # 检查是否需要跳过记录
        should_skip = (
            path in self.EXCLUDED_PATHS or
            any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES)
        )
        
        if not should_skip:
            import asyncio
            asyncio.create_task(self.record_visit(request))
        
        response = await call_next(request)
        return response
    
    async def record_visit(self, request):
        """记录页面访问"""
        try:
            from app.models import PageView
            from app.database import SessionLocal
            
            # 脱敏处理IP地址
            client_ip = request.client.host if request.client else "unknown"
            if client_ip and client_ip != "unknown":
                parts = client_ip.split('.')
                if len(parts) >= 2:
                    client_ip = '.'.join(parts[:2]) + '.xxx.xxx'
            
            user_agent = request.headers.get('user-agent', '')[:500]
            referrer = request.headers.get('referer', '')[:500]
            
            db = SessionLocal()
            try:
                page_view = PageView(
                    path=request.url.path,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    referrer=referrer if referrer else None
                )
                db.add(page_view)
                db.commit()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"记录访问失败: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"访问统计异常: {e}")


# 添加中间件
app.add_middleware(PageViewMiddleware)
