#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Panels - 面板组件（跨平台兼容）
"""

import sys
import platform

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.style import Style

from ..utils.logger import get_logger

logger = get_logger(__name__)

# 跨平台 emoji 处理
IS_WINDOWS = sys.platform == 'win32'

# Windows 上用文字替代 emoji
EMOJI = {
    'welcome': '🤖' if not IS_WINDOWS else '[BOT]',
    'status': '📊' if not IS_WINDOWS else '[STATUS]',
    'progress': '📈' if not IS_WINDOWS else '[PROGRESS]',
    'messages': '📝' if not IS_WINDOWS else '[MESSAGES]',
    'help': '❓' if not IS_WINDOWS else '[HELP]',
    'ok': '✅' if not IS_WINDOWS else '[OK]',
    'error': '❌' if not IS_WINDOWS else '[ERR]',
    'warning': '⚠️' if not IS_WINDOWS else '[WARN]',
}


class WelcomePanel:
    """欢迎面板（美化版）"""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.console = Console()
    
    def render(self) -> Panel:
        """渲染欢迎面板"""
        content = Text()
        content.append("YM-CODE ", style="bold green")
        content.append(f"v{self.version}\n", style="bold bright_green")
        content.append("AI Programming Assistant\n", style="italic cyan")
        content.append("\n", style="")
        content.append("Type your request or 'help' for commands.\n", style="dim yellow")
        
        return Panel(
            content,
            title=f"[bold green]{EMOJI['welcome']} Welcome[/bold green]",
            subtitle="[dim]Press Ctrl+C to exit[/dim]",
            border_style="bright_green",
            box=box.DOUBLE_EDGE
        )
    
    def display(self) -> None:
        """显示欢迎面板（美化版）"""
        # 精美横幅
        self.console.print()
        self.console.print("[bold green]╔═══════════════════════════════════════════╗[/bold green]")
        self.console.print("[bold green]║[/bold green]                                           [bold green]║[/bold green]")
        self.console.print(f"[bold green]║[/bold green]     [bold bright_green]YM-CODE[/bold bright_green] [dim]v{self.version}[/dim]              [bold green]║[/bold green]")
        self.console.print("[bold green]║[/bold green]                                           [bold green]║[/bold green]")
        self.console.print("[bold green]║[/bold green]     [italic cyan]AI Programming Assistant[/italic cyan]      [bold green]║[/bold green]")
        self.console.print("[bold green]║[/bold green]                                           [bold green]║[/bold green]")
        self.console.print("[bold green]╚═══════════════════════════════════════════╝[/bold green]")
        self.console.print()
        self.console.print(f"[dim]{EMOJI['info']} 输入 'help' 查看命令 | 输入 'exit' 退出[/dim]")
        self.console.print()


class StatusPanel:
    """状态面板"""
    
    def __init__(self):
        self.console = Console()
        self.status_info = {}
    
    def update(self, key: str, value: str) -> None:
        """更新状态"""
        self.status_info[key] = value
    
    def render(self) -> Panel:
        """渲染状态面板"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in self.status_info.items():
            table.add_row(key, value)
        
        return Panel(
            table,
            title=f"[bold blue]{EMOJI['status']} Status[/bold blue]",
            border_style="blue"
        )
    
    def display(self) -> None:
        """显示状态面板"""
        self.console.print(self.render())


class ProgressPanel:
    """进度面板"""
    
    def __init__(self):
        self.console = Console()
        self.current_task = ""
        self.progress = 0
        self.status = "idle"
    
    def start_task(self, task_name: str) -> None:
        """开始任务"""
        self.current_task = task_name
        self.progress = 0
        self.status = "running"
        logger.info(f"开始任务：{task_name}")
    
    def update_progress(self, progress: int, status: str = "running") -> None:
        """更新进度"""
        self.progress = min(100, max(0, progress))
        self.status = status
    
    def complete_task(self) -> None:
        """完成任务"""
        self.progress = 100
        self.status = "completed"
        logger.info(f"任务完成：{self.current_task}")
    
    def render_progress(self) -> Progress:
        """渲染进度条"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
        
        task_id = progress.add_task(
            self.current_task,
            total=100,
            completed=self.progress
        )
        
        return progress
    
    def display_status(self) -> str:
        """显示状态文本"""
        status_colors = {
            "idle": "dim",
            "running": "yellow",
            "completed": "green",
            "error": "red"
        }
        color = status_colors.get(self.status, "white")
        return f"[{color}]●[/{color}] {self.status.capitalize()}"


class InfoPanel:
    """信息面板"""
    
    def __init__(self):
        self.console = Console()
        self.messages = []
    
    def add_message(self, message: str, style: str = "white") -> None:
        """添加消息"""
        self.messages.append((message, style))
        # Windows 兼容日志（移除 emoji）
        safe_message = message.replace('✅', '[OK]').replace('❌', '[ERR]').replace('⚠️ ', '[WARN]')
        logger.info(f"消息：{safe_message}")
    
    def add_success(self, message: str) -> None:
        """添加成功消息"""
        self.add_message(f"[OK] {message}", "green")
    
    def add_error(self, message: str) -> None:
        """添加错误消息"""
        self.add_message(f"[ERR] {message}", "red")
    
    def add_warning(self, message: str) -> None:
        """添加警告消息"""
        self.add_message(f"[WARN] {message}", "yellow")
    
    def render(self) -> Panel:
        """渲染信息面板"""
        content = Text()
        for message, style in self.messages[-10:]:  # 只显示最近 10 条
            content.append(message + "\n", style=style)
        
        return Panel(
            content,
            title=f"[bold white]{EMOJI['messages']} Messages[/bold white]",
            border_style="white"
        )
    
    def display(self) -> None:
        """显示信息面板"""
        if self.messages:
            self.console.print(self.render())
    
    def clear(self) -> None:
        """清空消息"""
        self.messages.clear()


class HelpPanel:
    """帮助面板"""
    
    def __init__(self):
        self.console = Console()
        self.commands = self._get_commands()
    
    def _get_commands(self) -> list:
        """获取命令列表"""
        return [
            ("help", "显示帮助信息", "white"),
            ("clear", "清空屏幕", "white"),
            ("status", "显示当前状态", "white"),
            ("config", "显示配置", "white"),
            ("exit / quit", "退出程序", "red"),
            ("", "", ""),
            ("文件操作", "", "cyan"),
            ("  read <file>", "读取文件", "white"),
            ("  write <file>", "写入文件", "white"),
            ("  edit <file>", "编辑文件", "white"),
            ("", "", ""),
            ("工具", "", "cyan"),
            ("  search <query>", "搜索文件", "white"),
            ("  analyze", "分析项目", "white"),
            ("  run <command>", "执行命令", "white"),
        ]
    
    def render(self) -> Panel:
        """渲染帮助面板"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Command", style="bold")
        table.add_column("Description", style="dim")
        
        for cmd, desc, style in self.commands:
            if cmd == "":
                table.add_row("", "")
            else:
                table.add_row(
                    Text(cmd, style=style),
                    Text(desc, style="dim")
                )
        
        return Panel(
            table,
            title=f"[bold yellow]{EMOJI['help']} Help[/bold yellow]",
            subtitle="Type a command to execute",
            border_style="yellow"
        )
    
    def display(self) -> None:
        """显示帮助面板"""
        self.console.print(self.render())
