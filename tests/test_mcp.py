#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Tests - MCP 协议测试
"""

import pytest
import asyncio
from ymcode.mcp.client import MCPClient, MCPTool, MCPToolRegistry


class TestMCPClient:
    """MCP 客户端测试"""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        client = MCPClient()
        assert client is not None
        assert len(client.servers) == 0
        assert len(client.tools) == 0
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """测试连接"""
        client = MCPClient()
        await client.connect("test-server", "http://localhost:8080")
        
        assert "test-server" in client.servers
        assert len(client.tools) > 0
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """测试列出工具"""
        client = MCPClient()
        await client.connect("test-server", "http://localhost:8080")
        
        tools = await client.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(t, MCPTool) for t in tools)
    
    @pytest.mark.asyncio
    async def test_call_tool(self):
        """测试调用工具"""
        client = MCPClient()
        await client.connect("test-server", "http://localhost:8080")
        
        # 获取第一个工具
        tools = await client.list_tools()
        if tools:
            tool_name = tools[0].name
            result = await client.call_tool(tool_name, test_param="test")
            
            assert isinstance(result, dict)
            assert "success" in result
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """测试断开连接"""
        client = MCPClient()
        await client.connect("test-server", "http://localhost:8080")
        
        # 断开特定服务器
        await client.disconnect("test-server")
        assert "test-server" not in client.servers
        
        # 重新连接
        await client.connect("test-server", "http://localhost:8080")
        
        # 断开所有
        await client.disconnect()
        assert len(client.servers) == 0
        assert len(client.tools) == 0
    
    def test_get_stats(self):
        """测试获取统计"""
        client = MCPClient()
        stats = client.get_stats()
        
        assert "connected_servers" in stats
        assert "available_tools" in stats
        assert "servers" in stats


class TestMCPToolRegistry:
    """MCP 工具注册表测试"""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        assert registry is not None
        assert registry.mcp_client == client
    
    @pytest.mark.asyncio
    async def test_register_local_tool(self):
        """测试注册本地工具"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        # 创建模拟工具
        class MockTool:
            name = "mock_tool"
            description = "Mock tool"
            input_schema = {}
            
            async def execute(self, **kwargs):
                return "mock result"
        
        mock_tool = MockTool()
        registry.register_local_tool(mock_tool)
        
        tools = registry.get_all_tools()
        assert "mock_tool" in tools
    
    @pytest.mark.asyncio
    async def test_sync_remote_tools(self):
        """测试同步远程工具"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        # 连接服务器
        await client.connect("test-server", "http://localhost:8080")
        
        # 同步远程工具
        await registry.sync_remote_tools()
        
        tools = registry.get_all_tools()
        assert len(tools) > 0
    
    @pytest.mark.asyncio
    async def test_remote_tool_wrapper(self):
        """测试远程工具包装器"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        await client.connect("test-server", "http://localhost:8080")
        await registry.sync_remote_tools()
        
        tools = registry.get_all_tools()
        
        # 测试远程工具调用
        for tool_name, tool in tools.items():
            if hasattr(tool, 'execute'):
                result = await tool.execute(test_param="test")
                assert isinstance(result, dict)
                break
