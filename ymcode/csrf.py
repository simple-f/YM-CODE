#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF 防护模块

提供 CSRF Token 生成和验证功能
"""

import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta

class CSRFProtect:
    """CSRF 防护类"""
    
    def __init__(self):
        """初始化 CSRF 防护"""
        self.tokens: dict = {}  # token -> {user_id, expires}
        self.token_expire_hours = 2
    
    def generate_token(self, user_id: str) -> str:
        """
        生成 CSRF Token
        
        参数:
            user_id: 用户 ID
        
        返回:
            CSRF Token 字符串
        """
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=self.token_expire_hours)
        
        self.tokens[token] = {
            'user_id': user_id,
            'expires': expires
        }
        
        return token
    
    def validate_token(self, token: str, user_id: str) -> bool:
        """
        验证 CSRF Token
        
        参数:
            token: CSRF Token
            user_id: 用户 ID
        
        返回:
            是否有效
        """
        if token not in self.tokens:
            return False
        
        token_data = self.tokens[token]
        
        # 检查用户 ID 是否匹配
        if token_data['user_id'] != user_id:
            return False
        
        # 检查是否过期
        if datetime.utcnow() > token_data['expires']:
            del self.tokens[token]
            return False
        
        return True
    
    def revoke_token(self, token: str) -> None:
        """
        撤销 Token
        
        参数:
            token: CSRF Token
        """
        if token in self.tokens:
            del self.tokens[token]
    
    def cleanup_expired(self) -> int:
        """
        清理过期 Token
        
        返回:
            清理的 Token 数量
        """
        now = datetime.utcnow()
        expired = [t for t, d in self.tokens.items() if now > d['expires']]
        
        for token in expired:
            del self.tokens[token]
        
        return len(expired)


# 全局 CSRF 防护实例
_csrf_instance: Optional[CSRFProtect] = None

def get_csrf() -> CSRFProtect:
    """获取全局 CSRF 防护实例"""
    global _csrf_instance
    if _csrf_instance is None:
        _csrf_instance = CSRFProtect()
    return _csrf_instance
