#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户自定义 Agent 框架

用户可以创建自己的 Agent 角色，定义专属能力
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import asyncio

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Agent 基类 - 用户创建自定义 Agent 时继承此类"""
    
    def __init__(self, name: str = None, description: str = None):
        """
        初始化 Agent
        
        参数:
            name: Agent 名称
            description: Agent 描述
        """
        self.name = name or self.__class__.__name__
        self.description = description or "自定义 Agent"
        self.enabled = True
        self.metadata = {}
        
        logger.info(f"Agent 初始化：{self.name}")
    
    @property
    @abstractmethod
    def role(self) -> str:
        """
        Agent 角色名称（由用户定义）
        
        例如："code_generator", "tester", "reviewer", "debugger"
        """
        pass
    
    @property
    def capabilities(self) -> List[str]:
        """
        Agent 能力列表（由用户定义）
        
        例如：["python", "javascript", "testing", "code_review"]
        """
        return []
    
    @abstractmethod
    async def execute(self, task: str, context: Dict = None) -> Dict:
        """
        执行任务（由用户实现具体逻辑）
        
        参数:
            task: 任务描述
            context: 上下文信息
        
        返回:
            执行结果
        """
        pass
    
    async def initialize(self) -> None:
        """初始化 Agent（可选）"""
        logger.info(f"Agent 初始化：{self.name}")
    
    async def cleanup(self) -> None:
        """清理资源（可选）"""
        logger.info(f"Agent 清理：{self.name}")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "capabilities": self.capabilities,
            "enabled": self.enabled,
            "metadata": self.metadata
        }


class UserAgent(BaseAgent):
    """用户自定义 Agent 的便捷实现"""
    
    def __init__(self, 
                 name: str,
                 role: str,
                 description: str = "",
                 capabilities: List[str] = None,
                 execute_func: Callable = None):
        """
        快速创建用户 Agent
        
        参数:
            name: Agent 名称
            role: Agent 角色
            description: Agent 描述
            capabilities: 能力列表
            execute_func: 执行函数
        """
        super().__init__(name, description)
        self._role = role
        self._capabilities = capabilities or []
        self._execute_func = execute_func
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def capabilities(self) -> List[str]:
        return self._capabilities
    
    async def execute(self, task: str, context: Dict = None) -> Dict:
        """执行任务"""
        if self._execute_func:
            if asyncio.iscoroutinefunction(self._execute_func):
                return await self._execute_func(task, context)
            else:
                return self._execute_func(task, context)
        
        # 默认实现 - 调用 LLM
        from ..core.llm import LLMClient
        llm = LLMClient()
        
        prompt = f"""你是一个 {self.role} 助手，名称是 {self.name}。
你的职责是：{self.description}
你的能力包括：{', '.join(self.capabilities)}

请完成以下任务：
{task}

上下文信息：
{context or '无'}
"""
        
        response = await llm.chat(prompt)
        return {
            "success": True,
            "result": response,
            "agent": self.name,
            "role": self.role
        }


class AgentRegistry:
    """Agent 注册表 - 管理所有用户创建的 Agent"""
    
    def __init__(self):
        """初始化注册表"""
        self.agents: Dict[str, BaseAgent] = {}
        logger.info("Agent 注册表初始化")
    
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
        logger.info(f"注册 Agent：{agent.name} (角色：{agent.role})")
        return True
    
    def unregister(self, agent_name: str) -> bool:
        """
        注销 Agent
        
        参数:
            agent_name: Agent 名称
        
        返回:
            是否成功
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent 不存在：{agent_name}")
            return False
        
        del self.agents[agent_name]
        logger.info(f"注销 Agent：{agent_name}")
        return True
    
    def get(self, agent_name: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(agent_name)
    
    def get_by_role(self, role: str) -> List[BaseAgent]:
        """根据角色获取 Agent"""
        return [a for a in self.agents.values() if a.role == role]
    
    def list_agents(self, role: Optional[str] = None) -> List[Dict]:
        """列出所有 Agent"""
        agents = self.agents.values()
        if role:
            agents = [a for a in agents if a.role == role]
        return [a.to_dict() for a in agents]
    
    def count(self) -> int:
        """获取 Agent 数量"""
        return len(self.agents)


# 全局注册表实例
_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """获取全局 Agent 注册表"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


# 便捷函数
def create_agent(name: str, 
                 role: str,
                 description: str = "",
                 capabilities: List[str] = None,
                 execute_func: Callable = None) -> UserAgent:
    """
    快速创建用户 Agent
    
    参数:
        name: Agent 名称
        role: Agent 角色
        description: Agent 描述
        capabilities: 能力列表
        execute_func: 执行函数
    
    返回:
        UserAgent 实例
    
    示例:
        # 创建代码生成 Agent
        coder = create_agent(
            name="PythonCoder",
            role="code_generator",
            description="专注于 Python 代码生成",
            capabilities=["python", "fastapi", "sqlalchemy"]
        )
        
        # 创建测试 Agent
        tester = create_agent(
            name="TestExpert",
            role="tester",
            description="编写单元测试和集成测试",
            capabilities=["pytest", "unittest", "mocking"]
        )
        
        # 注册 Agent
        registry = get_agent_registry()
        registry.register(coder)
        registry.register(tester)
    """
    return UserAgent(name, role, description, capabilities, execute_func)


def register_agent(name: str, 
                   role: str,
                   description: str = "",
                   capabilities: List[str] = None,
                   execute_func: Callable = None) -> bool:
    """
    快速创建并注册 Agent
    
    示例:
        register_agent(
            name="CodeReviewer",
            role="reviewer",
            description="代码审查专家",
            capabilities=["code_review", "security", "performance"]
        )
    """
    agent = create_agent(name, role, description, capabilities, execute_func)
    registry = get_agent_registry()
    return registry.register(agent)
