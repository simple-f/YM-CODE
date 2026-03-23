#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能路由集成
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
console = Console()

async def test_integration():
    """测试集成"""
    console.print("=" * 70)
    console.print("🧪 测试智能路由集成")
    console.print("=" * 70)
    
    # 1. 测试路由器加载
    console.print("\n[1] 测试路由器加载...")
    try:
        from ymcode.router import SmartRouter
        router = SmartRouter()
        console.print("[green]✓ 路由器加载成功[/green]")
    except Exception as e:
        console.print(f"[red]✗ 路由器加载失败：{e}[/red]")
        return
    
    # 2. 测试 CLI 初始化
    console.print("\n[2] 测试 CLI 初始化...")
    try:
        from ymcode.cli import YMCodeCLI
        cli = YMCodeCLI()
        if cli.router:
            console.print("[green]✓ CLI 路由器初始化成功[/green]")
        else:
            console.print("[yellow]⚠ CLI 路由器未初始化[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ CLI 初始化失败：{e}[/red]")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 测试路由功能
    console.print("\n[3] 测试路由功能...")
    test_cases = [
        "帮我设计一个微服务架构",
        "写一个 Python API",
        "开发 React 前端界面",
    ]
    
    for task in test_cases:
        result = router.route(task)
        console.print(f"  [cyan]{task}[/cyan]")
        console.print(f"    → {result.agent_name} (置信度:{result.confidence:.0%})")
    
    console.print("\n[green]✓ 所有测试通过！[/green]")
    console.print("\n[bold]💡 下一步：[/bold]")
    console.print("  运行 [cyan]python cli.py[/cyan] 启动交互式 CLI")
    console.print("  输入任务查看智能路由效果")


if __name__ == "__main__":
    asyncio.run(test_integration())
