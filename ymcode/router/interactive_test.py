#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式路由测试

可以实时输入任务，查看路由效果
"""

import sys
import time
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.smart_router import SmartRouter


def print_result(result, router):
    """打印路由结果"""
    print("\n" + "=" * 70)
    print(f"🎯 路由结果")
    print("=" * 70)
    
    # Agent 信息
    print(f"\n👤 选定 Agent: {result.agent_name} ({result.selected_agent})")
    print(f"   角色：{router.get_agent_info(result.selected_agent)['role']}")
    print(f"   模型：{router.get_agent_info(result.selected_agent)['model']}")
    
    # 置信度和原因
    confidence_emoji = "🟢" if result.confidence > 0.7 else "🟡" if result.confidence > 0.4 else "🔴"
    print(f"\n{confidence_emoji} 置信度：{result.confidence:.0%}")
    print(f"💡 原因：{result.reason}")
    
    # 匹配关键词
    if result.matched_keywords:
        print(f"\n🔑 匹配关键词:")
        for kw in result.matched_keywords:
            print(f"   • {kw}")
    else:
        print(f"\n🔑 匹配关键词：无（使用默认路由）")
    
    # 响应时间
    print(f"\n⏱️  预计响应时间：{result.response_time_estimate}s")
    
    # 备选 Agent
    if result.alternative_agents:
        print(f"\n🔀 备选 Agent:")
        for aid in result.alternative_agents:
            info = router.get_agent_info(aid)
            if info:
                print(f"   • {info['name']} ({aid})")
    
    print("\n" + "=" * 70)


def interactive_test():
    """交互式测试"""
    router = SmartRouter()
    
    print("=" * 70)
    print("🧪 ymcode 智能路由 - 交互式测试")
    print("=" * 70)
    print("\n💡 使用说明:")
    print("  • 输入任务描述，按回车查看路由结果")
    print("  • 输入 'q' 或 'quit' 退出")
    print("  • 输入 'stats' 查看统计")
    print("  • 输入 'agents' 查看所有 Agent")
    print("  • 输入 'test' 运行批量测试")
    print("=" * 70)
    
    # 预定义测试用例
    test_cases = [
        "帮我设计一个电商系统的微服务架构",
        "用 Python 写一个 REST API 接口",
        "开发一个 React 前端管理后台",
        "审查这段代码的质量和问题",
        "产品需求文档应该包含什么",
        "技术方案选型：MongoDB vs PostgreSQL",
        "帮我修复这个 bug",
        "今天天气不错",
    ]
    
    while True:
        try:
            # 获取输入
            print("\n📝 请输入任务 (或输入 'test' 运行示例):")
            task = input("> ").strip()
            
            if not task:
                continue
            
            if task.lower() in ['q', 'quit', 'exit']:
                print("\n👋 拜拜！")
                break
            
            if task.lower() == 'stats':
                print("\n📊 当前统计:")
                for agent in router.get_all_agents():
                    stats = agent.get("stats", {})
                    if stats and stats.get("total_tasks", 0) > 0:
                        print(f"\n  {agent['name']} ({agent['id']})")
                        print(f"    任务数：{stats['total_tasks']}")
                        print(f"    准确率：{stats['accuracy_rate'] * 100:.1f}%")
                        print(f"    平均响应：{stats['avg_response_time']:.2f}s")
                continue
            
            if task.lower() == 'agents':
                print("\n👥 所有 Agent:")
                for agent in router.get_all_agents():
                    print(f"\n  {agent['name']} ({agent['id']})")
                    print(f"    角色：{agent['role']}")
                    print(f"    模型：{agent['model']}")
                    print(f"    专长：{', '.join(agent['strengths'])}")
                    print(f"    目标响应：{agent['target_response_time']}s")
                continue
            
            if task.lower() == 'test':
                print("\n🚀 运行批量测试...\n")
                for i, test_task in enumerate(test_cases, 1):
                    print(f"\n[{i}/8] 任务：{test_task}")
                    result = router.route(test_task)
                    print(f"  → 路由到：{result.agent_name}")
                    print(f"  → 置信度：{result.confidence:.0%}")
                    print(f"  → 关键词：{', '.join(result.matched_keywords) or '无'}")
                    
                    # 模拟记录结果
                    router.record_result(result.selected_agent, True, result.response_time_estimate * 0.8)
                
                print("\n✅ 批量测试完成！")
                continue
            
            # 路由任务
            print("\n⏳ 正在路由...")
            start_time = time.time()
            result = router.route(task)
            route_time = (time.time() - start_time) * 1000
            
            # 显示结果
            print_result(result, router)
            print(f"⚡ 路由耗时：{route_time:.2f}ms")
            
            # 询问是否模拟执行
            print("\n❓ 是否模拟执行并记录结果？(y/n)")
            choice = input("> ").strip().lower()
            
            if choice in ['y', 'yes', '']:
                print("\n🔄 模拟执行中...", end=" ")
                time.sleep(0.5)
                
                # 模拟成功
                success = True
                actual_time = result.response_time_estimate * 0.8
                router.record_result(result.selected_agent, success, actual_time)
                
                print(f"✅ 完成 (实际响应：{actual_time:.1f}s)")
                print(f"📊 结果已记录，影响下次路由决策")
        
        except KeyboardInterrupt:
            print("\n\n👋 中断退出")
            break
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    interactive_test()
