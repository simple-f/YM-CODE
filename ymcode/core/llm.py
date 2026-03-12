#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Client - LLM 客户端

融合课程：s01 (Agent Loop)
支持：Anthropic Claude, OpenAI, OpenAI 兼容接口（百炼 GLM 等）
"""

import os
import logging
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    stop_reason: str
    usage: Dict = None
    tools: Optional[List[Dict]] = None


class LLMClient:
    """LLM 客户端"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 LLM 客户端
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.mock_mode = False
        
        # 检查 OpenAI API Key（支持兼容接口）
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        # 如果没有配置 API Key，使用模拟模式
        if not self.api_key:
            logger.warning("OPENAI_API_KEY 未配置，将使用模拟模式")
            self.mock_mode = True
        else:
            # 动态导入 OpenAI
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info(f"使用模型：{self.model} (base_url: {self.base_url})")
            except ImportError:
                logger.warning("openai 库未安装，将使用模拟模式")
                self.mock_mode = True
        
        # 最大 token 数
        self.max_tokens = self.config.get("max_tokens", 4000)
    
    async def chat(self, messages: List[Dict], tools: List[Dict] = None) -> LLMResponse:
        """
        聊天接口
        
        参数:
            messages: 消息列表
            tools: 工具定义列表（可选）
        
        返回:
            LLM 响应
        """
        if self.mock_mode:
            return self._mock_chat(messages)
        
        try:
            # 转换为 OpenAI 格式
            openai_messages = []
            for msg in messages:
                role = "assistant" if msg["role"] == "assistant" else "user"
                content = msg["content"]
                if isinstance(content, list):
                    # 处理工具结果
                    content = str(content)
                openai_messages.append({"role": role, "content": content})
            
            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": openai_messages,
                "max_tokens": self.max_tokens
            }
            
            # 如果有工具定义，添加到请求中
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # 调用 OpenAI API（或兼容接口）
            response = await self.client.chat.completions.create(**request_params)
            
            # 检查是否有工具调用
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # 有工具调用
                tool_calls = []
                for tc in message.tool_calls:
                    tool_calls.append({
                        "name": tc.function.name,
                        "input": json.loads(tc.function.arguments) if tc.function.arguments else {}
                    })
                
                return LLMResponse(
                    content="",
                    stop_reason="tool_use",
                    tools=tool_calls,
                    usage={
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens
                    }
                )
            else:
                # 普通文本响应
                return LLMResponse(
                    content=message.content or "",
                    stop_reason="stop",
                    usage={
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens
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
