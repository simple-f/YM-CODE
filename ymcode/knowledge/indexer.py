#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识索引器 - 自动索引文档和代码

支持：
- 文档内容提取
- 代码结构分析
- 关键词提取
- 自动分类
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

from ..utils.logger import get_logger
from .base import KnowledgeEntry, KnowledgeType, KnowledgeGraph

logger = get_logger(__name__)


@dataclass
class IndexedDocument:
    """已索引的文档"""
    path: str
    title: str
    content: str
    keywords: List[str] = field(default_factory=list)
    summary: str = ""
    type: str = "document"  # document, code, api
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentIndexer:
    """文档索引器"""
    
    # 常见停用词
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'this', 'that', 'these', 'those', 'it', 'its', 'as', 'so', 'than',
        '的', '了', '和', '是', '在', '就', '都', '而', '及', '与', '着',
        '就', '那', '你', '我', '他', '她', '它', '们', '个', '有', '大', '小'
    }
    
    def __init__(self, graph: KnowledgeGraph = None):
        """
        初始化索引器
        
        参数:
            graph: 知识图谱
        """
        self.graph = graph or KnowledgeGraph()
        self.indexed_files: Dict[str, IndexedDocument] = {}
        
        logger.info("文档索引器初始化完成")
    
    def index_file(self, file_path: Path, auto_categorize: bool = True) -> Optional[KnowledgeEntry]:
        """
        索引单个文件
        
        参数:
            file_path: 文件路径
            auto_categorize: 是否自动分类
        
        返回:
            知识条目
        """
        if not file_path.exists():
            logger.warning(f"文件不存在：{file_path}")
            return None
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 根据扩展名选择处理方式
            suffix = file_path.suffix.lower()
            
            if suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                indexed = self._index_code(file_path, content)
            elif suffix in ['.md', '.rst', '.txt']:
                indexed = self._index_document(file_path, content)
            elif suffix in ['.json', '.yaml', '.yml']:
                indexed = self._index_config(file_path, content)
            else:
                indexed = self._index_generic(file_path, content)
            
            # 创建知识条目
            entry = self._create_knowledge_entry(indexed, auto_categorize)
            
            # 添加到知识图谱
            self.graph.add_entry(entry)
            self.indexed_files[str(file_path)] = indexed
            
            logger.info(f"索引文件：{file_path} ({len(indexed.keywords)} 关键词)")
            
            return entry
            
        except Exception as e:
            logger.error(f"索引文件失败 {file_path}: {e}")
            return None
    
    def _index_document(self, file_path: Path, content: str) -> IndexedDocument:
        """索引文档"""
        # 提取标题（第一个 # 标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # 提取摘要（第一段）
        paragraphs = re.split(r'\n\s*\n', content)
        summary = ''
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('#'):
                summary = para[:200]
                break
        
        # 提取关键词
        keywords = self._extract_keywords(content)
        
        # 提取标签（从 YAML frontmatter 或 tags）
        tags = self._extract_tags(content)
        
        return IndexedDocument(
            path=str(file_path),
            title=title,
            content=content,
            keywords=keywords[:20],
            summary=summary,
            type='document',
            metadata={
                'tags': tags,
                'word_count': len(content.split()),
                'paragraph_count': len(paragraphs)
            }
        )
    
    def _index_code(self, file_path: Path, content: str) -> IndexedDocument:
        """索引代码文件"""
        # 提取函数和类
        functions = self._extract_functions(content, file_path.suffix)
        classes = self._extract_classes(content, file_path.suffix)
        
        # 生成标题
        title = f"{file_path.stem} ({file_path.suffix[1:].upper()})"
        
        # 生成摘要
        summary = f"包含 {len(functions)} 个函数，{len(classes)} 个类"
        
        # 提取关键词
        keywords = self._extract_keywords(content, is_code=True)
        
        return IndexedDocument(
            path=str(file_path),
            title=title,
            content=content,
            keywords=keywords[:20] + functions + classes,
            summary=summary,
            type='code',
            metadata={
                'language': file_path.suffix[1:],
                'functions': functions,
                'classes': classes,
                'lines': len(content.split('\n'))
            }
        )
    
    def _index_config(self, file_path: Path, content: str) -> IndexedDocument:
        """索引配置文件"""
        title = f"{file_path.stem} config"
        
        # 提取顶层键作为关键词
        try:
            if file_path.suffix == '.json':
                data = json.loads(content)
                keywords = list(data.keys())
            else:
                import yaml
                data = yaml.safe_load(content)
                keywords = list(data.keys()) if isinstance(data, dict) else []
        except:
            keywords = []
        
        return IndexedDocument(
            path=str(file_path),
            title=title,
            content=content,
            keywords=keywords,
            summary=f"配置文件 ({file_path.suffix[1:]})",
            type='config',
            metadata={
                'format': file_path.suffix[1:],
                'keys': keywords
            }
        )
    
    def _index_generic(self, file_path: Path, content: str) -> IndexedDocument:
        """索引通用文件"""
        keywords = self._extract_keywords(content)
        
        return IndexedDocument(
            path=str(file_path),
            title=file_path.stem,
            content=content[:10000],  # 限制内容长度
            keywords=keywords[:20],
            summary=f"文件类型：{file_path.suffix}",
            type='document',
            metadata={
                'size': len(content),
                'extension': file_path.suffix
            }
        )
    
    def _extract_keywords(self, content: str, is_code: bool = False) -> List[str]:
        """提取关键词"""
        # 分词（简单实现）
        if is_code:
            # 代码：提取标识符
            words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        else:
            # 文档：按空格和标点分词
            words = re.findall(r'\b\w+\b', content.lower())
        
        # 过滤停用词和短词
        words = [
            w for w in words
            if len(w) > 2 and w.lower() not in self.STOP_WORDS
        ]
        
        # 统计词频
        word_counts = Counter(words)
        
        # 返回高频词
        return [word for word, count in word_counts.most_common(30)]
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 从 YAML frontmatter 提取
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            try:
                import yaml
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if 'tags' in frontmatter:
                    tags = frontmatter['tags']
            except:
                pass
        
        # 从内容提取 #tags
        hashtag_matches = re.findall(r'#(\w+)', content)
        tags.extend(hashtag_matches)
        
        return list(set(tags))
    
    def _extract_functions(self, content: str, suffix: str) -> List[str]:
        """提取函数名"""
        functions = []
        
        if suffix == '.py':
            matches = re.findall(r'def\s+(\w+)\s*\(', content)
            functions.extend(matches)
        elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
            # function declaration
            matches = re.findall(r'function\s+(\w+)\s*\(', content)
            functions.extend(matches)
            # arrow functions
            matches = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', content)
            functions.extend(matches)
        
        return list(set(functions))
    
    def _extract_classes(self, content: str, suffix: str) -> List[str]:
        """提取类名"""
        classes = []
        
        if suffix == '.py':
            matches = re.findall(r'class\s+(\w+)', content)
            classes.extend(matches)
        elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
            matches = re.findall(r'class\s+(\w+)', content)
            classes.extend(matches)
        
        return list(set(classes))
    
    def _create_knowledge_entry(self, indexed: IndexedDocument, auto_categorize: bool) -> KnowledgeEntry:
        """创建知识条目"""
        # 自动分类
        category = indexed.type
        if auto_categorize:
            if indexed.type == 'code':
                lang = indexed.metadata.get('language', 'unknown')
                category = f"code/{lang}"
            elif indexed.type == 'config':
                category = "config"
        
        # 确定知识类型
        knowledge_type = KnowledgeType.DOCUMENTATION
        if indexed.type == 'code':
            knowledge_type = KnowledgeType.CODE_SNIPPET
        elif indexed.type == 'config':
            knowledge_type = KnowledgeType.FACT
        
        entry = KnowledgeEntry(
            title=indexed.title,
            content=indexed.content[:5000],  # 限制内容长度
            summary=indexed.summary,
            type=knowledge_type,
            category=category,
            tags=indexed.metadata.get('tags', []),
            source=indexed.path,
            confidence=0.9  # 自动索引的置信度
        )
        
        # 添加关键词作为标签
        for keyword in indexed.keywords[:10]:
            entry.add_tag(keyword)
        
        return entry
    
    def index_directory(self, dir_path: Path, pattern: str = None, 
                       exclude: List[str] = None, auto_categorize: bool = True) -> int:
        """
        索引目录
        
        参数:
            dir_path: 目录路径
            pattern: 文件匹配模式
            exclude: 排除的模式
            auto_categorize: 自动分类
        
        返回:
            索引的文件数
        """
        if not dir_path.exists():
            logger.warning(f"目录不存在：{dir_path}")
            return 0
        
        exclude = exclude or ['node_modules', '__pycache__', '.git', 'dist', 'build']
        
        count = 0
        
        for file_path in dir_path.rglob(pattern or '*'):
            if file_path.is_file():
                # 检查是否应该排除
                if any(excl in str(file_path) for excl in exclude):
                    continue
                
                # 索引文件
                if self.index_file(file_path, auto_categorize):
                    count += 1
        
        logger.info(f"索引完成：{count} 个文件")
        
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取索引统计"""
        type_counts = Counter(doc.type for doc in self.indexed_files.values())
        
        return {
            'total_indexed': len(self.indexed_files),
            'by_type': dict(type_counts),
            'total_keywords': sum(len(doc.keywords) for doc in self.indexed_files.values()),
            'graph_stats': self.graph.get_statistics()
        }
