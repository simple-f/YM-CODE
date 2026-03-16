#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化工具

提供缓存、异步处理、并发优化等功能
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from functools import wraps
import hashlib
import json
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class Cache(Generic[T]):
    """通用缓存类"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化缓存
        
        参数:
            max_size: 最大缓存条目数
            ttl: 默认生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                # 过期删除
                del self._cache[key]
        return None
    
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        # 检查大小限制
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        expires = time.time() + (ttl or self.ttl)
        self._cache[key] = {
            'value': value,
            'expires': expires,
            'created': time.time()
        }
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def _evict_oldest(self) -> None:
        """淘汰最旧的缓存"""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['created'])
        del self._cache[oldest_key]
    
    def stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        now = time.time()
        valid = sum(1 for e in self._cache.values() if now < e['expires'])
        expired = len(self._cache) - valid
        
        return {
            'total': len(self._cache),
            'valid': valid,
            'expired': expired,
            'max_size': self.max_size
        }


# 全局缓存实例
_default_cache: Optional[Cache] = None

def get_cache(max_size: int = 1000, ttl: int = 3600) -> Cache:
    """获取全局缓存实例"""
    global _default_cache
    if _default_cache is None:
        _default_cache = Cache(max_size, ttl)
    return _default_cache


def cached(ttl: int = 3600, cache: Optional[Cache] = None):
    """
    缓存装饰器
    
    参数:
        ttl: 缓存生存时间（秒）
        cache: 缓存实例（默认使用全局缓存）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_instance = cache or get_cache()
            
            # 生成缓存键
            key = cache_instance._generate_key(func.__name__, *args, **kwargs)
            
            # 尝试获取缓存
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                logger.debug(f"缓存命中：{func.__name__}")
                return cached_result
            
            # 执行函数
            logger.debug(f"缓存未命中：{func.__name__}")
            result = await func(*args, **kwargs)
            
            # 设置缓存
            cache_instance.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class AsyncBatchProcessor:
    """异步批量处理器"""
    
    def __init__(self, batch_size: int = 10, max_concurrency: int = 5):
        """
        初始化批量处理器
        
        参数:
            batch_size: 批量大小
            max_concurrency: 最大并发数
        """
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process(self, items: list, processor: Callable) -> list:
        """
        批量处理项目
        
        参数:
            items: 项目列表
            processor: 处理函数（异步）
        
        返回:
            处理结果列表
        """
        async def process_with_semaphore(item):
            async with self._semaphore:
                return await processor(item)
        
        # 创建任务
        tasks = [process_with_semaphore(item) for item in items]
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"处理项目 {i} 失败：{result}")
                processed_results.append({'error': str(result)})
            else:
                processed_results.append(result)
        
        return processed_results


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._metrics: Dict[str, list] = {}
    
    def record(self, name: str, value: float) -> None:
        """记录指标"""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)
    
    def stats(self, name: str) -> Dict[str, float]:
        """获取指标统计"""
        if name not in self._metrics:
            return {}
        
        values = self._metrics[name]
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'sum': sum(values)
        }
    
    def reset(self, name: Optional[str] = None) -> None:
        """重置指标"""
        if name:
            self._metrics[name] = []
        else:
            self._metrics.clear()


# 全局性能监控器
_perf_monitor = PerformanceMonitor()

def get_perf_monitor() -> PerformanceMonitor:
    """获取全局性能监控器"""
    return _perf_monitor


def timed(name: Optional[str] = None):
    """
    性能监控装饰器
    
    参数:
        name: 指标名称（默认使用函数名）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metric_name = name or func.__name__
            start = time.time()
            
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                _perf_monitor.record(metric_name, elapsed)
                logger.debug(f"{metric_name} 执行时间：{elapsed:.3f}秒")
        
        return wrapper
    return decorator


# 便捷函数
async def async_map(items: list, func: Callable, max_concurrency: int = 5) -> list:
    """异步映射（带并发控制）"""
    processor = AsyncBatchProcessor(max_concurrency=max_concurrency)
    return await processor.process(items, func)


def cache_clear() -> None:
    """清空缓存"""
    get_cache().clear()


def cache_stats() -> Dict[str, int]:
    """获取缓存统计"""
    return get_cache().stats()
