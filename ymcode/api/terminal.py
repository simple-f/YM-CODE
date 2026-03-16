#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 终端 API - WebSocket 实时终端
"""

import asyncio
import os
import platform
from pathlib import Path
from typing import Optional, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import subprocess

from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/terminal", tags=["terminal"])


class TerminalSession:
    """终端会话"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.process: Optional[asyncio.subprocess.Process] = None
        self.cwd = str(Path.cwd())
        self.os_type = platform.system()
        
    async def start(self):
        """启动终端进程"""
        if self.os_type == 'Windows':
            # Windows 使用 PowerShell
            self.process = await asyncio.create_subprocess_shell(
                'powershell.exe',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
        else:
            # Linux/Mac 使用 bash
            self.process = await asyncio.create_subprocess_shell(
                'bash',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd
            )
        
        logger.info(f"终端进程已启动：{self.session_id}")
    
    async def execute(self, command: str) -> Dict:
        """执行命令"""
        if not self.process:
            return {"error": "终端未启动", "stdout": "", "stderr": ""}
        
        try:
            # 发送命令
            command_with_newline = command + '\n'
            self.process.stdin.write(command_with_newline.encode('utf-8', errors='replace'))
            await self.process.stdin.drain()
            
            # 读取输出（带超时）
            try:
                stdout, stderr = await asyncio.wait_for(
                    asyncio.gather(
                        self.process.stdout.read(4096),
                        self.process.stderr.read(4096)
                    ),
                    timeout=5.0
                )
                
                # Windows 使用 GBK 解码
                if self.os_type == 'Windows':
                    stdout_text = stdout.decode('gbk', errors='replace') if stdout else ''
                    stderr_text = stderr.decode('gbk', errors='replace') if stderr else ''
                else:
                    stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ''
                    stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ''
                
                return {
                    "success": True,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": self.process.returncode
                }
                
            except asyncio.TimeoutError:
                return {
                    "success": True,
                    "stdout": "... (输出超时，已截断)",
                    "stderr": "",
                    "timeout": True
                }
                
        except Exception as e:
            logger.error(f"执行命令失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    async def close(self):
        """关闭终端"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except:
                self.process.kill()
            
            logger.info(f"终端进程已关闭：{self.session_id}")


# 全局终端会话存储
terminal_sessions: Dict[str, TerminalSession] = {}


@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket):
    """WebSocket 终端连接"""
    await websocket.accept()
    
    session_id = websocket.query_params.get("session_id", "default")
    
    # 创建或获取终端会话
    if session_id not in terminal_sessions:
        terminal = TerminalSession(session_id)
        await terminal.start()
        terminal_sessions[session_id] = terminal
    else:
        terminal = terminal_sessions[session_id]
    
    logger.info(f"终端 WebSocket 连接：{session_id}")
    
    try:
        while True:
            # 接收命令
            data = await websocket.receive_json()
            command = data.get("command", "")
            
            if command.lower() in ['exit', 'quit']:
                await websocket.send_json({
                    "type": "close",
                    "message": "终端已关闭"
                })
                break
            
            # 执行命令
            result = await terminal.execute(command)
            
            # 发送结果
            await websocket.send_json({
                "type": "output",
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "success": result.get("success", False)
            })
            
    except WebSocketDisconnect:
        logger.info(f"终端 WebSocket 断开：{session_id}")
    except Exception as e:
        logger.error(f"终端 WebSocket 错误：{e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    finally:
        # 清理终端会话（可选：保持会话）
        # if session_id in terminal_sessions:
        #     await terminal_sessions[session_id].close()
        #     del terminal_sessions[session_id]
        pass


@router.post("/execute")
async def execute_command(command: str, session_id: str = "default"):
    """执行单个命令（REST API）"""
    if session_id not in terminal_sessions:
        terminal = TerminalSession(session_id)
        await terminal.start()
        terminal_sessions[session_id] = terminal
    
    terminal = terminal_sessions[session_id]
    result = await terminal.execute(command)
    
    return result


@router.get("/sessions")
async def list_terminal_sessions():
    """列出活跃的终端会话"""
    return {
        "sessions": [
            {
                "id": sid,
                "cwd": term.cwd,
                "os": term.os_type
            }
            for sid, term in terminal_sessions.items()
        ],
        "total": len(terminal_sessions)
    }


@router.post("/close")
async def close_terminal(session_id: str):
    """关闭终端会话"""
    if session_id in terminal_sessions:
        await terminal_sessions[session_id].close()
        del terminal_sessions[session_id]
        return {"success": True, "message": "终端已关闭"}
    
    return {"success": False, "error": "会话不存在"}
