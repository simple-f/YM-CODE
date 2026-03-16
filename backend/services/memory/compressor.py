#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Compressor - 上下文压缩

融合课程：s06 (Context Compact)
"""

import logging
from typing import List, Dict
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化压缩器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.max_messages = self.config.get("max_messages", 100)
    
    def needs_compact(self, messages: List[Dict]) -> bool:
        """
        检查是否需要压缩
        
        参数:
            messages: 消息列表
        
        返回:
            是否需要压缩
        """
        return len(messages) > self.max_messages
    
    async def auto_compact(self, messages: List[Dict]) -> List[Dict]:
        """
        自动压缩
        
        参数:
            messages: 消息列表
        
        返回:
            压缩后的消息列表
        """
        logger.info(f"压缩上下文：{len(messages)} -> {self.max_messages}")
        
        # 简单实现：保留最近的消息
        # TODO: 实现智能压缩（LLM 总结）
        return messages[-self.max_messages:]
