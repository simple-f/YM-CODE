#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cascade Cancel - 级联取消器

功能：
- 父子任务关系追踪
- 取消传播逻辑
- 取消确认机制
- 取消事件通知
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field

from ..utils.logger import get_logger
from ..events import EventBus, EventType
from .state_tracker import StateTracker, TaskState, get_state_tracker

logger = get_logger(__name__)


@dataclass
class TaskRelation:
    """任务关系"""
    task_id: str
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CascadeCanceller:
    """
    级联取消器
    
    用法:
        canceller = CascadeCanceller(task_queue, state_tracker)
        await canceller.cancel_with_children(task_id)
    """
    
    def __init__(
        self,
        task_queue: Any = None,
        state_tracker: Optional[StateTracker] = None,
        event_bus: Optional[EventBus] = None
    ):
        """
        初始化级联取消器
        
        Args:
            task_queue: 任务队列实例
            state_tracker: 状态追踪器实例
            event_bus: 事件总线实例
        """
        self.task_queue = task_queue
        self.state_tracker = state_tracker or get_state_tracker()
        self.event_bus = event_bus
        
        # 任务关系存储
        self._relations: Dict[str, TaskRelation] = {}
        
        # 取消中的任务（防止重复取消）
        self._cancelling: Set[str] = set()
        
        # 取消处理器
        self._cancel_handlers: Dict[str, Callable] = {}
        
        logger.info("CascadeCanceller 初始化完成")
    
    def register_parent_child(self, parent_id: str, child_id: str):
        """
        注册父子任务关系
        
        Args:
            parent_id: 父任务 ID
            child_id: 子任务 ID
        """
        if parent_id not in self._relations:
            self._relations[parent_id] = TaskRelation(task_id=parent_id)
        
        if child_id not in self._relations:
            self._relations[child_id] = TaskRelation(task_id=child_id, parent_id=parent_id)
        
        # 添加到父任务的子任务列表
        if child_id not in self._relations[parent_id].children:
            self._relations[parent_id].children.append(child_id)
        
        logger.debug(f"注册任务关系：{parent_id} -> {child_id}")
    
    def unregister_task(self, task_id: str):
        """
        注销任务关系（任务完成或清理时调用）
        
        Args:
            task_id: 任务 ID
        """
        if task_id in self._relations:
            relation = self._relations[task_id]
            
            # 从父任务的子任务列表中移除
            if relation.parent_id and relation.parent_id in self._relations:
                if task_id in self._relations[relation.parent_id].children:
                    self._relations[relation.parent_id].children.remove(task_id)
            
            del self._relations[task_id]
            logger.debug(f"注销任务关系：{task_id}")
    
    def get_children(self, task_id: str, recursive: bool = True) -> List[str]:
        """
        获取任务的所有子任务
        
        Args:
            task_id: 任务 ID
            recursive: 是否递归获取（包括子任务的子任务）
        
        Returns:
            子任务 ID 列表
        """
        if task_id not in self._relations:
            return []
        
        children = []
        to_process = [task_id]
        
        while to_process:
            current_id = to_process.pop(0)
            if current_id in self._relations:
                direct_children = self._relations[current_id].children.copy()
                children.extend(direct_children)
                if recursive:
                    to_process.extend(direct_children)
        
        return children
    
    def get_parent(self, task_id: str) -> Optional[str]:
        """获取任务的父任务 ID"""
        if task_id in self._relations:
            return self._relations[task_id].parent_id
        return None
    
    async def cancel_with_children(
        self,
        task_id: str,
        reason: Optional[str] = None,
        timeout: float = 30.0
    ) -> Dict[str, bool]:
        """
        级联取消任务及其所有子任务
        
        Args:
            task_id: 任务 ID
            reason: 取消原因
            timeout: 取消超时时间（秒）
        
        Returns:
            任务取消结果字典 {task_id: success}
        """
        if task_id in self._cancelling:
            logger.warning(f"任务 {task_id} 已在取消中")
            return {task_id: False}
        
        self._cancelling.add(task_id)
        results = {}
        
        try:
            # 获取所有子任务
            children = self.get_children(task_id, recursive=True)
            
            # 按深度优先顺序取消（先取消子任务）
            cancel_order = list(reversed(children)) + [task_id]
            
            logger.info(f"开始级联取消：{task_id}，共 {len(cancel_order)} 个任务")
            
            # 发布取消开始事件
            await self._publish_event(EventType.TASK_CANCELLING, {
                "task_id": task_id,
                "reason": reason,
                "children_count": len(children)
            })
            
            # 并发取消所有任务
            tasks = [
                self._cancel_single_task(tid, reason, timeout)
                for tid in cancel_order
            ]
            
            cancel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for tid, result in zip(cancel_order, cancel_results):
                if isinstance(result, Exception):
                    logger.error(f"取消任务 {tid} 失败：{result}")
                    results[tid] = False
                else:
                    results[tid] = result
            
            success_count = sum(1 for v in results.values() if v)
            logger.info(f"级联取消完成：{success_count}/{len(cancel_order)} 成功")
            
            # 发布取消完成事件
            await self._publish_event(EventType.TASK_CANCELLED, {
                "task_id": task_id,
                "success_count": success_count,
                "total_count": len(cancel_order)
            })
            
        except Exception as e:
            logger.error(f"级联取消失败：{e}")
            results[task_id] = False
        finally:
            self._cancelling.discard(task_id)
        
        return results
    
    async def _cancel_single_task(
        self,
        task_id: str,
        reason: Optional[str],
        timeout: float
    ) -> bool:
        """
        取消单个任务
        
        Args:
            task_id: 任务 ID
            reason: 取消原因
            timeout: 超时时间
        
        Returns:
            是否成功取消
        """
        try:
            # 检查任务状态
            current_state = self.state_tracker.get_current_state(task_id)
            
            if current_state in [TaskState.COMPLETED, TaskState.CANCELLED]:
                logger.debug(f"任务 {task_id} 已是终态 ({current_state})，跳过取消")
                return True
            
            if current_state not in [TaskState.PENDING, TaskState.SCHEDULED, TaskState.RUNNING, TaskState.PAUSED]:
                logger.warning(f"任务 {task_id} 状态 {current_state} 不可取消")
                return False
            
            # 记录取消状态
            self.state_tracker.record_state(
                task_id=task_id,
                to_state=TaskState.CANCELLED,
                reason=reason or "级联取消"
            )
            
            # 调用自定义取消处理器
            if task_id in self._cancel_handlers:
                try:
                    handler = self._cancel_handlers[task_id]
                    if asyncio.iscoroutinefunction(handler):
                        await asyncio.wait_for(handler(task_id), timeout=timeout)
                    else:
                        handler(task_id)
                except asyncio.TimeoutError:
                    logger.error(f"取消处理器超时：{task_id}")
                    return False
                except Exception as e:
                    logger.error(f"取消处理器错误：{task_id}: {e}")
                    # 继续执行，不阻止状态更新
            
            # 从任务队列中移除（如果存在）
            if self.task_queue:
                try:
                    self.task_queue.cancel_task(task_id)
                except Exception as e:
                    logger.warning(f"从队列取消失败：{task_id}: {e}")
            
            logger.info(f"任务已取消：{task_id}")
            return True
            
        except Exception as e:
            logger.error(f"取消任务失败：{task_id}: {e}")
            return False
    
    def register_cancel_handler(self, task_id: str, handler: Callable):
        """
        注册任务取消处理器
        
        Args:
            task_id: 任务 ID
            handler: 取消处理函数
        """
        self._cancel_handlers[task_id] = handler
        logger.debug(f"注册取消处理器：{task_id}")
    
    def unregister_cancel_handler(self, task_id: str):
        """注销取消处理器"""
        if task_id in self._cancel_handlers:
            del self._cancel_handlers[task_id]
    
    async def _publish_event(self, event_type: EventType, data: Dict[str, Any]):
        """发布事件"""
        if self.event_bus:
            try:
                self.event_bus.publish(event_type, data, source="cascade_cancel")
            except Exception as e:
                logger.error(f"发布事件失败：{e}")
    
    def get_relation_stats(self) -> Dict[str, Any]:
        """获取关系统计"""
        parent_count = sum(1 for r in self._relations.values() if r.parent_id is None)
        child_count = sum(1 for r in self._relations.values() if r.parent_id is not None)
        
        return {
            "total_relations": len(self._relations),
            "parent_tasks": parent_count,
            "child_tasks": child_count,
            "cancelling_tasks": len(self._cancelling)
        }


# 全局单例
_canceller_instance: Optional[CascadeCanceller] = None


def get_cascade_canceller(
    task_queue: Any = None,
    state_tracker: Optional[StateTracker] = None,
    event_bus: Optional[EventBus] = None
) -> CascadeCanceller:
    """获取全局 CascadeCanceller 实例"""
    global _canceller_instance
    if _canceller_instance is None:
        _canceller_instance = CascadeCanceller(task_queue, state_tracker, event_bus)
    return _canceller_instance


def reset_cascade_canceller():
    """重置全局实例"""
    global _canceller_instance
    _canceller_instance = None
