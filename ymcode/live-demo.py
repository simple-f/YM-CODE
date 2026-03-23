#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时演示 - 展示智能路由效果
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from router.smart_router import SmartRouter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def live_demo():
    router = SmartRouter()
    
    console.print()
    console.print(Panel.fit(
        "[bold blue]🎯 ymcode 智能路由 - 实时演示[/bold blue]\n"
        "[dim]展示真实任务的路由决策过程和性能[/dim]",
        border_style="blue"
    ))
    console.print()
    
    # 真实场景测试
    test_cases = [
        "帮我设计一个电商系统的微服务架构，支持高并发",
        "用 Python 写一个 REST API，连接 MySQL 数据库",
        "开发一个 React 管理后台，包含数据可视化图表",
        "审查这段代码，看看有什么潜在问题",
        "产品需求文档应该包含哪些内容",
    ]
    
    console.print(f"📋 测试任务数：{len(test_cases)}\n")
    
    total_route_time = 0
    results = []
    
    for i, task in enumerate(test_cases, 1):
        console.print(f"[bold cyan]任务 {i}/{len(test_cases)}[/bold cyan]")
        console.print(f"[dim]任务内容：[/dim] {task}")
        console.print()
        
        # 路由决策
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_widget = progress.add_task("[cyan]正在路由...", total=None)
            
            start_time = time.time()
            result = router.route(task)
            route_time = (time.time() - start_time) * 1000
            total_route_time += route_time
            
            progress.update(task_widget, description=f"[green]路由完成！{route_time:.2f}ms[/green]")
        
        # 显示路由结果
        console.print()
        
        # 置信度表情
        if result.confidence > 0.7:
            emoji = "🟢"
        elif result.confidence > 0.4:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        console.print(f"[bold]🎯 路由结果:[/bold]")
        console.print(f"  [bold]选定 Agent:[/bold] [cyan]{result.agent_name}[/cyan] ({result.selected_agent})")
        console.print(f"  [bold]置信度:[/bold] {emoji} {result.confidence:.0%}")
        console.print(f"  [bold]预计响应:[/bold] {result.response_time_estimate}s")
        console.print(f"  [bold]路由耗时:[/bold] [green]{route_time:.2f}ms[/green]")
        
        if result.matched_keywords:
            console.print(f"  [bold]匹配关键词:[/bold] {', '.join(result.matched_keywords)}")
        
        if result.alternative_agents:
            alt_names = [router.get_agent_info(aid)["name"] for aid in result.alternative_agents if router.get_agent_info(aid)]
            if alt_names:
                console.print(f"  [bold]备选 Agent:[/bold] {', '.join(alt_names)}")
        
        console.print()
        console.print("-" * 70)
        console.print()
        
        # 保存结果
        results.append({
            "task": task,
            "agent": result.agent_name,
            "confidence": result.confidence,
            "time": route_time
        })
    
    # 统计汇总
    console.print()
    console.print(Panel.fit(
        "[bold green]📊 测试汇总[/bold green]",
        border_style="green"
    ))
    console.print()
    
    # 创建表格
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("任务", width=40)
    table.add_column("Agent", width=10)
    table.add_column("置信度", width=10)
    table.add_column("耗时 (ms)", width=10)
    
    for i, r in enumerate(results, 1):
        emoji = "🟢" if r["confidence"] > 0.7 else "🟡" if r["confidence"] > 0.4 else "🔴"
        table.add_row(
            str(i),
            r["task"][:38] + "..." if len(r["task"]) > 40 else r["task"],
            r["agent"],
            f"{emoji} {r['confidence']:.0%}",
            f"[green]{r['time']:.2f}[/green]"
        )
    
    console.print(table)
    
    # 性能统计
    console.print()
    avg_time = total_route_time / len(results)
    console.print(f"[bold]⚡ 性能统计:[/bold]")
    console.print(f"  总路由耗时：[green]{total_route_time:.2f}ms[/green]")
    console.print(f"  平均路由耗时：[green]{avg_time:.2f}ms[/green]")
    console.print(f"  最快路由：[green]{min(r['time'] for r in results):.2f}ms[/green]")
    console.print(f"  最慢路由：[green]{max(r['time'] for r in results):.2f}ms[/green]")
    
    console.print()
    console.print(f"[bold]🎯 平均置信度：[/bold] {sum(r['confidence'] for r in results) / len(results) * 100:.0f}%")
    
    console.print()
    console.print("[bold green]✅ 演示完成！智能路由系统运行正常！[/bold green]")
    console.print()


if __name__ == "__main__":
    live_demo()
