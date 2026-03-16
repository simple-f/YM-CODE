"""
任务服务

提供任务相关的业务逻辑
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from ..models.task import Task, TaskStatus, TaskResult

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务"""
    
    # 临时存储（后续替换为数据库）
    _tasks_db: Dict[str, Task] = {}
    
    @classmethod
    async def create(cls, task_data: Dict) -> Task:
        """
        创建任务
        
        参数:
            task_data: 任务数据
        
        返回:
            任务实例
        """
        task = Task(**task_data)
        cls._tasks_db[task.id] = task
        logger.info(f"创建任务：{task.id}")
        return task
    
    @classmethod
    async def get(cls, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            任务实例
        """
        return cls._tasks_db.get(task_id)
    
    @classmethod
    async def list(cls, status: Optional[TaskStatus] = None) -> List[Task]:
        """
        查询任务列表
        
        参数:
            status: 状态过滤（可选）
        
        返回:
            任务列表
        """
        tasks = list(cls._tasks_db.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # 按创建时间倒序
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return tasks
    
    @classmethod
    async def update(cls, task_id: str, updates: Dict) -> Optional[Task]:
        """
        更新任务
        
        参数:
            task_id: 任务 ID
            updates: 更新数据
        
        返回:
            更新后的任务
        """
        task = cls._tasks_db.get(task_id)
        if not task:
            return None
        
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        logger.info(f"更新任务：{task_id}")
        
        return task
    
    @classmethod
    async def delete(cls, task_id: str) -> bool:
        """
        删除任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            是否成功
        """
        if task_id in cls._tasks_db:
            del cls._tasks_db[task_id]
            logger.info(f"删除任务：{task_id}")
            return True
        return False
    
    @classmethod
    async def update_status(cls, task_id: str, status: TaskStatus) -> Optional[Task]:
        """
        更新任务状态
        
        参数:
            task_id: 任务 ID
            status: 新状态
        
        返回:
            更新后的任务
        """
        return await cls.update(task_id, {"status": status})
    
    @classmethod
    async def complete(cls, task_id: str, result: TaskResult) -> Optional[Task]:
        """
        完成任务
        
        参数:
            task_id: 任务 ID
            result: 执行结果
        
        返回:
            更新后的任务
        """
        updates = {
            "status": TaskStatus.COMPLETED if result.success else TaskStatus.FAILED,
            "result": result,
            "completed_at": datetime.now()
        }
        return await cls.update(task_id, updates)
