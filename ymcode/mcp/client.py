#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - Model Context Protocol 客户端

参考：https://github.com/anthropics/mcp
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MCPTool:
    """MCP 工具定义"""
    name: str
    description: str
    input_schema: Dict
    server_name: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPServer:
    """MCP 服务器"""
    name: str
    url: str
    connected: bool = False
    tools: List[MCPTool] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "url": self.url,
            "connected": self.connected,
            "tools": [t.to_dict() for t in self.tools]
        }


class MCPClient:
    """MCP 客户端"""
    
    def __init__(self):
        """初始化 MCP 客户端"""
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.connected = False
        
        logger.info("MCP Client 初始化完成")
    
    async def connect(self, server_name: str, url: str, timeout: int = 30) -> bool:
        """
        连接到 MCP 服务器
        
        参数:
            server_name: 服务器名称
            url: 服务器 URL
            timeout: 连接超时（秒，默认 30 秒）
        
        返回:
            是否成功
        """
        logger.info(f"正在连接到 MCP 服务器：{server_name} ({url})，超时={timeout}秒")
        
        try:
            # ✅ 添加超时控制
            await asyncio.wait_for(
                self._do_connect(server_name, url),
                timeout=timeout
            )
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"连接超时：{server_name}（超过{timeout}秒）")
            return False
        except Exception as e:
            logger.error(f"连接到 MCP 服务器失败：{e}")
            return False
    
    async def _do_connect(self, server_name: str, url: str) -> bool:
        """
        实际连接逻辑（内部方法）
        
        参数:
            server_name: 服务器名称
            url: 服务器 URL
        
        返回:
            是否成功
        """
        # 创建服务器对象
        server = MCPServer(name=server_name, url=url)
        
        # TODO: 实际连接到 MCP 服务器
        # 目前先模拟连接成功
        server.connected = True
        
        # 获取服务器工具列表
        await self._fetch_tools(server)
        
        # 注册服务器
        self.servers[server_name] = server
        
        # 注册工具
        for tool in server.tools:
            tool.server_name = server_name
            self.tools[tool.name] = tool
        
        self.connected = True
        
        logger.info(f"成功连接到 MCP 服务器：{server_name}")
        logger.info(f"发现 {len(server.tools)} 个工具")
        
        return True
    
    async def _fetch_tools(self, server: MCPServer) -> None:
        """
        获取服务器工具列表
        
        参数:
            server: MCP 服务器
        """
        # TODO: 实际从 MCP 服务器获取工具列表
        # 目前先模拟一些工具
        
        # 示例：如果是本地文件服务器
        if "filesystem" in server.url:
            server.tools = [
                MCPTool(
                    name="read_file",
                    description="读取文件内容",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"}
                        },
                        "required": ["path"]
                    },
                    server_name=server.name
                ),
                MCPTool(
                    name="write_file",
                    description="写入文件内容",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"},
                            "content": {"type": "string", "description": "文件内容"}
                        },
                        "required": ["path", "content"]
                    },
                    server_name=server.name
                )
            ]
        
        # 示例：如果是数据库服务器
        elif "database" in server.url:
            server.tools = [
                MCPTool(
                    name="query_database",
                    description="查询数据库",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL 查询"}
                        },
                        "required": ["query"]
                    },
                    server_name=server.name
                )
            ]
        
        logger.info(f"从 {server.name} 获取到 {len(server.tools)} 个工具")
    
    async def disconnect(self, server_name: str = None) -> None:
        """
        断开连接
        
        参数:
            server_name: 服务器名称（可选，默认断开所有）
        """
        if server_name:
            if server_name in self.servers:
                server = self.servers[server_name]
                server.connected = False
                
                # 移除工具
                tools_to_remove = [t for t in self.tools.values() if t.server_name == server_name]
                for tool in tools_to_remove:
                    del self.tools[tool.name]
                
                del self.servers[server_name]
                logger.info(f"已断开 MCP 服务器：{server_name}")
        else:
            # 断开所有连接
            self.servers.clear()
            self.tools.clear()
            self.connected = False
            logger.info("已断开所有 MCP 服务器连接")
    
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
                    "parameters": tool.input_schema
                }
            })
        return tools_def
    
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
            raise ValueError(f"未知工具：{tool_name}")
        
        tool = self.tools[tool_name]
        server = self.servers.get(tool.server_name)
        
        if not server:
            raise ValueError(f"服务器不存在：{tool.server_name}")
        
        if not server.connected:
            raise ValueError(f"服务器未连接：{tool.server_name}")
        
        logger.info(f"调用工具：{tool_name} (server: {server.name})")
        logger.debug(f"参数：{arguments}")
        
        # TODO: 实际调用 MCP 服务器
        # 目前先模拟执行结果
        
        # 示例：文件读取
        if tool_name == "read_file":
            path = arguments.get("path")
            if path and Path(path).exists():
                content = Path(path).read_text(encoding='utf-8')
                return {"content": content, "success": True}
            else:
                return {"error": f"文件不存在：{path}", "success": False}
        
        # 示例：文件写入
        elif tool_name == "write_file":
            path = arguments.get("path")
            content = arguments.get("content")
            if path and content:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(content, encoding='utf-8')
                return {"success": True, "message": f"文件已写入：{path}"}
            else:
                return {"error": "参数错误", "success": False}
        
        # 示例：数据库查询
        elif tool_name == "query_database":
            query = arguments.get("query")
            # 模拟查询结果
            return {
                "success": True,
                "data": [{"id": 1, "name": "示例数据"}]
            }
        
        else:
            return {"error": f"工具未实现：{tool_name}", "success": False}
    
    def get_status(self) -> Dict:
        """
        获取状态信息
        
        返回:
            状态字典
        """
        return {
            "connected_servers": len(self.servers),
            "available_tools": len(self.tools),
            "servers": list(self.servers.keys()),
            "connected": self.connected
        }


class MCPToolRegistry:
    """MCP 工具注册表 - 统一管理本地和远程工具"""
    
    def __init__(self, mcp_client: MCPClient):
        """
        初始化工具注册表
        
        参数:
            mcp_client: MCP 客户端实例
        """
        self.mcp_client = mcp_client
        self.tools: Dict[str, Any] = {}
        logger.info("MCPToolRegistry 初始化完成")
    
    def register_local_tool(self, tool: Any) -> None:
        """
        注册本地工具
        
        参数:
            tool: 工具实例（必须有 name 和 execute 方法）
        """
        if hasattr(tool, 'name') and hasattr(tool, 'execute'):
            self.tools[tool.name] = tool
            logger.info(f"注册本地工具：{tool.name}")
        else:
            logger.error(f"工具无效：缺少 name 或 execute 属性")
    
    async def sync_remote_tools(self) -> None:
        """
        同步远程 MCP 工具
        """
        # 从 MCP Client 同步工具
        for tool_name, tool in self.mcp_client.tools.items():
            # 创建工具包装器
            wrapper = self._create_tool_wrapper(tool)
            self.tools[tool_name] = wrapper
            logger.info(f"同步远程工具：{tool_name}")
    
    def _create_tool_wrapper(self, mcp_tool: MCPTool) -> Any:
        """
        创建 MCP 工具包装器
        
        参数:
            mcp_tool: MCP 工具定义
        
        返回:
            工具包装器实例
        """
        class MCPToolWrapper:
            def __init__(wrapper_self, tool: MCPTool, client: MCPClient):
                wrapper_self.tool = tool
                wrapper_self.client = client
                wrapper_self.name = tool.name
                wrapper_self.description = tool.description
            
            async def execute(wrapper_self, **kwargs) -> Dict:
                return await wrapper_self.client.call_tool(
                    wrapper_self.tool.name, 
                    kwargs
                )
        
        return MCPToolWrapper(mcp_tool, self.mcp_client)
    
    def get_all_tools(self) -> Dict[str, Any]:
        """
        获取所有工具
        
        返回:
            工具字典
        """
        return self.tools
    
    def get_tool(self, name: str) -> Optional[Any]:
        """
        获取指定工具
        
        参数:
            name: 工具名称
        
        返回:
            工具实例
        """
        return self.tools.get(name)
