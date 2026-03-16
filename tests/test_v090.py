#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.9.0 测试套件

测试所有新增功能
"""

import sys
import asyncio
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.skills.multi_language import MultiLanguageSkill
from ymcode.skills.code_runner import CodeRunnerSkill
from ymcode.utils.performance import (
    Cache, get_cache, cached,
    AsyncBatchProcessor, PerformanceMonitor, timed,
    async_map, cache_clear, cache_stats
)


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


async def test_multi_language(results: TestResults):
    """测试多语言支持"""
    print(f"\n{'='*60}")
    print("测试 1: 多语言支持")
    print(f"{'='*60}")
    
    try:
        skill = MultiLanguageSkill()
        results.record("创建多语言技能", True)
        
        # JavaScript 分析
        js_code = "function hello() { console.log('world'); }"
        result = await skill.execute({
            'code': js_code,
            'language': 'javascript',
            'action': 'analyze'
        })
        results.record("JavaScript 分析", result.get('success', False))
        
        # TypeScript 分析
        ts_code = "interface User { name: string; }"
        result = await skill.execute({
            'code': ts_code,
            'language': 'typescript',
            'action': 'analyze'
        })
        results.record("TypeScript 分析", result.get('success', False))
        
        # Java 分析
        java_code = "public class Main { public static void main(String[] args) {} }"
        result = await skill.execute({
            'code': java_code,
            'language': 'java',
            'action': 'analyze'
        })
        results.record("Java 分析", result.get('success', False))
        
        # Go 分析
        go_code = "func main() { fmt.Println(\"hello\") }"
        result = await skill.execute({
            'code': go_code,
            'language': 'go',
            'action': 'analyze'
        })
        results.record("Go 分析", result.get('success', False))
        
        # 语言检测
        result = await skill.execute({
            'code': js_code,
            'action': 'detect'
        })
        results.record("语言检测", result.get('success', False))
        
    except Exception as e:
        results.record("多语言测试", False, str(e))


async def test_code_runner(results: TestResults):
    """测试代码运行"""
    print(f"\n{'='*60}")
    print("测试 2: 代码运行")
    print(f"{'='*60}")
    
    try:
        skill = CodeRunnerSkill()
        results.record("创建代码运行技能", True)
        
        # Python 代码执行
        result = await skill.execute({
            'code': 'print("Hello, World!")',
            'language': 'python'
        })
        results.record("Python 代码执行", result.get('success', False))
        
        # JavaScript 代码执行
        result = await skill.execute({
            'code': 'console.log("Hello, World!");',
            'language': 'javascript'
        })
        results.record("JavaScript 代码执行", result.get('success', False))
        
        # 超时控制
        start = time.time()
        result = await skill.execute({
            'code': 'import time; time.sleep(5)',
            'language': 'python',
            'timeout': 2
        })
        elapsed = time.time() - start
        timeout_works = result.get('timeout', False) and elapsed < 4
        results.record("超时控制", timeout_works)
        
        # 错误处理
        result = await skill.execute({
            'code': 'raise Exception("test")',
            'language': 'python'
        })
        error_handled = not result.get('success', True)
        results.record("错误处理", error_handled)
        
    except Exception as e:
        results.record("代码运行测试", False, str(e))


async def test_performance(results: TestResults):
    """测试性能优化"""
    print(f"\n{'='*60}")
    print("测试 3: 性能优化")
    print(f"{'='*60}")
    
    try:
        # 缓存机制
        cache = Cache(max_size=100, ttl=60)
        cache.set('test', 'value')
        value = cache.get('test')
        results.record("缓存机制", value == 'value')
        
        # 异步批处理
        processor = AsyncBatchProcessor(batch_size=5, max_concurrency=2)
        
        async def square(x):
            return x * x
        
        items = [1, 2, 3, 4, 5]
        batch_result = await processor.process(items, square)
        results.record("异步批处理", batch_result == [1, 4, 9, 16, 25])
        
        # 性能监控
        monitor = PerformanceMonitor()
        monitor.record('test', 1.0)
        monitor.record('test', 2.0)
        stats = monitor.stats('test')
        results.record("性能监控", stats['avg'] == 1.5)
        
        # 装饰器
        @timed('test_func')
        async def test_func():
            await asyncio.sleep(0.1)
        
        await test_func()
        perf_stats = get_perf_monitor().stats('test_func')
        results.record("装饰器", perf_stats.get('count', 0) == 1)
        
    except Exception as e:
        results.record("性能优化测试", False, str(e))


async def main():
    """主测试函数"""
    print(f"\n{'#'*60}")
    print("# YM-CODE v0.9.0 测试套件")
    print(f"{'#'*60}")
    
    results = TestResults()
    
    # 运行测试
    await test_multi_language(results)
    await test_code_runner(results)
    await test_performance(results)
    
    # 总结
    success = results.summary()
    
    if success:
        print("\n✅ 所有测试通过！v0.9.0 可以发布！")
    else:
        print(f"\n⚠️ {results.failed} 个测试失败，需要修复")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
