#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力测试 - 更多真实场景
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.smart_router import SmartRouter
from rich.console import Console

console = Console()

def stress_test():
    router = SmartRouter()
    
    console.print("=" * 70)
    console.print("🧪 智能路由 - 压力测试（扩展场景）")
    console.print("=" * 70)
    
    # 扩展测试用例（30 个真实场景）
    test_cases = [
        # 架构类
        ("设计一个高并发电商系统", "ai1"),
        ("微服务架构怎么拆分", "ai1"),
        ("技术选型：MySQL vs PostgreSQL", "ai1"),
        ("系统架构文档怎么写", "ai1"),
        
        # 后端类
        ("Python 写个 API 接口", "ai2"),
        ("数据库表怎么设计", "ai2"),
        ("Redis 缓存怎么用", "ai2"),
        ("JWT 认证怎么实现", "ai2"),
        
        # 前端类
        ("React 项目初始化", "ai3"),
        ("Vue3 组件怎么写", "ai3"),
        ("CSS 布局优化", "ai3"),
        ("移动端适配方案", "ai3"),
        
        # 测试类
        ("代码审查要点", "ai5"),
        ("单元测试怎么写", "ai5"),
        ("测试覆盖率怎么提升", "ai5"),
        ("Bug 怎么定位", "ai5"),
        
        # 产品类
        ("产品需求文档模板", "ai7"),
        ("用户体验怎么优化", "ai7"),
        ("功能优先级怎么排", "ai7"),
        ("用户反馈怎么处理", "ai7"),
        
        # 全栈类
        ("快速实现 MVP", "ai4"),
        ("项目部署到 AWS", "ai4"),
        ("Docker 容器化", "ai4"),
        ("CI/CD 流程配置", "ai4"),
        
        # 顾问类
        ("性能瓶颈怎么分析", "ai6"),
        ("技术债务怎么处理", "ai6"),
        ("最佳实践有哪些", "ai6"),
        ("技术趋势怎么看", "ai6"),
        
        # 日常对话
        ("你好", "ai4"),
        ("在吗", "ai4"),
        ("今天天气不错", "ai4"),
    ]
    
    console.print(f"\n📋 测试用例数：{len(test_cases)}")
    console.print(f"🎯 测试目标：验证复杂场景下的路由准确率\n")
    
    passed = 0
    failed = 0
    
    for i, (task, expected) in enumerate(test_cases, 1):
        result = router.route(task)
        success = result.selected_agent == expected
        
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        console.print(f"{i:2d}. {status} {task:<35} → {result.agent_name:<8} (置信度:{result.confidence:.0%})")
        
        if not success:
            console.print(f"    期望：{expected}, 实际：{result.selected_agent}")
            console.print(f"    关键词：{result.matched_keywords}")
    
    # 统计
    console.print("\n" + "=" * 70)
    console.print(f"📊 测试结果")
    console.print("=" * 70)
    console.print(f"✅ 通过：{passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    console.print(f"❌ 失败：{failed}/{len(test_cases)} ({failed/len(test_cases)*100:.1f}%)")
    console.print("=" * 70)
    
    if passed/len(test_cases) >= 0.95:
        console.print("\n🎉 压力测试通过！准确率 ≥95%")
        return True
    else:
        console.print("\n⚠️  准确率未达标，需要继续优化")
        return False


if __name__ == "__main__":
    success = stress_test()
    sys.exit(0 if success else 1)
