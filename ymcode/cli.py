#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI - 交互式命令行界面

像 Claude Code 一样好用的 AI 编程助手
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# 主动加载 .env 文件
from dotenv import load_dotenv

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install
from rich.live import Live
from rich.text import Text

# 安装友好的 traceback
install(show_locals=True)

# 初始化控制台
console = Console()


class YMCodeCompleter:
    """命令自动补全"""
    
    def __init__(self):
        self.commands = [
            'help', 'quit', 'exit', 'clear',
            'bash', 'read', 'write', 'edit',
            'git status', 'git commit', 'git push',
            'test', 'run', 'explain', 'review'
        ]
    
    def complete(self, text: str) -> list:
        """返回匹配的命令"""
        if not text:
            return self.commands
        return [cmd for cmd in self.commands if cmd.startswith(text.lower())]


class YMCodeCLI:
    """YM-CODE 交互式 CLI"""
    
    def __init__(self):
        """初始化 CLI"""
        self.agent = None
        self.running = False
        self.completer = YMCodeCompleter()
        self.history = []
        self.config = self._load_config()
        
        # 初始化智能路由器
        try:
            from ymcode.router import SmartRouter
            self.router = SmartRouter()
            console.print("[green][✓] 智能路由已加载[/green]\n")
        except Exception as e:
            console.print(f"[yellow][!] 智能路由加载失败：{e}[/yellow]")
            console.print("[dim]提示：将使用默认 Agent[/dim]\n")
            self.router = None
    
    def _load_config(self) -> dict:
        """加载配置"""
        config = {
            'max_iterations': 30,
            'timeout': 300,
            'log_level': 'INFO',
            'mock_mode': False,
            'model': 'glm-5'  # 默认模型
        }
        
        # 加载模型配置
        self.models_config = self._load_models()
        
        # 检查 API Key
        if os.getenv('OPENAI_API_KEY'):
            config['mock_mode'] = False
        else:
            config['mock_mode'] = True
            console.print("[yellow][!] 未配置 API Key，使用 Mock 模式[/yellow]")
            console.print("[dim]提示：编辑 .env 文件配置 API Key[/dim]\n")
        
        return config
    
    def _load_models(self) -> dict:
        """加载模型配置"""
        import json
        models_file = Path(__file__).parent.parent / "models.json"
        if models_file.exists():
            with open(models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"models": {}, "default": "glm-5"}
    
    def list_models(self):
        """列出所有可用模型"""
        console.print("\n[bold]可用模型列表:[/bold]\n")
        
        for model_id, info in self.models_config.get("models", {}).items():
            current = " [green](当前)[/green]" if model_id == self.config['model'] else ""
            console.print(f"  [cyan]{model_id}[/cyan]{current}")
            console.print(f"    [dim]{info.get('description', '')}[/dim]")
            console.print(f"    [dim]Base URL: {info.get('base_url', '')}[/dim]\n")
        
        console.print(f"[dim]默认模型：{self.models_config.get('default', 'glm-5')}[/dim]\n")
    
    def switch_model(self, model_id: str):
        """切换模型"""
        if model_id not in self.models_config.get("models", {}):
            console.print(f"[red][!] 未知模型：{model_id}[/red]")
            console.print("[dim]使用 'models' 命令查看所有可用模型[/dim]")
            return
        
        # 更新配置
        model_info = self.models_config["models"][model_id]
        self.config['model'] = model_id
        self.config['base_url'] = model_info.get('base_url')
        self.config['max_tokens'] = model_info.get('max_tokens', 4000)
        
        # 重新初始化 Agent
        console.print(f"[green][OK] 已切换到模型：{model_id} ({model_info.get('name', '')})[/green]\n")
    
    def show_banner(self):
        """显示欢迎横幅"""
        banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   YM-CODE v0.2.0 - AI Programming Assistant          ║
║                                                       ║
║   Next Generation AI Programming Experience          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
        console.print(Panel(banner, style="bold green"))
        console.print()
        console.print("[dim]输入 'help' 查看帮助，'quit' 退出[/dim]\n")
    
    async def initialize(self):
        """初始化 Agent"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在初始化 YM-CODE...", total=None)
            
            # 导入 Agent
            from ymcode.core.agent import Agent
            
            # 初始化 Agent
            self.agent = Agent(config=self.config)
            
            progress.update(task, description="[green]✓ Agent 就绪[/green]")
        
        console.print("[green][OK] YM-CODE 准备就绪！[/green]\n")
    
    async def stream_output(self, text: str):
        """流式输出（打字机效果）"""
        # 分段显示，避免太慢
        chunk_size = 3
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            console.print(chunk, end='', highlight=False)
            await asyncio.sleep(0.01)
        console.print()  # 换行
    
    def show_help(self):
        """显示帮助"""
        help_text = """
## YM-CODE 帮助

### 基本用法

直接输入你的请求，例如：
- "帮我创建一个文件"
- "读取 test.py 的内容"
- "运行 git status"

### 命令列表

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助 |
| `quit` / `exit` | 退出程序 |
| `clear` | 清屏 |
| `model` | 查看/切换模型 |
| `models` | 列出所有可用模型 |
| `bash <命令>` | 执行 bash 命令 |
| `read <文件>` | 读取文件 |
| `write <文件> <内容>` | 写入文件 |
| `git <操作>` | Git 操作 |
| `test` | 运行测试 |
| `explain` | 解释代码 |
| `review` | 审查代码 |

### 模型切换

```
> model              # 查看当前模型
> models             # 列出所有模型
> model glm-4        # 切换到 GLM-4
> model gpt-4        # 切换到 GPT-4
```

### 示例

```
> 帮我创建 test.py，写入 print("hello")
> 读取 test.py
> 运行 git status
> 解释这段代码
> model glm-4
> 继续优化代码
```
"""
        console.print(Markdown(help_text))
    
    async def run_command(self, command: str):
        """运行用户命令"""
        if not command.strip():
            return
        
        # 特殊命令处理
        if command.lower() in ['quit', 'exit', 'q']:
            self.running = False
            return
        
        if command.lower() == 'help':
            self.show_help()
            return
        
        if command.lower() == 'clear':
            console.clear()
            return
        
        if command.lower() == 'models':
            self.list_models()
            return
        
        if command.lower().startswith('model'):
            parts = command.split(maxsplit=1)
            if len(parts) == 1:
                # 查看当前模型
                current = self.config.get('model', 'glm-5')
                console.print(f"\n[bold]当前模型：[cyan]{current}[/cyan][/bold]\n")
            else:
                # 切换模型
                model_id = parts[1].strip()
                self.switch_model(model_id)
            return
        
        # ========== 智能路由 ==========
        route_result = None
        if self.router:
            try:
                import time
                route_start = time.time()
                route_result = self.router.route(command)
                route_time = (time.time() - route_start) * 1000
                
                # 显示路由信息
                console.print()
                
                # 置信度表情
                if route_result.confidence > 0.7:
                    emoji = "🟢"
                elif route_result.confidence > 0.4:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                
                console.print(f"[bold blue]{emoji} 智能路由[/bold blue] [dim]{route_time:.1f}ms[/dim]")
                console.print(f"  [bold]Agent:[/bold] [cyan]{route_result.agent_name}[/cyan] ({route_result.selected_agent})")
                console.print(f"  [bold]置信度:[/bold] {emoji} {route_result.confidence:.0%}")
                console.print(f"  [bold]预计响应:[/bold] {route_result.response_time_estimate}s")
                
                if route_result.matched_keywords:
                    console.print(f"  [bold]关键词:[/bold] {', '.join(route_result.matched_keywords)}")
                
                if route_result.alternative_agents:
                    alt_names = [self.router.get_agent_info(aid)["name"] for aid in route_result.alternative_agents if self.router.get_agent_info(aid)]
                    if alt_names:
                        console.print(f"  [bold]备选:[/bold] {', '.join(alt_names)}")
                
                console.print()
            except Exception as e:
                console.print(f"[yellow][!] 路由失败：{e}，使用默认 Agent[/yellow]\n")
                route_result = None
        
        # 执行 Agent 命令
        console.print("[bold blue][AI] YM-CODE:[/bold blue]\n")
        
        try:
            import time
            start_time = time.time()
            
            # 调用 Agent（如果有路由结果，使用选定的 Agent）
            if route_result:
                # 更新配置使用路由选定的模型
                agent_info = self.router.get_agent_info(route_result.selected_agent)
                if agent_info:
                    old_model = self.config.get('model')
                    self.config['model'] = agent_info.get('model', old_model)
                    # 重新初始化 Agent（如果需要）
                    if self.agent and hasattr(self.agent, 'model') and self.agent.model != self.config['model']:
                        from ymcode.core.agent import Agent
                        self.agent = Agent(config=self.config)
            
            result = await self.agent.run(command)
            
            response_time = time.time() - start_time
            
            # 流式输出结果
            await self.stream_output(str(result))
            
            # 记录路由结果
            if self.router and route_result:
                try:
                    self.router.record_result(route_result.selected_agent, True, response_time)
                except:
                    pass
            
        except Exception as e:
            console.print(f"[red][!] 错误：{e}[/red]")
            # 记录失败
            if self.router and route_result:
                try:
                    self.router.record_result(route_result.selected_agent, False, 0)
                except:
                    pass
    
    async def run(self):
        """运行 CLI"""
        self.show_banner()
        
        # 初始化 Agent
        await self.initialize()
        
        # 主循环
        self.running = True
        
        while self.running:
            try:
                # 获取用户输入（带提示）
                command = Prompt.ask(
                    "[bold cyan]YM-CODE>[/bold cyan]",
                    console=console
                )
                
                # 添加到历史
                self.history.append(command)
                
                if command.strip():
                    await self.run_command(command)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]按 Ctrl+D 或输入 'quit' 退出[/yellow]")
            except EOFError:
                self.running = False
        
        console.print("\n[yellow]感谢使用 YM-CODE![/yellow]")


def main():
    """主函数（入口）"""
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        console.print("\n[yellow]再见！[/yellow]")
        sys.exit(0)


async def _async_main():
    """异步主函数"""
    cli = YMCodeCLI()
    await cli.run()


if __name__ == "__main__":
    main()
