"""
缓存装饰器 - 用于API路由的响应缓存
"""

from functools import wraps
from typing import Callable, Optional
import hashlib
import json
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.cache import get_cache, generate_cache_key

logger = logging.getLogger(__name__)


def cache_response(ttl: int = 300, key_prefix: str = "api", vary_by_user: bool = True, vary_by_params: bool = True):
    """
    缓存API响应的装饰器
    
    Args:
        ttl: 缓存时间（秒），默认5分钟
        key_prefix: 缓存键前缀
        vary_by_user: 是否按用户区分缓存（通过current_user参数）
        vary_by_params: 是否按请求参数区分缓存
        
    Usage:
        @router.get("/summary")
        @cache_response(ttl=300, key_prefix="dashboard_summary")
        async def get_summary(current_user: dict = Depends(require_subscription)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # 构建缓存键
            cache_key_parts = [key_prefix]
            
            # 如果需要按用户区分，从kwargs中获取user_id
            if vary_by_user:
                current_user = kwargs.get('current_user')
                if current_user and isinstance(current_user, dict):
                    user_id = current_user.get('id')
                    if user_id:
                        cache_key_parts.append(f"user_{user_id}")
            
            # 如果需要按参数区分，从kwargs中获取查询参数
            if vary_by_params:
                request = kwargs.get('request')
                if request and isinstance(request, Request):
                    # 从query_params获取查询参数
                    params = dict(request.query_params)
                    # 移除常见的非业务参数
                    params.pop('request_id', None)
                    if params:
                        param_key = generate_cache_key(**params)
                        cache_key_parts.append(f"params_{param_key}")
            
            cache_key = ":".join(cache_key_parts)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"[Cache Decorator HIT] {cache_key}")
                # 返回缓存结果，添加X-Cache头
                response_data = cached_value.copy() if isinstance(cached_value, dict) else cached_value
                if isinstance(response_data, dict) and 'headers' not in response_data:
                    response_data['_cached'] = True
                return response_data
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
                logger.debug(f"[Cache Decorator SET] {cache_key} (TTL={ttl}s)")
            
            return result
        
        return wrapper
    return decorator


class CacheMiddleware(BaseHTTPMiddleware):
    """
    缓存中间件 - 为响应添加X-Cache头
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 获取缓存状态（如果已处理）
        cache = get_cache()
        # 这里可以添加更多中间件逻辑
        
        response.headers["X-Cache-Enabled"] = "true"
        return response


def add_cache_headers(response: Response, cache_hit: bool):
    """
    为响应添加缓存状态头
    
    Args:
        response: FastAPI响应对象
        cache_hit: 是否命中缓存
    """
    response.headers["X-Cache"] = "HIT" if cache_hit else "MISS"


def clear_user_cache(user_id: int):
    """
    清除指定用户的所有缓存
    
    Args:
        user_id: 用户ID
    """
    cache = get_cache()
    count = cache.delete_pattern(f"*:user_{user_id}:*")
    logger.info(f"[Cache] 已清除用户 {user_id} 的 {count} 条缓存")


def clear_pattern_cache(pattern: str):
    """
    清除匹配模式的缓存
    
    Args:
        pattern: 缓存键模式，如 "dashboard*" 或 "*user_123*"
    """
    cache = get_cache()
    count = cache.delete_pattern(pattern)
    logger.info(f"[Cache] 模式 '{pattern}' 匹配删除了 {count} 条缓存")
