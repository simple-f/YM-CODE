#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bash Tool - Bash 命令执行工具

融合课程：s01 (Agent Loop)
"""

import asyncio
import subprocess
from typing import Dict
from .base import BaseTool


class BashTool(BaseTool):
    """Bash 工具"""
    
    name = "bash"
    description = "执行 shell 命令"
    
    async def execute(self, command: str) -> str:
        """
        执行 bash 命令
        
        参数:
            command: 命令
        
        返回:
            执行结果
        """
        try:
            # 异步执行
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # 返回结果
            if stdout:
                return stdout.decode('utf-8', errors='ignore')
            elif stderr:
                return f"错误：{stderr.decode('utf-8', errors='ignore')}"
            else:
                return f"命令执行完成，返回码：{process.returncode}"
                
        except Exception as e:
            return f"执行失败：{e}"
    
    def get_input_schema(self) -> Dict:
        """获取输入 schema"""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令"
                }
            },
            "required": ["command"]
        }
