#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由器测试
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.smart_router import SmartRouter


def test_router():
    """测试路由器"""
    router = SmartRouter()
    
    test_cases = [
        ("帮我设计一个微服务架构", "ai1"),
        ("写一个 Python API，连接数据库", "ai2"),
        {"task": "开发一个 React 前端界面", "expected": "ai3"},
        {"task": "审查这段代码的质量", "expected": "ai5"},
        {"task": "产品需求文档怎么写", "expected": "ai7"},
        {"task": "技术方案选型建议", "expected": "ai6"},
        {"task": "帮我修复这个 bug", "expected": "ai4"},
        {"task": "今天天气怎么样", "expected": "ai4"},  # 默认路由
    ]
    
    print("=" * 60)
    print("🧪 智能路由器测试")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        if isinstance(case, tuple):
            task, expected = case
        else:
            task = case["task"]
            expected = case["expected"]
        
        result = router.route(task)
        success = result.selected_agent == expected
        
        if success:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"
        
        print(f"\n测试 {i}: {status}")
        print(f"  任务：{task}")
        print(f"  期望：{expected}")
        print(f"  实际：{result.selected_agent} ({result.agent_name})")
        print(f"  置信度：{result.confidence:.2f}")
        print(f"  匹配关键词：{result.matched_keywords}")
        print(f"  原因：{result.reason}")
    
    print("\n" + "=" * 60)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print(f"通过率：{passed / len(test_cases) * 100:.1f}%")
    print("=" * 60)
    
    # 显示所有 Agent 信息
    print("\n📊 Agent 能力概览:")
    print("=" * 60)
    for agent in router.get_all_agents():
        stats = agent.get("stats", {})
        agent_id = agent.get("id", "unknown")
        print(f"\n{agent['name']} ({agent_id})")
        print(f"  角色：{agent['role']}")
        print(f"  模型：{agent['model']}")
        print(f"  专长：{', '.join(agent['strengths'])}")
        print(f"  目标响应时间：{agent['target_response_time']}s")
        if stats:
            print(f"  历史任务：{stats.get('total_tasks', 0)}")
            print(f"  准确率：{stats.get('accuracy_rate', 0.95) * 100:.1f}%")
            print(f"  平均响应：{stats.get('avg_response_time', 0):.2f}s")


if __name__ == "__main__":
    test_router()
