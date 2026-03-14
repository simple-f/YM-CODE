#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MemoryStore
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.agents.memory_store import MemoryStore


def test_memory_store():
    """测试 MemoryStore"""
    print("=" * 60)
    print("MemoryStore 测试")
    print("=" * 60)
    
    # 创建存储
    store = MemoryStore()
    print("\n[OK] MemoryStore 初始化完成")
    print(f"   数据库：{store.db_path}")
    
    # 测试 1: 添加记忆
    print("\n[测试 1] 添加记忆...")
    store.add_memory("builder", "创建文件 test.py", "note")
    store.add_memory("reviewer", "审查代码质量", "note")
    store.add_memory("builder", "运行测试通过", "task")
    print("   已添加 3 条记忆")
    
    # 测试 2: 获取记忆
    print("\n[测试 2] 获取记忆...")
    memories = store.get_memories(limit=10)
    print(f"   获取到 {len(memories)} 条记忆")
    for mem in memories[:3]:
        print(f"   - [{mem['agent']}] {mem['content']}")
    
    # 测试 3: 搜索记忆
    print("\n[测试 3] 搜索记忆...")
    results = store.search_memories("测试")
    print(f"   搜索结果：{len(results)} 条")
    for result in results:
        print(f"   - {result['content']}")
    
    # 测试 4: 创建任务
    print("\n[测试 4] 创建任务...")
    task_id = store.create_task(
        title="实现用户认证",
        description="添加登录和注册功能",
        assigned_to="builder",
        created_by="user"
    )
    print(f"   创建任务 #{task_id}")
    
    # 测试 5: 获取任务
    print("\n[测试 5] 获取任务...")
    tasks = store.get_tasks()
    print(f"   共 {len(tasks)} 个任务")
    for task in tasks:
        print(f"   - #{task['id']}: {task['title']} ({task['status']})")
    
    # 测试 6: 更新任务状态
    print("\n[测试 6] 更新任务状态...")
    store.update_task_status(task_id, "completed", "已完成")
    tasks = store.get_tasks()
    for task in tasks:
        if task['id'] == task_id:
            print(f"   任务 #{task_id} 状态：{task['status']}")
            print(f"   完成时间：{task['completed_at']}")
    
    # 测试 7: 保存 Agent 状态
    print("\n[测试 7] 保存 Agent 状态...")
    store.save_agent_state("builder", "idle", memory_count=5, completed_tasks=10)
    store.save_agent_state("reviewer", "busy", memory_count=3, completed_tasks=8)
    
    states = store.get_agent_states()
    print(f"   Agent 状态：")
    for state in states:
        print(f"   - {state['agent_name']}: {state['state']} (完成任务：{state['completed_tasks']})")
    
    # 测试 8: 统计信息
    print("\n[测试 8] 统计信息...")
    stats = store.get_stats()
    print(f"   总记忆数：{stats['total_memories']}")
    print(f"   任务状态：{stats['tasks']}")
    print(f"   活跃 Agent: {stats['active_agents']}")
    
    # 测试 9: 导出数据
    print("\n[测试 9] 导出数据...")
    export_file = Path.home() / ".ymcode" / "agents" / "export_test.json"
    store.export_data(str(export_file))
    print(f"   已导出：{export_file}")
    
    # 测试 10: 导入数据
    print("\n[测试 10] 导入数据...")
    store.import_data(str(export_file))
    print("   导入成功")
    
    print("\n" + "=" * 60)
    print("[OK] 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_memory_store()
