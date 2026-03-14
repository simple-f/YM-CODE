#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Skill - HTTP 请求技能

支持发送各种 HTTP 请求
"""

import logging
from typing import Dict, Any, Optional
import json

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HTTPSkill(BaseSkill):
    """HTTP 请求技能"""
    
    def __init__(self):
        """初始化 HTTP 技能"""
        super().__init__('http')
        self.default_timeout = 30
        self.default_headers = {
            'User-Agent': 'YM-CODE/1.0',
            'Content-Type': 'application/json'
        }
    
    @property
    def description(self) -> str:
        return "HTTP 请求技能 - 发送 GET/POST/PUT/DELETE 等请求"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "请求 URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "description": "HTTP 方法",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "请求头"
                },
                "body": {
                    "type": "string",
                    "description": "请求体（JSON 字符串）"
                },
                "params": {
                    "type": "object",
                    "description": "URL 参数"
                },
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（秒）",
                    "default": 30
                }
            },
            "required": ["url"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行 HTTP 请求
        
        参数:
            arguments: 输入参数
        
        返回:
            响应结果
        """
        url = arguments.get('url', '')
        method = arguments.get('method', 'GET').upper()
        headers = arguments.get('headers', {})
        body = arguments.get('body')
        params = arguments.get('params', {})
        timeout = arguments.get('timeout', self.default_timeout)
        
        if not url:
            return {"error": "URL 不能为空"}
        
        logger.info(f"HTTP 请求：{method} {url}")
        
        try:
            # 使用 aiohttp 发送请求
            import aiohttp
            
            # 合并 headers
            merged_headers = {**self.default_headers, **headers}
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=merged_headers,
                    data=body,
                    params=params if params else None,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    # 读取响应
                    text = await response.text()
                    
                    # 尝试解析 JSON
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        data = text
                    
                    return {
                        "success": response.status < 400,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": data,
                        "url": str(response.url)
                    }
        
        except ImportError:
            logger.warning("aiohttp 未安装，使用基础实现")
            return await self._basic_request(url, method, headers, body, params, timeout)
        
        except Exception as e:
            logger.error(f"HTTP 请求失败：{e}")
            return {"error": str(e), "url": url}
    
    async def _basic_request(self, url: str, method: str, headers: dict, 
                            body: str, params: dict, timeout: int) -> Dict:
        """基础 HTTP 请求（无 aiohttp 时）"""
        import urllib.request
        import urllib.error
        import urllib.parse
        
        try:
            # 构建 URL
            if params:
                url = f"{url}?{urllib.parse.urlencode(params)}"
            
            # 准备请求体
            data = body.encode('utf-8') if body else None
            
            # 创建请求
            req = urllib.request.Request(url, data=data, headers=headers)
            req.get_method = lambda: method
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=timeout) as response:
                text = response.read().decode('utf-8')
                
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = text
                
                return {
                    "success": True,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": data,
                    "url": url
                }
        
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "status": e.code,
                "error": str(e),
                "url": url
            }
        
        except Exception as e:
            return {"error": str(e), "url": url}
