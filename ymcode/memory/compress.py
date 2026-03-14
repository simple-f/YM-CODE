#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Compressor - 上下文压缩器
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CompressionResult:
    """压缩结果"""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    summary: str
    preserved_items: List[Dict]


class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, compression_threshold: float = 0.8):
        """
        初始化压缩器
        
        参数:
            compression_threshold: 压缩阈值（超过此比例触发压缩）
        """
        self.compression_threshold = compression_threshold
        self.compression_history: List[Dict] = []
        
        logger.info(f"上下文压缩器初始化完成（threshold={compression_threshold}）")
    
    def should_compress(self, current_tokens: int, max_tokens: int) -> bool:
        """
        判断是否需要压缩
        
        参数:
            current_tokens: 当前 token 数
            max_tokens: 最大 token 数
        
        返回:
            是否需要压缩
        """
        usage_ratio = current_tokens / max_tokens if max_tokens > 0 else 0
        return usage_ratio > self.compression_threshold
    
    def compress_messages(self, messages: List[Dict], target_tokens: int = None) -> CompressionResult:
        """
        压缩消息列表
        
        参数:
            messages: 消息列表
            target_tokens: 目标 token 数
        
        返回:
            压缩结果
        """
        if not messages:
            return CompressionResult(
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=0,
                summary="",
                preserved_items=[]
            )
        
        # 计算原始 token 数
        original_tokens = sum(len(m.get('content', '')) // 4 for m in messages)
        
        # 策略 1：保留最近的消息
        preserved = self._preserve_recent_messages(messages, target_tokens)
        
        # 策略 2：压缩早期消息为摘要
        summary = self._summarize_early_messages(messages, preserved)
        
        # 计算压缩后的 token 数
        compressed_tokens = sum(len(m.get('content', '')) // 4 for m in preserved)
        compressed_tokens += len(summary) // 4
        
        # 计算压缩率
        compression_ratio = 1 - (compressed_tokens / original_tokens) if original_tokens > 0 else 0
        
        result = CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            summary=summary,
            preserved_items=preserved
        )
        
        # 记录压缩历史
        self.compression_history.append({
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'compression_ratio': compression_ratio,
            'message_count': len(messages),
            'preserved_count': len(preserved)
        })
        
        logger.info(f"压缩完成：{original_tokens} -> {compressed_tokens} tokens ({compression_ratio:.1%} 压缩率)")
        
        return result
    
    def _preserve_recent_messages(self, messages: List[Dict], target_tokens: int = None) -> List[Dict]:
        """
        保留最近的消息
        
        参数:
            messages: 消息列表
            target_tokens: 目标 token 数
        
        返回:
            保留的消息列表
        """
        if target_tokens is None:
            target_tokens = 2000  # 默认保留最近 2000 tokens
        
        preserved = []
        current_tokens = 0
        
        # 从后向前遍历，保留最近的消息
        for message in reversed(messages):
            message_tokens = len(message.get('content', '')) // 4
            
            if current_tokens + message_tokens <= target_tokens:
                preserved.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        logger.debug(f"保留 {len(preserved)} 条最近消息，{current_tokens} tokens")
        
        return preserved
    
    def _summarize_early_messages(self, messages: List[Dict], preserved: List[Dict]) -> str:
        """
        摘要早期消息
        
        参数:
            messages: 完整消息列表
            preserved: 保留的消息列表
        
        返回:
            摘要文本
        """
        # 找出被压缩的消息
        preserved_ids = set(id(m) for m in preserved)
        early_messages = [m for m in messages if id(m) not in preserved_ids]
        
        if not early_messages:
            return ""
        
        # 简单摘要：统计消息数量和类型
        user_messages = sum(1 for m in early_messages if m.get('role') == 'user')
        assistant_messages = sum(1 for m in early_messages if m.get('role') == 'assistant')
        
        summary_parts = [
            f"[早期对话摘要]",
            f"共 {len(early_messages)} 条消息",
            f"用户：{user_messages} 条",
            f"助手：{assistant_messages} 条",
            f"[详细内容已压缩以节省空间]"
        ]
        
        summary = "\n".join(summary_parts)
        
        logger.debug(f"摘要早期消息：{len(early_messages)} 条 -> {len(summary)} 字符")
        
        return summary
    
    def compress_by_type(self, items: List[Dict], item_type: str) -> str:
        """
        按类型压缩项目
        
        参数:
            items: 项目列表
            item_type: 项目类型
        
        返回:
            压缩后的文本
        """
        filtered = [i for i in items if i.get('type') == item_type]
        
        if not filtered:
            return ""
        
        if item_type == 'file':
            # 文件：只保留路径和摘要
            paths = [i.get('metadata', {}).get('path', 'unknown') for i in filtered]
            return f"[已加载 {len(filtered)} 个文件：{', '.join(paths)}]"
        
        elif item_type == 'code':
            # 代码：只保留语言和行数
            code_info = []
            for item in filtered:
                lang = item.get('metadata', {}).get('language', 'unknown')
                lines = item.get('content', '').count('\n') + 1
                code_info.append(f"{lang} ({lines}行)")
            return f"[已分析代码：{', '.join(code_info)}]"
        
        elif item_type == 'summary':
            # 摘要：合并所有摘要
            summaries = [i.get('content', '') for i in filtered]
            return "\n".join(summaries)
        
        return ""
    
    def get_compression_stats(self) -> Dict:
        """获取压缩统计"""
        if not self.compression_history:
            return {
                'total_compressions': 0,
                'average_ratio': 0,
                'total_tokens_saved': 0
            }
        
        total_compressions = len(self.compression_history)
        average_ratio = sum(h['compression_ratio'] for h in self.compression_history) / total_compressions
        total_tokens_saved = sum(
            h['original_tokens'] - h['compressed_tokens']
            for h in self.compression_history
        )
        
        return {
            'total_compressions': total_compressions,
            'average_ratio': average_ratio,
            'total_tokens_saved': total_tokens_saved,
            'recent_compressions': self.compression_history[-5:]
        }
    
    def clear_history(self) -> None:
        """清空压缩历史"""
        self.compression_history.clear()
        logger.info("清空压缩历史")
