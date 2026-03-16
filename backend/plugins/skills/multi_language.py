#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言支持技能

支持 JavaScript/TypeScript/Java/Go 等语言
"""

import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LanguageHandler(ABC):
    """语言处理器基类"""
    
    @property
    @abstractmethod
    def language(self) -> str:
        """语言名称"""
        pass
    
    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        """文件扩展名列表"""
        pass
    
    @abstractmethod
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析代码"""
        pass
    
    @abstractmethod
    def get_syntax_features(self) -> List[str]:
        """获取语法特性"""
        pass


class JavaScriptHandler(LanguageHandler):
    """JavaScript 语言处理器"""
    
    @property
    def language(self) -> str:
        return 'javascript'
    
    @property
    def extensions(self) -> List[str]:
        return ['.js', '.jsx', '.mjs']
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析 JavaScript 代码"""
        import re
        
        # 统计
        lines = code.split('\n')
        functions = len(re.findall(r'function\s+\w+', code))
        classes = len(re.findall(r'class\s+\w+', code))
        arrow_functions = len(re.findall(r'=>', code))
        
        return {
            'language': self.language,
            'lines': len(lines),
            'functions': functions + arrow_functions,
            'classes': classes,
            'features': self.get_syntax_features(),
            'complexity': self._calculate_complexity(code)
        }
    
    def get_syntax_features(self) -> List[str]:
        return ['ES6+', '箭头函数', '解构', 'Promise', 'async/await']
    
    def _calculate_complexity(self, code: str) -> str:
        # 简单复杂度计算
        lines = len(code.split('\n'))
        if lines < 50:
            return '低'
        elif lines < 200:
            return '中'
        else:
            return '高'


class TypeScriptHandler(LanguageHandler):
    """TypeScript 语言处理器"""
    
    @property
    def language(self) -> str:
        return 'typescript'
    
    @property
    def extensions(self) -> List[str]:
        return ['.ts', '.tsx']
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析 TypeScript 代码"""
        import re
        
        lines = code.split('\n')
        interfaces = len(re.findall(r'interface\s+\w+', code))
        types = len(re.findall(r'type\s+\w+', code))
        generics = len(re.findall(r'<[^>]+>', code))
        
        return {
            'language': self.language,
            'lines': len(lines),
            'interfaces': interfaces,
            'types': types,
            'generics': generics,
            'features': self.get_syntax_features(),
            'complexity': '中'  # 简化处理
        }
    
    def get_syntax_features(self) -> List[str]:
        return ['类型系统', '接口', '泛型', '装饰器', '枚举']


class JavaHandler(LanguageHandler):
    """Java 语言处理器"""
    
    @property
    def language(self) -> str:
        return 'java'
    
    @property
    def extensions(self) -> List[str]:
        return ['.java']
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析 Java 代码"""
        import re
        
        lines = code.split('\n')
        classes = len(re.findall(r'class\s+\w+', code))
        methods = len(re.findall(r'public\s+\w+\s+\w+\s*\(', code))
        interfaces = len(re.findall(r'interface\s+\w+', code))
        
        return {
            'language': self.language,
            'lines': len(lines),
            'classes': classes,
            'methods': methods,
            'interfaces': interfaces,
            'features': self.get_syntax_features(),
            'complexity': '中'
        }
    
    def get_syntax_features(self) -> List[str]:
        return ['面向对象', '接口', '抽象类', '泛型', '注解']


class GoHandler(LanguageHandler):
    """Go 语言处理器"""
    
    @property
    def language(self) -> str:
        return 'go'
    
    @property
    def extensions(self) -> List[str]:
        return ['.go']
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析 Go 代码"""
        import re
        
        lines = code.split('\n')
        functions = len(re.findall(r'func\s+', code))
        structs = len(re.findall(r'type\s+\w+\s+struct', code))
        interfaces = len(re.findall(r'type\s+\w+\s+interface', code))
        
        return {
            'language': self.language,
            'lines': len(lines),
            'functions': functions,
            'structs': structs,
            'interfaces': interfaces,
            'features': self.get_syntax_features(),
            'complexity': '中'
        }
    
    def get_syntax_features(self) -> List[str]:
        return ['并发', '接口', '结构体', '错误处理', 'goroutine']


class MultiLanguageSkill(BaseSkill):
    """多语言支持技能"""
    
    def __init__(self):
        """初始化多语言技能"""
        super().__init__('multi_language')
        self.handlers = {
            'javascript': JavaScriptHandler(),
            'typescript': TypeScriptHandler(),
            'java': JavaHandler(),
            'go': GoHandler()
        }
    
    @property
    def description(self) -> str:
        return "多语言支持 - JavaScript/TypeScript/Java/Go 等"
    
    @property
    def capabilities(self) -> List[str]:
        return ['multi_language', 'code_analysis', 'language_detection']
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行多语言分析
        
        参数:
            arguments: 输入参数
                - code: 代码字符串
                - language: 编程语言
                - action: 操作类型 (analyze/detect/format)
        
        返回:
            分析结果
        """
        code = arguments.get('code', '')
        language = arguments.get('language', '').lower()
        action = arguments.get('action', 'analyze')
        
        if not code:
            return {
                'success': False,
                'error': '代码不能为空'
            }
        
        if action == 'detect':
            return self._detect_language(code)
        
        handler = self.handlers.get(language)
        if not handler:
            return {
                'success': False,
                'error': f'不支持的语言：{language}',
                'supported_languages': list(self.handlers.keys())
            }
        
        try:
            if action == 'analyze':
                result = handler.analyze(code)
                return {
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'未知操作：{action}'
                }
        
        except Exception as e:
            logger.error(f"多语言分析失败：{e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_language(self, code: str) -> Dict[str, Any]:
        """检测代码语言"""
        import re
        
        # 简单启发式检测
        scores = {}
        
        # JavaScript/TypeScript
        if re.search(r'function\s+\w+\s*\(', code):
            scores['javascript'] = scores.get('javascript', 0) + 1
        if re.search(r'interface\s+\w+', code):
            scores['typescript'] = scores.get('typescript', 0) + 1
        
        # Java
        if re.search(r'public\s+class\s+\w+', code):
            scores['java'] = scores.get('java', 0) + 1
        
        # Go
        if re.search(r'func\s+\w+\s*\(', code):
            scores['go'] = scores.get('go', 0) + 1
        
        if scores:
            detected = max(scores, key=scores.get)
            confidence = scores[detected] / sum(scores.values())
            return {
                'success': True,
                'detected_language': detected,
                'confidence': f'{confidence:.0%}',
                'scores': scores
            }
        else:
            return {
                'success': False,
                'error': '无法检测语言'
            }


# 便捷函数
def create_multi_language_skill() -> MultiLanguageSkill:
    """创建多语言技能实例"""
    return MultiLanguageSkill()
