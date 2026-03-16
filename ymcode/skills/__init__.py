# Comment
from .base import BaseSkill
from .registry import SkillRegistry, get_registry
from .search import SearchSkill
from .http import HTTPSkill
from .shell import ShellSkill
from .code_analysis import CodeAnalysisSkill
from .code_analyzer import CodeAnalyzerSkill
from .git_integration import GitIntegrationSkill
from .batch_project import BatchProjectSkill
from .multi_language import MultiLanguageSkill
from .code_runner import CodeRunnerSkill
from .memory import MemorySkill
from .self_improvement import SelfImprovementSkill
from .database import DatabaseSkill
from .formatter import FormatterSkill
from .docker import DockerSkill
from .chat import ChatSkill
from .llm import LLMSkill
from .skill_marketplace import SkillMarketplace
from .openclaw_bridge import OpenClawSkillBridge, OpenClawBridgeSkill, list_openclaw_skills, create_bridge

__all__ = [
    "BaseSkill",
    "SkillRegistry",
    "get_registry",
    "get_all_skills",
    # Comment
    "SearchSkill",
    "HTTPSkill",
    "ShellSkill",
    "CodeAnalysisSkill",
    "CodeAnalyzerSkill",
    "GitIntegrationSkill",
    "BatchProjectSkill",
    "MultiLanguageSkill",
    "CodeRunnerSkill",
    "MemorySkill",
    "SelfImprovementSkill",
    "ChatSkill",
    "LLMSkill",
    # Comment
    "DatabaseSkill",
    "FormatterSkill",
    "DockerSkill",
    # Comment
    "SkillMarketplace",
    # Comment
    "OpenClawSkillBridge",
    "OpenClawBridgeSkill",
    "list_openclaw_skills",
    "create_bridge"
]


def get_all_skills() -> dict:
    """
    鑾峰彇鎵€鏈夊凡娉ㄥ唽鐨勬妧鑳?
    
    杩斿洖:
        鎶€鑳藉瓧鍏?{skill_name: skill_instance}
    """
    from ..utils.logger import get_logger
    logger = get_logger(__name__)
    
    registry = get_registry()
    skills = {}
    
    # Comment
    for name, skill_class in registry.skill_classes.items():
        try:
            skill = skill_class()
            skills[skill.name] = skill
        except Exception as e:
            logger.warning(f"瀹炰緥鍖栨妧鑳藉け璐?{name}: {e}")
    
    return skills
