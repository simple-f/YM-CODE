# Skills module - 技能系统
from .base import BaseSkill
from .registry import SkillRegistry, get_registry
from .search import SearchSkill
from .http import HTTPSkill
from .shell import ShellSkill
from .code_analysis import CodeAnalysisSkill
from .memory import MemorySkill
from .self_improvement import SelfImprovementSkill
from .database import DatabaseSkill
from .formatter import FormatterSkill
from .docker import DockerSkill
from .chat import ChatSkill
from .llm import LLMSkill
from .skill_marketplace import SkillMarketplace, WebBrowserSkill
from .openclaw_bridge import OpenClawSkillBridge, OpenClawBridgeSkill, list_openclaw_skills, create_bridge

__all__ = [
    "BaseSkill",
    "SkillRegistry",
    "get_registry",
    "get_all_skills",
    # 核心技能
    "SearchSkill",
    "HTTPSkill",
    "ShellSkill",
    "CodeAnalysisSkill",
    "MemorySkill",
    "SelfImprovementSkill",
    "ChatSkill",
    "LLMSkill",
    # 开发工具
    "DatabaseSkill",
    "FormatterSkill",
    "DockerSkill",
    # 市场和浏览
    "SkillMarketplace",
    "WebBrowserSkill",
    # OpenClaw 桥接
    "OpenClawSkillBridge",
    "OpenClawBridgeSkill",
    "list_openclaw_skills",
    "create_bridge"
]


def get_all_skills() -> dict:
    """
    获取所有已注册的技能
    
    返回:
        技能字典 {skill_name: skill_instance}
    """
    from ..utils.logger import get_logger
    logger = get_logger(__name__)
    
    registry = get_registry()
    skills = {}
    
    # 实例化所有技能类
    for name, skill_class in registry.skill_classes.items():
        try:
            skill = skill_class()
            skills[skill.name] = skill
        except Exception as e:
            logger.warning(f"实例化技能失败 {name}: {e}")
    
    return skills
