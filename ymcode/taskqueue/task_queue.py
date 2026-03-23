#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务队列系统

提供优先级队列、持久化、重试机制
"""

import json
import heapq
import logging
import threading
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable, Any
from collections import defaultdict

from .task import Task, TaskStatus, TaskPriority, TaskResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TaskQueue:
    """
    任务队列类
    
    特性:
    - 优先级队列（高优先级任务优先）
    - 持久化存储（SQLite/JSON）
    - 重试机制
    - 死信队列
    - 统计信息
    
    使用示例:
        >>> queue = TaskQueue()
        >>> task = Task(title="测试任务", priority=TaskPriority.HIGH)
        >>> queue.enqueue(task)
        >>> next_task = queue.dequeue()
    """
    
    def __init__(self, storage_path: Optional[str] = None, use_sqlite: bool = False):
        """
        初始化任务队列
        
        参数:
            storage_path: 持久化路径（可选，默认内存）
            use_sqlite: 是否使用 SQLite（默认 False，使用 JSON）
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.use_sqlite = use_sqlite and self.storage_path is not None
        
        # 优先级队列：(priority, timestamp, task)
        # 使用负数实现高优先级优先
        self._queue: List[Tuple[int, float, Task]] = []
        self._counter = 0  # 用于稳定排序
        
        # 任务存储
        self._tasks: Dict[str, Task] = {}
        
        # 死信队列
        self._dead_letter: List[Task] = []
        
        # 统计信息
        self._stats = {
            "total_enqueued": 0,
            "total_dequeued": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_retried": 0
        }
        
        # 线程锁（并发安全）
        self._lock = threading.RLock()
        
        # 加载持久化数据
        if self.storage_path:
            self._load()
        
        logger.info(f"TaskQueue 初始化完成 (storage={self.storage_path})")
    
    def enqueue(self, task: Task, priority: Optional[TaskPriority] = None) -> str:
        """
        入队任务
        
        参数:
            task: 任务对象
            priority: 优先级（可选，覆盖任务的 priority）
        
        返回:
            任务 ID
        """
        with self._lock:  # ✅ 线程锁保护
            if priority:
                task.priority = priority
            
            task.status = TaskStatus.QUEUED
            task.updated_at = datetime.now()
            
            # 加入优先级队列
            # 使用负数：priority 越高，值越小，越先出队
            heapq.heappush(
                self._queue,
                (-task.priority.value, self._counter, task)
            )
            self._counter += 1
            
            # 存储任务
            self._tasks[task.id] = task
            
            # 更新统计
            self._stats["total_enqueued"] += 1
            
            # 持久化
            self._save()
            
            logger.info(f"任务入队：{task.id} ({task.title}) 优先级={task.priority.name}")
            return task.id
    
    def dequeue(self) -> Optional[Task]:
        """
        出队任务（获取最高优先级任务）
        
        返回:
            任务对象，如果队列为空则返回 None
        """
        with self._lock:  # ✅ 线程锁保护
            while self._queue:
                _, _, task = heapq.heappop(self._queue)
                
                # 检查任务是否仍然有效
                if task.id in self._tasks and task.status == TaskStatus.QUEUED:
                    task.status = TaskStatus.PENDING
                    task.updated_at = datetime.now()
                    
                    self._stats["total_dequeued"] += 1
                    
                    logger.info(f"任务出队：{task.id} ({task.title})")
                    return task
            
            logger.debug("队列为空")
            return None
    
    def peek(self) -> Optional[Task]:
        """
        查看队首任务（不出队）
        
        返回:
            队首任务，如果队列为空则返回 None
        """
        while self._queue:
            _, _, task = self._queue[0]
            if task.id in self._tasks:
                return task
            heapq.heappop(self._queue)  # 移除无效任务
        
        return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            任务对象，如果不存在则返回 None
        """
        return self._tasks.get(task_id)
    
    def complete_task(self, task_id: str, result: Optional[Dict] = None) -> bool:
        """
        完成任务
        
        参数:
            task_id: 任务 ID
            result: 执行结果
        
        返回:
            是否成功
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在：{task_id}")
            return False
        
        task.complete(result)
        self._stats["total_completed"] += 1
        
        logger.info(f"任务完成：{task_id}")
        self._save()
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """
        标记任务失败
        
        参数:
            task_id: 任务 ID
            error: 错误信息
        
        返回:
            是否成功
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在：{task_id}")
            return False
        
        old_status = task.status
        task.fail(error)
        
        if task.status == TaskStatus.FAILED:
            # 达到最大重试次数，加入死信队列
            self._dead_letter.append(task)
            self._stats["total_failed"] += 1
            logger.error(f"任务失败（达到最大重试次数）: {task_id} - {error}")
        elif task.status == TaskStatus.PENDING:
            # 可重试，重新入队
            self.enqueue(task)
            self._stats["total_retried"] += 1
            logger.warning(f"任务重试：{task_id} (第{task.retry_count}次)")
        
        self._save()
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            是否成功
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在：{task_id}")
            return False
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            logger.warning(f"任务已完成/失败/取消，无法取消：{task_id}")
            return False
        
        task.cancel()
        logger.info(f"任务已取消：{task_id}")
        self._save()
        return True
    
    def retry_task(self, task_id: str) -> bool:
        """
        重试任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            是否成功
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在：{task_id}")
            return False
        
        if task.status != TaskStatus.FAILED:
            logger.warning(f"任务未失败，无法重试：{task_id}")
            return False
        
        # 重置任务状态
        task.status = TaskStatus.PENDING
        task.error = None
        task.retry_count = 0
        task.updated_at = datetime.now()
        
        # 重新入队
        self.enqueue(task)
        
        logger.info(f"任务重试：{task_id}")
        self._save()
        return True
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """
        列出任务
        
        参数:
            status: 按状态筛选
            assigned_to: 按执行 Agent 筛选
            limit: 返回数量限制
        
        返回:
            任务列表
        """
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        
        # 按创建时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        返回:
            统计信息字典
        """
        queue_size = len([t for t in self._tasks.values() if t.status == TaskStatus.QUEUED])
        running_count = len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING])
        
        return {
            **self._stats,
            "queue_size": queue_size,
            "running_count": running_count,
            "dead_letter_count": len(self._dead_letter)
        }
    
    def clear_dead_letter(self) -> int:
        """
        清空死信队列
        
        返回:
            清空的任务数量
        """
        count = len(self._dead_letter)
        self._dead_letter.clear()
        logger.info(f"清空死信队列：{count} 个任务")
        return count
    
    def _save(self):
        """持久化数据（原子写入 - 防止数据损坏）"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "tasks": {tid: t.to_dict() for tid, t in self._tasks.items()},
                "dead_letter": [t.to_dict() for t in self._dead_letter],
                "stats": self._stats,
                "counter": self._counter,
                "saved_at": datetime.now().isoformat()
            }
            
            # ✅ 原子写入：先写临时文件，再重命名
            temp_path = self.storage_path.with_suffix(self.storage_path.suffix + ".tmp")
            
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入临时文件
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())  # ✅ 确保数据刷入磁盘
            
            # ✅ 原子重命名（覆盖旧文件）
            temp_path.replace(self.storage_path)
            
            logger.debug(f"数据已原子保存：{self.storage_path}")
            
        except Exception as e:
            logger.error(f"保存数据失败：{e}")
            # 清理临时文件
            try:
                if 'temp_path' in locals() and temp_path.exists():
                    temp_path.unlink()
            except:
                pass
    
    def _load(self):
        """加载持久化数据"""
        if not self.storage_path or not self.storage_path.exists():
            logger.info("无持久化数据，使用空队列")
            return
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 加载任务
            self._tasks = {
                tid: Task.from_dict(tdata)
                for tid, tdata in data.get("tasks", {}).items()
            }
            
            # 加载死信队列
            self._dead_letter = [
                Task.from_dict(tdata)
                for tdata in data.get("dead_letter", [])
            ]
            
            # 加载统计
            self._stats = data.get("stats", self._stats)
            self._counter = data.get("counter", 0)
            
            # 重建队列（只包含 QUEUED 状态的任务）
            self._queue = []
            self._counter = 0
            for task in self._tasks.values():
                if task.status == TaskStatus.QUEUED:
                    heapq.heappush(
                        self._queue,
                        (-task.priority.value, self._counter, task)
                    )
                    self._counter += 1
            
            logger.info(f"已加载 {len(self._tasks)} 个任务，{len(self._dead_letter)} 个死信任务")
            
        except Exception as e:
            logger.error(f"加载数据失败：{e}")
            # 失败时使用空队列
            self._tasks = {}
            self._dead_letter = []
            self._stats = {"total_enqueued": 0, "total_dequeued": 0, "total_completed": 0, "total_failed": 0, "total_retried": 0}
