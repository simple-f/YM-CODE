#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎单元测试
"""

import pytest
import asyncio
import time
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.workflow.state_tracker import StateTracker, TaskState, get_state_tracker, reset_state_tracker
from ymcode.workflow.cascade_cancel import CascadeCanceller, get_cascade_canceller
from ymcode.workflow.scheduler import TaskScheduler, SchedulingPolicy
from ymcode.workflow.a2a_coordinator import A2ACoordinator, AssignmentStrategy, AgentInfo


class TestStateTracker:
    """StateTracker 测试"""
    
    @pytest.fixture
    def tracker(self):
        """创建测试用 tracker"""
        reset_state_tracker()
        tracker = StateTracker(storage_path=Path(__file__).parent / "test_state.json")
        yield tracker
        # 清理
        if tracker.storage_path.exists():
            tracker.storage_path.unlink()
    
    def test_record_state(self, tracker):
        """测试状态记录"""
        result = tracker.record_state("task-1", TaskState.PENDING)
        assert result is True
        
        state = tracker.get_current_state("task-1")
        assert state == TaskState.PENDING
    
    def test_state_history(self, tracker):
        """测试状态历史"""
        tracker.record_state("task-1", TaskState.PENDING)
        tracker.record_state("task-1", TaskState.RUNNING)
        tracker.record_state("task-1", TaskState.COMPLETED)
        
        history = tracker.get_history("task-1")
        assert len(history) == 3
        assert history[0].to_state == TaskState.PENDING.value
        assert history[2].to_state == TaskState.COMPLETED.value
    
    def test_valid_transition(self, tracker):
        """测试有效状态转换"""
        assert tracker.is_valid_transition(TaskState.PENDING, TaskState.RUNNING) is False
        assert tracker.is_valid_transition(TaskState.PENDING, TaskState.SCHEDULED) is True
        assert tracker.is_valid_transition(TaskState.RUNNING, TaskState.COMPLETED) is True
    
    def test_invalid_transition(self, tracker):
        """测试无效状态转换"""
        # PENDING 不能直接到 COMPLETED
        assert tracker.is_valid_transition(TaskState.PENDING, TaskState.COMPLETED) is False
        
        # COMPLETED 是终态
        assert tracker.is_valid_transition(TaskState.COMPLETED, TaskState.RUNNING) is False
    
    def test_get_tasks_by_state(self, tracker):
        """测试按状态查询任务"""
        tracker.record_state("task-1", TaskState.PENDING)
        tracker.record_state("task-2", TaskState.PENDING)
        tracker.record_state("task-3", TaskState.RUNNING)
        
        pending = tracker.get_tasks_by_state(TaskState.PENDING)
        assert len(pending) == 2
        assert "task-1" in pending
        assert "task-2" in pending
    
    def test_stats(self, tracker):
        """测试统计信息"""
        tracker.record_state("task-1", TaskState.PENDING)
        tracker.record_state("task-2", TaskState.RUNNING)
        tracker.record_state("task-3", TaskState.COMPLETED)
        
        stats = tracker.get_stats()
        assert stats["total_tasks"] == 3
        assert stats["state_distribution"]["PENDING"] == 1
        assert stats["state_distribution"]["RUNNING"] == 1
        assert stats["state_distribution"]["COMPLETED"] == 1


class TestCascadeCanceller:
    """CascadeCanceller 测试"""
    
    @pytest.fixture
    def canceller(self):
        """创建测试用 canceller"""
        return CascadeCanceller()
    
    def test_register_parent_child(self, canceller):
        """测试注册父子关系"""
        canceller.register_parent_child("parent-1", "child-1")
        canceller.register_parent_child("parent-1", "child-2")
        
        children = canceller.get_children("parent-1")
        assert len(children) == 2
        assert "child-1" in children
        assert "child-2" in children
    
    def test_recursive_children(self, canceller):
        """测试递归获取子任务"""
        canceller.register_parent_child("parent-1", "child-1")
        canceller.register_parent_child("child-1", "grandchild-1")
        canceller.register_parent_child("child-1", "grandchild-2")
        
        children = canceller.get_children("parent-1", recursive=True)
        assert len(children) == 3
        assert "child-1" in children
        assert "grandchild-1" in children
        assert "grandchild-2" in children
    
    def test_get_parent(self, canceller):
        """测试获取父任务"""
        canceller.register_parent_child("parent-1", "child-1")
        
        parent = canceller.get_parent("child-1")
        assert parent == "parent-1"
    
    @pytest.mark.asyncio
    async def test_cancel_with_children(self, canceller):
        """测试级联取消"""
        # 注册关系
        canceller.register_parent_child("parent-1", "child-1")
        canceller.register_parent_child("parent-1", "child-2")
        
        # 模拟取消（没有实际任务队列）
        results = await canceller.cancel_with_children("parent-1", reason="测试取消")
        
        # 应该返回所有任务的结果
        assert "parent-1" in results
        assert "child-1" in results
        assert "child-2" in results
    
    def test_relation_stats(self, canceller):
        """测试关系统计"""
        canceller.register_parent_child("parent-1", "child-1")
        canceller.register_parent_child("parent-2", "child-2")
        
        stats = canceller.get_relation_stats()
        assert stats["total_relations"] == 4
        assert stats["parent_tasks"] == 2
        assert stats["child_tasks"] == 2


class TestTaskScheduler:
    """TaskScheduler 测试"""
    
    @pytest.fixture
    def scheduler(self):
        """创建测试用 scheduler"""
        return TaskScheduler(max_concurrent=5, policy=SchedulingPolicy.PRIORITY)
    
    def test_priority_selection(self, scheduler):
        """测试优先级选择"""
        from ymcode.queue import Task, TaskPriority
        
        tasks = [
            Task(title="Low", priority=TaskPriority.LOW),
            Task(title="High", priority=TaskPriority.HIGH),
            Task(title="Normal", priority=TaskPriority.NORMAL),
            Task(title="Critical", priority=TaskPriority.CRITICAL),
        ]
        
        selected = scheduler._select_priority(tasks)
        assert selected.priority == TaskPriority.CRITICAL
    
    def test_fair_selection(self, scheduler):
        """测试公平调度"""
        from ymcode.queue import Task, TaskPriority
        
        tasks = [
            Task(title="Task 1", priority=TaskPriority.NORMAL),
            Task(title="Task 2", priority=TaskPriority.NORMAL),
        ]
        
        # 第一次选择
        selected1 = scheduler._select_fair(tasks)
        
        # 模拟等待
        for _ in range(10):
            for task in tasks:
                if task.id in scheduler._stats:
                    scheduler._stats[task.id].wait_count += 1
        
        # 第二次选择（等待久的优先）
        selected2 = scheduler._select_fair(tasks)
        
        # 应该选择了等待更久的
        assert selected2 is not None
    
    def test_stats(self, scheduler):
        """测试统计信息"""
        stats = scheduler.get_stats()
        assert stats["max_concurrent"] == 5
        assert stats["policy"] == "PRIORITY"
        assert stats["running_tasks"] == 0


class TestA2ACoordinator:
    """A2ACoordinator 测试"""
    
    @pytest.fixture
    def coordinator(self):
        """创建测试用 coordinator"""
        return A2ACoordinator(
            agents=["ai1", "ai2", "ai3"],
            strategy=AssignmentStrategy.ROUND_ROBIN
        )
    
    def test_register_agent(self, coordinator):
        """测试注册 Agent"""
        coordinator.register_agent("ai4", capabilities=["coding", "testing"])
        
        agent = coordinator.get_agent("ai4")
        assert agent is not None
        assert "coding" in agent.capabilities
    
    def test_round_robin_assignment(self, coordinator):
        """测试轮询分配"""
        from ymcode.queue import Task
        
        agents = coordinator._get_available_agents()
        
        # 第一次选择
        selected1 = coordinator._select_round_robin(agents)
        
        # 第二次选择（应该不同）
        selected2 = coordinator._select_round_robin(agents)
        
        # 轮询应该选择不同的
        assert selected1.name != selected2.name
    
    def test_least_loaded_assignment(self, coordinator):
        """测试最少负载分配"""
        from ymcode.queue import Task
        
        # 设置不同的负载
        coordinator._agents["ai1"].tasks_assigned = 10
        coordinator._agents["ai2"].tasks_assigned = 5
        coordinator._agents["ai3"].tasks_assigned = 2
        
        agents = coordinator._get_available_agents()
        selected = coordinator._select_least_loaded(agents)
        
        # 应该选择负载最少的
        assert selected.name == "ai3"
    
    def test_priority_based_assignment(self, coordinator):
        """测试优先级分配"""
        from ymcode.queue import Task, TaskPriority
        
        # 设置不同的成功率
        coordinator._agents["ai1"].tasks_completed = 100
        coordinator._agents["ai1"].tasks_failed = 0
        
        coordinator._agents["ai2"].tasks_completed = 50
        coordinator._agents["ai2"].tasks_failed = 50
        
        task = Task(title="Critical Task", priority=TaskPriority.CRITICAL)
        agents = coordinator._get_available_agents()
        
        selected = coordinator._select_priority_based(agents, task)
        
        # 高优先级任务应该分配给成功率高的
        assert selected.name == "ai1"
    
    def test_handoff(self, coordinator):
        """测试任务交接"""
        coordinator._task_assignments["task-1"] = "ai1"
        
        # 模拟交接
        import asyncio
        result = asyncio.run(
            coordinator.handoff_task("task-1", "ai1", "ai2", reason="测试交接")
        )
        
        assert result is True
        assert coordinator.get_assigned_agent("task-1") == "ai2"
    
    def test_stats(self, coordinator):
        """测试统计信息"""
        stats = coordinator.get_stats()
        assert stats["total_agents"] == 3
        assert stats["strategy"] == "ROUND_ROBIN"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
