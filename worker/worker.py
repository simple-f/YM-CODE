"""
Worker 工作节点

负责从队列拉取任务并执行
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from backend.core.engine import ExecutionEngine
from backend.models.task import Task

logger = logging.getLogger(__name__)


class Worker:
    """工作节点"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.engine = ExecutionEngine()
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
    
    async def start(self):
        """启动 Worker"""
        logger.info(f"Worker {self.worker_id} 启动")
        self.running = True
        
        while self.running:
            try:
                # 从队列拉取任务
                task = await self.fetch_task()
                
                if task:
                    # 执行任务
                    await self.execute_task(task)
                else:
                    # 无任务，等待
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Worker 执行错误：{e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """停止 Worker"""
        logger.info(f"Worker {self.worker_id} 停止")
        self.running = False
    
    async def fetch_task(self) -> Optional[Task]:
        """
        从队列拉取任务
        
        TODO: 实现从 Redis/Celery 队列拉取
        """
        # 临时返回 None
        return None
    
    async def execute_task(self, task: Task):
        """
        执行任务
        
        参数:
            task: 任务
        """
        logger.info(f"Worker {self.worker_id} 开始执行任务：{task.id}")
        
        self.current_task = task
        task.started_at = datetime.now()
        
        try:
            # 执行
            result = await self.engine.execute(task)
            
            # 更新统计
            self.tasks_processed += 1
            
            logger.info(f"任务执行完成：{task.id}")
        
        except Exception as e:
            logger.error(f"任务执行失败：{task.id}, 错误：{e}")
        
        finally:
            task.completed_at = datetime.now()
            self.current_task = None
    
    def get_stats(self) -> dict:
        """获取 Worker 统计"""
        return {
            "worker_id": self.worker_id,
            "running": self.running,
            "current_task": self.current_task.id if self.current_task else None,
            "tasks_processed": self.tasks_processed
        }
