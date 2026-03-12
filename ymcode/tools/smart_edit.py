#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Edit Tool - 智能文件编辑工具

融合课程：s02 (Tool Use) + 生产级智能编辑
"""

import difflib
from pathlib import Path
from typing import Dict, List, Optional
from .base import BaseTool


class SmartEditTool(BaseTool):
    """智能编辑工具"""
    
    name = "smart_edit"
    description = "智能编辑文件（支持局部修改、模糊匹配、多位置替换）"
    
    async def execute(
        self,
        path: str,
        old_text: str,
        new_text: str,
        fuzzy: bool = False,
        all_occurrences: bool = False
    ) -> str:
        """
        智能编辑文件
        
        参数:
            path: 文件路径
            old_text: 原文本
            new_text: 新文本
            fuzzy: 是否模糊匹配
            all_occurrences: 是否替换所有匹配项
        
        返回:
            编辑结果
        """
        try:
            file_path = Path(path)
            
            # 检查文件
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            if not file_path.is_file():
                return f"错误：不是文件 {path}"
            
            # 读取文件
            content = file_path.read_text(encoding='utf-8')
            
            # 查找匹配
            if fuzzy:
                # 模糊匹配
                matches = self._fuzzy_find(content, old_text)
            else:
                # 精确匹配
                matches = self._exact_find(content, old_text)
            
            if not matches:
                return f"错误：未找到匹配的文本"
            
            if len(matches) > 1 and not all_occurrences:
                return f"警告：找到 {len(matches)} 处匹配，请指定 all_occurrences=True 替换所有，或提供更精确的 old_text"
            
            # 替换文本
            if all_occurrences:
                new_content = content.replace(old_text, new_text)
            else:
                # 只替换第一处
                position = matches[0]
                new_content = (
                    content[:position] + 
                    new_text + 
                    content[position + len(old_text):]
                )
            
            # 写回文件
            file_path.write_text(new_content, encoding='utf-8')
            
            # 生成 diff
            diff = self._generate_diff(content, new_content, path)
            
            return f"✓ 文件已编辑：{path}\n\n{diff}"
            
        except Exception as e:
            return f"编辑失败：{e}"
    
    def _exact_find(self, content: str, text: str) -> List[int]:
        """
        精确查找
        
        参数:
            content: 文件内容
            text: 查找文本
        
        返回:
            匹配位置列表
        """
        positions = []
        start = 0
        
        while True:
            pos = content.find(text, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def _fuzzy_find(self, content: str, text: str, threshold: float = 0.8) -> List[int]:
        """
        模糊查找
        
        参数:
            content: 文件内容
            text: 查找文本
            threshold: 匹配阈值（0-1）
        
        返回:
            匹配位置列表
        """
        positions = []
        
        # 按行分割
        content_lines = content.splitlines(keepends=True)
        text_lines = text.splitlines(keepends=True)
        
        # 滑动窗口匹配
        for i in range(len(content_lines) - len(text_lines) + 1):
            window = ''.join(content_lines[i:i + len(text_lines)])
            
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, window, text).ratio()
            
            if similarity >= threshold:
                # 计算位置
                position = sum(len(line) for line in content_lines[:i])
                positions.append(position)
        
        return positions
    
    def _generate_diff(self, old_content: str, new_content: str, path: str) -> str:
        """
        生成 diff
        
        参数:
            old_content: 旧内容
            new_content: 新内容
            path: 文件路径
        
        返回:
            diff 字符串
        """
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f'a/{path}',
            tofile=f'b/{path}'
        )
        
        return ''.join(diff)
    
    def get_input_schema(self) -> Dict:
        """获取输入 schema"""
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "old_text": {
                    "type": "string",
                    "description": "原文本"
                },
                "new_text": {
                    "type": "string",
                    "description": "新文本"
                },
                "fuzzy": {
                    "type": "boolean",
                    "description": "是否模糊匹配"
                },
                "all_occurrences": {
                    "type": "boolean",
                    "description": "是否替换所有匹配项"
                }
            },
            "required": ["path", "old_text", "new_text"]
        }


class InsertTextTool(BaseTool):
    """插入文本工具"""
    
    name = "insert_text"
    description = "在文件指定位置插入文本"
    
    async def execute(
        self,
        path: str,
        line_number: int,
        text: str,
        mode: str = "after"
    ) -> str:
        """
        插入文本
        
        参数:
            path: 文件路径
            line_number: 行号（从 1 开始）
            text: 要插入的文本
            mode: 插入模式（before/after）
        
        返回:
            插入结果
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            # 读取文件
            lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
            
            # 调整行号
            if mode == "after":
                insert_pos = line_number
            else:  # before
                insert_pos = line_number - 1
            
            # 确保位置有效
            insert_pos = max(0, min(insert_pos, len(lines)))
            
            # 插入文本
            if not text.endswith('\n'):
                text += '\n'
            
            lines.insert(insert_pos, text)
            
            # 写回文件
            file_path.write_text(''.join(lines), encoding='utf-8')
            
            return f"✓ 已插入文本到 {path}:{line_number} 行"
            
        except Exception as e:
            return f"插入失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "line_number": {
                    "type": "integer",
                    "description": "行号（从 1 开始）"
                },
                "text": {
                    "type": "string",
                    "description": "要插入的文本"
                },
                "mode": {
                    "type": "string",
                    "description": "插入模式",
                    "enum": ["before", "after"]
                }
            },
            "required": ["path", "line_number", "text"]
        }


class DeleteLinesTool(BaseTool):
    """删除行工具"""
    
    name = "delete_lines"
    description = "删除文件指定行"
    
    async def execute(
        self,
        path: str,
        start_line: int,
        end_line: int = None
    ) -> str:
        """
        删除行
        
        参数:
            path: 文件路径
            start_line: 起始行号（从 1 开始）
            end_line: 结束行号（可选，默认删除单行）
        
        返回:
            删除结果
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            # 读取文件
            lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
            
            # 调整行号
            start_idx = start_line - 1
            end_idx = end_line if end_line else start_idx
            
            # 确保索引有效
            start_idx = max(0, min(start_idx, len(lines)))
            end_idx = max(start_idx, min(end_idx, len(lines)))
            
            # 删除行
            deleted_lines = lines[start_idx:end_idx + 1]
            del lines[start_idx:end_idx + 1]
            
            # 写回文件
            file_path.write_text(''.join(lines), encoding='utf-8')
            
            return f"✓ 已删除 {len(deleted_lines)} 行从 {path}:{start_line}-{end_line}"
            
        except Exception as e:
            return f"删除失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "start_line": {
                    "type": "integer",
                    "description": "起始行号"
                },
                "end_line": {
                    "type": "integer",
                    "description": "结束行号"
                }
            },
            "required": ["path", "start_line"]
        }
