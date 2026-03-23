#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 消息定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


@dataclass
class AgentMessage:
    """
    Agent 消息类
    
    用于 Agent 之间的通信
    
    属性:
        id: 消息唯一标识
        sender: 发送者
        content: 消息内容
        metadata: 元数据
        timestamp: 时间戳
    """
    sender: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "sender": self.sender,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        """从字典创建"""
        data = data.copy()
        if data.get("timestamp"):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
