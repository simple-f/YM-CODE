#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 模块独立测试 - Windows 兼容版
"""

import sys
import time
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.queue import TaskQueue, Task, TaskStatus, TaskPriority, TaskResult
from ymcode.results import ResultCollector
from ymcode.metrics import MetricsCollector
from ymcode.events import EventBus, EventType


def test_task_queue():
    print("\n=== Test Task Queue ===")
    queue = TaskQueue()
    
    print("Test 1: enqueue/dequeue... ", end="")
    task = Task(title="Test Task")
    task_id = queue.enqueue(task)
    assert task_id == task.id
    dequeued = queue.dequeue()
    assert dequeued == task
    print("OK")
    
    print("Test 2: priority... ", end="")
    low_task = Task(title="Low Priority", priority=TaskPriority.LOW)
    queue.enqueue(low_task)
    high_task = Task(title="High Priority", priority=TaskPriority.HIGH)
    queue.enqueue(high_task)
    dequeued = queue.dequeue()
    assert dequeued == high_task
    print("OK")
    
    print("Test 3: complete... ", end="")
    queue.dequeue()
    result = queue.complete_task(low_task.id, {"result": "success"})
    assert result is True
    assert low_task.status == TaskStatus.COMPLETED
    print("OK")
    
    print("Test 4: retry... ", end="")
    retry_task = Task(title="Retry Task", max_retries=2)
    queue.enqueue(retry_task)
    queue.dequeue()
    queue.fail_task(retry_task.id, "Error 1")
    assert retry_task.status == TaskStatus.QUEUED
    assert retry_task.retry_count == 1
    print("OK")
    
    print("Test 5: stats... ", end="")
    stats = queue.get_stats()
    assert stats["total_enqueued"] >= 3
    assert stats["total_completed"] >= 1
    print("OK")
    
    print("[PASS] Task Queue Tests")
    return True


def test_result_collector():
    print("\n=== Test Result Collector ===")
    collector = ResultCollector()
    
    print("Test 1: store/get... ", end="")
    result = TaskResult(task_id="task-123", agent_id="ai2", success=True, result={"data": "ok"})
    collector.store(result)
    results = collector.get("task-123")
    assert len(results) == 1
    print("OK")
    
    print("Test 2: multi-agent... ", end="")
    collector.store(TaskResult(task_id="task-2", agent_id="ai1", success=True, result={"a": 1}))
    collector.store(TaskResult(task_id="task-2", agent_id="ai2", success=True, result={"b": 2}))
    collector.store(TaskResult(task_id="task-2", agent_id="ai3", success=False, error="Error"))
    aggregated = collector.aggregate_results("task-2")
    assert aggregated["total_results"] == 3
    assert aggregated["success_count"] == 2
    print("OK")
    
    print("Test 3: subscription... ", end="")
    received = []
    def callback(result): received.append(result)
    collector.subscribe("task-3", callback)
    collector.store(TaskResult(task_id="task-3", agent_id="ai2", success=True))
    time.sleep(0.1)
    assert len(received) == 1
    print("OK")
    
    print("Test 4: by_agent... ", end="")
    results = collector.get_by_agent("ai2")
    assert len(results) >= 2
    print("OK")
    
    print("[PASS] Result Collector Tests")
    return True


def test_metrics_collector():
    print("\n=== Test Metrics Collector ===")
    collector = MetricsCollector()
    
    print("Test 1: record/get... ", end="")
    collector.record("agent.tasks_completed", 1, {"agent_id": "ai2"})
    metrics = collector.get_metrics("agent.tasks_completed", hours=1)
    assert len(metrics) == 1
    print("OK")
    
    print("Test 2: counter... ", end="")
    for _ in range(10):
        collector.increment("system.total_tasks")
    assert collector.get_counter("system.total_tasks") == 10
    print("OK")
    
    print("Test 3: histogram... ", end="")
    for i in range(100):
        collector.histogram("response_time", i * 0.1)
    stats = collector.get_histogram_stats("response_time")
    assert stats["count"] == 100
    assert stats["min"] == 0
    assert stats["max"] == 9.9
    print("OK")
    
    print("Test 4: gauge... ", end="")
    collector.gauge("agent.status", 1, {"agent_id": "ai2"})
    assert collector.get_latest("agent.status", {"agent_id": "ai2"}) == 1
    print("OK")
    
    print("Test 5: dashboard... ", end="")
    dashboard = collector.get_dashboard()
    assert "system" in dashboard
    assert "success_rate_timeline" in dashboard
    print("OK")
    
    print("[PASS] Metrics Collector Tests")
    return True


def test_event_bus():
    print("\n=== Test Event Bus ===")
    bus = EventBus()
    
    print("Test 1: pub/sub... ", end="")
    received = []
    def callback(event): received.append(event)
    bus.subscribe(EventType.TASK_COMPLETED, callback)
    bus.publish(EventType.TASK_COMPLETED, {"task_id": "123"}, source="ai2")
    time.sleep(0.1)
    assert len(received) == 1
    print("OK")
    
    print("Test 2: global sub... ", end="")
    received.clear()
    bus.subscribe(None, callback)
    bus.publish(EventType.TASK_STARTED, {"task_id": "1"}, source="ai2")
    bus.publish(EventType.TASK_COMPLETED, {"task_id": "1"}, source="ai2")
    time.sleep(0.1)
    assert len(received) >= 2
    print("OK")
    
    print("Test 3: get_events... ", end="")
    events = bus.get_events(event_type=EventType.TASK_COMPLETED)
    assert len(events) >= 1
    print("OK")
    
    print("Test 4: stats... ", end="")
    stats = bus.get_stats()
    assert stats["total_events"] >= 2
    print("OK")
    
    bus.shutdown()
    print("[PASS] Event Bus Tests")
    return True


def test_persistence():
    print("\n=== Test Persistence ===")
    
    print("Test 1: queue... ", end="")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        storage_path = f.name
    try:
        queue1 = TaskQueue(storage_path=storage_path)
        task = Task(title="Persistence Test")
        queue1.enqueue(task)
        queue2 = TaskQueue(storage_path=storage_path)
        loaded_task = queue2.get_task(task.id)
        assert loaded_task is not None
        print("OK")
    finally:
        Path(storage_path).unlink(missing_ok=True)
    
    print("Test 2: results... ", end="")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        storage_path = f.name
    try:
        collector1 = ResultCollector(storage_path=storage_path)
        collector1.store(TaskResult(task_id="task-1", agent_id="ai2", success=True))
        collector2 = ResultCollector(storage_path=storage_path)
        results = collector2.get("task-1")
        assert len(results) == 1
        print("OK")
    finally:
        Path(storage_path).unlink(missing_ok=True)
    
    print("[PASS] Persistence Tests")
    return True


def main():
    print("=" * 60)
    print("P0 Module Test Suite")
    print("=" * 60)
    
    tests = [
        ("Task Queue", test_task_queue),
        ("Result Collector", test_result_collector),
        ("Metrics Collector", test_metrics_collector),
        ("Event Bus", test_event_bus),
        ("Persistence", test_persistence),
    ]
    
    passed = failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
