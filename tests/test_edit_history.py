#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edit History Tests - 编辑历史测试
"""

import pytest
from pathlib import Path
from ymcode.tools.edit_history import EditHistory, EditRecord, EditHistoryManager


class TestEditHistory:
    """编辑历史测试"""
    
    def test_init(self, tmp_path):
        """测试初始化"""
        history = EditHistory(history_dir=tmp_path)
        assert history is not None
        assert history.history_dir == tmp_path
    
    def test_add_record(self, tmp_path):
        """测试添加记录"""
        history = EditHistory(history_dir=tmp_path)
        
        record = EditRecord(
            id="test123",
            file_path="/test/file.txt",
            old_content="old",
            new_content="new",
            timestamp="2026-03-12T19:00:00",
            operation="replace"
        )
        
        history.add_record(record)
        
        # 验证记录已添加
        assert "/test/file.txt" in history.file_histories
        assert len(history.file_histories["/test/file.txt"]) == 1
    
    def test_undo(self, tmp_path):
        """测试撤销"""
        history = EditHistory(history_dir=tmp_path)
        
        # 添加记录
        record = EditRecord(
            id="test123",
            file_path="/test/file.txt",
            old_content="old",
            new_content="new",
            timestamp="2026-03-12T19:00:00",
            operation="replace"
        )
        
        history.add_record(record)
        
        # 撤销
        undone = history.undo("/test/file.txt")
        
        assert undone is not None
        assert undone.id == "test123"
        assert len(history.file_histories["/test/file.txt"]) == 0
    
    def test_get_history(self, tmp_path):
        """测试获取历史"""
        history = EditHistory(history_dir=tmp_path)
        
        # 添加多条记录
        for i in range(10):
            record = EditRecord(
                id=f"test{i}",
                file_path="/test/file.txt",
                old_content=f"old{i}",
                new_content=f"new{i}",
                timestamp=f"2026-03-12T19:{i:02d}:00",
                operation="replace"
            )
            history.add_record(record)
        
        # 获取历史
        records = history.get_history("/test/file.txt", limit=5)
        
        assert len(records) == 5
        assert records[-1].id == "test9"
    
    def test_max_history(self, tmp_path):
        """测试最大历史记录限制"""
        history = EditHistory(history_dir=tmp_path, max_history=5)
        
        # 添加 10 条记录
        for i in range(10):
            record = EditRecord(
                id=f"test{i}",
                file_path="/test/file.txt",
                old_content=f"old{i}",
                new_content=f"new{i}",
                timestamp=f"2026-03-12T19:{i:02d}:00",
                operation="replace"
            )
            history.add_record(record)
        
        # 验证只保留最后 5 条
        assert len(history.file_histories["/test/file.txt"]) == 5
    
    def test_get_stats(self, tmp_path):
        """测试获取统计"""
        history = EditHistory(history_dir=tmp_path)
        
        # 添加记录
        record = EditRecord(
            id="test123",
            file_path="/test/file.txt",
            old_content="old",
            new_content="new",
            timestamp="2026-03-12T19:00:00",
            operation="replace"
        )
        history.add_record(record)
        
        stats = history.get_stats()
        
        assert "total_files" in stats
        assert "total_records" in stats
        assert stats["total_files"] == 1
        assert stats["total_records"] == 1


class TestEditHistoryManager:
    """编辑历史管理器测试"""
    
    def test_record_edit(self):
        """测试记录编辑"""
        manager = EditHistoryManager()
        
        record_id = manager.record_edit(
            file_path="/test/file.txt",
            old_content="old",
            new_content="new",
            operation="replace"
        )
        
        assert record_id is not None
        assert len(record_id) == 8  # UUID 前 8 位
    
    def test_undo_last_edit(self):
        """测试撤销最后编辑"""
        manager = EditHistoryManager()
        
        # 记录编辑
        manager.record_edit(
            file_path="/test/file.txt",
            old_content="old",
            new_content="new"
        )
        
        # 撤销
        result = manager.undo_last_edit("/test/file.txt")
        
        assert result is not None
        assert result["success"] is True
        assert result["old_content"] == "old"
    
    def test_get_edit_history(self):
        """测试获取编辑历史"""
        manager = EditHistoryManager()
        
        # 记录多条编辑
        for i in range(3):
            manager.record_edit(
                file_path="/test/file.txt",
                old_content=f"old{i}",
                new_content=f"new{i}"
            )
        
        # 获取历史
        history = manager.get_edit_history("/test/file.txt", limit=5)
        
        assert len(history) == 3
        assert all("id" in h for h in history)
