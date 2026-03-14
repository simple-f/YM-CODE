#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript Language Completion Handler
"""

import re
from typing import List, Optional, Dict, Any

from ..completion import CompletionItem, CompletionEngine
from ...utils.logger import get_logger

logger = get_logger(__name__)


class JavaScriptCompletion:
    """JavaScript 代码补全处理器"""
    
    def __init__(self):
        """初始化 JavaScript 补全处理器"""
        self.builtins = self._get_js_builtins()
        self.dom_apis = self._get_dom_apis()
        self.common_imports = self._get_common_imports()
        logger.info("JavaScript 补全处理器初始化完成")
    
    def _get_js_builtins(self) -> List[str]:
        """获取 JavaScript 内置对象和函数"""
        return [
            # 全局对象
            'Array', 'Boolean', 'Date', 'Error', 'Function', 'JSON',
            'Map', 'Math', 'Number', 'Object', 'Promise', 'RegExp',
            'Set', 'String', 'Symbol', 'WeakMap', 'WeakSet',
            # 全局函数
            'eval', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
            'decodeURI', 'decodeURIComponent', 'encodeURI', 'encodeURIComponent',
            # 控制台
            'console', 'log', 'warn', 'error', 'info', 'debug', 'table',
            # 定时器
            'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            # 异步
            'async', 'await', 'Promise', 'then', 'catch', 'finally',
            # 模块
            'import', 'export', 'default', 'require', 'module', 'exports',
            # 类型
            'typeof', 'instanceof', 'constructor', 'prototype'
        ]
    
    def _get_dom_apis(self) -> Dict[str, List[str]]:
        """获取 DOM API"""
        return {
            'document': ['getElementById', 'querySelector', 'querySelectorAll', 'createElement', 'appendChild'],
            'window': ['addEventListener', 'removeEventListener', 'fetch', 'alert', 'confirm', 'prompt'],
            'localStorage': ['getItem', 'setItem', 'removeItem', 'clear'],
            'fetch': ['then', 'catch', 'json', 'text', 'blob']
        }
    
    def _get_common_imports(self) -> List[Dict[str, Any]]:
        """获取常用导入"""
        return [
            {'module': 'react', 'members': ['useState', 'useEffect', 'useContext', 'useReducer', 'useCallback', 'useMemo']},
            {'module': 'lodash', 'members': ['map', 'filter', 'reduce', 'clone', 'merge', 'debounce', 'throttle']},
            {'module': 'axios', 'members': ['get', 'post', 'put', 'delete', 'request', 'create']},
            {'module': 'express', 'members': ['Router', 'json', 'urlencoded', 'static']}
        ]
    
    async def get_completions(self, text: str, line: int, column: int) -> List[CompletionItem]:
        """
        获取 JavaScript 代码补全
        
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
        
        # 1. 内置对象和函数补全
        completions.extend(self._get_builtin_completions(prefix))
        
        # 2. DOM API 补全
        completions.extend(self._get_dom_completions(prefix))
        
        # 3. 导入模块补全
        completions.extend(self._get_import_completions(text, prefix))
        
        # 4. ES6+ 语法补全
        completions.extend(self._get_es6_completions(text, line, column))
        
        # 5. 方法链补全
        completions.extend(self._get_method_chain_completions(prefix))
        
        logger.debug(f"JavaScript 补全：生成 {len(completions)} 个建议")
        
        return completions
    
    def _get_builtin_completions(self, prefix: str) -> List[CompletionItem]:
        """获取内置函数补全"""
        completions = []
        
        for builtin in self.builtins:
            if builtin.lower().startswith(prefix.lower()):
                kind = CompletionEngine.KIND_CLASS if builtin[0].isupper() else CompletionEngine.KIND_FUNCTION
                completions.append(CompletionItem(
                    label=builtin,
                    kind=kind,
                    detail=f"JavaScript {builtin}"
                ))
        
        return completions
    
    def _get_dom_completions(self, prefix: str) -> List[CompletionItem]:
        """获取 DOM API 补全"""
        completions = []
        
        for obj, methods in self.dom_apis.items():
            if prefix.startswith(obj + '.'):
                method_prefix = prefix[len(obj) + 1:]
                for method in methods:
                    if method.startswith(method_prefix):
                        completions.append(CompletionItem(
                            label=method,
                            kind=CompletionEngine.KIND_METHOD,
                            detail=f"{obj}.{method}()"
                        ))
        
        return completions
    
    def _get_import_completions(self, text: str, prefix: str) -> List[CompletionItem]:
        """获取导入模块补全"""
        completions = []
        
        # 分析 import 语句
        import_pattern = r'import\s+.*?\s+from\s+[\'"](\w+)[\'"]'
        matches = re.findall(import_pattern, text)
        
        imported_modules = set(matches)
        
        # 为导入的模块提供成员补全
        for imp in self.common_imports:
            if imp['module'] in imported_modules:
                # 检测是否解构导入
                destruct_pattern = rf'import\s+{{\s*([^}}]*)\s*}}\s+from\s+[\'"]{imp["module"]}[\'"]'
                destruct_match = re.search(destruct_pattern, text)
                
                if destruct_match:
                    # 已解构导入，直接提供成员补全
                    imported_members = [m.strip() for m in destruct_match.group(1).split(',')]
                    for member in imp['members']:
                        if member.startswith(prefix):
                            completions.append(CompletionItem(
                                label=member,
                                kind=CompletionEngine.KIND_FUNCTION,
                                detail=f"from {imp['module']}"
                            ))
                elif prefix.startswith(imp['module'] + '.'):
                    # 命名空间导入
                    method_prefix = prefix[len(imp['module']) + 1:]
                    for member in imp['members']:
                        if member.startswith(method_prefix):
                            completions.append(CompletionItem(
                                label=member,
                                kind=CompletionEngine.KIND_FUNCTION,
                                detail=f"{imp['module']}.{member}"
                            ))
                else:
                    # 直接提供模块成员补全（未使用命名空间）
                    for member in imp['members']:
                        if member.startswith(prefix):
                            completions.append(CompletionItem(
                                label=member,
                                kind=CompletionEngine.KIND_FUNCTION,
                                detail=f"from {imp['module']}"
                            ))
        
        return completions
    
    def _get_es6_completions(self, text: str, line: int, column: int) -> List[CompletionItem]:
        """获取 ES6+ 语法补全"""
        completions = []
        lines = text.split('\n')
        current_line = lines[line] if line < len(lines) else ''
        
        # const/let 声明
        if re.match(r'\s*(?:const|let|var)\s+\w+\s*$', current_line[:column]):
            completions.append(CompletionItem(
                label='=>',
                kind=CompletionEngine.KIND_SNIPPET,
                insert_text= ' => {\n    ${1:return}\n}',
                detail='Arrow function'
            ))
        
        # 对象字面量
        if current_line.strip().endswith('{'):
            completions.append(CompletionItem(
                label='method',
                kind=CompletionEngine.KIND_SNIPPET,
                insert_text='${1:methodName}(${2:args}) {\n    ${3:return}\n}',
                detail='Method shorthand'
            ))
        
        # class 声明
        if re.match(r'\s*class\s+\w+\s*$', current_line[:column]):
            completions.append(CompletionItem(
                label='constructor',
                kind=CompletionEngine.KIND_SNIPPET,
                insert_text='constructor(${1:args}) {\n    super(${2:args});\n    ${3:this.props = props};\n}',
                detail='Constructor'
            ))
        
        return completions
    
    def _get_method_chain_completions(self, prefix: str) -> List[CompletionItem]:
        """获取方法链补全"""
        completions = []
        
        # 常见类型的方法
        type_methods = {
            'array': ['map', 'filter', 'reduce', 'forEach', 'find', 'findIndex', 'some', 'every', 'slice', 'splice', 'push', 'pop'],
            'string': ['charAt', 'concat', 'includes', 'indexOf', 'match', 'replace', 'search', 'slice', 'split', 'substring', 'toUpperCase', 'toLowerCase'],
            'promise': ['then', 'catch', 'finally', 'all', 'race', 'resolve', 'reject'],
            'object': ['keys', 'values', 'entries', 'assign', 'freeze', 'seal', 'hasOwnProperty'],
            'Array': ['map', 'filter', 'reduce', 'forEach', 'find', 'findIndex', 'some', 'every', 'slice', 'splice'],
            'String': ['charAt', 'concat', 'includes', 'indexOf', 'match', 'replace', 'search', 'slice', 'split', 'substring'],
            'Promise': ['then', 'catch', 'finally', 'all', 'race', 'resolve', 'reject'],
            'Object': ['keys', 'values', 'entries', 'assign', 'freeze', 'seal', 'hasOwnProperty']
        }
        
        for type_name, methods in type_methods.items():
            # 检测 new Type 或 Type. 或小写类型
            if prefix.endswith(type_name + '.') or prefix.endswith(f'{type_name}.'):
                for method in methods:
                    completions.append(CompletionItem(
                        label=method,
                        kind=CompletionEngine.KIND_METHOD,
                        detail=f"{type_name}.{method}()"
                    ))
        
        return completions
    
    def get_hover_info(self, text: str, line: int, column: int) -> Optional[str]:
        """
        获取 JavaScript 悬停信息
        
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
        
        # 获取光标下的单词
        word_match = re.search(r'\b(\w+)\b', current_line[max(0, column-20):column+50])
        if not word_match:
            return None
        
        word = word_match.group(1)
        
        # 检查是否是内置对象
        if word in self.builtins:
            return f"`{word}` - JavaScript built-in"
        
        # 检查是否是 DOM API
        for obj in self.dom_apis:
            if word == obj:
                return f"`{word}` - DOM API"
        
        return None
