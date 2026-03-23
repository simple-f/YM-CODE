#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务定义模块

提供任务数据结构和状态管理
"""

import uuid
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"       # 等待中
    QUEUED = "queued"         # 已入队
    RUNNING = "running"       # 运行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 0       # 低优先级
    NORMAL = 1    # 普通优先级
    HIGH = 2      # 高优先级
    URGENT = 3    # 紧急优先级


@dataclass
class Task:
    """
    任务类
    
    属性:
        id: 任务唯一标识
        title: 任务标题
        description: 任务描述
        status: 任务状态
        priority: 任务优先级
        assigned_to: 分配给的 Agent 名称
        created_at: 创建时间
        updated_at: 更新时间
        started_at: 开始时间
        completed_at: 完成时间
        metadata: 元数据
        error: 错误信息（失败时）
        retry_count: 重试次数
        max_retries: 最大重试次数
    """
    title: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """后处理：确保时间对象正确"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)
    
    def start(self):
        """标记任务开始"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def complete(self, result: Optional[Dict] = None):
        """标记任务完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        if result:
            self.metadata["result"] = result
    
    def fail(self, error: str):
        """标记任务失败"""
        self.error = error
        self.updated_at = datetime.now()
        
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = TaskStatus.PENDING  # 可重试
        else:
            self.status = TaskStatus.FAILED   # 达到最大重试次数
    
    def cancel(self):
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.retry_count < self.max_retries
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """从字典创建"""
        data = data.copy()
        data["status"] = TaskStatus(data["status"])
        data["priority"] = TaskPriority(data["priority"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        
        return cls(**data)


@dataclass
class TaskResult:
    """
    任务结果类
    
    属性:
        task_id: 任务 ID
        agent_id: 执行 Agent ID
        success: 是否成功
        result: 结果数据
        error: 错误信息
        execution_time: 执行时间（秒）
        created_at: 创建时间
    """
    task_id: str
    agent_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TaskResult":
        """从字典创建"""
        data = data.copy()
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)
