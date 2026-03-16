#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Test Runner - 增强测试运行器（智能分析 + 修复建议）
"""

import subprocess
import asyncio
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from ..cli.enhanced import InfoBox, TaskPanel, StatsTable


class ErrorType(Enum):
    """错误类型"""
    ASSERTION = "assertion"
    SYNTAX = "syntax"
    IMPORT = "import"
    NAME = "name"
    TYPE = "type"
    ATTRIBUTE = "attribute"
    KEY = "key"
    INDEX = "index"
    VALUE = "value"
    RUNTIME = "runtime"
    TIMEOUT = "timeout"
    OTHER = "other"


@dataclass
class TestFailure:
    """测试失败详情"""
    test_name: str
    file_path: str
    line_number: int
    error_type: ErrorType
    error_message: str
    expected: str = ""
    actual: str = ""
    suggestion: str = ""


@dataclass
class TestResult:
    """测试结果（增强版）"""
    passed: bool
    total: int = 0
    passed_count: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    output: str = ""
    duration: float = 0.0
    failure_details: List[TestFailure] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class EnhancedTestRunner:
    """增强的测试运行器（智能分析 + 修复建议）"""
    
    def __init__(self, console: Optional[Console] = None):
        if hasattr(console, 'force_terminal'):
            self.console = console or Console()
        else:
            self.console = console or Console(force_terminal=True, color_system="basic")
        self.info_box = InfoBox(self.console)
        
        # 错误模式匹配
        self.error_patterns = {
            ErrorType.ASSERTION: (
                r'AssertionError[:\s]*(.*?)\n',
                r'assert (.+?)\n',
                r'Expected:?(.*?)\n.*?Actual:?(.*?)\n',
            ),
            ErrorType.SYNTAX: (
                r'SyntaxError[:\s]*(.*?)\n',
                r'invalid syntax',
            ),
            ErrorType.IMPORT: (
                r'ImportError[:\s]*(.*?)\n',
                r'ModuleNotFoundError.*?No module named [\'"](.+?)[\'"]',
            ),
            ErrorType.NAME: (
                r'NameError[:\s]*(.*?)\n',
                r'name [\'"](.+?)[\'"] is not defined',
            ),
            ErrorType.TYPE: (
                r'TypeError[:\s]*(.*?)\n',
            ),
            ErrorType.ATTRIBUTE: (
                r'AttributeError[:\s]*(.*?)\n',
                r'[\'"](.+?)[\'"] object has no attribute [\'"](.+?)[\'"]',
            ),
        }
        
        # 修复建议模板
        self.suggestion_templates = {
            ErrorType.ASSERTION: [
                "检查断言条件是否正确",
                "验证输入数据是否符合预期",
                "确认函数返回值是否正确",
            ],
            ErrorType.SYNTAX: [
                "检查语法错误（缺少括号、冒号等）",
                "验证缩进是否正确",
                "检查关键字拼写",
            ],
            ErrorType.IMPORT: [
                "确认模块已安装：pip install <module>",
                "检查导入路径是否正确",
                "验证 __init__.py 是否存在",
            ],
            ErrorType.NAME: [
                "检查变量是否已定义",
                "验证拼写是否正确",
                "确认作用域是否正确",
            ],
            ErrorType.ATTRIBUTE: [
                "检查对象是否有该属性",
                "验证类定义是否完整",
                "确认是否拼写错误",
            ],
        }
    
    async def run_tests(
        self,
        test_path: str = ".",
        framework: str = "pytest",
        verbose: bool = True,
        auto_fix: bool = False
    ) -> TestResult:
        """
        运行测试（增强版）
        
        参数:
            test_path: 测试路径
            framework: 测试框架
            verbose: 是否详细输出
            auto_fix: 是否自动修复
        
        返回:
            测试结果（包含详细分析和修复建议）
        """
        import time
        start_time = time.time()
        
        args = ["pytest"]
        
        if verbose:
            args.append("-v")
        
        args.extend([
            test_path,
            "--tb=short",  # 简化 traceback
            "--color=no",  # 禁用颜色（我们自己处理）
        ])
        
        try:
            result = await asyncio.create_subprocess_exec(
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            duration = time.time() - start_time
            
            # 解析输出
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            full_output = output + error_output
            
            # 解析测试结果
            total, passed_count, failures, errors, skipped = self._parse_pytest_output(output)
            
            # 解析失败详情
            failure_details = self._parse_failures(full_output)
            
            # 生成修复建议
            suggestions = self._generate_suggestions(failure_details)
            
            return TestResult(
                passed=result.returncode == 0,
                total=total,
                passed_count=passed_count,
                failures=failures,
                errors=errors,
                skipped=skipped,
                output=full_output,
                duration=duration,
                failure_details=failure_details,
                suggestions=suggestions
            )
            
        except asyncio.TimeoutError:
            return TestResult(
                passed=False,
                output="测试超时（>60 秒）",
                suggestions=["优化测试代码，减少执行时间"]
            )
        except FileNotFoundError:
            return TestResult(
                passed=False,
                output="未找到 pytest 命令，请确认已安装：pip install pytest",
                suggestions=["安装 pytest: pip install pytest"]
            )
    
    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int, int, int]:
        """解析 pytest 输出"""
        total = 0
        passed_count = 0
        failures = 0
        errors = 0
        skipped = 0
        
        # 匹配测试数量
        total_match = re.search(r'(\d+) tests? run', output, re.IGNORECASE)
        if total_match:
            total = int(total_match.group(1))
        
        # 匹配通过数量
        passed_match = re.search(r'(\d+) passed', output)
        if passed_match:
            passed_count = int(passed_match.group(1))
        
        # 匹配失败数量
        failed_match = re.search(r'(\d+) failed', output)
        if failed_match:
            failures = int(failed_match.group(1))
        
        # 匹配错误数量
        error_match = re.search(r'(\d+) errors?', output)
        if error_match:
            errors = int(error_match.group(1))
        
        # 匹配跳过数量
        skipped_match = re.search(r'(\d+) skipped', output)
        if skipped_match:
            skipped = int(skipped_match.group(1))
        
        # 如果没有明确数量，从测试行推断
        if total == 0:
            test_lines = len(re.findall(r'TEST.*?PASSED|FAILED|ERROR|SKIPPED', output, re.IGNORECASE))
            if test_lines > 0:
                total = test_lines
                passed_count = len(re.findall(r'PASSED', output))
                failures = len(re.findall(r'FAILED', output))
                errors = len(re.findall(r'ERROR', output))
                skipped = len(re.findall(r'SKIPPED', output))
        
        return total, passed_count, failures, errors, skipped
    
    def _parse_failures(self, output: str) -> List[TestFailure]:
        """解析失败详情"""
        failures = []
        
        # 分割失败信息
        failure_blocks = re.split(r'_(FAILED|ERROR)_', output)
        
        for block in failure_blocks:
            if 'FAILED' in block or 'ERROR' in block:
                failure = self._parse_single_failure(block)
                if failure:
                    failures.append(failure)
        
        return failures
    
    def _parse_single_failure(self, block: str) -> Optional[TestFailure]:
        """解析单个失败"""
        # 提取测试名称
        test_match = re.search(r'TEST (.+?) (FAILED|ERROR)', block)
        if not test_match:
            return None
        
        test_name = test_match.group(1)
        
        # 提取文件路径和行号
        file_match = re.search(r'File "(.+?)", line (\d+)', block)
        if file_match:
            file_path = file_match.group(1)
            line_number = int(file_match.group(2))
        else:
            file_path = "unknown"
            line_number = 0
        
        # 提取错误信息
        error_message = ""
        error_type = ErrorType.OTHER
        
        for err_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, block, re.IGNORECASE)
                if match:
                    error_type = err_type
                    error_message = match.group(0) if match else "未知错误"
                    break
            if error_type != ErrorType.OTHER:
                break
        
        if not error_message:
            # 提取第一行错误信息
            lines = block.strip().split('\n')
            for line in lines:
                if 'AssertionError' in line or 'Error' in line:
                    error_message = line.strip()
                    break
        
        # 提取期望/实际值（针对 assertion）
        expected = ""
        actual = ""
        if error_type == ErrorType.ASSERTION:
            exp_match = re.search(r'Expected:?(.+?)(?:\n|$)', block, re.IGNORECASE)
            act_match = re.search(r'Actual:?(.+?)(?:\n|$)', block, re.IGNORECASE)
            if exp_match:
                expected = exp_match.group(1).strip()
            if act_match:
                actual = act_match.group(1).strip()
        
        # 生成修复建议
        suggestion = self._get_suggestion(error_type, block)
        
        return TestFailure(
            test_name=test_name,
            file_path=file_path,
            line_number=line_number,
            error_type=error_type,
            error_message=error_message,
            expected=expected,
            actual=actual,
            suggestion=suggestion
        )
    
    def _get_suggestion(self, error_type: ErrorType, context: str) -> str:
        """获取修复建议"""
        suggestions = self.suggestion_templates.get(error_type, ["检查代码逻辑"])
        
        # 根据上下文选择最相关的建议
        if error_type == ErrorType.IMPORT:
            module_match = re.search(r'No module named [\'"](.+?)[\'"]', context)
            if module_match:
                module_name = module_match.group(1)
                return f"安装缺失模块：pip install {module_name}"
        
        if error_type == ErrorType.ASSERTION:
            if 'None' in context:
                return "检查函数是否返回了预期值（可能返回了 None）"
            if '0' in context or 'False' in context:
                return "检查边界条件处理是否正确"
        
        # 返回第一个建议
        return suggestions[0] if suggestions else "检查代码逻辑"
    
    def _generate_suggestions(self, failures: List[TestFailure]) -> List[str]:
        """生成总体修复建议"""
        suggestions = []
        
        # 按错误类型分组
        error_types = {}
        for failure in failures:
            error_types[failure.error_type] = error_types.get(failure.error_type, 0) + 1
        
        # 生成建议
        if ErrorType.ASSERTION in error_types:
            count = error_types[ErrorType.ASSERTION]
            suggestions.append(f"有 {count} 个断言失败，检查测试用例和实现逻辑")
        
        if ErrorType.IMPORT in error_types:
            suggestions.append("有导入错误，确认依赖已安装")
        
        if ErrorType.SYNTAX in error_types:
            suggestions.append("有语法错误，优先修复语法问题")
        
        if len(failures) > 10:
            suggestions.append("失败较多，建议先修复共性问题")
        
        if not suggestions:
            suggestions.append("查看失败详情，逐个修复")
        
        return suggestions
    
    def show_visual_report(self, result: TestResult) -> None:
        """可视化测试报告"""
        self.console.print()
        
        # 标题面板
        title = "✅ 测试通过" if result.passed else "❌ 测试失败"
        style = "green" if result.passed else "red"
        
        header = Text()
        header.append(f"{title}\n", style=f"bold {style}")
        header.append(f"总计：{result.total} | 通过：{result.passed_count} | 失败：{result.failures} | 错误：{result.errors}", style="white")
        
        if result.duration > 0:
            header.append(f" | 耗时：{result.duration:.1f}秒", style="dim")
        
        self.console.print(Panel(header, border_style=style, box=box.ROUNDED))
        self.console.print()
        
        # 统计表格
        stats = {
            "总测试数": str(result.total),
            "通过": str(result.passed_count),
            "失败": str(result.failures),
            "错误": str(result.errors),
        }
        
        if result.skipped > 0:
            stats["跳过"] = str(result.skipped)
        
        stats_table = StatsTable(self.console)
        stats_table.show("测试统计", stats)
        
        # 失败详情
        if result.failure_details:
            self.console.print()
            self.console.print(f"[bold red]失败详情 ({len(result.failure_details)} 个)[/bold red]")
            self.console.print()
            
            for i, failure in enumerate(result.failure_details[:5], 1):  # 只显示前 5 个
                panel = Panel(
                    Text(
                        f"测试：{failure.test_name}\n"
                        f"文件：{failure.file_path}:{failure.line_number}\n"
                        f"类型：{failure.error_type.value}\n"
                        f"错误：{failure.error_message[:100]}\n"
                        f"\n"
                        f"[dim]建议：{failure.suggestion}[/dim]",
                        style="white"
                    ),
                    title=f"失败 #{i}",
                    border_style="red",
                    box=box.ROUNDED
                )
                self.console.print(panel)
                self.console.print()
            
            if len(result.failure_details) > 5:
                self.console.print(f"[dim]... 还有 {len(result.failure_details) - 5} 个失败[/dim]\n")
        
        # 修复建议
        if result.suggestions:
            self.console.print()
            self.console.print(f"[bold yellow]修复建议[/bold yellow]")
            self.console.print()
            
            for suggestion in result.suggestions:
                self.console.print(f"  • {suggestion}")
            
            self.console.print()
    
    async def auto_fix(self, result: TestResult) -> Dict[str, bool]:
        """
        自动修复（实验性）
        
        参数:
            result: 测试结果
        
        返回:
            修复结果 {file_path: success}
        """
        fixes = {}
        
        for failure in result.failure_details:
            if failure.error_type == ErrorType.IMPORT:
                # 尝试安装缺失模块
                module_match = re.search(r'No module named [\'"](.+?)[\'"]', failure.error_message)
                if module_match:
                    module_name = module_match.group(1)
                    self.console.print(f"[yellow]正在安装缺失模块：{module_name}...[/yellow]")
                    
                    try:
                        proc = await asyncio.create_subprocess_exec(
                            "pip", "install", module_name,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        stdout, stderr = await proc.communicate()
                        
                        if proc.returncode == 0:
                            fixes[failure.file_path] = True
                            self.console.print(f"[green]✓ {module_name} 安装成功[/green]")
                        else:
                            fixes[failure.file_path] = False
                    except Exception as e:
                        fixes[failure.file_path] = False
            
            elif failure.error_type == ErrorType.SYNTAX:
                # 语法错误无法自动修复
                fixes[failure.file_path] = False
        
        return fixes


# 导出以便使用
def create_enhanced_test_runner(console=None):
    """创建增强测试运行器实例"""
    return EnhancedTestRunner(console)
