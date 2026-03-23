#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集器

收集系统、Agent 和任务的统计指标
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MetricPoint":
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MetricsCollector:
    """
    指标收集器
    
    功能:
    - 收集系统指标
    - 收集 Agent 指标
    - 收集任务指标
    - 时间窗口聚合
    - 指标查询
    
    使用示例:
        >>> collector = MetricsCollector()
        >>> collector.record("agent.tasks_completed", 1, {"agent_id": "ai2"})
        >>> metrics = collector.get_metrics("agent.*", hours=1)
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        retention_hours: int = 24,
        aggregation_interval: int = 60
    ):
        """
        初始化指标收集器
        
        参数:
            storage_path: 持久化路径
            retention_hours: 数据保留时间（小时）
            aggregation_interval: 聚合间隔（秒）
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.retention_hours = retention_hours
        self.aggregation_interval = aggregation_interval
        
        # 指标存储：metric_name -> List[MetricPoint]
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        
        # 聚合缓存
        self._aggregated: Dict[str, Dict] = {}
        self._last_aggregation: Optional[datetime] = None
        
        # 实时指标（最新值）
        self._gauges: Dict[str, float] = {}
        
        # 计数器（累加值）
        self._counters: Dict[str, float] = {}
        
        # 直方图（分布统计）
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 加载持久化数据
        if self.storage_path:
            self._load()
        
        logger.info(f"MetricsCollector 初始化完成 (retention={retention_hours}h)")
    
    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        记录指标
        
        参数:
            name: 指标名称（如 "agent.tasks_completed"）
            value: 指标值
            labels: 标签（如 {"agent_id": "ai2"}）
            timestamp: 时间戳（默认当前时间）
        """
        with self._lock:
            point = MetricPoint(
                name=name,
                value=value,
                timestamp=timestamp or datetime.now(),
                labels=labels or {}
            )
            
            self._metrics[name].append(point)
            
            # 更新实时指标
            self._gauges[name] = value
            
            # 更新计数器
            if name not in self._counters:
                self._counters[name] = 0
            self._counters[name] += value
            
            logger.debug(f"记录指标：{name}={value}")
    
    def increment(self, name: str, labels: Optional[Dict[str, str]] = None, amount: float = 1):
        """
        增加计数器
        
        参数:
            name: 指标名称
            labels: 标签
            amount: 增加量
        """
        self.record(name, amount, labels)
    
    def histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        记录直方图数据
        
        参数:
            name: 指标名称
            value: 值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            
            # 限制直方图大小
            if len(self._histograms[key]) > 10000:
                self._histograms[key] = self._histograms[key][-5000:]
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        设置 gauge 指标（实时值）
        
        参数:
            name: 指标名称
            value: 值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            self.record(name, value, labels)
    
    def timing(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """
        记录耗时
        
        参数:
            name: 指标名称
            duration: 耗时（秒）
            labels: 标签
        """
        self.record(name, duration, labels)
        self.histogram(f"{name}.distribution", duration, labels)
    
    def get_metrics(
        self,
        name_pattern: str = "*",
        hours: int = 1,
        labels: Optional[Dict[str, str]] = None
    ) -> List[MetricPoint]:
        """
        获取指标
        
        参数:
            name_pattern: 指标名称模式（支持 * 通配符）
            hours: 时间范围（小时）
            labels: 标签过滤
        
        返回:
            指标列表
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            results = []
            
            for name, points in self._metrics.items():
                # 名称匹配
                if not self._match_pattern(name, name_pattern):
                    continue
                
                # 过滤时间和标签
                for point in points:
                    if point.timestamp < cutoff:
                        continue
                    
                    if labels and not self._match_labels(point.labels, labels):
                        continue
                    
                    results.append(point)
            
            # 按时间排序
            results.sort(key=lambda p: p.timestamp)
            return results
    
    def get_latest(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """
        获取最新值
        
        参数:
            name: 指标名称
            labels: 标签
        
        返回:
            最新值
        """
        with self._lock:
            key = self._make_key(name, labels)
            return self._gauges.get(key)
    
    def get_counter(self, name: str) -> float:
        """
        获取计数器值
        
        参数:
            name: 指标名称
        
        返回:
            计数器值
        """
        with self._lock:
            return self._counters.get(name, 0)
    
    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        获取直方图统计
        
        参数:
            name: 指标名称
            labels: 标签
        
        返回:
            统计信息（count, sum, avg, min, max, p50, p90, p99）
        """
        with self._lock:
            key = self._make_key(name, labels)
            values = self._histograms.get(key, [])
            
            if not values:
                return {
                    "count": 0,
                    "sum": 0,
                    "avg": 0,
                    "min": 0,
                    "max": 0,
                    "p50": 0,
                    "p90": 0,
                    "p99": 0
                }
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            return {
                "count": count,
                "sum": sum(sorted_values),
                "avg": sum(sorted_values) / count,
                "min": sorted_values[0],
                "max": sorted_values[-1],
                "p50": sorted_values[int(count * 0.5)],
                "p90": sorted_values[int(count * 0.9)],
                "p99": sorted_values[min(int(count * 0.99), count - 1)]
            }
    
    def get_agent_metrics(self, agent_id: str) -> Dict:
        """
        获取 Agent 指标
        
        参数:
            agent_id: Agent ID
        
        返回:
            指标字典
        """
        with self._lock:
            return {
                "tasks_completed": self.get_counter(f"agent.tasks_completed:{agent_id}"),
                "tasks_failed": self.get_counter(f"agent.tasks_failed:{agent_id}"),
                "avg_execution_time": self.get_histogram_stats(
                    f"agent.execution_time",
                    {"agent_id": agent_id}
                ),
                "status": self.get_latest(f"agent.status:{agent_id}")
            }
    
    def get_system_metrics(self) -> Dict:
        """
        获取系统指标
        
        返回:
            指标字典
        """
        with self._lock:
            return {
                "total_tasks": self.get_counter("system.total_tasks"),
                "completed_tasks": self.get_counter("system.completed_tasks"),
                "failed_tasks": self.get_counter("system.failed_tasks"),
                "active_agents": self.get_latest("system.active_agents") or 0,
                "queue_size": self.get_latest("system.queue_size") or 0,
                "avg_response_time": self.get_histogram_stats("system.response_time")
            }
    
    def get_dashboard(self) -> Dict:
        """
        获取 Dashboard 数据
        
        返回:
            Dashboard 数据
        """
        with self._lock:
            now = datetime.now()
            
            # 最近 1 小时的数据
            recent_points = self.get_metrics("*", hours=1)
            
            # 按分钟聚合
            minute_buckets = defaultdict(list)
            for point in recent_points:
                minute_key = point.timestamp.replace(second=0, microsecond=0)
                minute_buckets[minute_key].append(point)
            
            # 计算每分钟的任务完成率
            success_rate_timeline = []
            for minute, points in sorted(minute_buckets.items()):
                total = sum(1 for p in points if "tasks_completed" in p.name or "tasks_failed" in p.name)
                success = sum(1 for p in points if "tasks_completed" in p.name)
                rate = (success / total * 100) if total > 0 else 100
                success_rate_timeline.append({
                    "time": minute.isoformat(),
                    "rate": rate
                })
            
            return {
                "system": self.get_system_metrics(),
                "success_rate_timeline": success_rate_timeline[-60:],  # 最近 60 分钟
                "updated_at": now.isoformat()
            }
    
    def clear_old_data(self, older_than_hours: Optional[int] = None):
        """
        清理旧数据
        
        参数:
            older_than_hours: 清理早于此时间的数据（默认使用 retention_hours）
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=older_than_hours or self.retention_hours)
            
            total_removed = 0
            
            for name in list(self._metrics.keys()):
                old_points = [p for p in self._metrics[name] if p.timestamp < cutoff]
                new_points = [p for p in self._metrics[name] if p.timestamp >= cutoff]
                
                if len(new_points) < len(self._metrics[name]):
                    self._metrics[name] = new_points
                    total_removed += len(old_points)
                    
                    # 如果为空，删除该指标
                    if not new_points:
                        del self._metrics[name]
            
            logger.info(f"清理旧指标数据：{total_removed} 个点")
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """生成带标签的键"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _match_pattern(self, name: str, pattern: str) -> bool:
        """简单通配符匹配"""
        if pattern == "*":
            return True
        
        if "*" in pattern:
            prefix = pattern.split("*")[0]
            return name.startswith(prefix)
        
        return name == pattern
    
    def _match_labels(self, point_labels: Dict[str, str], filter_labels: Dict[str, str]) -> bool:
        """标签匹配"""
        for key, value in filter_labels.items():
            if point_labels.get(key) != value:
                return False
        return True
    
    def _save(self):
        """持久化数据"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "metrics": {
                    name: [p.to_dict() for p in points]
                    for name, points in self._metrics.items()
                },
                "counters": self._counters,
                "gauges": self._gauges,
                "saved_at": datetime.now().isoformat()
            }
            
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"指标数据已保存：{self.storage_path}")
            
        except Exception as e:
            logger.error(f"保存指标数据失败：{e}")
    
    def _load(self):
        """加载持久化数据"""
        if not self.storage_path or not self.storage_path.exists():
            logger.info("无持久化数据，使用空收集器")
            return
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 加载指标
            self._metrics = defaultdict(list)
            for name, points in data.get("metrics", {}).items():
                for point_data in points:
                    point = MetricPoint.from_dict(point_data)
                    self._metrics[name].append(point)
            
            # 加载计数器和 gauge
            self._counters = data.get("counters", {})
            self._gauges = data.get("gauges", {})
            
            logger.info(f"已加载 {sum(len(p) for p in self._metrics.values())} 个指标点")
            
        except Exception as e:
            logger.error(f"加载指标数据失败：{e}")
            self._metrics = defaultdict(list)
            self._counters = {}
            self._gauges = {}
