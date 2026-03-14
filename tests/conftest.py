#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest 配置文件
提供共享的 fixtures 和测试工具
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.cli.panels import WelcomePanel, StatusPanel, ProgressPanel, InfoPanel, HelpPanel
from ymcode.skills.shell import ShellSkill
from ymcode.skills.memory import MemorySkill
from ymcode.skills.http import HTTPSkill
from ymcode.skills.search import SearchSkill
from ymcode.skills.formatter import FormatterSkill
from ymcode.skills.code_analysis import CodeAnalysisSkill
from ymcode.core.agent import Agent
from ymcode.mcp import get_registry as get_mcp_registry
from ymcode.skills import get_registry as get_skills_registry


class TestResults:
    """测试结果追踪（兼容旧测试）"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []
    
    def record(self, name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.details.append({"name": name, "passed": passed, "details": details})
        return passed
    
    def summary(self):
        """打印总结"""
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        return {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "rate": rate
        }


@pytest.fixture
def results():
    """提供测试结果追踪器"""
    return TestResults()


@pytest.fixture
def welcome_panel():
    """提供 WelcomePanel 实例"""
    return WelcomePanel(version="1.0.0")


@pytest.fixture
def status_panel():
    """提供 StatusPanel 实例"""
    return StatusPanel()


@pytest.fixture
def progress_panel():
    """提供 ProgressPanel 实例"""
    return ProgressPanel()


@pytest.fixture
def info_panel():
    """提供 InfoPanel 实例"""
    return InfoPanel()


@pytest.fixture
def help_panel():
    """提供 HelpPanel 实例"""
    return HelpPanel()


@pytest.fixture
def shell_skill():
    """提供 ShellSkill 实例"""
    return ShellSkill()


@pytest.fixture
def memory_skill():
    """提供 MemorySkill 实例"""
    return MemorySkill()


@pytest.fixture
def http_skill():
    """提供 HTTPSkill 实例"""
    return HTTPSkill()


@pytest.fixture
def search_skill():
    """提供 SearchSkill 实例"""
    return SearchSkill()


@pytest.fixture
def formatter_skill():
    """提供 FormatterSkill 实例"""
    return FormatterSkill()


@pytest.fixture
def code_analysis_skill():
    """提供 CodeAnalysisSkill 实例"""
    return CodeAnalysisSkill()


@pytest.fixture
def agent():
    """提供 Agent 实例"""
    return Agent(config={'max_iterations': 3, 'timeout': 30})


@pytest.fixture
def mcp_registry():
    """提供 MCP Registry 实例"""
    return get_mcp_registry()


@pytest.fixture
def skills_registry():
    """提供 Skills Registry 实例"""
    return get_skills_registry()


@pytest.fixture
def temp_file(tmp_path):
    """创建临时文件"""
    file = tmp_path / "test.txt"
    file.write_text("test content")
    return file


@pytest.fixture
def temp_python_file(tmp_path):
    """创建临时 Python 文件"""
    file = tmp_path / "test.py"
    file.write_text("def hello():\n    print('hello')\n")
    return file


@pytest.fixture
def sample_code():
    """示例代码"""
    return """
def calculate_sum(numbers):
    '''计算总和'''
    return sum(numbers)

class Calculator:
    '''计算器类'''
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""


@pytest.fixture
def sample_project_dir(tmp_path):
    """创建示例项目目录"""
    # 创建目录结构
    src = tmp_path / "src"
    src.mkdir()
    
    tests = tmp_path / "tests"
    tests.mkdir()
    
    # 创建文件
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "main.py").write_text("print('hello')")
    (src / "utils.py").write_text("def helper(): pass")
    (tests / "test_main.py").write_text("def test_main(): pass")
    
    return tmp_path
