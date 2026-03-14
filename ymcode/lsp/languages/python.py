#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Language Completion Handler
"""

import re
import ast
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..completion import CompletionItem, CompletionEngine
from ...utils.logger import get_logger

logger = get_logger(__name__)


class PythonCompletion:
    """Python 代码补全处理器"""
    
    def __init__(self):
        """初始化 Python 补全处理器"""
        self.builtins = self._get_python_builtins()
        self.common_imports = self._get_common_imports()
        logger.info("Python 补全处理器初始化完成")
    
    def _get_python_builtins(self) -> List[str]:
        """获取 Python 内置函数和类型"""
        return [
            # 内置函数
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint',
            'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
            'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
            'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help',
            'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
            'iter', 'len', 'list', 'locals', 'map', 'max', 'min',
            'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
            'property', 'range', 'repr', 'reversed', 'round', 'set',
            'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
            'super', 'tuple', 'type', 'vars', 'zip',
            # 内置类型
            'int', 'float', 'str', 'list', 'dict', 'tuple', 'set',
            'frozenset', 'bytes', 'bytearray', 'bool', 'complex',
            # 常用模块
            'os', 'sys', 're', 'json', 'math', 'random', 'datetime',
            'collections', 'itertools', 'functools', 'pathlib',
            # 装饰器
            'staticmethod', 'classmethod', 'property'
        ]
    
    def _get_common_imports(self) -> List[Dict[str, Any]]:
        """获取常用导入"""
        return [
            {'module': 'os', 'members': ['path', 'getcwd', 'listdir', 'mkdir', 'remove']},
            {'module': 'sys', 'members': ['path', 'argv', 'exit', 'stdout', 'stderr']},
            {'module': 're', 'members': ['match', 'search', 'findall', 'sub', 'compile']},
            {'module': 'json', 'members': ['load', 'dump', 'loads', 'dumps']},
            {'module': 'asyncio', 'members': ['run', 'sleep', 'gather', 'wait', 'create_task']},
            {'module': 'typing', 'members': ['List', 'Dict', 'Optional', 'Union', 'Callable', 'Any']}
        ]
    
    async def get_completions(self, text: str, line: int, column: int) -> List[CompletionItem]:
        """
        获取 Python 代码补全
        
        参数:
            text: 文档内容
            line: 行号
            column: 列号
        
        返回:
            补全项列表
        """
        completions = []
        lines = text.split('\n')
        
        # 获取当前行和上下文
        current_line = lines[line] if line < len(lines) else ''
        prefix = current_line[:column] if column <= len(current_line) else ''
        
        # 1. 内置函数和类型补全
        completions.extend(self._get_builtin_completions(prefix))
        
        # 2. 导入模块补全
        completions.extend(self._get_import_completions(text, prefix))
        
        # 3. 上下文智能补全
        completions.extend(self._get_context_completions(text, line, column))
        
        # 4. 方法链补全
        completions.extend(self._get_method_chain_completions(prefix))
        
        logger.debug(f"Python 补全：生成 {len(completions)} 个建议")
        
        return completions
    
    def _get_builtin_completions(self, prefix: str) -> List[CompletionItem]:
        """获取内置函数补全"""
        completions = []
        
        for builtin in self.builtins:
            if builtin.startswith(prefix.lower()):
                completions.append(CompletionItem(
                    label=builtin,
                    kind=CompletionEngine.KIND_FUNCTION,
                    detail=f"Built-in {builtin}"
                ))
        
        return completions
    
    def _get_import_completions(self, text: str, prefix: str) -> List[CompletionItem]:
        """获取导入模块补全"""
        completions = []
        
        # 分析导入语句
        import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
        matches = re.findall(import_pattern, text)
        
        imported_modules = set()
        for match in matches:
            if match[0]:  # from module import
                imported_modules.add(match[0])
            if match[1]:  # import module
                imported_modules.add(match[1])
        
        # 为导入的模块提供成员补全
        for imp in self.common_imports:
            if imp['module'] in imported_modules and prefix.startswith(imp['module'] + '.'):
                member_prefix = prefix[len(imp['module']) + 1:]
                for member in imp['members']:
                    if member.startswith(member_prefix):
                        completions.append(CompletionItem(
                            label=member,
                            kind=CompletionEngine.KIND_FUNCTION,
                            detail=f"{imp['module']}.{member}"
                        ))
        
        return completions
    
    def _get_context_completions(self, text: str, line: int, column: int) -> List[CompletionItem]:
        """获取上下文智能补全"""
        completions = []
        lines = text.split('\n')
        
        # 分析当前上下文
        in_class = False
        in_function = False
        indent_level = 0
        
        for i in range(line, -1, -1):
            if i < len(lines):
                line_text = lines[i].strip()
                if line_text.startswith('class '):
                    in_class = True
                    break
                elif line_text.startswith('def '):
                    in_function = True
                    break
        
        # 根据上下文提供建议
        current_line = lines[line] if line < len(lines) else ''
        
        if current_line.strip() == '':
            # 空行建议
            if in_class and not in_function:
                completions.append(CompletionItem(
                    label='def __init__',
                    kind=CompletionEngine.KIND_SNIPPET,
                    insert_text='def __init__(self, ${1:args}):\n    ${2:pass}',
                    detail='Constructor'
                ))
            elif in_function:
                completions.append(CompletionItem(
                    label='return',
                    kind=CompletionEngine.KIND_KEYWORD,
                    detail='Return statement'
                ))
        
        return completions
    
    def _get_method_chain_completions(self, prefix: str) -> List[CompletionItem]:
        """获取方法链补全（如 list.）"""
        completions = []
        
        # 检测常见类型的方法链
        type_methods = {
            'str': ['upper', 'lower', 'strip', 'split', 'join', 'replace', 'find', 'startswith', 'endswith'],
            'list': ['append', 'extend', 'insert', 'remove', 'pop', 'clear', 'index', 'count', 'sort', 'reverse'],
            'dict': ['keys', 'values', 'items', 'get', 'update', 'pop', 'clear', 'copy'],
            'set': ['add', 'remove', 'discard', 'pop', 'clear', 'update', 'intersection', 'union']
        }
        
        for type_name, methods in type_methods.items():
            if prefix.endswith(type_name + '.'):
                method_prefix = ''
                for method in methods:
                    if method.startswith(method_prefix):
                        completions.append(CompletionItem(
                            label=method,
                            kind=CompletionEngine.KIND_METHOD,
                            detail=f"{type_name}.{method}()"
                        ))
        
        return completions
    
    def get_hover_info(self, text: str, line: int, column: int) -> Optional[str]:
        """
        获取 Python 悬停信息
        
        参数:
            text: 文档内容
            line: 行号
            column: 列号
        
        返回:
            悬停信息
        """
        lines = text.split('\n')
        if line >= len(lines):
            return None
        
        current_line = lines[line]
        if column >= len(current_line):
            column = len(current_line) - 1
        
        # 获取光标下的单词
        word_match = re.search(r'\b(\w+)\b', current_line[max(0, column-20):column+50])
        if not word_match:
            return None
        
        word = word_match.group(1)
        
        # 检查是否是内置函数
        if word in self.builtins:
            return f"`{word}` - Python built-in function"
        
        # 检查是否是导入的模块
        for imp in self.common_imports:
            if word == imp['module']:
                return f"`{word}` - Common Python module"
        
        return None
