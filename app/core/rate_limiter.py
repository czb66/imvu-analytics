"""
分层限流配置与实现
根据用户等级（free/pro/admin）实现精细化限流策略
"""

from fastapi import Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Callable
from datetime import datetime, timedelta
import logging

from app.services.cache import get_cache

logger = logging.getLogger(__name__)

# ==================== 限流配置 ====================

RATE_LIMITS = {
    "free": {
        "upload": "5/day",
        "dashboard": "30/hour",
        "diagnosis": "10/hour",
        "compare": "10/hour",
        "insights": "5/hour",      # AI洞察消耗大，免费用户限制
        "report": "3/day",
        "promo_card": "10/day",
        "export": "3/day",
    },
    "pro": {
        "upload": "50/day",
        "dashboard": "120/hour",
        "diagnosis": "60/hour",
        "compare": "60/hour",
        "insights": "30/hour",
        "report": "20/day",
        "promo_card": "50/day",
        "export": "20/day",
    },
    "admin": {
        # 管理员基本不限
        "default": "1000/hour",
        "upload": "1000/day",
        "dashboard": "1000/hour",
        "diagnosis": "1000/hour",
        "compare": "1000/hour",
        "insights": "1000/hour",
        "report": "1000/day",
        "promo_card": "1000/day",
        "export": "1000/day",
    }
}

# 功能中文名称映射
FEATURE_NAMES = {
    "upload": "数据上传",
    "dashboard": "仪表盘",
    "diagnosis": "深度诊断",
    "compare": "数据对比",
    "insights": "AI洞察",
    "report": "报告生成",
    "promo_card": "推广卡片",
    "export": "数据导出",
}

# 功能英文名称映射
FEATURE_NAMES_EN = {
    "upload": "Data Upload",
    "dashboard": "Dashboard",
    "diagnosis": "Deep Diagnosis",
    "compare": "Data Compare",
    "insights": "AI Insights",
    "report": "Report Generation",
    "promo_card": "Promo Card",
    "export": "Data Export",
}


def parse_rate_limit(limit_str: str) -> tuple:
    """
    解析限流字符串，返回(数量, 时间窗口秒数)
    
    支持格式:
    - "5/minute" -> (5, 60)
    - "30/hour" -> (30, 3600)
    - "5/day" -> (5, 86400)
    
    Returns:
        (max_count, window_seconds, window_unit)
    """
    parts = limit_str.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate limit format: {limit_str}")
    
    count = int(parts[0])
    unit = parts[1].strip()
    
    window_seconds = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }.get(unit, 60)
    
    return count, window_seconds, unit


def get_user_tier(user: dict) -> str:
    """
    获取用户等级
    
    优先级:
    1. admin -> "admin"
    2. active subscription -> "pro"
    3. trial -> "pro" (试用期内享受Pro待遇)
    4. 其他 -> "free"
    
    Args:
        user: 用户信息字典，应包含 is_admin, is_subscribed, is_in_trial 等字段
    
    Returns:
        用户等级字符串: "admin", "pro", 或 "free"
    """
    if not user:
        return "free"
    
    # 管理员直接返回
    if user.get("is_admin"):
        return "admin"
    
    # 订阅用户或试用期内用户享受Pro待遇
    if user.get("is_subscribed") or user.get("is_in_trial"):
        return "pro"
    
    # 白名单用户也享受Pro待遇
    if user.get("is_whitelisted"):
        return "pro"
    
    return "free"


def get_tier_display_name(tier: str) -> str:
    """获取用户等级的显示名称"""
    names = {
        "free": "Free",
        "pro": "Pro",
        "admin": "Admin"
    }
    return names.get(tier, tier)


def get_limit_for_tier(tier: str, feature: str) -> Optional[tuple]:
    """
    获取指定用户等级和功能的限流配置
    
    Args:
        tier: 用户等级 (free/pro/admin)
        feature: 功能名称 (upload/dashboard/diagnosis/...)
    
    Returns:
        (max_count, window_seconds) 或 None
    """
    tier_limits = RATE_LIMITS.get(tier, {})
    
    # 优先查找具体功能的限流
    if feature in tier_limits:
        limit_str = tier_limits[feature]
        count, window_seconds, _ = parse_rate_limit(limit_str)
        return count, window_seconds
    
    # 其次查找默认限流
    if "default" in tier_limits:
        limit_str = tier_limits["default"]
        count, window_seconds, _ = parse_rate_limit(limit_str)
        return count, window_seconds
    
    return None


# ==================== 分层限流器类 ====================

class TieredRateLimiter:
    """
    分层限流器
    
    根据用户等级和功能类型实现动态限流
    """
    
    def __init__(self):
        self.cache = None
    
    def _get_cache(self):
        """获取缓存实例"""
        if self.cache is None:
            self.cache = get_cache()
        return self.cache
    
    def _build_cache_key(self, user_id: int, feature: str) -> str:
        """构建限流缓存键"""
        return f"rate_limit:{user_id}:{feature}"
    
    def _parse_window_start(self, window_seconds: int) -> str:
        """
        计算当前时间窗口的开始时间戳
        用于按时间窗口对齐限流计数
        """
        now = datetime.utcnow()
        if window_seconds >= 86400:  # 天级别
            # 按天对齐，00:00 UTC
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif window_seconds >= 3600:  # 小时级别
            # 按小时对齐
            start = now.replace(minute=0, second=0, microsecond=0)
        elif window_seconds >= 60:  # 分钟级别
            # 按分钟对齐
            start = now.replace(second=0, microsecond=0)
        else:
            # 秒级不特殊处理
            start = now
        return start.isoformat()
    
    def check_rate_limit(self, user_id: int, feature: str, tier: str) -> tuple:
        """
        检查限流
        
        Args:
            user_id: 用户ID
            feature: 功能名称
            tier: 用户等级
        
        Returns:
            (allowed: bool, remaining: int, reset_in: int, limit_str: str)
            - allowed: 是否允许请求
            - remaining: 剩余请求次数
            - reset_in: 距离限流重置的秒数
            - limit_str: 限流描述字符串
        """
        limit_config = get_limit_for_tier(tier, feature)
        
        if limit_config is None:
            # 没有限流配置，允许请求
            return True, -1, 0, "unlimited"
        
        max_count, window_seconds = limit_config
        cache = self._get_cache()
        cache_key = self._build_cache_key(user_id, feature)
        window_key = f"{cache_key}:window"
        
        # 获取当前计数和时间窗口
        current_count = cache.get(cache_key) or 0
        window_start = cache.get(window_key) or self._parse_window_start(window_seconds)
        
        # 检查时间窗口是否过期
        window_dt = datetime.fromisoformat(window_start)
        now = datetime.utcnow()
        elapsed = (now - window_dt).total_seconds()
        
        if elapsed >= window_seconds:
            # 时间窗口过期，重置计数
            current_count = 0
            window_start = self._parse_window_start(window_seconds)
        
        # 检查是否超限
        if current_count >= max_count:
            # 计算重置时间
            reset_in = int(window_seconds - elapsed)
            if reset_in < 0:
                reset_in = window_seconds
            return False, 0, reset_in, f"{max_count}/{window_seconds // 60 if window_seconds >= 60 else window_seconds}{'min' if window_seconds >= 60 else 's'}"
        
        return True, max_count - current_count - 1, int(window_seconds - elapsed), f"{max_count}/{window_seconds // 60 if window_seconds >= 60 else window_seconds}{'min' if window_seconds >= 60 else 's'}"
    
    def record_request(self, user_id: int, feature: str, tier: str) -> bool:
        """
        记录一次请求
        
        Args:
            user_id: 用户ID
            feature: 功能名称
            tier: 用户等级
        
        Returns:
            是否成功记录
        """
        limit_config = get_limit_for_tier(tier, feature)
        
        if limit_config is None:
            return True
        
        max_count, window_seconds = limit_config
        cache = self._get_cache()
        cache_key = self._build_cache_key(user_id, feature)
        window_key = f"{cache_key}:window"
        
        # 获取当前计数
        current_count = cache.get(cache_key) or 0
        window_start = cache.get(window_key)
        
        # 检查时间窗口
        if window_start:
            window_dt = datetime.fromisoformat(window_start)
            now = datetime.utcnow()
            elapsed = (now - window_dt).total_seconds()
            
            if elapsed >= window_seconds:
                # 窗口过期，重置
                current_count = 0
                window_start = self._parse_window_start(window_seconds)
        else:
            window_start = self._parse_window_start(window_seconds)
        
        # 增加计数
        new_count = current_count + 1
        cache.set(cache_key, new_count, ttl=window_seconds + 60)  # 多留1分钟缓冲
        cache.set(window_key, window_start, ttl=window_seconds + 60)
        
        return True
    
    def get_user_quotas(self, user_id: int, tier: str) -> Dict:
        """
        获取用户所有功能的配额信息
        
        Returns:
            各功能的配额使用情况字典
        """
        quotas = {}
        cache = self._get_cache()
        
        # 获取该等级所有功能的限流配置
        tier_limits = RATE_LIMITS.get(tier, {})
        
        # 添加默认限流的功能列表
        all_features = set(tier_limits.keys())
        if "default" in tier_limits:
            # 如果有默认限流，添加到所有常见功能
            default_features = ["upload", "dashboard", "diagnosis", "compare", 
                             "insights", "report", "promo_card", "export"]
            for f in default_features:
                if f not in all_features:
                    all_features.add(f)
        
        for feature in all_features:
            limit_config = get_limit_for_tier(tier, feature)
            if limit_config is None:
                continue
            
            max_count, window_seconds = limit_config
            cache_key = self._build_cache_key(user_id, feature)
            window_key = f"{cache_key}:window"
            
            current_count = cache.get(cache_key) or 0
            window_start = cache.get(window_key)
            
            # 检查窗口是否过期
            remaining = max_count - current_count if current_count < max_count else 0
            reset_in = 0
            window_expired = True
            
            if window_start:
                window_dt = datetime.fromisoformat(window_start)
                now = datetime.utcnow()
                elapsed = (now - window_dt).total_seconds()
                
                if elapsed < window_seconds:
                    window_expired = False
                    remaining = max(max_count - current_count, 0)
                    reset_in = int(window_seconds - elapsed)
            
            # 解析限流字符串
            unit = "day" if window_seconds >= 86400 else "hour" if window_seconds >= 3600 else "minute"
            limit_str = f"{max_count}/{unit}"
            
            quotas[feature] = {
                "limit": max_count,
                "limit_str": limit_str,
                "used": current_count,
                "remaining": remaining,
                "reset_in_seconds": reset_in,
                "window_seconds": window_seconds,
                "window_expired": window_expired,
                "feature_name": FEATURE_NAMES.get(feature, feature),
                "feature_name_en": FEATURE_NAMES_EN.get(feature, feature),
            }
        
        return quotas


# 创建全局限流器实例
tiered_limiter = TieredRateLimiter()


# ==================== FastAPI 依赖项 ====================

async def check_tiered_rate_limit(
    feature: str,
    request: Request,
    current_user: dict = None
) -> dict:
    """
    检查分层限流的依赖项
    
    用法:
    @router.post("/insights")
    async def get_insights(
        request: Request,
        user: dict = Depends(lambda r: check_tiered_rate_limit("insights", r))
    ):
    
    或使用依赖链:
    async def insights_limit(request: Request, current_user = Depends(get_current_user)):
        return Depends(check_tiered_rate_limit("insights", request, current_user))
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录才能使用此功能"
        )
    
    user_id = current_user.get("id")
    tier = get_user_tier(current_user)
    
    # 检查限流
    allowed, remaining, reset_in, limit_str = tiered_limiter.check_rate_limit(user_id, feature, tier)
    
    if not allowed:
        # 获取功能名称
        feature_name = FEATURE_NAMES.get(feature, feature)
        tier_display = get_tier_display_name(tier)
        
        # 构建友好消息
        window_unit = "小时" if "hour" in limit_str or "/h" in limit_str else "分钟" if "/m" in limit_str else "天"
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "message": f"您已达到{tier_display}用户的{window_unit}{FEATURE_NAMES.get(feature, feature)}限制",
                "upgrade_url": "/pricing",
                "current_tier": tier,
                "tier_display": tier_display,
                "feature": feature,
                "feature_name": feature_name,
                "limit": limit_str,
                "retry_after": reset_in,
            },
            headers={
                "Retry-After": str(reset_in),
                "X-RateLimit-Limit": limit_str,
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_in),
            }
        )
    
    # 记录请求
    tiered_limiter.record_request(user_id, feature, tier)
    
    # 在响应中添加限流头
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_reset = reset_in
    request.state.rate_limit_limit = limit_str
    
    return current_user


def create_rate_limit_dependency(feature: str):
    """
    创建一个特定功能的限流依赖项
    
    用法:
    insights_limit = create_rate_limit_dependency("insights")
    
    @router.post("/insights")
    async def get_insights(
        request: Request,
        current_user: dict = Depends(insights_limit)
    ):
    """
    async def rate_limit_dependency(
        request: Request,
        current_user: dict = None
    ):
        return await check_tiered_rate_limit(feature, request, current_user)
    
    return rate_limit_dependency


# ==================== 预定义的功能限流依赖项 ====================

# 上传限流
upload_rate_limit = create_rate_limit_dependency("upload")

# 仪表盘限流
dashboard_rate_limit = create_rate_limit_dependency("dashboard")

# 诊断限流
diagnosis_rate_limit = create_rate_limit_dependency("diagnosis")

# 对比限流
compare_rate_limit = create_rate_limit_dependency("compare")

# AI洞察限流
insights_rate_limit = create_rate_limit_dependency("insights")

# 报告限流
report_rate_limit = create_rate_limit_dependency("report")

# 推广卡片限流
promo_card_rate_limit = create_rate_limit_dependency("promo_card")

# 导出限流
export_rate_limit = create_rate_limit_dependency("export")


# ==================== 辅助函数 ====================

def get_user_quota_info(user: dict) -> Dict:
    """
    获取用户配额信息（用于API返回）
    
    Args:
        user: 用户信息字典
    
    Returns:
        包含配额信息的字典
    """
    user_id = user.get("id")
    tier = get_user_tier(user)
    quotas = tiered_limiter.get_user_quotas(user_id, tier)
    
    return {
        "tier": tier,
        "tier_display": get_tier_display_name(tier),
        "is_premium": tier in ("pro", "admin"),
        "quotas": quotas,
    }


__all__ = [
    "RATE_LIMITS",
    "FEATURE_NAMES",
    "get_user_tier",
    "get_tier_display_name",
    "get_limit_for_tier",
    "parse_rate_limit",
    "TieredRateLimiter",
    "tiered_limiter",
    "check_tiered_rate_limit",
    "create_rate_limit_dependency",
    "upload_rate_limit",
    "dashboard_rate_limit",
    "diagnosis_rate_limit",
    "compare_rate_limit",
    "insights_rate_limit",
    "report_rate_limit",
    "promo_card_rate_limit",
    "export_rate_limit",
    "get_user_quota_info",
]
