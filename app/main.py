"""
FastAPI 主应用入口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import os

import config
from app.database import init_db
from app.routers import upload, dashboard, diagnosis, report
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

# 挂载静态文件
if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 注册路由
app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(diagnosis.router)
app.include_router(report.router)


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
            "upload": "/api/upload/",
            "dashboard": "/api/dashboard/",
            "diagnosis": "/api/diagnosis/",
            "report": "/api/report/",
            "docs": "/docs"
        }
    }


@app.get("/dashboard")
async def dashboard_page():
    """仪表盘页面"""
    return templates.TemplateResponse("dashboard.html", {
        "request": {},
        "app_name": config.APP_NAME,
        "version": config.APP_VERSION
    })


@app.get("/diagnosis")
async def diagnosis_page():
    """诊断页面"""
    return templates.TemplateResponse("diagnosis.html", {
        "request": {},
        "app_name": config.APP_NAME,
        "version": config.APP_VERSION
    })


@app.get("/report")
async def report_page():
    """报告页面"""
    return templates.TemplateResponse("report.html", {
        "request": {},
        "app_name": config.APP_NAME,
        "version": config.APP_VERSION
    })


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        from sqlalchemy import text
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ==================== 定时任务 ====================

scheduler = BackgroundScheduler()


def generate_daily_report():
    """生成每日报告"""
    try:
        logger.info("开始生成每日报告...")
        
        from app.database import get_db, ProductDataRepository
        from app.services.analytics import AnalyticsService
        
        with get_db() as db:
            repo = ProductDataRepository(db)
            products = repo.get_all()
            
            if not products:
                logger.warning("没有产品数据，跳过报告生成")
                return
            
            product_dicts = [
                {
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
                for p in products
            ]
            
            analytics = AnalyticsService(product_dicts)
            
            report_data = {
                'summary': analytics.get_summary_metrics(),
                'top_products': analytics.get_top_products(10),
                'bottom_products': analytics.get_bottom_products(10),
                'anomalies': analytics.detect_sales_anomalies()
            }
            
            # 发送邮件
            recipients = [e.strip() for e in config.EMAIL_TO.split(',') if e.strip()]
            if recipients and config.SMTP_USER:
                success, message = email_service.send_daily_report(report_data, recipients)
                if success:
                    logger.info(f"每日报告已发送至: {recipients}")
                else:
                    logger.error(f"邮件发送失败: {message}")
            
            logger.info("每日报告生成完成")
            
    except Exception as e:
        logger.error(f"生成每日报告失败: {e}")


def start_scheduler():
    """启动定时任务调度器"""
    # 添加每日报告任务
    scheduler.add_job(
        generate_daily_report,
        'cron',
        hour=config.REPORT_CRON_HOUR,
        minute=config.REPORT_CRON_MINUTE,
        id='daily_report',
        name='每日营销报告',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"定时任务已启动 (每天 {config.REPORT_CRON_HOUR}:{config.REPORT_CRON_MINUTE:02d} UTC)")


# ==================== CORS支持 ====================

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
