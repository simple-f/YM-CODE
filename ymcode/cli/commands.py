#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI 命令系统

支持 Agent 管理、工作空间管理
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..agents.identity import get_identity_manager, create_agent, switch_agent, get_current_agent, PERSONALITY_TEMPLATES
from ..workspace.manager import get_workspace_manager, create_workspace, switch_workspace, get_current_workspace

console = Console()


@click.group()
def agents():
    """Agent 管理命令"""
    pass


@agents.command('list')
def agents_list():
    """列出所有 Agent"""
    manager = get_identity_manager()
    identities = manager.list_identities()
    
    if not identities:
        console.print("[yellow]还没有创建任何 Agent[/yellow]")
        return
    
    table = Table(title="🎭 可用 Agent")
    table.add_column("Name", style="cyan")
    table.add_column("Codename", style="magenta")
    table.add_column("Personality", style="green")
    table.add_column("Avatar", style="yellow")
    table.add_column("Expertise", style="blue")
    
    for identity in identities:
        expertise = ", ".join(identity['expertise'][:3])
        table.add_row(
            identity['name'],
            identity['codename'],
            identity['personality'],
            identity['avatar_emoji'],
            expertise
        )
    
    console.print(table)


@agents.command('create')
@click.argument('name')
@click.option('--template', '-t', default=None, help='使用预设模板')
@click.option('--personality', '-p', default='friendly', help='人格类型')
def agents_create(name, template, personality):
    """创建新 Agent"""
    try:
        identity = create_agent(name, template=template, personality=personality)
        
        console.print()
        console.print(Panel(
            f"[bold green]✅ Agent 创建成功！[/bold green]\n\n"
            f"[cyan]Name:[/cyan] {identity.name}\n"
            f"[magenta]Codename:[/magenta] {identity.codename}\n"
            f"[green]Personality:[/green] {identity.personality}\n"
            f"[yellow]Avatar:[/yellow] {identity.avatar_emoji}\n\n"
            f"[dim]使用 `ym-code agents switch {name}` 切换到此 Agent[/dim]",
            title="🎉 创建成功",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]创建失败：{e}[/red]")


@agents.command('switch')
@click.argument('name')
def agents_switch(name):
    """切换当前 Agent"""
    if switch_agent(name):
        console.print(f"[green]✅ 已切换到 Agent: {name}[/green]")
    else:
        console.print(f"[red]❌ Agent 不存在：{name}[/red]")


@agents.command('show')
def agents_show():
    """显示当前 Agent"""
    agent = get_current_agent()
    
    if not agent:
        console.print("[yellow]当前没有激活的 Agent[/yellow]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold cyan]{agent.avatar_emoji} {agent.name}[/bold cyan]\n\n"
        f"[dim]Codename:[/dim] {agent.codename}\n"
        f"[dim]Personality:[/dim] {agent.personality}\n"
        f"[dim]Tone:[/dim] {agent.tone}\n"
        f"[dim]Expertise:[/dim] {', '.join(agent.expertise)}\n\n"
        f"[dim]{agent.quotes[0] if agent.quotes else ''}[/dim]",
        title="🎭 当前 Agent",
        border_style=agent.avatar_color
    ))


@agents.command('templates')
def agents_templates():
    """列出可用模板"""
    console.print("\n[bold]📋 可用 Agent 模板：[/bold]\n")
    
    for name, template in PERSONALITY_TEMPLATES.items():
        console.print(f"  {template.avatar_emoji} [cyan]{name}[/cyan] - {template.codename}")
        console.print(f"     [dim]{template.quotes[0] if template.quotes else ''}[/dim]\n")


@click.group()
def workspace():
    """工作空间管理命令"""
    pass


@workspace.command('list')
def workspace_list():
    """列出所有工作空间"""
    manager = get_workspace_manager()
    workspaces = manager.list_workspaces()
    
    if not workspaces:
        console.print("[yellow]还没有创建工作空间[/yellow]")
        return
    
    table = Table(title="📁 工作空间")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Agent", style="green")
    table.add_column("Description", style="yellow")
    table.add_column("Current", style="blue")
    
    for ws in workspaces:
        table.add_row(
            ws['name'],
            ws['type'],
            ws['agent'],
            ws['description'][:30] + "..." if len(ws['description']) > 30 else ws['description'],
            "✅" if ws['current'] else ""
        )
    
    console.print(table)


@workspace.command('create')
@click.argument('name')
@click.option('--description', '-d', default='', help='工作空间描述')
@click.option('--type', '-t', 'ws_type', default='default', help='工作空间类型')
@click.option('--agent', '-a', default=None, help='关联的 Agent')
@click.option('--copy-from', '-c', default=None, help='从现有工作空间复制')
def workspace_create(name, description, ws_type, agent, copy_from):
    """创建工作空间"""
    try:
        ws = create_workspace(
            name,
            description=description,
            type=ws_type,
            agent_identity=agent,
            copy_from=copy_from
        )
        
        console.print()
        console.print(Panel(
            f"[bold green]✅ 工作空间创建成功！[/bold green]\n\n"
            f"[cyan]Name:[/cyan] {ws.name}\n"
            f"[magenta]Type:[/magenta] {ws.type}\n"
            f"[green]Path:[/green] {ws.path}\n"
            f"[yellow]Agent:[/yellow] {ws.agent_identity}\n\n"
            f"[dim]使用 `ym-code workspace switch {name}` 切换到此工作空间[/dim]",
            title="🎉 创建成功",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]创建失败：{e}[/red]")


@workspace.command('switch')
@click.argument('name')
def workspace_switch(name):
    """切换工作空间"""
    if switch_workspace(name):
        console.print(f"[green]✅ 已切换到工作空间：{name}[/green]")
    else:
        console.print(f"[red]❌ 工作空间不存在：{name}[/red]")


@workspace.command('show')
def workspace_show():
    """显示当前工作空间"""
    ws = get_current_workspace()
    
    if not ws:
        console.print("[yellow]当前没有激活的工作空间[/yellow]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold cyan]📁 {ws.name}[/bold cyan]\n\n"
        f"[dim]Type:[/dim] {ws.type}\n"
        f"[dim]Description:[/dim] {ws.description}\n"
        f"[dim]Agent:[/dim] {ws.agent_identity}\n"
        f"[dim]Path:[/dim] {ws.path}\n"
        f"[dim]Created:[/dim] {ws.created_at}",
        title="📁 当前工作空间",
        border_style="blue"
    ))


@workspace.command('delete')
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='强制删除（不确认）')
def workspace_delete(name, force):
    """删除工作空间"""
    if name == 'default':
        console.print("[red]❌ 不能删除默认工作空间[/red]")
        return
    
    if not force:
        click.confirm(f"确定要删除工作空间 '{name}' 吗？此操作不可恢复！", abort=True)
    
    manager = get_workspace_manager()
    if manager.delete_workspace(name):
        console.print(f"[green]✅ 工作空间已删除：{name}[/green]")
    else:
        console.print(f"[red]❌ 删除失败：{name}[/red]")


# 主 CLI 命令集成
@click.group()
def cli():
    """YM-CODE CLI"""
    pass


cli.add_command(agents)
cli.add_command(workspace)


if __name__ == '__main__':
    cli()
