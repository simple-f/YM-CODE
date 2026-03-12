#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI - 命令行界面

融合课程：s01 (Agent Loop) + 生产级 CLI 设计
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install

from .core.agent import Agent
from .utils.logger import get_logger

# 安装友好的 traceback
install(show_locals=True)

# 初始化控制台
console = Console()
logger = get_logger(__name__)


class YMCodeCLI:
    """YM-CODE 命令行界面"""
    
    def __init__(self):
        """初始化 CLI"""
        self.agent: Optional[Agent] = None
        self.running = False
    
    def show_banner(self):
        """显示欢迎横幅"""
        banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   YM-CODE v0.1.0 - AI Programming Assistant          ║
║                                                       ║
║   Next Generation AI Programming Experience          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
        console.print(Panel(banner, style="bold green"))
        console.print()
        console.print("[dim]Type 'help' for commands, 'quit' to exit[/dim]")
        console.print()
    
    async def initialize(self):
        """初始化 Agent"""
        console.print("[yellow]正在初始化 YM-CODE...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("加载 Agent...", total=None)
            
            # 初始化 Agent
            self.agent = Agent()
            
            progress.update(task, description="[green]✓ Agent 就绪[/green]")
        
        console.print("[green]✓ YM-CODE 准备就绪！[/green]")
        console.print()
    
    async def run_command(self, command: str):
        """
        运行用户命令
        
        参数:
            command: 用户输入
        """
        if not self.agent:
            console.print("[red]错误：Agent 未初始化[/red]")
            return
        
        # 特殊命令处理
        if command.lower() in ['quit', 'exit', 'q']:
            self.running = False
            return
        
        if command.lower() == 'help':
            self.show_help()
            return
        
        # 执行 Agent 任务
        console.print()
        console.print("[bold blue]🤖 YM-CODE:[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("思考中...", total=None)
            
            try:
                # 调用 Agent
                response = await self.agent.run(command)
                
                progress.update(task, description="[green]✓ 完成[/green]")
                
                # 显示结果
                console.print()
                console.print(Markdown(response))
                
            except Exception as e:
                logger.error(f"执行失败：{e}", exc_info=True)
                progress.update(task, description="[red]✗ 失败[/red]")
                console.print(f"[red]错误：{e}[/red]")
        
        console.print()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
## YM-CODE 帮助

### 基本用法

直接输入你的请求，例如：
- "帮我修复这个 bug"
- "审查这个文件"
- "解释这段代码"

### 特殊命令

- `help` - 显示帮助
- `quit` - 退出程序
- `clear` - 清屏

### 示例

```bash
> 帮我创建一个 Python 项目
> 审查 main.py 文件
> 解释这个函数的作用
```
"""
        console.print(Markdown(help_text))
    
    async def run(self):
        """运行 CLI"""
        self.show_banner()
        
        # 初始化 Agent
        await self.initialize()
        
        # 主循环
        self.running = True
        
        while self.running:
            try:
                # 获取用户输入
                command = Prompt.ask(
                    "[bold cyan]>[/bold cyan]",
                    console=console
                )
                
                if command.strip():
                    await self.run_command(command)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]按 Ctrl+C 退出，输入 'quit' 确认退出[/yellow]")
            except EOFError:
                self.running = False
        
        console.print("[yellow]感谢使用 YM-CODE！[/yellow]")


async def main():
    """主函数"""
    cli = YMCodeCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]再见！[/yellow]")
        sys.exit(0)
