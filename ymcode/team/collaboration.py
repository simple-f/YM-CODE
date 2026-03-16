#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队协作功能 - 任务分配 + 评论系统
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class Comment:
    """评论"""
    id: int
    user_id: str
    user_name: str
    content: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = None
    parent_id: int = None  # 回复评论
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Comment':
        """从字典创建"""
        return cls(**data)


@dataclass
class Task:
    """任务"""
    id: int
    title: str
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "normal"  # low, normal, high, urgent
    assigned_to: str = None  # user_id
    created_by: str = None  # user_id
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: str = None
    completed_at: str = None
    completed_by: str = None
    tags: List[str] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["comments"] = [c.to_dict() for c in self.comments]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """从字典创建"""
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]
        data["comments"] = comments
        return cls(**data)


class TaskManager:
    """任务管理器"""
    
    def __init__(self, storage_path: str = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".ymcode" / "team" / "tasks.json"
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[int, Task] = {}
        self._next_id = 1
        self._comment_counter = 0
        
        self._load_tasks()
        logger.info("任务管理器初始化完成")
    
    def create_task(self, title: str, description: str = "", 
                    assigned_to: str = None, created_by: str = None,
                    priority: str = "normal", due_date: str = None,
                    tags: List[str] = None) -> Task:
        """创建任务"""
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            created_by=created_by,
            priority=priority,
            due_date=due_date,
            tags=tags or []
        )
        
        self.tasks[task.id] = task
        self._next_id += 1
        
        logger.info(f"创建任务 #{task.id}: {title}")
        self._save_tasks()
        
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """更新任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        logger.info(f"更新任务 #{task_id}")
        self._save_tasks()
        return True
    
    def assign_task(self, task_id: int, user_id: str) -> bool:
        """分配任务"""
        return self.update_task(task_id, assigned_to=user_id)
    
    def complete_task(self, task_id: int, user_id: str, result: str = None) -> bool:
        """完成任务"""
        return self.update_task(
            task_id,
            status="completed",
            completed_at=datetime.now().isoformat(),
            completed_by=user_id,
            metadata={"result": result}
        )
    
    def cancel_task(self, task_id: int) -> bool:
        """取消任务"""
        return self.update_task(task_id, status="cancelled")
    
    def list_tasks(self, status: str = None, assigned_to: str = None,
                   created_by: str = None, tags: List[str] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        
        if created_by:
            tasks = [t for t in tasks if t.created_by == created_by]
        
        if tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]
        
        # 按创建时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks
    
    def add_comment(self, task_id: int, user_id: str, user_name: str,
                    content: str, parent_id: int = None) -> Optional[Comment]:
        """添加评论"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        self._comment_counter += 1
        comment = Comment(
            id=self._comment_counter,
            user_id=user_id,
            user_name=user_name,
            content=content,
            parent_id=parent_id
        )
        
        task.comments.append(comment)
        
        logger.info(f"添加评论到任务 #{task_id}")
        self._save_tasks()
        
        return comment
    
    def get_comments(self, task_id: int) -> List[Comment]:
        """获取评论"""
        task = self.get_task(task_id)
        return task.comments if task else []
    
    def delete_comment(self, task_id: int, comment_id: int) -> bool:
        """删除评论"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.comments = [c for c in task.comments if c.id != comment_id]
        self._save_tasks()
        return True
    
    def get_task_stats(self) -> Dict:
        """获取任务统计"""
        stats = {
            "total": len(self.tasks),
            "by_status": {},
            "by_priority": {},
            "by_user": {},
        }
        
        for task in self.tasks.values():
            # 按状态统计
            status = task.status
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # 按优先级统计
            priority = task.priority
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # 按分配用户统计
            if task.assigned_to:
                stats["by_user"][task.assigned_to] = stats["by_user"].get(task.assigned_to, 0) + 1
        
        return stats
    
    def search_tasks(self, query: str) -> List[Task]:
        """搜索任务"""
        query_lower = query.lower()
        
        return [
            task for task in self.tasks.values()
            if (query_lower in task.title.lower() or
                query_lower in task.description.lower() or
                any(query_lower in tag.lower() for tag in task.tags) or
                any(query_lower in comment.content.lower() for comment in task.comments))
        ]
    
    def _load_tasks(self):
        """加载任务"""
        if not self.storage_path.exists():
            logger.info("创建新任务存储")
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for task_data in data.get("tasks", []):
                task = Task.from_dict(task_data)
                self.tasks[task.id] = task
            
            self._next_id = data.get("next_id", 1)
            self._comment_counter = data.get("comment_counter", 0)
            
            logger.info(f"加载 {len(self.tasks)} 个任务")
        except Exception as e:
            logger.error(f"加载任务失败：{e}")
    
    def _save_tasks(self):
        """保存任务"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "next_id": self._next_id,
            "comment_counter": self._comment_counter,
            "updated_at": datetime.now().isoformat(),
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug("任务已保存")
    
    def export_tasks(self, output_path: str, task_ids: List[int] = None):
        """导出任务"""
        if task_ids:
            tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]
        else:
            tasks = list(self.tasks.values())
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total": len(tasks),
            "tasks": [t.to_dict() for t in tasks],
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"导出 {len(tasks)} 个任务到：{output_path}")
    
    def import_tasks(self, input_path: str, merge: bool = True):
        """导入任务"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not merge and not data.get("tasks"):
            self.tasks.clear()
        
        for task_data in data.get("tasks", []):
            task = Task.from_dict(task_data)
            self.tasks[task.id] = task
        
        self._next_id = max(self.tasks.keys(), default=0) + 1
        self._save_tasks()
        
        logger.info(f"导入 {len(data.get('tasks', []))} 个任务")
