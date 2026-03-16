#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session 持久化存储 - SQLite 实现
"""

import aiosqlite
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SessionStore:
    """Session 持久化存储"""
    
    def __init__(self, db_path: str = None):
        """初始化数据库"""
        if db_path is None:
            db_dir = Path.home() / ".ymcode"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "sessions.db")
        
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
        logger.info(f"SessionStore 初始化：{db_path}")
    
    async def connect(self):
        """连接数据库"""
        self.db = await aiosqlite.connect(self.db_path)
        await self._init_tables()
        logger.info("数据库连接成功")
    
    async def close(self):
        """关闭数据库"""
        if self.db:
            await self.db.close()
            logger.info("数据库连接已关闭")
    
    async def _init_tables(self):
        """初始化数据表"""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id)
        """)
        
        await self.db.commit()
        logger.info("数据表初始化完成")
    
    async def save_session(self, session_id: str, title: str = None, status: str = 'active'):
        """保存或更新 Session"""
        now = datetime.now().isoformat()
        
        # 检查是否存在
        cursor = await self.db.execute(
            "SELECT id FROM sessions WHERE id = ?",
            (session_id,)
        )
        exists = await cursor.fetchone()
        await cursor.close()
        
        if exists:
            # 更新
            await self.db.execute(
                """UPDATE sessions 
                   SET updated_at = ?, status = ?, title = ?
                   WHERE id = ?""",
                (now, status, title, session_id)
            )
        else:
            # 插入
            await self.db.execute(
                """INSERT INTO sessions (id, title, created_at, updated_at, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, title or f"会话 {session_id[-8:]}", now, now, status)
            )
        
        await self.db.commit()
        logger.debug(f"Session 已保存：{session_id}")
    
    async def save_message(self, session_id: str, role: str, content: str, timestamp: str = None):
        """保存消息"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        await self.db.execute(
            """INSERT INTO messages (session_id, role, content, timestamp)
               VALUES (?, ?, ?, ?)""",
            (session_id, role, content, timestamp)
        )
        
        # 更新 Session 的更新时间
        await self.db.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), session_id)
        )
        
        await self.db.commit()
        logger.debug(f"消息已保存：{session_id} - {role}")
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取 Session 详情"""
        cursor = await self.db.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "status": row[4]
        }
    
    async def get_messages(self, session_id: str) -> List[Dict]:
        """获取 Session 的所有消息"""
        cursor = await self.db.execute(
            """SELECT role, content, timestamp 
               FROM messages 
               WHERE session_id = ?
               ORDER BY id ASC""",
            (session_id,)
        )
        rows = await cursor.fetchall()
        await cursor.close()
        
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in rows
        ]
    
    async def list_sessions(self, limit: int = 50) -> List[Dict]:
        """获取 Session 列表"""
        cursor = await self.db.execute(
            """SELECT id, title, created_at, updated_at, status
               FROM sessions
               ORDER BY updated_at DESC
               LIMIT ?""",
            (limit,)
        )
        rows = await cursor.fetchall()
        await cursor.close()
        
        # 获取每个 Session 的消息数量
        sessions = []
        for row in rows:
            msg_cursor = await self.db.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (row[0],)
            )
            msg_count = (await msg_cursor.fetchone())[0]
            await msg_cursor.close()
            
            sessions.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "status": row[4],
                "message_count": msg_count
            })
        
        return sessions
    
    async def delete_session(self, session_id: str) -> bool:
        """删除 Session"""
        cursor = await self.db.execute(
            "SELECT id FROM sessions WHERE id = ?",
            (session_id,)
        )
        exists = await cursor.fetchone()
        await cursor.close()
        
        if not exists:
            return False
        
        # 删除消息（外键会自动删除）
        await self.db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await self.db.commit()
        
        logger.info(f"Session 已删除：{session_id}")
        return True
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        # Session 总数
        cursor = await self.db.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = (await cursor.fetchone())[0]
        await cursor.close()
        
        # 消息总数
        cursor = await self.db.execute("SELECT COUNT(*) FROM messages")
        total_messages = (await cursor.fetchone())[0]
        await cursor.close()
        
        # 活跃 Session 数
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM sessions WHERE status = 'active'"
        )
        active_sessions = (await cursor.fetchone())[0]
        await cursor.close()
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_sessions": active_sessions
        }


# 全局存储实例
_store: Optional[SessionStore] = None


def get_store() -> SessionStore:
    """获取全局存储实例"""
    global _store
    if _store is None:
        _store = SessionStore()
    return _store


async def init_store():
    """初始化全局存储"""
    store = get_store()
    await store.connect()
    return store
