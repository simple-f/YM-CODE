#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 路由器
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from .base import BaseAgent
from .message import AgentMessage

logger = logging.getLogger(__name__)


class AgentRouter:
    """Agent 路由器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_memory: List[Dict] = []
        self._task_counter = 0
    
    def register_agent(self, name: str, agent: BaseAgent):
        """注册 Agent"""
        self.agents[name] = agent
        logger.info(f"注册 Agent: {name} ({agent.role})")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict]:
        """列出所有 Agent"""
        return [agent.get_status() for agent in self.agents.values()]
    
    async def route(self, message: AgentMessage, target: str = None) -> AgentMessage:
        """路由消息到 Agent"""
        if target and target in self.agents:
            # 指定 Agent
            agent = self.agents[target]
            logger.info(f"路由到 {target}")
            return await agent.process(message)
        else:
            # 自动路由
            return await self._auto_route(message)
    
    async def _auto_route(self, message: AgentMessage) -> AgentMessage:
        """自动路由（根据内容）"""
        content = message.content.lower()
        
        # 简单规则路由
        if any(word in content for word in ["创建", "实现", "编写", "build", "create", "write"]):
            target = "builder"
        elif any(word in content for word in ["审查", "review", "检查", "分析", "check", "analyze"]):
            target = "reviewer"
        elif any(word in content for word in ["测试", "test", "run test"]):
            target = "tester" if "tester" in self.agents else "builder"
        else:
            target = "builder"  # 默认
        
        agent = self.agents.get(target)
        if agent:
            logger.info(f"自动路由到 {target}")
            return await agent.process(message)
        else:
            return AgentMessage(
                sender="router",
                content=f"没有可用的 Agent: {target}"
            )
    
    def add_to_shared_memory(self, data: Dict):
        """添加到共享记忆"""
        self.shared_memory.append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近 1000 条
        if len(self.shared_memory) > 1000:
            self.shared_memory = self.shared_memory[-1000:]
    
    def get_shared_memory(self, limit: int = 100) -> List[Dict]:
        """获取共享记忆"""
        return self.shared_memory[-limit:]
    
    def search_shared_memory(self, query: str) -> List[Dict]:
        """搜索共享记忆"""
        query_lower = query.lower()
        return [
            mem for mem in self.shared_memory
            if query_lower in mem.get("content", "").lower()
        ]
    
    def create_task(self, title: str, assigned_to: str = None) -> Dict:
        """创建任务"""
        self._task_counter += 1
        task = {
            "id": self._task_counter,
            "title": title,
            "status": "pending",
            "assigned_to": assigned_to,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.add_to_shared_memory({
            "type": "task",
            "content": f"创建任务 #{self._task_counter}: {title}"
        })
        return task
    
    def complete_task(self, task_id: int):
        """完成任务"""
        for mem in reversed(self.shared_memory):
            if mem.get("type") == "task" and f"#{task_id}" in mem.get("content", ""):
                mem["status"] = "completed"
                mem["completed_at"] = datetime.now().isoformat()
                break
