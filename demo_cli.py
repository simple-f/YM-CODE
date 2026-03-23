#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI 演示脚本

演示 P0 模块的 CLI 功能
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from ymcode.queue import TaskQueue, Task, TaskStatus, TaskPriority
from ymcode.metrics import MetricsCollector
from ymcode.events import EventBus, EventType

print("=" * 60)
print("YM-CODE CLI 演示")
print("=" * 60)

# 演示 1: 任务队列
print("\n### 1. 任务队列演示 ###\n")

queue = TaskQueue()

# 创建任务
print("创建任务...")
task1 = Task(title="实现用户登录功能", description="支持邮箱和密码登录", priority=TaskPriority.HIGH, assigned_to="builder")
task2 = Task(title="代码审查", description="审查登录模块代码", priority=TaskPriority.NORMAL, assigned_to="reviewer")
task3 = Task(title="编写单元测试", description="为登录功能编写测试", priority=TaskPriority.LOW, assigned_to="tester")

queue.enqueue(task1)
queue.enqueue(task2)
queue.enqueue(task3)

print(f"[OK] 已创建 3 个任务")

# 查看任务列表
print("\n任务列表:")
tasks = queue.list_tasks(limit=10)
for i, task in enumerate(tasks, 1):
    print(f"  {i}. [{task.priority.name}] {task.title} -> {task.assigned_to}")

# 处理任务
print("\n处理任务...")
task = queue.dequeue()
print(f"[OK] 开始处理：{task.title}")
queue.complete_task(task.id, {"result": "功能已实现"})
print(f"[OK] 任务完成")

# 查看统计
print("\n任务统计:")
stats = queue.get_stats()
print(f"  总入队数：{stats['total_enqueued']}")
print(f"  已完成：{stats['total_completed']}")
print(f"  队列中：{stats['queue_size']}")

# 演示 2: 指标监控
print("\n### 2. 指标监控演示 ###\n")

collector = MetricsCollector()

# 记录指标
print("记录指标...")
collector.increment("system.total_tasks")
collector.increment("system.total_tasks")
collector.increment("agent.tasks_completed", {"agent_id": "builder"})
collector.gauge("agent.status", 1, {"agent_id": "builder"})
collector.timing("task.execution", 2.3)
collector.histogram("response_time", 1.5)

print("[OK] 已记录指标")

# 查看系统指标
print("\n系统指标:")
dashboard = collector.get_dashboard()
print(f"  总任务数：{dashboard['system'].get('total_tasks', 0)}")
print(f"  活跃 Agent: {dashboard['system'].get('active_agents', 0)}")

# 查看计数器
print("\n计数器:")
print(f"  system.total_tasks = {collector.get_counter('system.total_tasks')}")
print(f"  agent.tasks_completed:builder = {collector.get_counter('agent.tasks_completed:builder')}")

# 演示 3: 事件总线
print("\n### 3. 事件总线演示 ###\n")

bus = EventBus()

# 订阅事件
print("订阅事件...")
received_events = []

def event_callback(event):
    received_events.append(event)
    print(f"  [事件] {event.type.value} from {event.source}")

bus.subscribe(EventType.TASK_COMPLETED, event_callback)
bus.subscribe(None, event_callback)  # 全局订阅

# 发布事件
print("\n发布事件...")
bus.publish(EventType.TASK_CREATED, {"task_id": "1", "title": "任务 1"}, source="system")
bus.publish(EventType.TASK_STARTED, {"task_id": "1", "agent_id": "builder"}, source="builder")
bus.publish(EventType.TASK_COMPLETED, {"task_id": "1", "result": "成功"}, source="builder")

import time
time.sleep(0.1)  # 等待异步处理

print(f"\n✓ 已接收 {len(received_events)} 个事件")

# 查看事件统计
print("\n事件统计:")
event_stats = bus.get_stats()
print(f"  总事件数：{event_stats['total_events']}")
print(f"  订阅者数：{event_stats['subscriber_count']}")

print("\n" + "=" * 60)
print("演示完成!")
print("=" * 60)
