#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务持久化存储模块

使用 SQLite 存储任务数据
"""

import sqlite3
import json
import datetime
from typing import Dict, List, Optional
from pathlib import Path

class TaskStore:
    """任务持久化存储类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化任务存储
        
        参数:
            db_path: 数据库文件路径
        """
        if db_path is None:
            db_path = str(Path.home() / '.ymcode' / 'tasks.db')
        
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'inbox',
                priority TEXT DEFAULT 'normal',
                assignee TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_assignee ON tasks(assignee)')
        
        conn.commit()
        conn.close()
    
    def create_task(self, task_id: str, title: str, description: str = '', 
                    status: str = 'inbox', priority: str = 'normal',
                    assignee: str = '', metadata: Dict = None) -> bool:
        """
        创建任务
        
        参数:
            task_id: 任务 ID
            title: 任务标题
            description: 任务描述
            status: 任务状态
            priority: 优先级
            assignee: 负责人
            metadata: 元数据
        
        返回:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tasks (id, title, description, status, priority, assignee, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, title, description, status, priority, assignee, 
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"创建任务失败：{e}")
            return False
        finally:
            conn.close()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            任务数据
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'status': row[3],
                'priority': row[4],
                'assignee': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'metadata': json.loads(row[8]) if row[8] else None
            }
        
        return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """
        更新任务
        
        参数:
            task_id: 任务 ID
            **kwargs: 要更新的字段
        
        返回:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建更新语句
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['title', 'description', 'status', 'priority', 'assignee', 'metadata']:
                fields.append(f"{key} = ?")
                values.append(json.dumps(value) if key == 'metadata' else value)
        
        if not fields:
            conn.close()
            return False
        
        # 添加 updated_at
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(task_id)
        
        sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        
        try:
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"更新任务失败：{e}")
            return False
        finally:
            conn.close()
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除任务失败：{e}")
            return False
        finally:
            conn.close()
    
    def list_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None,
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        列出任务
        
        参数:
            status: 状态过滤
            assignee: 负责人过滤
            limit: 数量限制
            offset: 偏移量
        
        返回:
            任务列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM tasks"
        conditions = []
        values = []
        
        if status:
            conditions.append("status = ?")
            values.append(status)
        
        if assignee:
            conditions.append("assignee = ?")
            values.append(assignee)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        values.extend([limit, offset])
        
        cursor.execute(query, values)
        rows = cursor.fetchall()
        
        conn.close()
        
        # 转换为字典列表
        tasks = []
        for row in rows:
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'status': row[3],
                'priority': row[4],
                'assignee': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'metadata': json.loads(row[8]) if row[8] else None
            })
        
        return tasks
    
    def get_stats(self) -> Dict:
        """
        获取任务统计
        
        返回:
            统计数据
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总数
        cursor.execute("SELECT COUNT(*) FROM tasks")
        stats['total'] = cursor.fetchone()[0]
        
        # 按状态统计
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        conn.close()
        
        return stats


# 全局任务存储实例
_task_store_instance: Optional[TaskStore] = None

def get_task_store() -> TaskStore:
    """获取全局任务存储实例"""
    global _task_store_instance
    if _task_store_instance is None:
        _task_store_instance = TaskStore()
    return _task_store_instance
