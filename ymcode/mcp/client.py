#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - MCP 协议客户端

融合课程：生产级 MCP 协议 + 工具市场接入
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MCPTool:
    """MCP 工具定义"""
    name: str
    description: str
    input_schema: Dict
    server_url: str


class MCPClient:
    """MCP 客户端"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 MCP 客户端
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.servers: Dict[str, str] = {}  # server_name -> server_url
        self.tools: Dict[str, MCPTool] = {}
        self.session = None
        
        logger.info("MCP 客户端初始化完成")
    
    async def connect(self, server_name: str, server_url: str):
        """
        连接到 MCP 服务器
        
        参数:
            server_name: 服务器名称
            server_url: 服务器 URL
        """
        self.servers[server_name] = server_url
        logger.info(f"连接到 MCP 服务器：{server_name} ({server_url})")
        
        # 获取服务器工具列表
        await self._fetch_tools(server_name, server_url)
    
    async def _fetch_tools(self, server_name: str, server_url: str):
        """
        获取服务器工具列表
        
        参数:
            server_name: 服务器名称
            server_url: 服务器 URL
        """
        try:
            # 模拟获取工具列表（实际应该调用 MCP API）
            # GET {server_url}/tools
            logger.info(f"获取服务器工具列表：{server_name}")
            
            # 示例工具（实际从服务器获取）
            example_tools = [
                {
                    "name": f"{server_name}_search",
                    "description": f"Search using {server_name}",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            ]
            
            for tool_data in example_tools:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["input_schema"],
                    server_url=server_url
                )
                self.tools[tool.name] = tool
            
            logger.info(f"从 {server_name} 获取到 {len(example_tools)} 个工具")
            
        except Exception as e:
            logger.error(f"获取工具列表失败 {server_name}: {e}")
    
    async def list_tools(self) -> List[MCPTool]:
        """
        列出所有可用工具
        
        返回:
            工具列表
        """
        return list(self.tools.values())
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        调用远程工具
        
        参数:
            tool_name: 工具名称
            **kwargs: 工具参数
        
        返回:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"未知工具：{tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"调用远程工具：{tool_name}")
            
            # 模拟调用（实际应该发送 HTTP 请求）
            # POST {tool.server_url}/tools/{tool_name}
            # Body: kwargs
            
            # 模拟响应
            result = {
                "success": True,
                "tool": tool_name,
                "input": kwargs,
                "output": f"Mock result from {tool_name}"
            }
            
            logger.info(f"远程工具调用成功：{tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"远程工具调用失败 {tool_name}: {e}")
            raise
    
    async def disconnect(self, server_name: str = None):
        """
        断开连接
        
        参数:
            server_name: 服务器名称（可选，默认断开所有）
        """
        if server_name:
            if server_name in self.servers:
                del self.servers[server_name]
                logger.info(f"断开 MCP 服务器：{server_name}")
        else:
            self.servers.clear()
            self.tools.clear()
            logger.info("断开所有 MCP 服务器")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        返回:
            统计字典
        """
        return {
            "connected_servers": len(self.servers),
            "available_tools": len(self.tools),
            "servers": list(self.servers.keys())
        }


class MCPToolRegistry:
    """MCP 工具注册表"""
    
    def __init__(self, mcp_client: MCPClient):
        """
        初始化 MCP 工具注册表
        
        参数:
            mcp_client: MCP 客户端
        """
        self.mcp_client = mcp_client
        self.local_tools = {}
    
    def register_local_tool(self, tool):
        """
        注册本地工具
        
        参数:
            tool: 本地工具实例
        """
        self.local_tools[tool.name] = tool
        logger.info(f"注册本地工具：{tool.name}")
    
    async def sync_remote_tools(self):
        """同步远程工具"""
        remote_tools = await self.mcp_client.list_tools()
        
        for tool in remote_tools:
            # 创建远程工具包装器
            wrapper = self._create_remote_tool_wrapper(tool)
            self.local_tools[tool.name] = wrapper
        
        logger.info(f"同步 {len(remote_tools)} 个远程工具")
    
    def _create_remote_tool_wrapper(self, mcp_tool: MCPTool):
        """
        创建远程工具包装器
        
        参数:
            mcp_tool: MCP 工具
        
        返回:
            工具包装器
        """
        class RemoteToolWrapper:
            def __init__(self, mcp_tool, mcp_client):
                self.name = mcp_tool.name
                self.description = mcp_tool.description
                self.input_schema = mcp_tool.input_schema
                self.mcp_client = mcp_client
            
            async def execute(self, **kwargs):
                return await self.mcp_client.call_tool(self.name, **kwargs)
        
        return RemoteToolWrapper(mcp_tool, self.mcp_client)
    
    def get_all_tools(self) -> Dict:
        """获取所有工具"""
        return self.local_tools.copy()
