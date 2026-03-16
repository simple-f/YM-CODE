#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 集成技能

支持 Git 仓库操作和项目分析
"""

import logging
import subprocess
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GitIntegrationSkill(BaseSkill):
    """Git 集成技能"""
    
    def __init__(self):
        """初始化 Git 集成技能"""
        super().__init__('git')
        self.git_available = self._check_git()
    
    @property
    def description(self) -> str:
        return "Git 集成 - 代码仓库管理和分析"
    
    @property
    def capabilities(self) -> List[str]:
        return ['git', 'repository', 'project_analysis', 'batch_operations']
    
    def _check_git(self) -> bool:
        """检查 Git 是否可用"""
        import shutil
        return shutil.which('git') is not None
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行 Git 操作
        
        参数:
            arguments: 输入参数
                - action: 操作类型 (clone/analyze/commit/status)
                - repo_url: 仓库 URL（clone 需要）
                - path: 路径（analyze 需要）
        
        返回:
            操作结果
        """
        if not self.git_available:
            return {
                'success': False,
                'error': 'Git 未安装，请先安装 Git'
            }
        
        action = arguments.get('action', '')
        
        if action == 'clone':
            return await self._clone(arguments)
        elif action == 'analyze':
            return await self._analyze_repo(arguments)
        elif action == 'status':
            return await self._status(arguments)
        elif action == 'commit':
            return await self._commit(arguments)
        else:
            return {
                'success': False,
                'error': f'未知操作：{action}'
            }
    
    async def _clone(self, arguments: Dict) -> Any:
        """克隆仓库"""
        repo_url = arguments.get('repo_url', '')
        path = arguments.get('path', '.')
        
        if not repo_url:
            return {'success': False, 'error': '仓库 URL 不能为空'}
        
        try:
            result = subprocess.run(
                ['git', 'clone', repo_url, path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'仓库已克隆到 {path}',
                    'path': path
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '克隆超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _analyze_repo(self, arguments: Dict) -> Any:
        """分析仓库"""
        path = arguments.get('path', '.')
        
        try:
            repo_path = Path(path)
            if not repo_path.exists():
                return {'success': False, 'error': f'路径不存在：{path}'}
            
            # 检查是否是 Git 仓库
            git_dir = repo_path / '.git'
            if not git_dir.exists():
                return {'success': False, 'error': '不是 Git 仓库'}
            
            # 获取仓库信息
            info = self._get_repo_info(repo_path)
            
            # 分析项目结构
            structure = self._analyze_project_structure(repo_path)
            
            return {
                'success': True,
                'info': info,
                'structure': structure,
                'summary': {
                    'total_files': structure.get('total_files', 0),
                    'languages': list(structure.get('languages', {}).keys()),
                    'has_tests': structure.get('has_tests', False)
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _status(self, arguments: Dict) -> Any:
        """获取仓库状态"""
        path = arguments.get('path', '.')
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            changes = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    changes.append(line.strip())
            
            return {
                'success': True,
                'changes': changes,
                'has_changes': len(changes) > 0
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _commit(self, arguments: Dict) -> Any:
        """提交更改"""
        path = arguments.get('path', '.')
        message = arguments.get('message', '')
        
        if not message:
            return {'success': False, 'error': '提交信息不能为空'}
        
        try:
            # 添加所有更改
            subprocess.run(
                ['git', 'add', '.'],
                cwd=path,
                capture_output=True,
                timeout=30
            )
            
            # 提交
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '提交成功'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_repo_info(self, repo_path: Path) -> Dict:
        """获取仓库信息"""
        info = {}
        
        try:
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            info['branch'] = result.stdout.strip()
            
            # 获取最新提交
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%s'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            info['last_commit'] = result.stdout.strip()
            
            # 获取远程
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            info['remote'] = result.stdout.strip()
        
        except:
            pass
        
        return info
    
    def _analyze_project_structure(self, repo_path: Path) -> Dict:
        """分析项目结构"""
        structure = {
            'total_files': 0,
            'languages': {},
            'directories': {},
            'has_tests': False,
            'has_docs': False
        }
        
        # 文件扩展名映射
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }
        
        # 遍历文件
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                structure['total_files'] += 1
                
                # 统计语言
                ext = file_path.suffix.lower()
                if ext in lang_map:
                    lang = lang_map[ext]
                    structure['languages'][lang] = structure['languages'].get(lang, 0) + 1
                
                # 检查特殊目录
                if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                    structure['has_tests'] = True
                
                if 'doc' in file_path.name.lower() or 'docs' in str(file_path):
                    structure['has_docs'] = True
        
        return structure


# 便捷函数
def create_git_skill() -> GitIntegrationSkill:
    """创建 Git 集成技能实例"""
    return GitIntegrationSkill()
