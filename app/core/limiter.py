"""
速率限制配置
使用 slowapi 实现 API 速率限制
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建速率限制器实例 - 使用客户端IP作为限速key
limiter = Limiter(key_func=get_remote_address)

__all__ = ["limiter"]
