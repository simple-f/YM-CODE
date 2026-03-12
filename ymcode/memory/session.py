#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager - Session 管理

融合课程：s03 (TodoWrite)
"""

import logging
from typing import Dict, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Session 管理器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 Session 管理器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.sessions: Dict[str, List[Dict]] = {}
    
    def get_session(self, session_id: str) -> List[Dict]:
        """
        获取会话
        
        参数:
            session_id: 会话 ID
        
        返回:
            消息列表
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"创建新会话：{session_id}")
        
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        添加消息
        
        参数:
            session_id: 会话 ID
            role: 角色
            content: 内容
        """
        session = self.get_session(session_id)
        session.append({"role": role, "content": content})
    
    def clear_session(self, session_id: str):
        """
        清空会话
        
        参数:
            session_id: 会话 ID
        """
        if session_id in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"清空会话：{session_id}")
    
    def __len__(self) -> int:
        """返回会话数量"""
        return len(self.sessions)
