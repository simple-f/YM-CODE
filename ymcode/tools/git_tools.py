#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Tools - Git 操作工具集

融合课程：s02 (Tool Use) + 生产级 Git 集成
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from .base import BaseTool


class GitTool(BaseTool):
    """Git 工具基类"""
    
    name = "git"
    description = "Git 版本控制操作"
    
    async def execute(self, operation: str, **kwargs) -> str:
        """
        执行 Git 操作
        
        参数:
            operation: 操作名（status/diff/commit/push/log）
            **kwargs: 操作参数
        
        返回:
            执行结果
        """
        operations = {
            "status": self._git_status,
            "diff": self._git_diff,
            "commit": self._git_commit,
            "push": self._git_push,
            "log": self._git_log,
            "branch": self._git_branch,
            "checkout": self._git_checkout,
            "add": self._git_add,
        }
        
        if operation not in operations:
            return f"错误：未知操作 {operation}"
        
        try:
            return await operations[operation](**kwargs)
        except Exception as e:
            return f"Git 操作失败：{e}"
    
    def _run_git(self, args: List[str], check: bool = False) -> str:
        """
        运行 Git 命令
        
        参数:
            args: Git 参数列表
            check: 是否检查返回码
        
        返回:
            命令输出
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=check,
                timeout=30
            )
            
            if result.returncode != 0 and check:
                return f"错误：{result.stderr}"
            
            return result.stdout or "操作成功"
            
        except subprocess.TimeoutExpired:
            return "错误：命令超时（>30 秒）"
        except FileNotFoundError:
            return "错误：未找到 git 命令，请确认已安装 Git"
    
    async def _git_status(self) -> str:
        """Git status"""
        return self._run_git(["status", "--short"])
    
    async def _git_diff(self, staged: bool = False) -> str:
        """Git diff"""
        args = ["diff"]
        if staged:
            args.append("--staged")
        return self._run_git(args)
    
    async def _git_commit(self, message: str, all_files: bool = False) -> str:
        """
        Git commit
        
        参数:
            message: 提交信息
            all_files: 是否包含所有修改
        """
        if not message:
            return "错误：提交信息不能为空"
        
        args = ["commit", "-m", message]
        if all_files:
            args.insert(1, "-a")
        
        return self._run_git(args, check=True)
    
    async def _git_push(self, remote: str = "origin", branch: str = None) -> str:
        """
        Git push
        
        参数:
            remote: 远程仓库名
            branch: 分支名
        """
        args = ["push"]
        
        if remote:
            args.append(remote)
        
        if branch:
            args.append(branch)
        
        return self._run_git(args, check=True)
    
    async def _git_log(self, count: int = 5) -> str:
        """
        Git log
        
        参数:
            count: 显示数量
        """
        args = ["log", f"-{min(count, 20)}", "--oneline"]
        return self._run_git(args)
    
    async def _git_branch(self) -> str:
        """Git branch"""
        return self._run_git(["branch", "-a"])
    
    async def _git_checkout(self, branch: str, create: bool = False) -> str:
        """
        Git checkout
        
        参数:
            branch: 分支名
            create: 是否创建新分支
        """
        args = ["checkout"]
        if create:
            args.append("-b")
        args.append(branch)
        
        return self._run_git(args, check=True)
    
    async def _git_add(self, path: str = ".") -> str:
        """
        Git add
        
        参数:
            path: 文件路径
        """
        return self._run_git(["add", path], check=True)
    
    def get_input_schema(self) -> Dict:
        """获取输入 schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Git 操作",
                    "enum": ["status", "diff", "commit", "push", "log", "branch", "checkout", "add"]
                },
                "message": {
                    "type": "string",
                    "description": "提交信息（commit 操作需要）"
                },
                "path": {
                    "type": "string",
                    "description": "文件路径（add 操作需要）"
                },
                "branch": {
                    "type": "string",
                    "description": "分支名"
                },
                "remote": {
                    "type": "string",
                    "description": "远程仓库名"
                },
                "staged": {
                    "type": "boolean",
                    "description": "是否查看暂存区差异"
                },
                "all_files": {
                    "type": "boolean",
                    "description": "是否包含所有修改"
                },
                "count": {
                    "type": "integer",
                    "description": "日志显示数量"
                },
                "create": {
                    "type": "boolean",
                    "description": "是否创建新分支"
                }
            },
            "required": ["operation"]
        }


class GitStatusTool(BaseTool):
    """Git Status 快捷工具"""
    
    name = "git_status"
    description = "查看 Git 状态"
    
    async def execute(self) -> str:
        """执行 Git status"""
        git_tool = GitTool()
        return await git_tool.execute("status")


class GitDiffTool(BaseTool):
    """Git Diff 快捷工具"""
    
    name = "git_diff"
    description = "查看 Git 差异"
    
    async def execute(self, staged: bool = False) -> str:
        """
        执行 Git diff
        
        参数:
            staged: 是否查看暂存区
        """
        git_tool = GitTool()
        return await git_tool.execute("diff", staged=staged)


class GitCommitTool(BaseTool):
    """Git Commit 快捷工具"""
    
    name = "git_commit"
    description = "Git 提交"
    
    async def execute(self, message: str, all_files: bool = False) -> str:
        """
        执行 Git commit
        
        参数:
            message: 提交信息
            all_files: 是否包含所有修改
        """
        git_tool = GitTool()
        return await git_tool.execute("commit", message=message, all_files=all_files)
