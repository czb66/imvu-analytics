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
from app.database import init_db, engine
from app.routers import upload, dashboard, diagnosis, report, compare, insights, auth, subscription
from app.services.email_service import email_service
from app.services.report_generator import scheduler, start_scheduler, stop_scheduler

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
app.include_router(subscription.router)  # 订阅路由
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
    stop_scheduler()


@app.get("/")
async def root():
    """首页 - 重定向到登录页"""
    return RedirectResponse(url="/login")


@app.get("/health/db")
async def db_health_check():
    """数据库健康检查"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}



@app.get("/health")
async def health_check():
    """健康检查端点 - 用于Railway健康检查"""
    return {"status": "healthy", "service": config.APP_NAME, "version": config.APP_VERSION}


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
    return templates.TemplateResponse("report.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/insights", response_class=HTMLResponse)
async def insights_page(request: Request):
    """AI洞察页面"""
    return templates.TemplateResponse("insights.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """上传页面"""
    return templates.TemplateResponse("upload.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """个人中心页面"""
    return templates.TemplateResponse("profile.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """定价页面"""
    return templates.TemplateResponse("pricing.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    """支付成功页面"""
    return templates.TemplateResponse("success.html", {"request": request, "app_name": config.APP_NAME})


@app.get("/cancel", response_class=HTMLResponse)
async def cancel_page(request: Request):
    """支付取消页面"""
    return templates.TemplateResponse("cancel.html", {"request": request, "app_name": config.APP_NAME})


# 使用 report_generator 模块中的调度器
# scheduler, start_scheduler, stop_scheduler 已从 report_generator 导入
