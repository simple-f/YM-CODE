"""
Agent 基类

所有 Agent 必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.task import Task, TaskResult


class BaseAgent(ABC):
    """Agent 基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 名称"""
        pass
    
    @property
    def description(self) -> str:
        """Agent 描述"""
        return ""
    
    @property
    def capabilities(self) -> list:
        """Agent 能力列表"""
        return []
    
    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """
        执行任务
        
        参数:
            task: 任务
        
        返回:
            执行结果
        """
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """
        判断是否能处理该类型的任务
        
        参数:
            task_type: 任务类型
        
        返回:
            是否能处理
        """
        return task_type in self.capabilities
    
    async def initialize(self) -> None:
        """初始化 Agent（可选）"""
        pass
    
    async def cleanup(self) -> None:
        """清理资源（可选）"""
        pass
