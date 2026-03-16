#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 模型调用

兼容现有 DashScope、OpenAI 等 API
"""

import os
import logging
from typing import Dict, Optional, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class APIModel:
    """
    API 模型调用
    
    支持 DashScope、OpenAI 等 API
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化 API 模型
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('DASHSCOPE_API_KEY')
        self.model_name = self.config.get('model', 'qwen3.5-plus')
        self.base_url = self.config.get('base_url', 'https://api.dashscope.cn')
        
        logger.info(f"API 模型初始化：{self.model_name}")
    
    def chat(self, prompt: str, context: Optional[Any] = None) -> str:
        """
        聊天接口
        
        参数:
            prompt: 用户提示
            context: 上下文信息
        
        返回:
            AI 响应
        """
        try:
            # 调用 DashScope API
            import dashscope
            from dashscope import Generation
            
            dashscope.api_key = self.api_key
            
            # 构建消息
            messages = self._build_messages(prompt, context)
            
            # 调用 API
            response = Generation.call(
                model=self.model_name,
                messages=messages
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                logger.error(f"API 调用失败：{response.code} - {response.message}")
                return f"API 调用失败：{response.message}"
        
        except Exception as e:
            logger.error(f"API 调用异常：{e}")
            return f"API 调用异常：{str(e)}"
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        参数:
            prompt: 提示文本
            **kwargs: 其他参数
        
        返回:
            生成的文本
        """
        return self.chat(prompt)
    
    def _build_messages(self, prompt: str, context: Optional[Any] = None) -> list:
        """
        构建消息列表
        
        参数:
            prompt: 用户提示
            context: 上下文信息
        
        返回:
            消息列表
        """
        messages = []
        
        # 添加系统消息
        messages.append({
            'role': 'system',
            'content': '你是一个专业的 AI 编程助手。'
        })
        
        # 添加上下文（如果有）
        if context:
            if isinstance(context, list):
                for msg in context:
                    messages.append(msg)
            elif isinstance(context, dict):
                messages.append(context)
        
        # 添加用户消息
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        return messages
    
    def get_info(self) -> Dict:
        """
        获取模型信息
        
        返回:
            模型信息字典
        """
        return {
            'type': 'api',
            'model': self.model_name,
            'base_url': self.base_url
        }
