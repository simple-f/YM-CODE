#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Protocol - 标准 MCP 协议实现

参考：https://github.com/anthropics/mcp
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MessageType(str, Enum):
    """MCP 消息类型"""
    # 请求
    INITIALIZE = "initialize"
    PING = "ping"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    
    # 响应
    INITIALIZE_RESULT = "initialize/result"
    TOOLS_LIST_RESULT = "tools/list/result"
    TOOLS_CALL_RESULT = "tools/call/result"
    RESOURCES_LIST_RESULT = "resources/list/result"
    RESOURCES_READ_RESULT = "resources/read/result"
    
    # 错误
    ERROR = "error"


@dataclass
class MCPMessage:
    """MCP 消息基类"""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict] = None
    result: Optional[Any] = None
    error: Optional[Dict] = None
    
    def to_json(self) -> str:
        """转换为 JSON"""
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """从 JSON 解析"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class MCPTool:
    """MCP 工具定义"""
    name: str
    description: str
    inputSchema: Dict
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class MCPResource:
    """MCP 资源定义"""
    uri: str
    name: str
    description: str
    mimeType: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class MCPProtocol:
    """MCP 协议处理器"""
    
    def __init__(self):
        """初始化 MCP 协议"""
        self.initialized = False
        self.message_id = 0
        self.pending_requests: Dict[int, any] = {}
        
        logger.info("MCP 协议初始化完成")
    
    def create_request(self, method: str, params: Dict = None) -> MCPMessage:
        """
        创建请求消息
        
        参数:
            method: 方法名
            params: 参数
        
        返回:
            MCP 请求消息
        """
        self.message_id += 1
        
        message = MCPMessage(
            id=self.message_id,
            method=method,
            params=params
        )
        
        self.pending_requests[self.message_id] = message
        
        logger.debug(f"创建请求：{method} (id={self.message_id})")
        
        return message
    
    def create_response(self, request_id: int, result: Any) -> MCPMessage:
        """
        创建响应消息
        
        参数:
            request_id: 请求 ID
            result: 结果
        
        返回:
            MCP 响应消息
        """
        message = MCPMessage(
            id=request_id,
            result=result
        )
        
        logger.debug(f"创建响应：id={request_id}")
        
        return message
    
    def create_error(self, request_id: int, code: int, message: str) -> MCPMessage:
        """
        创建错误消息
        
        参数:
            request_id: 请求 ID
            code: 错误码
            message: 错误消息
        
        返回:
            MCP 错误消息
        """
        message = MCPMessage(
            id=request_id,
            error={
                "code": code,
                "message": message
            }
        )
        
        logger.error(f"创建错误：id={request_id}, code={code}, message={message}")
        
        return message
    
    # ========== 标准方法 ==========
    
    def initialize(self, client_info: Dict) -> MCPMessage:
        """
        初始化连接
        
        参数:
            client_info: 客户端信息
        
        返回:
            初始化响应
        """
        request = self.create_request(
            MessageType.INITIALIZE,
            {
                "protocolVersion": "1.0",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": client_info
            }
        )
        
        logger.info(f"MCP 初始化：{client_info}")
        
        return request
    
    def ping(self) -> MCPMessage:
        """
        Ping 请求（心跳）
        
        返回:
            Ping 请求
        """
        request = self.create_request(MessageType.PING)
        
        logger.debug("MCP Ping")
        
        return request
    
    def list_tools(self) -> MCPMessage:
        """
        获取工具列表
        
        返回:
            工具列表请求
        """
        request = self.create_request(MessageType.TOOLS_LIST)
        
        logger.debug("MCP 获取工具列表")
        
        return request
    
    def call_tool(self, name: str, arguments: Dict) -> MCPMessage:
        """
        调用工具
        
        参数:
            name: 工具名称
            arguments: 工具参数
        
        返回:
            工具调用请求
        """
        request = self.create_request(
            MessageType.TOOLS_CALL,
            {
                "name": name,
                "arguments": arguments
            }
        )
        
        logger.info(f"MCP 调用工具：{name}")
        
        return request
    
    def list_resources(self) -> MCPMessage:
        """
        获取资源列表
        
        返回:
            资源列表请求
        """
        request = self.create_request(MessageType.RESOURCES_LIST)
        
        logger.debug("MCP 获取资源列表")
        
        return request
    
    def read_resource(self, uri: str) -> MCPMessage:
        """
        读取资源
        
        参数:
            uri: 资源 URI
        
        返回:
            资源读取请求
        """
        request = self.create_request(
            MessageType.RESOURCES_READ,
            {
                "uri": uri
            }
        )
        
        logger.info(f"MCP 读取资源：{uri}")
        
        return request
    
    # ========== 响应处理 ==========
    
    def parse_response(self, json_str: str) -> MCPMessage:
        """
        解析响应
        
        参数:
            json_str: JSON 字符串
        
        返回:
            MCP 消息
        """
        message = MCPMessage.from_json(json_str)
        
        if message.error:
            logger.error(f"MCP 错误：{message.error}")
        elif message.result:
            logger.debug(f"MCP 响应：{message.result}")
        
        return message
    
    def handle_initialize_result(self, result: Dict) -> None:
        """
        处理初始化结果
        
        参数:
            result: 初始化结果
        """
        self.initialized = True
        
        logger.info(f"MCP 初始化成功：{result}")
    
    def handle_tools_list_result(self, result: Dict) -> List[MCPTool]:
        """
        处理工具列表结果
        
        参数:
            result: 工具列表结果
        
        返回:
            工具列表
        """
        tools_data = result.get("tools", [])
        tools = [MCPTool(**tool) for tool in tools_data]
        
        logger.info(f"MCP 工具列表：{len(tools)} 个工具")
        
        return tools
    
    def handle_tool_call_result(self, result: Dict) -> Any:
        """
        处理工具调用结果
        
        参数:
            result: 工具调用结果
        
        返回:
            工具执行结果
        """
        logger.info(f"MCP 工具调用结果：{result}")
        
        return result.get("content")
    
    def handle_resources_list_result(self, result: Dict) -> List[MCPResource]:
        """
        处理资源列表结果
        
        参数:
            result: 资源列表结果
        
        返回:
            资源列表
        """
        resources_data = result.get("resources", [])
        resources = [MCPResource(**res) for res in resources_data]
        
        logger.info(f"MCP 资源列表：{len(resources)} 个资源")
        
        return resources
    
    def handle_resource_read_result(self, result: Dict) -> str:
        """
        处理资源读取结果
        
        参数:
            result: 资源读取结果
        
        返回:
            资源内容
        """
        logger.info(f"MCP 资源读取结果")
        
        return result.get("content", "")
