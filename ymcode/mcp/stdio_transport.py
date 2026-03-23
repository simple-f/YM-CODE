#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP STDIO Transport - STDIO 传输协议实现

通过标准输入/输出与本地 MCP Server 通信
"""

import asyncio
import subprocess
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from .protocol import MCPProtocol, MCPMessage
from ..utils.logger import get_logger

logger = get_logger(__name__)


class STDIOTransport:
    """STDIO 传输层"""
    
    def __init__(self, command: str, args: list = None):
        """
        初始化 STDIO 传输
        
        参数:
            command: 命令（MCP Server 可执行文件）
            args: 参数列表
        """
        self.command = command
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None
        self.protocol = MCPProtocol()
        
        self._message_queue = asyncio.Queue()
        self._running = False
        self._read_task: Optional[asyncio.Task] = None
        
        logger.info(f"STDIO 传输初始化：{command} {' '.join(self.args)}")
    
    async def connect(self) -> bool:
        """
        连接到 MCP Server
        
        返回:
            是否成功
        """
        try:
            # 启动进程
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            self._running = True
            
            # 启动读取任务
            self._read_task = asyncio.create_task(self._read_loop())
            
            # 发送初始化请求
            init_request = self.protocol.initialize({
                "name": "ym-code",
                "version": "0.3.3"
            })
            
            await self._send_message(init_request)
            
            logger.info(f"STDIO 连接成功：{self.command}")
            
            return True
            
        except Exception as e:
            logger.error(f"STDIO 连接失败：{e}")
            return False
    
    async def disconnect(self) -> None:
        """断开连接（增强版 - 确保资源正确释放）"""
        logger.info("正在断开 STDIO 连接...")
        
        self._running = False
        
        # ✅ 1. 取消读取任务
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"取消读取任务失败：{e}")
            self._read_task = None
        
        # ✅ 2. 正确关闭进程
        if self.process:
            try:
                # 先尝试优雅终止
                self.process.terminate()
                
                # 等待进程退出（最多 5 秒）
                try:
                    self.process.wait(timeout=5)
                    logger.info("STDIO 进程已正常退出")
                except subprocess.TimeoutExpired:
                    # 超时后强制终止
                    logger.warning("STDIO 进程未在 5 秒内退出，强制终止...")
                    self.process.kill()
                    self.process.wait(timeout=2)
                    logger.info("STDIO 进程已被强制终止")
                
            except Exception as e:
                logger.error(f"关闭 STDIO 进程失败：{e}")
            finally:
                self.process = None
        
        # ✅ 3. 关闭管道
        try:
            if self.process and self.process.stdin:
                self.process.stdin.close()
            if self.process and self.process.stdout:
                self.process.stdout.close()
            if self.process and self.process.stderr:
                self.process.stderr.close()
        except:
            pass
        
        logger.info("STDIO 已断开连接")
    
    async def send_request(self, message: MCPMessage) -> None:
        """
        发送请求
        
        参数:
            message: MCP 消息
        """
        await self._send_message(message)
        logger.debug(f"STDIO 发送请求：{message.method}")
    
    async def _send_message(self, message: MCPMessage) -> None:
        """
        发送消息
        
        参数:
            message: MCP 消息
        """
        if not self.process:
            raise RuntimeError("未连接")
        
        json_str = message.to_json() + "\n"
        
        # 写入标准输入
        self.process.stdin.write(json_str.encode('utf-8'))
        self.process.stdin.flush()
        
        logger.debug(f"STDIO 发送：{json_str.strip()}")
    
    async def _read_loop(self) -> None:
        """读取循环"""
        buffer = ""
        
        while self._running:
            try:
                # 读取标准输出
                if self.process.stdout:
                    line = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.process.stdout.readline
                    )
                    
                    if not line:
                        # 进程结束
                        break
                    
                    buffer += line.decode('utf-8')
                    
                    # 处理完整消息（以换行符分隔）
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            await self._handle_message(line)
                
            except Exception as e:
                logger.error(f"STDIO 读取错误：{e}")
                break
        
        logger.info("STDIO 读取循环结束")
    
    async def _handle_message(self, json_str: str) -> None:
        """
        处理消息
        
        参数:
            json_str: JSON 消息
        """
        try:
            message = self.protocol.parse_response(json_str)
            
            # 放入消息队列
            await self._message_queue.put(message)
            
            logger.debug(f"STDIO 接收：{message.method or '响应'}")
            
        except Exception as e:
            logger.error(f"STDIO 消息处理错误：{e}")
    
    async def wait_for_response(self, request_id: int, timeout: float = 30.0) -> Optional[MCPMessage]:
        """
        等待响应
        
        参数:
            request_id: 请求 ID
            timeout: 超时时间（秒）
        
        返回:
            MCP 响应消息
        """
        try:
            message = await asyncio.wait_for(
                self._message_queue.get(),
                timeout=timeout
            )
            
            if message.id == request_id:
                return message
            else:
                # 不是我们要的响应，放回队列
                await self._message_queue.put(message)
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"STDIO 响应超时：request_id={request_id}")
            return None
    
    # ========== 高级方法 ==========
    
    async def initialize(self) -> bool:
        """
        初始化 MCP 连接
        
        返回:
            是否成功
        """
        request = self.protocol.initialize({
            "name": "ym-code",
            "version": "0.3.3"
        })
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id)
        
        if response and response.result:
            self.protocol.handle_initialize_result(response.result)
            return True
        
        return False
    
    async def list_tools(self):
        """
        获取工具列表
        
        返回:
            工具列表
        """
        request = self.protocol.list_tools()
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id)
        
        if response and response.result:
            return self.protocol.handle_tools_list_result(response.result)
        
        return []
    
    async def call_tool(self, name: str, arguments: Dict) -> Any:
        """
        调用工具
        
        参数:
            name: 工具名称
            arguments: 工具参数
        
        返回:
            工具执行结果
        """
        request = self.protocol.call_tool(name, arguments)
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id)
        
        if response and response.result:
            return self.protocol.handle_tool_call_result(response.result)
        
        return None
    
    async def list_resources(self):
        """
        获取资源列表
        
        返回:
            资源列表
        """
        request = self.protocol.list_resources()
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id)
        
        if response and response.result:
            return self.protocol.handle_resources_list_result(response.result)
        
        return []
    
    async def read_resource(self, uri: str) -> str:
        """
        读取资源
        
        参数:
            uri: 资源 URI
        
        返回:
            资源内容
        """
        request = self.protocol.read_resource(uri)
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id)
        
        if response and response.result:
            return self.protocol.handle_resource_read_result(response.result)
        
        return ""
    
    async def ping(self) -> bool:
        """
        Ping 测试
        
        返回:
            是否成功
        """
        request = self.protocol.ping()
        
        await self.send_request(request)
        
        response = await self.wait_for_response(request.id, timeout=5.0)
        
        return response is not None
