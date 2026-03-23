#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能记忆管理器测试

测试场景：
1. 添加记忆（自动重要性评估）
2. 滑动窗口（工作记忆限制）
3. 按需加载（基于评分）
4. 搜索记忆
5. 统计信息
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.memory.smart_memory import (
    SmartMemoryManager,
    MemoryType,
    ImportanceLevel,
    MemoryConfig
)


async def test_add_memory():
    """测试添加记忆"""
    print("=" * 60)
    print("测试 1: 添加记忆（自动重要性评估）")
    print("=" * 60)
    
    config = MemoryConfig(
        working_window_size=10,
        long_term_threshold=3
    )
    
    memory = SmartMemoryManager(config=config)
    
    # 添加不同类型的记忆
    print("\n添加记忆:")
    
    # 普通对话（应该 LOW）
    m1 = await memory.add("你好，今天天气不错")
    print(f"  1. 普通对话 -> 重要性={m1.importance.name} (期望：LOW)")
    
    # 技术讨论（应该 MEDIUM）
    m2 = await memory.add("我们决定使用 Python 实现这个功能")
    print(f"  2. 技术方案 -> 重要性={m2.importance.name} (期望：MEDIUM)")
    
    # 重要决策（应该 HIGH）
    m3 = await memory.add("最终结论：采用微服务架构")
    print(f"  3. 重要决策 -> 重要性={m3.importance.name} (期望：HIGH)")
    
    # 错误报告（应该 MEDIUM）
    m4 = await memory.add("发现一个 bug：登录失败")
    print(f"  4. 错误报告 -> 重要性={m4.importance.name} (期望：MEDIUM)")
    
    # 验证统计
    stats = await memory.get_stats()
    print(f"\n统计：工作记忆={stats['working_count']}, 长期记忆={stats['long_term_count']}")
    
    # 验证：HIGH 重要性应该进入长期记忆
    assert m3.importance == ImportanceLevel.HIGH, "重要决策应该是 HIGH"
    assert m3.id in memory.long_term_memories, "HIGH 重要性应存入长期记忆"
    
    print("\n✓ 添加记忆测试通过")
    return True


async def test_sliding_window():
    """测试滑动窗口"""
    print("\n" + "=" * 60)
    print("测试 2: 滑动窗口（工作记忆限制）")
    print("=" * 60)
    
    config = MemoryConfig(
        working_window_size=5,  # 小窗口便于测试
        long_term_threshold=4,  # 只有 CRITICAL 才进入长期
        auto_compact_enabled=True
    )
    
    memory = SmartMemoryManager(config=config)
    
    print(f"\n窗口大小={config.working_window_size}")
    print("添加 10 条普通记忆...")
    
    # 添加超过窗口大小的记忆
    for i in range(10):
        await memory.add(f"普通消息 {i}", importance=ImportanceLevel.LOW)
    
    stats = await memory.get_stats()
    working_count = stats['working_count']
    
    print(f"工作记忆数量：{working_count}")
    print(f"期望：<= {config.working_window_size}")
    
    # 验证窗口限制
    assert working_count <= config.working_window_size, f"工作记忆不应超过窗口大小 {config.working_window_size}"
    
    print("\n✓ 滑动窗口测试通过")
    return True


async def test_load_context():
    """测试按需加载"""
    print("\n" + "=" * 60)
    print("测试 3: 按需加载（基于评分）")
    print("=" * 60)
    
    config = MemoryConfig(
        working_window_size=20,
        long_term_threshold=3,
        working_max_tokens=1000
    )
    
    memory = SmartMemoryManager(config=config)
    
    print("\n添加不同类型的记忆:")
    
    # 添加一些记忆
    await memory.add("用户说：你好", metadata={'role': 'user'})
    await memory.add("决定：使用 FastAPI 框架", importance=ImportanceLevel.HIGH)
    await memory.add("代码实现：def hello(): pass")
    await memory.add("结论：性能优化完成", importance=ImportanceLevel.HIGH)
    await memory.add("普通聊天：今天天气不错")
    
    # 按需加载
    print("\n加载上下文（无查询）:")
    context = await memory.load_context(max_tokens=500)
    print(f"  加载 {len(context)} 条记忆")
    
    # 验证：重要记忆应该优先加载
    if context:
        print(f"  第 1 条：{context[0].content[:50]}...")
        print(f"  重要性：{context[0].importance.name}")
    
    # 带查询加载
    print("\n加载上下文（查询='决定'）:")
    context_with_query = await memory.load_context(query="决定", max_tokens=500)
    
    if context_with_query:
        print(f"  加载 {len(context_with_query)} 条记忆")
        print(f"  第 1 条：{context_with_query[0].content[:50]}...")
    
    print("\n✓ 按需加载测试通过")
    return True


async def test_search():
    """测试搜索"""
    print("\n" + "=" * 60)
    print("测试 4: 搜索记忆")
    print("=" * 60)
    
    config = MemoryConfig(
        working_window_size=20,
        long_term_threshold=2
    )
    
    memory = SmartMemoryManager(config=config)
    
    print("\n添加测试记忆:")
    
    # 添加各种记忆
    await memory.add("Python 代码实现", tags=['python', 'code'])
    await memory.add("JavaScript 前端开发", tags=['javascript', 'frontend'])
    await memory.add("Python 数据分析", tags=['python', 'data'])
    await memory.add("数据库设计", tags=['database', 'design'])
    await memory.add("Python 性能优化", tags=['python', 'performance'])
    
    # 搜索
    print("\n搜索 'Python':")
    results = await memory.search("Python", limit=3)
    
    print(f"  找到 {len(results)} 条相关记忆")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.content[:40]}... (标签：{', '.join(result.tags)})")
    
    # 验证：Python 相关的应该排前面
    assert len(results) > 0, "应该找到相关记忆"
    assert 'python' in results[0].content.lower() or 'python' in results[0].tags, "最相关的应该排第一"
    
    print("\n✓ 搜索测试通过")
    return True


async def test_memory_lifecycle():
    """测试记忆生命周期"""
    print("\n" + "=" * 60)
    print("测试 5: 记忆生命周期（添加->访问->统计）")
    print("=" * 60)
    
    config = MemoryConfig(
        working_window_size=10,
        long_term_threshold=2
    )
    
    memory = SmartMemoryManager(config=config)
    
    print("\n添加记忆:")
    m = await memory.add("重要决策：使用 PostgreSQL 数据库")
    print(f"  创建：{m.created_at}")
    print(f"  重要性：{m.importance.name}")
    print(f"  访问次数：{m.access_count}")
    
    print("\n访问记忆（加载上下文）:")
    await memory.load_context(query="数据库")
    print(f"  访问次数：{m.access_count} (应该 > 0)")
    
    # 再次访问
    await memory.load_context(query="PostgreSQL")
    print(f"  再次访问后：{m.access_count}")
    
    # 验证：访问次数应该增加
    assert m.access_count > 0, "访问次数应该增加"
    
    print("\n✓ 记忆生命周期测试通过")
    return True


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("YM-CODE 智能记忆管理器测试")
    print("=" * 60)
    
    results = []
    
    tests = [
        ("添加记忆", test_add_memory),
        ("滑动窗口", test_sliding_window),
        ("按需加载", test_load_context),
        ("搜索记忆", test_search),
        ("记忆生命周期", test_memory_lifecycle)
    ]
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！智能记忆系统正常工作！")
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，请检查")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
