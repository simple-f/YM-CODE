#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Indexer - 代码索引器
"""

import logging
import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Symbol:
    """代码符号"""
    name: str
    type: str  # function, class, variable, constant
    file: str
    line: int
    column: int
    end_line: int
    end_column: int
    signature: Optional[str]
    docstring: Optional[str]
    references: List[str]


@dataclass
class Reference:
    """符号引用"""
    from_file: str
    to_file: str
    to_symbol: str
    line: int
    type: str  # import, call, access


class CodeIndexer:
    """代码索引器"""
    
    def __init__(self, root_path: str = None):
        """
        初始化代码索引器
        
        参数:
            root_path: 项目根路径
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.symbols: Dict[str, List[Symbol]] = defaultdict(list)
        self.references: List[Reference] = []
        self.file_index: Dict[str, Dict] = {}
        
        logger.info(f"代码索引器初始化完成：{self.root_path}")
    
    def index_file(self, file_path: str, content: str = None) -> Dict:
        """
        索引单个文件
        
        参数:
            file_path: 文件路径
            content: 文件内容（可选）
        
        返回:
            索引结果
        """
        path = Path(file_path)
        rel_path = str(path.relative_to(self.root_path)) if path.is_absolute() else file_path
        
        logger.debug(f"索引文件：{rel_path}")
        
        # 读取内容
        if content is None:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"读取文件失败：{e}")
                return {}
        
        # 根据语言选择索引器
        extension = path.suffix.lower()
        
        if extension == '.py':
            index = self._index_python(rel_path, content)
        elif extension in ['.js', '.jsx', '.ts', '.tsx']:
            index = self._index_javascript(rel_path, content)
        else:
            index = self._index_generic(rel_path, content)
        
        # 缓存索引
        self.file_index[rel_path] = index
        
        return index
    
    def _index_python(self, file_path: str, content: str) -> Dict:
        """索引 Python 文件"""
        import ast
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Python 语法错误 {file_path}: {e}")
            return {'symbols': [], 'error': str(e)}
        
        symbols = []
        lines = content.split('\n')
        
        # 遍历 AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbol = Symbol(
                    name=node.name,
                    type='function',
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    end_line=getattr(node, 'end_lineno', node.lineno),
                    end_column=getattr(node, 'end_col_offset', node.col_offset),
                    signature=self._get_python_signature(node),
                    docstring=ast.get_docstring(node),
                    references=[]
                )
                symbols.append(symbol)
                self.symbols[f"function:{node.name}"].append(symbol)
            
            elif isinstance(node, ast.ClassDef):
                symbol = Symbol(
                    name=node.name,
                    type='class',
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    end_line=getattr(node, 'end_lineno', node.lineno),
                    end_column=getattr(node, 'end_col_offset', node.col_offset),
                    signature=f"class {node.name}",
                    docstring=ast.get_docstring(node),
                    references=[]
                )
                symbols.append(symbol)
                self.symbols[f"class:{node.name}"].append(symbol)
        
        return {
            'language': 'python',
            'symbols': [asdict(s) for s in symbols],
            'lines': len(lines)
        }
    
    def _index_javascript(self, file_path: str, content: str) -> Dict:
        """索引 JavaScript/TypeScript 文件"""
        import re
        
        symbols = []
        lines = content.split('\n')
        
        # 匹配函数定义
        for i, line in enumerate(lines, 1):
            # function declaration
            match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                symbol = Symbol(
                    name=match.group(1),
                    type='function',
                    file=file_path,
                    line=i,
                    column=line.index(match.group(0)),
                    end_line=i,
                    end_column=len(line),
                    signature=f"function {match.group(1)}({match.group(2)})",
                    docstring=None,
                    references=[]
                )
                symbols.append(symbol)
                self.symbols[f"function:{match.group(1)}"].append(symbol)
            
            # class declaration
            match = re.search(r'class\s+(\w+)', line)
            if match:
                symbol = Symbol(
                    name=match.group(1),
                    type='class',
                    file=file_path,
                    line=i,
                    column=line.index(match.group(0)),
                    end_line=i,
                    end_column=len(line),
                    signature=f"class {match.group(1)}",
                    docstring=None,
                    references=[]
                )
                symbols.append(symbol)
                self.symbols[f"class:{match.group(1)}"].append(symbol)
            
            # const/let function
            match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>', line)
            if match:
                symbol = Symbol(
                    name=match.group(1),
                    type='function',
                    file=file_path,
                    line=i,
                    column=line.index(match.group(0)),
                    end_line=i,
                    end_column=len(line),
                    signature=f"{match.group(1)}({match.group(2)}) => ...",
                    docstring=None,
                    references=[]
                )
                symbols.append(symbol)
                self.symbols[f"function:{match.group(1)}"].append(symbol)
        
        return {
            'language': 'javascript',
            'symbols': [asdict(s) for s in symbols],
            'lines': len(lines)
        }
    
    def _index_generic(self, file_path: str, content: str) -> Dict:
        """通用索引（简单统计）"""
        lines = content.split('\n')
        
        return {
            'language': 'unknown',
            'symbols': [],
            'lines': len(lines),
            'chars': len(content)
        }
    
    def _get_python_signature(self, node) -> str:
        """获取 Python 函数签名"""
        import ast
        
        args = []
        if node.args.args:
            for arg in node.args.args:
                arg_name = arg.arg
                if hasattr(arg, 'annotation') and arg.annotation:
                    arg_name += ": ..."
                args.append(arg_name)
        
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        return f"def {node.name}({', '.join(args)})"
    
    def find_symbol(self, name: str, symbol_type: str = None) -> List[Symbol]:
        """查找符号"""
        key = f"{symbol_type}:{name}" if symbol_type else None
        
        if key and key in self.symbols:
            return self.symbols[key]
        
        # 模糊匹配 - 支持多种匹配方式
        results = []
        for symbol_key, symbols in self.symbols.items():
            # 精确匹配符号名
            if f":{name}" in symbol_key or symbol_key.endswith(f":{name}"):
                results.extend(symbols)
            # 或者模糊匹配
            elif name.lower() in symbol_key.lower():
                results.extend(symbols)
        
        return results
    
    def find_references(self, symbol: Symbol) -> List[Reference]:
        """查找符号引用"""
        # 简化实现：搜索所有文件中对该符号的引用
        references = []
        
        for file_path, index in self.file_index.items():
            if file_path == symbol.file:
                continue
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if symbol.name in content:
                    # 找到引用
                    references.append(Reference(
                        from_file=file_path,
                        to_file=symbol.file,
                        to_symbol=symbol.name,
                        line=0,  # TODO: 精确定位
                        type='reference'
                    ))
            except Exception:
                pass
        
        return references
    
    def index_project(self, file_paths: List[str]) -> Dict:
        """索引整个项目"""
        logger.info(f"开始索引项目：{len(file_paths)} 个文件")
        
        for file_path in file_paths:
            try:
                self.index_file(file_path)
            except Exception as e:
                logger.debug(f"索引文件失败 {file_path}: {e}")
        
        logger.info(f"项目索引完成：{len(self.symbols)} 个符号")
        
        return self.get_summary()
    
    def get_summary(self) -> Dict:
        """获取索引摘要"""
        symbol_counts = defaultdict(int)
        for key, symbols in self.symbols.items():
            symbol_type = key.split(':')[0]
            symbol_counts[symbol_type] += len(symbols)
        
        return {
            'total_files': len(self.file_index),
            'total_symbols': sum(len(s) for s in self.symbols.values()),
            'by_type': dict(symbol_counts),
            'unique_symbols': len(self.symbols)
        }
    
    def search(self, query: str) -> List[Dict]:
        """搜索符号"""
        results = []
        
        for key, symbols in self.symbols.items():
            if query.lower() in key.lower():
                for symbol in symbols:
                    results.append({
                        'name': symbol.name,
                        'type': symbol.type,
                        'file': symbol.file,
                        'line': symbol.line,
                        'signature': symbol.signature
                    })
        
        return results[:50]  # 限制结果数
    
    def save_to_file(self, output_path: str) -> None:
        """保存索引到文件"""
        data = {
            'summary': self.get_summary(),
            'symbols': {
                key: [asdict(s) for s in symbols]
                for key, symbols in self.symbols.items()
            },
            'file_index': self.file_index
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"索引已保存到：{output_path}")
