"""
执行引擎

核心执行引擎，负责任务调度和执行
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.task import Task, TaskStatus, TaskResult
from ..agents.base_agent import BaseAgent
from ..plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """执行引擎"""
    
    def __init__(self):
        self.agent_manager = None  # TODO: 初始化 Agent 管理器
        self.plugin_manager = None  # TODO: 初始化插件管理器
        self.task_manager = None    # TODO: 初始化任务管理器
    
    async def execute(self, task: Task) -> TaskResult:
        """
        执行任务
        
        流程：
        1. 解析任务
        2. 选择 Agent
        3. 执行任务
        4. 返回结果
        """
        logger.info(f"开始执行任务：{task.id}")
        
        try:
            # 1. 更新任务状态
            task.status = TaskStatus.RUNNING
            task.updated_at = datetime.now()
            
            # 2. 选择 Agent
            agent = await self._select_agent(task)
            if not agent:
                raise ValueError(f"未找到合适的 Agent 处理任务：{task.type}")
            
            logger.info(f"选择 Agent: {agent.name}")
            
            # 3. 执行任务
            result = await agent.execute(task)
            
            # 4. 更新任务
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.updated_at = datetime.now()
            
            logger.info(f"任务执行完成：{task.id}")
            
            return result
        
        except Exception as e:
            logger.error(f"任务执行失败：{task.id}, 错误：{e}")
            task.status = TaskStatus.FAILED
            task.result = TaskResult(success=False, error=str(e))
            task.updated_at = datetime.now()
            
            return TaskResult(success=False, error=str(e))
    
    async def _select_agent(self, task: Task) -> Optional[BaseAgent]:
        """
        选择 Agent
        
        策略：
        1. 如果任务指定了 Agent，直接使用
        2. 否则根据任务类型选择
        """
        if task.agent:
            # 指定 Agent
            return self.agent_manager.get(task.agent)
        
        # 根据任务类型选择
        return self.agent_manager.select_for_task(task)
    
    async def plan_task(self, task: Task) -> list:
        """
        规划任务
        
        将复杂任务拆解为多个步骤
        """
        # TODO: 实现任务规划
        return [task]
