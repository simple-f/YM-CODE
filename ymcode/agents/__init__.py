#!/usr/bin/env python3
# Comment
"""
YM-CODE 澶?Agent 绯荤粺
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
    """鍒涘缓榛樿璺敱鍣紙鍖呭惈 Builder 鍜?Reviewer锛?""
    router = AgentRouter()
    
    # Comment
    router.register_agent("builder", BuilderAgent())
    router.register_agent("reviewer", ReviewerAgent())
    
    return router


def create_persistent_router() -> tuple:
    """鍒涘缓甯︽寔涔呭寲鐨勮矾鐢卞櫒"""
    router = create_default_router()
    store = MemoryStore()
    return router, store
