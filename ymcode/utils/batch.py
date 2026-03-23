#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量操作优化

支持：
- 批量处理
- 异步并发
- 结果聚合
- 错误隔离
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable, Awaitable, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import time

from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult:
    """批量操作结果"""
    success_count: int = 0
    failed_count: int = 0
    results: List[Any] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_time: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "total_count": self.success_count + self.failed_count,
            "total_time": self.total_time,
            "errors": self.errors[:10]  # 只返回前 10 个错误
        }


class BatchProcessor:
    """
    批量处理器
    
    特性:
    - 并发执行
    - 错误隔离
    - 结果聚合
    - 进度跟踪
    
    使用示例:
        >>> processor = BatchProcessor(concurrency=10)
        >>> results = await processor.process_batch(items, process_func)
    """
    
    def __init__(
        self,
        concurrency: int = 10,
        timeout: Optional[float] = None,
        retry_count: int = 0
    ):
        """
        初始化批量处理器
        
        参数:
            concurrency: 并发数
            timeout: 单个任务超时（秒）
            retry_count: 重试次数
        """
        self.concurrency = concurrency
        self.timeout = timeout
        self.retry_count = retry_count
        self._semaphore = asyncio.Semaphore(concurrency)
    
    async def process_batch(
        self,
        items: List[T],
        process_func: Callable[[T], Awaitable[R]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """
        批量处理
        
        参数:
            items: 项目列表
            process_func: 处理函数（异步）
            progress_callback: 进度回调 (current, total)
        
        返回:
            BatchResult
        """
        result = BatchResult()
        start_time = time.time()
        
        async def process_with_semaphore(item: T, index: int):
            """带信号量控制的单个处理"""
            async with self._semaphore:
                try:
                    # 执行处理
                    if self.timeout:
                        res = await asyncio.wait_for(
                            process_func(item),
                            timeout=self.timeout
                        )
                    else:
                        res = await process_func(item)
                    
                    result.success_count += 1
                    result.results.append(res)
                    
                except Exception as e:
                    result.failed_count += 1
                    result.errors.append({
                        "index": index,
                        "error": str(e),
                        "type": type(e).__name__
                    })
                    logger.error(f"处理失败 [{index}]: {e}")
                
                finally:
                    # 进度回调
                    current = result.success_count + result.failed_count
                    if progress_callback:
                        progress_callback(current, len(items))
        
        # 创建所有任务
        tasks = [
            process_with_semaphore(item, i)
            for i, item in enumerate(items)
        ]
        
        # 并发执行
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        result.end_time = datetime.now()
        result.total_time = time.time() - start_time
        
        logger.info(
            f"批量处理完成：{result.success_count}成功，"
            f"{result.failed_count}失败，{result.total_time:.2f}秒"
        )
        
        return result
    
    async def process_batch_with_retry(
        self,
        items: List[T],
        process_func: Callable[[T], Awaitable[R]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """批量处理（带重试）"""
        
        async def process_with_retry(item: T):
            """带重试的处理"""
            last_error = None
            
            for attempt in range(self.retry_count + 1):
                try:
                    return await process_func(item)
                except Exception as e:
                    last_error = e
                    if attempt < self.retry_count:
                        # 指数退避
                        wait_time = (attempt + 1) * 0.1
                        await asyncio.sleep(wait_time)
                        logger.warning(f"重试 [{attempt + 1}/{self.retry_count}]: {e}")
            
            # 所有重试失败
            raise last_error
        
        return await self.process_batch(
            items,
            process_with_retry,
            progress_callback
        )


class Cache:
    """
    简单缓存
    
    特性:
    - TTL 过期
    - LRU 淘汰
    - 线程安全
    
    使用示例:
        >>> cache = Cache(max_size=1000, ttl=300)
        >>> cache.set("key", "value")
        >>> value = cache.get("key")
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """
        初始化缓存
        
        参数:
            max_size: 最大缓存数量
            ttl: 默认 TTL（秒）
        """
        self.max_size = max_size
        self.default_ttl = ttl
        self._cache: Dict[str, Dict] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存"""
        async with self._lock:
            if key not in self._cache:
                return default
            
            entry = self._cache[key]
            
            # 检查过期
            if entry['expires'] and datetime.now() > entry['expires']:
                del self._cache[key]
                self._access_order.remove(key)
                return default
            
            # 更新访问顺序
            self._access_order.remove(key)
            self._access_order.append(key)
            
            return entry['value']
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """设置缓存"""
        async with self._lock:
            # 如果已存在，先移除
            if key in self._cache:
                self._access_order.remove(key)
            
            # 检查大小限制
            while len(self._cache) >= self.max_size:
                # 淘汰最久未使用的
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
            
            # 添加新条目
            expires = None
            if ttl is not None:
                from datetime import timedelta
                expires = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl > 0:
                from datetime import timedelta
                expires = datetime.now() + timedelta(seconds=self.default_ttl)
            
            self._cache[key] = {
                'value': value,
                'expires': expires,
                'created_at': datetime.now()
            }
            self._access_order.append(key)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.remove(key)
                return True
            return False
    
    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def get_stats(self) -> Dict:
        """获取缓存统计"""
        async with self._lock:
            now = datetime.now()
            expired = sum(
                1 for entry in self._cache.values()
                if entry['expires'] and now > entry['expires']
            )
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "expired_count": expired,
                "default_ttl": self.default_ttl
            }


# 便捷函数

async def batch_process(
    items: List[T],
    process_func: Callable[[T], Awaitable[R]],
    concurrency: int = 10,
    timeout: Optional[float] = None
) -> BatchResult:
    """便捷函数：批量处理"""
    processor = BatchProcessor(concurrency=concurrency, timeout=timeout)
    return await processor.process_batch(items, process_func)


async def batch_map(
    items: List[T],
    map_func: Callable[[T], Awaitable[R]],
    concurrency: int = 10
) -> List[R]:
    """便捷函数：批量映射"""
    processor = BatchProcessor(concurrency=concurrency)
    result = await processor.process_batch(items, map_func)
    return result.results


# 使用示例
if __name__ == "__main__":
    async def test():
        # 测试批量处理
        processor = BatchProcessor(concurrency=5)
        
        async def process_item(item):
            await asyncio.sleep(0.1)
            return item * 2
        
        items = list(range(20))
        result = await processor.process_batch(items, process_item)
        
        print(f"结果：{result.to_dict()}")
        
        # 测试缓存
        cache = Cache(max_size=100, ttl=60)
        
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        print(f"缓存值：{value}")
        
        stats = await cache.get_stats()
        print(f"缓存统计：{stats}")
    
    asyncio.run(test())
