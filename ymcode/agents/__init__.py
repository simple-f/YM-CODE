#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 多 Agent 系统
"""

from .base import BaseAgent, AgentMessage
from .router import AgentRouter
from .builder import BuilderAgent
from .reviewer import ReviewerAgent
from .memory_store import MemoryStore

__all__ = [
    'BaseAgent',
    'AgentMessage',
    'AgentRouter',
    'BuilderAgent',
    'ReviewerAgent',
    'MemoryStore',
]


def create_default_router() -> AgentRouter:
    """创建默认路由器（包含 Builder 和 Reviewer）"""
    router = AgentRouter()
    
    # 注册默认 Agent
    router.register_agent("builder", BuilderAgent())
    router.register_agent("reviewer", ReviewerAgent())
    
    return router


def create_persistent_router() -> tuple:
    """创建带持久化的路由器"""
    router = create_default_router()
    store = MemoryStore()
    return router, store
