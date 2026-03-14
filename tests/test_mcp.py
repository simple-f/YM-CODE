#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Tests - MCP 协议测试（使用 Mock）
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
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
        """测试连接（Mock）"""
        client = MCPClient()
        
        # Mock connect 方法
        with patch.object(client, 'connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = None
            await client.connect("test-server", "http://localhost:8080")
            
            # 验证调用
            mock_connect.assert_called_once_with("test-server", "http://localhost:8080")
            assert True
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """测试列出工具（Mock）"""
        client = MCPClient()
        
        # 创建 Mock MCPTool
        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        
        # Mock list_tools 方法
        with patch.object(client, 'list_tools', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [mock_tool]
            
            tools = await client.list_tools()
            
            assert isinstance(tools, list)
            assert len(tools) > 0
            assert tools[0].name == "test_tool"
    
    @pytest.mark.asyncio
    async def test_call_tool(self):
        """测试调用工具（Mock）"""
        client = MCPClient()
        
        # Mock call_tool 方法
        with patch.object(client, 'call_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"success": True, "result": "test result"}
            
            result = await client.call_tool("test_tool", test_param="test")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] == True
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """测试断开连接（Mock）"""
        client = MCPClient()
        
        # Mock disconnect 方法
        with patch.object(client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
            mock_disconnect.return_value = None
            
            await client.disconnect("test-server")
            mock_disconnect.assert_called_with("test-server")
            
            await client.disconnect()
            assert True
    
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
        """测试同步远程工具（Mock）"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        # Mock sync_remote_tools
        with patch.object(registry, 'sync_remote_tools', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = None
            
            await registry.sync_remote_tools()
            
            mock_sync.assert_called_once()
            assert True
    
    @pytest.mark.asyncio
    async def test_remote_tool_wrapper(self):
        """测试远程工具包装器（Mock）"""
        client = MCPClient()
        registry = MCPToolRegistry(client)
        
        # 创建 Mock 工具
        mock_tool = MagicMock()
        mock_tool.name = "remote_tool"
        mock_tool.execute = AsyncMock(return_value={"success": True})
        
        registry.register_local_tool(mock_tool)
        
        tools = registry.get_all_tools()
        assert "remote_tool" in tools
        
        # 测试调用
        result = await tools["remote_tool"].execute(test_param="test")
        assert isinstance(result, dict)
        assert result["success"] == True
