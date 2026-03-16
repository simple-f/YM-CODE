#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队 CLI 命令
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..team import TeamManager, TaskManager, Role

console = Console()


@click.group()
def team():
    """团队管理命令"""
    pass


# ========== 团队成员管理 ==========

@team.command()
@click.argument('name')
@click.option('--user-id', required=True, help='用户 ID')
@click.option('--role', default='developer', type=click.Choice(['admin', 'developer', 'viewer', 'guest']))
def add_member(name, user_id, role):
    """添加团队成员"""
    team_mgr = TeamManager("default")
    
    member = team_mgr.add_member(user_id, name, Role(role))
    
    console.print(f"[green]✅ 成员已添加[/green]")
    console.print(f"   姓名：{member.name}")
    console.print(f"   角色：{member.role.value}")
    console.print(f"   权限：{', '.join(p.value for p in member.permissions)}")


@team.command()
@click.option('--role', help='按角色筛选')
def list_members(role):
    """列出团队成员"""
    team_mgr = TeamManager("default")
    
    if role:
        members = team_mgr.list_members(Role(role))
    else:
        members = team_mgr.list_members()
    
    if not members:
        console.print("[yellow]暂无成员[/yellow]")
        return
    
    table = Table(title="团队成员")
    table.add_column("姓名", style="cyan")
    table.add_column("用户 ID", style="dim")
    table.add_column("角色", style="green")
    table.add_column("加入时间", style="dim")
    
    for member in members:
        table.add_row(
            member.name,
            member.user_id,
            member.role.value,
            member.joined_at[:19] if member.joined_at else "-"
        )
    
    console.print(table)


@team.command()
@click.argument('user_id')
@click.argument('new_role', type=click.Choice(['admin', 'developer', 'viewer', 'guest']))
def update_role(user_id, new_role):
    """更新成员角色"""
    team_mgr = TeamManager("default")
    
    if team_mgr.update_role(user_id, Role(new_role)):
        console.print(f"[green]✅ 角色已更新[/green]")
        console.print(f"   用户：{user_id}")
        console.print(f"   新角色：{new_role}")
    else:
        console.print(f"[red]❌ 用户不存在[/red]")


@team.command()
@click.argument('user_id')
def remove_member(user_id):
    """移除成员"""
    team_mgr = TeamManager("default")
    
    if team_mgr.remove_member(user_id):
        console.print(f"[green]✅ 成员已移除[/green]")
    else:
        console.print(f"[red]❌ 用户不存在[/red]")


@team.command()
@click.argument('user_id')
def member_info(user_id):
    """查看成员信息"""
    team_mgr = TeamManager("default")
    
    member = team_mgr.get_member(user_id)
    
    if not member:
        console.print(f"[red]❌ 用户不存在[/red]")
        return
    
    console.print(Panel.fit(f"成员信息 - {member.name}", style="bold cyan"))
    
    console.print(f"[cyan]用户 ID:[/cyan] {member.user_id}")
    console.print(f"[cyan]角色:[/cyan] {member.role.value}")
    console.print(f"[cyan]权限:[/cyan] {', '.join(p.value for p in member.permissions)}")
    console.print(f"[cyan]加入时间:[/cyan] {member.joined_at[:19] if member.joined_at else 'N/A'}")
    console.print(f"[cyan]最后活跃:[/cyan] {member.last_active[:19] if member.last_active else 'N/A'}")


# ========== 任务管理 ==========

@team.group()
def task():
    """任务管理命令"""
    pass


@task.command()
@click.argument('title')
@click.option('--desc', default='', help='任务描述')
@click.option('--assign-to', help='分配给谁')
@click.option('--priority', default='normal', type=click.Choice(['low', 'normal', 'high', 'urgent']))
@click.option('--due', help='截止日期 (YYYY-MM-DD)')
@click.option('--tag', multiple=True, help='标签（可多次）')
def create(title, desc, assign_to, priority, due, tag):
    """创建任务"""
    task_mgr = TaskManager()
    
    task = task_mgr.create_task(
        title=title,
        description=desc,
        assigned_to=assign_to,
        created_by="current_user",
        priority=priority,
        due_date=due,
        tags=list(tag)
    )
    
    console.print(f"[green]✅ 任务已创建 #[/green][bold]{task.id}[/bold]")
    console.print(f"   标题：{task.title}")
    console.print(f"   优先级：{task.priority}")
    if task.assigned_to:
        console.print(f"   分配给：{task.assigned_to}")


@task.command()
@click.option('--status', help='按状态筛选')
@click.option('--assign-to', help='按分配用户筛选')
@click.option('--priority', help='按优先级筛选')
def list_tasks(status, assign_to, priority):
    """列出任务"""
    task_mgr = TaskManager()
    
    tasks = task_mgr.list_tasks(
        status=status,
        assigned_to=assign_to
    )
    
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    
    if not tasks:
        console.print("[yellow]暂无任务[/yellow]")
        return
    
    table = Table(title="任务列表")
    table.add_column("ID", style="cyan")
    table.add_column("标题", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("优先级", style="magenta")
    table.add_column("分配给", style="blue")
    table.add_column("截止日期", style="dim")
    
    for task in tasks[:20]:  # 限制显示 20 个
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }.get(task.status, "")
        
        priority_icon = {
            "low": "🔵",
            "normal": "🟢",
            "high": "🟡",
            "urgent": "🔴"
        }.get(task.priority, "")
        
        table.add_row(
            str(task.id),
            task.title[:30],
            f"{status_emoji} {task.status}",
            f"{priority_icon} {task.priority}",
            task.assigned_to or "-",
            task.due_date or "-"
        )
    
    console.print(table)


@task.command()
@click.argument('task_id', type=int)
def show(task_id):
    """查看任务详情"""
    task_mgr = TaskManager()
    
    task = task_mgr.get_task(task_id)
    
    if not task:
        console.print(f"[red]❌ 任务不存在[/red]")
        return
    
    console.print(Panel.fit(f"任务 #{task_id}", style="bold cyan"))
    
    console.print(f"[cyan]标题:[/cyan] {task.title}")
    console.print(f"[cyan]描述:[/cyan] {task.description or '无'}")
    console.print(f"[cyan]状态:[/cyan] {task.status}")
    console.print(f"[cyan]优先级:[/cyan] {task.priority}")
    console.print(f"[cyan]分配给:[/cyan] {task.assigned_to or '未分配'}")
    console.print(f"[cyan]创建者:[/cyan] {task.created_by or '未知'}")
    console.print(f"[cyan]创建时间:[/cyan] {task.created_at[:19]}")
    if task.due_date:
        console.print(f"[cyan]截止日期:[/cyan] {task.due_date}")
    if task.tags:
        console.print(f"[cyan]标签:[/cyan] {', '.join(task.tags)}")
    if task.comments:
        console.print(f"[cyan]评论:[/cyan] {len(task.comments)} 条")


@task.command()
@click.argument('task_id', type=int)
@click.argument('user_id')
def assign(task_id, user_id):
    """分配任务"""
    task_mgr = TaskManager()
    
    if task_mgr.assign_task(task_id, user_id):
        console.print(f"[green]✅ 任务已分配[/green]")
        console.print(f"   任务 #{task_id} → {user_id}")
    else:
        console.print(f"[red]❌ 任务不存在[/red]")


@task.command()
@click.argument('task_id', type=int)
@click.option('--result', help='完成结果说明')
def complete(task_id, result):
    """完成任务"""
    task_mgr = TaskManager()
    
    if task_mgr.complete_task(task_id, "current_user", result):
        console.print(f"[green]✅ 任务已完成[/green]")
        if result:
            console.print(f"   结果：{result}")
    else:
        console.print(f"[red]❌ 任务不存在[/red]")


@task.command()
@click.argument('task_id', type=int)
@click.argument('content')
def comment(task_id, content):
    """添加评论"""
    task_mgr = TaskManager()
    
    comment = task_mgr.add_comment(
        task_id,
        "current_user",
        "当前用户",
        content
    )
    
    if comment:
        console.print(f"[green]✅ 评论已添加[/green]")
        console.print(f"   评论 ID: {comment.id}")
    else:
        console.print(f"[red]❌ 任务不存在[/red]")


@task.command()
@click.argument('query')
def search(query):
    """搜索任务"""
    task_mgr = TaskManager()
    
    tasks = task_mgr.search_tasks(query)
    
    if not tasks:
        console.print(f"[yellow]未找到匹配 '{query}' 的任务[/yellow]")
        return
    
    console.print(Panel.fit(f"搜索结果：{query}", style="bold green"))
    console.print(f"找到 {len(tasks)} 个任务\n")
    
    for task in tasks[:10]:
        console.print(f"[cyan]#{task.id}[/cyan] {task.title}")
        console.print(f"   状态：{task.status} | 优先级：{task.priority}")
        console.print()


@task.command()
def stats():
    """查看任务统计"""
    task_mgr = TaskManager()
    
    stats = task_mgr.get_task_stats()
    
    console.print(Panel.fit("任务统计", style="bold magenta"))
    
    console.print(f"[cyan]总任务数:[/cyan] {stats['total']}")
    
    console.print(f"\n[cyan]按状态:[/cyan]")
    for status, count in stats['by_status'].items():
        console.print(f"  - {status}: {count}")
    
    console.print(f"\n[cyan]按优先级:[/cyan]")
    for priority, count in stats['by_priority'].items():
        console.print(f"  - {priority}: {count}")
    
    console.print(f"\n[cyan]按用户:[/cyan]")
    for user, count in stats['by_user'].items():
        console.print(f"  - {user}: {count} 个任务")


# ========== 主 CLI 集成 ==========

@click.group()
def cli():
    """YM-CODE CLI"""
    pass


cli.add_command(team)
cli.add_command(task)


if __name__ == '__main__':
    cli()
