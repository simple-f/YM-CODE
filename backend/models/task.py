"""
任务模型

定义任务数据结构
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"       # 等待执行
    RUNNING = "running"       # 执行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消


class TaskResult(BaseModel):
    """任务结果"""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """任务模型"""
    id: str = Field(..., description="任务 ID")
    name: str = Field(..., description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    type: str = Field(default="general", description="任务类型")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    agent: Optional[str] = Field(None, description="执行的 Agent")
    plugins: List[str] = Field(default=[], description="使用的插件列表")
    params: Dict[str, Any] = Field(default={}, description="任务参数")
    result: Optional[TaskResult] = Field(None, description="执行结果")
    priority: int = Field(default=0, description="优先级")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        arbitrary_types_allowed = True
    
    def is_completed(self) -> bool:
        """判断任务是否完成"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def is_pending(self) -> bool:
        """判断任务是否等待执行"""
        return self.status == TaskStatus.PENDING
    
    def is_running(self) -> bool:
        """判断任务是否执行中"""
        return self.status == TaskStatus.RUNNING
