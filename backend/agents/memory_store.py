#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享记忆存储（SQLite）
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryStore:
    """共享记忆存储"""
    
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".ymcode" / "agents" / "memory.db"
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"MemoryStore 初始化：{self.db_path}")
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建共享记忆表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                type TEXT DEFAULT 'note',
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                assigned_to TEXT,
                created_by TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                result TEXT
            )
        ''')
        
        # 创建 Agent 状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_name TEXT PRIMARY KEY,
                state TEXT DEFAULT 'idle',
                memory_count INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                last_active TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON shared_memory(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def add_memory(self, agent: str, content: str, mem_type: str = "note", metadata: Dict = None):
        """添加记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shared_memory (agent, type, content, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            agent,
            mem_type,
            content,
            json.dumps(metadata or {}, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        logger.debug(f"添加记忆：{agent} - {content[:50]}...")
    
    def get_memories(self, limit: int = 100, agent: str = None, mem_type: str = None) -> List[Dict]:
        """获取记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT agent, type, content, metadata, timestamp
            FROM shared_memory
            WHERE 1=1
        '''
        params = []
        
        if agent:
            query += ' AND agent = ?'
            params.append(agent)
        
        if mem_type:
            query += ' AND type = ?'
            params.append(mem_type)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "agent": row[0],
                "type": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]),
                "timestamp": row[4]
            }
            for row in rows
        ]
    
    def search_memories(self, query: str, limit: int = 100) -> List[Dict]:
        """搜索记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT agent, type, content, metadata, timestamp
            FROM shared_memory
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "agent": row[0],
                "type": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]),
                "timestamp": row[4]
            }
            for row in rows
        ]
    
    def create_task(self, title: str, description: str = None, assigned_to: str = None, created_by: str = "user") -> int:
        """创建任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, assigned_to, created_by, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, assigned_to, created_by, datetime.now().isoformat()))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"创建任务 #{task_id}: {title}")
        return task_id
    
    def get_tasks(self, status: str = None, assigned_to: str = None) -> List[Dict]:
        """获取任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if assigned_to:
            query += ' AND assigned_to = ?'
            params.append(assigned_to)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "assigned_to": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "completed_at": row[7],
                "result": row[8]
            }
            for row in rows
        ]
    
    def update_task_status(self, task_id: int, status: str, result: str = None):
        """更新任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat() if status == "completed" else None
        
        cursor.execute('''
            UPDATE tasks
            SET status = ?, completed_at = ?, result = ?
            WHERE id = ?
        ''', (status, completed_at, result, task_id))
        
        conn.commit()
        conn.close()
        logger.info(f"更新任务 #{task_id} 状态：{status}")
    
    def save_agent_state(self, agent_name: str, state: str, memory_count: int = 0, completed_tasks: int = 0):
        """保存 Agent 状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO agent_states (agent_name, state, memory_count, completed_tasks, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_name, state, memory_count, completed_tasks, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_agent_states(self) -> List[Dict]:
        """获取所有 Agent 状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agent_states')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "agent_name": row[0],
                "state": row[1],
                "memory_count": row[2],
                "completed_tasks": row[3],
                "last_active": row[4]
            }
            for row in rows
        ]
    
    def clear_old_memories(self, days: int = 30):
        """清理旧记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            DELETE FROM shared_memory
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"清理 {deleted} 条旧记忆")
        return deleted
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 记忆统计
        cursor.execute('SELECT COUNT(*) FROM shared_memory')
        stats["total_memories"] = cursor.fetchone()[0]
        
        # 任务统计
        cursor.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
        task_stats = dict(cursor.fetchall())
        stats["tasks"] = task_stats
        
        # Agent 统计
        cursor.execute('SELECT COUNT(*) FROM agent_states')
        stats["active_agents"] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def export_data(self, output_file: str):
        """导出数据"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "memories": self.get_memories(limit=1000),
            "tasks": self.get_tasks(),
            "agent_states": self.get_agent_states()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"数据已导出：{output_file}")
    
    def import_data(self, input_file: str, clear_existing: bool = True):
        """导入数据"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 可选：清理现有数据
        if clear_existing:
            cursor.execute('DELETE FROM shared_memory')
            cursor.execute('DELETE FROM tasks')
            cursor.execute('DELETE FROM agent_states')
        
        # 导入记忆
        for mem in data.get("memories", []):
            cursor.execute('''
                INSERT INTO shared_memory (agent, type, content, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (mem["agent"], mem["type"], mem["content"], json.dumps(mem["metadata"]), mem["timestamp"]))
        
        # 导入任务
        for task in data.get("tasks", []):
            cursor.execute('''
                INSERT INTO tasks (id, title, description, status, assigned_to, created_by, created_at, completed_at, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task["id"], task["title"], task["description"], task["status"], task["assigned_to"], task["created_by"], task["created_at"], task["completed_at"], task["result"]))
        
        # 导入 Agent 状态
        for agent in data.get("agent_states", []):
            cursor.execute('''
                INSERT OR REPLACE INTO agent_states (agent_name, state, memory_count, completed_tasks, last_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (agent["agent_name"], agent["state"], agent["memory_count"], agent["completed_tasks"], agent["last_active"]))
        
        conn.commit()
        conn.close()
        
        logger.info(f"数据已导入：{input_file}")
