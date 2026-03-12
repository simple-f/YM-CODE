#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Tool - 工具基类

融合课程：s02 (Tool Use)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """工具基类"""
    
    name: str = "base_tool"
    description: str = "基础工具"
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        执行工具
        
        参数:
            **kwargs: 工具参数
        
        返回:
            执行结果
        """
        pass
    
    def to_dict(self) -> Dict:
        """
        转换为字典（用于 LLM）
        
        返回:
            工具定义字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema()
        }
    
    def get_input_schema(self) -> Dict:
        """
        获取输入 schema
        
        返回:
            JSON Schema
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
