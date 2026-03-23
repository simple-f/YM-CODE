#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量路由测试 - 展示真实任务的路由效果
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from router.smart_router import SmartRouter


def main():
    router = SmartRouter()
    
    print("=" * 70)
    print("🧪 ymcode 智能路由 - 批量测试")
    print("=" * 70)
    
    # 真实场景测试用例
    test_cases = [
        # 架构类
        ("帮我设计一个电商系统的微服务架构，支持高并发", "ai1"),
        ("技术选型：用 MongoDB 还是 PostgreSQL？", "ai1"),
        ("系统性能瓶颈怎么分析", "ai6"),
        
        # 后端类
        ("用 Python 写一个 REST API，连接 MySQL 数据库", "ai2"),
        ("设计一个用户认证系统，支持 JWT 和 OAuth2", "ai2"),
        ("Redis 缓存策略怎么设计", "ai2"),
        
        # 前端类
        ("开发一个 React 管理后台，包含数据可视化图表", "ai3"),
        ("Vue3 + TypeScript 项目怎么配置", "ai3"),
        ("移动端适配方案有哪些", "ai3"),
        
        # 测试类
        ("审查这段代码，看看有什么潜在问题", "ai5"),
        ("怎么写单元测试", "ai5"),
        ("代码质量怎么保证", "ai5"),
        
        # 产品类
        ("产品需求文档应该包含哪些内容", "ai7"),
        ("用户体验怎么优化", "ai7"),
        ("功能优先级怎么排", "ai7"),
        
        # 全栈类
        ("帮我修复这个 bug，程序运行时崩溃了", "ai4"),
        ("快速实现一个 MVP 原型", "ai4"),
        ("部署到 AWS 需要什么配置", "ai4"),
        
        # 日常对话（默认路由）
        ("今天天气不错", "ai4"),
        ("你好", "ai4"),
    ]
    
    print(f"\n📋 测试用例数：{len(test_cases)}")
    print(f"🎯 测试目标：验证路由准确率\n")
    
    passed = 0
    failed = 0
    total_time = 0
    
    for i, (task, expected) in enumerate(test_cases, 1):
        # 路由
        start = time.time()
        result = router.route(task)
        route_time = (time.time() - start) * 1000
        total_time += route_time
        
        # 判断
        success = result.selected_agent == expected
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        # 显示
        print(f"{i:2d}. {status} {task[:40]:<40} → {result.agent_name:<8} (置信度:{result.confidence:.0%})")
        
        if not success:
            print(f"    期望：{expected}, 实际：{result.selected_agent}")
            print(f"    关键词：{result.matched_keywords}")
    
    # 统计
    print("\n" + "=" * 70)
    print(f"📊 测试结果")
    print("=" * 70)
    print(f"✅ 通过：{passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print(f"❌ 失败：{failed}/{len(test_cases)} ({failed/len(test_cases)*100:.1f}%)")
    print(f"⚡ 平均路由耗时：{total_time/len(test_cases):.2f}ms")
    print("=" * 70)
    
    if passed/len(test_cases) >= 0.9:
        print("\n🎉 测试通过！路由准确率达到 90% 以上")
        print("\n💡 建议：可以集成到 ymcode 主流程")
    else:
        print("\n⚠️  准确率未达标，需要优化关键词映射")
    
    return passed/len(test_cases) >= 0.9


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
