#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI App - YM-CODE 主应用程序（美化版）
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.status import Status
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from .panels import WelcomePanel, StatusPanel, ProgressPanel, InfoPanel, HelpPanel
from ..utils.logger import get_logger
from ..mcp import get_registry as get_mcp_registry
from ..skills import get_registry as get_skills_registry

logger = get_logger(__name__)


# 跨平台 emoji 处理
IS_WINDOWS = sys.platform == 'win32'
EMOJI = {
    'robot': '🤖' if not IS_WINDOWS else '[BOT]',
    'check': '✅' if not IS_WINDOWS else '[✓]',
    'cross': '❌' if not IS_WINDOWS else '[✗]',
    'warning': '⚠️' if not IS_WINDOWS else '[!]',
    'info': 'ℹ️' if not IS_WINDOWS else '[i]',
    'sparkle': '✨' if not IS_WINDOWS else '[*]',
    'fire': '🔥' if not IS_WINDOWS else '[~]',
    'clock': '⏰' if not IS_WINDOWS else '[t]',
    'target': '🎯' if not IS_WINDOWS else '[>]',
}


class YMCodeApp:
    """YM-CODE 主应用程序（美化版）"""
    
    def __init__(self):
        """初始化应用程序"""
        self.console = Console(force_terminal=True, color_system="auto")
        self.welcome_panel = WelcomePanel(version="0.2.0")
        self.status_panel = StatusPanel()
        self.progress_panel = ProgressPanel()
        self.info_panel = InfoPanel()
        self.help_panel = HelpPanel()
        
        self.running = False
        self.command_history: List[str] = []
        self.history_index = -1
        
        # 注册表
        self.mcp_registry = None
        self.skills_registry = None
        self.llm_skill = None  # LLM 技能（大脑）
        
        # 任务状态
        self.current_task = None
        self.task_start_time = None
        
        logger.info("YM-CODE App 初始化完成（美化版）")
    
    def show_banner(self) -> None:
        """显示精美横幅"""
        banner = Text()
        banner.append("\n", style="")
        banner.append("╔═══════════════════════════════════════════╗\n", style="bold green")
        banner.append("║                                           ║\n", style="bold green")
        banner.append("║     ", style="bold green")
        banner.append("YM-CODE", style="bold bright_green")
        banner.append(" v0.2.0              ║\n", style="bold green")
        banner.append("║                                           ║\n", style="bold green")
        banner.append("║     ", style="bold green")
        banner.append("AI Programming Assistant", style="italic cyan")
        banner.append("      ║\n", style="bold green")
        banner.append("║                                           ║\n", style="bold green")
        banner.append("╚═══════════════════════════════════════════╝\n", style="bold green")
        banner.append("\n", style="")
        
        self.console.print(banner)
        
        # 显示快速帮助
        help_text = Text()
        help_text.append(f"{EMOJI['info']} ", style="cyan")
        help_text.append("输入 ", style="dim")
        help_text.append("'help'", style="bold yellow")
        help_text.append(" 查看命令 | 输入 ", style="dim")
        help_text.append("'exit'", style="bold yellow")
        help_text.append(" 退出\n", style="dim")
        
        self.console.print(help_text)
        self.console.print()
    
    def create_progress(self) -> Progress:
        """创建进度条"""
        return Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, complete_style="green", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            refresh_per_second=10
        )
    
    def show_task_start(self, task_name: str) -> None:
        """显示任务开始"""
        self.task_start_time = datetime.now()
        self.current_task = task_name
        
        panel = Panel(
            Text(f"{task_name}", style="bold white"),
            title=f"{EMOJI['target']} 任务进行中",
            border_style="yellow",
            subtitle=f"开始时间：{self.task_start_time.strftime('%H:%M:%S')}"
        )
        self.console.print(panel)
        self.console.print()
    
    def show_task_progress(self, description: str, progress: float) -> None:
        """显示任务进度"""
        with self.create_progress() as p:
            task = p.add_task(description, total=100)
            p.update(task, completed=progress)
    
    def show_task_complete(self, task_name: str, success: bool = True, message: str = "") -> None:
        """显示任务完成"""
        duration = ""
        if self.task_start_time:
            delta = datetime.now() - self.task_start_time
            duration = f"耗时：{delta.total_seconds():.1f}秒"
        
        if success:
            panel = Panel(
                Text(f"{message or '任务完成'}", style="bold green"),
                title=f"{EMOJI['check']} 成功",
                border_style="green",
                subtitle=duration
            )
        else:
            panel = Panel(
                Text(f"{message or '任务失败'}", style="bold red"),
                title=f"{EMOJI['cross']} 失败",
                border_style="red",
                subtitle=duration
            )
        
        self.console.print(panel)
        self.console.print()
        
        self.current_task = None
    
    def show_error(self, error: str, suggestion: str = "") -> None:
        """显示错误信息"""
        panel = Panel(
            Text(f"{error}\n\n{suggestion}", style="white"),
            title=f"{EMOJI['warning']} 错误",
            border_style="red",
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()
    
    def show_info(self, title: str, message: str) -> None:
        """显示信息"""
        panel = Panel(
            Text(message, style="white"),
            title=f"{EMOJI['info']} {title}",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()
    
    def format_response(self, response: str) -> str:
        """格式化响应"""
        # 如果是代码块，使用语法高亮
        if "```" in response:
            return Markdown(response)
        return response
    
    async def process_command(self, command: str) -> None:
        """处理命令"""
        command = command.strip()
        
        if not command:
            return
        
        self.command_history.append(command)
        if len(self.command_history) > 100:
            self.command_history.pop(0)
        
        # 特殊命令处理
        if command.lower() in ['exit', 'quit', 'q']:
            self.running = False
            return
        
        if command.lower() == 'help':
            self.help_panel.display()
            return
        
        if command.lower() == 'status':
            self.status_panel.display()
            return
        
        if command.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        
        # 显示任务开始
        self.show_task_start(f"处理：{command[:50]}...")
        
        try:
            # 显示进度
            with self.create_progress() as progress:
                task = progress.add_task("[cyan]分析中...", total=100)
                
                # 阶段 1: 分析
                progress.update(task, description="[cyan]分析中...", completed=20)
                await asyncio.sleep(0.3)
                
                # 阶段 2: 处理
                progress.update(task, description="[yellow]处理中...", completed=60)
                await asyncio.sleep(0.5)
                
                # 阶段 3: 完成
                progress.update(task, description="[green]完成", completed=100)
            
            # 显示完成
            self.show_task_complete(
                command[:50],
                success=True,
                message="命令执行完成"
            )
            
        except Exception as e:
            logger.error(f"命令处理失败：{e}")
            self.show_task_complete(
                command[:50],
                success=False,
                message=str(e)
            )
    
    async def run(self) -> None:
        """运行应用程序"""
        self.running = True
        
        # 显示欢迎横幅
        self.show_banner()
        
        # 初始化注册表
        self.mcp_registry = get_mcp_registry()
        self.skills_registry = get_skills_registry()
        
        while self.running:
            try:
                # 显示提示符
                prompt_text = f"{EMOJI['robot']} YM-CODE"
                user_input = Prompt.ask(prompt_text, default="")
                
                if user_input:
                    await self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]使用 'exit' 退出[/yellow]")
            except EOFError:
                break
        
        self.console.print("[dim]再见！[/dim]")
    
    def run_sync(self) -> None:
        """同步运行"""
        asyncio.run(self.run())


def main():
    """主函数"""
    app = YMCodeApp()
    app.run_sync()


if __name__ == "__main__":
    main()
