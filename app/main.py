"""
FastAPI 主应用入口
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import os

import config
from app.database import init_db
from app.routers import upload, dashboard, diagnosis, report, compare, insights, auth
from app.services.email_service import email_service

# 配置日志
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="营销数据分析平台 - 支持XML数据上传、多维度分析和自动化报告"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(diagnosis.router)
app.include_router(report.router)
app.include_router(compare.router)
app.include_router(insights.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"启动 {config.APP_NAME} v{config.APP_VERSION}")
    
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


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("正在关闭应用...")
    scheduler.shutdown()


@app.get("/")
async def root():
    """首页"""
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
            "docs": "/docs"
        }
    }


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/dashboard")
async def dashboard_page():
    """仪表盘页面"""
    pass


@app.get("/diagnosis")
async def diagnosis_page():
    """诊断页面"""
    pass


@app.get("/compare")
async def compare_page():
    """对比页面"""
    pass


@app.get("/report")
async def report_page():
    """报告页面"""
    pass


@app.get("/insights")
async def insights_page():
    """AI洞察页面"""
    pass


@app.get("/upload")
async def upload_page():
    """上传页面"""
    pass


@app.get("/settings")
async def settings_page():
    """设置页面"""
    pass


# 全局调度器
scheduler = BackgroundScheduler()


def start_scheduler():
    """启动定时任务"""
    from app.services.report_generator import report_generator
    
    # 每天定时生成报告
    scheduler.add_job(
        report_generator.generate_daily_report,
        'cron',
        hour=config.REPORT_CRON_HOUR,
        minute=config.REPORT_CRON_MINUTE,
        id='daily_report',
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"定时任务已启动 (每天 {config.REPORT_CRON_HOUR}:{config.REPORT_CRON_MINUTE:02d} UTC)")
