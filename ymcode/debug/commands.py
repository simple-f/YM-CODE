#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试系统 CLI 命令
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .tracer import get_tracer
from .profiler import get_profiler

console = Console()


@click.group()
def debug():
    """调试系统命令"""
    pass


# ========== 追踪命令 ==========

@debug.group()
def trace():
    """执行追踪命令"""
    pass


@trace.command('start')
@click.option('--filter', '-f', multiple=True, help='过滤的目标')
def trace_start(filter):
    """开始追踪"""
    tracer = get_tracer()
    tracer.enable(filters=list(filter))
    
    session_id = tracer.current_session
    console.print(f"[green]✅ 追踪已启动[/green]")
    console.print(f"Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"[dim]使用 `ym-code debug trace stop` 停止追踪[/dim]")


@trace.command('stop')
def trace_stop():
    """停止追踪"""
    tracer = get_tracer()
    session_id = tracer.stop_session()
    
    if session_id:
        console.print(f"[green]✅ 追踪已停止[/green]")
        console.print(f"Session ID: [cyan]{session_id}[/cyan]")
        console.print(f"Events: {len(tracer.get_session(session_id).events)}")
    else:
        console.print("[yellow]⚠️ 当前没有活跃的追踪[/yellow]")


@trace.command('status')
def trace_status():
    """查看追踪状态"""
    tracer = get_tracer()
    
    if tracer.enabled and tracer.current_session:
        session = tracer.get_session(tracer.current_session)
        console.print()
        console.print(Panel(
            f"[bold green]✅ 追踪进行中[/bold green]\n\n"
            f"[cyan]Session:[/cyan] {tracer.current_session}\n"
            f"[cyan]Events:[/cyan] {len(session.events)}\n"
            f"[cyan]Duration:[/cyan] {session.duration():.2f}s",
            title="📊 追踪状态",
            border_style="green"
        ))
    else:
        console.print("[yellow]⚠️ 追踪未启用[/yellow]")


@trace.command('list')
def trace_list():
    """列出追踪会话"""
    tracer = get_tracer()
    sessions = tracer.list_sessions()
    
    if not sessions:
        console.print("[yellow]还没有追踪会话[/yellow]")
        return
    
    table = Table(title="📋 追踪会话")
    table.add_column("Session ID", style="cyan")
    table.add_column("Start Time", style="magenta")
    table.add_column("Duration", style="green")
    table.add_column("Events", style="yellow")
    
    for session in sessions[-10:]:  # 最近 10 个
        table.add_row(
            session['id'][:8] + "...",
            session['start_time'].split('T')[1][:8],
            f"{session['duration']:.2f}s",
            str(session['event_count'])
        )
    
    console.print(table)


@trace.command('show')
@click.argument('session_id')
def trace_show(session_id):
    """查看追踪详情"""
    tracer = get_tracer()
    session = tracer.get_session(session_id)
    
    if not session:
        console.print(f"[red]❌ 会话不存在：{session_id}[/red]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold cyan]Session:[/bold cyan] {session.id}\n"
        f"[bold cyan]Duration:[/bold cyan] {session.duration():.2f}s\n"
        f"[bold cyan]Events:[/bold cyan] {len(session.events)}",
        title="📊 追踪详情",
        border_style="cyan"
    ))
    
    # 显示最近事件
    console.print("\n[bold]最近事件：[/bold]\n")
    
    for event in session.events[-10:]:
        emoji = {
            'call': '📞',
            'return': '✅',
            'error': '❌',
            'log': '📝'
        }.get(event.event_type, '📌')
        
        console.print(
            f"{emoji} [{event.timestamp.split('T')[1][:8]}] "
            f"[cyan]{event.event_type}[/cyan] "
            f"{event.target}"
        )
        
        if event.duration_ms > 0:
            console.print(f"   [dim]Duration: {event.duration_ms:.2f}ms[/dim]")


@trace.command('replay')
@click.argument('session_id')
def trace_replay(session_id):
    """回放追踪会话"""
    tracer = get_tracer()
    
    try:
        events = tracer.replay_session(session_id)
        
        console.print(f"\n[bold]回放会话：{session_id}[/bold]\n")
        
        for event in events:
            emoji = {
                'call': '📞',
                'return': '✅',
                'error': '❌'
            }.get(event.event_type, '📌')
            
            console.print(
                f"{emoji} [{event.timestamp.split('T')[1][:8]}] "
                f"[cyan]{event.event_type}[/cyan] "
                f"{event.target}"
            )
            
            if event.args:
                console.print(f"   [dim]Args: {str(event.args)[:100]}[/dim]")
            if event.result:
                console.print(f"   [dim]Result: {str(event.result)[:100]}[/dim]")
            if event.error:
                console.print(f"   [red]Error: {event.error}[/red]")
    
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")


@trace.command('stats')
@click.argument('session_id')
def trace_stats(session_id):
    """查看追踪统计"""
    tracer = get_tracer()
    stats = tracer.get_statistics(session_id)
    
    if not stats:
        console.print(f"[red]❌ 会话不存在：{session_id}[/red]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold]Session:[/bold] {stats['session_id']}\n"
        f"[bold]Duration:[/bold] {stats['duration']:.2f}s\n"
        f"[bold]Total Events:[/bold] {stats['total_events']}\n"
        f"[bold]Errors:[/bold] {stats['error_count']}",
        title="📊 追踪统计",
        border_style="yellow"
    ))
    
    # 显示目标统计
    if stats['targets']:
        console.print("\n[bold]目标统计：[/bold]\n")
        
        table = Table()
        table.add_column("Target", style="cyan")
        table.add_column("Calls", style="yellow")
        table.add_column("Avg Time", style="green")
        table.add_column("Errors", style="red")
        
        for target, target_stats in sorted(
            stats['targets'].items(),
            key=lambda x: x[1]['call_count'],
            reverse=True
        )[:10]:
            table.add_row(
                target,
                str(target_stats['call_count']),
                f"{target_stats.get('avg_duration_ms', 0):.2f}ms",
                str(target_stats['error_count'])
            )
        
        console.print(table)


@trace.command('export')
@click.argument('session_id')
@click.option('--format', '-f', type=click.Choice(['json', 'text']), default='json')
@click.option('--output', '-o', help='输出文件路径')
def trace_export(session_id, format, output):
    """导出追踪会话"""
    tracer = get_tracer()
    
    try:
        content = tracer.export_session(session_id, format=format)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]✅ 已导出到：{output}[/green]")
        else:
            console.print(content)
    
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")


# ========== 性能分析命令 ==========

@debug.group()
def profile():
    """性能分析命令"""
    pass


@profile.command('report')
@click.argument('profile_id')
@click.option('--format', '-f', type=click.Choice(['text', 'html', 'json']), default='text')
@click.option('--output', '-o', help='输出文件路径')
def profile_report(profile_id, format, output):
    """生成性能报告"""
    profiler = get_profiler()
    
    try:
        if output:
            profiler.export_report(profile_id, output)
            console.print(f"[green]✅ 报告已导出到：{output}[/green]")
        else:
            report = profiler.generate_report(profile_id, format=format)
            console.print(report)
    
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")


@profile.command('list')
def profile_list():
    """列出性能分析结果"""
    profiler = get_profiler()
    results = profiler.list_results()
    
    if not results:
        console.print("[yellow]还没有性能分析结果[/yellow]")
        return
    
    table = Table(title="📊 性能分析结果")
    table.add_column("ID", style="cyan")
    table.add_column("Start Time", style="magenta")
    table.add_column("Duration", style="green")
    table.add_column("Calls", style="yellow")
    
    for result in results[-10:]:
        table.add_row(
            result['id'][:8] + "...",
            result['start_time'].split('T')[1][:8],
            f"{result['duration']:.3f}s",
            str(result['call_count'])
        )
    
    console.print(table)


@profile.command('compare')
@click.argument('profile_ids', nargs=-1)
def profile_compare(profile_ids):
    """比较性能分析结果"""
    profiler = get_profiler()
    
    if len(profile_ids) < 2:
        console.print("[red]❌ 至少需要 2 个分析结果[/red]")
        return
    
    try:
        comparison = profiler.compare(list(profile_ids))
        
        console.print()
        console.print(Panel(
            f"[bold]比较结果：[/bold]\n\n"
            f"Duration 差异：{comparison['duration_diff']:+.3f}s\n"
            f"Call Count 差异：{comparison['call_count_diff']:+d}",
            title="📊 性能比较",
            border_style="cyan"
        ))
    
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")


# 主 CLI 集成
@click.group()
def cli():
    """YM-CODE Debug CLI"""
    pass


cli.add_command(debug)


if __name__ == '__main__':
    cli()
