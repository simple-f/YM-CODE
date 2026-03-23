#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI - 指标管理命令

提供系统指标查看功能
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime, timedelta

from ..metrics import MetricsCollector

console = Console()


@click.group()
def metrics():
    """指标管理命令"""
    pass


@metrics.command('system')
@click.option('--hours', '-h', type=int, default=1, help='查看最近 N 小时的数据')
@click.option('--storage', type=str, default=None, help='指标存储路径')
def metrics_system(hours, storage):
    """查看系统指标"""
    collector = MetricsCollector(storage_path=storage)
    dashboard = collector.get_dashboard()
    system = dashboard['system']
    
    console.print(Panel(
        f"[bold]📊 总任务数:[/bold] {system.get('total_tasks', 0)}\n"
        f"[bold]✅ 已完成:[/bold] {system.get('completed_tasks', 0)}\n"
        f"[bold]❌ 已失败:[/bold] {system.get('failed_tasks', 0)}\n"
        f"[bold]🤖 活跃 Agent:[/bold] {system.get('active_agents', 0)}\n"
        f"[bold]📥 队列大小:[/bold] {system.get('queue_size', 0)}\n"
        f"[bold]⏱️ 平均响应:[/bold] {system.get('avg_response_time', {}).get('avg', 0):.2f}s",
        title="🖥️ 系统指标",
        box=box.ROUNDED
    ))


@metrics.command('agent')
@click.argument('agent_id')
@click.option('--hours', '-h', type=int, default=1, help='查看最近 N 小时的数据')
@click.option('--storage', type=str, default=None, help='指标存储路径')
def metrics_agent(agent_id, hours, storage):
    """查看 Agent 指标"""
    collector = MetricsCollector(storage_path=storage)
    agent_metrics = collector.get_agent_metrics(agent_id)
    
    exec_time = agent_metrics.get('avg_execution_time', {})
    
    console.print(Panel(
        f"[bold]✅ 完成任务:[/bold] {agent_metrics.get('tasks_completed', 0)}\n"
        f"[bold]❌ 失败任务:[/bold] {agent_metrics.get('tasks_failed', 0)}\n"
        f"[bold]⏱️ 平均执行:[/bold] {exec_time.get('avg', 0):.2f}s\n"
        f"[bold]📊 执行次数:[/bold] {exec_time.get('count', 0)}\n"
        f"[bold]⚡ 最快:[/bold] {exec_time.get('min', 0):.2f}s\n"
        f"[bold]🐢 最慢:[/bold] {exec_time.get('max', 0):.2f}s",
        title=f"🤖 Agent 指标：{agent_id}",
        box=box.ROUNDED
    ))


@metrics.command('list')
@click.option('--pattern', '-p', type=str, default="*", help='指标名称模式（支持 * 通配符）')
@click.option('--hours', '-h', type=int, default=1, help='查看最近 N 小时的数据')
@click.option('--limit', '-l', type=int, default=50, help='返回数量限制')
@click.option('--storage', type=str, default=None, help='指标存储路径')
def metrics_list(pattern, hours, limit, storage):
    """列出指标"""
    collector = MetricsCollector(storage_path=storage)
    metrics = collector.get_metrics(pattern, hours=hours)
    
    if not metrics:
        console.print("[yellow]没有找到指标数据[/yellow]")
        return
    
    table = Table(title=f"📊 指标列表 (最近{hours}小时)", box=box.ROUNDED)
    table.add_column("指标名称", style="cyan")
    table.add_column("值", style="green")
    table.add_column("时间", style="magenta")
    table.add_column("标签", style="yellow")
    
    for metric in metrics[-limit:]:
        labels_str = ", ".join(f"{k}={v}" for k, v in metric.labels.items()) if metric.labels else "-"
        table.add_row(
            metric.name,
            f"{metric.value:.2f}",
            metric.timestamp.strftime("%H:%M:%S"),
            labels_str[:30] + "..." if len(labels_str) > 30 else labels_str
        )
    
    console.print(table)


@metrics.command('counter')
@click.argument('name')
@click.option('--storage', type=str, default=None, help='指标存储路径')
def metrics_counter(name, storage):
    """查看计数器值"""
    collector = MetricsCollector(storage_path=storage)
    value = collector.get_counter(name)
    
    console.print(f"[bold]{name}[/bold] = [green]{value}[/green]")


@metrics.command('histogram')
@click.argument('name')
@click.option('--labels', '-l', type=str, help='标签（格式：key1=value1,key2=value2）')
@click.option('--storage', type=str, default=None, help='指标存储路径')
def metrics_histogram(name, labels, storage):
    """查看直方图统计"""
    collector = MetricsCollector(storage_path=storage)
    
    # 解析标签
    label_dict = {}
    if labels:
        for pair in labels.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                label_dict[k.strip()] = v.strip()
    
    stats = collector.get_histogram_stats(name, label_dict if label_dict else None)
    
    console.print(Panel(
        f"[bold]📊 总数:[/bold] {stats['count']}\n"
        f"[bold]∑ 总和:[/bold] {stats['sum']:.2f}\n"
        f"[bold]📈 平均:[/bold] {stats['avg']:.2f}\n"
        f"[bold]⚡ 最小:[/bold] {stats['min']:.2f}\n"
        f"[bold]🐢 最大:[/bold] {stats['max']:.2f}\n"
        f"[bold]📊 P50:[/bold] {stats['p50']:.2f}\n"
        f"[bold]📊 P90:[/bold] {stats['p90']:.2f}\n"
        f"[bold]📊 P99:[/bold] {stats['p99']:.2f}",
        title=f"📉 直方图统计：{name}",
        box=box.ROUNDED
    ))


@metrics.command('clear')
@click.option('--older-than', type=int, help='清理早于 N 小时的数据')
@click.option('--storage', type=str, default=None, help='指标存储路径')
@click.option('--yes', '-y', is_flag=True, help='确认清理')
def metrics_clear(older_than, storage, yes):
    """清理指标数据"""
    collector = MetricsCollector(storage_path=storage)
    
    if not yes:
        click.confirm(f"确定要清理{older_than or '所有'}指标数据吗？", abort=True)
    
    collector.clear_old_data(older_than)
    console.print("[green]✅ 清理完成[/green]")
