#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell Skill - Shell 命令执行技能

安全地执行 shell 命令
"""

import logging
import subprocess
import shlex
import asyncio
import platform
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ShellSkill(BaseSkill):
    """Shell 命令执行技能"""
    
    # 危险命令黑名单
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'rm -rf /*',
        'dd if=/dev/zero',
        ':(){ :|:& };:',
        'mkfs',
        'wget.*\\|.*sh',
        'curl.*\\|.*sh',
    ]
    
    # 允许的命令白名单
    ALLOWED_COMMANDS = [
        'ls', 'dir', 'pwd', 'cd',
        'cat', 'head', 'tail', 'less', 'more',
        'grep', 'find', 'which', 'whereis',
        'git', 'npm', 'pip', 'python', 'node',
        'echo', 'printf',
        'mkdir', 'rmdir', 'cp', 'mv',
        'chmod', 'chown',
        'ps', 'top', 'htop', 'kill',
        'netstat', 'ping', 'curl', 'wget',
        'docker', 'docker-compose',
    ]
    
    def __init__(self):
        """初始化 Shell 技能"""
        super().__init__('shell')
        self.default_timeout = 30
        self.default_cwd = str(Path.home())
        self.os_type = platform.system()  # Windows, Linux, Darwin
        
        # 跨平台命令别名
        self.command_aliases = {
            'Windows': {
                'ls': 'dir',
                'cat': 'type',
                'pwd': 'cd',
                'rm': 'del',
                'cp': 'copy',
                'mv': 'move',
                'mkdir': 'mkdir',
                'grep': 'findstr',
            },
            'Linux': {},
            'Darwin': {},  # macOS
        }
    
    @property
    def description(self) -> str:
        return "Shell 命令执行技能 - 安全地执行系统命令"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的命令"
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "命令参数"
                },
                "cwd": {
                    "type": "string",
                    "description": "工作目录",
                    "default": "."
                },
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（秒）",
                    "default": 30
                },
                "shell": {
                    "type": "boolean",
                    "description": "是否使用 shell 执行",
                    "default": False
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行 Shell 命令
        
        参数:
            arguments: 输入参数
        
        返回:
            执行结果
        """
        command = arguments.get('command', '')
        args = arguments.get('args', [])
        cwd = arguments.get('cwd', self.default_cwd)
        timeout = arguments.get('timeout', self.default_timeout)
        use_shell = arguments.get('shell', False)
        
        if not command:
            return {"error": "命令不能为空"}
        
        # 跨平台命令转换
        if self.os_type in self.command_aliases:
            aliases = self.command_aliases[self.os_type]
            if command in aliases:
                original_command = command
                command = aliases[command]
                logger.debug(f"命令转换：{original_command} -> {command} ({self.os_type})")
        
        # 安全检查
        safety_check = self._check_safety(command, args)
        if not safety_check['safe']:
            return {
                "error": f"危险命令被阻止：{safety_check['reason']}"
            }
        
        logger.info(f"执行 Shell 命令：{command} {' '.join(args)} [{self.os_type}]")
        
        try:
            # 构建完整命令
            if use_shell:
                full_command = f"{command} {' '.join(args)}" if args else command
                cmd = full_command
                shell = True
            else:
                # 不使用 shell 时用 exec（更安全）
                cmd = [command] + args
                shell = False
            
            # 执行命令
            if shell:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    shell=True
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "error": f"命令执行超时（{timeout}秒）",
                    "command": command
                }
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "command": command,
                "cwd": cwd
            }
        
        except FileNotFoundError:
            return {
                "error": f"命令不存在：{command}",
                "suggestion": "请检查命令是否正确"
            }
        
        except Exception as e:
            logger.error(f"命令执行失败：{e}")
            return {"error": str(e), "command": command}
    
    def _check_safety(self, command: str, args: List[str]) -> Dict:
        """
        检查命令安全性
        
        返回:
            {'safe': bool, 'reason': str}
        """
        full_command = f"{command} {' '.join(args)}"
        
        # 检查黑名单
        for dangerous in self.DANGEROUS_COMMANDS:
            if re.search(dangerous, full_command, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': f"命令包含危险模式：{dangerous}"
                }
        
        # 检查命令是否在白名单
        if command not in self.ALLOWED_COMMANDS:
            logger.warning(f"命令不在白名单：{command}")
            # 不在白名单不一定禁止，但需要记录
        
        # 检查管道和重定向
        if '|' in full_command or '>' in full_command or '&' in full_command:
            logger.warning(f"命令包含特殊字符：{full_command}")
        
        return {'safe': True, 'reason': ''}
    
    def add_allowed_command(self, command: str) -> None:
        """添加允许的命令"""
        if command not in self.ALLOWED_COMMANDS:
            self.ALLOWED_COMMANDS.append(command)
            logger.info(f"添加允许的命令：{command}")
    
    def get_allowed_commands(self) -> List[str]:
        """获取允许的命令列表"""
        return self.ALLOWED_COMMANDS.copy()


# 需要导入 asyncio
import asyncio
import re
