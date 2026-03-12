#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Client - LLM 客户端

融合课程：s01 (Agent Loop)
"""

import os
import logging
from typing import List, Dict
from dataclasses import dataclass

from anthropic import AsyncAnthropic
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    stop_reason: str
    usage: Dict = None


class LLMClient:
    """LLM 客户端"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 LLM 客户端
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        
        # 获取 API Key
        api_key = self.config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY 未配置，将使用模拟模式")
            self.mock_mode = True
        else:
            self.mock_mode = False
            self.client = AsyncAnthropic(api_key=api_key)
        
        # 模型配置
        self.model = self.config.get("model", "claude-3-5-sonnet-20241022")
        self.max_tokens = self.config.get("max_tokens", 8000)
    
    async def chat(self, messages: List[Dict]) -> LLMResponse:
        """
        聊天接口
        
        参数:
            messages: 消息列表
        
        返回:
            LLM 响应
        """
        if self.mock_mode:
            return self._mock_chat(messages)
        
        try:
            # 调用 Anthropic API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages
            )
            
            return LLMResponse(
                content=response.content[0].text,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"LLM 调用失败：{e}", exc_info=True)
            raise
    
    def _mock_chat(self, messages: List[Dict]) -> LLMResponse:
        """模拟聊天（用于测试）"""
        logger.warning("使用模拟响应")
        
        # 简单响应
        last_message = messages[-1]["content"] if messages else ""
        
        return LLMResponse(
            content=f"[模拟响应] 收到：{last_message[:100]}",
            stop_reason="end_turn"
        )
