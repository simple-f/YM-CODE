#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Skills Server - 将 Skills 暴露为 MCP 工具
"""

import logging
from typing import Dict, List, Any

from ..skills.base import BaseSkill
from .client import MCPServer, MCPTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SkillsMCPServer:
    """Skills MCP 服务器"""
    
    def __init__(self, skills: Dict[str, BaseSkill] = None):
        """
        初始化 Skills MCP 服务器
        
        参数:
            skills: 技能字典 {skill_name: skill_instance}
        """
        self.skills = skills or {}
        self.server = MCPServer(
            name="skills",
            url="local://skills"
        )
        self.server.connected = True
        
        # 注册所有技能为 MCP 工具
        self._register_all_tools()
        
        logger.info(f"Skills MCP Server 初始化完成，{len(self.skills)} 个技能")
    
    def add_skill(self, name: str, skill: BaseSkill) -> None:
        """
        添加技能
        
        参数:
            name: 技能名称
            skill: 技能实例
        """
        self.skills[name] = skill
        self._register_tool(name, skill)
        
        logger.info(f"添加技能：{name}")
    
    def remove_skill(self, name: str) -> None:
        """
        移除技能
        
        参数:
            name: 技能名称
        """
        if name in self.skills:
            del self.skills[name]
            
            # 从服务器移除工具
            self.server.tools = [t for t in self.server.tools if t.name != f"skill_{name}"]
            
            logger.info(f"移除技能：{name}")
    
    def _register_all_tools(self) -> None:
        """注册所有技能为 MCP 工具"""
        for name, skill in self.skills.items():
            self._register_tool(name, skill)
    
    def _register_tool(self, name: str, skill: BaseSkill) -> None:
        """
        注册单个技能为 MCP 工具
        
        参数:
            name: 技能名称
            skill: 技能实例
        """
        tool = MCPTool(
            name=f"skill_{name}",
            description=skill.description,
            input_schema=skill.get_input_schema(),
            server_name="skills"
        )
        
        self.server.tools.append(tool)
        
        logger.debug(f"注册 MCP 工具：{tool.name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        调用 MCP 工具（实际调用技能）
        
        参数:
            tool_name: 工具名称（格式：skill_{skill_name}）
            arguments: 工具参数
        
        返回:
            执行结果
        """
        # 解析工具名称
        if not tool_name.startswith("skill_"):
            raise ValueError(f"无效的工具名称：{tool_name}")
        
        skill_name = tool_name.replace("skill_", "")
        
        if skill_name not in self.skills:
            raise ValueError(f"技能不存在：{skill_name}")
        
        skill = self.skills[skill_name]
        
        if not skill.enabled:
            raise ValueError(f"技能已禁用：{skill_name}")
        
        logger.info(f"调用技能：{skill_name}")
        logger.debug(f"参数：{arguments}")
        
        try:
            # 执行技能
            result = await skill.execute(arguments)
            
            logger.debug(f"技能执行结果：{result}")
            
            return result
            
        except Exception as e:
            logger.error(f"技能执行失败：{e}")
            raise
    
    def get_tools_definition(self) -> List[Dict]:
        """
        获取工具定义（用于传递给 LLM）
        
        返回:
            工具定义列表
        """
        return [tool.to_dict() for tool in self.server.tools]
    
    def get_status(self) -> Dict:
        """
        获取状态信息
        
        返回:
            状态字典
        """
        return {
            "name": self.server.name,
            "connected": self.server.connected,
            "skills_count": len(self.skills),
            "tools_count": len(self.server.tools),
            "skills": list(self.skills.keys())
        }
