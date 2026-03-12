#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Tools Tests - Git 工具测试
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from ymcode.tools.git_tools import GitTool, GitStatusTool, GitCommitTool


@pytest.fixture
def git_repo(tmp_path):
    """创建测试 Git 仓库"""
    # 初始化 Git 仓库
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True, capture_output=True)
    
    return tmp_path


class TestGitTool:
    """Git 工具测试"""
    
    @pytest.mark.asyncio
    async def test_status(self, git_repo):
        """测试 git status"""
        tool = GitTool()
        result = await tool.execute("status")
        # 验证返回了结果
        assert result is not None and len(result) > 0
    
    @pytest.mark.asyncio
    async def test_commit(self, git_repo):
        """测试 git commit"""
        # 创建测试文件
        test_file = git_repo / "test.txt"
        test_file.write_text("hello")
        
        # 添加并提交
        tool = GitTool()
        await tool.execute("add", path=".")
        result = await tool.execute("commit", message="test commit")
        
        assert "test commit" in result or "1 file changed" in result
    
    @pytest.mark.asyncio
    async def test_log(self, git_repo):
        """测试 git log"""
        # 创建提交
        test_file = git_repo / "test.txt"
        test_file.write_text("hello")
        
        tool = GitTool()
        await tool.execute("add", path=".")
        await tool.execute("commit", message="test commit")
        
        # 查看日志
        result = await tool.execute("log", count=1)
        assert "test commit" in result


class TestGitStatusTool:
    """Git Status 工具测试"""
    
    @pytest.mark.asyncio
    async def test_execute(self, git_repo):
        """测试执行"""
        tool = GitStatusTool()
        result = await tool.execute()
        assert isinstance(result, str)


class TestGitCommitTool:
    """Git Commit 工具测试"""
    
    @pytest.mark.asyncio
    async def test_execute(self, git_repo):
        """测试执行"""
        # 创建测试文件
        test_file = git_repo / "test.txt"
        test_file.write_text("hello")
        
        # 添加文件
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        
        # 提交
        tool = GitCommitTool()
        result = await tool.execute(message="test commit")
        
        assert isinstance(result, str)
