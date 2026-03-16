#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能市场模块

技能已经内置，市场只是展示和管理（启用/禁用/配置）
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

from .base import BaseSkill
from .registry import get_registry
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SkillInfo:
    """技能信息（用于市场展示）"""
    
    def __init__(self, 
                 name: str,
                 role: str,
                 description: str,
                 capabilities: List[str],
                 version: str = "1.0.0",
                 author: str = "YM-CODE Team",
                 enabled: bool = True,
                 builtin: bool = True):
        self.name = name
        self.role = role
        self.description = description
        self.capabilities = capabilities
        self.version = version
        self.author = author
        self.enabled = enabled
        self.builtin = builtin  # 是否内置技能
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled,
            "builtin": self.builtin,
            "downloadable": False  # 内置技能不可下载，只能启用/禁用
        }


class SkillMarketplace:
    """技能市场
    
    核心理念：
    - 技能已经内置，不需要下载
    - 市场只是展示和管理（启用/禁用/配置）
    """
    
    def __init__(self):
        """初始化技能市场"""
        self.registry = get_registry()
        self.skill_configs: Dict[str, Dict] = {}
        logger.info("技能市场初始化完成")
    
    def list_all_skills(self) -> List[Dict]:
        """列出所有技能（包括已启用和未启用）"""
        skills = []
        
        # 获取已注册的技能
        registered_skills = self.registry.list_agents()
        
        for skill_data in registered_skills:
            skill_info = SkillInfo(
                name=skill_data.get('name', ''),
                role=skill_data.get('role', ''),
                description=skill_data.get('description', ''),
                capabilities=skill_data.get('capabilities', []),
                enabled=skill_data.get('enabled', True),
                builtin=True
            )
            skills.append(skill_info.to_dict())
        
        # 添加预定义但未实例化的技能模板
        predefined_skills = self._get_predefined_skills()
        for predefined in predefined_skills:
            if not any(s['name'] == predefined['name'] for s in skills):
                skills.append(predefined)
        
        return skills
    
    def _get_predefined_skills(self) -> List[Dict]:
        """获取预定义技能模板"""
        return [
            {
                "name": "MemorySkill",
                "role": "memory",
                "description": "记忆管理 - 保存和回忆对话历史",
                "capabilities": ["memory", "context", "recall"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "SearchSkill",
                "role": "search",
                "description": "网络搜索 - 搜索互联网信息",
                "capabilities": ["web_search", "information_retrieval"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "HTTPSkill",
                "role": "http_client",
                "description": "HTTP 请求 - 发送 API 请求",
                "capabilities": ["http", "api", "rest"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "ShellSkill",
                "role": "shell",
                "description": "Shell 命令 - 执行系统命令",
                "capabilities": ["shell", "command_line", "automation"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "CodeAnalysisSkill",
                "role": "code_analyzer",
                "description": "代码分析 - 分析代码质量和结构",
                "capabilities": ["code_analysis", "quality_check", "metrics"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "DatabaseSkill",
                "role": "database",
                "description": "数据库 - SQL 查询和管理",
                "capabilities": ["sql", "database", "mysql", "postgresql"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "FormatterSkill",
                "role": "formatter",
                "description": "格式化 - 代码格式化",
                "capabilities": ["formatting", "linting", "python", "javascript"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "DockerSkill",
                "role": "docker",
                "description": "Docker - 容器管理",
                "capabilities": ["docker", "containers", "deployment"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "ChatSkill",
                "role": "chat",
                "description": "聊天 - 自然对话",
                "capabilities": ["conversation", "chat", "dialogue"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "LLMSkill",
                "role": "llm",
                "description": "LLM - 大语言模型调用",
                "capabilities": ["llm", "ai", "generation"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            },
            {
                "name": "SelfImprovementSkill",
                "role": "self_improvement",
                "description": "自我提升 - 从经验中学习",
                "capabilities": ["learning", "improvement", "optimization"],
                "version": "1.0.0",
                "author": "YM-CODE Team",
                "enabled": True,
                "builtin": True,
                "downloadable": False
            }
        ]
    
    def enable_skill(self, skill_name: str) -> bool:
        """
        启用技能
        
        参数:
            skill_name: 技能名称
        
        返回:
            是否成功
        """
        registry = get_registry()
        agent = registry.get(skill_name)
        
        if not agent:
            logger.warning(f"技能不存在：{skill_name}")
            return False
        
        agent.enabled = True
        logger.info(f"启用技能：{skill_name}")
        return True
    
    def disable_skill(self, skill_name: str) -> bool:
        """
        禁用技能
        
        参数:
            skill_name: 技能名称
        
        返回:
            是否成功
        """
        registry = get_registry()
        agent = registry.get(skill_name)
        
        if not agent:
            logger.warning(f"技能不存在：{skill_name}")
            return False
        
        agent.enabled = False
        logger.info(f"禁用技能：{skill_name}")
        return True
    
    def configure_skill(self, skill_name: str, config: Dict) -> bool:
        """
        配置技能
        
        参数:
            skill_name: 技能名称
            config: 配置字典
        
        返回:
            是否成功
        """
        self.skill_configs[skill_name] = config
        logger.info(f"配置技能 {skill_name}: {config}")
        return True
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """获取技能详细信息"""
        skills = self.list_all_skills()
        for skill in skills:
            if skill['name'] == skill_name:
                return skill
        return None
    
    def get_enabled_skills(self) -> List[Dict]:
        """获取已启用的技能"""
        all_skills = self.list_all_skills()
        return [s for s in all_skills if s.get('enabled', True)]
    
    def get_disabled_skills(self) -> List[Dict]:
        """获取已禁用的技能"""
        all_skills = self.list_all_skills()
        return [s for s in all_skills if not s.get('enabled', True)]


# 全局技能市场实例
_marketplace: Optional[SkillMarketplace] = None

def get_skill_marketplace() -> SkillMarketplace:
    """获取全局技能市场实例"""
    global _marketplace
    if _marketplace is None:
        _marketplace = SkillMarketplace()
    return _marketplace


# 便捷函数
def list_skills() -> List[Dict]:
    """列出所有技能"""
    return get_skill_marketplace().list_all_skills()


def enable_skill(skill_name: str) -> bool:
    """启用技能"""
    return get_skill_marketplace().enable_skill(skill_name)


def disable_skill(skill_name: str) -> bool:
    """禁用技能"""
    return get_skill_marketplace().disable_skill(skill_name)


def configure_skill(skill_name: str, config: Dict) -> bool:
    """配置技能"""
    return get_skill_marketplace().configure_skill(skill_name, config)
