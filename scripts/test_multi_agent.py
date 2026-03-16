#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多 Agent 系统
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.agents import create_default_router, AgentMessage


async def test_multi_agent():
    """测试多 Agent 系统"""
    print("=" * 60)
    print("YM-CODE 多 Agent 系统测试")
    print("=" * 60)
    
    # 创建路由器
    router = create_default_router()
    
    print("\n[OK] Agent 已初始化")
    print(f"   可用 Agent: {list(router.agents.keys())}")
    
    # 测试 1: 查看 Agent 状态
    print("\n[测试 1] 查看 Agent 状态...")
    agents = router.list_agents()
    for agent in agents:
        print(f"   - {agent['name']}: {agent['role']} ({agent['state']})")
    
    # 测试 2: Builder 创建文件
    print("\n[测试 2] Builder 创建文件...")
    msg = AgentMessage(
        sender="user",
        content="创建文件 test.py，写入 print('hello')"
    )
    response = await router.route(msg)
    print(f"   发送：{msg.content}")
    print(f"   回复：{response.content}")
    print(f"   发送者：{response.sender}")
    
    # 测试 3: Reviewer 审查代码
    print("\n[测试 3] Reviewer 审查代码...")
    msg = AgentMessage(
        sender="user",
        content="审查 src/main.py 的代码质量"
    )
    response = await router.route(msg)
    print(f"   发送：{msg.content[:30]}...")
    print(f"   回复：{response.content[:100]}...")
    print(f"   发送者：{response.sender}")
    
    # 测试 4: 自动路由
    print("\n[测试 4] 自动路由测试...")
    test_cases = [
        "实现用户登录功能",
        "分析这个文件的复杂度",
        "运行测试",
    ]
    
    for task in test_cases:
        msg = AgentMessage(sender="user", content=task)
        response = await router.route(msg)
        print(f"   任务：{task[:20]}... → Agent: {response.sender}")
    
    # 测试 5: 共享记忆
    print("\n[测试 5] 共享记忆测试...")
    router.add_to_shared_memory({
        "type": "note",
        "content": "项目使用 Python 3.13"
    })
    router.add_to_shared_memory({
        "type": "note",
        "content": "测试框架是 pytest"
    })
    
    memories = router.get_shared_memory(limit=5)
    print(f"   共享记忆数量：{len(memories)}")
    for mem in memories:
        print(f"   - {mem['content']}")
    
    # 测试 6: 搜索记忆
    print("\n[测试 6] 搜索记忆...")
    results = router.search_shared_memory("pytest")
    print(f"   搜索结果：{len(results)} 条")
    for result in results:
        print(f"   - {result['content']}")
    
    # 最终状态
    print("\n" + "=" * 60)
    print("最终状态")
    print("=" * 60)
    agents = router.list_agents()
    for agent in agents:
        print(f"\n{agent['name']} ({agent['role']}):")
        print(f"  状态：{agent['state']}")
        print(f"  记忆：{agent['memory_count']} 条")
        if 'completed_tasks' in agent:
            print(f"  完成任务：{agent['completed_tasks']}")
        if 'reviewed_tasks' in agent:
            print(f"  审查任务：{agent['reviewed_tasks']}")
    
    print("\n[OK] 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_multi_agent())
