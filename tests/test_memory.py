#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory 系统测试脚本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.memory import (
    SessionManager,
    ContextManager,
    ContextCompressor
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


def test_session_manager(results: TestResults):
    """测试会话管理器"""
    print("\n📋 第一部分：SessionManager 测试\n")
    
    # 测试 1: 创建管理器
    print("测试 1: 创建会话管理器")
    try:
        manager = SessionManager()
        results.record("创建 SessionManager", True)
    except Exception as e:
        results.record("创建 SessionManager", False, str(e))
        return
    
    # 测试 2: 创建会话
    print("\n测试 2: 创建会话")
    try:
        session = manager.create_session(metadata={'test': True})
        results.record(
            "创建会话",
            session.id is not None and len(session.messages) == 0,
            f"session_id={session.id}"
        )
    except Exception as e:
        results.record("创建会话", False, str(e))
    
    # 测试 3: 获取会话
    print("\n测试 3: 获取会话")
    try:
        session = manager.get_current_session()
        results.record(
            "获取当前会话",
            session is not None,
            f"session_id={session.id if session else None}"
        )
    except Exception as e:
        results.record("获取当前会话", False, str(e))
    
    # 测试 4: 添加消息
    print("\n测试 4: 添加消息")
    try:
        manager.add_message('user', '你好')
        manager.add_message('assistant', '你好！有什么可以帮助你的吗？')
        session = manager.get_current_session()
        results.record(
            "添加消息",
            len(session.messages) == 2,
            f"消息数={len(session.messages)}"
        )
    except Exception as e:
        results.record("添加消息", False, str(e))
    
    # 测试 5: 获取消息
    print("\n测试 5: 获取消息")
    try:
        messages = manager.get_messages()
        results.record(
            "获取消息",
            len(messages) == 2,
            f"消息数={len(messages)}"
        )
    except Exception as e:
        results.record("获取消息", False, str(e))
    
    # 测试 6: 列出会话
    print("\n测试 6: 列出会话")
    try:
        sessions = manager.list_sessions()
        results.record(
            "列出会话",
            len(sessions) > 0,
            f"会话数={len(sessions)}"
        )
    except Exception as e:
        results.record("列出会话", False, str(e))
    
    # 测试 7: 获取统计
    print("\n测试 7: 获取统计")
    try:
        stats = manager.get_stats()
        results.record(
            "获取统计",
            'total_sessions' in stats and 'total_messages' in stats,
            f"sessions={stats.get('total_sessions')}, messages={stats.get('total_messages')}"
        )
    except Exception as e:
        results.record("获取统计", False, str(e))
    
    # 测试 8: 清空消息
    print("\n测试 8: 清空消息")
    try:
        manager.clear_messages()
        session = manager.get_current_session()
        results.record(
            "清空消息",
            len(session.messages) == 0,
            f"消息数={len(session.messages)}"
        )
    except Exception as e:
        results.record("清空消息", False, str(e))


def test_context_manager(results: TestResults):
    """测试上下文管理器"""
    print("\n\n📋 第二部分：ContextManager 测试\n")
    
    # 测试 1: 创建管理器
    print("测试 1: 创建上下文管理器")
    try:
        manager = ContextManager(max_tokens=4000)
        results.record("创建 ContextManager", True)
    except Exception as e:
        results.record("创建 ContextManager", False, str(e))
        return
    
    # 测试 2: 添加消息
    print("\n测试 2: 添加消息")
    try:
        manager.add_message('user', '你好')
        manager.add_message('assistant', '你好！')
        results.record(
            "添加消息",
            len(manager.context_items) == 2,
            f"items={len(manager.context_items)}"
        )
    except Exception as e:
        results.record("添加消息", False, str(e))
    
    # 测试 3: 添加文件
    print("\n测试 3: 添加文件")
    try:
        manager.add_file('test.py', 'print("hello")')
        results.record(
            "添加文件",
            len(manager.context_items) == 3,
            f"items={len(manager.context_items)}"
        )
    except Exception as e:
        results.record("添加文件", False, str(e))
    
    # 测试 4: 添加代码
    print("\n测试 4: 添加代码")
    try:
        manager.add_code('python', 'def hello():\n    pass')
        results.record(
            "添加代码",
            len(manager.context_items) == 4,
            f"items={len(manager.context_items)}"
        )
    except Exception as e:
        results.record("添加代码", False, str(e))
    
    # 测试 5: 添加摘要
    print("\n测试 5: 添加摘要")
    try:
        manager.add_summary('这是对话摘要')
        results.record(
            "添加摘要",
            len(manager.context_items) == 5,
            f"items={len(manager.context_items)}"
        )
    except Exception as e:
        results.record("添加摘要", False, str(e))
    
    # 测试 6: 获取统计
    print("\n测试 6: 获取统计")
    try:
        stats = manager.get_stats()
        results.record(
            "获取统计",
            stats['total_items'] == 5 and 'usage_percent' in stats,
            f"items={stats['total_items']}, usage={stats['usage_percent']:.1f}%"
        )
    except Exception as e:
        results.record("获取统计", False, str(e))
    
    # 测试 7: 检查是否接近限制
    print("\n测试 7: 检查是否接近限制")
    try:
        is_near = manager.is_near_limit(0.8)
        results.record(
            "检查接近限制",
            isinstance(is_near, bool),
            f"is_near={is_near}"
        )
    except Exception as e:
        results.record("检查接近限制", False, str(e))
    
    # 测试 8: 获取可用 tokens
    print("\n测试 8: 获取可用 tokens")
    try:
        available = manager.get_available_tokens()
        results.record(
            "获取可用 tokens",
            available > 0,
            f"available={available}"
        )
    except Exception as e:
        results.record("获取可用 tokens", False, str(e))
    
    # 测试 9: 清空上下文
    print("\n测试 9: 清空上下文")
    try:
        manager.clear()
        results.record(
            "清空上下文",
            len(manager.context_items) == 0 and manager.current_tokens == 0,
            f"items={len(manager.context_items)}, tokens={manager.current_tokens}"
        )
    except Exception as e:
        results.record("清空上下文", False, str(e))


def test_context_compressor(results: TestResults):
    """测试上下文压缩器"""
    print("\n\n📋 第三部分：ContextCompressor 测试\n")
    
    # 测试 1: 创建压缩器
    print("测试 1: 创建压缩器")
    try:
        compressor = ContextCompressor()
        results.record("创建 ContextCompressor", True)
    except Exception as e:
        results.record("创建 ContextCompressor", False, str(e))
        return
    
    # 测试 2: 判断是否需要压缩
    print("\n测试 2: 判断是否需要压缩")
    try:
        need_compress = compressor.should_compress(3500, 4000)
        results.record(
            "判断需要压缩",
            need_compress == True,
            f"need_compress={need_compress}"
        )
    except Exception as e:
        results.record("判断是否需要压缩", False, str(e))
    
    # 测试 3: 判断不需要压缩
    print("\n测试 3: 判断不需要压缩")
    try:
        need_compress = compressor.should_compress(2000, 4000)
        results.record(
            "判断不需要压缩",
            need_compress == False,
            f"need_compress={need_compress}"
        )
    except Exception as e:
        results.record("判断不需要压缩", False, str(e))
    
    # 测试 4: 压缩消息
    print("\n测试 4: 压缩消息")
    try:
        messages = [
            {'role': 'user', 'content': '消息 1' * 100},
            {'role': 'assistant', 'content': '回复 1' * 100},
            {'role': 'user', 'content': '消息 2' * 100},
            {'role': 'assistant', 'content': '回复 2' * 100},
        ]
        result = compressor.compress_messages(messages, target_tokens=500)
        results.record(
            "压缩消息",
            result.compression_ratio >= 0 and result.compression_ratio <= 1,
            f"ratio={result.compression_ratio:.1%}"
        )
    except Exception as e:
        results.record("压缩消息", False, str(e))
    
    # 测试 5: 压缩统计
    print("\n测试 5: 压缩统计")
    try:
        stats = compressor.get_compression_stats()
        results.record(
            "压缩统计",
            'total_compressions' in stats,
            f"compressions={stats['total_compressions']}"
        )
    except Exception as e:
        results.record("压缩统计", False, str(e))


def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE Memory 系统测试")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    test_session_manager(results)
    test_context_manager(results)
    test_context_compressor(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    return results.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
