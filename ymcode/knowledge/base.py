#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库基础 - 结构化知识存储

支持：
- 知识条目管理
- 分类体系
- 标签系统
- 知识关联
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeType(str, Enum):
    """知识类型"""
    CONCEPT = "concept"      # 概念
    PROCEDURE = "procedure"  # 流程
    FACT = "fact"           # 事实
    EXAMPLE = "example"     # 示例
    BEST_PRACTICE = "best_practice"  # 最佳实践
    TROUBLESHOOTING = "troubleshooting"  # 故障排除
    CODE_SNIPPET = "code_snippet"  # 代码片段
    DOCUMENTATION = "documentation"  # 文档


@dataclass
class KnowledgeEntry:
    """知识条目"""
    
    # 基础信息
    id: str = field(default_factory=lambda: f"kb_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    title: str = ""
    content: str = ""
    summary: str = ""
    
    # 分类
    type: KnowledgeType = KnowledgeType.CONCEPT
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    # 关联
    related_to: List[str] = field(default_factory=list)  # 关联的知识 ID
    prerequisites: List[str] = field(default_factory=list)  # 前置知识
    
    # 元数据
    source: str = ""  # 来源
    confidence: float = 1.0  # 置信度 (0-1)
    usage_count: int = 0  # 使用次数
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        """从字典创建"""
        if 'type' in data:
            data['type'] = KnowledgeType(data['type'])
        return cls(**data)
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
    
    def add_relation(self, knowledge_id: str, relation_type: str = "related") -> None:
        """添加关联"""
        if knowledge_id not in self.related_to:
            self.related_to.append(knowledge_id)
            self.updated_at = datetime.now().isoformat()
    
    def increment_usage(self) -> None:
        """增加使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.now().isoformat()


@dataclass
class KnowledgeCategory:
    """知识分类"""
    id: str
    name: str
    parent: str = None
    children: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KnowledgeGraph:
    """知识图谱 - 管理知识关联"""
    
    def __init__(self):
        """初始化知识图谱"""
        self.nodes: Dict[str, KnowledgeEntry] = {}
        self.edges: Dict[str, Set[str]] = {}  # 邻接表
        self.categories: Dict[str, KnowledgeCategory] = {}
        
        logger.info("知识图谱初始化完成")
    
    def add_entry(self, entry: KnowledgeEntry) -> None:
        """添加知识条目"""
        self.nodes[entry.id] = entry
        self.edges[entry.id] = set()
        
        # 添加到分类
        if entry.category not in self.categories:
            self.add_category(KnowledgeCategory(
                id=entry.category,
                name=entry.category
            ))
        
        logger.debug(f"添加知识条目：{entry.id} - {entry.title}")
    
    def remove_entry(self, entry_id: str) -> bool:
        """删除知识条目"""
        if entry_id not in self.nodes:
            return False
        
        # 删除相关边
        if entry_id in self.edges:
            del self.edges[entry_id]
        
        # 从其他节点的关联中移除
        for edges in self.edges.values():
            edges.discard(entry_id)
        
        del self.nodes[entry_id]
        
        logger.info(f"删除知识条目：{entry_id}")
        return True
    
    def add_relation(self, from_id: str, to_id: str, bidirectional: bool = True) -> bool:
        """添加知识关联"""
        if from_id not in self.nodes or to_id not in self.nodes:
            return False
        
        self.edges[from_id].add(to_id)
        
        if bidirectional:
            self.edges[to_id].add(from_id)
        
        # 更新知识条目的关联列表
        if to_id not in self.nodes[from_id].related_to:
            self.nodes[from_id].related_to.append(to_id)
        
        if bidirectional and from_id not in self.nodes[to_id].related_to:
            self.nodes[to_id].related_to.append(from_id)
        
        logger.debug(f"添加关联：{from_id} <-> {to_id}")
        return True
    
    def get_related(self, entry_id: str, depth: int = 1) -> List[str]:
        """获取关联知识"""
        if entry_id not in self.edges:
            return []
        
        related = set()
        current_level = {entry_id}
        
        for _ in range(depth):
            next_level = set()
            for node_id in current_level:
                if node_id in self.edges:
                    next_level.update(self.edges[node_id])
            related.update(next_level)
            current_level = next_level
        
        related.discard(entry_id)
        return list(related)
    
    def add_category(self, category: KnowledgeCategory) -> None:
        """添加分类"""
        self.categories[category.id] = category
        
        # 添加到父分类
        if category.parent and category.parent in self.categories:
            if category.id not in self.categories[category.parent].children:
                self.categories[category.parent].children.append(category.id)
        
        logger.debug(f"添加分类：{category.id}")
    
    def get_category_tree(self, category_id: str = None, indent: int = 0) -> str:
        """获取分类树"""
        if category_id is None:
            # 获取根分类
            roots = [c for c in self.categories.values() if not c.parent]
            return '\n'.join([self.get_category_tree(c.id, indent) for c in roots])
        
        category = self.categories.get(category_id)
        if not category:
            return ""
        
        result = "  " * indent + f"📁 {category.name} ({category.id})"
        
        for child_id in category.children:
            result += "\n" + self.get_category_tree(child_id, indent + 1)
        
        return result
    
    def search(self, query: str, category: str = None, tags: List[str] = None) -> List[KnowledgeEntry]:
        """搜索知识"""
        results = []
        
        for entry in self.nodes.values():
            # 分类过滤
            if category and entry.category != category:
                continue
            
            # 标签过滤
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # 文本搜索
            if (query.lower() in entry.title.lower() or
                query.lower() in entry.content.lower() or
                query.lower() in entry.summary.lower() or
                any(query.lower() in tag.lower() for tag in entry.tags)):
                results.append(entry)
        
        # 按置信度和使用次数排序
        results.sort(key=lambda x: (x.confidence, x.usage_count), reverse=True)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        type_counts = {}
        category_counts = {}
        tag_counts = {}
        
        for entry in self.nodes.values():
            # 类型统计
            type_counts[entry.type.value] = type_counts.get(entry.type.value, 0) + 1
            
            # 分类统计
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1
            
            # 标签统计
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_entries': len(self.nodes),
            'total_categories': len(self.categories),
            'total_relations': sum(len(edges) for edges in self.edges.values()),
            'by_type': type_counts,
            'by_category': category_counts,
            'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'entries': {k: v.to_dict() for k, v in self.nodes.items()},
            'edges': {k: list(v) for k, v in self.edges.items()},
            'categories': {k: v.to_dict() for k, v in self.categories.items()}
        }
    
    def save(self, file_path: Path) -> None:
        """保存到文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"知识图谱已保存：{file_path}")
    
    @classmethod
    def load(cls, file_path: Path) -> 'KnowledgeGraph':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        graph = cls()
        
        # 加载分类
        for cat_id, cat_data in data.get('categories', {}).items():
            graph.categories[cat_id] = KnowledgeCategory(**cat_data)
        
        # 加载条目
        for entry_id, entry_data in data.get('entries', {}).items():
            entry = KnowledgeEntry.from_dict(entry_data)
            graph.nodes[entry_id] = entry
            graph.edges[entry_id] = set()
        
        # 加载边
        for from_id, to_ids in data.get('edges', {}).items():
            graph.edges[from_id] = set(to_ids)
        
        logger.info(f"知识图谱已加载：{file_path}")
        
        return graph
