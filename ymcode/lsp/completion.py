#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Completion Engine - 智能代码补全引擎
"""

import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CompletionItem:
    """补全项"""
    label: str
    kind: int  # CompletionItemKind
    detail: Optional[str] = None
    documentation: Optional[str] = None
    insert_text: Optional[str] = None
    filter_text: Optional[str] = None
    sort_text: Optional[str] = None
    score: float = 0.0


class CompletionEngine:
    """代码补全引擎"""
    
    # LSP CompletionItemKind
    KIND_TEXT = 1
    KIND_METHOD = 2
    KIND_FUNCTION = 3
    KIND_CONSTRUCTOR = 4
    KIND_FIELD = 5
    KIND_VARIABLE = 6
    KIND_CLASS = 7
    KIND_INTERFACE = 8
    KIND_MODULE = 9
    KIND_PROPERTY = 10
    KIND_UNIT = 11
    KIND_VALUE = 12
    KIND_ENUM = 13
    KIND_KEYWORD = 14
    KIND_SNIPPET = 15
    KIND_COLOR = 16
    KIND_FILE = 17
    KIND_REFERENCE = 18
    KIND_FOLDER = 19
    KIND_ENUM_MEMBER = 20
    KIND_CONSTANT = 21
    KIND_STRUCT = 22
    KIND_EVENT = 23
    KIND_OPERATOR = 24
    KIND_TYPE_PARAMETER = 25
    
    def __init__(self):
        """初始化补全引擎"""
        self.language_handlers: Dict[str, Any] = {}
        self.context_cache: Dict[str, dict] = {}
        self.snippets: List[dict] = []
        self.keywords: Dict[str, List[str]] = {}
        
        self._load_snippets()
        self._load_keywords()
        
        logger.info("代码补全引擎初始化完成")
    
    def _load_snippets(self):
        """加载代码片段"""
        self.snippets = [
            {
                'label': 'for',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'for ${1:item} in ${2:iterable}:\n    ${3:pass}',
                'detail': 'For loop'
            },
            {
                'label': 'if',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'if ${1:condition}:\n    ${2:pass}',
                'detail': 'If statement'
            },
            {
                'label': 'def',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'def ${1:function_name}(${2:args}):\n    """${3:docstring}"""\n    ${4:pass}',
                'detail': 'Function definition'
            },
            {
                'label': 'class',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'class ${1:ClassName}:\n    """${2:docstring}"""\n    \n    def __init__(self, ${3:args}):\n        ${4:pass}',
                'detail': 'Class definition'
            },
            {
                'label': 'try',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'try:\n    ${1:pass}\nexcept ${2:Exception} as ${3:e}:\n    ${4:print(e)}',
                'detail': 'Try-except block'
            },
            {
                'label': 'with',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'with ${1:resource} as ${2:var}:\n    ${3:pass}',
                'detail': 'With statement'
            },
            {
                'label': 'async',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'async def ${1:function_name}(${2:args}):\n    ${3:pass}',
                'detail': 'Async function'
            },
            {
                'label': 'await',
                'kind': self.KIND_SNIPPET,
                'insert_text': 'await ${1:coroutine}',
                'detail': 'Await expression'
            }
        ]
    
    def _load_keywords(self):
        """加载编程语言关键字"""
        self.keywords = {
            'python': [
                'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try',
                'except', 'finally', 'with', 'as', 'import', 'from', 'return',
                'yield', 'raise', 'pass', 'break', 'continue', 'lambda',
                'async', 'await', 'True', 'False', 'None', 'and', 'or', 'not',
                'in', 'is', 'global', 'nonlocal', 'assert', 'del'
            ],
            'javascript': [
                'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                'do', 'switch', 'case', 'break', 'continue', 'return', 'throw',
                'try', 'catch', 'finally', 'class', 'extends', 'new', 'this',
                'super', 'import', 'export', 'default', 'async', 'await',
                'yield', 'typeof', 'instanceof', 'in', 'of', 'true', 'false',
                'null', 'undefined', 'void', 'delete'
            ]
        }
    
    def register_language(self, language_id: str, handler: Any) -> None:
        """
        注册语言处理器
        
        参数:
            language_id: 语言 ID
            handler: 处理器实例
        """
        self.language_handlers[language_id] = handler
        logger.info(f"注册语言处理器：{language_id}")
    
    async def get_completions(
        self,
        language_id: str,
        uri: str,
        text: str,
        line: int,
        column: int,
        lsp_client: Optional[Any] = None
    ) -> List[CompletionItem]:
        """
        获取代码补全建议
        
        参数:
            language_id: 语言 ID
            uri: 文档 URI
            text: 文档内容
            line: 行号
            column: 列号
            lsp_client: LSP 客户端（可选）
        
        返回:
            补全项列表
        """
        completions = []
        
        # 1. 从 LSP 服务器获取补全
        if lsp_client and lsp_client.initialized:
            try:
                lsp_completions = await lsp_client.completion(uri, line, column)
                for item in lsp_completions:
                    completions.append(self._convert_lsp_item(item))
            except Exception as e:
                logger.error(f"LSP 补全失败：{e}")
        
        # 2. 添加关键字补全
        keyword_completions = self._get_keyword_completions(language_id, text, line, column)
        completions.extend(keyword_completions)
        
        # 3. 添加代码片段补全
        snippet_completions = self._get_snippet_completions(language_id, text, line, column)
        completions.extend(snippet_completions)
        
        # 4. 语言特定的智能补全
        if language_id in self.language_handlers:
            handler = self.language_handlers[language_id]
            try:
                lang_completions = await handler.get_completions(text, line, column)
                completions.extend(lang_completions)
            except Exception as e:
                logger.error(f"语言处理器补全失败：{e}")
        
        # 5. 排序和过滤
        completions = self._filter_and_sort(completions, text, line, column)
        
        logger.debug(f"生成 {len(completions)} 个补全建议")
        
        return completions
    
    def _convert_lsp_item(self, item: dict) -> CompletionItem:
        """转换 LSP 补全项"""
        return CompletionItem(
            label=item.get('label', ''),
            kind=item.get('kind', self.KIND_TEXT),
            detail=item.get('detail'),
            documentation=self._parse_documentation(item.get('documentation')),
            insert_text=item.get('textEdit', {}).get('newText') or item.get('insertText'),
            filter_text=item.get('filterText'),
            sort_text=item.get('sortText'),
            score=0.0
        )
    
    def _parse_documentation(self, doc) -> Optional[str]:
        """解析文档字符串"""
        if doc is None:
            return None
        if isinstance(doc, str):
            return doc
        if isinstance(doc, dict):
            return doc.get('value', '')
        return str(doc)
    
    def _get_keyword_completions(self, language_id: str, text: str, line: int, column: int) -> List[CompletionItem]:
        """获取关键字补全"""
        completions = []
        keywords = self.keywords.get(language_id, [])
        
        # 获取当前行的前缀
        lines = text.split('\n')
        if line < len(lines):
            prefix = lines[line][:column].strip()
            
            for keyword in keywords:
                if keyword.startswith(prefix):
                    completions.append(CompletionItem(
                        label=keyword,
                        kind=self.KIND_KEYWORD,
                        detail=f"Keyword ({language_id})"
                    ))
        
        return completions
    
    def _get_snippet_completions(self, language_id: str, text: str, line: int, column: int) -> List[CompletionItem]:
        """获取代码片段补全"""
        completions = []
        
        # 获取当前行的前缀
        lines = text.split('\n')
        if line < len(lines):
            prefix = lines[line][:column].strip()
            
            for snippet in self.snippets:
                if snippet['label'].startswith(prefix):
                    completions.append(CompletionItem(
                        label=snippet['label'],
                        kind=snippet['kind'],
                        detail=snippet.get('detail'),
                        insert_text=snippet.get('insert_text')
                    ))
        
        return completions
    
    def _filter_and_sort(self, completions: List[CompletionItem], text: str, line: int, column: int) -> List[CompletionItem]:
        """过滤和排序补全项"""
        # 获取当前行的前缀
        lines = text.split('\n')
        prefix = ''
        if line < len(lines):
            prefix = lines[line][:column].strip().lower()
        
        # 过滤
        filtered = []
        for item in completions:
            label_lower = item.label.lower()
            if prefix and not label_lower.startswith(prefix):
                continue
            filtered.append(item)
        
        # 排序
        def sort_key(item):
            score = 0.0
            
            # 完全匹配优先
            if item.label.lower() == prefix:
                score += 100
            
            # 关键字优先
            if item.kind == self.KIND_KEYWORD:
                score += 50
            
            # 方法/函数优先
            if item.kind in [self.KIND_METHOD, self.KIND_FUNCTION]:
                score += 30
            
            # 有文档的优先
            if item.documentation:
                score += 10
            
            # 有详细信息的优先
            if item.detail:
                score += 5
            
            return (-score, item.label)
        
        filtered.sort(key=sort_key)
        
        # 限制数量
        return filtered[:50]
    
    def get_hover_info(
        self,
        language_id: str,
        text: str,
        line: int,
        column: int
    ) -> Optional[str]:
        """
        获取悬停信息
        
        参数:
            language_id: 语言 ID
            text: 文档内容
            line: 行号
            column: 列号
        
        返回:
            悬停信息
        """
        if language_id in self.language_handlers:
            handler = self.language_handlers[language_id]
            try:
                return handler.get_hover_info(text, line, column)
            except Exception as e:
                logger.error(f"获取悬停信息失败：{e}")
        
        return None
    
    def get_status(self) -> dict:
        """
        获取引擎状态
        
        返回:
            状态字典
        """
        return {
            'languages': list(self.language_handlers.keys()),
            'snippets': len(self.snippets),
            'keywords': sum(len(kws) for kws in self.keywords.values())
        }
