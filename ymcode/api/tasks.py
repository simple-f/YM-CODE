#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理 API - 任务创建、跟踪、管理
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskStatus(str, Enum):
    INBOX = "inbox"
    SPEC = "spec"
    BUILD = "build"
    REVIEW = "review"
    DONE = "done"


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.INBOX
    priority: int = 3  # 1-5, 5 最高
    created_at: str
    updated_at: str
    session_id: Optional[str] = None
    tags: List[str] = []


# 内存存储（后续可替换为数据库）
tasks_store: Dict[str, Task] = {}


@router.get("/list")
async def list_tasks(status: str = None):
    """获取任务列表"""
    tasks = list(tasks_store.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    # 按优先级和创建时间排序
    tasks.sort(key=lambda x: (-x.priority, x.created_at))
    
    return {
        "tasks": tasks,
        "total": len(tasks),
        "by_status": {
            "inbox": len([t for t in tasks if t.status == TaskStatus.INBOX]),
            "spec": len([t for t in tasks if t.status == TaskStatus.SPEC]),
            "build": len([t for t in tasks if t.status == TaskStatus.BUILD]),
            "review": len([t for t in tasks if t.status == TaskStatus.REVIEW]),
            "done": len([t for t in tasks if t.status == TaskStatus.DONE])
        }
    }


@router.get("/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return tasks_store[task_id]


@router.post("/create")
async def create_task(title: str, description: str = "", priority: int = 3):
    """创建任务"""
    import uuid
    
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    task = Task(
        id=task_id,
        title=title,
        description=description,
        priority=priority,
        created_at=now,
        updated_at=now
    )
    
    tasks_store[task_id] = task
    
    return {
        "success": True,
        "task": task
    }


@router.post("/update/{task_id}")
async def update_task(task_id: str, status: str = None, priority: int = None):
    """更新任务"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_store[task_id]
    
    if status:
        task.status = TaskStatus(status)
    if priority:
        task.priority = priority
    
    task.updated_at = datetime.now().isoformat()
    
    return {
        "success": True,
        "task": task
    }


@router.post("/move/{task_id}")
async def move_task(task_id: str, new_status: str):
    """移动任务到下一个状态"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_store[task_id]
    old_status = task.status
    
    try:
        task.status = TaskStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态")
    
    task.updated_at = datetime.now().isoformat()
    
    logger.info(f"任务 {task_id} 从 {old_status} 移动到 {new_status}")
    
    return {
        "success": True,
        "task": task,
        "old_status": old_status,
        "new_status": new_status
    }


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del tasks_store[task_id]
    
    return {
        "success": True,
        "message": f"任务 {task_id} 已删除"
    }


@router.get("/stats/summary")
async def get_stats():
    """获取任务统计"""
    tasks = list(tasks_store.values())
    
    return {
        "total": len(tasks),
        "by_status": {
            "inbox": len([t for t in tasks if t.status == TaskStatus.INBOX]),
            "spec": len([t for t in tasks if t.status == TaskStatus.SPEC]),
            "build": len([t for t in tasks if t.status == TaskStatus.BUILD]),
            "review": len([t for t in tasks if t.status == TaskStatus.REVIEW]),
            "done": len([t for t in tasks if t.status == TaskStatus.DONE])
        },
        "avg_priority": sum(t.priority for t in tasks) / len(tasks) if tasks else 0
    }
