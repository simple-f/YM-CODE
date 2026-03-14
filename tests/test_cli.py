#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 测试脚本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.cli.panels import (
    WelcomePanel,
    StatusPanel,
    ProgressPanel,
    InfoPanel,
    HelpPanel
)
from ymcode.utils.logger import get_logger

logger = get_logger(__name__)


class TestResults:
    """测试结果追踪"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []
    
    def record(self, name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            print(f"  ❌ {name}: {details}")
        self.details.append({"name": name, "passed": passed, "details": details})
    
    def summary(self):
        """打印总结"""
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n📊 测试结果：{self.passed}/{total} 通过 ({rate:.1f}%)")
        
        if self.failed > 0:
            print("\n❌ 失败的测试:")
            for d in self.details:
                if not d["passed"]:
                    print(f"  - {d['name']}: {d['details']}")
        else:
            print("\n🎉 全部通过！")


def test_welcome_panel(results: TestResults):
    """测试欢迎面板"""
    print("\n📋 第一部分：WelcomePanel 测试\n")
    
    # 测试 1: 创建面板
    print("测试 1: 创建欢迎面板")
    try:
        panel = WelcomePanel(version="1.0.0")
        results.record("创建 WelcomePanel", True)
    except Exception as e:
        results.record("创建 WelcomePanel", False, str(e))
        return
    
    # 测试 2: 渲染面板
    print("\n测试 2: 渲染面板")
    try:
        rendered = panel.render()
        results.record(
            "渲染面板",
            rendered is not None and str(rendered.title) != "",
            f"title={rendered.title}"
        )
    except Exception as e:
        results.record("渲染面板", False, str(e))
    
    # 测试 3: 版本信息
    print("\n测试 3: 版本信息")
    try:
        rendered = panel.render()
        results.record(
            "版本信息显示",
            "1.0.0" in str(rendered.renderable),
            "版本包含在渲染内容中"
        )
    except Exception as e:
        results.record("版本信息", False, str(e))


def test_status_panel(results: TestResults):
    """测试状态面板"""
    print("\n\n📋 第二部分：StatusPanel 测试\n")
    
    # 测试 1: 创建面板
    print("测试 1: 创建状态面板")
    try:
        panel = StatusPanel()
        results.record("创建 StatusPanel", True)
    except Exception as e:
        results.record("创建 StatusPanel", False, str(e))
        return
    
    # 测试 2: 更新状态
    print("\n测试 2: 更新状态")
    try:
        panel.update("MCP Servers", "5")
        panel.update("Skills", "6")
        results.record(
            "更新状态",
            len(panel.status_info) == 2,
            f"状态数={len(panel.status_info)}"
        )
    except Exception as e:
        results.record("更新状态", False, str(e))
    
    # 测试 3: 渲染面板
    print("\n测试 3: 渲染面板")
    try:
        rendered = panel.render()
        results.record(
            "渲染状态面板",
            rendered is not None,
            "面板渲染成功"
        )
    except Exception as e:
        results.record("渲染状态面板", False, str(e))


def test_progress_panel(results: TestResults):
    """测试进度面板"""
    print("\n\n📋 第三部分：ProgressPanel 测试\n")
    
    # 测试 1: 创建面板
    print("测试 1: 创建进度面板")
    try:
        panel = ProgressPanel()
        results.record("创建 ProgressPanel", True)
    except Exception as e:
        results.record("创建 ProgressPanel", False, str(e))
        return
    
    # 测试 2: 开始任务
    print("\n测试 2: 开始任务")
    try:
        panel.start_task("测试任务")
        results.record(
            "开始任务",
            panel.current_task == "测试任务" and panel.status == "running",
            f"task={panel.current_task}, status={panel.status}"
        )
    except Exception as e:
        results.record("开始任务", False, str(e))
    
    # 测试 3: 更新进度
    print("\n测试 3: 更新进度")
    try:
        panel.update_progress(50, "running")
        results.record(
            "更新进度",
            panel.progress == 50,
            f"progress={panel.progress}%"
        )
    except Exception as e:
        results.record("更新进度", False, str(e))
    
    # 测试 4: 完成任务
    print("\n测试 4: 完成任务")
    try:
        panel.complete_task()
        results.record(
            "完成任务",
            panel.progress == 100 and panel.status == "completed",
            f"progress={panel.progress}%, status={panel.status}"
        )
    except Exception as e:
        results.record("完成任务", False, str(e))
    
    # 测试 5: 状态显示
    print("\n测试 5: 状态显示")
    try:
        status_text = panel.display_status()
        results.record(
            "状态显示",
            len(status_text) > 0,
            f"status_text={status_text}"
        )
    except Exception as e:
        results.record("状态显示", False, str(e))


def test_info_panel(results: TestResults):
    """测试信息面板"""
    print("\n\n📋 第四部分：InfoPanel 测试\n")
    
    # 测试 1: 创建面板
    print("测试 1: 创建信息面板")
    try:
        panel = InfoPanel()
        results.record("创建 InfoPanel", True)
    except Exception as e:
        results.record("创建 InfoPanel", False, str(e))
        return
    
    # 测试 2: 添加消息
    print("\n测试 2: 添加消息")
    try:
        panel.add_message("测试消息", "white")
        results.record(
            "添加消息",
            len(panel.messages) == 1,
            f"消息数={len(panel.messages)}"
        )
    except Exception as e:
        results.record("添加消息", False, str(e))
    
    # 测试 3: 添加成功消息
    print("\n测试 3: 添加成功消息")
    try:
        panel.add_success("操作成功")
        results.record(
            "添加成功消息",
            len(panel.messages) == 2 and "✅" in panel.messages[1][0],
            f"消息数={len(panel.messages)}"
        )
    except Exception as e:
        results.record("添加成功消息", False, str(e))
    
    # 测试 4: 添加错误消息
    print("\n测试 4: 添加错误消息")
    try:
        panel.add_error("操作失败")
        results.record(
            "添加错误消息",
            len(panel.messages) == 3 and "❌" in panel.messages[2][0],
            f"消息数={len(panel.messages)}"
        )
    except Exception as e:
        results.record("添加错误消息", False, str(e))
    
    # 测试 5: 添加警告消息
    print("\n测试 5: 添加警告消息")
    try:
        panel.add_warning("注意风险")
        results.record(
            "添加警告消息",
            len(panel.messages) == 4 and "⚠️" in panel.messages[3][0],
            f"消息数={len(panel.messages)}"
        )
    except Exception as e:
        results.record("添加警告消息", False, str(e))
    
    # 测试 6: 渲染面板
    print("\n测试 6: 渲染面板")
    try:
        rendered = panel.render()
        results.record(
            "渲染信息面板",
            rendered is not None,
            "面板渲染成功"
        )
    except Exception as e:
        results.record("渲染信息面板", False, str(e))
    
    # 测试 7: 清空消息
    print("\n测试 7: 清空消息")
    try:
        panel.clear()
        results.record(
            "清空消息",
            len(panel.messages) == 0,
            f"消息数={len(panel.messages)}"
        )
    except Exception as e:
        results.record("清空消息", False, str(e))


def test_help_panel(results: TestResults):
    """测试帮助面板"""
    print("\n\n📋 第五部分：HelpPanel 测试\n")
    
    # 测试 1: 创建面板
    print("测试 1: 创建帮助面板")
    try:
        panel = HelpPanel()
        results.record("创建 HelpPanel", True)
    except Exception as e:
        results.record("创建 HelpPanel", False, str(e))
        return
    
    # 测试 2: 命令列表
    print("\n测试 2: 命令列表")
    try:
        commands = panel.commands
        results.record(
            "命令列表",
            len(commands) > 5,
            f"命令数={len(commands)}"
        )
    except Exception as e:
        results.record("命令列表", False, str(e))
    
    # 测试 3: 渲染面板
    print("\n测试 3: 渲染面板")
    try:
        rendered = panel.render()
        results.record(
            "渲染帮助面板",
            rendered is not None,
            "面板渲染成功"
        )
    except Exception as e:
        results.record("渲染帮助面板", False, str(e))


def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE CLI 组件测试")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    test_welcome_panel(results)
    test_status_panel(results)
    test_progress_panel(results)
    test_info_panel(results)
    test_help_panel(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    return results.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
