#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由演示

展示如何集成到 ymcode 主流程
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from router.smart_router import SmartRouter


def demo_routing():
    """演示路由功能"""
    router = SmartRouter()
    
    print("=" * 70)
    print("🎯 ymcode 智能路由演示")
    print("=" * 70)
    
    # 模拟用户任务
    tasks = [
        "帮我设计一个电商系统的微服务架构，需要支持高并发",
        "用 Python 写一个 REST API，连接 MySQL 数据库",
        "开发一个 React 管理后台，包含数据可视化图表",
        "审查这段代码，看看有什么潜在问题",
        "产品需求文档应该包含哪些内容",
        "帮我修复这个 bug，程序运行时崩溃了",
        "技术方案选型：用 MongoDB 还是 PostgreSQL？",
        "今天天气不错",  # 无明确意图
    ]
    
    print("\n📝 模拟用户任务处理:\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"任务 {i}: {task}")
        print("-" * 70)
        
        # 路由决策
        start_time = time.time()
        result = router.route(task)
        route_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 显示路由信息
        print(f"  🎯 路由到：{result.agent_name} ({result.selected_agent})")
        print(f"  📊 置信度：{result.confidence:.0%}")
        print(f"  ⏱️  预计响应：{result.response_time_estimate}s")
        print(f"  🔍 匹配关键词：{', '.join(result.matched_keywords) or '无'}")
        print(f"  💡 原因：{result.reason}")
        print(f"  ⚡ 路由耗时：{route_time:.2f}ms")
        
        if result.alternative_agents:
            alt_names = [router.get_agent_info(aid)["name"] for aid in result.alternative_agents if router.get_agent_info(aid)]
            print(f"  🔀 备选：{', '.join(alt_names)}")
        
        # 模拟执行并记录结果
        print(f"\n  🔄 执行中...", end=" ")
        time.sleep(0.5)  # 模拟处理时间
        
        # 模拟成功
        success = True
        actual_response_time = result.response_time_estimate * 0.8  # 模拟实际响应
        router.record_result(result.selected_agent, success, actual_response_time)
        
        print(f"✅ 完成 (实际响应：{actual_response_time:.1f}s)")
        print()
    
    # 显示统计
    print("\n" + "=" * 70)
    print("📊 Agent 使用统计")
    print("=" * 70)
    
    for agent in router.get_all_agents():
        stats = agent.get("stats", {})
        if stats and stats.get("total_tasks", 0) > 0:
            print(f"\n{agent['name']} ({agent['id']})")
            print(f"  处理任务：{stats['total_tasks']}")
            print(f"  准确率：{stats['accuracy_rate'] * 100:.1f}%")
            print(f"  平均响应：{stats['avg_response_time']:.2f}s")
    
    print("\n" + "=" * 70)
    print("✨ 演示完成！")
    print("=" * 70)
    
    print("\n💡 集成建议:")
    print("  1. 在 ymcode/cli.py 的 handle_task 方法中添加路由")
    print("  2. 在 Agent 执行前后调用 record_result 记录统计")
    print("  3. 在 Hub 界面展示 router.get_all_agents() 返回的能力信息")
    print("  4. 定期清理 router_stats.json 保持性能")


if __name__ == "__main__":
    demo_routing()
