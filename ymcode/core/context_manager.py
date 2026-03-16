#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文管理器

支持长上下文自动处理、压缩、分片
"""

import logging
from typing import List, Dict, Any, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContextManager:
    """
    上下文管理器
    
    自动处理长上下文，支持压缩和分片
    """
    
    def __init__(self, max_tokens: int = 8000):
        """
        初始化上下文管理器
        
        参数:
            max_tokens: 最大 token 数
        """
        self.max_tokens = max_tokens
        self.compression_threshold = int(max_tokens * 0.8)
        
        logger.info(f"上下文管理器初始化 (max_tokens={max_tokens})")
    
    def process(self, context: Any) -> Any:
        """
        处理上下文
        
        参数:
            context: 原始上下文
        
        返回:
            处理后的上下文
        """
        if not context:
            return context
        
        token_count = self._count_tokens(context)
        
        if token_count > self.max_tokens:
            logger.info(f"上下文超长 ({token_count}/{self.max_tokens})，开始优化")
            return self._optimize_context(context, token_count)
        else:
            return context
    
    def _optimize_context(self, context: Any, token_count: int) -> Any:
        """
        优化上下文
        
        参数:
            context: 原始上下文
            token_count: token 数量
        
        返回:
            优化后的上下文
        """
        # 1. 尝试压缩
        compressed = self._compress_context(context)
        compressed_count = self._count_tokens(compressed)
        
        if compressed_count <= self.max_tokens:
            logger.info(f"压缩成功：{token_count} -> {compressed_count} tokens")
            return compressed
        
        # 2. 分片处理
        chunks = self._split_context(context)
        logger.info(f"分片处理：{len(chunks)} 个片段")
        return chunks
    
    def _compress_context(self, context: Any) -> Any:
        """
        压缩上下文
        
        保留关键信息，移除冗余内容
        
        参数:
            context: 原始上下文
        
        返回:
            压缩后的上下文
        """
        if isinstance(context, list):
            return self._compress_list_context(context)
        elif isinstance(context, str):
            return self._compress_text_context(context)
        else:
            return context
    
    def _compress_list_context(self, context: List) -> List:
        """压缩列表形式的上下文"""
        compressed = []
        
        for item in context:
            # 保留系统消息和用户消息
            if isinstance(item, dict):
                role = item.get('role', '')
                if role in ['system', 'user']:
                    compressed.append(item)
                elif role == 'assistant':
                    # 压缩助手消息，保留关键内容
                    content = item.get('content', '')
                    if len(content) > 200:
                        # 截断长消息
                        compressed_content = content[:200] + '...'
                        compressed.append({
                            'role': 'assistant',
                            'content': compressed_content
                        })
                    else:
                        compressed.append(item)
            else:
                compressed.append(item)
        
        return compressed
    
    def _compress_text_context(self, context: str) -> str:
        """压缩文本形式的上下文"""
        # 简单实现：截断
        if len(context) > self.max_tokens * 4:  # 粗略估计
            return context[:self.max_tokens * 4] + '...'
        return context
    
    def _split_context(self, context: Any) -> List:
        """
        分片处理上下文
        
        参数:
            context: 原始上下文
        
        返回:
            分片后的上下文列表
        """
        if isinstance(context, list):
            return self._split_list_context(context)
        elif isinstance(context, str):
            return self._split_text_context(context)
        else:
            return [context]
    
    def _split_list_context(self, context: List) -> List[List]:
        """分片处理列表上下文"""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for item in context:
            item_tokens = self._count_tokens(item)
            
            if current_tokens + item_tokens > self.max_tokens:
                # 当前片段已满，开始新片段
                chunks.append(current_chunk)
                current_chunk = [item]
                current_tokens = item_tokens
            else:
                current_chunk.append(item)
                current_tokens += item_tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_text_context(self, context: str) -> List[str]:
        """分片处理文本上下文"""
        chunks = []
        chunk_size = self.max_tokens * 4  # 粗略估计
        
        for i in range(0, len(context), chunk_size):
            chunk = context[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def _count_tokens(self, context: Any) -> int:
        """
        估算 token 数量
        
        参数:
            context: 上下文
        
        返回:
            token 数量
        """
        if isinstance(context, list):
            return sum(self._count_tokens(item) for item in context)
        elif isinstance(context, dict):
            content = context.get('content', '')
            return len(content) // 4  # 粗略估计
        elif isinstance(context, str):
            return len(context) // 4
        else:
            return 0


# 便捷函数
_default_context_manager: Optional[ContextManager] = None

def get_context_manager(max_tokens: int = 8000) -> ContextManager:
    """
    获取全局上下文管理器实例
    
    参数:
        max_tokens: 最大 token 数
    
    返回:
        ContextManager 实例
    """
    global _default_context_manager
    if _default_context_manager is None:
        _default_context_manager = ContextManager(max_tokens)
    return _default_context_manager


def process_context(context: Any, max_tokens: int = 8000) -> Any:
    """
    便捷处理上下文函数
    
    参数:
        context: 原始上下文
        max_tokens: 最大 token 数
    
    返回:
        处理后的上下文
    """
    manager = get_context_manager(max_tokens)
    return manager.process(context)
