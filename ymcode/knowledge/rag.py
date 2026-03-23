#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG (Retrieval-Augmented Generation) 知识库系统

支持：
- 文档导入
- 自动分块
- 向量化
- 语义检索
- 混合检索（语义 + 关键词）
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re

from ..storage.database import DocumentModel, ChunkModel, get_db_session
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """文档对象"""
    doc_id: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Chunk:
    """文档分块对象"""
    chunk_id: str
    doc_id: str
    content: str
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """搜索结果"""
    chunk_id: str
    doc_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    document_title: str = ""


class TextSplitter:
    """
    文本分块器
    
    支持：
    - 按字符数分块
    - 按段落分块
    - 重叠分块
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        初始化分块器
        
        参数:
            chunk_size: 每块大小（字符数）
            chunk_overlap: 重叠大小
            separators: 分隔符列表
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """
        分割文本
        
        参数:
            text: 原始文本
        
        返回:
            分块列表
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # 计算结束位置
            end = start + self.chunk_size
            
            if end >= len(text):
                # 最后一块
                chunk = text[start:]
                chunks.append(chunk.strip())
                break
            
            # 寻找最佳分割点
            chunk = text[start:end]
            
            # 尝试在分隔符处分割
            for separator in self.separators:
                if separator:
                    last_sep = chunk.rfind(separator)
                    if last_sep > self.chunk_size * 0.5:  # 至少 50% 长度
                        end = start + last_sep + len(separator)
                        break
            
            chunk = text[start:end].strip()
            chunks.append(chunk)
            
            # 移动起始位置（考虑重叠）
            start = end - self.chunk_overlap
        
        return chunks


class EmbeddingModel:
    """
    向量化模型
    
    支持：
    - 本地模型（sentence-transformers）
    - API 模型（DashScope、OpenAI）
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        初始化向量化模型
        
        参数:
            model_name: 模型名称
            api_key: API Key（使用 API 时）
            api_url: API URL（使用 API 时）
        """
        self.model_name = model_name
        self.api_key = api_key
        self.api_url = api_url
        self._model = None
        self._dimension = 384  # 默认维度
    
    def _load_model(self):
        """加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
                logger.info(f"加载本地模型：{self.model_name}")
            except ImportError:
                logger.warning("sentence-transformers 未安装，使用 API 模式")
    
    def embed_text(self, text: str) -> List[float]:
        """
        向量化文本
        
        参数:
            text: 输入文本
        
        返回:
            向量（列表）
        """
        # 使用 API
        if self.api_key and self.api_url:
            return self._embed_with_api(text)
        
        # 使用本地模型
        self._load_model()
        if self._model:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        
        # 降级：使用简单哈希
        logger.warning("使用降级方案：简单哈希向量")
        return self._simple_hash(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量向量化"""
        return [self.embed_text(text) for text in texts]
    
    def _embed_with_api(self, text: str) -> List[float]:
        """使用 API 向量化"""
        import requests
        
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": text, "model": self.model_name}
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"API 向量化失败：{e}")
            return self._simple_hash(text)
    
    def _simple_hash(self, text: str) -> List[float]:
        """简单哈希向量（降级方案）"""
        hash_bytes = hashlib.md5(text.encode()).digest()
        # 转换为 384 维向量
        vector = []
        for i in range(384):
            byte_idx = i % 16
            vector.append((hash_bytes[byte_idx] - 128) / 128.0)
        return vector


class RAGKnowledgeBase:
    """
    RAG 知识库
    
    功能:
    - 文档导入
    - 自动分块
    - 向量化存储
    - 语义检索
    - 混合检索
    
    使用示例:
        >>> kb = RAGKnowledgeBase()
        >>> kb.add_document("doc1", "标题", "内容...")
        >>> results = kb.search("查询", top_k=5)
    """
    
    def __init__(
        self,
        database_url: str = "sqlite:///rag.db",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        初始化知识库
        
        参数:
            database_url: 数据库 URL
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            embedding_model: 向量化模型
            api_key: API Key
            api_url: API URL
        """
        # 初始化数据库
        from ..storage.database import DatabaseManager
        self.db = DatabaseManager(database_url)
        self.db.init_db()
        
        # 初始化分块器
        self.splitter = TextSplitter(chunk_size, chunk_overlap)
        
        # 初始化向量化模型
        self.embedding_model = EmbeddingModel(embedding_model, api_key, api_url)
        
        logger.info("RAG 知识库初始化完成")
    
    def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        添加文档
        
        参数:
            doc_id: 文档 ID
            title: 标题
            content: 内容
            metadata: 元数据
        
        返回:
            分块数量
        """
        session = self.db.get_session()
        
        try:
            # 计算内容哈希
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # 检查是否已存在
            existing = session.query(DocumentModel).filter_by(doc_id=doc_id).first()
            if existing:
                logger.warning(f"文档已存在：{doc_id}")
                return 0
            
            # 创建文档
            doc = DocumentModel(
                doc_id=doc_id,
                title=title,
                content=content,
                content_hash=content_hash,
                metadata_json=metadata or {}
            )
            session.add(doc)
            
            # 分块
            chunks = self.splitter.split_text(content)
            
            # 向量化并保存分块
            chunk_count = 0
            for i, chunk_content in enumerate(chunks):
                # 计算向量
                embedding = self.embedding_model.embed_text(chunk_content)
                
                # 创建分块
                chunk = ChunkModel(
                    doc_id=doc_id,
                    chunk_id=f"{doc_id}_chunk_{i}",
                    content=chunk_content,
                    embedding=json.dumps(embedding),
                    chunk_index=i,
                    metadata={"title": title}
                )
                session.add(chunk)
                chunk_count += 1
            
            session.commit()
            
            logger.info(f"添加文档：{doc_id} ({chunk_count}个分块)")
            return chunk_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"添加文档失败：{e}")
            raise
        finally:
            self.db.close_session(session)
    
    def add_documents_from_dir(self, dir_path: str, pattern: str = "*.md") -> int:
        """
        从目录导入文档
        
        参数:
            dir_path: 目录路径
            pattern: 文件匹配模式
        
        返回:
            导入的文档数量
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise ValueError(f"目录不存在：{dir_path}")
        
        count = 0
        for file_path in dir_path.glob(pattern):
            try:
                # 读取内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用文件名作为 doc_id
                doc_id = file_path.stem
                title = file_path.stem
                
                # 添加文档
                self.add_document(doc_id, title, content)
                count += 1
                
                logger.info(f"导入文档：{file_path.name}")
                
            except Exception as e:
                logger.error(f"导入文件失败 {file_path}: {e}")
        
        return count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_doc_id: Optional[str] = None,
        min_score: float = 0.5
    ) -> List[SearchResult]:
        """
        语义检索
        
        参数:
            query: 查询文本
            top_k: 返回数量
            filter_doc_id: 过滤文档 ID
            min_score: 最低相似度阈值
        
        返回:
            搜索结果列表
        """
        session = self.db.get_session()
        
        try:
            # 向量化查询
            query_embedding = self.embedding_model.embed_text(query)
            
            # 获取所有分块
            query_chunks = session.query(ChunkModel)
            if filter_doc_id:
                query_chunks = query_chunks.filter_by(doc_id=filter_doc_id)
            
            chunks = query_chunks.all()
            
            # 计算相似度
            results = []
            for chunk in chunks:
                if chunk.embedding:
                    chunk_embedding = json.loads(chunk.embedding)
                    score = self._cosine_similarity(query_embedding, chunk_embedding)
                    
                    if score >= min_score:
                        # 获取文档标题
                        doc = session.query(DocumentModel).filter_by(doc_id=chunk.doc_id).first()
                        
                        results.append(SearchResult(
                            chunk_id=chunk.chunk_id,
                            doc_id=chunk.doc_id,
                            content=chunk.content,
                            score=score,
                            metadata=chunk.metadata_json or {},
                            document_title=doc.title if doc else ""
                        ))
            
            # 按分数排序
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"检索失败：{e}")
            return []
        finally:
            self.db.close_session(session)
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7
    ) -> List[SearchResult]:
        """
        混合检索（语义 + 关键词）
        
        参数:
            query: 查询文本
            top_k: 返回数量
            semantic_weight: 语义权重
        
        返回:
            搜索结果
        """
        session = self.db.get_session()
        
        try:
            # 语义检索
            semantic_results = self.search(query, top_k=top_k * 2)
            
            # 关键词检索
            keyword_results = self._keyword_search(query, top_k=top_k * 2, session=session)
            
            # 融合结果
            fused_results = self._fuse_results(
                semantic_results,
                keyword_results,
                semantic_weight=semantic_weight
            )
            
            return fused_results[:top_k]
            
        finally:
            self.db.close_session(session)
    
    def _keyword_search(
        self,
        query: str,
        top_k: int = 10,
        session = None
    ) -> List[SearchResult]:
        """关键词检索"""
        # 简单实现：全文搜索
        query_words = query.lower().split()
        
        chunks = session.query(ChunkModel).all()
        results = []
        
        for chunk in chunks:
            content_lower = chunk.content.lower()
            score = sum(1 for word in query_words if word in content_lower)
            
            if score > 0:
                doc = session.query(DocumentModel).filter_by(doc_id=chunk.doc_id).first()
                results.append(SearchResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    content=chunk.content,
                    score=score / len(query_words),
                    document_title=doc.title if doc else ""
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _fuse_results(
        self,
        semantic: List[SearchResult],
        keyword: List[SearchResult],
        semantic_weight: float = 0.7
    ) -> List[SearchResult]:
        """融合检索结果"""
        # 创建结果字典
        result_dict = {}
        
        # 添加语义结果
        for i, result in enumerate(semantic):
            result_dict[result.chunk_id] = {
                "result": result,
                "semantic_score": result.score,
                "keyword_score": 0
            }
        
        # 添加关键词结果
        for i, result in enumerate(keyword):
            if result.chunk_id in result_dict:
                result_dict[result.chunk_id]["keyword_score"] = result.score
            else:
                result_dict[result.chunk_id] = {
                    "result": result,
                    "semantic_score": 0,
                    "keyword_score": result.score
                }
        
        # 计算加权分数
        fused = []
        for data in result_dict.values():
            result = data["result"]
            result.score = (
                data["semantic_score"] * semantic_weight +
                data["keyword_score"] * (1 - semantic_weight)
            )
            fused.append(result)
        
        fused.sort(key=lambda x: x.score, reverse=True)
        return fused
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def get_stats(self) -> Dict:
        """获取知识库统计"""
        session = self.db.get_session()
        
        try:
            doc_count = session.query(DocumentModel).count()
            chunk_count = session.query(ChunkModel).count()
            
            return {
                "document_count": doc_count,
                "chunk_count": chunk_count,
                "avg_chunks_per_doc": chunk_count / doc_count if doc_count > 0 else 0
            }
        finally:
            self.db.close_session(session)


# 便捷函数

_default_kb = None


def get_knowledge_base(
    database_url: str = "sqlite:///rag.db",
    **kwargs
) -> RAGKnowledgeBase:
    """获取全局知识库实例"""
    global _default_kb
    if _default_kb is None:
        _default_kb = RAGKnowledgeBase(database_url, **kwargs)
    return _default_kb


if __name__ == "__main__":
    # 测试知识库
    kb = RAGKnowledgeBase()
    
    # 添加文档
    kb.add_document(
        "test-1",
        "测试文档",
        "这是一个测试文档，包含一些内容。RAG 系统可以检索这些内容。"
    )
    
    # 检索
    results = kb.search("RAG 系统", top_k=3)
    
    print(f"检索到 {len(results)} 个结果")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result.score:.3f}] {result.content[:50]}...")
    
    # 统计
    stats = kb.get_stats()
    print(f"统计：{stats}")
