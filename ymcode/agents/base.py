#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 基类
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Agent 消息"""
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """从字典创建"""
        return cls(
            sender=data.get("sender", "unknown"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory: List[Dict] = []  # 短期记忆
        self.state = "idle"  # idle, busy, error
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentMessage:
        """处理消息"""
        pass
    
    def add_to_memory(self, message: str, metadata: Dict = None):
        """添加到短期记忆"""
        self.memory.append({
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近 100 条
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
    
    def get_memory(self, limit: int = 10) -> List[Dict]:
        """获取最近记忆"""
        return self.memory[-limit:]
    
    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "memory_count": len(self.memory),
            "created_at": self.created_at
        }
    
    def __repr__(self) -> str:
        return f"Agent({self.name}, {self.role}, {self.state})"
