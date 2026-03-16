"""
任务 API

提供任务创建、查询、管理等接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()

# 临时存储（后续替换为数据库）
tasks_db = {}


class TaskCreate(BaseModel):
    """任务创建请求"""
    name: str
    description: Optional[str] = None
    agent: Optional[str] = None
    plugins: Optional[List[str]] = None
    params: Optional[dict] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    description: Optional[str]
    status: str  # pending, running, completed, failed
    agent: Optional[str]
    plugins: Optional[List[str]]
    params: Optional[dict]
    result: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """
    创建任务
    
    - **name**: 任务名称
    - **description**: 任务描述
    - **agent**: 指定 Agent（可选）
    - **plugins**: 使用的插件列表（可选）
    - **params**: 任务参数（可选）
    """
    task_id = str(uuid.uuid4())
    
    task_data = {
        "id": task_id,
        "name": task.name,
        "description": task.description,
        "status": "pending",
        "agent": task.agent,
        "plugins": task.plugins or [],
        "params": task.params or {},
        "result": None,
        "created_at": datetime.now(),
        "updated_at": None
    }
    
    tasks_db[task_id] = task_data
    
    # TODO: 触发任务执行
    # await execute_task(task_id)
    
    return TaskResponse(**task_data)


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(status: Optional[str] = None):
    """
    查询任务列表
    
    - **status**: 按状态过滤（可选）
    """
    tasks = list(tasks_db.values())
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    # 按创建时间倒序
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [TaskResponse(**t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    查询任务详情
    
    - **task_id**: 任务 ID
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskResponse(**tasks_db[task_id])


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    
    - **task_id**: 任务 ID
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del tasks_db[task_id]
    return {"message": "任务已删除"}
