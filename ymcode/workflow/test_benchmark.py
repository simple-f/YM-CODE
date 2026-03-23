#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段 4: 性能基准测试

测试 LangGraph A2A Coordinator 的性能指标
"""

import asyncio
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Stage 4: Performance Benchmark")
print("=" * 60)
print()

# Test 1: Task Assignment Latency
print("Test 1: Task Assignment Latency")
print("-" * 60)

async def test_assignment_latency():
    """测试任务分配延迟"""
    try:
        from ymcode.workflow.langgraph_coordinator import LangGraphA2ACoordinator
        from ymcode.taskqueue.task import Task, TaskPriority
        
        coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3', 'ai4', 'ai5'])
        
        # 测试 100 次任务分配
        latencies = []
        for i in range(100):
            task = Task(title=f"Test Task {i}", priority=TaskPriority.NORMAL)
            
            start = time.perf_counter()
            await coordinator.assign_task(task)
            end = time.perf_counter()
            
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print(f"[OK] Task Assignment Latency")
        print(f"   Samples: {len(latencies)}")
        print(f"   Average: {avg_latency:.2f} ms")
        print(f"   Min: {min_latency:.2f} ms")
        print(f"   Max: {max_latency:.2f} ms")
        print(f"   P95: {p95_latency:.2f} ms")
        
        return {
            'test': 'assignment_latency',
            'samples': len(latencies),
            'avg_ms': avg_latency,
            'min_ms': min_latency,
            'max_ms': max_latency,
            'p95_ms': p95_latency
        }
        
    except Exception as e:
        print(f"[FAIL] Assignment latency test failed: {e}")
        return None

# Run test
result1 = asyncio.run(test_assignment_latency())
print()

# Test 2: Concurrent Task Assignment
print("Test 2: Concurrent Task Assignment")
print("-" * 60)

async def test_concurrent_assignment():
    """测试并发任务分配"""
    try:
        from ymcode.workflow.langgraph_coordinator import LangGraphA2ACoordinator
        from ymcode.taskqueue.task import Task, TaskPriority
        
        coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3', 'ai4', 'ai5'])
        
        # 并发分配 50 个任务
        num_tasks = 50
        tasks = [Task(title=f"Concurrent Task {i}", priority=TaskPriority.NORMAL) for i in range(num_tasks)]
        
        start = time.perf_counter()
        
        # 并发执行
        coroutines = [coordinator.assign_task(task) for task in tasks]
        results = await asyncio.gather(*coroutines)
        
        end = time.perf_counter()
        total_time = end - start
        
        successful = sum(1 for r in results if r is not None)
        throughput = num_tasks / total_time
        
        print(f"[OK] Concurrent Assignment")
        print(f"   Tasks: {num_tasks}")
        print(f"   Total Time: {total_time:.2f} s")
        print(f"   Successful: {successful}/{num_tasks}")
        print(f"   Throughput: {throughput:.2f} tasks/s")
        
        return {
            'test': 'concurrent_assignment',
            'tasks': num_tasks,
            'total_time_s': total_time,
            'successful': successful,
            'throughput': throughput
        }
        
    except Exception as e:
        print(f"[FAIL] Concurrent assignment test failed: {e}")
        return None

# Run test
result2 = asyncio.run(test_concurrent_assignment())
print()

# Test 3: Memory Usage
print("Test 3: Memory Usage")
print("-" * 60)

try:
    import tracemalloc
    tracemalloc.start()
    
    from ymcode.workflow.langgraph_coordinator import LangGraphA2ACoordinator
    
    coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3', 'ai4', 'ai5'])
    
    # 创建 100 个任务
    for i in range(100):
        coordinator._handoffs.append({
            'task_id': f'task-{i}',
            'from_agent': 'ai1',
            'to_agent': 'ai2',
            'timestamp': time.time(),
            'reason': 'test'
        })
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"[OK] Memory Usage")
    print(f"   Current: {current / 1024 / 1024:.2f} MB")
    print(f"   Peak: {peak / 1024 / 1024:.2f} MB")
    
    result3 = {
        'test': 'memory_usage',
        'current_mb': current / 1024 / 1024,
        'peak_mb': peak / 1024 / 1024
    }
    
except Exception as e:
    print(f"[FAIL] Memory usage test failed: {e}")
    result3 = None

print()

# Test 4: Handoff Performance
print("Test 4: Handoff Performance")
print("-" * 60)

async def test_handoff_performance():
    """测试任务交接性能"""
    try:
        from ymcode.workflow.langgraph_coordinator import LangGraphA2ACoordinator
        
        coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3'])
        
        # 预先分配任务
        for i in range(20):
            coordinator._task_assignments[f'task-{i}'] = 'ai1'
        
        # 执行 20 次交接
        latencies = []
        for i in range(20):
            start = time.perf_counter()
            await coordinator.handoff_task(
                task_id=f'task-{i}',
                from_agent='ai1',
                to_agent='ai2',
                reason='load_balancing'
            )
            end = time.perf_counter()
            
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"[OK] Handoff Performance")
        print(f"   Handoffs: {len(latencies)}")
        print(f"   Average: {avg_latency:.2f} ms")
        
        return {
            'test': 'handoff_performance',
            'handoffs': len(latencies),
            'avg_ms': avg_latency
        }
        
    except Exception as e:
        print(f"[FAIL] Handoff performance test failed: {e}")
        return None

# Run test
result4 = asyncio.run(test_handoff_performance())
print()

# Summary
print("=" * 60)
print("Performance Benchmark Summary")
print("=" * 60)
print()

results = [result1, result2, result3, result4]
successful_tests = sum(1 for r in results if r is not None)

print(f"Tests Completed: {successful_tests}/{len(results)}")
print()

if result1:
    print(f"Task Assignment:")
    print(f"  Average Latency: {result1['avg_ms']:.2f} ms")
    print(f"  P95 Latency: {result1['p95_ms']:.2f} ms")
    print()

if result2:
    print(f"Concurrent Assignment:")
    print(f"  Throughput: {result2['throughput']:.2f} tasks/s")
    print(f"  Success Rate: {result2['successful']}/{result2['tasks']}")
    print()

if result3:
    print(f"Memory Usage:")
    print(f"  Current: {result3['current_mb']:.2f} MB")
    print(f"  Peak: {result3['peak_mb']:.2f} MB")
    print()

if result4:
    print(f"Handoff:")
    print(f"  Average Latency: {result4['avg_ms']:.2f} ms")
    print()

print("=" * 60)
print("Benchmark Complete!")
print("=" * 60)
