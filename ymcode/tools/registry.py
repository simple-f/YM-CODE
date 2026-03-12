#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Registry - 工具注册表

融合课程：s02 (Tool Use)
"""

import logging
from typing import Dict, List, Optional
from .base import BaseTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        """初始化工具注册表"""
        self.tools: Dict[str, BaseTool] = {}
        self.register_default_tools()
    
    def register(self, tool: BaseTool):
        """
        注册工具
        
        参数:
            tool: 工具实例
        """
        self.tools[tool.name] = tool
        logger.info(f"注册工具：{tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        获取工具
        
        参数:
            name: 工具名
        
        返回:
            工具实例
        """
        return self.tools.get(name)
    
    async def execute(self, tool_calls: List) -> List:
        """
        执行工具调用
        
        参数:
            tool_calls: 工具调用列表
        
        返回:
            执行结果列表
        """
        results = []
        
        for call in tool_calls:
            tool_name = call.get("name")
            tool_args = call.get("input", {})
            
            tool = self.get(tool_name)
            if tool:
                try:
                    result = await tool.execute(**tool_args)
                    results.append(result)
                except Exception as e:
                    logger.error(f"工具执行失败 {tool_name}: {e}")
                    results.append(f"错误：{e}")
            else:
                logger.warning(f"未知工具：{tool_name}")
                results.append(f"未知工具：{tool_name}")
        
        return results
    
    def register_default_tools(self):
        """注册默认工具"""
        # 导入基础工具
        from .file_tools import ReadFileTool, WriteFileTool, ListDirTool
        from .bash_tool import BashTool
        from .git_tools import GitTool, GitStatusTool, GitDiffTool, GitCommitTool
        from .test_runner import RunTestTool
        from .smart_edit import SmartEditTool, InsertTextTool, DeleteLinesTool
        from .edit_history_tools import UndoTool, RedoTool, HistoryTool
        from .regex_edit import RegexReplaceTool, RegexSearchTool, RegexValidateTool
        
        # 注册基础工具
        self.register(BashTool())
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(ListDirTool())
        
        # 注册 Git 工具
        self.register(GitTool())
        self.register(GitStatusTool())
        self.register(GitDiffTool())
        self.register(GitCommitTool())
        
        # 注册测试工具
        self.register(RunTestTool())
        
        # 注册智能编辑工具
        self.register(SmartEditTool())
        self.register(InsertTextTool())
        self.register(DeleteLinesTool())
        
        # 注册编辑历史工具
        self.register(UndoTool())
        self.register(RedoTool())
        self.register(HistoryTool())
        
        # 注册正则表达式工具
        self.register(RegexReplaceTool())
        self.register(RegexSearchTool())
        self.register(RegexValidateTool())
        
        logger.info(f"已注册 {len(self.tools)} 个默认工具")
    
    def __len__(self) -> int:
        """返回工具数量"""
        return len(self.tools)
