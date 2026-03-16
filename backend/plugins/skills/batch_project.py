#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量项目处理技能

支持整个项目的分析、检查和重构
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
import asyncio

from .base import BaseSkill
from .code_analyzer import CodeAnalyzerSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BatchProjectSkill(BaseSkill):
    """批量项目处理技能"""
    
    def __init__(self):
        """初始化批量项目处理技能"""
        super().__init__('batch_project')
        self.code_analyzer = CodeAnalyzerSkill()
    
    @property
    def description(self) -> str:
        return "批量项目处理 - 整个项目的分析、检查和重构"
    
    @property
    def capabilities(self) -> List[str]:
        return ['batch_analysis', 'project_check', 'refactoring', 'dependency_analysis']
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行批量项目处理
        
        参数:
            arguments: 输入参数
                - action: 操作类型 (analyze/check/refactor/dependencies)
                - path: 项目路径
                - language: 编程语言（默认 python）
                - pattern: 文件匹配模式（默认 *.py）
        
        返回:
            处理结果
        """
        action = arguments.get('action', 'analyze')
        path = arguments.get('path', '.')
        language = arguments.get('language', 'python')
        pattern = arguments.get('pattern', '*.py')
        
        project_path = Path(path)
        if not project_path.exists():
            return {
                'success': False,
                'error': f'路径不存在：{path}'
            }
        
        if action == 'analyze':
            return await self._analyze_project(project_path, language, pattern)
        elif action == 'check':
            return await self._check_project(project_path, language, pattern)
        elif action == 'refactor':
            return await self._refactor_project(project_path, language, pattern)
        elif action == 'dependencies':
            return await self._analyze_dependencies(project_path, language)
        else:
            return {
                'success': False,
                'error': f'未知操作：{action}'
            }
    
    async def _analyze_project(self, project_path: Path, language: str, pattern: str) -> Any:
        """分析项目结构"""
        try:
            # 获取所有匹配的文件
            files = list(project_path.rglob(pattern))
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            
            # 分析项目结构
            structure = {
                'total_files': len(files),
                'directories': self._count_directories(project_path),
                'languages': self._detect_languages(files),
                'structure': self._build_structure_tree(project_path, 3)
            }
            
            # 分析每个文件
            file_analysis = []
            for file in files[:50]:  # 限制分析文件数量
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    analysis = {
                        'file': str(file.relative_to(project_path)),
                        'lines': len(code.split('\n')),
                        'size': file.stat().st_size
                    }
                    file_analysis.append(analysis)
                except:
                    pass
            
            return {
                'success': True,
                'structure': structure,
                'files': file_analysis,
                'summary': {
                    'total_files': structure['total_files'],
                    'total_lines': sum(f['lines'] for f in file_analysis),
                    'total_size': sum(f['size'] for f in file_analysis)
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_project(self, project_path: Path, language: str, pattern: str) -> Any:
        """批量检查项目代码"""
        try:
            # 获取所有匹配的文件
            files = list(project_path.rglob(pattern))
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            
            # 批量检查
            results = []
            total_issues = 0
            total_errors = 0
            
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # 使用代码分析技能
                    result = await self.code_analyzer.execute({
                        'code': code,
                        'language': language
                    })
                    
                    if result.get('success'):
                        summary = result.get('summary', {})
                        issues = summary.get('total_issues', 0)
                        errors = summary.get('total_errors', 0)
                        
                        if issues > 0:
                            results.append({
                                'file': str(file.relative_to(project_path)),
                                'issues': issues,
                                'errors': errors
                            })
                            total_issues += issues
                            total_errors += errors
                
                except Exception as e:
                    logger.error(f"检查文件失败 {file}: {e}")
            
            return {
                'success': True,
                'results': results,
                'summary': {
                    'total_files': len(files),
                    'checked_files': len(results),
                    'total_issues': total_issues,
                    'total_errors': total_errors,
                    'files_with_issues': len(results)
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _refactor_project(self, project_path: Path, language: str, pattern: str) -> Any:
        """批量重构项目"""
        try:
            # 获取所有匹配的文件
            files = list(project_path.rglob(pattern))
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            
            # 批量重构
            refactored = []
            
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # 使用 Black 格式化
                    result = await self.code_analyzer.execute({
                        'code': code,
                        'language': language,
                        'tools': ['black']
                    })
                    
                    if result.get('success'):
                        formatted = result['results'][0]['result'].get('formatted_code')
                        if formatted and formatted != code:
                            # 写回文件
                            with open(file, 'w', encoding='utf-8') as f:
                                f.write(formatted)
                            refactored.append(str(file.relative_to(project_path)))
                
                except Exception as e:
                    logger.error(f"重构文件失败 {file}: {e}")
            
            return {
                'success': True,
                'refactored_files': refactored,
                'summary': {
                    'total_files': len(files),
                    'refactored_count': len(refactored)
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _analyze_dependencies(self, project_path: Path, language: str) -> Any:
        """分析项目依赖"""
        try:
            dependencies = {
                'python': [],
                'javascript': [],
                'other': []
            }
            
            # Python 依赖
            requirements_file = project_path / 'requirements.txt'
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies['python'].append(line.split('==')[0].split('>=')[0])
            
            # setup.py
            setup_file = project_path / 'setup.py'
            if setup_file.exists():
                # 简单解析 setup.py
                with open(setup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'install_requires' in content:
                        # 提取依赖
                        import re
                        matches = re.findall(r"'([^']+)'", content)
                        dependencies['python'].extend(matches)
            
            # JavaScript 依赖
            package_file = project_path / 'package.json'
            if package_file.exists():
                import json
                with open(package_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies['javascript'].extend(list(deps.keys()))
                    dependencies['javascript'].extend(list(dev_deps.keys()))
            
            return {
                'success': True,
                'dependencies': dependencies,
                'summary': {
                    'python_deps': len(dependencies['python']),
                    'javascript_deps': len(dependencies['javascript']),
                    'total_deps': len(dependencies['python']) + len(dependencies['javascript'])
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _count_directories(self, project_path: Path) -> int:
        """统计目录数量"""
        count = 0
        for item in project_path.rglob('*'):
            if item.is_dir() and not item.name.startswith('.'):
                count += 1
        return count
    
    def _detect_languages(self, files: List[Path]) -> Dict[str, int]:
        """检测编程语言"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        
        languages = {}
        for file in files:
            ext = file.suffix.lower()
            if ext in lang_map:
                lang = lang_map[ext]
                languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def _build_structure_tree(self, project_path: Path, max_depth: int = 3) -> Dict:
        """构建项目结构树"""
        tree = {
            'name': project_path.name,
            'type': 'directory',
            'children': []
        }
        
        def build_tree(path: Path, depth: int) -> Dict:
            if depth > max_depth:
                return None
            
            node = {
                'name': path.name,
                'type': 'directory' if path.is_dir() else 'file',
                'children': []
            }
            
            if path.is_dir():
                try:
                    for item in sorted(path.iterdir()):
                        if not item.name.startswith('.'):
                            child = build_tree(item, depth + 1)
                            if child:
                                node['children'].append(child)
                except PermissionError:
                    pass
            
            return node
        
        try:
            for item in sorted(project_path.iterdir()):
                if not item.name.startswith('.'):
                    child = build_tree(item, 1)
                    if child:
                        tree['children'].append(child)
        except PermissionError:
            pass
        
        return tree


# 便捷函数
def create_batch_skill() -> BatchProjectSkill:
    """创建批量项目处理技能实例"""
    return BatchProjectSkill()
