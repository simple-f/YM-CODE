#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件类型定义
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class EventType(Enum):
    """事件类型枚举"""
    # Agent 相关
    AGENT_REGISTERED = "agent.registered"
    AGENT_UNREGISTERED = "agent.unregistered"
    AGENT_STATUS_CHANGED = "agent.status_changed"
    AGENT_ERROR = "agent.error"
    
    # 任务相关
    TASK_CREATED = "task.created"
    TASK_QUEUED = "task.queued"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    TASK_RETRIED = "task.retried"
    
    # 交接相关
    HANDOFF_STARTED = "handoff.started"
    HANDOFF_COMPLETED = "handoff.completed"
    HANDOFF_FAILED = "handoff.failed"
    
    # 系统相关
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"
    
    # 队列相关
    QUEUE_LOW = "queue.low"
    QUEUE_HIGH = "queue.high"


@dataclass
class Event:
    """
    事件类
    
    属性:
        id: 事件唯一标识
        type: 事件类型
        timestamp: 时间戳
        source: 事件来源（Agent ID 或系统组件）
        data: 事件数据
        metadata: 元数据
    """
    type: EventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Event":
        """从字典创建"""
        data = data.copy()
        data["type"] = EventType(data["type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


# 便捷事件创建函数

def agent_registered(agent_id: str, capabilities: list) -> Event:
    """Agent 注册事件"""
    return Event(
        type=EventType.AGENT_REGISTERED,
        source=agent_id,
        data={"agent_id": agent_id, "capabilities": capabilities}
    )


def agent_unregistered(agent_id: str) -> Event:
    """Agent 注销事件"""
    return Event(
        type=EventType.AGENT_UNREGISTERED,
        source=agent_id,
        data={"agent_id": agent_id}
    )


def agent_status_changed(agent_id: str, old_status: str, new_status: str) -> Event:
    """Agent 状态变化事件"""
    return Event(
        type=EventType.AGENT_STATUS_CHANGED,
        source=agent_id,
        data={
            "agent_id": agent_id,
            "old_status": old_status,
            "new_status": new_status
        }
    )


def task_created(task_id: str, title: str, assigned_to: Optional[str] = None) -> Event:
    """任务创建事件"""
    return Event(
        type=EventType.TASK_CREATED,
        source="system",
        data={
            "task_id": task_id,
            "title": title,
            "assigned_to": assigned_to
        }
    )


def task_started(task_id: str, agent_id: str) -> Event:
    """任务开始事件"""
    return Event(
        type=EventType.TASK_STARTED,
        source=agent_id,
        data={"task_id": task_id, "agent_id": agent_id}
    )


def task_completed(task_id: str, agent_id: str, result: Dict) -> Event:
    """任务完成事件"""
    return Event(
        type=EventType.TASK_COMPLETED,
        source=agent_id,
        data={
            "task_id": task_id,
            "agent_id": agent_id,
            "result": result
        }
    )


def task_failed(task_id: str, agent_id: str, error: str) -> Event:
    """任务失败事件"""
    return Event(
        type=EventType.TASK_FAILED,
        source=agent_id,
        data={
            "task_id": task_id,
            "agent_id": agent_id,
            "error": error
        }
    )


def handoff_completed(from_agent: str, to_agent: str, task_id: str) -> Event:
    """交接完成事件"""
    return Event(
        type=EventType.HANDOFF_COMPLETED,
        source=from_agent,
        data={
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_id": task_id
        }
    )
