#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Tracker - 任务状态追踪器

功能：
- 记录任务状态历史
- 状态转换验证
- 状态查询 API
- 状态持久化
"""

import json
import threading
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TaskState(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"       # 待处理
    SCHEDULED = "SCHEDULED"   # 已调度
    RUNNING = "RUNNING"       # 进行中
    PAUSED = "PAUSED"         # 已暂停
    COMPLETED = "COMPLETED"   # 已完成
    FAILED = "FAILED"         # 失败
    CANCELLED = "CANCELLED"   # 已取消
    TIMEOUT = "TIMEOUT"       # 超时


# 有效的状态转换
VALID_TRANSITIONS = {
    TaskState.PENDING: {TaskState.SCHEDULED, TaskState.CANCELLED},
    TaskState.SCHEDULED: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.PENDING},
    TaskState.RUNNING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.TIMEOUT, TaskState.PAUSED},
    TaskState.PAUSED: {TaskState.RUNNING, TaskState.CANCELLED},
    TaskState.COMPLETED: set(),  # 终态
    TaskState.FAILED: {TaskState.PENDING},  # 可重试
    TaskState.CANCELLED: set(),  # 终态
    TaskState.TIMEOUT: {TaskState.PENDING},  # 可重试
}


@dataclass
class StateChange:
    """状态变更记录"""
    task_id: str
    from_state: Optional[str]
    to_state: str
    timestamp: str
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class StateTracker:
    """
    任务状态追踪器
    
    用法:
        tracker = StateTracker()
        tracker.record_state(task_id, "PENDING")
        tracker.get_history(task_id)
    """
    
    def __init__(self, storage_path: Optional[Path] = None, max_history: int = 100):
        """
        初始化状态追踪器
        
        Args:
            storage_path: 持久化存储路径（可选）
            max_history: 每个任务最大历史记录数
        """
        self.storage_path = storage_path or Path(__file__).parent.parent / "data" / "state_history.json"
        self.max_history = max_history
        
        # 内存存储
        self._states: Dict[str, TaskState] = {}  # task_id -> current_state
        self._history: Dict[str, List[StateChange]] = {}  # task_id -> [StateChange]
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 加载持久化数据
        self._load()
        
        logger.info(f"StateTracker 初始化完成，存储路径：{self.storage_path}")
    
    def record_state(
        self,
        task_id: str,
        to_state: str,
        from_state: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录状态变化
        
        Args:
            task_id: 任务 ID
            to_state: 目标状态
            from_state: 源状态（可选，自动获取）
            reason: 变化原因（可选）
            metadata: 附加元数据（可选）
        
        Returns:
            bool: 是否成功记录
        """
        with self._lock:
            try:
                # 转换状态枚举
                if isinstance(to_state, str):
                    to_state_enum = TaskState(to_state)
                else:
                    to_state_enum = to_state
                
                # 获取当前状态
                if from_state is None:
                    from_state_enum = self._states.get(task_id)
                else:
                    from_state_enum = TaskState(from_state) if isinstance(from_state, str) else from_state
                
                # 验证状态转换
                if not self._is_valid_transition(from_state_enum, to_state_enum):
                    logger.warning(f"无效的状态转换：{from_state_enum} -> {to_state_enum} (task: {task_id})")
                    # 不阻止记录，但记录警告
                
                # 创建状态变更记录
                change = StateChange(
                    task_id=task_id,
                    from_state=from_state_enum.value if from_state_enum else None,
                    to_state=to_state_enum.value,
                    timestamp=datetime.now().isoformat(),
                    reason=reason,
                    metadata=metadata
                )
                
                # 更新当前状态
                self._states[task_id] = to_state_enum
                
                # 添加到历史记录
                if task_id not in self._history:
                    self._history[task_id] = []
                
                self._history[task_id].append(change)
                
                # 限制历史记录数量
                if len(self._history[task_id]) > self.max_history:
                    self._history[task_id] = self._history[task_id][-self.max_history:]
                
                # 持久化
                self._save()
                
                logger.debug(f"状态更新：{task_id} {from_state_enum.value if from_state_enum else 'None'} -> {to_state_enum.value}")
                
                return True
                
            except Exception as e:
                logger.error(f"记录状态失败：{e}")
                return False
    
    def get_current_state(self, task_id: str) -> Optional[TaskState]:
        """获取任务当前状态"""
        with self._lock:
            return self._states.get(task_id)
    
    def get_history(self, task_id: str, limit: Optional[int] = None) -> List[StateChange]:
        """
        获取任务状态历史
        
        Args:
            task_id: 任务 ID
            limit: 返回数量限制（可选）
        
        Returns:
            状态变更记录列表
        """
        with self._lock:
            history = self._history.get(task_id, [])
            if limit:
                return history[-limit:]
            return history.copy()
    
    def get_all_states(self) -> Dict[str, TaskState]:
        """获取所有任务当前状态"""
        with self._lock:
            return self._states.copy()
    
    def get_tasks_by_state(self, state: str) -> List[str]:
        """
        获取指定状态的所有任务 ID
        
        Args:
            state: 状态名称
        
        Returns:
            任务 ID 列表
        """
        with self._lock:
            state_enum = TaskState(state) if isinstance(state, str) else state
            return [
                task_id for task_id, task_state in self._states.items()
                if task_state == state_enum
            ]
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """检查状态转换是否有效"""
        from_state_enum = TaskState(from_state) if isinstance(from_state, str) else from_state
        to_state_enum = TaskState(to_state) if isinstance(to_state, str) else to_state
        return self._is_valid_transition(from_state_enum, to_state_enum)
    
    def _is_valid_transition(self, from_state: Optional[TaskState], to_state: TaskState) -> bool:
        """内部状态转换验证"""
        if from_state is None:
            return True  # 新任务
        
        valid_targets = VALID_TRANSITIONS.get(from_state, set())
        return to_state in valid_targets
    
    def _save(self):
        """持久化到磁盘"""
        try:
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 序列化数据
            data = {
                "states": {k: v.value for k, v in self._states.items()},
                "history": {
                    task_id: [change.to_dict() for change in changes]
                    for task_id, changes in self._history.items()
                },
                "updated_at": datetime.now().isoformat()
            }
            
            # 原子写入
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            temp_path.replace(self.storage_path)
            
        except Exception as e:
            logger.error(f"持久化失败：{e}")
    
    def _load(self):
        """从磁盘加载数据"""
        if not self.storage_path.exists():
            logger.info("未找到持久化文件，使用空数据")
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复状态
            self._states = {
                task_id: TaskState(state)
                for task_id, state in data.get("states", {}).items()
            }
            
            # 恢复历史
            self._history = {
                task_id: [StateChange(**change) for change in changes]
                for task_id, changes in data.get("history", {}).items()
            }
            
            logger.info(f"加载了 {len(self._states)} 个任务状态")
            
        except Exception as e:
            logger.error(f"加载失败：{e}")
    
    def clear(self):
        """清空所有状态（用于测试）"""
        with self._lock:
            self._states.clear()
            self._history.clear()
            self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            state_counts = {}
            for state in self._states.values():
                state_counts[state.value] = state_counts.get(state.value, 0) + 1
            
            return {
                "total_tasks": len(self._states),
                "state_distribution": state_counts,
                "total_history_records": sum(len(h) for h in self._history.values()),
                "storage_path": str(self.storage_path)
            }


# 全局单例
_tracker_instance: Optional[StateTracker] = None


def get_state_tracker() -> StateTracker:
    """获取全局 StateTracker 实例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = StateTracker()
    return _tracker_instance


def reset_state_tracker():
    """重置全局实例（用于测试）"""
    global _tracker_instance
    _tracker_instance = None
