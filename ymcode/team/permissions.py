#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队权限管理
"""

import logging
import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Role(Enum):
    """角色枚举"""
    ADMIN = "admin"           # 管理员：所有权限
    DEVELOPER = "developer"   # 开发者：读写执行
    VIEWER = "viewer"         # 观察者：只读
    GUEST = "guest"           # 访客：有限访问


class Permission(Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_TASKS = "manage_tasks"
    VIEW_AUDIT = "view_audit"


# 角色权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.READ,
        Permission.WRITE,
        Permission.EXECUTE,
        Permission.ADMIN,
        Permission.MANAGE_USERS,
        Permission.MANAGE_TASKS,
        Permission.VIEW_AUDIT,
    },
    Role.DEVELOPER: {
        Permission.READ,
        Permission.WRITE,
        Permission.EXECUTE,
        Permission.MANAGE_TASKS,
    },
    Role.VIEWER: {
        Permission.READ,
    },
    Role.GUEST: {
        Permission.READ,
    },
}


class TeamMember:
    """团队成员"""
    
    def __init__(self, user_id: str, name: str, role: Role = Role.DEVELOPER):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.joined_at = datetime.now().isoformat()
        self.last_active = None
        self.permissions = ROLE_PERMISSIONS.get(role, set())
        self.metadata: Dict = {}
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有权限"""
        return permission in self.permissions
    
    def upgrade_role(self, new_role: Role):
        """升级角色"""
        self.role = new_role
        self.permissions = ROLE_PERMISSIONS.get(new_role, set())
        logger.info(f"用户 {self.name} 角色升级为 {new_role.value}")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "joined_at": self.joined_at,
            "last_active": self.last_active,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TeamMember':
        """从字典创建"""
        member = cls(
            user_id=data["user_id"],
            name=data["name"],
            role=Role(data.get("role", "developer"))
        )
        member.joined_at = data.get("joined_at", member.joined_at)
        member.last_active = data.get("last_active")
        member.metadata = data.get("metadata", {})
        return member


class TeamManager:
    """团队管理器"""
    
    def __init__(self, team_name: str, config_path: str = None):
        self.team_name = team_name
        self.created_at = datetime.now().isoformat()
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".ymcode" / "team" / f"{team_name}.json"
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 成员管理
        self.members: Dict[str, TeamMember] = {}
        
        # 加载配置
        self._load_config()
        
        logger.info(f"团队 {team_name} 初始化完成")
    
    def add_member(self, user_id: str, name: str, role: Role = Role.DEVELOPER) -> TeamMember:
        """添加成员"""
        if user_id in self.members:
            logger.warning(f"用户已存在：{user_id}")
            return self.members[user_id]
        
        member = TeamMember(user_id, name, role)
        self.members[user_id] = member
        
        logger.info(f"添加成员：{name} ({role.value})")
        self._save_config()
        
        return member
    
    def remove_member(self, user_id: str) -> bool:
        """移除成员"""
        if user_id not in self.members:
            return False
        
        member = self.members.pop(user_id)
        logger.info(f"移除成员：{member.name}")
        self._save_config()
        
        return True
    
    def get_member(self, user_id: str) -> Optional[TeamMember]:
        """获取成员"""
        return self.members.get(user_id)
    
    def list_members(self, role: Role = None) -> List[TeamMember]:
        """列出成员"""
        if role:
            return [m for m in self.members.values() if m.role == role]
        return list(self.members.values())
    
    def update_role(self, user_id: str, new_role: Role) -> bool:
        """更新角色"""
        member = self.get_member(user_id)
        if not member:
            return False
        
        member.upgrade_role(new_role)
        self._save_config()
        return True
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """检查权限"""
        member = self.get_member(user_id)
        if not member:
            return False
        
        # 更新活跃时间
        member.last_active = datetime.now().isoformat()
        
        return member.has_permission(permission)
    
    def get_team_stats(self) -> Dict:
        """获取团队统计"""
        roles_count = {}
        for member in self.members.values():
            role = member.role.value
            roles_count[role] = roles_count.get(role, 0) + 1
        
        return {
            "team_name": self.team_name,
            "total_members": len(self.members),
            "roles": roles_count,
            "created_at": self.created_at,
        }
    
    def _load_config(self):
        """加载配置"""
        if not self.config_path.exists():
            logger.info("创建新团队配置")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for member_data in data.get("members", []):
                member = TeamMember.from_dict(member_data)
                self.members[member.user_id] = member
            
            logger.info(f"加载 {len(self.members)} 个成员")
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
    
    def _save_config(self):
        """保存配置"""
        data = {
            "team_name": self.team_name,
            "created_at": self.created_at,
            "members": [m.to_dict() for m in self.members.values()],
            "updated_at": datetime.now().isoformat(),
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug("配置已保存")
    
    def export_config(self, output_path: str):
        """导出配置"""
        self._save_config()
        
        # 复制到指定路径
        import shutil
        shutil.copy2(self.config_path, output_path)
        logger.info(f"配置已导出到：{output_path}")
    
    def import_config(self, input_path: str, merge: bool = False):
        """导入配置"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not merge:
            self.members.clear()
        
        for member_data in data.get("members", []):
            member = TeamMember.from_dict(member_data)
            self.members[member.user_id] = member
        
        self._save_config()
        logger.info(f"导入 {len(self.members)} 个成员")


class AccessControl:
    """访问控制"""
    
    def __init__(self, team_manager: TeamManager):
        self.team_manager = team_manager
    
    def can_read(self, user_id: str) -> bool:
        """检查读权限"""
        return self.team_manager.check_permission(user_id, Permission.READ)
    
    def can_write(self, user_id: str) -> bool:
        """检查写权限"""
        return self.team_manager.check_permission(user_id, Permission.WRITE)
    
    def can_execute(self, user_id: str) -> bool:
        """检查执行权限"""
        return self.team_manager.check_permission(user_id, Permission.EXECUTE)
    
    def can_admin(self, user_id: str) -> bool:
        """检查管理权限"""
        return self.team_manager.check_permission(user_id, Permission.ADMIN)
    
    def can_manage_tasks(self, user_id: str) -> bool:
        """检查任务管理权限"""
        return self.team_manager.check_permission(user_id, Permission.MANAGE_TASKS)
    
    def can_view_audit(self, user_id: str) -> bool:
        """检查审计查看权限"""
        return self.team_manager.check_permission(user_id, Permission.VIEW_AUDIT)
