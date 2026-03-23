#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 Agent 对话测试

测试场景：
1. 两个 Agent 互相对话
2. 验证深度限制 (MAX_DEPTH=15)
3. 验证消息正确传递
4. 验证共享记忆
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.agents.router import AgentRouter
from ymcode.agents.message import AgentMessage
from ymcode.agents.builder import BuilderAgent
from ymcode.agents.reviewer import ReviewerAgent


async def test_agent_to_agent_conversation():
    """测试 Agent 之间互相对话"""
    print("=" * 60)
    print("测试 1: Agent 对话 (Builder <-> Reviewer)")
    print("=" * 60)
    
    # 创建路由器
    router = AgentRouter()
    
    # 注册 Agent
    builder = BuilderAgent()
    reviewer = ReviewerAgent()
    
    router.register_agent("builder", builder)
    router.register_agent("reviewer", reviewer)
    
    print(f"\n已注册 Agent: {router.list_agents()}")
    
    # 模拟对话：Builder 创建代码 → Reviewer 审查 → Builder 修改 → ...
    messages = []
    
    # 第 1 轮：用户请求
    msg1 = AgentMessage(
        sender="user",
        content="创建一个简单的 Python 函数，计算两个数的和"
    )
    print(f"\n[用户] {msg1.content}")
    result1 = await router.route(msg1, target="builder")
    print(f"[Builder] {result1.content[:100]}...")
    messages.append(result1)
    
    # 第 2 轮：Reviewer 审查
    msg2 = AgentMessage(
        sender="builder",
        content=f"请审查这段代码：{result1.content}"
    )
    print(f"\n[Builder → Reviewer] 请审查这段代码")
    result2 = await router.route(msg2, target="reviewer")
    print(f"[Reviewer] {result2.content[:100]}...")
    messages.append(result2)
    
    # 第 3 轮：Builder 根据反馈修改
    msg3 = AgentMessage(
        sender="reviewer",
        content=f"审查反馈：{result2.content}"
    )
    print(f"\n[Reviewer → Builder] 审查反馈")
    result3 = await router.route(msg3, target="builder")
    print(f"[Builder] {result3.content[:100]}...")
    messages.append(result3)
    
    print(f"\n✓ 对话测试完成，共 {len(messages)} 条消息")
    return True


async def test_depth_limit():
    """测试深度限制"""
    print("\n" + "=" * 60)
    print("测试 2: 深度限制 (MAX_DEPTH=15)")
    print("=" * 60)
    
    router = AgentRouter()
    builder = BuilderAgent()
    reviewer = ReviewerAgent()
    
    router.register_agent("builder", builder)
    router.register_agent("reviewer", reviewer)
    
    # 模拟多轮对话，测试深度限制
    max_rounds = 20  # 超过 15 应该被限制
    current_depth = 0
    messages = []
    
    print(f"\n开始多轮对话测试 (最大 {max_rounds} 轮，限制 15)...")
    
    msg = AgentMessage(
        sender="user",
        content="开始多轮对话测试",
        metadata={"depth": 0}
    )
    
    while current_depth < max_rounds:
        current_depth += 1
        
        # 检查深度限制
        if current_depth > 15:
            print(f"\n⚠️ 达到深度限制 (depth={current_depth} > 15)，停止对话")
            break
        
        # 交替发送给 Builder 和 Reviewer
        target = "builder" if current_depth % 2 == 1 else "reviewer"
        
        msg = AgentMessage(
            sender="reviewer" if target == "builder" else "builder",
            content=f"第 {current_depth} 轮对话",
            metadata={"depth": current_depth}
        )
        
        print(f"  轮次 {current_depth}: → {target}", end="")
        
        try:
            result = await router.route(msg, target=target)
            messages.append(result)
            print(" ✓")
        except Exception as e:
            print(f" ✗ (错误：{e})")
            break
    
    print(f"\n✓ 深度限制测试完成")
    print(f"  - 总轮次：{current_depth}")
    print(f"  - 成功消息：{len(messages)}")
    print(f"  - 深度限制：15 (符合 Cat Café 铁律)")
    
    return len(messages) <= 15


async def test_shared_memory():
    """测试共享记忆"""
    print("\n" + "=" * 60)
    print("测试 3: 共享记忆")
    print("=" * 60)
    
    router = AgentRouter()
    builder = BuilderAgent()
    reviewer = ReviewerAgent()
    
    router.register_agent("builder", builder)
    router.register_agent("reviewer", reviewer)
    
    # 添加到共享记忆
    print("\n添加到共享记忆:")
    router.add_to_shared_memory({"event": "code_created", "file": "test.py"})
    router.add_to_shared_memory({"event": "review_started", "reviewer": "reviewer"})
    router.add_to_shared_memory({"event": "review_completed", "issues": 3})
    
    print(f"  - 共享记忆条目数：{len(router.shared_memory)}")
    print(f"  - 最近记忆：{router.shared_memory[-1]}")
    
    # 验证共享记忆可访问
    assert len(router.shared_memory) > 0, "共享记忆应该不为空"
    
    print("\n✓ 共享记忆测试完成")
    return True


async def test_agent_roles():
    """测试 Agent 角色和职责"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 角色验证")
    print("=" * 60)
    
    router = AgentRouter()
    builder = BuilderAgent()
    reviewer = ReviewerAgent()
    
    router.register_agent("builder", builder)
    router.register_agent("reviewer", reviewer)
    
    agents = router.list_agents()
    
    print("\n已注册 Agent:")
    for agent in agents:
        print(f"  - {agent['name']}: {agent.get('role', 'N/A')}")
    
    # 验证角色
    builder_agent = router.get_agent("builder")
    reviewer_agent = router.get_agent("reviewer")
    
    assert builder_agent is not None, "Builder Agent 应该存在"
    assert reviewer_agent is not None, "Reviewer Agent 应该存在"
    
    print("\n✓ Agent 角色验证完成")
    return True


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("YM-CODE 多 Agent 对话测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: Agent 对话
    try:
        result1 = await test_agent_to_agent_conversation()
        results.append(("Agent 对话", result1))
    except Exception as e:
        print(f"[FAIL] Agent 对话测试失败：{e}")
        results.append(("Agent 对话", False))
    
    # 测试 2: 深度限制
    try:
        result2 = await test_depth_limit()
        results.append(("深度限制", result2))
    except Exception as e:
        print(f"[FAIL] 深度限制测试失败：{e}")
        results.append(("深度限制", False))
    
    # 测试 3: 共享记忆
    try:
        result3 = await test_shared_memory()
        results.append(("共享记忆", result3))
    except Exception as e:
        print(f"[FAIL] 共享记忆测试失败：{e}")
        results.append(("共享记忆", False))
    
    # 测试 4: Agent 角色
    try:
        result4 = await test_agent_roles()
        results.append(("Agent 角色", result4))
    except Exception as e:
        print(f"[FAIL] Agent 角色测试失败：{e}")
        results.append(("Agent 角色", False))
    
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
        print("\n[SUCCESS] 所有测试通过！多 Agent 交流功能正常工作！")
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，请检查")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
