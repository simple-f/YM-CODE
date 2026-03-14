#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent CLI 命令
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..agents import create_default_router, AgentMessage
from ..agents.memory_store import MemoryStore

console = Console()


@click.group()
def agent():
    """Agent 管理命令"""
    pass


@agent.command()
def status():
    """查看 Agent 状态"""
    router = create_default_router()
    
    agents = router.list_agents()
    
    table = Table(title="Agent 状态")
    table.add_column("名称", style="cyan")
    table.add_column("角色", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("记忆", style="blue")
    table.add_column("完成任务", style="magenta")
    
    for agent_info in agents:
        completed = agent_info.get('completed_tasks', 'N/A')
        table.add_row(
            agent_info["name"],
            agent_info["role"],
            agent_info["state"],
            str(agent_info.get("memory_count", 0)),
            str(completed)
        )
    
    console.print(table)


@agent.command()
@click.option('--limit', default=10, help='显示数量')
def memory(limit):
    """查看共享记忆"""
    router = create_default_router()
    
    memories = router.get_shared_memory(limit=limit)
    
    if not memories:
        console.print("[yellow]暂无共享记忆[/yellow]")
        return
    
    console.print(Panel.fit(f"共享记忆 (最近 {limit} 条)", style="bold magenta"))
    
    for mem in memories:
        content = mem.get('content', 'N/A')
        mem_type = mem.get('type', 'note')
        console.print(f"[cyan]•[/cyan] [{mem_type}] {content}")


@agent.command()
@click.option('--limit', default=10, help='显示数量')
def tasks(limit):
    """查看任务列表"""
    store = MemoryStore()
    
    tasks = store.get_tasks()
    
    if not tasks:
        console.print("[yellow]暂无任务[/yellow]")
        return
    
    table = Table(title="任务列表")
    table.add_column("ID", style="cyan")
    table.add_column("标题", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("分配给", style="blue")
    table.add_column("完成时间", style="dim")
    
    for task in tasks[:limit]:
        completed_at = task.get('completed_at', '-')
        if completed_at and completed_at != 'None':
            completed_at = completed_at[:19]  # 截断时间
        
        table.add_row(
            str(task["id"]),
            task["title"],
            task["status"],
            task.get("assigned_to", "-"),
            completed_at
        )
    
    console.print(table)


@agent.command()
@click.argument('title')
@click.option('--assign-to', default=None, help='分配给哪个 Agent')
def create(title, assign_to):
    """创建新任务"""
    store = MemoryStore()
    
    task_id = store.create_task(
        title=title,
        assigned_to=assign_to
    )
    
    console.print(f"[green]✅ 任务已创建 #[/green][bold]{task_id}[/bold]")
    console.print(f"   标题：{title}")
    if assign_to:
        console.print(f"   分配给：{assign_to}")


@agent.command()
@click.argument('task_id', type=int)
@click.option('--result', default=None, help='任务结果')
def complete(task_id, result):
    """完成任务"""
    store = MemoryStore()
    
    store.update_task_status(task_id, "completed", result)
    
    console.print(f"[green]✅ 任务 #{task_id} 已完成[/green]")
    if result:
        console.print(f"   结果：{result}")


@agent.command()
@click.argument('query')
@click.option('--limit', default=10, help='显示数量')
def search(query, limit):
    """搜索记忆"""
    store = MemoryStore()
    
    results = store.search_memories(query, limit=limit)
    
    if not results:
        console.print(f"[yellow]未找到匹配 '{query}' 的记忆[/yellow]")
        return
    
    console.print(Panel.fit(f"搜索结果：{query}", style="bold cyan"))
    
    for mem in results:
        console.print(f"[cyan]•[/cyan] [{mem['agent']}] {mem['content']}")


@agent.command()
def stats():
    """查看统计信息"""
    store = MemoryStore()
    
    stats = store.get_stats()
    
    console.print(Panel.fit("统计信息", style="bold green"))
    
    console.print(f"[cyan]总记忆数:[/cyan] {stats.get('total_memories', 0)}")
    
    tasks = stats.get('tasks', {})
    console.print(f"[cyan]任务状态:[/cyan]")
    for status, count in tasks.items():
        console.print(f"  - {status}: {count}")
    
    console.print(f"[cyan]活跃 Agent:[/cyan] {stats.get('active_agents', 0)}")


@agent.command()
@click.option('--output', default='backup.json', help='导出文件路径')
def export(output):
    """导出数据"""
    store = MemoryStore()
    
    store.export_data(output)
    
    console.print(f"[green]✅ 数据已导出到[/green] [bold]{output}[/bold]")


@agent.command()
@click.argument('input_file')
@click.option('--clear', is_flag=True, help='导入前清空现有数据')
def import_data(input_file, clear):
    """导入数据"""
    store = MemoryStore()
    
    try:
        store.import_data(input_file, clear_existing=clear)
        console.print(f"[green]✅ 数据已从[/green] [bold]{input_file}[/bold] [green]导入[/green]")
    except Exception as e:
        console.print(f"[red]❌ 导入失败：{e}[/red]")


@agent.command()
def clean():
    """清理旧数据"""
    store = MemoryStore()
    
    deleted = store.clear_old_memories(days=30)
    
    console.print(f"[green]✅ 已清理[/green] [bold]{deleted}[/bold] [green]条旧记忆（>30 天）[/green]")


# 主 CLI 集成
@click.group()
def cli():
    """YM-CODE CLI"""
    pass


cli.add_command(agent)


if __name__ == '__main__':
    cli()
