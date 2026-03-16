#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 认证模块

提供 JWT Token 生成和验证功能
"""

import jwt
import datetime
from typing import Optional, Dict
from pathlib import Path

class JWTAuth:
    """JWT 认证类"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化 JWT 认证
        
        参数:
            secret_key: 密钥（不提供则从环境变量读取）
        """
        import os
        self.secret_key = secret_key or os.getenv('YM_CODE_JWT_SECRET', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expire_hours = 24
    
    def create_token(self, user_id: str, username: str, role: str = 'user') -> str:
        """
        创建 JWT Token
        
        参数:
            user_id: 用户 ID
            username: 用户名
            role: 用户角色（user/admin）
        
        返回:
            JWT Token 字符串
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_expire_hours),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Dict:
        """
        验证 JWT Token
        
        参数:
            token: JWT Token 字符串
        
        返回:
            解析后的 payload
        
        异常:
            jwt.ExpiredSignatureError: Token 过期
            jwt.InvalidTokenError: Token 无效
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError('Token 已过期')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'无效的 Token: {str(e)}')
    
    def refresh_token(self, token: str) -> str:
        """
        刷新 Token
        
        参数:
            token: 当前 Token
        
        返回:
            新的 Token
        """
        payload = self.verify_token(token)
        return self.create_token(
            user_id=payload['user_id'],
            username=payload['username'],
            role=payload['role']
        )


# 全局认证实例
_auth_instance: Optional[JWTAuth] = None

def get_auth() -> JWTAuth:
    """获取全局认证实例"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = JWTAuth()
    return _auth_instance
