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
    
    # 安全路径白名单
    SAFE_PATHS = [
        os.path.expanduser('~'),
        os.path.join(os.path.expanduser('~'), 'projects'),
        os.path.join(os.path.expanduser('~'), 'workspace'),
        '/tmp',
        '/var/tmp',
    ]
    
    # 敏感文件保护
    SENSITIVE_FILES = [
        '.env',
        'id_rsa',
        'id_rsa.pub',
        '.ssh/authorized_keys',
        '/etc/passwd',
        '/etc/shadow',
    ]
    
    # 危险命令黑名单
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'rm -rf /*',
        'dd if=/dev/zero',
        ':(){ :|:& };:',
        'mkfs',
        'wget.*\\|.*sh',
        'curl.*\\|.*sh',
        'sudo',
        'su ',
        'chmod 777',
        'chown root',
    ]
    
    # 允许的命令白名单
    ALLOWED_COMMANDS = [
        # 文件操作
        'ls', 'dir', 'pwd', 'cd',
        'cat', 'head', 'tail', 'less', 'more', 'type',
        'grep', 'find', 'which', 'whereis',
        # 开发工具
        'git', 'npm', 'pip', 'python', 'python3', 'node', 'nodejs',
        'echo', 'echo.', 'printf',
        # 目录操作
        'mkdir', 'rmdir', 'cp', 'mv', 'copy', 'move', 'del', 'rm',
        'chmod', 'chown',
        # 系统命令
        'ps', 'top', 'htop', 'kill', 'tasklist', 'taskkill',
        'netstat', 'ping', 'curl', 'wget',
        'docker', 'docker-compose', 'docker-compose',
        # Windows 特殊命令
        'type', 'copy', 'move', 'del', 'ren',
        'tasklist', 'taskkill', 'systeminfo', 'ipconfig',
        'hostname', 'whoami', 'ver', 'wmic', 'powershell', 'cmd',
        'findstr', 'cls', 'timeout', 'sleep',
        # 创建文件命令
        'touch', 'ni', 'new-item',
        # Linux/Mac 命令
        'uname', 'df', 'du', 'free', 'pkill', 'clear',
        # 网络命令
        'nslookup', 'tracert', 'traceroute', 'ssh', 'scp', 'ftp',
        # 环境变量
        'set', 'env', 'export',
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
    
    def _validate_command(self, command: str) -> tuple:
        """
        验证命令安全性
        
        返回:
            (is_safe: bool, reason: str)
        """
        import re
        
        # 1. 检查黑名单
        for dangerous in self.DANGEROUS_COMMANDS:
            if re.search(dangerous, command, re.IGNORECASE):
                return False, f"包含危险命令：{dangerous}"
        
        # 2. 检查敏感文件
        for sensitive in self.SENSITIVE_FILES:
            if sensitive in command:
                return False, f"访问敏感文件：{sensitive}"
        
        # 3. 检查命令白名单（第一个单词）
        cmd = command.split()[0].lower()
        # 处理 Windows 命令
        if self.os_type == 'Windows':
            cmd = cmd.lower()
        if cmd not in self.ALLOWED_COMMANDS:
            return False, f"未授权命令：{cmd}"
        
        return True, "验证通过"
    
    def _validate_path(self, path: str) -> tuple:
        """
        验证路径安全性
        
        返回:
            (is_safe: bool, reason: str)
        """
        import os
        
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # 检查是否在安全路径内
        is_safe = any(abs_path.startswith(safe) for safe in self.SAFE_PATHS)
        if not is_safe:
            return False, f"路径不在白名单内：{abs_path}"
        
        return True, "路径安全"
    
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
        
        # 提取实际命令（处理 "dir D:\" 和 "echo." 这种情况）
        actual_command = command.split()[0] if command else ''
        command_args = command.split(maxsplit=1)[1] if ' ' in command else ''
        
        # 特殊处理：echo. -> echo (Windows 创建空文件语法)
        if actual_command == 'echo.':
            actual_command = 'echo'
        
        # 如果有 args 参数，合并到命令参数中
        if args and command_args:
            all_args = [command_args] + args
        elif args:
            all_args = args
        elif command_args:
            all_args = [command_args]
        else:
            all_args = []
        
        # 跨平台命令转换（使用实际命令）
        if self.os_type in self.command_aliases:
            aliases = self.command_aliases[self.os_type]
            if actual_command in aliases:
                original_command = actual_command
                actual_command = aliases[actual_command]
                logger.debug(f"命令转换：{original_command} -> {actual_command} ({self.os_type})")
        
        # 安全检查（使用实际命令 + 所有参数）
        safety_check = self._check_safety(actual_command, all_args)
        if not safety_check['safe']:
            return {
                "error": f"危险命令被阻止：{safety_check['reason']}"
            }
        
        logger.info(f"执行 Shell 命令：{actual_command} {' '.join(all_args)} [{self.os_type}]")
        
        try:
            # Windows 内置命令需要用 shell 执行
            windows_builtin = [
                'dir', 'cd', 'cls', 'copy', 'del', 'move', 'type', 
                'mkdir', 'rmdir', 'echo', 'ren', 'tasklist', 
                'taskkill', 'systeminfo', 'ipconfig', 'ni', 'new-item'
            ]
            # 检测是否包含特殊字符（管道、重定向等）
            full_cmd_str = f"{actual_command} {' '.join(all_args)}"
            has_special_chars = any(c in full_cmd_str for c in ['>', '<', '|', '&'])
            needs_shell = use_shell or (self.os_type == 'Windows' and (actual_command in windows_builtin or has_special_chars))
            
            # 构建完整命令
            if needs_shell:
                full_command = f"{actual_command} {' '.join(all_args)}" if all_args else actual_command
                cmd = full_command
                shell = True
                logger.debug(f"使用 shell 执行：{cmd}")
            else:
                # 不使用 shell 时用 exec（更安全）
                cmd = [actual_command] + all_args
                shell = False
                logger.debug(f"使用 exec 执行：{cmd}")
            
            # 执行命令
            if shell:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
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
            
            # Windows 平台使用 GBK 编码解码
            if self.os_type == 'Windows':
                stdout_text = stdout.decode('gbk', errors='replace')
                stderr_text = stderr.decode('gbk', errors='replace')
            else:
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
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
        
        支持两种模式:
        1. command='dir', args=['D:\\'] -> 检查 'dir'
        2. command='dir D:\\', args=[] -> 提取 'dir' 并检查
        
        返回:
            {'safe': bool, 'reason': str}
        """
        full_command = f"{command} {' '.join(args)}" if args else command
        
        # 提取实际命令（处理 "dir D:\" 这种情况）
        actual_command = command.split()[0] if command else ''
        
        # 检查黑名单
        for dangerous in self.DANGEROUS_COMMANDS:
            if re.search(dangerous, full_command, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': f"命令包含危险模式：{dangerous}"
                }
        
        # 检查命令是否在白名单（使用提取后的实际命令）
        if actual_command not in self.ALLOWED_COMMANDS:
            logger.warning(f"命令不在白名单：{command} (实际命令：{actual_command})")
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
