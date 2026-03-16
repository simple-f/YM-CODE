"""
Agent Message

Message structure for agent communication
"""

from typing import Dict, Any, Optional
from datetime import datetime


class AgentMessage:
    """Agent message class"""
    
    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Any,
        metadata: Optional[Dict] = None
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        """Create from dictionary"""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=data["message_type"],
            content=data["content"],
            metadata=data.get("metadata", {})
        )
