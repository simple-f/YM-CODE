#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 基类 - 核心技能系统

用于实现有状态、复杂逻辑的核心技能
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseSkill(ABC):
    """技能基类"""
    
    def __init__(self, name: str = None):
        """
        初始化技能
        
        参数:
            name: 技能名称
        """
        self.name = name or self.__class__.__name__
        self.enabled = True
        self.metadata = {}
        
        logger.info(f"技能初始化：{self.name}")
    
    @property
    @abstractmethod
    def description(self) -> str:
        """技能描述"""
        pass
    
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
    
    @abstractmethod
    async def execute(self, arguments: Dict) -> Any:
        """
        执行技能
        
        参数:
            arguments: 输入参数
        
        返回:
            执行结果
        """
        pass
    
    async def initialize(self) -> None:
        """初始化技能（可选）"""
        logger.info(f"技能初始化：{self.name}")
    
    async def cleanup(self) -> None:
        """清理资源（可选）"""
        logger.info(f"技能清理：{self.name}")
    
    def to_mcp_tool(self) -> Dict:
        """
        转换为 MCP 工具定义
        
        返回:
            MCP 工具定义
        """
        return {
            "name": f"skill_{self.name}",
            "description": self.description,
            "inputSchema": self.get_input_schema()
        }
    
    def __repr__(self) -> str:
        return f"Skill({self.name}, enabled={self.enabled})"
