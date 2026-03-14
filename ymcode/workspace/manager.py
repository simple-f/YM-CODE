#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作空间管理器 - 支持多工作空间

用户可以创建多个工作空间，每个工作空间有独立的配置和历史
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Workspace:
    """工作空间配置"""
    
    # 基础信息
    name: str
    path: str
    description: str = ""
    
    # 类型
    type: str = "default"  # default, project, sandbox
    
    # 关联的 Agent
    agent_identity: str = "YM-Assistant"
    
    # 配置
    config: Dict[str, Any] = None
    
    # 元数据
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class WorkspaceManager:
    """工作空间管理器"""
    
    DEFAULT_WORKSPACE_NAME = "default"
    
    def __init__(self, workspaces_dir: str = None):
        """
        初始化工作空间管理器
        
        参数:
            workspaces_dir: 工作空间根目录
        """
        self.workspaces_dir = Path(workspaces_dir) if workspaces_dir else Path.home() / '.ym-code' / 'workspaces'
        self.workspaces: Dict[str, Workspace] = {}
        self.current_workspace: Optional[str] = None
        
        # 确保目录存在
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载工作空间
        self._load_workspaces()
        
        logger.info(f"工作空间管理器初始化完成（目录：{self.workspaces_dir}）")
    
    def _load_workspaces(self) -> None:
        """加载工作空间"""
        index_file = self.workspaces_dir / 'workspaces.json'
        
        if not index_file.exists():
            # 创建默认工作空间
            self._create_default_workspace()
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for ws_data in data.get('workspaces', []):
                workspace = Workspace(**ws_data)
                self.workspaces[workspace.name] = workspace
            
            self.current_workspace = data.get('current', self.DEFAULT_WORKSPACE_NAME)
            
            logger.info(f"加载 {len(self.workspaces)} 个工作空间")
        except Exception as e:
            logger.warning(f"加载工作空间索引失败：{e}")
            self._create_default_workspace()
    
    def _create_default_workspace(self) -> Workspace:
        """创建默认工作空间"""
        workspace = Workspace(
            name=self.DEFAULT_WORKSPACE_NAME,
            path=str(self.workspaces_dir / self.DEFAULT_WORKSPACE_NAME),
            description="默认工作空间",
            type="default"
        )
        
        self.workspaces[self.DEFAULT_WORKSPACE_NAME] = workspace
        self.current_workspace = self.DEFAULT_WORKSPACE_NAME
        
        # 创建工作空间目录
        Path(workspace.path).mkdir(parents=True, exist_ok=True)
        
        # 初始化工作空间
        self._initialize_workspace(workspace)
        
        self._save_index()
        
        logger.info(f"创建默认工作空间：{self.DEFAULT_WORKSPACE_NAME}")
        
        return workspace
    
    def _initialize_workspace(self, workspace: Workspace) -> None:
        """初始化工作空间"""
        ws_path = Path(workspace.path)
        
        # 创建子目录
        (ws_path / 'config').mkdir(exist_ok=True)
        (ws_path / 'memory').mkdir(exist_ok=True)
        (ws_path / 'history').mkdir(exist_ok=True)
        (ws_path / 'cache').mkdir(exist_ok=True)
        
        # 创建工作空间配置
        config_file = ws_path / 'config' / 'workspace.yaml'
        if not config_file.exists():
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(f"""# {workspace.name} 工作空间配置

workspace:
  name: {workspace.name}
  type: {workspace.type}
  agent: {workspace.agent_identity}

# 项目特定配置
project:
  auto_index: true
  ignore:
    - node_modules/
    - __pycache__/
    - .git/
""")
        
        logger.debug(f"初始化工作空间：{workspace.name}")
    
    def create_workspace(self, name: str, description: str = "", type: str = "default", 
                        agent_identity: str = None, copy_from: str = None) -> Workspace:
        """
        创建工作空间
        
        参数:
            name: 工作空间名称
            description: 描述
            type: 类型（default/project/sandbox）
            agent_identity: 关联的 Agent 身份
            copy_from: 从哪个工作空间复制（可选）
        
        返回:
            创建的工作空间
        """
        if name in self.workspaces:
            raise ValueError(f"工作空间已存在：{name}")
        
        # 创建工作空间对象
        workspace = Workspace(
            name=name,
            path=str(self.workspaces_dir / name),
            description=description,
            type=type,
            agent_identity=agent_identity or "YM-Assistant"
        )
        
        # 创建目录
        ws_path = Path(workspace.path)
        
        if copy_from and copy_from in self.workspaces:
            # 从现有工作空间复制
            source_path = Path(self.workspaces[copy_from].path)
            if source_path.exists():
                shutil.copytree(source_path, ws_path)
                logger.info(f"从 {copy_from} 复制工作空间")
        else:
            # 新建
            ws_path.mkdir(parents=True, exist_ok=True)
            self._initialize_workspace(workspace)
        
        # 保存
        self.workspaces[name] = workspace
        self._save_index()
        
        logger.info(f"创建工作空间：{name}")
        
        return workspace
    
    def _save_index(self) -> None:
        """保存工作空间索引"""
        index_file = self.workspaces_dir / 'workspaces.json'
        
        data = {
            'workspaces': [ws.to_dict() for ws in self.workspaces.values()],
            'current': self.current_workspace
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_workspace(self, name: str) -> Optional[Workspace]:
        """获取工作空间"""
        return self.workspaces.get(name)
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """列出所有工作空间"""
        return [
            {
                'name': ws.name,
                'description': ws.description,
                'type': ws.type,
                'agent': ws.agent_identity,
                'current': ws.name == self.current_workspace,
                'created_at': ws.created_at
            }
            for ws in self.workspaces.values()
        ]
    
    def switch_workspace(self, name: str) -> bool:
        """切换工作空间"""
        if name not in self.workspaces:
            logger.warning(f"工作空间不存在：{name}")
            return False
        
        self.current_workspace = name
        self._save_index()
        
        logger.info(f"切换到工作空间：{name}")
        return True
    
    def get_current(self) -> Optional[Workspace]:
        """获取当前工作空间"""
        if not self.current_workspace:
            return None
        
        return self.workspaces.get(self.current_workspace)
    
    def delete_workspace(self, name: str) -> bool:
        """删除工作空间"""
        if name not in self.workspaces:
            return False
        
        if name == self.DEFAULT_WORKSPACE_NAME:
            logger.warning("不能删除默认工作空间")
            return False
        
        workspace = self.workspaces[name]
        
        # 删除目录
        ws_path = Path(workspace.path)
        if ws_path.exists():
            shutil.rmtree(ws_path)
        
        # 从索引中移除
        del self.workspaces[name]
        
        if self.current_workspace == name:
            self.current_workspace = self.DEFAULT_WORKSPACE_NAME
        
        self._save_index()
        
        logger.info(f"删除工作空间：{name}")
        return True
    
    def update_workspace(self, name: str, **kwargs) -> bool:
        """更新工作空间配置"""
        if name not in self.workspaces:
            return False
        
        workspace = self.workspaces[name]
        
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        
        workspace.updated_at = datetime.now().isoformat()
        self._save_index()
        
        logger.info(f"更新工作空间：{name}")
        return True
    
    def get_workspace_path(self, name: str = None) -> Path:
        """获取工作空间路径"""
        ws_name = name or self.current_workspace
        workspace = self.get_workspace(ws_name)
        
        if workspace:
            return Path(workspace.path)
        
        return self.workspaces_dir / self.DEFAULT_WORKSPACE_NAME


# 全局工作空间管理器
_manager: Optional[WorkspaceManager] = None


def get_workspace_manager() -> WorkspaceManager:
    """获取全局工作空间管理器"""
    global _manager
    if _manager is None:
        _manager = WorkspaceManager()
    return _manager


def create_workspace(name: str, **kwargs) -> Workspace:
    """便捷函数：创建工作空间"""
    return get_workspace_manager().create_workspace(name, **kwargs)


def switch_workspace(name: str) -> bool:
    """便捷函数：切换工作空间"""
    return get_workspace_manager().switch_workspace(name)


def get_current_workspace() -> Optional[Workspace]:
    """便捷函数：获取当前工作空间"""
    return get_workspace_manager().get_current()
