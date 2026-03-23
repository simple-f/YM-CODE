#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 模块测试

测试任务队列、结果收集器、指标收集器、事件总线
"""

import pytest
import time
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from ymcode.queue import TaskQueue, Task, TaskStatus, TaskPriority, TaskResult
from ymcode.results import ResultCollector
from ymcode.metrics import MetricsCollector
from ymcode.events import EventBus, EventType, task_completed, task_failed


class TestTaskQueue:
    """测试任务队列"""
    
    def test_enqueue_dequeue(self):
        """测试入队出队"""
        queue = TaskQueue()
        
        task = Task(title="测试任务")
        task_id = queue.enqueue(task)
        
        assert task_id == task.id
        assert queue.get_task(task_id) == task
        
        dequeued = queue.dequeue()
        assert dequeued == task
        assert dequeued.status == TaskStatus.PENDING
    
    def test_priority(self):
        """测试优先级"""
        queue = TaskQueue()
        
        # 低优先级先入队
        low_task = Task(title="低优先级", priority=TaskPriority.LOW)
        queue.enqueue(low_task)
        
        # 高优先级后入队
        high_task = Task(title="高优先级", priority=TaskPriority.HIGH)
        queue.enqueue(high_task)
        
        # 高优先级应该先出队
        dequeued = queue.dequeue()
        assert dequeued == high_task
        
        dequeued = queue.dequeue()
        assert dequeued == low_task
    
    def test_complete_task(self):
        """测试完成任务"""
        queue = TaskQueue()
        
        task = Task(title="测试任务")
        queue.enqueue(task)
        
        queue.dequeue()  # 出队
        
        result = queue.complete_task(task.id, {"result": "success"})
        
        assert result is True
        assert task.status == TaskStatus.COMPLETED
        assert task.metadata["result"] == {"result": "success"}
    
    def test_fail_task_with_retry(self):
        """测试任务失败重试"""
        queue = TaskQueue()
        
        task = Task(title="测试任务", max_retries=2)
        queue.enqueue(task)
        
        queue.dequeue()
        queue.fail_task(task.id, "错误 1")
        
        # 应该自动重试
        assert task.status == TaskStatus.QUEUED
        assert task.retry_count == 1
        
        queue.dequeue()
        queue.fail_task(task.id, "错误 2")
        
        # 达到最大重试次数
        assert task.status == TaskStatus.FAILED
        assert task.retry_count == 2
    
    def test_persistence(self):
        """测试持久化"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            storage_path = f.name
        
        try:
            # 创建队列并添加任务
            queue1 = TaskQueue(storage_path=storage_path)
            task = Task(title="持久化测试")
            queue1.enqueue(task)
            
            # 创建新队列（加载持久化数据）
            queue2 = TaskQueue(storage_path=storage_path)
            loaded_task = queue2.get_task(task.id)
            
            assert loaded_task is not None
            assert loaded_task.title == "持久化测试"
        
        finally:
            Path(storage_path).unlink(missing_ok=True)
    
    def test_stats(self):
        """测试统计"""
        queue = TaskQueue()
        
        for i in range(5):
            task = Task(title=f"任务{i}")
            queue.enqueue(task)
            queue.dequeue()
            queue.complete_task(task.id)
        
        stats = queue.get_stats()
        
        assert stats["total_enqueued"] == 5
        assert stats["total_completed"] == 5
        assert stats["queue_size"] == 0


class TestResultCollector:
    """测试结果收集器"""
    
    def test_store_get(self):
        """测试存储和获取"""
        collector = ResultCollector()
        
        result = TaskResult(
            task_id="task-123",
            agent_id="ai2",
            success=True,
            result={"data": "ok"}
        )
        
        collector.store(result)
        
        results = collector.get("task-123")
        assert len(results) == 1
        assert results[0].success is True
    
    def test_multiple_results(self):
        """测试多 Agent 结果"""
        collector = ResultCollector()
        
        # 多个 Agent 执行同一任务
        collector.store(TaskResult(task_id="task-1", agent_id="ai1", success=True, result={"a": 1}))
        collector.store(TaskResult(task_id="task-1", agent_id="ai2", success=True, result={"b": 2}))
        collector.store(TaskResult(task_id="task-1", agent_id="ai3", success=False, error="错误"))
        
        results = collector.get_all("task-1")
        assert len(results) == 3
        
        # 聚合结果
        aggregated = collector.aggregate_results("task-1")
        assert aggregated["total_results"] == 3
        assert aggregated["success_count"] == 2
        assert aggregated["failed_count"] == 1
    
    def test_subscription(self):
        """测试订阅"""
        collector = ResultCollector()
        
        received = []
        
        def callback(result):
            received.append(result)
        
        collector.subscribe("task-1", callback)
        
        collector.store(TaskResult(task_id="task-1", agent_id="ai2", success=True))
        
        assert len(received) == 1
        assert received[0].task_id == "task-1"
    
    def test_get_by_agent(self):
        """测试按 Agent 查询"""
        collector = ResultCollector()
        
        collector.store(TaskResult(task_id="t1", agent_id="ai2", success=True))
        collector.store(TaskResult(task_id="t2", agent_id="ai2", success=True))
        collector.store(TaskResult(task_id="t3", agent_id="ai3", success=True))
        
        results = collector.get_by_agent("ai2")
        assert len(results) == 2


class TestMetricsCollector:
    """测试指标收集器"""
    
    def test_record_get(self):
        """测试记录和获取"""
        collector = MetricsCollector()
        
        collector.record("agent.tasks_completed", 1, {"agent_id": "ai2"})
        
        metrics = collector.get_metrics("agent.tasks_completed", hours=1)
        assert len(metrics) == 1
        assert metrics[0].value == 1
    
    def test_counter(self):
        """测试计数器"""
        collector = MetricsCollector()
        
        for _ in range(10):
            collector.increment("system.total_tasks")
        
        assert collector.get_counter("system.total_tasks") == 10
    
    def test_histogram(self):
        """测试直方图"""
        collector = MetricsCollector()
        
        for i in range(100):
            collector.histogram("response_time", i * 0.1)
        
        stats = collector.get_histogram_stats("response_time")
        
        assert stats["count"] == 100
        assert stats["min"] == 0
        assert stats["max"] == 9.9
        assert 4 < stats["avg"] < 6
    
    def test_gauge(self):
        """测试 gauge"""
        collector = MetricsCollector()
        
        collector.gauge("agent.status", 1, {"agent_id": "ai2"})
        assert collector.get_latest("agent.status", {"agent_id": "ai2"}) == 1
        
        collector.gauge("agent.status", 2, {"agent_id": "ai2"})
        assert collector.get_latest("agent.status", {"agent_id": "ai2"}) == 2
    
    def test_agent_metrics(self):
        """测试 Agent 指标"""
        collector = MetricsCollector()
        
        collector.increment("agent.tasks_completed:ai2")
        collector.increment("agent.tasks_completed:ai2")
        collector.timing("agent.execution_time", 1.5, {"agent_id": "ai2"})
        
        metrics = collector.get_agent_metrics("ai2")
        
        assert metrics["tasks_completed"] == 2


class TestEventBus:
    """测试事件总线"""
    
    def test_publish_subscribe(self):
        """测试发布订阅"""
        bus = EventBus()
        
        received = []
        
        def callback(event):
            received.append(event)
        
        bus.subscribe(EventType.TASK_COMPLETED, callback)
        
        bus.publish(
            EventType.TASK_COMPLETED,
            {"task_id": "123", "result": "ok"},
            source="ai2"
        )
        
        # 等待异步处理
        time.sleep(0.1)
        
        assert len(received) == 1
        assert received[0].type == EventType.TASK_COMPLETED
        assert received[0].data["task_id"] == "123"
    
    def test_global_subscription(self):
        """测试全局订阅"""
        bus = EventBus()
        
        received = []
        
        def callback(event):
            received.append(event)
        
        bus.subscribe(None, callback)  # 订阅所有事件
        
        bus.publish(EventType.TASK_STARTED, {"task_id": "1"}, source="ai2")
        bus.publish(EventType.TASK_COMPLETED, {"task_id": "1"}, source="ai2")
        
        time.sleep(0.1)
        
        assert len(received) == 2
    
    def test_get_events(self):
        """测试获取事件"""
        bus = EventBus()
        
        bus.publish(EventType.TASK_COMPLETED, {"task_id": "1"}, source="ai2")
        bus.publish(EventType.TASK_COMPLETED, {"task_id": "2"}, source="ai3")
        bus.publish(EventType.TASK_FAILED, {"task_id": "3"}, source="ai2")
        
        time.sleep(0.1)
        
        # 按类型过滤
        events = bus.get_events(event_type=EventType.TASK_COMPLETED)
        assert len(events) == 2
        
        # 按来源过滤
        events = bus.get_events(source="ai2")
        assert len(events) == 2
    
    def test_replay(self):
        """测试回放"""
        bus = EventBus()
        
        from_time = datetime.now()
        
        bus.publish(EventType.TASK_COMPLETED, {"task_id": "1"}, source="ai2")
        bus.publish(EventType.TASK_COMPLETED, {"task_id": "2"}, source="ai2")
        
        time.sleep(0.1)
        
        received = []
        
        def callback(event):
            received.append(event)
        
        # 回放
        count = bus.replay(from_time, callback=callback)
        
        assert count == 2
        assert len(received) == 2
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        bus = EventBus()
        
        received = []
        
        def callback(event):
            received.append(event)
        
        bus.subscribe(EventType.TASK_COMPLETED, callback)
        
        # 使用便捷函数
        event = task_completed("task-123", "ai2", {"result": "ok"})
        bus.publish_event(event)
        
        time.sleep(0.1)
        
        assert len(received) == 1
        assert received[0].data["task_id"] == "task-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
