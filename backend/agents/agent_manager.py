"""
Agent 管理器

负责 Agent 的注册、选择和管理
"""

import logging
from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent
from ..models.task import Task

logger = logging.getLogger(__name__)


class AgentManager:
    """Agent 管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_classes: Dict[str, Type[BaseAgent]] = {}
    
    def register(self, agent: BaseAgent) -> bool:
        """
        注册 Agent
        
        参数:
            agent: Agent 实例
        
        返回:
            是否成功
        """
        if agent.name in self.agents:
            logger.warning(f"Agent 已存在：{agent.name}")
            return False
        
        self.agents[agent.name] = agent
        logger.info(f"注册 Agent: {agent.name}")
        return True
    
    def register_class(self, agent_class: Type[BaseAgent]) -> bool:
        """
        注册 Agent 类
        
        参数:
            agent_class: Agent 类
        
        返回:
            是否成功
        """
        # 创建实例获取名称
        try:
            instance = agent_class()
            name = instance.name
            self.agent_classes[name] = agent_class
            logger.info(f"注册 Agent 类：{name}")
            return True
        except Exception as e:
            logger.error(f"注册 Agent 类失败：{e}")
            return False
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """
        获取 Agent
        
        参数:
            name: Agent 名称
        
        返回:
            Agent 实例
        """
        if name not in self.agents:
            # 尝试从类创建
            if name in self.agent_classes:
                try:
                    agent = self.agent_classes[name]()
                    self.agents[name] = agent
                    return agent
                except Exception as e:
                    logger.error(f"创建 Agent 失败：{e}")
                    return None
            return None
        
        return self.agents[name]
    
    def list_agents(self) -> List[Dict]:
        """
        列出所有 Agent
        
        返回:
            Agent 信息列表
        """
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities
            }
            for agent in self.agents.values()
        ]
    
    def select_for_task(self, task: Task) -> Optional[BaseAgent]:
        """
        为任务选择合适的 Agent
        
        参数:
            task: 任务
        
        返回:
            最合适的 Agent
        """
        # 根据任务类型选择
        for agent in self.agents.values():
            if agent.can_handle(task.type):
                logger.info(f"为任务选择 Agent: {agent.name}")
                return agent
        
        # 如果没有匹配的，返回第一个可用的
        if self.agents:
            return list(self.agents.values())[0]
        
        return None
    
    async def initialize_all(self) -> None:
        """初始化所有 Agent"""
        for agent in self.agents.values():
            try:
                await agent.initialize()
                logger.info(f"Agent 初始化完成：{agent.name}")
            except Exception as e:
                logger.error(f"Agent 初始化失败 {agent.name}: {e}")
    
    async def cleanup_all(self) -> None:
        """清理所有 Agent"""
        for agent in self.agents.values():
            try:
                await agent.cleanup()
                logger.info(f"Agent 清理完成：{agent.name}")
            except Exception as e:
                logger.error(f"Agent 清理失败 {agent.name}: {e}")
