#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced CLI Components - 增强的 CLI 组件
"""

import sys
from typing import Optional, List, Dict
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.live import Live
from rich.layout import Layout

IS_WINDOWS = sys.platform == 'win32'

# Emoji 映射（Windows 上用文字替代）
EMOJI = {
    'robot': '[BOT]',
    'check': '[OK]',
    'cross': '[ERR]',
    'warning': '[WARN]',
    'info': '[INFO]',
    'sparkle': '[*]',
    'fire': '[~]',
    'clock': '[TIME]',
    'target': '[TARGET]',
    'lightning': '[!]',
    'package': '[PKG]',
    'tools': '[TOOLS]',
}


class TaskPanel:
    """任务面板 - 显示当前任务状态"""
    
    def __init__(self, console: Optional[Console] = None):
        # Windows 上强制使用兼容模式
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
        self.task_name = ""
        self.start_time = None
        self.status = "pending"  # pending, running, completed, failed
    
    def start(self, task_name: str) -> None:
        """开始任务"""
        self.task_name = task_name
        self.start_time = datetime.now()
        self.status = "running"
        
        panel = Panel(
            Text(f"{task_name}", style="bold white"),
            title=f"{EMOJI['target']} 任务进行中",
            border_style="yellow",
            subtitle=f"开始：{self.start_time.strftime('%H:%M:%S')}",
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()
    
    def complete(self, success: bool = True, message: str = "") -> None:
        """完成任务"""
        duration = ""
        if self.start_time:
            delta = datetime.now() - self.start_time
            duration = f"耗时：{delta.total_seconds():.1f}秒"
        
        self.status = "completed" if success else "failed"
        
        if success:
            panel = Panel(
                Text(f"{message or '任务完成'}", style="bold green"),
                title=f"{EMOJI['check']} 成功",
                border_style="green",
                subtitle=duration,
                box=box.ROUNDED
            )
        else:
            panel = Panel(
                Text(f"{message or '任务失败'}", style="bold red"),
                title=f"{EMOJI['cross']} 失败",
                border_style="red",
                subtitle=duration,
                box=box.ROUNDED
            )
        
        self.console.print(panel)
        self.console.print()
    
    def error(self, error: str, suggestion: str = "") -> None:
        """显示错误"""
        full_message = error
        if suggestion:
            full_message += f"\n\n[dim]建议：{suggestion}[/dim]"
        
        panel = Panel(
            Text(full_message, style="white"),
            title=f"{EMOJI['warning']} 错误",
            border_style="red",
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()


class EnhancedProgress:
    """增强的进度条"""
    
    def __init__(self, console: Optional[Console] = None):
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
    
    def create(self, description: str = "处理中...", total: float = 100) -> Progress:
        """创建进度条"""
        return Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            refresh_per_second=10
        )
    
    def show_stages(self, stages: List[Dict]) -> None:
        """显示多阶段进度"""
        with self.create() as progress:
            for i, stage in enumerate(stages):
                task = progress.add_task(
                    f"[cyan]阶段 {i+1}/{len(stages)}: {stage['name']}",
                    total=100
                )
                
                # 模拟进度
                for percent in range(0, 101, 20):
                    progress.update(task, completed=percent)
                    import time
                    time.sleep(0.1)
                
                progress.remove_task(task)


class InfoBox:
    """信息框 - 显示各类信息"""
    
    def __init__(self, console: Optional[Console] = None):
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
    
    def success(self, title: str, message: str) -> None:
        """成功信息"""
        panel = Panel(
            Text(message, style="white"),
            title=f"{EMOJI['check']} {title}",
            border_style="green",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def error(self, title: str, message: str, suggestion: str = "") -> None:
        """错误信息"""
        full_message = message
        if suggestion:
            full_message += f"\n\n[dim]{suggestion}[/dim]"
        
        panel = Panel(
            Text(full_message, style="white"),
            title=f"{EMOJI['cross']} {title}",
            border_style="red",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def warning(self, title: str, message: str) -> None:
        """警告信息"""
        panel = Panel(
            Text(message, style="white"),
            title=f"{EMOJI['warning']} {title}",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def info(self, title: str, message: str) -> None:
        """普通信息"""
        panel = Panel(
            Text(message, style="white"),
            title=f"{EMOJI['info']} {title}",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)


class StatsTable:
    """统计表格"""
    
    def __init__(self, console: Optional[Console] = None):
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
    
    def show(self, title: str, data: Dict[str, str]) -> None:
        """显示统计表格"""
        table = Table(
            title=f"{EMOJI['sparkle']} {title}",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=False,
            padding=(0, 2)
        )
        
        table.add_column("Key", style="cyan", width=20)
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            table.add_row(key, value)
        
        self.console.print(table)
        self.console.print()


class CommandHelp:
    """命令帮助"""
    
    def __init__(self, console: Optional[Console] = None):
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
    
    def show(self, commands: Dict[str, str]) -> None:
        """显示命令帮助"""
        table = Table(
            title=f"{EMOJI['info']} 可用命令",
            box=box.ROUNDED,
            border_style="green",
            show_header=True,
            padding=(0, 2)
        )
        
        table.add_column("命令", style="bold yellow", width=15)
        table.add_column("说明", style="white")
        
        for cmd, desc in commands.items():
            table.add_row(cmd, desc)
        
        self.console.print(table)
        self.console.print()


# 快捷函数
def show_task_start(console: Console, task_name: str) -> TaskPanel:
    """显示任务开始"""
    panel = TaskPanel(console)
    panel.start(task_name)
    return panel


def show_success(console: Console, title: str, message: str) -> None:
    """显示成功信息"""
    box = InfoBox(console)
    box.success(title, message)


def show_error(console: Console, title: str, message: str, suggestion: str = "") -> None:
    """显示错误信息"""
    box = InfoBox(console)
    box.error(title, message, suggestion)


def show_progress(console: Console, description: str, total: float = 100) -> Progress:
    """显示进度条"""
    progress = EnhancedProgress(console)
    return progress.create(description, total)
