#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Edit Tests - 智能编辑工具测试
"""

import pytest
from pathlib import Path
from ymcode.tools.smart_edit import SmartEditTool, InsertTextTool, DeleteLinesTool


class TestSmartEditTool:
    """智能编辑工具测试"""
    
    @pytest.mark.asyncio
    async def test_exact_replace(self, tmp_path):
        """测试精确替换"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        tool = SmartEditTool()
        result = await tool.execute(
            path=str(test_file),
            old_text="world",
            new_text="YM-CODE"
        )
        
        assert "✓ 文件已编辑" in result
        assert test_file.read_text() == "hello YM-CODE"
    
    @pytest.mark.asyncio
    async def test_fuzzy_match(self, tmp_path):
        """测试模糊匹配"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("def hello_world():\n    pass")
        
        tool = SmartEditTool()
        result = await tool.execute(
            path=str(test_file),
            old_text="def hello_world()",
            new_text="def greet()",
            fuzzy=True
        )
        
        assert "✓ 文件已编辑" in result
    
    @pytest.mark.asyncio
    async def test_all_occurrences(self, tmp_path):
        """测试替换所有匹配项"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar foo baz foo")
        
        tool = SmartEditTool()
        result = await tool.execute(
            path=str(test_file),
            old_text="foo",
            new_text="qux",
            all_occurrences=True
        )
        
        assert "✓ 文件已编辑" in result
        assert test_file.read_text() == "qux bar qux baz qux"


class TestInsertTextTool:
    """插入文本工具测试"""
    
    @pytest.mark.asyncio
    async def test_insert_after(self, tmp_path):
        """测试在行后插入"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        tool = InsertTextTool()
        result = await tool.execute(
            path=str(test_file),
            line_number=2,
            text="inserted line",
            mode="after"
        )
        
        assert "✓ 已插入" in result
        content = test_file.read_text()
        assert "inserted line" in content
    
    @pytest.mark.asyncio
    async def test_insert_before(self, tmp_path):
        """测试在行前插入"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        tool = InsertTextTool()
        result = await tool.execute(
            path=str(test_file),
            line_number=1,
            text="first line",
            mode="before"
        )
        
        assert "✓ 已插入" in result


class TestDeleteLinesTool:
    """删除行工具测试"""
    
    @pytest.mark.asyncio
    async def test_delete_single_line(self, tmp_path):
        """测试删除单行"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        tool = DeleteLinesTool()
        result = await tool.execute(
            path=str(test_file),
            start_line=2
        )
        
        assert "✓ 已删除" in result
        content = test_file.read_text()
        assert "line 2" not in content
    
    @pytest.mark.asyncio
    async def test_delete_multiple_lines(self, tmp_path):
        """测试删除多行"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3\nline 4")
        
        tool = DeleteLinesTool()
        result = await tool.execute(
            path=str(test_file),
            start_line=2,
            end_line=3
        )
        
        assert "✓ 已删除" in result
        content = test_file.read_text()
        assert "line 2" not in content
        assert "line 3" not in content
