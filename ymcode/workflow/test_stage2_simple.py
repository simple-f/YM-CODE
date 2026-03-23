#!/usr/bin/env python3
"""
阶段 2 集成测试 - 独立版本 (不依赖 __init__.py)
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Stage 2 Integration Test")
print("=" * 60)
print()

# Test 1: Import modules directly
print("Test 1: Import modules")
print("-" * 60)
try:
    # Import directly from files
    import importlib.util
    
    # Load task module
    task_spec = importlib.util.spec_from_file_location(
        "task", 
        str(Path(__file__).parent.parent / "taskqueue" / "task.py")
    )
    task_module = importlib.util.module_from_spec(task_spec)
    task_spec.loader.exec_module(task_module)
    Task = task_module.Task
    TaskStatus = task_module.TaskStatus
    TaskPriority = task_module.TaskPriority
    
    # Load events module
    events_spec = importlib.util.spec_from_file_location(
        "events",
        str(Path(__file__).parent.parent / "events" / "__init__.py")
    )
    events_module = importlib.util.module_from_spec(events_spec)
    events_spec.loader.exec_module(events_module)
    EventBus = events_module.EventBus
    EventType = events_module.EventType
    
    print("[OK] Modules loaded successfully")
    print(f"   Task: {Task.__module__}")
    print(f"   EventBus: {EventBus.__module__}")
    
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Create Task
print("Test 2: Create Task")
print("-" * 60)
try:
    task = Task(
        title="Integration Test",
        description="Test Task and EventBus integration",
        priority=TaskPriority.HIGH
    )
    
    print(f"[OK] Task created")
    print(f"   ID: {task.id}")
    print(f"   Title: {task.title}")
    print(f"   Priority: {task.priority}")
    
except Exception as e:
    print(f"[FAIL] Task creation failed: {e}")
    sys.exit(1)

print()

# Test 3: Create EventBus
print("Test 3: Create EventBus")
print("-" * 60)
try:
    event_bus = EventBus()
    print(f"[OK] EventBus created")
    
except Exception as e:
    print(f"[FAIL] EventBus creation failed: {e}")
    sys.exit(1)

print()

# Summary
print("=" * 60)
print("Basic integration test PASSED!")
print("=" * 60)
print()
print("Verified:")
print("  [OK] Task module imported")
print("  [OK] EventBus module imported")
print("  [OK] Task creation works")
print("  [OK] EventBus creation works")
print()
print("Note: Full workflow test requires fixing __init__.py encoding")
print()
