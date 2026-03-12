#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edit History Tools - 编辑历史工具（Undo/Redo）

融合课程：s07 (Task System) + 生产级编辑历史
"""

from typing import Dict, Optional
from .base import BaseTool
from .edit_history import EditHistoryManager


# 全局编辑历史管理器
_edit_history_manager = None


def get_edit_history_manager() -> EditHistoryManager:
    """获取编辑历史管理器（单例）"""
    global _edit_history_manager
    if _edit_history_manager is None:
        _edit_history_manager = EditHistoryManager()
    return _edit_history_manager


class UndoTool(BaseTool):
    """撤销工具"""
    
    name = "undo"
    description = "撤销最后一次文件编辑"
    
    async def execute(self, file_path: str) -> str:
        """
        撤销编辑
        
        参数:
            file_path: 文件路径
        
        返回:
            撤销结果
        """
        manager = get_edit_history_manager()
        result = manager.undo_last_edit(file_path)
        
        if not result:
            return f"错误：没有可撤销的编辑记录 {file_path}"
        
        return f"✓ 已撤销操作\n\n{result['message']}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                }
            },
            "required": ["file_path"]
        }


class RedoTool(BaseTool):
    """重做工具"""
    
    name = "redo"
    description = "重做已撤销的编辑"
    
    async def execute(self, file_path: str, record_id: str) -> str:
        """
        重做编辑
        
        参数:
            file_path: 文件路径
            record_id: 记录 ID
        
        返回:
            重做结果
        """
        # TODO: 实现 redo 功能
        return f"功能开发中：redo {file_path} {record_id}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "record_id": {
                    "type": "string",
                    "description": "编辑记录 ID"
                }
            },
            "required": ["file_path", "record_id"]
        }


class HistoryTool(BaseTool):
    """查看历史工具"""
    
    name = "edit_history"
    description = "查看文件编辑历史"
    
    async def execute(self, file_path: str, limit: int = 5) -> str:
        """
        查看编辑历史
        
        参数:
            file_path: 文件路径
            limit: 返回数量
        
        返回:
            历史记录
        """
        manager = get_edit_history_manager()
        history = manager.get_edit_history(file_path, limit)
        
        if not history:
            return f"没有编辑历史：{file_path}"
        
        # 格式化输出
        output = f"## 编辑历史：{file_path}\n\n"
        output += "| ID | 时间 | 操作 |\n"
        output += "|---|---|---|\n"
        
        for record in reversed(history):
            output += f"| {record['id']} | {record['timestamp']} | {record['operation']} |\n"
        
        return output
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回数量",
                    "default": 5
                }
            },
            "required": ["file_path"]
        }
