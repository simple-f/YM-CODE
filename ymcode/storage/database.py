#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库持久化层

支持：
- SQLite（默认）
- PostgreSQL（可选）
- 自动迁移
- 连接池
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


# ============ 数据模型 ============

class TaskModel(Base):
    """任务数据模型"""
    __tablename__ = 'tasks'
    
    id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=1)
    assigned_to = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    metadata_json = Column(JSON, default=dict)
    error = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # 索引
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_assigned_to', 'assigned_to'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata_json or {},
            "error": self.error,
            "retry_count": self.retry_count
        }


class TaskResultModel(Base):
    """任务结果数据模型"""
    __tablename__ = 'task_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey('tasks.id'), nullable=False)
    agent_id = Column(String(50), nullable=False)
    success = Column(Integer, default=1)  # 1=True, 0=False
    result_json = Column(JSON)
    error = Column(Text)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    task = relationship("TaskModel", backref="results")
    
    # 索引
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_agent_id', 'agent_id'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": bool(self.success),
            "result": self.result_json,
            "error": self.error,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MetricModel(Base):
    """指标数据模型"""
    __tablename__ = 'metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    labels_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # 索引
    __table_args__ = (
        Index('idx_name_timestamp', 'name', 'timestamp'),
        Index('idx_labels', 'labels_json', postgresql_using='gin'),
    )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "labels": self.labels_json or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class DocumentModel(Base):
    """文档数据模型（RAG 知识库）"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    metadata_json = Column(JSON, default=dict)
    embedding = Column(Text)  # JSON 数组的字符串表示
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 索引
    __table_args__ = (
        Index('idx_content_hash', 'content_hash'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "content_hash": self.content_hash,
            "metadata": self.metadata_json or {},
            "embedding": json.loads(self.embedding) if self.embedding else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ChunkModel(Base):
    """文档分块数据模型（RAG 知识库）"""
    __tablename__ = 'chunks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), ForeignKey('documents.doc_id'), nullable=False)
    chunk_id = Column(String(64), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text)  # JSON 数组的字符串表示
    chunk_index = Column(Integer)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    document = relationship("DocumentModel", backref="chunks")
    
    # 索引
    __table_args__ = (
        Index('idx_doc_id', 'doc_id'),
        Index('idx_chunk_id', 'chunk_id'),
    )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "content": self.content,
            "embedding": json.loads(self.embedding) if self.embedding else None,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ============ 数据库管理器 ============

class DatabaseManager:
    """
    数据库管理器
    
    支持 SQLite 和 PostgreSQL
    
    使用示例:
        >>> db = DatabaseManager("sqlite:///ymcode.db")
        >>> db.init_db()
        >>> session = db.get_session()
        >>> session.add(TaskModel(...))
        >>> session.commit()
    """
    
    def __init__(
        self,
        database_url: str = "sqlite:///ymcode.db",
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10
    ):
        """
        初始化数据库
        
        参数:
            database_url: 数据库 URL
                - SQLite: "sqlite:///path/to/db.db"
                - PostgreSQL: "postgresql://user:pass@host:5432/dbname"
            echo: 是否打印 SQL
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
        """
        self.database_url = database_url
        self.echo = echo
        
        # 创建引擎
        if database_url.startswith("sqlite"):
            # SQLite 使用静态池
            self.engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            # PostgreSQL 使用连接池
            self.engine = create_engine(
                database_url,
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow
            )
        
        # 创建 Session
        SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.SessionLocal = SessionLocal
        
        logger.info(f"数据库初始化完成：{database_url}")
    
    def init_db(self):
        """初始化数据库（创建表）"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("数据库表已创建")
    
    def drop_db(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("数据库表已删除")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """关闭数据库会话"""
        session.close()
    
    def execute_query(self, query, params=None):
        """执行原生 SQL 查询"""
        with self.engine.connect() as conn:
            result = conn.execute(query, params or {})
            return result.fetchall()
    
    def get_stats(self) -> Dict:
        """获取数据库统计"""
        with self.engine.connect() as conn:
            # 获取表大小
            tables = ['tasks', 'task_results', 'metrics', 'documents', 'chunks']
            stats = {}
            
            for table in tables:
                result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                stats[f"{table}_count"] = count
            
            return stats


# ============ 便捷函数 ============

_default_db = None


def get_database(database_url: str = "sqlite:///ymcode.db") -> DatabaseManager:
    """获取全局数据库实例"""
    global _default_db
    if _default_db is None:
        _default_db = DatabaseManager(database_url)
        _default_db.init_db()
    return _default_db


def get_db_session() -> Session:
    """获取数据库会话"""
    db = get_database()
    return db.get_session()


# ============ 使用示例 ============

if __name__ == "__main__":
    # 初始化数据库
    db = DatabaseManager("sqlite:///test.db")
    db.init_db()
    
    # 创建会话
    session = db.get_session()
    
    try:
        # 创建任务
        task = TaskModel(
            id="test-123",
            title="测试任务",
            description="这是一个测试任务",
            status="pending",
            priority=2
        )
        session.add(task)
        session.commit()
        
        # 查询任务
        task = session.query(TaskModel).filter_by(id="test-123").first()
        print(f"任务：{task.to_dict()}")
        
        # 创建任务结果
        result = TaskResultModel(
            task_id="test-123",
            agent_id="ai2",
            success=1,
            result_json={"data": "ok"},
            execution_time=1.5
        )
        session.add(result)
        session.commit()
        
        # 获取统计
        stats = db.get_stats()
        print(f"数据库统计：{stats}")
        
    finally:
        db.close_session(session)
