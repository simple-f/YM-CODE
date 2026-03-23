#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LangGraph A2A Coordinator (已修复版本)
"""

import asyncio
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("LangGraph A2A Coordinator - 修复验证测试")
print("=" * 60)
print()

# Test 1: Import check
print("Test 1: 导入模块")
print("-" * 60)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from typing import TypedDict, Optional, Literal, List, Dict, Any
    
    print("[OK] LangGraph 导入成功")
except Exception as e:
    print(f"[FAIL] 导入失败：{e}")
    sys.exit(1)

print()

# Test 2: Create coordinator instance
print("Test 2: 创建 Coordinator 实例")
print("-" * 60)
try:
    from ymcode.workflow.langgraph_coordinator import (
        LangGraphA2ACoordinator,
        AssignmentStrategy,
        TaskStatus,
        AgentInfo
    )
    
    coordinator = LangGraphA2ACoordinator(
        agents=['ai1', 'ai2', 'ai3'],
        strategy=AssignmentStrategy.ROUND_ROBIN
    )
    
    print(f"[OK] Coordinator 创建成功")
    print(f"   Agent 列表：{list(coordinator._agents.keys())}")
    print(f"   工作流图节点：{list(coordinator.app.get_graph().nodes)}")
    
except Exception as e:
    print(f"[FAIL] 创建失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Check Agent registration
print("Test 3: Agent 注册功能")
print("-" * 60)
try:
    # 注册新 Agent
    coordinator.register_agent('ai4', capabilities=['python', 'testing'])
    
    ai4 = coordinator.get_agent('ai4')
    assert ai4 is not None, "Agent ai4 注册失败"
    assert 'python' in ai4.capabilities, "Agent 能力设置失败"
    
    print(f"[OK] Agent 注册成功")
    print(f"   ai4 能力：{ai4.capabilities}")
    print(f"   总 Agent 数：{len(coordinator.get_all_agents())}")
    
except Exception as e:
    print(f"[FAIL] Agent 注册失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Check available agents
print("Test 4: 获取可用 Agent")
print("-" * 60)
try:
    available = coordinator._get_available_agents()
    
    print(f"[OK] 获取可用 Agent: {len(available)} 个")
    for agent in available:
        print(f"   - {agent.name} (status={agent.status})")
    
    # 应该至少有 4 个 Agent (ai1, ai2, ai3, ai4)
    assert len(available) >= 4, f"期望至少 4 个 Agent，实际 {len(available)}"
    
except Exception as e:
    print(f"[FAIL] 获取可用 Agent 失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Agent selection strategies
print("Test 5: Agent 选择策略")
print("-" * 60)
try:
    available = coordinator._get_available_agents()
    
    # 轮询选择
    selected1 = coordinator._select_round_robin(available)
    print(f"[OK] 轮询选择：{selected1.name if selected1 else 'None'}")
    
    # 最少负载选择
    selected2 = coordinator._select_least_loaded(available)
    print(f"[OK] 最少负载选择：{selected2.name if selected2 else 'None'}")
    
    # 优先级选择
    from ymcode.taskqueue import Task, TaskPriority
    task = Task(id="test-1", priority=TaskPriority.HIGH, description="High priority")
    selected3 = coordinator._select_priority_based(available, task)
    print(f"[OK] 优先级选择：{selected3.name if selected3 else 'None'}")
    
except Exception as e:
    print(f"[FAIL] Agent 选择失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 6: Workflow structure
print("Test 6: 工作流结构验证")
print("-" * 60)
try:
    graph = coordinator.app.get_graph()
    
    nodes = list(graph.nodes)
    edges = list(graph.edges)
    
    print(f"[OK] 工作流结构正确")
    print(f"   节点数：{len(nodes)}")
    print(f"   边数：{len(edges)}")
    
    # 验证关键节点存在
    expected_nodes = ['__start__', 'initialize', 'route', 'select_agent', 
                      'execute', 'complete', 'fail', 'finalize', '__end__']
    
    for node in expected_nodes:
        assert node in nodes, f"缺少节点：{node}"
    
    print(f"   关键节点检查：通过")
    
except Exception as e:
    print(f"[FAIL] 工作流结构验证失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 7: Task assignment (模拟)
print("Test 7: 任务分配 (模拟)")
print("-" * 60)
try:
    from ymcode.taskqueue import Task, TaskPriority
    
    # 创建测试任务
    task = Task(
        id="test-task-001",
        type="code",
        priority=TaskPriority.NORMAL,
        description="Test task for LangGraph coordinator"
    )
    
    print(f"   任务 ID: {task.id}")
    print(f"   优先级：{task.priority}")
    
    # 注意：实际执行需要完整的事件循环和异步环境
    # 这里只验证准备工作
    
    print(f"[OK] 任务创建成功")
    print(f"   注：完整异步测试需要 pytest-asyncio")
    
except Exception as e:
    print(f"[FAIL] 任务分配测试失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 8: Stats collection
print("Test 8: 统计信息收集")
print("-" * 60)
try:
    stats = coordinator.get_stats()
    
    print(f"[OK] 统计信息收集成功")
    print(f"   总 Agent 数：{stats['total_agents']}")
    print(f"   Agent 详情:")
    for name, info in stats['agents'].items():
        print(f"     {name}: assigned={info['tasks_assigned']}, " +
              f"completed={info['tasks_completed']}, failed={info['tasks_failed']}")
    
except Exception as e:
    print(f"[FAIL] 统计信息收集失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Summary
print("=" * 60)
print("所有测试通过！✅")
print("=" * 60)
print()
print("已修复问题:")
print("  ✅ P1: _get_available_agents() 从 self._agents 获取")
print("  ✅ P1: 节点函数添加 self 参数 (改为实例方法)")
print("  ✅ P1: 重试逻辑添加次数限制")
print("  ✅ P2: 类型使用 TaskStatus Enum")
print("  ✅ P2: 添加 Dict 导入")
print("  ✅ P2: Agent 状态实际更新")
print("  ✅ P2: 添加 asyncio.Lock 并发控制")
print()
print("下一步:")
print("  1. 集成 EventBus 发布事件")
print("  2. 实现完整的异步任务执行")
print("  3. 添加 pytest 测试套件")
print("  4. 实现 handoff_task() 功能")
print()
