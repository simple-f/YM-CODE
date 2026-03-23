#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎独立测试（不依赖 conftest.py）
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ymcode.workflow import (
    StateTracker, TaskState,
    CascadeCanceller,
    TaskScheduler, SchedulingPolicy,
    A2ACoordinator, AssignmentStrategy
)


def test_state_tracker():
    """测试 StateTracker"""
    print("\n=== Testing StateTracker ===")
    
    tracker = StateTracker(storage_path=Path(__file__).parent / "test_state.json")
    
    # 测试 1: 记录状态
    result = tracker.record_state("task-1", TaskState.PENDING)
    assert result is True, "记录状态失败"
    print("[PASS] 记录状态成功")
    
    # 测试 2: 获取当前状态
    state = tracker.get_current_state("task-1")
    assert state == TaskState.PENDING, f"状态错误：{state}"
    print(f"[PASS] 获取当前状态：{state}")
    
    # 测试 3: 状态历史
    tracker.record_state("task-1", TaskState.SCHEDULED)
    tracker.record_state("task-1", TaskState.RUNNING)
    tracker.record_state("task-1", TaskState.COMPLETED)
    history = tracker.get_history("task-1")
    print(f"[INFO] 状态历史：{len(history)} 条记录")
    # 注意：第一次 PENDING->PENDING 是无效的，所以实际是 4 条
    assert len(history) >= 3, f"历史记录数量错误：{len(history)}"
    print(f"[PASS] 状态历史验证通过")
    
    # 测试 4: 状态转换验证
    assert tracker.is_valid_transition(TaskState.PENDING, TaskState.SCHEDULED) is True
    assert tracker.is_valid_transition(TaskState.PENDING, TaskState.COMPLETED) is False
    print("[PASS] 状态转换验证正确")
    
    # 测试 5: 统计信息
    stats = tracker.get_stats()
    assert stats["total_tasks"] > 0, "统计信息错误"
    print(f"[PASS] 统计信息：{stats['total_tasks']} 个任务")
    
    # 清理
    if tracker.storage_path.exists():
        tracker.storage_path.unlink()
    
    print("\n[OK] StateTracker: ALL PASSED\n")
    return True


def test_cascade_canceller():
    """测试 CascadeCanceller"""
    print("\n=== Testing CascadeCanceller ===")
    
    canceller = CascadeCanceller()
    
    # 测试 1: 注册父子关系
    canceller.register_parent_child("parent-1", "child-1")
    canceller.register_parent_child("parent-1", "child-2")
    print("[PASS] 注册父子关系成功")
    
    # 测试 2: 获取子任务
    children = canceller.get_children("parent-1")
    assert len(children) == 2, f"子任务数量错误：{len(children)}"
    print(f"[PASS] 获取子任务：{len(children)} 个")
    
    # 测试 3: 递归获取
    canceller.register_parent_child("child-1", "grandchild-1")
    all_children = canceller.get_children("parent-1", recursive=True)
    assert len(all_children) == 3, f"递归子任务数量错误：{len(all_children)}"
    print(f"[PASS] 递归获取子任务：{len(all_children)} 个")
    
    # 测试 4: 获取父任务
    parent = canceller.get_parent("child-1")
    assert parent == "parent-1", f"父任务错误：{parent}"
    print(f"[PASS] 获取父任务：{parent}")
    
    # 测试 5: 关系统计
    stats = canceller.get_relation_stats()
    assert stats["total_relations"] > 0, "关系统计错误"
    print(f"[PASS] 关系统计：{stats}")
    
    print("\n[OK] CascadeCanceller: ALL PASSED\n")
    return True


def test_scheduler():
    """测试 TaskScheduler"""
    print("\n=== Testing TaskScheduler ===")
    
    scheduler = TaskScheduler(max_concurrent=5, policy=SchedulingPolicy.PRIORITY)
    
    # 测试 1: 初始化
    assert scheduler.max_concurrent == 5, "并发数错误"
    assert scheduler.policy == SchedulingPolicy.PRIORITY, "策略错误"
    print("[PASS] 初始化成功")
    
    # 测试 2: 统计信息
    stats = scheduler.get_stats()
    assert stats["max_concurrent"] == 5, "统计信息错误"
    print(f"[PASS] 统计信息：{stats}")
    
    # 测试 3: 优先级选择
    from ymcode.queue import Task, TaskPriority
    tasks = [
        Task(title="Low", priority=TaskPriority.LOW),
        Task(title="High", priority=TaskPriority.HIGH),
        Task(title="Urgent", priority=TaskPriority.URGENT),
    ]
    selected = scheduler._select_priority(tasks)
    assert selected.priority == TaskPriority.URGENT, f"选择错误：{selected.priority}"
    print(f"[PASS] 优先级选择：{selected.title}")
    
    print("\n[OK] TaskScheduler: ALL PASSED\n")
    return True


def test_a2a_coordinator():
    """测试 A2ACoordinator"""
    print("\n=== Testing A2ACoordinator ===")
    
    coordinator = A2ACoordinator(
        agents=["ai1", "ai2", "ai3"],
        strategy=AssignmentStrategy.ROUND_ROBIN
    )
    
    # 测试 1: 初始化
    assert len(coordinator._agents) == 3, "Agent 数量错误"
    print("[PASS] 初始化成功")
    
    # 测试 2: 获取可用 Agent
    available = coordinator._get_available_agents()
    assert len(available) == 3, f"可用 Agent 数量错误：{len(available)}"
    print(f"[PASS] 可用 Agent: {len(available)} 个")
    
    # 测试 3: 轮询分配
    selected1 = coordinator._select_round_robin(available)
    selected2 = coordinator._select_round_robin(available)
    assert selected1.name != selected2.name, "轮询未正常工作"
    print(f"[PASS] 轮询分配：{selected1.name} -> {selected2.name}")
    
    # 测试 4: 最少负载分配
    coordinator._agents["ai1"].tasks_assigned = 10
    coordinator._agents["ai2"].tasks_assigned = 5
    coordinator._agents["ai3"].tasks_assigned = 2
    selected = coordinator._select_least_loaded(available)
    assert selected.name == "ai3", f"最少负载选择错误：{selected.name}"
    print(f"[PASS] 最少负载分配：{selected.name}")
    
    # 测试 5: 统计信息
    stats = coordinator.get_stats()
    assert stats["total_agents"] == 3, "统计信息错误"
    print(f"[PASS] 统计信息：{stats['total_agents']} 个 Agent")
    
    print("\n[OK] A2ACoordinator: ALL PASSED\n")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("YM-CODE Workflow Engine Tests")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("StateTracker", test_state_tracker()))
    except Exception as e:
        print(f"\n[FAIL] StateTracker FAILED: {e}\n")
        results.append(("StateTracker", False))
    
    try:
        results.append(("CascadeCanceller", test_cascade_canceller()))
    except Exception as e:
        print(f"\n[FAIL] CascadeCanceller FAILED: {e}\n")
        results.append(("CascadeCanceller", False))
    
    try:
        results.append(("TaskScheduler", test_scheduler()))
    except Exception as e:
        print(f"\n[FAIL] TaskScheduler FAILED: {e}\n")
        results.append(("TaskScheduler", False))
    
    try:
        results.append(("A2ACoordinator", test_a2a_coordinator()))
    except Exception as e:
        print(f"\n[FAIL] A2ACoordinator FAILED: {e}\n")
        results.append(("A2ACoordinator", False))
    
    # 汇总
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print("\n[WARNING] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
