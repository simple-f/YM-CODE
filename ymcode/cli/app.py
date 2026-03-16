#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI App - YM-CODE 主应用程序
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from .panels import WelcomePanel, StatusPanel, ProgressPanel, InfoPanel, HelpPanel
from ..utils.logger import get_logger
from ..mcp import get_registry as get_mcp_registry
from ..skills import get_registry as get_skills_registry

logger = get_logger(__name__)


class YMCodeApp:
    """YM-CODE 主应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        self.console = Console()
        self.welcome_panel = WelcomePanel(version="1.0.0-dev")
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
        
        logger.info("YM-CODE App 初始化完成")
    
    async def initialize(self) -> bool:
        """初始化应用"""
        logger.info("初始化 YM-CODE...")
        
        try:
            # 初始化 MCP 注册表
            self.mcp_registry = get_mcp_registry()
            self.status_panel.update("MCP Servers", str(len(self.mcp_registry.list_servers())))
            
            # 初始化 Skills 注册表
            self.skills_registry = get_skills_registry()
            skills = self.skills_registry.list_skills()
            self.status_panel.update("Skills", str(len(skills)))
            
            # 初始化 LLM 技能（大脑）
            self.llm_skill = self.skills_registry.get('llm')
            if self.llm_skill:
                # 构建工具定义供 LLM 调用
                tools = self._build_llm_tools()
                self.llm_skill.set_available_tools(tools)
                # 设置技能注册表（用于工具调用）
                self.llm_skill.set_skills_registry(self.skills_registry)
                logger.info(f"LLM 技能已初始化，可用工具：{len(tools)} 个")
            
            self.info_panel.add_success("初始化完成")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化失败：{e}")
            self.info_panel.add_error(f"初始化失败：{e}")
            return False
    
    def create_layout(self) -> Layout:
        """创建布局"""
        layout = Layout()
        
        # 分割为上下两部分
        layout.split(
            Layout(name="header", size=10),
            Layout(name="body"),
            Layout(name="footer", size=5)
        )
        
        # 身体部分再分割
        layout["body"].split_row(
            Layout(name="status", ratio=1),
            Layout(name="info", ratio=2)
        )
        
        return layout
    
    def update_layout(self, layout: Layout) -> None:
        """更新布局内容"""
        # Header - 欢迎信息
        layout["header"].update(self.welcome_panel.render())
        
        # Status - 状态面板
        layout["status"].update(self.status_panel.render())
        
        # Info - 信息面板
        layout["info"].update(self.info_panel.render())
        
        # Footer - 进度条
        footer_text = Text()
        footer_text.append("Ready", style="green")
        layout["footer"].update(Panel(footer_text, style="dim"))
    
    async def run(self) -> None:
        """运行应用"""
        self.running = True
        
        # 显示欢迎信息
        self.welcome_panel.display()
        
        # 初始化
        if not await self.initialize():
            return
        
        # 主循环
        while self.running:
            try:
                # 显示状态
                self.status_panel.display()
                
                # 获取用户输入
                command = await self.get_input()
                
                if command:
                    # 执行命令
                    await self.execute_command(command)
                    
                    # 添加到历史记录
                    self.command_history.append(command)
                    self.history_index = len(self.command_history)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"运行错误：{e}")
                self.info_panel.add_error(str(e))
        
        # 清理
        await self.cleanup()
    
    async def get_input(self) -> Optional[str]:
        """获取用户输入"""
        try:
            command = Prompt.ask(
                "[bold green]ym-code>[/bold green]",
                console=self.console
            )
            return command.strip()
        except EOFError:
            return None
    
    async def execute_command(self, command: str) -> None:
        """执行命令"""
        logger.info(f"执行命令：{command}")
        
        # 特殊命令处理
        if command.lower() in ['exit', 'quit', 'q']:
            self.running = False
            return
        
        if command.lower() == 'help':
            self.help_panel.display()
            return
        
        if command.lower() == 'clear':
            self.console.clear()
            return
        
        if command.lower() == 'status':
            self.status_panel.display()
            return
        
        # 开始进度
        self.progress_panel.start_task("处理中...")
        
        try:
            # 尝试执行技能命令
            result = await self.execute_skill_command(command)
            
            if result:
                if isinstance(result, dict):
                    # 特殊处理响应字段
                    if 'response' in result:
                        self.info_panel.add_message(result['response'], style="white")
                    if 'success' in result and result['success']:
                        pass  # 成功时不重复显示
                    elif 'error' in result:
                        self.info_panel.add_error(result['error'])
                    else:
                        self.info_panel.add_success("执行完成")
                else:
                    self.info_panel.add_message(str(result), style="white")
            else:
                self.info_panel.add_warning(f"未知命令：{command}")
            
        except Exception as e:
            logger.error(f"命令执行失败：{e}")
            self.info_panel.add_error(str(e))
        
        finally:
            self.progress_panel.complete_task()
    
    def _build_llm_tools(self) -> List[Dict]:
        """构建 LLM 可调用的工具定义"""
        tools = []
        
        skills = self.skills_registry.list_skills()
        for skill_info in skills:
            skill_name = skill_info['name']
            
            # 跳过 LLM 自身和 chat
            if skill_name in ['llm', 'chat']:
                continue
            
            # 构建工具定义（OpenAI 兼容格式）
            tool_def = {
                "type": "function",
                "function": {
                    "name": f"skill_{skill_name}",
                    "description": skill_info.get('description', f'执行{skill_name}技能'),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户输入或查询内容"
                            },
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            },
                            "message": {
                                "type": "string",
                                "description": "消息内容"
                            }
                        },
                        "required": []
                    }
                }
            }
            tools.append(tool_def)
        
        logger.info(f"构建 LLM 工具定义：{len(tools)} 个工具")
        for tool in tools:
            logger.debug(f"  - {tool['function']['name']}: {tool['function']['description'][:50]}")
        
        return tools
    
    async def execute_skill_command(self, command: str) -> Optional[dict]:
        """执行技能命令"""
        if not self.skills_registry:
            return None
        
        # 简单的命令解析
        parts = command.split()
        if not parts:
            return None
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # 如果是明确的技能命令，直接执行
        skills = self.skills_registry.list_skills()
        for skill_info in skills:
            skill_name = skill_info['name']
            
            # 检查命令是否匹配技能
            if cmd == skill_name or cmd == f"skill_{skill_name}":
                skill = self.skills_registry.get(skill_name)
                if skill:
                    # 构建参数
                    arguments = {}
                    if args:
                        arguments['query'] = ' '.join(args)
                        arguments['command'] = ' '.join(args)
                    
                    # 执行技能
                    result = await skill.execute(arguments)
                    return result
        
        # 优先使用 LLM 处理自然语言（如果有配置 API Key）
        if self.llm_skill and self.llm_skill.api_key:
            try:
                result = await self.llm_skill.execute({'message': command, 'use_tools': True})
                if result.get('success'):
                    return result
            except Exception as e:
                logger.warning(f"LLM 执行失败，降级到 chat 技能：{e}")
        
        # 降级到 chat 技能
        chat_skill = self.skills_registry.get('chat')
        if chat_skill:
            result = await chat_skill.execute({'message': command})
            return result
        
        return None
    
    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("清理资源...")
        
        self.info_panel.add_message("再见！", style="dim")
        self.console.print()
    
    def run_sync(self) -> None:
        """同步运行"""
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]已退出[/yellow]")


def main():
    """主入口"""
    import sys
    import platform
    
    # 确保工作空间正确
    workspace = Path(__file__).parent.parent.parent
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    
    # 跨平台 UTF-8 设置
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Windows 特定设置
    if sys.platform == 'win32':
        try:
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # 系统信息
    system_info = f"{platform.system()} {platform.machine()}"
    
    console = Console()
    
    # 显示欢迎横幅（跨平台兼容）
    console.print()
    console.print("[bold green]+========================================+[/bold green]")
    console.print("[bold green]|[/bold green]  [bold white]YM-CODE v0.1.0[/bold white]                    [bold green]|[/bold green]")
    console.print("[bold green]|[/bold green]  [dim]AI Programming Assistant[/dim]             [bold green]|[/bold green]")
    console.print("[bold green]|[/bold green]  [dim]Port: 18770[/dim]                        [bold green]|[/bold green]")
    console.print(f"[bold green]|[/bold green]  [dim]Platform: {system_info}[/dim]           [bold green]|[/bold green]")
    console.print("[bold green]+========================================+[/bold green]")
    console.print()
    
    # 创建并运行应用
    app = YMCodeApp()
    app.run_sync()


if __name__ == "__main__":
    main()
