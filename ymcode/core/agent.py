#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent - 核心引擎

融合课程：s01 (Agent Loop) + s09 (Agent Teams)
"""

import logging
from typing import List, Dict, Optional

from .llm import LLMClient
from .state import StateManager
from ..tools.registry import ToolRegistry
from ..memory.session import SessionManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Agent:
    """AI Agent 核心类"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 Agent
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.llm = LLMClient(self.config)
        self.tools = ToolRegistry()
        self.memory = SessionManager(self.config)
        self.state = StateManager()
        
        logger.info(f"Agent 初始化完成，加载 {len(self.tools)} 个工具")
    
    async def run(self, user_input: str, session_id: str = "default") -> str:
        """
        运行 Agent 循环
        
        参数:
            user_input: 用户输入
            session_id: 会话 ID
        
        返回:
            Agent 回答
        """
        logger.info(f"开始处理：{user_input[:50]}...")
        
        # 加载会话
        messages = self.memory.get_session(session_id)
        messages.append({"role": "user", "content": user_input})
        
        # 循环
        max_iterations = self.config.get("max_iterations", 30)
        
        for iteration in range(max_iterations):
            logger.debug(f"第 {iteration + 1} 轮")
            
            # 调用 LLM
            response = await self.llm.chat(messages)
            messages.append({"role": "assistant", "content": response.content})
            
            # 检查是否完成
            if response.stop_reason != "tool_use":
                logger.info(f"完成，迭代 {iteration + 1} 轮")
                return response.text
            
            # 执行工具
            results = await self.tools.execute(response.tools)
            messages.append({"role": "user", "content": results})
        
        logger.warning(f"达到最大迭代次数 ({max_iterations})")
        return "抱歉，任务过于复杂，已达到最大迭代次数。"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "tools_loaded": len(self.tools),
            "active_sessions": len(self.memory.sessions),
            "state": self.state.get_current_state()
        }
