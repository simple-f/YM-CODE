"""
Agent Base

All agents must inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

try:
    from .message import AgentMessage
except ImportError:
    AgentMessage = None


class BaseAgent(ABC):
    """Agent base class"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name"""
        pass
    
    @property
    def description(self) -> str:
        """Agent description"""
        return ""
    
    @property
    def capabilities(self) -> list:
        """Agent capabilities"""
        return []
    
    @abstractmethod
    async def execute(self, task) -> Any:
        """
        Execute task
        
        Args:
            task: Task to execute
        
        Returns:
            Execution result
        """
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """
        Check if can handle task type
        
        Args:
            task_type: Task type
        
        Returns:
            True if can handle
        """
        return task_type in self.capabilities
    
    async def initialize(self) -> None:
        """Initialize agent (optional)"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources (optional)"""
        pass
