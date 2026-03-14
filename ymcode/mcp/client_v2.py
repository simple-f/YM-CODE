#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client v2 - 支持 STDIO 传输的 MCP 客户端
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from .protocol import MCPProtocol, MCPTool, MCPResource
from .stdio_transport import STDIOTransport
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MCPClientV2:
    """MCP 客户端 v2（支持 STDIO 传输）"""
    
    def __init__(self):
        """初始化 MCP 客户端"""
        self.servers: Dict[str, STDIOTransport] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.connected = False
        
        logger.info("MCP Client v2 初始化完成")
    
    async def connect_stdio(self, server_name: str, command: str, args: list = None) -> bool:
        """
        通过 STDIO 连接到 MCP Server
        
        参数:
            server_name: 服务器名称
            command: 命令
            args: 参数
        
        返回:
            是否成功
        """
        logger.info(f"通过 STDIO 连接 MCP Server: {server_name} ({command})")
        
        try:
            # 创建 STDIO 传输
            transport = STDIOTransport(command, args)
            
            # 连接
            if not await transport.connect():
                return False
            
            # 初始化
            if not await transport.initialize():
                await transport.disconnect()
                return False
            
            # 获取工具列表
            tools = await transport.list_tools()
            for tool in tools:
                tool.server_name = server_name
                self.tools[tool.name] = tool
            
            # 获取资源列表
            resources = await transport.list_resources()
            for resource in resources:
                self.resources[resource.uri] = resource
            
            # 保存连接
            self.servers[server_name] = transport
            
            self.connected = True
            
            logger.info(f"MCP Server 连接成功：{server_name}, {len(tools)} 个工具，{len(resources)} 个资源")
            
            return True
            
        except Exception as e:
            logger.error(f"MCP Server 连接失败：{e}")
            return False
    
    async def disconnect(self, server_name: str = None) -> None:
        """
        断开连接
        
        参数:
            server_name: 服务器名称（可选，默认断开所有）
        """
        if server_name:
            if server_name in self.servers:
                await self.servers[server_name].disconnect()
                del self.servers[server_name]
                
                # 移除相关工具和资源
                self.tools = {k: v for k, v in self.tools.items() if v.server_name != server_name}
                
                logger.info(f"MCP Server 断开连接：{server_name}")
        else:
            # 断开所有连接
            for server in self.servers.values():
                await server.disconnect()
            
            self.servers.clear()
            self.tools.clear()
            self.resources.clear()
            self.connected = False
            
            logger.info("所有 MCP Server 断开连接")
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        调用工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数
        
        返回:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在：{tool_name}")
        
        tool = self.tools[tool_name]
        server_name = tool.server_name
        
        if server_name not in self.servers:
            raise ValueError(f"服务器未连接：{server_name}")
        
        transport = self.servers[server_name]
        
        logger.info(f"调用 MCP 工具：{tool_name}")
        
        return await transport.call_tool(tool_name, arguments)
    
    async def read_resource(self, uri: str) -> str:
        """
        读取资源
        
        参数:
            uri: 资源 URI
        
        返回:
            资源内容
        """
        if uri not in self.resources:
            raise ValueError(f"资源不存在：{uri}")
        
        # 找到资源所在的服务器
        for server_name, transport in self.servers.items():
            try:
                content = await transport.read_resource(uri)
                logger.info(f"读取 MCP 资源：{uri}")
                return content
            except Exception:
                continue
        
        raise ValueError(f"无法读取资源：{uri}")
    
    def get_tools_definition(self) -> List[Dict]:
        """
        获取工具定义（用于传递给 LLM）
        
        返回:
            工具定义列表
        """
        tools_def = []
        
        for tool in self.tools.values():
            tools_def.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        
        logger.debug(f"获取 MCP 工具定义：{len(tools_def)} 个")
        
        return tools_def
    
    def get_status(self) -> Dict:
        """
        获取状态信息
        
        返回:
            状态字典
        """
        return {
            "connected": self.connected,
            "servers": len(self.servers),
            "tools": len(self.tools),
            "resources": len(self.resources),
            "servers_list": list(self.servers.keys()),
            "tools_list": list(self.tools.keys()),
            "resources_list": list(self.resources.keys())
        }
