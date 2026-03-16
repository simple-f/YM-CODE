#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Analysis Skill - 代码分析技能

支持代码质量检查、复杂度分析等
"""

import logging
import ast
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeAnalysisSkill(BaseSkill):
    """代码分析技能"""
    
    def __init__(self):
        """初始化代码分析技能"""
        super().__init__('code_analysis')
        self.supported_languages = ['python', 'javascript', 'typescript']
    
    @property
    def description(self) -> str:
        return "代码分析技能 - 代码质量检查、复杂度分析、统计信息"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要分析的代码"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "typescript"],
                    "description": "编程语言",
                    "default": "python"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["complexity", "stats", "quality", "full"],
                    "description": "分析类型",
                    "default": "full"
                },
                "file_path": {
                    "type": "string",
                    "description": "文件路径（可选，用于读取文件）"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行代码分析
        
        参数:
            arguments: 输入参数
        
        返回:
            分析结果
        """
        code = arguments.get('code', '')
        language = arguments.get('language', 'python')
        analysis_type = arguments.get('analysis_type', 'full')
        file_path = arguments.get('file_path')
        
        # 从文件读取代码
        if file_path and not code:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception as e:
                return {"error": f"读取文件失败：{e}"}
        
        if not code:
            return {"error": "代码不能为空"}
        
        logger.info(f"代码分析：language={language}, type={analysis_type}")
        
        try:
            if language == 'python':
                return await self._analyze_python(code, analysis_type)
            elif language in ['javascript', 'typescript']:
                return await self._analyze_javascript(code, analysis_type)
            else:
                return {"error": f"不支持的语言：{language}"}
        
        except Exception as e:
            logger.error(f"代码分析失败：{e}")
            return {"error": str(e)}
    
    async def _analyze_python(self, code: str, analysis_type: str) -> Dict:
        """分析 Python 代码"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": f"语法错误：{e}"}
        
        result = {
            "language": "python",
            "lines": len(code.split('\n')),
            "chars": len(code)
        }
        
        if analysis_type in ['stats', 'full']:
            result['stats'] = self._get_python_stats(tree)
        
        if analysis_type in ['complexity', 'full']:
            result['complexity'] = self._get_python_complexity(tree)
        
        if analysis_type in ['quality', 'full']:
            result['quality'] = self._get_python_quality(code, tree)
        
        return result
    
    def _get_python_stats(self, tree: ast.AST) -> Dict:
        """获取 Python 代码统计信息"""
        stats = {
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'loops': 0,
            'conditionals': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats['functions'] += 1
            elif isinstance(node, ast.ClassDef):
                stats['classes'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                stats['imports'] += 1
            elif isinstance(node, (ast.For, ast.While)):
                stats['loops'] += 1
            elif isinstance(node, ast.If):
                stats['conditionals'] += 1
        
        return stats
    
    def _get_python_complexity(self, tree: ast.AST) -> Dict:
        """获取 Python 代码复杂度"""
        complexity = {
            'cyclomatic': 0,
            'max_depth': 0,
            'functions': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = self._calculate_function_complexity(node)
                complexity['functions'].append({
                    'name': node.name,
                    'complexity': func_complexity
                })
                complexity['cyclomatic'] += func_complexity
        
        return complexity
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _get_python_quality(self, code: str, tree: ast.AST) -> Dict:
        """获取 Python 代码质量评估"""
        quality = {
            'score': 100,
            'issues': [],
            'suggestions': []
        }
        
        lines = code.split('\n')
        
        # 检查长行
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            quality['issues'].append(f"发现 {len(long_lines)} 行长超过 100 字符")
            quality['score'] -= len(long_lines) * 2
        
        # 检查长函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    quality['issues'].append(f"函数 '{node.name}' 过长 ({func_lines}行)")
                    quality['score'] -= 5
        
        # 检查 docstring
        missing_docstring = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing_docstring.append(node.name)
        
        if missing_docstring:
            quality['suggestions'].append(f"以下函数/类缺少文档字符串：{', '.join(missing_docstring[:5])}")
        
        quality['score'] = max(0, quality['score'])
        
        return quality
    
    async def _analyze_javascript(self, code: str, analysis_type: str) -> Dict:
        """分析 JavaScript 代码（简化版）"""
        result = {
            "language": "javascript",
            "lines": len(code.split('\n')),
            "chars": len(code),
            "stats": {
                'functions': code.count('function '),
                'classes': code.count('class '),
                'imports': code.count('import '),
                'exports': code.count('export ')
            }
        }
        
        if analysis_type in ['quality', 'full']:
            result['quality'] = {
                'score': 100,
                'issues': [],
                'suggestions': []
            }
            
            # 简单质量检查
            lines = code.split('\n')
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            if long_lines:
                result['quality']['issues'].append(f"发现 {len(long_lines)} 行长超过 100 字符")
                result['quality']['score'] -= len(long_lines) * 2
            
            result['quality']['score'] = max(0, result['quality']['score'])
        
        return result
