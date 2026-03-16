#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Git Tools - 增强的 Git 工具（可视化 + 交互式）
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from ..cli.enhanced import InfoBox, TaskPanel, StatsTable
from .base import BaseTool


# 跨平台 emoji（Windows 兼容）
IS_WINDOWS = True
EMOJI = {
    'added': '[ADD]',
    'modified': '[MOD]',
    'deleted': '[DEL]',
    'renamed': '[REN]',
    'copied': '[CPY]',
    'untracked': '[NEW]',
    'staged': '[OK]',
    'unstaged': '[  ]',
    'branch': '[>]',
    'commit': '[C]',
}


class ChangeType(Enum):
    """变更类型"""
    ADDED = 'A'
    MODIFIED = 'M'
    DELETED = 'D'
    RENAMED = 'R'
    COPIED = 'C'
    UNTRACKED = '?'


@dataclass
class GitStatus:
    """Git 状态数据"""
    staged: List[Tuple[str, str]]  # [(变更类型，文件路径), ...]
    unstaged: List[Tuple[str, str]]
    untracked: List[str]
    branch: str
    ahead: int
    behind: int


class EnhancedGitTool(BaseTool):
    """增强的 Git 工具（可视化 + 交互式）"""
    
    name = "git_enhanced"
    description = "增强的 Git 版本控制操作（可视化 + 交互式）"
    
    def __init__(self, console: Optional[Console] = None):
        # Windows 兼容模式
        if IS_WINDOWS:
            self.console = console or Console(force_terminal=True, color_system="basic")
        else:
            self.console = console or Console()
        self.info_box = InfoBox(self.console)
    
    def _run_git(self, args: List[str], check: bool = False, cwd: str = None) -> str:
        """运行 Git 命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=check,
                timeout=30,
                cwd=cwd
            )
            
            if result.returncode != 0 and check:
                return f"错误：{result.stderr}"
            
            return result.stdout or ""
            
        except subprocess.TimeoutExpired:
            return "错误：命令超时（>30 秒）"
        except FileNotFoundError:
            return "错误：未找到 git 命令"
    
    def parse_status(self, output: str) -> GitStatus:
        """解析 git status 输出"""
        staged = []
        unstaged = []
        untracked = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            if line.startswith('??'):
                # 未跟踪
                untracked.append(line[3:].strip())
            elif line.startswith(' '):
                # 工作区变更
                change_type = line[0].strip() or 'M'
                file_path = line[3:].strip()
                unstaged.append((change_type, file_path))
            else:
                # 暂存区变更
                change_type = line[0].strip() or 'M'
                file_path = line[1:].strip()
                staged.append((change_type, file_path))
        
        # 获取分支信息
        branch_output = self._run_git(["branch", "--show-current"])
        branch = branch_output.strip() or "main"
        
        # 获取 ahead/behind
        ahead_behind_output = self._run_git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
        ahead, behind = 0, 0
        if ahead_behind_output.strip():
            parts = ahead_behind_output.strip().split('\t')
            if len(parts) == 2:
                ahead = int(parts[0])
                behind = int(parts[1])
        
        return GitStatus(
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            branch=branch,
            ahead=ahead,
            behind=behind
        )
    
    def show_status_visual(self, status: GitStatus) -> None:
        """可视化显示 Git 状态"""
        self.console.print()
        
        # 分支信息
        branch_text = Text()
        branch_text.append(f"{EMOJI['branch']} ", style="bold cyan")
        branch_text.append(f"分支：{status.branch}", style="bold white")
        
        if status.ahead > 0:
            branch_text.append(f" ↑{status.ahead}", style="yellow")
        if status.behind > 0:
            branch_text.append(f" ↓{status.behind}", style="yellow")
        
        self.console.print(Panel(branch_text, border_style="cyan", box=box.ROUNDED))
        self.console.print()
        
        # 暂存区
        if status.staged:
            table = Table(
                title=f"{EMOJI['staged']} 暂存区 ({len(status.staged)} 个文件)",
                box=box.ROUNDED,
                border_style="green",
                show_header=True
            )
            table.add_column("变更", style="cyan", width=8)
            table.add_column("文件", style="white")
            
            for change_type, file_path in status.staged:
                icon = self._get_change_icon(change_type)
                table.add_row(icon, file_path)
            
            self.console.print(table)
            self.console.print()
        
        # 工作区变更
        if status.unstaged:
            table = Table(
                title=f"{EMOJI['unstaged']} 工作区变更 ({len(status.unstaged)} 个文件)",
                box=box.ROUNDED,
                border_style="yellow",
                show_header=True
            )
            table.add_column("变更", style="cyan", width=8)
            table.add_column("文件", style="white")
            
            for change_type, file_path in status.unstaged:
                icon = self._get_change_icon(change_type)
                table.add_row(icon, file_path)
            
            self.console.print(table)
            self.console.print()
        
        # 未跟踪文件
        if status.untracked:
            table = Table(
                title=f"{EMOJI['untracked']} 未跟踪文件 ({len(status.untracked)} 个)",
                box=box.ROUNDED,
                border_style="blue",
                show_header=True
            )
            table.add_column("文件", style="white")
            
            for file_path in status.untracked:
                table.add_row(file_path)
            
            self.console.print(table)
            self.console.print()
        
        # 统计
        stats = {
            "暂存区": str(len(status.staged)),
            "工作区": str(len(status.unstaged)),
            "未跟踪": str(len(status.untracked)),
            "分支": status.branch,
        }
        
        if status.ahead > 0 or status.behind > 0:
            stats["远程同步"] = f"↑{status.ahead} ↓{status.behind}"
        
        stats_table = StatsTable(self.console)
        stats_table.show("Git 状态统计", stats)
    
    def _get_change_icon(self, change_type: str) -> str:
        """获取变更类型图标"""
        icons = {
            'A': f"{EMOJI['added']} 新增",
            'M': f"{EMOJI['modified']} 修改",
            'D': f"{EMOJI['deleted']} 删除",
            'R': f"{EMOJI['renamed']} 重命名",
            'C': f"{EMOJI['copied']} 复制",
            '?': f"{EMOJI['untracked']} 未跟踪",
        }
        return icons.get(change_type, f"[?] {change_type}")
    
    def show_diff_visual(self, diff: str) -> None:
        """可视化显示 diff"""
        if not diff.strip():
            self.info_box.info("Git Diff", "没有变更")
            return
        
        lines = diff.split('\n')
        text = Text()
        
        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                text.append(line + '\n', style="bold cyan")
            elif line.startswith('+'):
                text.append(line + '\n', style="green")
            elif line.startswith('-'):
                text.append(line + '\n', style="red")
            elif line.startswith('@@'):
                text.append(line + '\n', style="bold yellow")
            elif line.startswith('diff --git'):
                text.append(line + '\n', style="bold white")
            else:
                text.append(line + '\n', style="dim")
        
        panel = Panel(
            text,
            title="Git Diff",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    async def interactive_commit(self) -> str:
        """交互式 commit"""
        self.console.print()
        self.console.print("[bold cyan]=== Git 交互式提交 ===[/bold cyan]")
        self.console.print()
        
        # 1. 显示状态
        status_output = self._run_git(["status", "--short"])
        if not status_output.strip():
            self.info_box.info("Git Status", "没有变更需要提交")
            return "没有变更"
        
        status = self.parse_status(status_output)
        self.show_status_visual(status)
        
        # 2. 选择文件（简化版：全部添加）
        self.console.print("[yellow]提示：输入 'git add -A' 添加所有变更[/yellow]")
        self.console.print()
        
        # 3. 输入提交信息
        self.console.print("[bold]请输入提交信息（输入 'q' 取消）:[/bold]")
        message = input("> ").strip()
        
        if not message or message.lower() == 'q':
            self.info_box.warning("已取消", "提交已取消")
            return "已取消"
        
        # 4. 执行提交
        self.console.print()
        task = TaskPanel(self.console)
        task.start("Git 提交中...")
        
        add_result = self._run_git(["add", "-A"])
        commit_result = self._run_git(["commit", "-m", message])
        
        if "错误" in commit_result:
            task.complete(success=False, message=commit_result)
            return f"提交失败：{commit_result}"
        
        task.complete(success=True, message=f"成功提交：{message[:30]}...")
        return commit_result
    
    async def show_log_visual(self, limit: int = 10) -> None:
        """可视化显示提交历史"""
        self.console.print()
        self.console.print("[bold cyan]=== Git 提交历史 ===[/bold cyan]")
        self.console.print()
        
        output = self._run_git([
            "log",
            f"-n{limit}",
            "--pretty=format:%h|%an|%ad|%s",
            "--date=short"
        ])
        
        if not output.strip():
            self.info_box.info("Git Log", "没有提交历史")
            return
        
        table = Table(
            title=f"最近 {limit} 次提交",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True
        )
        table.add_column("Hash", style="yellow", width=10)
        table.add_column("作者", style="cyan", width=15)
        table.add_column("日期", style="white", width=12)
        table.add_column("说明", style="white")
        
        for line in output.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    hash, author, date, message = parts[0], parts[1], parts[2], '|'.join(parts[3:])
                    table.add_row(hash[:7], author[:15], date, message[:50])
        
        self.console.print(table)
        self.console.print()
    
    async def branch_management(self) -> None:
        """分支管理界面"""
        self.console.print()
        self.console.print("[bold cyan]=== Git 分支管理 ===[/bold cyan]")
        self.console.print()
        
        # 显示所有分支
        output = self._run_git(["branch", "-a"])
        
        table = Table(
            title="全部分支",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=False
        )
        table.add_column("分支", style="white")
        
        current_branch = self._run_git(["branch", "--show-current"]).strip()
        
        for line in output.strip().split('\n'):
            if line.strip():
                branch_name = line.strip().lstrip('* ').lstrip()
                is_current = branch_name == current_branch
                prefix = f"{EMOJI['branch']} " if is_current else "  "
                style = "bold green" if is_current else "white"
                table.add_row(f"{prefix}{branch_name}", style=style)
        
        self.console.print(table)
        self.console.print()
        
        # 快捷操作提示
        self.info_box.info(
            "分支操作",
            "创建分支：git checkout -b <branch>\n"
            "切换分支：git checkout <branch>\n"
            "删除分支：git branch -d <branch>"
        )
    
    async def execute(self, operation: str, **kwargs) -> str:
        """执行 Git 操作（增强版）"""
        operations = {
            "status_visual": lambda: self._status_visual(),
            "diff_visual": lambda: self._diff_visual(**kwargs),
            "commit_interactive": lambda: self.interactive_commit(),
            "log_visual": lambda: self.show_log_visual(**kwargs),
            "branch_management": lambda: self.branch_management(),
        }
        
        if operation not in operations:
            return f"错误：未知操作 {operation}"
        
        try:
            await operations[operation]()
            return "操作完成"
        except Exception as e:
            return f"Git 操作失败：{e}"
    
    def _status_visual(self) -> None:
        """可视化状态"""
        status_output = self._run_git(["status", "--short"])
        if not status_output.strip():
            self.info_box.success("Git Status", "工作区干净")
            return
        
        status = self.parse_status(status_output)
        self.show_status_visual(status)
    
    def _diff_visual(self, staged: bool = False, file: str = None) -> None:
        """可视化 diff"""
        args = ["diff"]
        if staged:
            args.append("--staged")
        if file:
            args.extend(["--", file])
        
        diff = self._run_git(args)
        self.show_diff_visual(diff)


# 导出以便使用
def create_enhanced_git_tool(console=None):
    """创建增强 Git 工具实例"""
    return EnhancedGitTool(console)
