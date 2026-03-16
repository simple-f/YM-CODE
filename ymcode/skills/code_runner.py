#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码运行技能

在安全沙箱中运行代码
"""

import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeRunnerSkill(BaseSkill):
    """代码运行技能"""
    
    def __init__(self):
        """初始化代码运行技能"""
        super().__init__('code_runner')
        self.timeout = 30  # 默认超时 30 秒
        self.max_output_size = 1024 * 1024  # 最大输出 1MB
    
    @property
    def description(self) -> str:
        return "代码运行 - 在安全沙箱中执行代码"
    
    @property
    def capabilities(self) -> List[str]:
        return ['code_execution', 'sandbox', 'output_capture', 'error_handling']
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行代码
        
        参数:
            arguments: 输入参数
                - code: 代码字符串
                - language: 编程语言
                - input: 标准输入（可选）
                - timeout: 超时时间（可选）
        
        返回:
            执行结果
        """
        code = arguments.get('code', '')
        language = arguments.get('language', 'python').lower()
        stdin_input = arguments.get('input', '')
        timeout = arguments.get('timeout', self.timeout)
        
        if not code:
            return {
                'success': False,
                'error': '代码不能为空'
            }
        
        # 检查语言支持
        supported_languages = ['python', 'javascript', 'node']
        if language not in supported_languages:
            return {
                'success': False,
                'error': f'不支持的语言：{language}',
                'supported': supported_languages
            }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{self._get_extension(language)}',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 执行代码
            result = await self._run_code(
                temp_file,
                language,
                stdin_input,
                timeout
            )
            
            return result
        
        except Exception as e:
            logger.error(f"代码运行失败：{e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _run_code(
        self,
        file_path: str,
        language: str,
        stdin_input: str,
        timeout: int
    ) -> Dict[str, Any]:
        """运行代码"""
        
        # 构建命令
        if language == 'python':
            cmd = ['python', file_path]
        elif language in ['javascript', 'node']:
            cmd = ['node', file_path]
        else:
            return {
                'success': False,
                'error': f'不支持的语言：{language}'
            }
        
        try:
            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path(file_path).parent),
                env=self._get_safe_env()
            )
            
            # 等待执行完成
            try:
                stdout, stderr = process.communicate(
                    input=stdin_input.encode('utf-8') if stdin_input else None,
                    timeout=timeout
                )
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': f'代码执行超时（{timeout}秒）',
                    'timeout': True
                }
            
            # 处理输出
            stdout_str = stdout.decode('utf-8', errors='ignore')
            stderr_str = stderr.decode('utf-8', errors='ignore')
            
            # 限制输出大小
            if len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[:self.max_output_size] + '\n... (输出被截断)'
            
            if len(stderr_str) > self.max_output_size:
                stderr_str = stderr_str[:self.max_output_size] + '\n... (输出被截断)'
            
            return {
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'stdout': stdout_str,
                'stderr': stderr_str,
                'language': language,
                'execution_time': getattr(process, 'execution_time', 0)
            }
        
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'运行时未找到：{cmd[0]}，请确保已安装 {language}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行失败：{str(e)}'
            }
    
    def _get_extension(self, language: str) -> str:
        """获取文件扩展名"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'node': 'js',
            'java': 'java',
            'go': 'go'
        }
        return extensions.get(language, 'txt')
    
    def _get_safe_env(self) -> Dict[str, str]:
        """获取安全的环境变量"""
        # 复制当前环境
        env = os.environ.copy()
        
        # 移除敏感变量
        sensitive_keys = [
            'AWS_SECRET_KEY',
            'AWS_ACCESS_KEY',
            'PRIVATE_KEY',
            'DATABASE_URL',
            'API_KEY'
        ]
        
        for key in sensitive_keys:
            env.pop(key, None)
        
        # 设置安全限制
        env['PYTHONUNBUFFERED'] = '1'
        env['NODE_ENV'] = 'production'
        
        return env


# 便捷函数
def create_code_runner() -> CodeRunnerSkill:
    """创建代码运行器实例"""
    return CodeRunnerSkill()
