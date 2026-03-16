#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队协作功能测试
"""

import pytest
from pathlib import Path
from ymcode.team import (
    Role,
    Permission,
    TeamMember,
    TeamManager,
    TaskManager,
)


class TestPermissions:
    """测试权限管理"""
    
    def test_role_permissions(self):
        """测试角色权限"""
        from ymcode.team.permissions import ROLE_PERMISSIONS
        
        # Admin 应该有所有权限
        admin_perms = {p.value for p in ROLE_PERMISSIONS[Role.ADMIN]}
        assert "read" in admin_perms
        assert "write" in admin_perms
        assert "admin" in admin_perms
        
        # Developer 应该有写权限
        dev_perms = {p.value for p in ROLE_PERMISSIONS[Role.DEVELOPER]}
        assert "read" in dev_perms
        assert "write" in dev_perms
        assert "admin" not in dev_perms
        
        # Viewer 只应该有读权限
        viewer_perms = {p.value for p in ROLE_PERMISSIONS[Role.VIEWER]}
        assert "read" in viewer_perms
        assert "write" not in viewer_perms
    
    def test_team_member(self):
        """测试团队成员"""
        member = TeamMember("user1", "Alice", Role.DEVELOPER)
        
        assert member.user_id == "user1"
        assert member.name == "Alice"
        assert member.role == Role.DEVELOPER
        assert member.has_permission(Permission.READ)
        assert member.has_permission(Permission.WRITE)
        assert not member.has_permission(Permission.ADMIN)
    
    def test_upgrade_role(self):
        """测试角色升级"""
        member = TeamMember("user1", "Alice", Role.VIEWER)
        
        # 初始只有读权限
        assert member.has_permission(Permission.READ)
        assert not member.has_permission(Permission.WRITE)
        
        # 升级后应该有写权限
        member.upgrade_role(Role.DEVELOPER)
        assert member.has_permission(Permission.WRITE)


class TestTeamManager:
    """测试团队管理器"""
    
    def test_create_team(self, tmp_path):
        """创建团队"""
        config_path = tmp_path / "team.json"
        team_mgr = TeamManager("test-team", str(config_path))
        
        assert team_mgr.team_name == "test-team"
        # 配置文件在保存时才会创建
        team_mgr._save_config()
        assert config_path.exists()
    
    def test_add_member(self, tmp_path):
        """添加成员"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        
        member = team_mgr.add_member("user1", "Alice", Role.DEVELOPER)
        
        assert member.user_id == "user1"
        assert member.name == "Alice"
        assert len(team_mgr.list_members()) == 1
    
    def test_remove_member(self, tmp_path):
        """移除成员"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        
        team_mgr.add_member("user1", "Alice")
        team_mgr.add_member("user2", "Bob")
        
        assert team_mgr.remove_member("user1")
        assert len(team_mgr.list_members()) == 1
    
    def test_list_members_by_role(self, tmp_path):
        """按角色列出成员"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        
        team_mgr.add_member("user1", "Alice", Role.ADMIN)
        team_mgr.add_member("user2", "Bob", Role.DEVELOPER)
        team_mgr.add_member("user3", "Charlie", Role.DEVELOPER)
        
        developers = team_mgr.list_members(Role.DEVELOPER)
        assert len(developers) == 2
    
    def test_check_permission(self, tmp_path):
        """检查权限"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        
        team_mgr.add_member("user1", "Alice", Role.VIEWER)
        
        assert team_mgr.check_permission("user1", Permission.READ)
        assert not team_mgr.check_permission("user1", Permission.WRITE)
    
    def test_team_stats(self, tmp_path):
        """测试团队统计"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        
        team_mgr.add_member("user1", "Alice", Role.ADMIN)
        team_mgr.add_member("user2", "Bob", Role.DEVELOPER)
        team_mgr.add_member("user3", "Charlie", Role.DEVELOPER)
        
        stats = team_mgr.get_team_stats()
        
        assert stats["total_members"] == 3
        assert stats["roles"]["admin"] == 1
        assert stats["roles"]["developer"] == 2


class TestTaskManager:
    """测试任务管理器"""
    
    def test_create_task(self, tmp_path):
        """创建任务"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task = task_mgr.create_task(
            title="测试任务",
            description="这是一个测试",
            priority="high"
        )
        
        assert task.id == 1
        assert task.title == "测试任务"
        assert task.priority == "high"
        assert task.status == "pending"
    
    def test_assign_task(self, tmp_path):
        """分配任务"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task = task_mgr.create_task("测试任务")
        task_mgr.assign_task(task.id, "user1")
        
        updated_task = task_mgr.get_task(task.id)
        assert updated_task.assigned_to == "user1"
    
    def test_complete_task(self, tmp_path):
        """完成任务"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task = task_mgr.create_task("测试任务")
        task_mgr.complete_task(task.id, "user1", "完成得很好")
        
        updated_task = task_mgr.get_task(task.id)
        assert updated_task.status == "completed"
        assert updated_task.completed_by == "user1"
        assert updated_task.metadata["result"] == "完成得很好"
    
    def test_list_tasks(self, tmp_path):
        """列出任务"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task_mgr.create_task("任务 1", priority="low")
        task_mgr.create_task("任务 2", priority="normal")
        task_mgr.create_task("任务 3", priority="high")
        
        all_tasks = task_mgr.list_tasks()
        assert len(all_tasks) == 3
        
        # 过滤高优先级任务
        all_tasks_list = task_mgr.list_tasks()
        high_priority_tasks = [t for t in all_tasks_list if t.priority == "high"]
        assert len(high_priority_tasks) == 1
    
    def test_add_comment(self, tmp_path):
        """添加评论"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task = task_mgr.create_task("测试任务")
        comment = task_mgr.add_comment(
            task.id,
            "user1",
            "Alice",
            "这个任务很重要"
        )
        
        assert comment.id == 1
        assert comment.content == "这个任务很重要"
        
        # 验证评论已保存
        task = task_mgr.get_task(task.id)
        assert len(task.comments) == 1
    
    def test_search_tasks(self, tmp_path):
        """搜索任务"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task_mgr.create_task("实现用户认证", tags=["backend", "security"])
        task_mgr.create_task("设计首页", tags=["frontend", "design"])
        
        # 按标题搜索
        results = task_mgr.search_tasks("认证")
        assert len(results) == 1
        
        # 按标签搜索
        results = task_mgr.search_tasks("frontend")
        assert len(results) == 1
    
    def test_task_stats(self, tmp_path):
        """测试任务统计"""
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        task_mgr.create_task("任务 1", priority="low")
        task_mgr.create_task("任务 2", priority="high")
        task_mgr.create_task("任务 3", priority="normal")
        
        stats = task_mgr.get_task_stats()
        
        assert stats["total"] == 3
        assert stats["by_status"]["pending"] == 3
        assert stats["by_priority"]["high"] == 1


class TestIntegration:
    """集成测试"""
    
    def test_team_workflow(self, tmp_path):
        """测试团队工作流"""
        team_mgr = TeamManager("test-team", str(tmp_path / "team.json"))
        task_mgr = TaskManager(str(tmp_path / "tasks.json"))
        
        # 1. 添加团队成员
        team_mgr.add_member("dev1", "开发者 1", Role.DEVELOPER)
        team_mgr.add_member("dev2", "开发者 2", Role.DEVELOPER)
        
        # 2. 创建任务并分配
        task = task_mgr.create_task(
            "实现功能",
            assigned_to="dev1"
        )
        
        # 3. 添加评论
        task_mgr.add_comment(
            task.id,
            "dev1",
            "开发者 1",
            "开始开发"
        )
        
        # 4. 完成任务
        task_mgr.complete_task(task.id, "dev1", "功能已完成")
        
        # 5. 验证
        tasks = task_mgr.list_tasks(status="completed")
        assert len(tasks) == 1
        
        task = task_mgr.get_task(task.id)
        assert len(task.comments) == 1
