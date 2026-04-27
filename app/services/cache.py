"""
内存缓存服务 - 支持TTL和LRU淘汰
用于减少重复的数据库查询和计算，提升API响应速度
"""

from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib
import json
import threading
import logging
import fnmatch
import sys

logger = logging.getLogger(__name__)


class CacheService:
    """内存缓存服务 - 支持TTL和LRU淘汰"""
    
    def __init__(self, max_size: int = 500, default_ttl: int = 300):
        """
        初始化缓存服务
        
        Args:
            max_size: 最大缓存条目数，超过后触发LRU淘汰
            default_ttl: 默认过期时间（秒）
        """
        self._cache = {}  # {key: {"value": ..., "expires_at": datetime}}
        self._access_order = []  # LRU追踪，recently used at end
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "cleanups": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回None
        """
        with self._lock:
            # 清理过期条目
            self._cleanup_expired()
            
            if key not in self._cache:
                self._stats["misses"] += 1
                logger.debug(f"[Cache MISS] {key}")
                return None
            
            entry = self._cache[key]
            
            # 检查是否过期
            if entry["expires_at"] < datetime.now():
                del self._cache[key]
                self._access_order.remove(key)
                self._stats["misses"] += 1
                logger.debug(f"[Cache EXPIRED] {key}")
                return None
            
            # 更新LRU顺序（移到末尾表示最近使用）
            self._access_order.remove(key)
            self._access_order.append(key)
            
            self._stats["hits"] += 1
            logger.debug(f"[Cache HIT] {key}")
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认使用default_ttl
        """
        if ttl is None:
            ttl = self._default_ttl
        
        with self._lock:
            # 如果key已存在，先从LRU列表移除
            if key in self._access_order:
                self._access_order.remove(key)
            
            # 检查是否需要LRU淘汰
            while len(self._cache) >= self._max_size and self._access_order:
                self._evict_lru()
            
            # 设置缓存
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.now()
            }
            self._access_order.append(key)
            
            logger.debug(f"[Cache SET] {key} (TTL={ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        删除指定缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                logger.debug(f"[Cache DELETE] {key}")
                return True
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的缓存
        
        Args:
            pattern: 通配符模式，如 "user_123_*"
            
        Returns:
            删除的缓存数量
        """
        with self._lock:
            # 获取所有匹配的键
            keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
            
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            
            if keys_to_delete:
                logger.info(f"[Cache DELETE PATTERN] {pattern} - 删除了 {len(keys_to_delete)} 条缓存")
            
            return len(keys_to_delete)
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            logger.info(f"[Cache CLEAR] 清空了 {count} 条缓存")
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            包含命中率、大小等信息的字典
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            # 计算内存估算（简单估算）
            try:
                cache_size = sys.getsizeof(json.dumps(self._cache, default=str))
            except:
                cache_size = 0
            
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "total_requests": total_requests,
                "hit_rate": round(hit_rate, 2),
                "size": len(self._cache),
                "max_size": self._max_size,
                "evictions": self._stats["evictions"],
                "cleanups": self._stats["cleanups"],
                "memory_estimate_bytes": cache_size
            }
    
    def _evict_lru(self):
        """LRU淘汰 - 移除最久未使用的条目"""
        if not self._access_order:
            return
        
        # 移除最久未使用的（列表第一个）
        lru_key = self._access_order.pop(0)
        if lru_key in self._cache:
            del self._cache[lru_key]
            self._stats["evictions"] += 1
            logger.debug(f"[Cache EVICT LRU] {lru_key}")
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        now = datetime.now()
        keys_to_delete = []
        
        for key, entry in self._cache.items():
            if entry["expires_at"] < now:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
        
        if keys_to_delete:
            self._stats["cleanups"] += len(keys_to_delete)
            logger.debug(f"[Cache CLEANUP] 清理了 {len(keys_to_delete)} 条过期缓存")


def generate_cache_key(*args, **kwargs) -> str:
    """
    生成缓存键的辅助函数
    
    Args:
        *args: 可变位置参数
        **kwargs: 关键字参数
        
    Returns:
        MD5哈希后的缓存键
    """
    # 组合所有参数
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    raw_key = ":".join(key_parts)
    
    # 如果键长度合理，直接返回
    if len(raw_key) <= 100:
        return raw_key
    
    # 键太长则哈希
    return hashlib.md5(raw_key.encode()).hexdigest()


# 全局缓存实例（延迟初始化）
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """获取全局缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService(max_size=500, default_ttl=300)
    return _cache_instance


def init_cache(max_size: int = 500, default_ttl: int = 300) -> CacheService:
    """初始化全局缓存实例"""
    global _cache_instance
    _cache_instance = CacheService(max_size=max_size, default_ttl=default_ttl)
    logger.info(f"缓存服务已初始化 (max_size={max_size}, default_ttl={default_ttl}s)")
    return _cache_instance
