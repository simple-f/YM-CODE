#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 身份系统 - 定制化 Agent 人格

支持创建多个不同性格的 Agent
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentIdentity:
    """Agent 身份配置"""
    
    # 基础信息
    name: str = "YM-Assistant"
    codename: str = "Aurora"
    version: str = "0.1.0"
    
    # 人格设定
    personality: str = "friendly"  # friendly, professional, humorous, strict
    tone: str = "warm"  # warm, formal, casual, witty
    
    # 沟通风格
    communication_style: Dict[str, Any] = field(default_factory=lambda: {
        'verbosity': 'medium',  # brief, medium, detailed
        'emoji_usage': 'moderate',  # none, moderate, frequent
        'humor_level': 'light',  # none, light, moderate, heavy
        'formality': 'casual'  # formal, casual, friendly
    })
    
    # 专业领域
    expertise: List[str] = field(default_factory=lambda: [
        'python',
        'code-review',
        'debugging'
    ])
    
    # 行为约束
    constraints: List[str] = field(default_factory=lambda: [
        'always_ask_before_destructive_actions',
        'explain_reasoning',
        'admit_uncertainty'
    ])
    
    # 经典语录模板
    quotes: List[str] = field(default_factory=list)
    
    # 创建时间
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 头像/标识
    avatar_emoji: str = "🔮"
    avatar_color: str = "#8B5CF6"  # 极光紫
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_yaml(self) -> str:
        """转换为 YAML 字符串"""
        return yaml.dump(self.to_dict(), allow_unicode=True, default_flow_style=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentIdentity':
        """从字典创建"""
        return cls(**data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'AgentIdentity':
        """从 YAML 字符串创建"""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'AgentIdentity':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return cls.from_yaml(f.read())
            else:
                data = json.load(f)
                return cls.from_dict(data)
    
    def save(self, file_path: Path) -> None:
        """保存到文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                f.write(self.to_yaml())
            else:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# 预设人格模板
PERSONALITY_TEMPLATES = {
    'friendly': AgentIdentity(
        name="YM-Friend",
        codename="Buddy",
        personality="friendly",
        tone="warm",
        communication_style={
            'verbosity': 'medium',
            'emoji_usage': 'moderate',
            'humor_level': 'light',
            'formality': 'friendly'
        },
        avatar_emoji="🤝",
        avatar_color="#10B981",
        quotes=[
            "别担心，我来帮你搞定！",
            "这个功能很有意思，一起看看吧！",
            "有问题随时问我~"
        ]
    ),
    
    'professional': AgentIdentity(
        name="YM-Pro",
        codename="Expert",
        personality="professional",
        tone="formal",
        communication_style={
            'verbosity': 'detailed',
            'emoji_usage': 'none',
            'humor_level': 'none',
            'formality': 'formal'
        },
        avatar_emoji="💼",
        avatar_color="#3B82F6",
        quotes=[
            "根据最佳实践，建议...",
            "从专业角度分析...",
            "这个方案的优势在于..."
        ]
    ),
    
    'humorous': AgentIdentity(
        name="YM-Joker",
        codename="Comedy",
        personality="humorous",
        tone="witty",
        communication_style={
            'verbosity': 'brief',
            'emoji_usage': 'frequent',
            'humor_level': 'moderate',
            'formality': 'casual'
        },
        avatar_emoji="🎭",
        avatar_color="#F59E0B",
        quotes=[
            "这个 bug 比我家的猫还难捉摸！",
            "代码写得不错，我给 101 分（多 1 分怕你骄傲）",
            "调试成功！今晚可以加鸡腿了🍗"
        ]
    ),
    
    'strict': AgentIdentity(
        name="YM-Mentor",
        codename="Sensei",
        personality="strict",
        tone="formal",
        communication_style={
            'verbosity': 'detailed',
            'emoji_usage': 'none',
            'humor_level': 'none',
            'formality': 'formal'
        },
        avatar_emoji="🦉",
        avatar_color="#6366F1",
        quotes=[
            "代码可以更好，再想想。",
            "这个错误不应该犯。",
            "优秀的代码需要反复打磨。"
        ]
    ),
    
    'creative': AgentIdentity(
        name="YM-Creator",
        codename="Artist",
        personality="creative",
        tone="warm",
        communication_style={
            'verbosity': 'medium',
            'emoji_usage': 'moderate',
            'humor_level': 'light',
            'formality': 'casual'
        },
        avatar_emoji="🎨",
        avatar_color="#EC4899",
        quotes=[
            "代码也是艺术！",
            "让我们一起创造美。",
            "这个设计很有创意！"
        ]
    ),
}


class IdentityManager:
    """身份管理器"""
    
    def __init__(self, identities_dir: str = None):
        """
        初始化身份管理器
        
        参数:
            identities_dir: 身份文件目录
        """
        self.identities_dir = Path(identities_dir) if identities_dir else Path.home() / '.ym-code' / 'identities'
        self.identities: Dict[str, AgentIdentity] = {}
        self.current_identity: Optional[str] = None
        
        # 确保目录存在
        self.identities_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载已有身份
        self._load_identities()
        
        logger.info(f"身份管理器初始化完成（目录：{self.identities_dir}）")
    
    def _load_identities(self) -> None:
        """加载身份文件"""
        if not self.identities_dir.exists():
            return
        
        for file_path in self.identities_dir.glob('*.yaml'):
            try:
                identity = AgentIdentity.from_file(file_path)
                self.identities[identity.name] = identity
                logger.debug(f"加载身份：{identity.name}")
            except Exception as e:
                logger.warning(f"加载身份文件失败 {file_path}: {e}")
        
        logger.info(f"共加载 {len(self.identities)} 个身份")
    
    def create_identity(self, name: str, template: str = None, **kwargs) -> AgentIdentity:
        """
        创建新身份
        
        参数:
            name: 身份名称
            template: 预设模板名称
            **kwargs: 自定义参数
        
        返回:
            创建的身份
        """
        if template and template in PERSONALITY_TEMPLATES:
            # 基于模板创建
            identity = PERSONALITY_TEMPLATES[template]
            identity.name = name
            identity.codename = name.replace(' ', '-').lower()
        else:
            # 从头创建
            identity = AgentIdentity(name=name, **kwargs)
        
        # 应用自定义参数
        for key, value in kwargs.items():
            if hasattr(identity, key):
                setattr(identity, key, value)
        
        # 保存
        self.identities[name] = identity
        self._save_identity(identity)
        
        logger.info(f"创建新身份：{name}")
        
        return identity
    
    def _save_identity(self, identity: AgentIdentity) -> None:
        """保存身份"""
        file_path = self.identities_dir / f"{identity.codename}.yaml"
        identity.save(file_path)
    
    def get_identity(self, name: str) -> Optional[AgentIdentity]:
        """获取身份"""
        return self.identities.get(name)
    
    def list_identities(self) -> List[Dict[str, Any]]:
        """列出所有身份"""
        return [
            {
                'name': i.name,
                'codename': i.codename,
                'personality': i.personality,
                'avatar_emoji': i.avatar_emoji,
                'avatar_color': i.avatar_color,
                'expertise': i.expertise
            }
            for i in self.identities.values()
        ]
    
    def set_current(self, name: str) -> bool:
        """设置当前身份"""
        if name not in self.identities:
            logger.warning(f"身份不存在：{name}")
            return False
        
        self.current_identity = name
        logger.info(f"切换到身份：{name}")
        return True
    
    def get_current(self) -> Optional[AgentIdentity]:
        """获取当前身份"""
        if not self.current_identity:
            return None
        
        return self.identities.get(self.current_identity)
    
    def delete_identity(self, name: str) -> bool:
        """删除身份"""
        if name not in self.identities:
            return False
        
        identity = self.identities[name]
        file_path = self.identities_dir / f"{identity.codename}.yaml"
        
        if file_path.exists():
            file_path.unlink()
        
        del self.identities[name]
        
        if self.current_identity == name:
            self.current_identity = None
        
        logger.info(f"删除身份：{name}")
        return True
    
    def list_templates(self) -> List[str]:
        """列出可用模板"""
        return list(PERSONALITY_TEMPLATES.keys())
    
    def get_template(self, name: str) -> Optional[AgentIdentity]:
        """获取模板"""
        return PERSONALITY_TEMPLATES.get(name)


# 全局身份管理器
_manager: Optional[IdentityManager] = None


def get_identity_manager() -> IdentityManager:
    """获取全局身份管理器"""
    global _manager
    if _manager is None:
        _manager = IdentityManager()
    return _manager


def create_agent(name: str, template: str = None, **kwargs) -> AgentIdentity:
    """便捷函数：创建 Agent"""
    return get_identity_manager().create_identity(name, template, **kwargs)


def switch_agent(name: str) -> bool:
    """便捷函数：切换 Agent"""
    return get_identity_manager().set_current(name)


def get_current_agent() -> Optional[AgentIdentity]:
    """便捷函数：获取当前 Agent"""
    return get_identity_manager().get_current()
