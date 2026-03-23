#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果收集器

统一收集、存储和查询 Agent 执行结果
支持 WebSocket 推送
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Set
from collections import defaultdict
from dataclasses import dataclass, field
import threading
import queue

from ..queue.task import Task, TaskResult, TaskStatus
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(eq=False)
class Subscription:
    """订阅者信息"""
    callback: Callable[[TaskResult], None]
    created_at: datetime = field(default_factory=datetime.now)


class ResultCollector:
    """
    结果收集器
    
    功能:
    - 存储任务结果
    - 查询结果
    - 聚合多 Agent 结果
    - WebSocket 推送（订阅模式）
    
    使用示例:
        >>> collector = ResultCollector()
        >>> result = TaskResult(task_id="123", agent_id="ai2", success=True, result={"data": "ok"})
        >>> collector.store(result)
        >>> retrieved = collector.get("123")
    """
    
    def __init__(self, storage_path: Optional[str] = None, max_results: int = 10000):
        """
        初始化结果收集器
        
        参数:
            storage_path: 持久化路径（可选）
            max_results: 最大存储结果数（超过后自动清理旧结果）
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_results = max_results
        
        # 结果存储：task_id -> List[TaskResult]
        # 一个任务可能有多个结果（多 Agent 协作、重试等）
        self._results: Dict[str, List[TaskResult]] = defaultdict(list)
        
        # 订阅者：task_id -> Set[Subscription]
        self._subscribers: Dict[str, Set[Subscription]] = defaultdict(set)
        
        # 全局订阅者（接收所有结果）
        self._global_subscribers: Set[Subscription] = set()
        
        # 结果索引（用于快速查询）
        self._index_by_agent: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> task_ids
        self._index_by_status: Dict[bool, Set[str]] = defaultdict(set)  # success -> task_ids
        
        # 统计信息
        self._stats = {
            "total_stored": 0,
            "total_queries": 0,
            "total_subscribers": 0
        }
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 加载持久化数据
        if self.storage_path:
            self._load()
        
        logger.info(f"ResultCollector 初始化完成 (storage={self.storage_path}, max_results={max_results})")
    
    def store(self, result: TaskResult) -> str:
        """
        存储结果
        
        参数:
            result: 任务结果
        
        返回:
            任务 ID
        """
        with self._lock:
            task_id = result.task_id
            
            # 存储结果
            self._results[task_id].append(result)
            
            # 更新索引
            self._index_by_agent[result.agent_id].add(task_id)
            self._index_by_status[result.success].add(task_id)
            
            # 更新统计
            self._stats["total_stored"] += 1
            
            # 通知订阅者
            self._notify_subscribers(task_id, result)
            
            # 清理旧结果
            self._cleanup_if_needed()
            
            # 持久化
            self._save()
            
            logger.debug(f"结果已存储：task={task_id}, agent={result.agent_id}, success={result.success}")
            return task_id
    
    def get(self, task_id: str, limit: int = 10) -> List[TaskResult]:
        """
        获取任务结果
        
        参数:
            task_id: 任务 ID
            limit: 返回数量限制
        
        返回:
            结果列表（按时间倒序）
        """
        with self._lock:
            self._stats["total_queries"] += 1
            
            results = self._results.get(task_id, [])
            
            # 按时间倒序
            sorted_results = sorted(results, key=lambda r: r.created_at, reverse=True)
            
            return sorted_results[:limit]
    
    def get_latest(self, task_id: str) -> Optional[TaskResult]:
        """
        获取最新结果
        
        参数:
            task_id: 任务 ID
        
        返回:
            最新结果，如果不存在则返回 None
        """
        results = self.get(task_id, limit=1)
        return results[0] if results else None
    
    def get_all(self, task_id: str) -> List[TaskResult]:
        """
        获取任务所有结果（多 Agent 协作场景）
        
        参数:
            task_id: 任务 ID
        
        返回:
            所有结果
        """
        return self.get(task_id, limit=1000)
    
    def get_by_agent(self, agent_id: str, limit: int = 100) -> List[TaskResult]:
        """
        按 Agent 获取结果
        
        参数:
            agent_id: Agent ID
            limit: 返回数量限制
        
        返回:
            结果列表
        """
        with self._lock:
            task_ids = self._index_by_agent.get(agent_id, set())
            results = []
            
            for task_id in task_ids:
                task_results = self._results.get(task_id, [])
                results.extend([r for r in task_results if r.agent_id == agent_id])
            
            # 按时间倒序
            sorted_results = sorted(results, key=lambda r: r.created_at, reverse=True)
            
            return sorted_results[:limit]
    
    def get_successful(self, limit: int = 100) -> List[TaskResult]:
        """
        获取成功的结果
        
        参数:
            limit: 返回数量限制
        
        返回:
            结果列表
        """
        with self._lock:
            task_ids = self._index_by_status.get(True, set())
            results = []
            
            for task_id in task_ids:
                task_results = self._results.get(task_id, [])
                results.extend([r for r in task_results if r.success])
            
            sorted_results = sorted(results, key=lambda r: r.created_at, reverse=True)
            return sorted_results[:limit]
    
    def get_failed(self, limit: int = 100) -> List[TaskResult]:
        """
        获取失败的结果
        
        参数:
            limit: 返回数量限制
        
        返回:
            结果列表
        """
        with self._lock:
            task_ids = self._index_by_status.get(False, set())
            results = []
            
            for task_id in task_ids:
                task_results = self._results.get(task_id, [])
                results.extend([r for r in task_results if not r.success])
            
            sorted_results = sorted(results, key=lambda r: r.created_at, reverse=True)
            return sorted_results[:limit]
    
    def subscribe(self, task_id: str, callback: Callable[[TaskResult], None]) -> str:
        """
        订阅任务结果
        
        参数:
            task_id: 任务 ID（"*" 表示订阅所有）
            callback: 回调函数
        
        返回:
            订阅 ID
        """
        with self._lock:
            subscription = Subscription(callback=callback)
            
            if task_id == "*":
                self._global_subscribers.add(subscription)
            else:
                self._subscribers[task_id].add(subscription)
            
            self._stats["total_subscribers"] += 1
            
            logger.debug(f"订阅结果：task={task_id}")
            return str(id(subscription))
    
    def unsubscribe(self, task_id: str, callback: Callable[[TaskResult], None]) -> bool:
        """
        取消订阅
        
        参数:
            task_id: 任务 ID
            callback: 回调函数
        
        返回:
            是否成功
        """
        with self._lock:
            if task_id == "*":
                # 取消全局订阅
                to_remove = [s for s in self._global_subscribers if s.callback == callback]
                for s in to_remove:
                    self._global_subscribers.remove(s)
                return len(to_remove) > 0
            else:
                # 取消特定任务订阅
                subscribers = self._subscribers.get(task_id, set())
                to_remove = [s for s in subscribers if s.callback == callback]
                for s in to_remove:
                    subscribers.remove(s)
                return len(to_remove) > 0
    
    def aggregate_results(self, task_id: str) -> Dict:
        """
        聚合多 Agent 结果
        
        参数:
            task_id: 任务 ID
        
        返回:
            聚合结果
        """
        results = self.get_all(task_id)
        
        if not results:
            return {
                "task_id": task_id,
                "total_results": 0,
                "success_count": 0,
                "failed_count": 0,
                "results": []
            }
        
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        # 合并结果
        merged_result = {}
        errors = []
        
        for result in results:
            if result.success and result.result:
                if isinstance(result.result, dict):
                    merged_result.update(result.result)
                else:
                    merged_result[result.agent_id] = result.result
            elif result.error:
                errors.append({
                    "agent_id": result.agent_id,
                    "error": result.error
                })
        
        return {
            "task_id": task_id,
            "total_results": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "merged_result": merged_result,
            "errors": errors,
            "results": [r.to_dict() for r in results]
        }
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        返回:
            统计信息字典
        """
        with self._lock:
            return {
                **self._stats,
                "unique_tasks": len(self._results),
                "unique_agents": len(self._index_by_agent),
                "subscriber_count": len(self._global_subscribers) + sum(len(s) for s in self._subscribers.values())
            }
    
    def clear(self, older_than: Optional[datetime] = None) -> int:
        """
        清理结果
        
        参数:
            older_than: 清理早于此时间的结果（None 表示清理所有）
        
        返回:
            清理的结果数量
        """
        with self._lock:
            if older_than is None:
                count = sum(len(results) for results in self._results.values())
                self._results.clear()
                self._index_by_agent.clear()
                self._index_by_status.clear()
                logger.info(f"清理所有结果：{count} 个")
                return count
            
            count = 0
            task_ids_to_remove = set()
            
            for task_id, results in self._results.items():
                # 过滤旧结果
                new_results = [r for r in results if r.created_at >= older_than]
                removed_count = len(results) - len(new_results)
                
                if removed_count > 0:
                    count += removed_count
                    self._results[task_id] = new_results
                    
                    if not new_results:
                        task_ids_to_remove.add(task_id)
            
            # 移除空任务
            for task_id in task_ids_to_remove:
                del self._results[task_id]
            
            # 重建索引
            self._rebuild_index()
            
            logger.info(f"清理结果：{count} 个")
            return count
    
    def _notify_subscribers(self, task_id: str, result: TaskResult):
        """通知订阅者"""
        # 通知特定任务订阅者
        for subscription in self._subscribers.get(task_id, set()):
            try:
                subscription.callback(result)
            except Exception as e:
                logger.error(f"通知订阅者失败：{e}")
        
        # 通知全局订阅者
        for subscription in self._global_subscribers:
            try:
                subscription.callback(result)
            except Exception as e:
                logger.error(f"通知全局订阅者失败：{e}")
    
    def _cleanup_if_needed(self):
        """如果超过最大数量，清理旧结果"""
        total_results = sum(len(results) for results in self._results.values())
        
        if total_results > self.max_results:
            # 找出最旧的结果
            all_results = []
            for task_id, results in self._results.items():
                for result in results:
                    all_results.append((result.created_at, task_id, result))
            
            # 按时间排序
            all_results.sort(key=lambda x: x[0])
            
            # 删除最旧的 10%
            to_delete = int(total_results * 0.1)
            for _, task_id, result in all_results[:to_delete]:
                if task_id in self._results:
                    self._results[task_id] = [
                        r for r in self._results[task_id]
                        if r.created_at != result.created_at
                    ]
            
            # 重建索引
            self._rebuild_index()
            
            logger.info(f"自动清理旧结果：{to_delete} 个")
    
    def _rebuild_index(self):
        """重建索引"""
        self._index_by_agent.clear()
        self._index_by_status.clear()
        
        for task_id, results in self._results.items():
            for result in results:
                self._index_by_agent[result.agent_id].add(task_id)
                self._index_by_status[result.success].add(task_id)
    
    def _save(self):
        """持久化数据"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "results": {
                    task_id: [r.to_dict() for r in results]
                    for task_id, results in self._results.items()
                },
                "stats": self._stats,
                "saved_at": datetime.now().isoformat()
            }
            
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"结果数据已保存：{self.storage_path}")
            
        except Exception as e:
            logger.error(f"保存结果数据失败：{e}")
    
    def _load(self):
        """加载持久化数据"""
        if not self.storage_path or not self.storage_path.exists():
            logger.info("无持久化数据，使用空收集器")
            return
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 加载结果
            self._results = defaultdict(list)
            for task_id, result_list in data.get("results", {}).items():
                for result_data in result_list:
                    result = TaskResult.from_dict(result_data)
                    self._results[task_id].append(result)
            
            # 加载统计
            self._stats = data.get("stats", self._stats)
            
            # 重建索引
            self._rebuild_index()
            
            logger.info(f"已加载 {sum(len(r) for r in self._results.values())} 个结果")
            
        except Exception as e:
            logger.error(f"加载结果数据失败：{e}")
            self._results = defaultdict(list)
            self._stats = {"total_stored": 0, "total_queries": 0, "total_subscribers": 0}
