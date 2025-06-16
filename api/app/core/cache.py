"""
Redis缓存实现
"""
import json
import logging
import hashlib
from typing import Any, Optional
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器 - 支持Redis和内存缓存回退"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis连接"""
        if settings.REDIS_URL:
            try:
                self.redis_client = Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # 测试连接
                self.redis_client.ping()
                logger.info("Redis连接成功")
            except (ConnectionError, RedisError) as e:
                logger.warning(f"Redis连接失败，将使用内存缓存: {e}")
                self.redis_client = None
        else:
            logger.info("未配置Redis，使用内存缓存")
    
    def _get_cache_key(self, endpoint: str, params: dict) -> str:
        """生成缓存键"""
        cache_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return f"hqxx:cache:{hashlib.md5(cache_data.encode()).hexdigest()}"
    
    def get(self, endpoint: str, params: dict = None) -> Optional[Any]:
        """获取缓存数据"""
        if params is None:
            params = {}
        
        cache_key = self._get_cache_key(endpoint, params)
        
        # 尝试从Redis获取
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except (ConnectionError, RedisError, json.JSONDecodeError) as e:
                logger.warning(f"Redis获取缓存失败: {e}")
        
        # 回退到内存缓存
        return self._get_from_memory(cache_key)
    
    def set(self, endpoint: str, params: dict, data: Any, ttl_seconds: int = 300):
        """设置缓存数据"""
        if params is None:
            params = {}
        
        cache_key = self._get_cache_key(endpoint, params)
        
        # 尝试设置到Redis
        if self.redis_client:
            try:
                serialized_data = json.dumps(data, ensure_ascii=False, default=str)
                self.redis_client.setex(cache_key, ttl_seconds, serialized_data)
                logger.debug(f"Redis缓存设置成功: {cache_key}")
                return
            except (ConnectionError, RedisError, TypeError) as e:
                logger.warning(f"Redis设置缓存失败: {e}")
        
        # 回退到内存缓存
        self._set_to_memory(cache_key, data, ttl_seconds)
    
    def delete(self, endpoint: str, params: dict = None):
        """删除缓存"""
        if params is None:
            params = {}
        
        cache_key = self._get_cache_key(endpoint, params)
        
        # 从Redis删除
        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
            except (ConnectionError, RedisError) as e:
                logger.warning(f"Redis删除缓存失败: {e}")
        
        # 从内存缓存删除
        self._delete_from_memory(cache_key)
    
    def delete_pattern(self, pattern: str):
        """删除匹配模式的缓存"""
        # Redis模式删除
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"hqxx:cache:*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Redis删除了 {len(keys)} 个匹配的缓存项")
            except (ConnectionError, RedisError) as e:
                logger.warning(f"Redis模式删除失败: {e}")
        
        # 内存缓存模式删除
        keys_to_delete = [key for key in self.memory_cache.keys() if pattern in key]
        for key in keys_to_delete:
            self._delete_from_memory(key)
        
        if keys_to_delete:
            logger.info(f"内存缓存删除了 {len(keys_to_delete)} 个匹配的缓存项")
    
    def clear_all(self):
        """清空所有缓存"""
        # 清空Redis缓存
        if self.redis_client:
            try:
                keys = self.redis_client.keys("hqxx:cache:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Redis清空了 {len(keys)} 个缓存项")
            except (ConnectionError, RedisError) as e:
                logger.warning(f"Redis清空缓存失败: {e}")
        
        # 清空内存缓存
        self.memory_cache.clear()
        self.memory_cache_ttl.clear()
        logger.info("内存缓存已清空")
    
    def _get_from_memory(self, cache_key: str) -> Optional[Any]:
        """从内存缓存获取数据"""
        import time
        
        if cache_key in self.memory_cache:
            if cache_key in self.memory_cache_ttl and time.time() < self.memory_cache_ttl[cache_key]:
                return self.memory_cache[cache_key]
            else:
                # 缓存过期，清理
                self._delete_from_memory(cache_key)
        
        return None
    
    def _set_to_memory(self, cache_key: str, data: Any, ttl_seconds: int):
        """设置内存缓存"""
        import time
        
        self.memory_cache[cache_key] = data
        self.memory_cache_ttl[cache_key] = time.time() + ttl_seconds
        logger.debug(f"内存缓存设置成功: {cache_key}")
    
    def _delete_from_memory(self, cache_key: str):
        """从内存缓存删除"""
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        if cache_key in self.memory_cache_ttl:
            del self.memory_cache_ttl[cache_key]
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        stats = {
            "redis_connected": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache)
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_used_memory": info.get("used_memory_human", "N/A"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_total_commands_processed": info.get("total_commands_processed", 0)
                })
            except (ConnectionError, RedisError) as e:
                logger.warning(f"获取Redis统计信息失败: {e}")
                stats["redis_error"] = str(e)
        
        return stats
    
    def health_check(self) -> dict:
        """健康检查"""
        health = {
            "cache_status": "healthy",
            "redis_status": "disconnected",
            "memory_cache_status": "active"
        }
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                health["redis_status"] = "connected"
            except (ConnectionError, RedisError) as e:
                health["redis_status"] = f"error: {e}"
                health["cache_status"] = "degraded"
        
        return health


# 创建全局缓存实例
cache_manager = CacheManager()


# 便捷函数
def get_cache_key(endpoint: str, params: dict) -> str:
    """生成缓存键 - 兼容现有代码"""
    return cache_manager._get_cache_key(endpoint, params)


def get_from_cache(cache_key: str):
    """从缓存获取数据 - 兼容现有代码"""
    # 解析缓存键获取endpoint和params
    # 这里简化处理，直接使用内存缓存的逻辑
    return cache_manager._get_from_memory(cache_key)


def set_cache(cache_key: str, data: Any, ttl_seconds: int = 300):
    """设置缓存数据 - 兼容现有代码"""
    # 这里简化处理，直接使用内存缓存的逻辑
    cache_manager._set_to_memory(cache_key, data, ttl_seconds)
