#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager - 上下文管理器
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ContextItem:
    """上下文项"""
    type: str  # message, file, code, summary
    content: str
    metadata: Dict = field(default_factory=dict)
    token_count: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'type': self.type,
            'content': self.content,
            'metadata': self.metadata,
            'token_count': self.token_count
        }


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_tokens: int = 4000):
        """
        初始化上下文管理器
        
        参数:
            max_tokens: 最大 token 数
        """
        self.max_tokens = max_tokens
        self.context_items: List[ContextItem] = []
        self.current_tokens = 0
        
        logger.info(f"上下文管理器初始化完成（max_tokens={max_tokens}）")
    
    def add_item(self, item_type: str, content: str, metadata: Dict = None) -> ContextItem:
        """
        添加上下文项
        
        参数:
            item_type: 类型
            content: 内容
            metadata: 元数据
        
        返回:
            上下文项
        """
        # 估算 token 数
        token_count = len(content) // 4
        
        item = ContextItem(
            type=item_type,
            content=content,
            metadata=metadata or {},
            token_count=token_count
        )
        
        self.context_items.append(item)
        self.current_tokens += token_count
        
        logger.debug(f"添加上下文项：{item_type}, {token_count} tokens")
        
        # 检查是否超出限制
        if self.current_tokens > self.max_tokens:
            logger.warning(f"上下文超出限制：{self.current_tokens}/{self.max_tokens}")
        
        return item
    
    def add_message(self, role: str, content: str) -> ContextItem:
        """
        添加消息
        
        参数:
            role: 角色（user/assistant/system）
            content: 内容
        
        返回:
            上下文项
        """
        return self.add_item(
            item_type='message',
            content=content,
            metadata={'role': role}
        )
    
    def add_file(self, path: str, content: str) -> ContextItem:
        """
        添加文件内容
        
        参数:
            path: 文件路径
            content: 文件内容
        
        返回:
            上下文项
        """
        return self.add_item(
            item_type='file',
            content=content,
            metadata={'path': path}
        )
    
    def add_code(self, language: str, code: str) -> ContextItem:
        """
        添加代码
        
        参数:
            language: 语言
            code: 代码
        
        返回:
            上下文项
        """
        return self.add_item(
            item_type='code',
            content=code,
            metadata={'language': language}
        )
    
    def add_summary(self, summary: str) -> ContextItem:
        """
        添加摘要
        
        参数:
            summary: 摘要内容
        
        返回:
            上下文项
        """
        return self.add_item(
            item_type='summary',
            content=summary
        )
    
    def get_items(self, limit: int = None, item_type: str = None) -> List[ContextItem]:
        """
        获取上下文项
        
        参数:
            limit: 限制数量
            item_type: 类型过滤
        
        返回:
            上下文项列表
        """
        items = self.context_items
        
        if item_type:
            items = [i for i in items if i.type == item_type]
        
        if limit:
            items = items[-limit:]
        
        return items
    
    def get_messages(self) -> List[Dict]:
        """获取消息列表"""
        messages = []
        for item in self.get_items(item_type='message'):
            messages.append({
                'role': item.metadata.get('role', 'user'),
                'content': item.content
            })
        return messages
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        summaries = self.get_items(item_type='summary')
        if not summaries:
            return ""
        
        return "\n".join([s.content for s in summaries])
    
    def remove_oldest(self, count: int = 1) -> int:
        """
        移除最旧的上下文项
        
        参数:
            count: 移除数量
        
        返回:
            移除的 token 数
        """
        removed_tokens = 0
        
        for _ in range(min(count, len(self.context_items))):
            if self.context_items:
                item = self.context_items.pop(0)
                removed_tokens += item.token_count
                self.current_tokens -= item.token_token
        
        logger.debug(f"移除 {count} 个最旧的上下文项，释放 {removed_tokens} tokens")
        
        return removed_tokens
    
    def remove_until_under_limit(self, target_tokens: int = None) -> int:
        """
        移除直到低于限制
        
        参数:
            target_tokens: 目标 token 数（默认 max_tokens 的 80%）
        
        返回:
            移除的 token 数
        """
        if target_tokens is None:
            target_tokens = int(self.max_tokens * 0.8)
        
        removed_tokens = 0
        
        while self.current_tokens > target_tokens and self.context_items:
            item = self.context_items.pop(0)
            removed_tokens += item.token_count
            self.current_tokens -= item.token_count
        
        logger.info(f"移除上下文项直到 {target_tokens} tokens，释放 {removed_tokens} tokens")
        
        return removed_tokens
    
    def clear(self) -> None:
        """清空上下文"""
        self.context_items.clear()
        self.current_tokens = 0
        logger.info("清空上下文")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        type_counts = {}
        for item in self.context_items:
            type_counts[item.type] = type_counts.get(item.type, 0) + 1
        
        return {
            'total_items': len(self.context_items),
            'total_tokens': self.current_tokens,
            'max_tokens': self.max_tokens,
            'usage_percent': (self.current_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0,
            'by_type': type_counts
        }
    
    def is_near_limit(self, threshold: float = 0.8) -> bool:
        """
        检查是否接近限制
        
        参数:
            threshold: 阈值（0-1）
        
        返回:
            是否接近限制
        """
        return self.current_tokens > (self.max_tokens * threshold)
    
    def get_available_tokens(self) -> int:
        """获取可用 token 数"""
        return max(0, self.max_tokens - self.current_tokens)
