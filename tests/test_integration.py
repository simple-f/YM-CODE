#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests - 集成测试

测试完整的 Agent 工作流程
"""

import pytest
import asyncio
from pathlib import Path
from ymcode.core.agent import Agent
from ymcode.tools.registry import ToolRegistry


class TestAgentIntegration:
    """Agent 集成测试"""
    
    @pytest.mark.asyncio
    async def test_agent_basic_workflow(self, tmp_path):
        """测试 Agent 基本工作流"""
        # 初始化 Agent（Mock 模式）
        agent = Agent(config={"mock_mode": True})
        
        # 测试基本对话
        result = await agent.run("你好")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # 测试工具调用
        result = await agent.run("读取当前目录文件")
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_tool_chain(self, tmp_path):
        """测试工具链"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("initial content")
        
        # 初始化工具
        tools = ToolRegistry()
        
        # 测试工具链：read -> edit -> write
        read_result = await tools.execute([{
            "name": "read_file",
            "input": {"path": str(test_file)}
        }])
        
        assert "initial content" in str(read_result)
    
    @pytest.mark.asyncio
    async def test_git_workflow(self, tmp_path):
        """测试 Git 工作流"""
        import subprocess
        
        # 初始化 Git 仓库
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
        
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # 初始化工具
        tools = ToolRegistry()
        
        # 测试 Git 添加
        result = await tools.execute([{
            "name": "git",
            "input": {"operation": "add", "path": "."}
        }])
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_regex_workflow(self, tmp_path):
        """测试正则表达式工作流"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world hello")
        
        # 初始化工具
        tools = ToolRegistry()
        
        # 测试正则替换
        result = await tools.execute([{
            "name": "regex_replace",
            "input": {
                "path": str(test_file),
                "pattern": "hello",
                "replacement": "hi"
            }
        }])
        
        assert "✓ 正则替换完成" in str(result)
        assert test_file.read_text() == "hi world hi"
    
    @pytest.mark.asyncio
    async def test_edit_history_workflow(self, tmp_path):
        """测试编辑历史工作流"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("version 1")
        
        # 初始化工具
        tools = ToolRegistry()
        
        # 第一次编辑
        await tools.execute([{
            "name": "write_file",
            "input": {"path": str(test_file), "content": "version 2"}
        }])
        
        # 第二次编辑
        await tools.execute([{
            "name": "write_file",
            "input": {"path": str(test_file), "content": "version 3"}
        }])
        
        # 验证最终内容
        assert test_file.read_text() == "version 3"


class TestCLIIIntegration:
    """CLI 集成测试"""
    
    def test_cli_import(self):
        """测试 CLI 导入"""
        from ymcode.cli import YMCodeCLI
        cli = YMCodeCLI()
        assert cli is not None
    
    def test_agent_import(self):
        """测试 Agent 导入"""
        from ymcode.core.agent import Agent
        agent = Agent()
        assert agent is not None
    
    def test_tools_import(self):
        """测试工具导入"""
        from ymcode.tools.registry import ToolRegistry
        tools = ToolRegistry()
        assert len(tools) > 0


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """测试文件未找到错误"""
        tools = ToolRegistry()
        result = await tools.execute([{
            "name": "read_file",
            "input": {"path": "/nonexistent/file.txt"}
        }])
        
        assert "错误" in str(result) or "Error" in str(result)
    
    @pytest.mark.asyncio
    async def test_invalid_regex(self, tmp_path):
        """测试无效正则表达式"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        tools = ToolRegistry()
        result = await tools.execute([{
            "name": "regex_replace",
            "input": {
                "path": str(test_file),
                "pattern": "[invalid",
                "replacement": "test"
            }
        }])
        
        assert "错误" in str(result)
