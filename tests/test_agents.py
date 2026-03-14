#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 系统测试
"""

import pytest
import asyncio
from ymcode.agents import (
    BaseAgent,
    AgentMessage,
    AgentRouter,
    BuilderAgent,
    ReviewerAgent,
    create_default_router,
)
from ymcode.agents.memory_store import MemoryStore


class TestAgentMessage:
    """测试 AgentMessage"""
    
    def test_create_message(self):
        """创建消息"""
        msg = AgentMessage(
            sender="user",
            content="测试消息"
        )
        
        assert msg.sender == "user"
        assert msg.content == "测试消息"
        assert msg.timestamp is not None
    
    def test_message_to_dict(self):
        """消息转字典"""
        msg = AgentMessage(
            sender="user",
            content="测试",
            metadata={"key": "value"}
        )
        
        data = msg.to_dict()
        
        assert data["sender"] == "user"
        assert data["content"] == "测试"
        assert data["metadata"]["key"] == "value"
    
    def test_message_from_dict(self):
        """从字典创建消息"""
        data = {
            "sender": "user",
            "content": "测试",
            "timestamp": "2026-03-14T14:00:00",
            "metadata": {}
        }
        
        msg = AgentMessage.from_dict(data)
        
        assert msg.sender == "user"
        assert msg.content == "测试"


class TestBuilderAgent:
    """测试 Builder Agent"""
    
    @pytest.mark.asyncio
    async def test_builder_init(self):
        """初始化 Builder"""
        builder = BuilderAgent()
        
        assert builder.name == "builder"
        assert builder.role == "Builder"
        assert builder.state == "idle"
    
    @pytest.mark.asyncio
    async def test_builder_process(self):
        """处理任务"""
        builder = BuilderAgent()
        
        msg = AgentMessage(
            sender="user",
            content="创建文件 test.py"
        )
        
        response = await builder.process(msg)
        
        assert response.sender == "builder"
        assert "[OK]" in response.content or "任务已接收" in response.content
    
    @pytest.mark.asyncio
    async def test_builder_memory(self):
        """测试记忆"""
        builder = BuilderAgent()
        
        # 添加记忆
        builder.add_to_memory("任务 1")
        builder.add_to_memory("任务 2")
        
        memories = builder.get_memory()
        
        assert len(memories) == 2
    
    @pytest.mark.asyncio
    async def test_builder_status(self):
        """测试状态"""
        builder = BuilderAgent()
        
        status = builder.get_status()
        
        assert status["name"] == "builder"
        assert status["role"] == "Builder"
        assert status["state"] == "idle"


class TestReviewerAgent:
    """测试 Reviewer Agent"""
    
    @pytest.mark.asyncio
    async def test_reviewer_init(self):
        """初始化 Reviewer"""
        reviewer = ReviewerAgent()
        
        assert reviewer.name == "reviewer"
        assert reviewer.role == "Reviewer"
    
    @pytest.mark.asyncio
    async def test_reviewer_process(self):
        """处理审查任务"""
        reviewer = ReviewerAgent()
        
        msg = AgentMessage(
            sender="user",
            content="审查代码质量"
        )
        
        response = await reviewer.process(msg)
        
        assert response.sender == "reviewer"
        assert "报告" in response.content or "审查" in response.content


class TestAgentRouter:
    """测试 Agent Router"""
    
    def test_router_init(self):
        """初始化路由器"""
        router = AgentRouter()
        
        assert len(router.agents) == 0
    
    def test_register_agent(self):
        """注册 Agent"""
        router = AgentRouter()
        builder = BuilderAgent()
        
        router.register_agent("builder", builder)
        
        assert "builder" in router.agents
        assert router.get_agent("builder") == builder
    
    def test_list_agents(self):
        """列出 Agent"""
        router = AgentRouter()
        router.register_agent("builder", BuilderAgent())
        router.register_agent("reviewer", ReviewerAgent())
        
        agents = router.list_agents()
        
        assert len(agents) == 2
        assert any(a["name"] == "builder" for a in agents)
    
    @pytest.mark.asyncio
    async def test_route_to_target(self):
        """路由到指定 Agent"""
        router = AgentRouter()
        router.register_agent("builder", BuilderAgent())
        
        msg = AgentMessage(
            sender="user",
            content="创建文件"
        )
        
        response = await router.route(msg, target="builder")
        
        assert response.sender == "builder"
    
    @pytest.mark.asyncio
    async def test_auto_route(self):
        """自动路由"""
        router = create_default_router()
        
        # 构建类任务 → Builder
        msg = AgentMessage(sender="user", content="实现功能")
        response = await router.route(msg)
        assert response.sender == "builder"
        
        # 审查类任务 → Reviewer
        msg = AgentMessage(sender="user", content="审查代码")
        response = await router.route(msg)
        assert response.sender == "reviewer"
    
    def test_shared_memory(self):
        """测试共享记忆"""
        router = AgentRouter()
        
        # 添加记忆
        router.add_to_shared_memory({
            "type": "note",
            "content": "测试记忆"
        })
        
        memories = router.get_shared_memory()
        
        assert len(memories) == 1
        assert memories[0]["content"] == "测试记忆"
    
    def test_search_memory(self):
        """搜索记忆"""
        router = AgentRouter()
        
        router.add_to_shared_memory({"content": "Python 项目"})
        router.add_to_shared_memory({"content": "JavaScript 项目"})
        
        results = router.search_shared_memory("Python")
        
        assert len(results) == 1
        assert "Python" in results[0]["content"]
    
    def test_create_task(self):
        """创建任务"""
        router = AgentRouter()
        
        task = router.create_task(
            title="实现功能",
            assigned_to="builder"
        )
        
        assert task["id"] == 1
        assert task["title"] == "实现功能"
        assert task["status"] == "pending"


class TestMemoryStore:
    """测试 SQLite MemoryStore"""
    
    def test_store_init(self, tmp_path):
        """初始化存储"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        assert db_path.exists()
    
    def test_add_memory(self, tmp_path):
        """添加记忆"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        store.add_memory("builder", "测试记忆", "note")
        
        memories = store.get_memories()
        
        assert len(memories) == 1
        assert memories[0]["content"] == "测试记忆"
    
    def test_search_memory(self, tmp_path):
        """搜索记忆"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        store.add_memory("builder", "Python 项目", "note")
        store.add_memory("reviewer", "JavaScript 项目", "note")
        
        results = store.search_memories("Python")
        
        assert len(results) == 1
    
    def test_create_task(self, tmp_path):
        """创建任务"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        task_id = store.create_task(
            title="测试任务",
            assigned_to="builder"
        )
        
        assert task_id > 0
        
        tasks = store.get_tasks()
        
        assert len(tasks) == 1
        assert tasks[0]["title"] == "测试任务"
    
    def test_update_task(self, tmp_path):
        """更新任务"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        task_id = store.create_task("测试任务")
        store.update_task_status(task_id, "completed", "已完成")
        
        tasks = store.get_tasks(status="completed")
        
        assert len(tasks) == 1
        assert tasks[0]["result"] == "已完成"
    
    def test_agent_states(self, tmp_path):
        """测试 Agent 状态"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        store.save_agent_state("builder", "idle", 5, 10)
        
        states = store.get_agent_states()
        
        assert len(states) == 1
        assert states[0]["agent_name"] == "builder"
        assert states[0]["completed_tasks"] == 10
    
    def test_export_import(self, tmp_path):
        """测试导出导入"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        # 添加数据
        store.add_memory("builder", "测试", "note")
        store.create_task("测试任务")
        
        # 导出
        export_file = tmp_path / "export.json"
        store.export_data(str(export_file))
        
        assert export_file.exists()
        
        # 导入（清理现有数据）
        store.import_data(str(export_file), clear_existing=True)
        
        memories = store.get_memories()
        tasks = store.get_tasks()
        
        assert len(memories) == 1
        assert len(tasks) == 1
    
    def test_stats(self, tmp_path):
        """测试统计"""
        db_path = tmp_path / "test.db"
        store = MemoryStore(str(db_path))
        
        store.add_memory("builder", "记忆 1", "note")
        store.create_task("任务 1")
        store.save_agent_state("builder", "idle")
        
        stats = store.get_stats()
        
        assert stats["total_memories"] == 1
        assert "tasks" in stats
        assert stats["active_agents"] == 1
