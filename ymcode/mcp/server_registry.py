#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server 注册表
管理可用的 MCP Server 配置
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MCPServerConfig:
    """MCP Server 配置"""
    name: str
    type: str  # stdio, sse, http
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    description: str = ""
    tools: List[str] = None
    active: bool = True
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class MCPServerRegistry:
    """MCP Server 注册表"""
    
    # 预定义的 MCP Server 配置
    BUILTIN_SERVERS = {
        "filesystem": MCPServerConfig(
            name="filesystem",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
            description="本地文件系统访问",
            tools=["read_file", "write_file", "list_directory", "search_files"]
        ),
        "git": MCPServerConfig(
            name="git",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-git"],
            description="Git 仓库操作",
            tools=["git_status", "git_diff", "git_commit", "git_push"]
        ),
        "database": MCPServerConfig(
            name="database",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres"],
            description="PostgreSQL 数据库访问",
            tools=["query", "insert", "update", "delete"]
        ),
        "github": MCPServerConfig(
            name="github",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            description="GitHub API 访问",
            tools=["list_repos", "create_issue", "create_pr", "search_code"]
        ),
        "brave-search": MCPServerConfig(
            name="brave-search",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            description="Brave 搜索引擎",
            tools=["search", "news_search"]
        ),
        "memory": MCPServerConfig(
            name="memory",
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            description="持久化记忆存储",
            tools=["create_memory", "search_memories", "delete_memory"]
        )
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化注册表
        
        参数:
            config_path: 配置文件路径（可选）
        """
        self.config_path = config_path or Path.home() / ".ymcode" / "mcp_servers.json"
        self.custom_servers: Dict[str, MCPServerConfig] = {}
        self._load_config()
        
        logger.info(f"MCP Server 注册表初始化完成，内置 {len(self.BUILTIN_SERVERS)} 个服务器")
    
    def _load_config(self) -> None:
        """加载用户配置"""
        if not self.config_path.exists():
            logger.debug("用户配置文件不存在，使用默认配置")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for name, server_config in config.get('servers', {}).items():
                self.custom_servers[name] = MCPServerConfig(**server_config)
            
            logger.info(f"加载 {len(self.custom_servers)} 个自定义服务器配置")
        except Exception as e:
            logger.error(f"加载配置文件失败：{e}")
    
    def _save_config(self) -> None:
        """保存用户配置"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'servers': {
                    name: asdict(server) 
                    for name, server in self.custom_servers.items()
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("保存服务器配置")
        except Exception as e:
            logger.error(f"保存配置文件失败：{e}")
    
    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """
        获取服务器配置
        
        参数:
            name: 服务器名称
        
        返回:
            服务器配置，不存在返回 None
        """
        # 先查自定义
        if name in self.custom_servers:
            return self.custom_servers[name]
        
        # 再查内置
        if name in self.BUILTIN_SERVERS:
            return self.BUILTIN_SERVERS[name]
        
        return None
    
    def list_servers(self, active_only: bool = False) -> List[MCPServerConfig]:
        """
        列出所有服务器
        
        参数:
            active_only: 只列出激活的
        
        返回:
            服务器配置列表
        """
        all_servers = list(self.BUILTIN_SERVERS.values()) + list(self.custom_servers.values())
        
        if active_only:
            return [s for s in all_servers if s.active]
        
        return all_servers
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """
        添加自定义服务器
        
        参数:
            config: 服务器配置
        
        返回:
            是否成功
        """
        if config.name in self.BUILTIN_SERVERS:
            logger.warning(f"不能覆盖内置服务器：{config.name}")
            return False
        
        self.custom_servers[config.name] = config
        self._save_config()
        
        logger.info(f"添加自定义服务器：{config.name}")
        return True
    
    def remove_server(self, name: str) -> bool:
        """
        移除自定义服务器
        
        参数:
            name: 服务器名称
        
        返回:
            是否成功
        """
        if name in self.BUILTIN_SERVERS:
            logger.warning(f"不能移除内置服务器：{name}")
            return False
        
        if name in self.custom_servers:
            del self.custom_servers[name]
            self._save_config()
            logger.info(f"移除自定义服务器：{name}")
            return True
        
        logger.warning(f"服务器不存在：{name}")
        return False
    
    def update_server(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        更新服务器配置
        
        参数:
            name: 服务器名称
            updates: 更新内容
        
        返回:
            是否成功
        """
        if name in self.BUILTIN_SERVERS:
            logger.warning(f"不能更新内置服务器：{name}")
            return False
        
        if name not in self.custom_servers:
            logger.warning(f"服务器不存在：{name}")
            return False
        
        server = self.custom_servers[name]
        for key, value in updates.items():
            if hasattr(server, key):
                setattr(server, key, value)
        
        self._save_config()
        logger.info(f"更新服务器配置：{name}")
        return True
    
    def get_available_tools(self) -> List[str]:
        """
        获取所有可用的工具名称
        
        返回:
            工具名称列表
        """
        tools = []
        for server in self.list_servers():
            if server.active:
                tools.extend(server.tools)
        return list(set(tools))


# 全局注册表实例
_registry: Optional[MCPServerRegistry] = None


def get_registry(config_path: Optional[str] = None) -> MCPServerRegistry:
    """获取全局注册表实例"""
    global _registry
    if _registry is None:
        _registry = MCPServerRegistry(config_path)
    return _registry


def reset_registry() -> None:
    """重置注册表（用于测试）"""
    global _registry
    _registry = None
