#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 注册表 - 技能管理和发现
"""

import importlib
import logging
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self):
        """初始化注册表"""
        self.skills: Dict[str, BaseSkill] = {}
        self.skill_classes: Dict[str, Type[BaseSkill]] = {}
        self._builtin_skills = self._discover_builtin_skills()
        
        logger.info(f"技能注册表初始化完成，发现 {len(self._builtin_skills)} 个内置技能")
    
    def _discover_builtin_skills(self) -> Dict[str, Type[BaseSkill]]:
        """发现内置技能"""
        builtin_skills = {}
        
        # 内置技能模块 - 包含所有技能
        skill_modules = [
            'ymcode.skills.memory',
            'ymcode.skills.self_improvement',
            'ymcode.skills.search',
            'ymcode.skills.http',
            'ymcode.skills.shell',
            'ymcode.skills.code_analysis',
            'ymcode.skills.database',
            'ymcode.skills.formatter',
            'ymcode.skills.docker',
            'ymcode.skills.chat',
            'ymcode.skills.llm',
        ]
        
        for module_path in skill_modules:
            try:
                module = importlib.import_module(module_path)
                
                # 查找技能类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseSkill) and 
                        attr is not BaseSkill):
                        # 尝试实例化获取真实的 name
                        try:
                            instance = attr()
                            skill_name = instance.name.lower()
                        except:
                            # 如果实例化失败，使用类名
                            skill_name = attr.__name__.lower()
                        builtin_skills[skill_name] = attr
                        logger.debug(f"发现技能：{skill_name}")
            except Exception as e:
                logger.warning(f"加载技能模块失败 {module_path}: {e}")
        
        logger.info(f"共发现 {len(builtin_skills)} 个内置技能")
        
        # 注册到 skill_classes
        for name, skill_class in builtin_skills.items():
            self.skill_classes[name] = skill_class
        
        return builtin_skills
    
    def register(self, skill: BaseSkill) -> bool:
        """
        注册技能实例
        
        参数:
            skill: 技能实例
        
        返回:
            是否成功
        """
        if skill.name in self.skills:
            logger.warning(f"技能已存在：{skill.name}")
            return False
        
        self.skills[skill.name] = skill
        logger.info(f"注册技能：{skill.name}")
        return True
    
    def register_class(self, skill_class: Type[BaseSkill]) -> bool:
        """
        注册技能类
        
        参数:
            skill_class: 技能类
        
        返回:
            是否成功
        """
        skill_name = skill_class.__name__.lower()
        if skill_name in self.skill_classes:
            logger.warning(f"技能类已存在：{skill_name}")
            return False
        
        self.skill_classes[skill_name] = skill_class
        logger.info(f"注册技能类：{skill_name}")
        return True
    
    def get(self, name: str) -> Optional[BaseSkill]:
        """
        获取技能实例
        
        参数:
            name: 技能名称
        
        返回:
            技能实例
        """
        if name in self.skills:
            return self.skills[name]
        
        # 自动实例化
        if name in self.skill_classes:
            skill_class = self.skill_classes[name]
            skill = skill_class()
            self.register(skill)
            return skill
        
        return None
    
    def list_skills(self) -> List[Dict]:
        """
        列出所有技能
        
        返回:
            技能信息列表
        """
        result = []
        
        # 已实例化的技能
        for skill in self.skills.values():
            result.append({
                'name': skill.name,
                'description': skill.description,
                'enabled': skill.enabled,
                'metadata': skill.metadata
            })
        
        # 未实例化的类
        for name, skill_class in self.skill_classes.items():
            if name not in self.skills:
                try:
                    instance = skill_class()
                    result.append({
                        'name': name,
                        'description': instance.description,
                        'enabled': True,
                        'metadata': instance.metadata
                    })
                except Exception as e:
                    logger.warning(f"实例化技能失败 {name}: {e}")
        
        return result
    
    def get_tools_definition(self) -> List[Dict]:
        """
        获取 MCP 工具定义
        
        返回:
            工具定义列表
        """
        tools = []
        
        for skill_info in self.list_skills():
            tools.append({
                'type': 'function',
                'function': {
                    'name': f"skill_{skill_info['name']}",
                    'description': skill_info['description'],
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                }
            })
        
        return tools
    
    async def execute_skill(self, name: str, arguments: Dict) -> Any:
        """
        执行技能
        
        参数:
            name: 技能名称
            arguments: 输入参数
        
        返回:
            执行结果
        """
        skill = self.get(name)
        
        if not skill:
            raise ValueError(f"技能不存在：{name}")
        
        if not skill.enabled:
            raise ValueError(f"技能已禁用：{name}")
        
        logger.info(f"执行技能：{name}")
        
        return await skill.execute(arguments)
    
    def load_from_directory(self, directory: Path) -> int:
        """
        从目录加载技能
        
        参数:
            directory: 技能目录
        
        返回:
            加载的技能数量
        """
        count = 0
        
        if not directory.exists():
            logger.warning(f"目录不存在：{directory}")
            return 0
        
        for file in directory.glob('*.py'):
            if file.name.startswith('_'):
                continue
            
            try:
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(
                    f"skills.{file.stem}",
                    file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找技能类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseSkill) and 
                        attr is not BaseSkill):
                        self.register_class(attr)
                        count += 1
                        logger.info(f"加载技能：{attr.__name__}")
            except Exception as e:
                logger.error(f"加载技能文件失败 {file}: {e}")
        
        return count
    
    def get_status(self) -> Dict:
        """
        获取注册表状态
        
        返回:
            状态字典
        """
        return {
            'total_skills': len(self.skills) + len(self.skill_classes),
            'instantiated': len(self.skills),
            'classes': len(self.skill_classes),
            'builtin': len(self._builtin_skills),
            'skills': list(self.skills.keys()),
            'classes': list(self.skill_classes.keys())
        }


# 全局注册表实例
_registry: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """获取全局注册表实例"""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def reset_registry() -> None:
    """重置注册表（用于测试）"""
    global _registry
    _registry = None
