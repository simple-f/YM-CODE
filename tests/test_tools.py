#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools Tests - 工具测试
"""

import pytest
from ymcode.tools.registry import ToolRegistry
from ymcode.tools.bash_tool import BashTool
from ymcode.tools.file_tools import ReadFileTool, WriteFileTool


class TestToolRegistry:
    """工具注册表测试"""
    
    def test_init(self):
        """测试初始化"""
        registry = ToolRegistry()
        assert len(registry) > 0
    
    def test_register(self):
        """测试注册"""
        registry = ToolRegistry()
        tool = BashTool()
        registry.register(tool)
        assert registry.get("bash") == tool
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """测试执行"""
        registry = ToolRegistry()
        results = await registry.execute([])
        assert isinstance(results, list)


class TestBashTool:
    """Bash 工具测试"""
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """测试执行"""
        tool = BashTool()
        result = await tool.execute(command="echo hello")
        assert "hello" in result
    
    def test_schema(self):
        """测试 schema"""
        tool = BashTool()
        schema = tool.get_input_schema()
        assert "command" in schema["properties"]


class TestFileTools:
    """文件工具测试"""
    
    @pytest.mark.asyncio
    async def test_read_write(self, tmp_path):
        """测试读写"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_content = "hello world"
        
        # 写入
        write_tool = WriteFileTool()
        write_result = await write_tool.execute(
            path=str(test_file),
            content=test_content
        )
        assert "✓" in write_result
        
        # 读取
        read_tool = ReadFileTool()
        read_result = await read_tool.execute(path=str(test_file))
        assert test_content in read_result
