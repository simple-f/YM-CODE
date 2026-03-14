#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识检索器 - 智能检索相关知识

支持：
- 语义搜索
- 关键词匹配
- 关联推荐
- 上下文感知
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter

from ..utils.logger import get_logger
from .base import KnowledgeGraph, KnowledgeEntry, KnowledgeType

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """搜索结果"""
    entry: KnowledgeEntry
    score: float
    matched_fields: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entry': self.entry.to_dict(),
            'score': self.score,
            'matched_fields': self.matched_fields,
            'highlights': self.highlights
        }


class KnowledgeRetriever:
    """知识检索器"""
    
    def __init__(self, graph: KnowledgeGraph):
        """
        初始化检索器
        
        参数:
            graph: 知识图谱
        """
        self.graph = graph
        self.query_cache: Dict[str, List[SearchResult]] = {}
        
        logger.info("知识检索器初始化完成")
    
    def search(self, query: str, 
               category: str = None,
               tags: List[str] = None,
               knowledge_type: KnowledgeType = None,
               limit: int = 20) -> List[SearchResult]:
        """
        搜索知识
        
        参数:
            query: 搜索查询
            category: 分类过滤
            tags: 标签过滤
            knowledge_type: 知识类型过滤
            limit: 结果数量限制
        
        返回:
            搜索结果列表
        """
        # 检查缓存
        cache_key = f"{query}:{category}:{','.join(tags or [])}:{knowledge_type}"
        if cache_key in self.query_cache:
            logger.debug(f"使用缓存结果：{cache_key}")
            return self.query_cache[cache_key][:limit]
        
        results = []
        
        # 提取查询关键词
        query_keywords = self._extract_query_keywords(query)
        
        for entry in self.graph.nodes.values():
            # 分类过滤
            if category and entry.category != category:
                continue
            
            # 标签过滤
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # 类型过滤
            if knowledge_type and entry.type != knowledge_type:
                continue
            
            # 计算相关性分数
            score, matched_fields, highlights = self._calculate_relevance(
                entry, query, query_keywords
            )
            
            if score > 0.1:  # 阈值
                results.append(SearchResult(
                    entry=entry,
                    score=score,
                    matched_fields=matched_fields,
                    highlights=highlights
                ))
        
        # 排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        # 缓存结果
        self.query_cache[cache_key] = results
        
        logger.info(f"搜索 '{query}': {len(results)} 个结果")
        
        return results[:limit]
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        # 分词
        words = re.findall(r'\b\w+\b', query.lower())
        
        # 过滤停用词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'how', 'what', 'when', 'where', 'why', 'which', 'who', 'whom',
            '怎么', '如何', '什么', '哪里', '哪个', '哪些', '为什么'
        }
        
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        return keywords
    
    def _calculate_relevance(self, entry: KnowledgeEntry, 
                            query: str, query_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        计算相关性分数
        
        返回:
            (分数，匹配的字段，高亮片段)
        """
        score = 0.0
        matched_fields = []
        highlights = []
        
        # 标题匹配（权重最高）
        if self._match_text(entry.title, query_keywords):
            score += 3.0
            matched_fields.append('title')
            highlights.append(f"标题：{entry.title}")
        
        # 摘要匹配
        if self._match_text(entry.summary, query_keywords):
            score += 2.0
            matched_fields.append('summary')
            highlights.append(f"摘要：{entry.summary[:100]}")
        
        # 内容匹配
        if self._match_text(entry.content, query_keywords):
            score += 1.0
            matched_fields.append('content')
            # 提取高亮片段
            snippet = self._extract_snippet(entry.content, query_keywords)
            if snippet:
                highlights.append(f"内容：...{snippet}...")
        
        # 标签匹配
        tag_matches = [tag for tag in entry.tags if any(kw in tag.lower() for kw in query_keywords)]
        if tag_matches:
            score += 1.5
            matched_fields.append('tags')
            highlights.append(f"标签：{', '.join(tag_matches)}")
        
        # 关键词匹配
        keyword_matches = [kw for kw in entry.tags if kw in query_keywords]
        if keyword_matches:
            score += 0.5 * len(keyword_matches)
        
        # 关联知识加分
        related_count = len(entry.related_to)
        if related_count > 0:
            score += min(0.5, related_count * 0.1)
        
        # 使用次数加分
        if entry.usage_count > 0:
            score += min(0.5, entry.usage_count * 0.05)
        
        # 置信度加权
        score *= entry.confidence
        
        return score, matched_fields, highlights
    
    def _match_text(self, text: str, keywords: List[str]) -> bool:
        """检查文本是否匹配关键词"""
        if not text or not keywords:
            return False
        
        text_lower = text.lower()
        
        # 完全匹配
        if any(kw in text_lower for kw in keywords):
            return True
        
        # 部分匹配（前缀）
        if any(text_lower.startswith(kw) for kw in keywords):
            return True
        
        return False
    
    def _extract_snippet(self, content: str, keywords: List[str], 
                        snippet_size: int = 100) -> str:
        """提取包含关键词的片段"""
        content_lower = content.lower()
        
        # 找到第一个匹配的关键词位置
        for keyword in keywords:
            pos = content_lower.find(keyword)
            if pos != -1:
                start = max(0, pos - snippet_size // 2)
                end = min(len(content), pos + snippet_size // 2)
                return content[start:end].strip()
        
        # 没有匹配则返回开头
        return content[:snippet_size].strip()
    
    def get_related_knowledge(self, entry_id: str, 
                             limit: int = 10) -> List[SearchResult]:
        """获取相关知识"""
        if entry_id not in self.graph.nodes:
            return []
        
        entry = self.graph.nodes[entry_id]
        results = []
        
        # 直接关联
        related_ids = self.graph.get_related(entry_id, depth=1)
        
        for related_id in related_ids[:limit]:
            if related_id in self.graph.nodes:
                related_entry = self.graph.nodes[related_id]
                results.append(SearchResult(
                    entry=related_entry,
                    score=0.8,  # 关联知识分数
                    matched_fields=['related_to']
                ))
        
        # 基于标签推荐
        if len(results) < limit:
            for other_entry in self.graph.nodes.values():
                if other_entry.id == entry_id:
                    continue
                
                # 计算标签相似度
                common_tags = set(entry.tags) & set(other_entry.tags)
                if len(common_tags) >= 2:
                    score = len(common_tags) / max(len(entry.tags), len(other_entry.tags))
                    results.append(SearchResult(
                        entry=other_entry,
                        score=score * 0.7,
                        matched_fields=['tags']
                    ))
                
                if len(results) >= limit:
                    break
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def suggest_tags(self, query: str) -> List[str]:
        """建议标签"""
        keywords = self._extract_query_keywords(query)
        
        # 统计所有标签
        tag_counts = Counter()
        
        for entry in self.graph.nodes.values():
            for tag in entry.tags:
                if any(kw in tag.lower() for kw in keywords):
                    tag_counts[tag] += 1
        
        return [tag for tag, count in tag_counts.most_common(10)]
    
    def get_popular_knowledge(self, category: str = None, 
                             limit: int = 10) -> List[KnowledgeEntry]:
        """获取热门知识"""
        entries = list(self.graph.nodes.values())
        
        # 分类过滤
        if category:
            entries = [e for e in entries if e.category == category]
        
        # 按使用次数排序
        entries.sort(key=lambda x: x.usage_count, reverse=True)
        
        return entries[:limit]
    
    def get_recent_knowledge(self, limit: int = 10) -> List[KnowledgeEntry]:
        """获取最近知识"""
        entries = list(self.graph.nodes.values())
        
        # 按更新时间排序
        entries.sort(key=lambda x: x.updated_at, reverse=True)
        
        return entries[:limit]
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.query_cache.clear()
        logger.info("检索缓存已清空")
