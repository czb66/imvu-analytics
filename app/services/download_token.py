"""
报告下载 Token 服务 - 生成和验证临时下载链接
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# 内存缓存存储 token（生产环境可用 Redis）
# 结构: {token_hash: {"filename": str, "user_id": int, "expires_at": datetime}}
_download_tokens: Dict[str, dict] = {}

# Token 有效期（小时）
TOKEN_EXPIRE_HOURS = 24


def generate_download_token(filename: str, user_id: int) -> str:
    """
    生成临时下载 token
    
    Args:
        filename: 报告文件名
        user_id: 用户 ID
    
    Returns:
        token: 临时下载 token
    """
    # 生成随机 token
    token = secrets.token_urlsafe(32)
    
    # 存储 token hash（安全考虑，不存储明文）
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # 计算过期时间
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    
    # 存储
    _download_tokens[token_hash] = {
        "filename": filename,
        "user_id": user_id,
        "expires_at": expires_at
    }
    
    logger.info(f"生成下载 token: user_id={user_id}, filename={filename}, expires={expires_at}")
    
    return token


def verify_download_token(token: str) -> Optional[Dict]:
    """
    验证下载 token
    
    Args:
        token: 下载 token
    
    Returns:
        验证成功返回 {"filename": str, "user_id": int}，失败返回 None
    """
    if not token:
        return None
    
    # 计算 token hash
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # 查找
    token_data = _download_tokens.get(token_hash)
    
    if not token_data:
        logger.warning(f"Token 不存在: {token[:10]}...")
        return None
    
    # 检查是否过期
    if datetime.utcnow() > token_data["expires_at"]:
        logger.warning(f"Token 已过期: {token[:10]}...")
        # 删除过期 token
        del _download_tokens[token_hash]
        return None
    
    return {
        "filename": token_data["filename"],
        "user_id": token_data["user_id"]
    }


def cleanup_expired_tokens():
    """清理过期的 token"""
    now = datetime.utcnow()
    expired = [k for k, v in _download_tokens.items() if v["expires_at"] < now]
    
    for k in expired:
        del _download_tokens[k]
    
    if expired:
        logger.info(f"清理了 {len(expired)} 个过期下载 token")
