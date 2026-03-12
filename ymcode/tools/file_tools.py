#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Tools - 文件操作工具

融合课程：s02 (Tool Use)
"""

from pathlib import Path
from typing import Dict
from .base import BaseTool


class ReadFileTool(BaseTool):
    """读文件工具"""
    
    name = "read_file"
    description = "读取文件内容"
    
    async def execute(self, path: str) -> str:
        """
        读取文件
        
        参数:
            path: 文件路径
        
        返回:
            文件内容
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            if not file_path.is_file():
                return f"错误：不是文件 {path}"
            
            content = file_path.read_text(encoding='utf-8')
            return content
            
        except Exception as e:
            return f"读取失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                }
            },
            "required": ["path"]
        }


class WriteFileTool(BaseTool):
    """写文件工具"""
    
    name = "write_file"
    description = "写入文件内容"
    
    async def execute(self, path: str, content: str) -> str:
        """
        写入文件
        
        参数:
            path: 文件路径
            content: 文件内容
        
        返回:
            执行结果
        """
        try:
            file_path = Path(path)
            
            # 创建父目录
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            file_path.write_text(content, encoding='utf-8')
            
            return f"✓ 文件已写入：{path}"
            
        except Exception as e:
            return f"写入失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容"
                }
            },
            "required": ["path", "content"]
        }


class ListDirTool(BaseTool):
    """列出目录工具"""
    
    name = "list_dir"
    description = "列出目录内容"
    
    async def execute(self, path: str) -> str:
        """
        列出目录
        
        参数:
            path: 目录路径
        
        返回:
            目录列表
        """
        try:
            dir_path = Path(path)
            
            if not dir_path.exists():
                return f"错误：目录不存在 {path}"
            
            if not dir_path.is_dir():
                return f"错误：不是目录 {path}"
            
            # 列出内容
            items = []
            for item in dir_path.iterdir():
                prefix = "📁 " if item.is_dir() else "📄 "
                items.append(f"{prefix}{item.name}")
            
            return "\n".join(items)
            
        except Exception as e:
            return f"列出失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径"
                }
            },
            "required": ["path"]
        }
