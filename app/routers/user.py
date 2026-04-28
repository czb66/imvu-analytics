"""
用户配额和限流状态路由
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
import logging

from app.services.auth import get_current_user
from app.core.rate_limiter import get_user_quota_info, get_user_tier, RATE_LIMITS, FEATURE_NAMES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/rate-limits")
async def get_user_rate_limits(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的各功能剩余配额
    
    返回各功能的限流配置和使用情况
    
    Returns:
    {
        "success": true,
        "tier": "pro",
        "tier_display": "Pro",
        "is_premium": true,
        "quotas": {
            "insights": {
                "limit": 30,
                "limit_str": "30/hour",
                "used": 5,
                "remaining": 25,
                "reset_in_seconds": 1800,
                "feature_name": "AI洞察"
            },
            ...
        }
    }
    """
    try:
        quota_info = get_user_quota_info(current_user)
        
        return {
            "success": True,
            **quota_info
        }
    except Exception as e:
        logger.error(f"获取用户配额失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "操作失败，请稍后重试"}
        )


@router.get("/tier")
async def get_user_tier_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的等级信息
    
    Returns:
    {
        "success": true,
        "tier": "pro",
        "tier_display": "Pro",
        "is_premium": true,
        "limits": {
            "insights": "30/hour",
            "dashboard": "120/hour",
            ...
        }
    }
    """
    try:
        tier = get_user_tier(current_user)
        tier_display = {
            "free": "Free",
            "pro": "Pro", 
            "admin": "Admin"
        }.get(tier, tier)
        
        # 获取该等级的限流配置
        tier_limits = RATE_LIMITS.get(tier, {})
        limits = {}
        for feature in FEATURE_NAMES.keys():
            if feature in tier_limits:
                limits[feature] = tier_limits[feature]
            elif "default" in tier_limits:
                limits[feature] = tier_limits["default"]
        
        return {
            "success": True,
            "tier": tier,
            "tier_display": tier_display,
            "is_premium": tier in ("pro", "admin"),
            "limits": limits
        }
    except Exception as e:
        logger.error(f"获取用户等级失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "操作失败，请稍后重试"}
        )


__all__ = ["router"]
