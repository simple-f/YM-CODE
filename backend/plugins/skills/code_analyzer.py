#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码分析技能

集成 Pylint、Black 等代码分析工具
"""

import logging
from typing import Dict, Any, List

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeAnalyzerSkill(BaseSkill):
    """代码分析技能"""
    
    def __init__(self):
        """初始化代码分析技能"""
        super().__init__('code_analyzer')
        self.analyzers = {}
        self._initialized = False
    
    @property
    def description(self) -> str:
        return "代码分析 - 检测代码质量、风格问题"
    
    @property
    def capabilities(self) -> List[str]:
        return ['code_analysis', 'quality_check', 'python', 'linting']
    
    def initialize(self):
        """延迟初始化（按需加载分析工具）"""
        if self._initialized:
            return
        
        logger.info("初始化代码分析工具...")
        
        # 可选依赖，不强制安装
        try:
            import pylint
            from .analyzers.pylint_analyzer import PylintAnalyzer
            self.analyzers['pylint'] = PylintAnalyzer()
            logger.info("✓ Pylint 分析器已加载")
        except ImportError:
            logger.warning("Pylint 未安装，跳过（pip install pylint）")
        
        try:
            import black
            from .analyzers.black_formatter import BlackFormatter
            self.analyzers['black'] = BlackFormatter()
            logger.info("✓ Black 格式化器已加载")
        except ImportError:
            logger.warning("Black 未安装，跳过（pip install black）")
        
        try:
            import flake8
            from .analyzers.flake8_checker import Flake8Checker
            self.analyzers['flake8'] = Flake8Checker()
            logger.info("✓ Flake8 检查器已加载")
        except ImportError:
            logger.warning("Flake8 未安装，跳过（pip install flake8）")
        
        self._initialized = True
        logger.info(f"代码分析工具初始化完成（已加载 {len(self.analyzers)} 个工具）")
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行代码分析
        
        参数:
            arguments: 输入参数
                - code: 要分析的代码
                - language: 编程语言（默认 python）
                - tools: 使用的工具列表（默认全部）
        
        返回:
            分析结果
        """
        self.initialize()  # 按需加载
        
        code = arguments.get('code', '')
        language = arguments.get('language', 'python')
        tools = arguments.get('tools', list(self.analyzers.keys()))
        
        if not code:
            return {
                'success': False,
                'error': '代码不能为空'
            }
        
        if language != 'python':
            return {
                'success': False,
                'error': f'暂不支持 {language} 语言，仅支持 python'
            }
        
        results = []
        for tool_name in tools:
            if tool_name not in self.analyzers:
                logger.warning(f"分析工具不存在：{tool_name}")
                continue
            
            analyzer = self.analyzers[tool_name]
            if not analyzer.supports(language):
                logger.warning(f"工具 {tool_name} 不支持 {language}")
                continue
            
            try:
                result = analyzer.analyze(code)
                results.append({
                    'tool': tool_name,
                    'result': result
                })
            except Exception as e:
                logger.error(f"{tool_name} 分析失败：{e}")
                results.append({
                    'tool': tool_name,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'language': language,
            'results': results,
            'tools_used': [r['tool'] for r in results],
            'summary': self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """生成分析摘要"""
        total_issues = 0
        total_errors = 0
        total_warnings = 0
        
        for result in results:
            if 'error' in result:
                total_errors += 1
                continue
            
            analysis = result.get('result', {})
            total_issues += analysis.get('issue_count', 0)
            total_warnings += analysis.get('warning_count', 0)
        
        return {
            'total_issues': total_issues,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'tools_run': len(results)
        }


# 便捷函数
def create_code_analyzer() -> CodeAnalyzerSkill:
    """创建代码分析器实例"""
    return CodeAnalyzerSkill()
