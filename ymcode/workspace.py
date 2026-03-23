#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作区管理模块

每个工作区独立，用户可以自定义加入哪些 Agent
"""

import logging
import uuid
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ymcode.utils.logger import get_logger
from ymcode.agents.base import get_agent_registry, BaseAgent

logger = get_logger(__name__)


class Workspace:
    """工作区类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化工作区
        
        参数:
            name: 工作区名称
            description: 工作区描述
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.agents: Dict[str, BaseAgent] = {}
        self.sessions: List[Dict] = []
        self.metadata = {}
        
        logger.info(f"创建工作区：{name} (ID: {self.id})")
    
    def add_agent(self, agent: BaseAgent) -> bool:
        """
        添加 Agent 到工作区
        
        参数:
            agent: Agent 实例
        
        返回:
            是否成功
        """
        if agent.name in self.agents:
            logger.warning(f"Agent 已在工作区中：{agent.name}")
            return False
        
        self.agents[agent.name] = agent
        logger.info(f"工作区 [{self.name}] 添加 Agent: {agent.name}")
        return True
    
    def remove_agent(self, agent_name: str) -> bool:
        """
        从工作区移除 Agent
        
        参数:
            agent_name: Agent 名称
        
        返回:
            是否成功
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent 不在工作区中：{agent_name}")
            return False
        
        del self.agents[agent_name]
        logger.info(f"工作区 [{self.name}] 移除 Agent: {agent_name}")
        return True
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """获取工作区中的 Agent"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict]:
        """列出工作区中的所有 Agent"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def create_session(self, name: str = None) -> Dict:
        """
        创建工作区会话
        
        参数:
            name: 会话名称
        
        返回:
            会话信息
        """
        session = {
            "id": str(uuid.uuid4()),
            "name": name or f"Session {len(self.sessions) + 1}",
            "created_at": datetime.now(),
            "messages": [],
            "context": {}
        }
        
        self.sessions.append(session)
        logger.info(f"工作区 [{self.name}] 创建会话：{session['name']}")
        return session
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "agent_count": len(self.agents),
            "agents": self.list_agents(),
            "session_count": len(self.sessions),
            "metadata": self.metadata
        }


class WorkspaceManager:
    """工作区管理器"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        初始化工作区管理器
        
        参数:
            workspace_dir: 工作区存储目录
        """
        if workspace_dir is None:
            workspace_dir = str(Path.home() / '.ymcode' / 'workspaces')
        
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.workspaces: Dict[str, Workspace] = {}
        self.current_workspace: Optional[Workspace] = None
        
        logger.info(f"工作区管理器初始化：{workspace_dir}")
        self._load_workspaces()
    
    def _load_workspaces(self):
        """加载已存在的工作区"""
        # TODO: 从磁盘加载工作区
        logger.info("加载已存在的工作区")
    
    def create_workspace(self, name: str, description: str = "") -> Workspace:
        """
        创建新工作区
        
        参数:
            name: 工作区名称
            description: 工作区描述
        
        返回:
            Workspace 实例
        """
        workspace = Workspace(name, description)
        self.workspaces[workspace.id] = workspace
        
        # 自动保存
        self._save_workspace(workspace)
        
        logger.info(f"创建新工作区：{name}")
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """获取工作区"""
        return self.workspaces.get(workspace_id)
    
    def switch_workspace(self, workspace_id: str) -> bool:
        """
        切换到指定工作区
        
        参数:
            workspace_id: 工作区 ID
        
        返回:
            是否成功
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            logger.error(f"工作区不存在：{workspace_id}")
            return False
        
        self.current_workspace = workspace
        logger.info(f"切换到工作区：{workspace.name}")
        return True
    
    def list_workspaces(self) -> List[Dict]:
        """列出所有工作区"""
        return [ws.to_dict() for ws in self.workspaces.values()]
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """
        删除工作区
        
        参数:
            workspace_id: 工作区 ID
        
        返回:
            是否成功
        """
        if workspace_id not in self.workspaces:
            logger.warning(f"工作区不存在：{workspace_id}")
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # 如果删除的是当前工作区，切换到 None
        if self.current_workspace and self.current_workspace.id == workspace_id:
            self.current_workspace = None
        
        del self.workspaces[workspace_id]
        logger.info(f"删除工作区：{workspace.name}")
        return True
    
    def _save_workspace(self, workspace: Workspace):
        """保存工作区到磁盘"""
        # TODO: 实现持久化
        pass
    
    def get_current_workspace(self) -> Optional[Workspace]:
        """获取当前工作区"""
        return self.current_workspace
    
    def create_session_in_current(self, name: str = None) -> Optional[Dict]:
        """在当前工作区创建会话"""
        if not self.current_workspace:
            logger.error("没有当前工作区")
            return None
        
        return self.current_workspace.create_session(name)


# 全局工作区管理器实例
_manager: Optional[WorkspaceManager] = None

def get_workspace_manager() -> WorkspaceManager:
    """获取全局工作区管理器"""
    global _manager
    if _manager is None:
        _manager = WorkspaceManager()
    return _manager


# 便捷函数
def create_workspace(name: str, description: str = "") -> Workspace:
    """创建工作区"""
    manager = get_workspace_manager()
    return manager.create_workspace(name, description)


def switch_workspace(workspace_id: str) -> bool:
    """切换工作区"""
    manager = get_workspace_manager()
    return manager.switch_workspace(workspace_id)


def get_current_workspace() -> Optional[Workspace]:
    """获取当前工作区"""
    manager = get_workspace_manager()
    return manager.get_current_workspace()


def add_agent_to_current_workspace(agent: BaseAgent) -> bool:
    """添加 Agent 到当前工作区"""
    workspace = get_current_workspace()
    if not workspace:
        logger.error("没有当前工作区")
        return False
    
    return workspace.add_agent(agent)


def list_available_agents() -> List[Dict]:
    """列出所有可用的 Agent（从注册表）"""
    registry = get_agent_registry()
    return registry.list_agents()


def list_workspace_agents() -> List[Dict]:
    """列出当前工作区的 Agent"""
    workspace = get_current_workspace()
    if not workspace:
        return []
    return workspace.list_agents()
