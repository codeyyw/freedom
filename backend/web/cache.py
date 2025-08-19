import time
import hashlib
import json
from typing import Any, Optional, Dict
from functools import wraps
from flask import request, jsonify
from config import config
from validators import ResponseFormatter
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._cache.items():
            if current_time > data['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        self._cleanup_expired()
        
        if key in self._cache:
            current_time = time.time()
            if current_time <= self._cache[key]['expires_at']:
                self._access_times[key] = current_time
                return self._cache[key]['value']
            else:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = config.CACHE_TTL
        
        current_time = time.time()
        self._cache[key] = {
            'value': value,
            'expires_at': current_time + ttl,
            'created_at': current_time
        }
        self._access_times[key] = current_time
        
        # 如果缓存过多，清理最久未访问的
        if len(self._cache) > 1000:
            self._cleanup_lru()
    
    def _cleanup_lru(self):
        """清理最久未使用的缓存"""
        # 保留最近访问的800个缓存项
        sorted_keys = sorted(self._access_times.items(), key=lambda x: x[1], reverse=True)
        keys_to_keep = [key for key, _ in sorted_keys[:800]]
        
        new_cache = {key: self._cache[key] for key in keys_to_keep if key in self._cache}
        new_access_times = {key: self._access_times[key] for key in keys_to_keep}
        
        self._cache = new_cache
        self._access_times = new_access_times
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._access_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        self._cleanup_expired()
        return {
            'total_keys': len(self._cache),
            'memory_usage_estimate': sum(len(str(v)) for v in self._cache.values()),
            'oldest_entry': min(self._access_times.values()) if self._access_times else None,
            'newest_entry': max(self._access_times.values()) if self._access_times else None
        }

# 全局缓存实例
cache = MemoryCache()

class RateLimiter:
    """限流器实现"""
    
    def __init__(self):
        self._requests: Dict[str, list] = {}
    
    def _cleanup_old_requests(self, client_id: str, window_seconds: int):
        """清理过期的请求记录"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        if client_id in self._requests:
            self._requests[client_id] = [
                req_time for req_time in self._requests[client_id]
                if req_time > cutoff_time
            ]
    
    def is_allowed(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """检查是否允许请求"""
        current_time = time.time()
        
        # 清理过期请求
        self._cleanup_old_requests(client_id, window_seconds)
        
        # 检查请求数量
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        if len(self._requests[client_id]) >= max_requests:
            return False
        
        # 记录当前请求
        self._requests[client_id].append(current_time)
        return True
    
    def get_remaining_requests(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> int:
        """获取剩余请求次数"""
        self._cleanup_old_requests(client_id, window_seconds)
        
        if client_id not in self._requests:
            return max_requests
        
        return max(0, max_requests - len(self._requests[client_id]))
    
    def reset_client(self, client_id: str):
        """重置客户端限流记录"""
        if client_id in self._requests:
            del self._requests[client_id]

# 全局限流器实例
rate_limiter = RateLimiter()

def generate_cache_key(prefix: str, params: dict) -> str:
    """生成缓存键"""
    # 对参数进行排序和序列化，确保相同参数生成相同的键
    sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
    param_hash = hashlib.md5(sorted_params.encode('utf-8')).hexdigest()[:16]
    return f"{prefix}:{param_hash}"

def cached(ttl: int = None, key_prefix: str = "api"):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                dict(request.args)
            )
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 只缓存成功的响应
            if hasattr(result, 'status_code') and result.status_code == 200:
                cache.set(cache_key, result, ttl)
                logger.debug(f"缓存设置: {cache_key}")
            
            return result
        return wrapper
    return decorator

def rate_limited(max_requests: int = 100, window_seconds: int = 60):
    """限流装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取客户端标识（IP地址）
            client_id = request.remote_addr or 'unknown'
            
            # 检查是否超过限流
            if not rate_limiter.is_allowed(client_id, max_requests, window_seconds):
                remaining = rate_limiter.get_remaining_requests(client_id, max_requests, window_seconds)
                logger.warning(f"客户端 {client_id} 触发限流")
                
                return jsonify(ResponseFormatter.error(
                    message=f"请求过于频繁，请稍后再试。窗口期内最多允许 {max_requests} 次请求",
                    code=429
                )), 429
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_stats():
    """获取缓存统计信息"""
    return cache.stats()

def clear_cache():
    """清空缓存"""
    cache.clear()
    logger.info("缓存已清空")