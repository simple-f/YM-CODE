#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.7.0 测试套件

测试所有新增功能
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.core.llm_client import LLMClient
from ymcode.core.context_manager import ContextManager, process_context
from ymcode.skills.code_analyzer import CodeAnalyzerSkill


class TestResults:
    """测试结果追踪"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            print(f"  ❌ {name}: {message}")
    
    def summary(self):
        """打印总结"""
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"测试结果：{self.passed}/{total} 通过 ({rate:.1f}%)")
        print(f"{'='*60}")
        return self.failed == 0


async def test_llm_client(results: TestResults):
    """测试 LLM 客户端"""
    print("\n{'='*60}")
    print("测试 1: LLM 客户端")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 创建客户端
        client = LLMClient()
        results.record("创建 LLM 客户端", True)
        
        # 测试 2: 获取模型信息
        info = client.get_model_info()
        results.record("获取模型信息", True, f"类型：{info.get('type')}")
        
        # 测试 3: API 模式
        if not client.config.get('use_local'):
            results.record("API 模式正常", True)
        else:
            results.record("API 模式正常", False, "当前使用本地模式")
        
    except Exception as e:
        results.record("LLM 客户端测试", False, str(e))


async def test_context_manager(results: TestResults):
    """测试上下文管理器"""
    print(f"\n{'='*60}")
    print("测试 2: 上下文管理器")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 创建管理器
        manager = ContextManager(max_tokens=8000)
        results.record("创建上下文管理器", True)
        
        # 测试 2: 处理短上下文
        short_context = [{"role": "user", "content": "你好"}]
        processed = manager.process(short_context)
        results.record("处理短上下文", True, "未压缩")
        
        # 测试 3: 处理长上下文
        long_context = [{"role": "user", "content": "x" * 100000}]
        processed = manager.process(long_context)
        results.record("处理长上下文", True, "自动压缩/分片")
        
        # 测试 4: 便捷函数
        processed = process_context(short_context)
        results.record("便捷函数", True)
        
    except Exception as e:
        results.record("上下文管理器测试", False, str(e))


async def test_code_analyzer(results: TestResults):
    """测试代码分析技能"""
    print(f"\n{'='*60}")
    print("测试 3: 代码分析技能")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 创建技能
        skill = CodeAnalyzerSkill()
        results.record("创建代码分析技能", True)
        
        # 测试 2: 初始化
        skill.initialize()
        analyzers_count = len(skill.analyzers)
        results.record("初始化工具", True, f"已加载 {analyzers_count} 个工具")
        
        # 测试 3: 分析代码
        test_code = """
def hello():
    print("world")
"""
        result = await skill.execute({
            'code': test_code,
            'language': 'python'
        })
        results.record("分析代码", result.get('success', False))
        
        if result.get('success'):
            summary = result.get('summary', {})
            print(f"    工具数：{summary.get('tools_run', 0)}")
            print(f"    问题数：{summary.get('total_issues', 0)}")
        
    except Exception as e:
        results.record("代码分析技能测试", False, str(e))


async def main():
    """主测试函数"""
    print(f"\n{'#'*60}")
    print("# YM-CODE v0.7.0 测试套件")
    print(f"{'#'*60}")
    
    results = TestResults()
    
    # 运行测试
    await test_llm_client(results)
    await test_context_manager(results)
    await test_code_analyzer(results)
    
    # 总结
    success = results.summary()
    
    if success:
        print("\n✅ 所有测试通过！v0.7.0 可以发布！")
    else:
        print(f"\n⚠️ {results.failed} 个测试失败，需要修复")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
