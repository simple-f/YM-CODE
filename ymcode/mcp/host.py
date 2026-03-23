#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Host - MCP 宿主层

负责管理 MCP Client 生命周期、配置和协调
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from .client import MCPClient
from .server_registry import MCPServerRegistry
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HostConfig:
    """Host 配置"""
    name: str = "ym-code"
    version: str = "1.0.0"
    max_clients: int = 10
    connection_timeout: int = 30
    retry_attempts: int = 3
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "max_clients": self.max_clients,
            "connection_timeout": self.connection_timeout,
            "retry_attempts": self.retry_attempts,
            "log_level": self.log_level
        }


class MCPHost:
    """
    MCP 宿主基类
    
    职责:
    - 管理多个 MCP Client
    - 配置管理
    - 生命周期管理
    - 错误恢复
    - 安全验证
    
    使用示例:
        >>> host = MCPHost()
        >>> await host.initialize()
        >>> await host.connect_client("filesystem", "npx -y @mcp/server-filesystem")
        >>> tools = await host.list_all_tools()
        >>> result = await host.call_tool("read_file", {"path": "/etc/hosts"})
        >>> await host.shutdown()
    """
    
    def __init__(self, config: Optional[HostConfig] = None):
        """
        初始化 MCP Host
        
        参数:
            config: Host 配置（可选）
        """
        self.config = config or HostConfig()
        self.clients: Dict[str, MCPClient] = {}
        self.server_registry = MCPServerRegistry()
        self._initialized = False
        self._running = False
        self._lock = asyncio.Lock()
        
        logger.info(f"MCPHost 初始化完成 (name={self.config.name})")
    
    async def initialize(self) -> bool:
        """
        初始化 Host
        
        返回:
            是否成功
        """
        logger.info("正在初始化 MCP Host...")
        
        try:
            # 验证配置
            self._validate_config()
            
            # 加载 Server 配置
            self._load_server_configs()
            
            self._initialized = True
            
            logger.info("MCP Host 初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"MCP Host 初始化失败：{e}")
            return False
    
    async def connect_client(
        self,
        client_id: str,
        server_name: str,
        server_url: str,
        retry: bool = True
    ) -> bool:
        """
        连接 MCP Client
        
        参数:
            client_id: Client 唯一标识
            server_name: Server 名称
            server_url: Server URL
            retry: 是否自动重试
        
        返回:
            是否成功
        """
        if not self._initialized:
            logger.error("Host 未初始化，无法连接 Client")
            return False
        
        if len(self.clients) >= self.config.max_clients:
            logger.error(f"已达到最大 Client 数量限制：{self.config.max_clients}")
            return False
        
        async with self._lock:
            if client_id in self.clients:
                logger.warning(f"Client 已存在：{client_id}")
                return True
            
            client = MCPClient()
            
            # 连接逻辑
            success = await self._connect_with_retry(
                client,
                server_name,
                server_url,
                retry
            )
            
            if success:
                self.clients[client_id] = client
                logger.info(f"Client 已连接：{client_id} -> {server_name}")
            else:
                logger.error(f"Client 连接失败：{client_id} -> {server_name}")
            
            return success
    
    async def disconnect_client(self, client_id: str) -> bool:
        """
        断开 Client 连接
        
        参数:
            client_id: Client ID
        
        返回:
            是否成功
        """
        async with self._lock:
            if client_id not in self.clients:
                logger.warning(f"Client 不存在：{client_id}")
                return False
            
            client = self.clients[client_id]
            await client.disconnect()
            del self.clients[client_id]
            
            logger.info(f"Client 已断开：{client_id}")
            return True
    
    async def list_all_tools(self) -> List[Dict]:
        """
        列出所有可用工具
        
        返回:
            工具列表
        """
        all_tools = []
        
        for client_id, client in self.clients.items():
            try:
                tools = await client.list_tools()
                for tool in tools:
                    tool["client_id"] = client_id
                    all_tools.append(tool)
            except Exception as e:
                logger.error(f"获取 Client {client_id} 工具列表失败：{e}")
        
        return all_tools
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        client_id: Optional[str] = None
    ) -> Any:
        """
        调用工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数
            client_id: Client ID（可选，自动选择如果为 None）
        
        返回:
            工具执行结果
        """
        # 验证参数
        self._validate_tool_arguments(tool_name, arguments)
        
        # 选择 Client
        if client_id:
            if client_id not in self.clients:
                raise ValueError(f"Client 不存在：{client_id}")
            client = self.clients[client_id]
        else:
            # 自动选择第一个可用的 Client
            client = await self._select_client(tool_name)
            if not client:
                raise ValueError(f"没有可用的 Client 执行工具：{tool_name}")
        
        # 调用工具
        try:
            result = await client.call_tool(tool_name, arguments)
            logger.info(f"工具调用成功：{tool_name}")
            return result
        except Exception as e:
            logger.error(f"工具调用失败：{tool_name} - {e}")
            raise
    
    async def shutdown(self):
        """关闭 Host，断开所有 Client"""
        logger.info("正在关闭 MCP Host...")
        
        self._running = False
        
        # 断开所有 Client
        for client_id in list(self.clients.keys()):
            try:
                await self.disconnect_client(client_id)
            except Exception as e:
                logger.error(f"断开 Client {client_id} 失败：{e}")
        
        self._initialized = False
        logger.info("MCP Host 已关闭")
    
    def get_status(self) -> Dict:
        """
        获取 Host 状态
        
        返回:
            状态字典
        """
        return {
            "name": self.config.name,
            "version": self.config.version,
            "initialized": self._initialized,
            "running": self._running,
            "client_count": len(self.clients),
            "max_clients": self.config.max_clients,
            "clients": list(self.clients.keys())
        }
    
    def _validate_config(self):
        """验证配置"""
        if self.config.max_clients < 1:
            raise ValueError("max_clients 必须大于 0")
        if self.config.connection_timeout < 1:
            raise ValueError("connection_timeout 必须大于 0")
        if self.config.retry_attempts < 0:
            raise ValueError("retry_attempts 不能为负数")
    
    def _load_server_configs(self):
        """加载 Server 配置"""
        # 从注册表加载预定义 Server
        registry = self.server_registry
        logger.info(f"已加载 {len(registry.list_servers())} 个 Server 配置")
    
    async def _connect_with_retry(
        self,
        client: MCPClient,
        server_name: str,
        server_url: str,
        retry: bool
    ) -> bool:
        """带重试的连接"""
        attempts = 0
        max_attempts = self.config.retry_attempts if retry else 1
        
        while attempts < max_attempts:
            try:
                success = await client.connect(server_name, server_url)
                if success:
                    return True
            except Exception as e:
                attempts += 1
                logger.warning(f"连接失败 (尝试 {attempts}/{max_attempts}): {e}")
                
                if attempts < max_attempts:
                    await asyncio.sleep(1 * attempts)  # 指数退避
        
        return False
    
    def _validate_tool_arguments(self, tool_name: str, arguments: Dict):
        """验证工具参数"""
        if not isinstance(arguments, dict):
            raise ValueError(f"工具参数必须是字典：{tool_name}")
        
        # 安全检查：防止注入攻击
        for key, value in arguments.items():
            if isinstance(value, str):
                # 检查危险字符
                if any(char in value for char in ["\x00", "\n", "\r"]):
                    raise ValueError(f"工具参数包含非法字符：{key}")
    
    async def _select_client(self, tool_name: str) -> Optional[MCPClient]:
        """自动选择 Client"""
        # 简单策略：返回第一个可用的 Client
        for client in self.clients.values():
            try:
                tools = await client.list_tools()
                if any(t.name == tool_name for t in tools):
                    return client
            except:
                continue
        
        # 如果没有找到匹配的工具，返回第一个 Client
        return next(iter(self.clients.values()), None)
