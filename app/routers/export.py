"""
数据导出路由 - 提供 CSV/Excel 格式导出 API
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db, UserRepository
from app.services.auth import get_current_user
from app.services.export import (
    export_dashboard_csv, export_dashboard_excel,
    export_products_csv, export_products_excel
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/export", tags=["数据导出"])

# 导出限流配置
EXPORT_RATE_LIMITS = {
    "free": {"daily": 3, "name": "Free"},
    "pro": {"daily": 20, "name": "Pro"}
}


class ExportTracker:
    """导出次数追踪（内存存储，生产环境建议使用 Redis）"""
    _daily_exports = {}
    
    @classmethod
    def get_daily_count(cls, user_id: int) -> int:
        """获取用户今日导出次数"""
        today = datetime.utcnow().date().isoformat()
        key = f"{user_id}:{today}"
        return cls._daily_exports.get(key, 0)
    
    @classmethod
    def increment(cls, user_id: int) -> int:
        """增加导出次数，返回新的计数"""
        today = datetime.utcnow().date().isoformat()
        key = f"{user_id}:{today}"
        cls._daily_exports[key] = cls._daily_exports.get(key, 0) + 1
        return cls._daily_exports[key]
    
    @classmethod
    def get_remaining(cls, user_id: int, tier: str) -> int:
        """获取剩余导出次数"""
        used = cls.get_daily_count(user_id)
        limit = EXPORT_RATE_LIMITS.get(tier, {}).get("daily", 3)
        return max(0, limit - used)


def _check_export_permission(user_id: int, format: str, db: Session) -> dict:
    """
    检查导出权限
    
    Returns:
        dict: {"allowed": bool, "message": str, "tier": str}
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return {"allowed": False, "message": "User not found", "tier": "free"}
    
    # 检查用户等级
    tier = "pro" if user.has_premium_access else "free"
    daily_limit = EXPORT_RATE_LIMITS.get(tier, {}).get("daily", 3)
    
    # Excel 导出仅限 Pro 用户
    if format == "excel" and tier == "free":
        return {
            "allowed": False,
            "message": "Excel export is a Pro feature",
            "tier": tier,
            "error_code": "pro_only"
        }
    
    # 检查限流
    remaining = ExportTracker.get_remaining(user_id, tier)
    if remaining <= 0:
        return {
            "allowed": False,
            "message": f"Daily export limit reached ({daily_limit}/day)",
            "tier": tier,
            "error_code": "limit_reached"
        }
    
    return {"allowed": True, "tier": tier, "remaining": remaining}


@router.get("/dashboard")
async def export_dashboard(
    format: str = Query(..., regex="^(csv|excel)$", description="导出格式: csv 或 excel"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出仪表盘数据
    
    - **format**: csv 或 excel
    - **权限**: Free 用户每天3次，Pro 用户每天20次
    - **Excel导出**: 仅限 Pro 用户
    """
    user_id = current_user["id"]
    
    # 检查权限
    permission = _check_export_permission(user_id, format, db)
    if not permission["allowed"]:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "message": permission["message"],
                "error_code": permission.get("error_code", "permission_denied")
            }
        )
    
    try:
        # 执行导出
        if format == "csv":
            file_content = export_dashboard_csv(user_id)
            return StreamingResponse(
                iter([file_content.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=dashboard_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        else:  # excel
            file_content = export_dashboard_excel(user_id)
            return StreamingResponse(
                iter([file_content.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=dashboard_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
                }
            )
    except Exception as e:
        logger.error(f"导出仪表盘数据失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "操作失败，请稍后重试"}
        )
    finally:
        # 增加导出计数
        ExportTracker.increment(user_id)
        logger.info(f"用户 {user_id} 导出仪表盘数据，格式: {format}")


@router.get("/products/{dataset_id}")
async def export_products(
    dataset_id: int,
    format: str = Query(..., regex="^(csv|excel)$", description="导出格式: csv 或 excel"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出指定数据集的产品明细
    
    - **dataset_id**: 数据集 ID
    - **format**: csv 或 excel
    - **权限**: Free 用户每天3次，Pro 用户每天20次
    - **Excel导出**: 仅限 Pro 用户
    """
    user_id = current_user["id"]
    
    # 检查权限
    permission = _check_export_permission(user_id, format, db)
    if not permission["allowed"]:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "message": permission["message"],
                "error_code": permission.get("error_code", "permission_denied")
            }
        )
    
    # 验证数据集归属
    from app.database import DatasetRepository
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "Dataset not found"}
        )
    
    if dataset.user_id != user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "Access denied to this dataset"}
        )
    
    try:
        # 执行导出
        if format == "csv":
            file_content = export_products_csv(user_id, dataset_id)
            return StreamingResponse(
                iter([file_content.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=products_dataset_{dataset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        else:  # excel
            file_content = export_products_excel(user_id, dataset_id)
            return StreamingResponse(
                iter([file_content.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=products_dataset_{dataset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
                }
            )
    except Exception as e:
        logger.error(f"导出产品数据失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "操作失败，请稍后重试"}
        )
    finally:
        # 增加导出计数
        ExportTracker.increment(user_id)
        logger.info(f"用户 {user_id} 导出数据集 {dataset_id} 产品数据，格式: {format}")


@router.get("/quota")
async def get_export_quota(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取导出配额信息
    """
    user_id = current_user["id"]
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "User not found"}
        )
    
    tier = "pro" if user.has_premium_access else "free"
    limit = EXPORT_RATE_LIMITS.get(tier, {}).get("daily", 3)
    used = ExportTracker.get_daily_count(user_id)
    remaining = max(0, limit - used)
    
    return {
        "success": True,
        "data": {
            "tier": tier,
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "reset_at": (datetime.utcnow() + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
        }
    }
