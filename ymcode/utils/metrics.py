#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集器 - 性能和使用指标
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    timestamp: str
    tags: Dict[str, str] = None


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, storage_path: str = None):
        """
        初始化指标收集器
        
        参数:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path) if storage_path else Path.home() / '.ymcode' / 'metrics'
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, float] = {}
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("指标收集器初始化完成")
    
    def increment(self, name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
        """
        增加计数器
        
        参数:
            name: 指标名称
            value: 增加的值
            tags: 标签
        """
        self.counters[name] += value
        logger.debug(f"计数器 {name}: {self.counters[name]}")
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """
        设置仪表值
        
        参数:
            name: 指标名称
            value: 值
            tags: 标签
        """
        self.gauges[name] = value
        logger.debug(f"仪表 {name}: {value}")
    
    def timer(self, name: str) -> 'TimerContext':
        """
        创建计时器上下文
        
        参数:
            name: 指标名称
        
        返回:
            计时器上下文
        """
        return TimerContext(self, name)
    
    def record_timing(self, name: str, duration: float, tags: Dict[str, str] = None) -> None:
        """
        记录计时数据
        
        参数:
            name: 指标名称
            duration: 时长（秒）
            tags: 标签
        """
        point = MetricPoint(
            name=f"{name}.timing",
            value=duration,
            timestamp=datetime.now().isoformat(),
            tags=tags or {}
        )
        self.metrics[name].append(point)
        
        # 保存数据点
        self._save_point(point)
        
        logger.debug(f"计时 {name}: {duration:.3f}s")
    
    def _save_point(self, point: MetricPoint) -> None:
        """保存数据点"""
        try:
            # 按日期保存
            date_str = point.timestamp.split('T')[0]
            file_path = self.storage_path / f"{point.name}_{date_str}.json"
            
            # 读取现有数据
            data = []
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 添加新数据点
            data.append(asdict(point))
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存指标数据失败：{e}")
    
    def get_counter(self, name: str) -> int:
        """获取计数器值"""
        return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """获取仪表值"""
        return self.gauges.get(name, 0.0)
    
    def get_stats(self, name: str) -> Dict[str, Any]:
        """
        获取统计信息
        
        参数:
            name: 指标名称
        
        返回:
            统计信息
        """
        points = self.metrics.get(name, [])
        
        if not points:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'sum': 0
            }
        
        values = [p.value for p in points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有统计信息"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'metrics': {
                name: self.get_stats(name)
                for name in self.metrics.keys()
            }
        }
    
    def reset(self) -> None:
        """重置所有指标"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.timers.clear()
        logger.info("指标已重置")
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        清理旧数据
        
        参数:
            days: 保留天数
        
        返回:
            删除的文件数
        """
        deleted = 0
        cutoff = datetime.now() - timedelta(days=days)
        
        for file_path in self.storage_path.glob('*.json'):
            # 从文件名提取日期
            try:
                date_str = file_path.stem.split('_')[-1]
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff:
                    file_path.unlink()
                    deleted += 1
            except Exception:
                pass
        
        logger.info(f"清理 {deleted} 个旧指标文件（>{days}天）")
        return deleted


class TimerContext:
    """计时器上下文管理器"""
    
    def __init__(self, collector: MetricsCollector, name: str):
        self.collector = collector
        self.name = name
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_timing(self.name, duration)


# 全局指标收集器
_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """获取全局指标收集器实例"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


# 便捷函数
def increment(name: str, value: int = 1) -> None:
    """增加计数器"""
    get_collector().increment(name, value)


def gauge(name: str, value: float) -> None:
    """设置仪表值"""
    get_collector().gauge(name, value)


def timer(name: str) -> TimerContext:
    """创建计时器"""
    return get_collector().timer(name)
