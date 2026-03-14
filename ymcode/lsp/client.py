#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSP Client - Language Server Protocol 客户端
基于 pygls 库实现
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path

try:
    from pygls.workspace import Workspace
    from pygls.protocol import LanguageServerProtocol
    from pygls.server import LanguageServer
    LSP_AVAILABLE = True
except ImportError:
    LSP_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)


class LSPClient:
    """LSP 客户端"""
    
    def __init__(self):
        """初始化 LSP 客户端"""
        self.server: Optional[Any] = None
        self.workspace: Optional[Workspace] = None
        self.initialized = False
        self.server_process: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.message_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        
        logger.info("LSP Client 初始化完成")
    
    async def start_server(self, command: str, args: List[str], cwd: Optional[str] = None) -> bool:
        """
        启动 LSP 服务器进程
        
        参数:
            command: 命令
            args: 参数列表
            cwd: 工作目录
        
        返回:
            是否成功
        """
        if not LSP_AVAILABLE:
            logger.error("pygls 库未安装，请运行：pip install pygls")
            return False
        
        logger.info(f"启动 LSP 服务器：{command} {' '.join(args)}")
        
        try:
            # 启动子进程
            self.server_process = await asyncio.create_subprocess_exec(
                command,
                *args,
                cwd=cwd or Path.cwd(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info(f"LSP 服务器进程已启动 (PID: {self.server_process.pid})")
            
            # 创建 IO 流
            self.reader = asyncio.StreamReader()
            self.writer = asyncio.StreamWriter(self.server_process.stdin, None, None, asyncio.get_event_loop())
            
            # 启动读取循环
            asyncio.create_task(self._read_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"LSP 服务器启动失败：{e}")
            return False
    
    async def _read_loop(self):
        """读取 LSP 服务器响应"""
        try:
            while self.server_process and self.server_process.returncode is None:
                # 读取 Content-Length
                line = await self.server_process.stdout.readline()
                if not line:
                    break
                
                if line.startswith(b'Content-Length: '):
                    length = int(line.decode().split(':')[1].strip())
                    
                    # 读取空行
                    await self.server_process.stdout.readline()
                    
                    # 读取消息体
                    body = await self.server_process.stdout.readexactly(length)
                    
                    # 解析消息
                    await self._handle_message(body)
        except Exception as e:
            logger.error(f"LSP 读取循环错误：{e}")
    
    async def _handle_message(self, body: bytes):
        """处理 LSP 消息"""
        try:
            message = json.loads(body.decode('utf-8'))
            
            # 响应消息
            if 'id' in message and 'result' in message:
                msg_id = message['id']
                if msg_id in self.pending_requests:
                    self.pending_requests[msg_id].set_result(message['result'])
                    del self.pending_requests[msg_id]
            
            # 通知消息（如诊断信息）
            elif 'method' in message:
                await self._handle_notification(message)
                
        except Exception as e:
            logger.error(f"处理 LSP 消息失败：{e}")
    
    async def _handle_notification(self, message: dict):
        """处理 LSP 通知"""
        method = message.get('method', '')
        params = message.get('params', {})
        
        if method == 'textDocument/publishDiagnostics':
            # 诊断信息（错误、警告等）
            logger.debug(f"收到诊断信息：{params}")
        elif method == 'window/logMessage':
            # 日志消息
            logger.debug(f"LSP 日志：{params.get('message', '')}")
    
    def _send_request(self, method: str, params: dict) -> int:
        """发送 LSP 请求"""
        self.message_id += 1
        msg_id = self.message_id
        
        message = {
            'jsonrpc': '2.0',
            'id': msg_id,
            'method': method,
            'params': params
        }
        
        body = json.dumps(message).encode('utf-8')
        header = f"Content-Length: {len(body)}\r\n\r\n".encode('utf-8')
        
        if self.server_process and self.server_process.stdin:
            self.server_process.stdin.write(header + body)
        
        return msg_id
    
    async def initialize(self, root_uri: str) -> bool:
        """
        初始化 LSP 连接
        
        参数:
            root_uri: 项目根目录 URI
        
        返回:
            是否成功
        """
        logger.info(f"初始化 LSP 连接：{root_uri}")
        
        params = {
            'processId': None,
            'rootUri': root_uri,
            'capabilities': {
                'textDocument': {
                    'completion': {
                        'completionItem': {
                            'snippetSupport': True
                        }
                    }
                }
            }
        }
        
        msg_id = self._send_request('initialize', params)
        self.pending_requests[msg_id] = asyncio.Future()
        
        try:
            result = await asyncio.wait_for(self.pending_requests[msg_id], timeout=30.0)
            self.initialized = True
            logger.info("LSP 连接初始化成功")
            return True
        except asyncio.TimeoutError:
            logger.error("LSP 初始化超时")
            return False
        except Exception as e:
            logger.error(f"LSP 初始化失败：{e}")
            return False
    
    async def did_open(self, uri: str, text: str, version: int = 1) -> None:
        """
        通知服务器文档已打开
        
        参数:
            uri: 文档 URI
            text: 文档内容
            version: 版本号
        """
        params = {
            'textDocument': {
                'uri': uri,
                'languageId': uri.split('.')[-1],
                'version': version,
                'text': text
            }
        }
        self._send_request('textDocument/didOpen', params)
        logger.debug(f"文档已打开：{uri}")
    
    async def did_change(self, uri: str, text: str, version: int) -> None:
        """
        通知服务器文档已更改
        
        参数:
            uri: 文档 URI
            text: 文档内容
            version: 版本号
        """
        params = {
            'textDocument': {
                'uri': uri,
                'version': version
            },
            'contentChanges': [
                {'text': text}
            ]
        }
        self._send_request('textDocument/didChange', params)
    
    async def completion(self, uri: str, line: int, column: int) -> List[dict]:
        """
        获取代码补全建议
        
        参数:
            uri: 文档 URI
            line: 行号（0-based）
            column: 列号（0-based）
        
        返回:
            补全建议列表
        """
        params = {
            'textDocument': {
                'uri': uri
            },
            'position': {
                'line': line,
                'character': column
            }
        }
        
        msg_id = self._send_request('textDocument/completion', params)
        self.pending_requests[msg_id] = asyncio.Future()
        
        try:
            result = await asyncio.wait_for(self.pending_requests[msg_id], timeout=10.0)
            
            if result is None:
                return []
            
            # 处理补全列表
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'items' in result:
                return result['items']
            
            return []
            
        except asyncio.TimeoutError:
            logger.warning("代码补全超时")
            return []
        except Exception as e:
            logger.error(f"代码补全失败：{e}")
            return []
    
    async def hover(self, uri: str, line: int, column: int) -> Optional[str]:
        """
        获取悬停信息
        
        参数:
            uri: 文档 URI
            line: 行号
            column: 列号
        
        返回:
            悬停信息文本
        """
        params = {
            'textDocument': {
                'uri': uri
            },
            'position': {
                'line': line,
                'character': column
            }
        }
        
        msg_id = self._send_request('textDocument/hover', params)
        self.pending_requests[msg_id] = asyncio.Future()
        
        try:
            result = await asyncio.wait_for(self.pending_requests[msg_id], timeout=5.0)
            
            if result and 'contents' in result:
                contents = result['contents']
                if isinstance(contents, dict) and 'value' in contents:
                    return contents['value']
                elif isinstance(contents, str):
                    return contents
            
            return None
            
        except Exception as e:
            logger.error(f"悬停信息获取失败：{e}")
            return None
    
    async def definition(self, uri: str, line: int, column: int) -> List[dict]:
        """
        跳转到定义
        
        参数:
            uri: 文档 URI
            line: 行号
            column: 列号
        
        返回:
            定义位置列表
        """
        params = {
            'textDocument': {
                'uri': uri
            },
            'position': {
                'line': line,
                'character': column
            }
        }
        
        msg_id = self._send_request('textDocument/definition', params)
        self.pending_requests[msg_id] = asyncio.Future()
        
        try:
            result = await asyncio.wait_for(self.pending_requests[msg_id], timeout=5.0)
            
            if result is None:
                return []
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return [result]
            
            return []
            
        except Exception as e:
            logger.error(f"跳转定义失败：{e}")
            return []
    
    async def shutdown(self) -> None:
        """关闭 LSP 连接"""
        logger.info("关闭 LSP 连接...")
        
        if self.server_process:
            # 发送 shutdown 请求
            self._send_request('shutdown', {})
            
            # 发送 exit 通知
            self._send_request('exit', {})
            
            # 等待进程结束
            try:
                await asyncio.wait_for(self.server_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.server_process.kill()
            
            logger.info("LSP 连接已关闭")
    
    def get_status(self) -> dict:
        """
        获取 LSP 状态
        
        返回:
            状态字典
        """
        return {
            'initialized': self.initialized,
            'server_running': self.server_process and self.server_process.returncode is None,
            'pid': self.server_process.pid if self.server_process else None
        }
