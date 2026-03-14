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
from .openclaw_bridge import OpenClawSkillBridge, OpenClawBridgeSkill, list_openclaw_skills, create_bridge

__all__ = [
    "BaseSkill",
    "SkillRegistry",
    "get_registry",
    # 核心技能
    "SearchSkill",
    "HTTPSkill",
    "ShellSkill",
    "CodeAnalysisSkill",
    "MemorySkill",
    "SelfImprovementSkill",
    # 开发工具
    "DatabaseSkill",
    "FormatterSkill",
    "DockerSkill",
    # OpenClaw 桥接
    "OpenClawSkillBridge",
    "OpenClawBridgeSkill",
    "list_openclaw_skills",
    "create_bridge"
]
