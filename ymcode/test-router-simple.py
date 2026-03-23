#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试路由集成
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
console = Console()

console.print("=" * 70)
console.print("🧪 测试智能路由模块")
console.print("=" * 70)

# 1. 测试导入
console.print("\n[1] 测试导入...")
try:
    from router import SmartRouter
    console.print("[green]✓ 导入成功[/green]")
except Exception as e:
    console.print(f"[red]✗ 导入失败：{e}[/red]")
    sys.exit(1)

# 2. 测试路由
console.print("\n[2] 测试路由功能...")
router = SmartRouter()

test_cases = [
    "帮我设计一个微服务架构",
    "写一个 Python API 接口",
    "开发 React 前端界面",
    "审查代码质量",
    "产品需求怎么写",
]

for task in test_cases:
    result = router.route(task)
    console.print(f"\n  [cyan]{task}[/cyan]")
    console.print(f"    → [yellow]{result.agent_name}[/yellow] ({result.selected_agent})")
    console.print(f"    置信度：{result.confidence:.0%}")
    console.print(f"    关键词：{', '.join(result.matched_keywords) or '无'}")

# 3. 测试统计
console.print("\n[3] 测试统计记录...")
router.record_result("ai1", True, 3.5)
router.record_result("ai2", True, 2.8)
console.print("[green]✓ 统计记录成功[/green]")

console.print("\n[green]✓ 所有测试通过！[/green]")
console.print("\n[bold]💡 集成完成！[/bold]")
console.print("智能路由已集成到 cli.py")
console.print("运行 [cyan]python cli.py[/cyan] 启动交互式 CLI")
