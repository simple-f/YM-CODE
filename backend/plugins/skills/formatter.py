#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formatter Skill - 代码格式化技能

支持 Python/JavaScript/TypeScript 代码格式化
"""

import logging
from typing import Dict, Any, Optional

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FormatterSkill(BaseSkill):
    """代码格式化技能"""
    
    def __init__(self):
        """初始化格式化技能"""
        super().__init__('formatter')
        self.indent_size = 4
        self.use_tabs = False
    
    @property
    def description(self) -> str:
        return "代码格式化技能 - 支持 Python/JavaScript/TypeScript 格式化"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要格式化的代码"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "typescript", "json"],
                    "description": "编程语言"
                },
                "indent_size": {
                    "type": "integer",
                    "description": "缩进大小",
                    "default": 4
                },
                "use_tabs": {
                    "type": "boolean",
                    "description": "使用 Tab 缩进",
                    "default": False
                }
            },
            "required": ["code", "language"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行代码格式化
        
        参数:
            arguments: 输入参数
        
        返回:
            格式化后的代码
        """
        code = arguments.get('code', '')
        language = arguments.get('language', 'python')
        indent_size = arguments.get('indent_size', self.indent_size)
        use_tabs = arguments.get('use_tabs', self.use_tabs)
        
        if not code:
            return {"error": "请提供代码"}
        
        try:
            if language == 'python':
                formatted = self._format_python(code, indent_size)
            elif language in ['javascript', 'typescript']:
                formatted = self._format_javascript(code, indent_size, use_tabs)
            elif language == 'json':
                formatted = self._format_json(code, indent_size)
            else:
                return {"error": f"不支持的语言：{language}"}
            
            return {
                "success": True,
                "formatted_code": formatted,
                "original_length": len(code),
                "formatted_length": len(formatted)
            }
        except Exception as e:
            return {"error": f"格式化失败：{e}"}
    
    def _format_python(self, code: str, indent_size: int) -> str:
        """格式化 Python 代码"""
        import re
        
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # 去除行尾空格
            line = line.rstrip()
            
            # 跳过空行
            if not line.strip():
                formatted_lines.append('')
                continue
            
            # 计算缩进
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            indent_level = indent // indent_size
            
            # 重新格式化
            new_indent = ' ' * (indent_level * indent_size)
            formatted_lines.append(new_indent + stripped)
        
        return '\n'.join(formatted_lines)
    
    def _format_javascript(self, code: str, indent_size: int, use_tabs: bool) -> str:
        """格式化 JavaScript/TypeScript 代码"""
        import re
        
        # 简单的格式化逻辑
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        indent_char = '\t' if use_tabs else ' ' * indent_size
        
        for line in lines:
            line = line.strip()
            
            if not line:
                formatted_lines.append('')
                continue
            
            # 减少缩进（遇到 }）
            if line.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # 添加格式化后的行
            formatted_lines.append(indent_char * indent_level + line)
            
            # 增加缩进（遇到 {）
            if line.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def _format_json(self, code: str, indent_size: int) -> str:
        """格式化 JSON"""
        import json
        
        try:
            data = json.loads(code)
            return json.dumps(data, indent=indent_size, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误：{e}")
