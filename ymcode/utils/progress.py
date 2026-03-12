#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Tracker - 进度追踪

融合课程：生产级进度显示
"""

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from typing import Optional


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, console=None):
        """
        初始化进度追踪器
        
        参数:
            console: Rich Console 实例
        """
        self.console = console
        self.progress: Optional[Progress] = None
        self.task_id = None
    
    def start(self, description: str, total: int = None):
        """
        开始进度
        
        参数:
            description: 描述
            total: 总数（None 表示不确定）
        """
        if self.console:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(description, total=total)
    
    def update(self, completed: int = None, advance: int = None, description: str = None):
        """
        更新进度
        
        参数:
            completed: 完成的数量
            advance: 前进的数量
            description: 新描述
        """
        if self.progress and self.task_id:
            self.progress.update(
                self.task_id,
                completed=completed,
                advance=advance,
                description=description
            )
    
    def stop(self):
        """停止进度"""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.task_id = None
