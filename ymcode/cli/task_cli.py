#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI - 任务管理命令

提供任务队列管理功能
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime

from ..taskqueue import TaskQueue, Task, TaskStatus, TaskPriority

console = Console()


@click.group()
def task():
    """任务管理命令"""
    pass


@task.command('list')
@click.option('--status', '-s', type=click.Choice(['pending', 'queued', 'running', 'completed', 'failed']), help='按状态筛�?)
@click.option('--assigned-to', '-a', type=str, help='按执�?Agent 筛�?)
@click.option('--limit', '-l', type=int, default=20, help='返回数量限制')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
def task_list(status, assigned_to, limit, storage):
    """列出任务"""
    queue = TaskQueue(storage_path=storage)
    
    # 转换状态枚�?    status_enum = None
    if status:
        status_enum = TaskStatus(status)
    
    tasks = queue.list_tasks(status=status_enum, assigned_to=assigned_to, limit=limit)
    
    if not tasks:
        console.print("[yellow]没有找到任务[/yellow]")
        return
    
    table = Table(title=f"📋 任务列表 (共{len(tasks)}�?", box=box.ROUNDED)
    table.add_column("ID", style="cyan", max_width=36)
    table.add_column("标题", style="white")
    table.add_column("状�?, style="green")
    table.add_column("优先�?, style="yellow")
    table.add_column("执行�?, style="blue")
    table.add_column("创建时间", style="magenta")
    
    for task in tasks:
        # 状态图�?        status_icons = {
            TaskStatus.PENDING: "�?,
            TaskStatus.QUEUED: "📥",
            TaskStatus.RUNNING: "🔄",
            TaskStatus.COMPLETED: "�?,
            TaskStatus.FAILED: "�?,
            TaskStatus.CANCELLED: "🚫"
        }
        status_str = f"{status_icons.get(task.status, '')} {task.status.value}"
        
        # 优先级图�?        priority_icons = {
            TaskPriority.LOW: "🔵",
            TaskPriority.NORMAL: "🟢",
            TaskPriority.HIGH: "🟡",
            TaskPriority.URGENT: "🔴"
        }
        priority_str = f"{priority_icons.get(task.priority, '')} {task.priority.name}"
        
        table.add_row(
            task.id[:8] + "...",
            task.title[:30] + "..." if len(task.title) > 30 else task.title,
            status_str,
            priority_str,
            task.assigned_to or "-",
            task.created_at.strftime("%m-%d %H:%M")
        )
    
    console.print(table)


@task.command('create')
@click.argument('title')
@click.option('--description', '-d', type=str, default="", help='任务描述')
@click.option('--priority', '-p', type=click.Choice(['LOW', 'NORMAL', 'HIGH', 'URGENT']), default='NORMAL', help='优先�?)
@click.option('--assigned-to', '-a', type=str, help='分配给的 Agent')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
def task_create(title, description, priority, assigned_to, storage):
    """创建新任�?""
    queue = TaskQueue(storage_path=storage)
    
    # 创建任务
    task = Task(
        title=title,
        description=description,
        priority=TaskPriority[priority],
        assigned_to=assigned_to
    )
    
    # 入队
    task_id = queue.enqueue(task)
    
    console.print(f"[green]�?任务已创建[/green]")
    console.print(Panel(
        f"[bold]ID:[/bold] {task_id}\n"
        f"[bold]标题:[/bold] {title}\n"
        f"[bold]优先�?[/bold] {priority}\n"
        f"[bold]执行�?[/bold] {assigned_to or '未分�?}",
        title="📝 任务详情",
        box=box.ROUNDED
    ))


@task.command('status')
@click.argument('task_id')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
def task_status(task_id, storage):
    """查看任务状�?""
    queue = TaskQueue(storage_path=storage)
    
    task = queue.get_task(task_id)
    if not task:
        console.print(f"[red]�?任务不存在：{task_id}[/red]")
        return
    
    # 状态图�?    status_icons = {
        TaskStatus.PENDING: "�?等待�?,
        TaskStatus.QUEUED: "📥 已入�?,
        TaskStatus.RUNNING: "🔄 运行�?,
        TaskStatus.COMPLETED: "�?已完�?,
        TaskStatus.FAILED: "�?失败",
        TaskStatus.CANCELLED: "🚫 已取�?
    }
    
    console.print(Panel(
        f"[bold]ID:[/bold] {task.id}\n"
        f"[bold]标题:[/bold] {task.title}\n"
        f"[bold]描述:[/bold] {task.description or '-'}\n"
        f"[bold]状�?[/bold] {status_icons.get(task.status, task.status.value)}\n"
        f"[bold]优先�?[/bold] {task.priority.name}\n"
        f"[bold]执行�?[/bold] {task.assigned_to or '未分�?}\n"
        f"[bold]创建时间:[/bold] {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"[bold]更新时间:[/bold] {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"[bold]重试次数:[/bold] {task.retry_count}/{task.max_retries}" +
        (f"\n[bold]错误:[/bold] {task.error}" if task.error else ""),
        title="📊 任务详情",
        box=box.ROUNDED
    ))


@task.command('cancel')
@click.argument('task_id')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
@click.option('--yes', '-y', is_flag=True, help='确认取消')
def task_cancel(task_id, storage, yes):
    """取消任务"""
    queue = TaskQueue(storage_path=storage)
    
    task = queue.get_task(task_id)
    if not task:
        console.print(f"[red]�?任务不存在：{task_id}[/red]")
        return
    
    if not yes:
        click.confirm(f"确定要取消任�?'{task.title}' 吗？", abort=True)
    
    success = queue.cancel_task(task_id)
    if success:
        console.print(f"[green]�?任务已取消：{task_id}[/green]")
    else:
        console.print(f"[red]�?取消失败[/red]")


@task.command('retry')
@click.argument('task_id')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
def task_retry(task_id, storage):
    """重试失败的任�?""
    queue = TaskQueue(storage_path=storage)
    
    task = queue.get_task(task_id)
    if not task:
        console.print(f"[red]�?任务不存在：{task_id}[/red]")
        return
    
    if task.status != TaskStatus.FAILED:
        console.print(f"[yellow]⚠️ 任务未失败，当前状态：{task.status.value}[/yellow]")
        return
    
    success = queue.retry_task(task_id)
    if success:
        console.print(f"[green]�?任务已重试：{task_id}[/green]")
    else:
        console.print(f"[red]�?重试失败[/red]")


@task.command('stats')
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
def task_stats(storage):
    """查看任务统计"""
    queue = TaskQueue(storage_path=storage)
    stats = queue.get_stats()
    
    console.print(Panel(
        f"[bold]📥 总入队数:[/bold] {stats['total_enqueued']}\n"
        f"[bold]📤 总出队数:[/bold] {stats['total_dequeued']}\n"
        f"[bold]�?已完�?[/bold] {stats['total_completed']}\n"
        f"[bold]�?已失�?[/bold] {stats['total_failed']}\n"
        f"[bold]🔄 已重�?[/bold] {stats['total_retried']}\n"
        f"[bold]📊 队列�?[/bold] {stats['queue_size']}\n"
        f"[bold]🔄 运行�?[/bold] {stats['running_count']}\n"
        f"[bold]💀 死信队列:[/bold] {stats['dead_letter_count']}",
        title="📈 任务统计",
        box=box.ROUNDED
    ))


@task.command('clear')
@click.option('--dead-letter', is_flag=True, help='只清空死信队�?)
@click.option('--storage', type=str, default=None, help='任务队列存储路径')
@click.option('--yes', '-y', is_flag=True, help='确认清空')
def task_clear(dead_letter, storage, yes):
    """清空任务队列"""
    queue = TaskQueue(storage_path=storage)
    
    if dead_letter:
        if not yes:
            click.confirm("确定要清空死信队列吗�?, abort=True)
        count = queue.clear_dead_letter()
        console.print(f"[green]�?已清�?{count} 个死信任务[/green]")
    else:
        console.print("[red]⚠️ 警告：此操作将删除所有任务！[/red]")
        if not yes:
            click.confirm("确定要继续吗�?, abort=True)
        console.print("[yellow]功能开发中...[/yellow]")
