#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager - 会话管理器
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Session:
    """会话数据"""
    id: str
    created_at: str
    updated_at: str
    messages: List[Dict]
    metadata: Dict
    token_count: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """从字典创建"""
        return cls(**data)


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_path: str = None):
        """
        初始化会话管理器
        
        参数:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path) if storage_path else Path.home() / '.ymcode' / 'sessions'
        self.sessions: Dict[str, Session] = {}
        self.current_session_id: Optional[str] = None
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载已有会话
        self._load_sessions()
        
        logger.info(f"会话管理器初始化完成：{self.storage_path}")
    
    def _load_sessions(self) -> None:
        """加载会话"""
        if not self.storage_path.exists():
            return
        
        for file in self.storage_path.glob('*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    self.sessions[session.id] = session
            except Exception as e:
                logger.warning(f"加载会话失败 {file}: {e}")
        
        logger.info(f"加载 {len(self.sessions)} 个会话")
    
    def create_session(self, metadata: Dict = None) -> Session:
        """
        创建新会话
        
        参数:
            metadata: 元数据
        
        返回:
            会话对象
        """
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session = Session(
            id=session_id,
            created_at=now,
            updated_at=now,
            messages=[],
            metadata=metadata or {},
            token_count=0
        )
        
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        # 保存到文件
        self._save_session(session)
        
        logger.info(f"创建新会话：{session_id}")
        
        return session
    
    def get_session(self, session_id: str = None) -> Optional[Session]:
        """
        获取会话
        
        参数:
            session_id: 会话 ID（可选，默认当前会话）
        
        返回:
            会话对象
        """
        sid = session_id or self.current_session_id
        return self.sessions.get(sid)
    
    def get_current_session(self) -> Optional[Session]:
        """获取当前会话"""
        return self.get_session(self.current_session_id)
    
    def add_message(self, role: str, content: str, session_id: str = None) -> None:
        """
        添加消息
        
        参数:
            role: 角色（user/assistant/system）
            content: 内容
            session_id: 会话 ID
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在：{session_id}")
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()
        
        # 估算 token 数（简单按字符数/4 计算）
        session.token_count += len(content) // 4
        
        # 保存到文件
        self._save_session(session)
        
        logger.debug(f"添加消息到会话 {session.id}: {role}")
    
    def get_messages(self, session_id: str = None, limit: int = None) -> List[Dict]:
        """
        获取消息列表
        
        参数:
            session_id: 会话 ID
            limit: 限制数量
        
        返回:
            消息列表
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_messages(self, session_id: str = None) -> None:
        """
        清空消息
        
        参数:
            session_id: 会话 ID
        """
        session = self.get_session(session_id)
        if not session:
            return
        
        session.messages = []
        session.token_count = 0
        session.updated_at = datetime.now().isoformat()
        
        self._save_session(session)
        
        logger.info(f"清空会话消息：{session.id}")
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        参数:
            session_id: 会话 ID
        
        返回:
            是否成功
        """
        if session_id not in self.sessions:
            return False
        
        del self.sessions[session_id]
        
        # 删除文件
        file_path = self.storage_path / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
        
        # 如果删除的是当前会话，清除当前会话 ID
        if self.current_session_id == session_id:
            self.current_session_id = None
        
        logger.info(f"删除会话：{session_id}")
        
        return True
    
    def list_sessions(self) -> List[Dict]:
        """
        列出所有会话
        
        返回:
            会话信息列表
        """
        sessions_info = []
        
        for session in sorted(
            self.sessions.values(),
            key=lambda s: s.updated_at,
            reverse=True
        ):
            sessions_info.append({
                'id': session.id,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'message_count': len(session.messages),
                'token_count': session.token_count,
                'is_current': session.id == self.current_session_id
            })
        
        return sessions_info
    
    def _save_session(self, session: Session) -> None:
        """保存会话到文件"""
        file_path = self.storage_path / f"{session.id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存会话失败：{e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        total_tokens = sum(s.token_count for s in self.sessions.values())
        
        return {
            'total_sessions': len(self.sessions),
            'total_messages': total_messages,
            'total_tokens': total_tokens,
            'current_session': self.current_session_id
        }
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        清理旧会话
        
        参数:
            days: 保留天数
        
        返回:
            删除的会话数
        """
        deleted = 0
        now = datetime.now()
        
        for session_id in list(self.sessions.keys()):
            session = self.sessions[session_id]
            updated = datetime.fromisoformat(session.updated_at)
            age = (now - updated).days
            
            if age > days:
                self.delete_session(session_id)
                deleted += 1
        
        logger.info(f"清理 {deleted} 个旧会话（>{days}天）")
        
        return deleted
