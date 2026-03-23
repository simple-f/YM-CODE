#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 主 CLI 入口

使用方法:
    ym-code --help
    ym-code task list
    ym-code metrics system
"""

import click
from rich.console import Console
from rich.panel import Panel

from .commands import agents, workspace
from .task_cli import task
from .metrics_cli import metrics

console = Console()


@click.group()
@click.version_option(version='1.0.0', prog_name='ym-code')
def cli():
    """
    🤖 YM-CODE - AI Programming Assistant
    
    多 Agent 协作系统，支持任务管理、指标监控、事件追踪等功能。
    """
    pass


# 注册子命令
cli.add_command(agents, 'agents')
cli.add_command(workspace, 'workspace')
cli.add_command(task, 'task')
cli.add_command(metrics, 'metrics')


@cli.command()
def hello():
    """测试命令"""
    console.print(Panel(
        "[bold green]👋 Hello from YM-CODE![/bold green]\n\n"
        "使用 [cyan]`ym-code --help`[/cyan] 查看所有命令\n"
        "使用 [cyan]`ym-code task --help`[/cyan] 查看任务命令\n"
        "使用 [cyan]`ym-code metrics --help`[/cyan] 查看指标命令",
        title="🎉 欢迎使用 YM-CODE",
        box="double"
    ))


def main():
    """CLI 入口函数"""
    cli()


if __name__ == '__main__':
    main()
