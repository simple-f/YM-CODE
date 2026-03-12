#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regex Edit Tests - 正则表达式编辑测试
"""

import pytest
from pathlib import Path
from ymcode.tools.regex_edit import RegexReplaceTool, RegexSearchTool, RegexValidateTool


class TestRegexReplaceTool:
    """正则替换工具测试"""
    
    @pytest.mark.asyncio
    async def test_basic_replace(self, tmp_path):
        """测试基本替换"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world hello")
        
        tool = RegexReplaceTool()
        result = await tool.execute(
            path=str(test_file),
            pattern="hello",
            replacement="hi"
        )
        
        assert "✓ 正则替换完成" in result
        assert test_file.read_text() == "hi world hi"
    
    @pytest.mark.asyncio
    async def test_regex_pattern(self, tmp_path):
        """测试正则模式"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("abc123 def456")
        
        tool = RegexReplaceTool()
        result = await tool.execute(
            path=str(test_file),
            pattern=r"\d+",
            replacement="NUM"
        )
        
        assert "✓ 正则替换完成" in result
        assert test_file.read_text() == "abcNUM defNUM"
    
    @pytest.mark.asyncio
    async def test_case_insensitive(self, tmp_path):
        """测试忽略大小写"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello HELLO hello")
        
        tool = RegexReplaceTool()
        result = await tool.execute(
            path=str(test_file),
            pattern="hello",
            replacement="hi",
            flags="i"
        )
        
        assert "✓ 正则替换完成" in result
        assert test_file.read_text() == "hi hi hi"
    
    @pytest.mark.asyncio
    async def test_invalid_pattern(self, tmp_path):
        """测试无效正则"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        tool = RegexReplaceTool()
        result = await tool.execute(
            path=str(test_file),
            pattern="[invalid",  # 无效正则
            replacement="test"
        )
        
        assert "错误：正则表达式无效" in result


class TestRegexSearchTool:
    """正则搜索工具测试"""
    
    @pytest.mark.asyncio
    async def test_basic_search(self, tmp_path):
        """测试基本搜索"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nhello world\nline 3")
        
        tool = RegexSearchTool()
        result = await tool.execute(
            path=str(test_file),
            pattern="hello"
        )
        
        assert "正则搜索结果" in result
        assert "找到 1 处匹配" in result
    
    @pytest.mark.asyncio
    async def test_search_with_context(self, tmp_path):
        """测试带上下文的搜索"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nline 2\nhello\nline 4\nline 5")
        
        tool = RegexSearchTool()
        result = await tool.execute(
            path=str(test_file),
            pattern="hello",
            context_lines=1
        )
        
        assert "上下文" in result


class TestRegexValidateTool:
    """正则验证工具测试"""
    
    @pytest.mark.asyncio
    async def test_valid_pattern(self):
        """测试有效正则"""
        tool = RegexValidateTool()
        result = await tool.execute(pattern=r"\d+")
        
        assert "✅ 正则表达式有效" in result
    
    @pytest.mark.asyncio
    async def test_invalid_pattern(self):
        """测试无效正则"""
        tool = RegexValidateTool()
        result = await tool.execute(pattern="[invalid")
        
        assert "❌ 正则表达式无效" in result
    
    @pytest.mark.asyncio
    async def test_with_test_text(self):
        """测试带测试文本"""
        tool = RegexValidateTool()
        result = await tool.execute(
            pattern=r"\d+",
            test_text="abc123def456"
        )
        
        assert "✅ 正则表达式有效" in result
        assert "测试文本匹配结果" in result
