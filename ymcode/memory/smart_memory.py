#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Memory Manager - 智能记忆管理器

功能：
- 基于窗口的记忆存储（滑动窗口）
- 重要性评分（自动 + 手动）
- 分类存储（工作记忆/长期记忆/归档记忆）
- 按需加载（基于相关性和重要性）
- 自动压缩和清理

设计原则：
1. 工作记忆：最近 N 条消息，快速访问
2. 长期记忆：重要事件，基于重要性评分
3. 归档记忆：压缩后的历史，节省空间
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MemoryType(str, Enum):
    """记忆类型"""
    WORKING = "working"      # 工作记忆（最近消息）
    LONG_TERM = "long_term"  # 长期记忆（重要事件）
    ARCHIVED = "archived"    # 归档记忆（压缩历史）


class ImportanceLevel(int, Enum):
    """重要性等级"""
    LOW = 1       # 低优先级
    MEDIUM = 2    # 中优先级
    HIGH = 3      # 高优先级
    CRITICAL = 4  # 关键信息


@dataclass
class Memory:
    """记忆单元"""
    id: str
    content: str
    memory_type: MemoryType
    importance: ImportanceLevel
    created_at: str
    updated_at: str
    metadata: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    access_count: int = 0  # 访问次数
    last_accessed: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata,
            'tags': self.tags,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """从字典创建"""
        data['memory_type'] = MemoryType(data['memory_type'])
        data['importance'] = ImportanceLevel(data['importance'])
        return cls(**data)


@dataclass
class MemoryConfig:
    """记忆配置"""
    working_window_size: int = 50        # 工作记忆窗口大小（消息数）
    working_max_tokens: int = 4000       # 工作记忆最大 token 数
    long_term_threshold: int = 3         # 长期记忆重要性阈值（>=3 存入长期）
    archive_after_days: int = 7          # 7 天后归档
    max_long_term_memories: int = 1000   # 长期记忆最大数量
    max_archived_memories: int = 10000   # 归档记忆最大数量
    auto_compact_enabled: bool = True    # 自动压缩
    compression_threshold: float = 0.8   # 压缩阈值（80%）


class SmartMemoryManager:
    """
    智能记忆管理器
    
    用法:
        memory = SmartMemoryManager()
        await memory.add("用户说...", metadata={...})
        await memory.add("重要决策", importance=ImportanceLevel.HIGH)
        
        # 按需加载
        context = await memory.load_context(query="用户需求")
    """
    
    def __init__(
        self,
        storage_path: str = None,
        config: MemoryConfig = None
    ):
        """
        初始化记忆管理器
        
        Args:
            storage_path: 存储路径
            config: 配置
        """
        self.storage_path = Path(storage_path) if storage_path else Path.home() / '.ymcode' / 'memory'
        self.config = config or MemoryConfig()
        
        # 记忆存储
        self.working_memories: List[Memory] = []
        self.long_term_memories: Dict[str, Memory] = {}
        self.archived_memories: Dict[str, Memory] = {}
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载已有记忆
        self._load_memories()
        
        logger.info(f"智能记忆管理器初始化完成：{self.storage_path}")
        logger.info(f"配置：窗口={self.config.working_window_size}, 长期阈值={self.config.long_term_threshold}")
    
    def _load_memories(self) -> None:
        """加载记忆"""
        # 工作记忆
        working_file = self.storage_path / 'working.json'
        if working_file.exists():
            try:
                with open(working_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.working_memories = [Memory.from_dict(m) for m in data]
                logger.info(f"加载 {len(self.working_memories)} 条工作记忆")
            except Exception as e:
                logger.warning(f"加载工作记忆失败：{e}")
        
        # 长期记忆
        long_term_file = self.storage_path / 'long_term.json'
        if long_term_file.exists():
            try:
                with open(long_term_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.long_term_memories = {m['id']: Memory.from_dict(m) for m in data}
                logger.info(f"加载 {len(self.long_term_memories)} 条长期记忆")
            except Exception as e:
                logger.warning(f"加载长期记忆失败：{e}")
    
    def _save_memories(self) -> None:
        """保存记忆"""
        # 保存工作记忆
        working_file = self.storage_path / 'working.json'
        with open(working_file, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in self.working_memories], f, ensure_ascii=False, indent=2)
        
        # 保存长期记忆
        long_term_file = self.storage_path / 'long_term.json'
        with open(long_term_file, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in self.long_term_memories.values()], f, ensure_ascii=False, indent=2)
    
    async def add(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        importance: ImportanceLevel = None,
        metadata: Dict = None,
        tags: List[str] = None
    ) -> Memory:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性等级（自动评估如果为 None）
            metadata: 元数据
            tags: 标签
        
        Returns:
            记忆对象
        """
        now = datetime.now().isoformat()
        
        # 自动评估重要性
        if importance is None:
            importance = await self._auto_evaluate_importance(content, metadata)
        
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            memory_type=memory_type,
            importance=importance,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            tags=tags or []
        )
        
        # 根据类型和重要性存储
        if importance.value >= self.config.long_term_threshold:
            # 重要信息存入长期记忆
            self.long_term_memories[memory.id] = memory
            logger.debug(f"存入长期记忆：{memory.id[:8]} (重要性={importance.value})")
        else:
            # 普通信息存入工作记忆
            self.working_memories.append(memory)
            
            # 检查窗口大小
            if len(self.working_memories) > self.config.working_window_size:
                await self._compact_working_memory()
        
        # 定期保存
        self._save_memories()
        
        return memory
    
    async def _auto_evaluate_importance(self, content: str, metadata: Dict = None) -> ImportanceLevel:
        """
        自动评估重要性
        
        规则：
        1. 包含决策/结论 → HIGH
        2. 包含代码/技术方案 → MEDIUM
        3. 包含错误/问题 → MEDIUM
        4. 普通对话 → LOW
        
        Args:
            content: 内容
            metadata: 元数据
        
        Returns:
            重要性等级
        """
        content_lower = content.lower()
        
        # 关键决策
        if any(word in content_lower for word in ['决定', '决策', '结论', '确定', 'confirmed', 'decided']):
            return ImportanceLevel.HIGH
        
        # 技术方案
        if any(word in content_lower for word in ['方案', '设计', '架构', '实现', 'implementation', 'design']):
            return ImportanceLevel.MEDIUM
        
        # 错误/问题
        if any(word in content_lower for word in ['错误', 'bug', 'fail', 'error', '问题']):
            return ImportanceLevel.MEDIUM
        
        # 用户指令
        if metadata and metadata.get('role') == 'user':
            return ImportanceLevel.MEDIUM
        
        # 默认低优先级
        return ImportanceLevel.LOW
    
    async def _compact_working_memory(self) -> None:
        """
        压缩工作记忆
        
        策略：
        1. 移除低重要性且访问次数少的记忆
        2. 合并相似的普通记忆
        3. 保留最近的记忆
        """
        if not self.config.auto_compact_enabled:
            return
        
        logger.info(f"压缩工作记忆：{len(self.working_memories)} 条")
        
        # 移除低重要性且未被访问的记忆
        to_remove = []
        for i, memory in enumerate(self.working_memories):
            if (memory.importance == ImportanceLevel.LOW and 
                memory.access_count == 0 and
                i < len(self.working_memories) - self.config.working_window_size // 2):
                to_remove.append(i)
        
        # 从后往前删除
        for i in reversed(to_remove):
            removed = self.working_memories.pop(i)
            logger.debug(f"移除工作记忆：{removed.id[:8]}")
        
        # 如果还是太多，保留最近的
        if len(self.working_memories) > self.config.working_window_size:
            removed_count = len(self.working_memories) - self.config.working_window_size
            self.working_memories = self.working_memories[-self.config.working_window_size:]
            logger.info(f"保留最近 {self.config.working_window_size} 条，移除 {removed_count} 条")
    
    async def load_context(
        self,
        query: str = None,
        max_tokens: int = None,
        include_types: List[MemoryType] = None
    ) -> List[Memory]:
        """
        按需加载上下文
        
        Args:
            query: 查询关键词（用于相关性排序）
            max_tokens: 最大 token 数
            include_types: 包含的记忆类型
        
        Returns:
            记忆列表（按重要性 + 相关性排序）
        """
        if max_tokens is None:
            max_tokens = self.config.working_max_tokens
        
        if include_types is None:
            include_types = [MemoryType.WORKING, MemoryType.LONG_TERM]
        
        candidates = []
        
        # 收集候选记忆
        if MemoryType.WORKING in include_types:
            candidates.extend(self.working_memories)
        
        if MemoryType.LONG_TERM in include_types:
            candidates.extend(self.long_term_memories.values())
        
        # 排序：重要性 + 访问时间 + 相关性
        scored_memories = []
        for memory in candidates:
            score = self._score_memory(memory, query)
            scored_memories.append((score, memory))
        
        # 按分数降序排序
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # 选择直到达到 token 限制
        result = []
        current_tokens = 0
        
        for score, memory in scored_memories:
            memory_tokens = len(memory.content) // 4  # 粗略估计
            
            if current_tokens + memory_tokens <= max_tokens:
                result.append(memory)
                current_tokens += memory_tokens
                
                # 更新访问统计
                memory.access_count += 1
                memory.last_accessed = datetime.now().isoformat()
            else:
                break
        
        logger.info(f"加载 {len(result)} 条记忆，{current_tokens}/{max_tokens} tokens")
        
        return result
    
    def _score_memory(self, memory: Memory, query: str = None) -> float:
        """
        评分记忆
        
        评分因素：
        1. 重要性等级（40%）
        2. 访问频率（20%）
        3. 新鲜度（20%）
        4. 查询相关性（20%）
        
        Args:
            memory: 记忆对象
            query: 查询关键词
        
        Returns:
            分数（0-100）
        """
        # 重要性分数（0-40）
        importance_score = memory.importance.value * 10
        
        # 访问频率分数（0-20）
        access_score = min(memory.access_count * 2, 20)
        
        # 新鲜度分数（0-20）
        # 越近的记忆分数越高
        try:
            created = datetime.fromisoformat(memory.created_at)
            age_days = (datetime.now() - created).days
            freshness_score = max(0, 20 - age_days * 2)
        except:
            freshness_score = 10
        
        # 查询相关性分数（0-20）
        relevance_score = 0
        if query:
            query_lower = query.lower()
            content_lower = memory.content.lower()
            
            # 简单关键词匹配
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_lower)
            relevance_score = min(matches * 5, 20)
        
        total_score = importance_score + access_score + freshness_score + relevance_score
        
        return total_score
    
    async def search(self, query: str, limit: int = 10) -> List[Memory]:
        """
        搜索记忆
        
        Args:
            query: 查询关键词
            limit: 返回数量限制
        
        Returns:
            记忆列表
        """
        all_memories = (
            self.working_memories + 
            list(self.long_term_memories.values()) + 
            list(self.archived_memories.values())
        )
        
        # 评分
        scored = [(self._score_memory(m, query), m) for m in all_memories]
        
        # 排序
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前 N 个
        return [m for _, m in scored[:limit]]
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'working_count': len(self.working_memories),
            'long_term_count': len(self.long_term_memories),
            'archived_count': len(self.archived_memories),
            'config': {
                'window_size': self.config.working_window_size,
                'max_tokens': self.config.working_max_tokens,
                'long_term_threshold': self.config.long_term_threshold
            }
        }
    
    async def clear(self) -> None:
        """清空所有记忆"""
        self.working_memories.clear()
        self.long_term_memories.clear()
        self.archived_memories.clear()
        self._save_memories()
        logger.info("清空所有记忆")


# 便捷函数
def create_memory_manager(storage_path: str = None, config: MemoryConfig = None) -> SmartMemoryManager:
    """
    创建记忆管理器
    
    Args:
        storage_path: 存储路径
        config: 配置
    
    Returns:
        记忆管理器实例
    """
    return SmartMemoryManager(storage_path, config)


# 全局实例
_memory_manager: Optional[SmartMemoryManager] = None

def get_memory_manager() -> SmartMemoryManager:
    """获取全局记忆管理器"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = SmartMemoryManager()
    return _memory_manager
