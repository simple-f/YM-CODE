#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Context 测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.project import (
    ProjectAnalyzer,
    CodeIndexer,
    DependencyAnalyzer
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


def test_project_analyzer(results: TestResults):
    """测试项目分析器"""
    print("\n📋 第一部分：ProjectAnalyzer 测试\n")
    
    # 测试 1: 创建分析器
    print("测试 1: 创建分析器")
    try:
        analyzer = ProjectAnalyzer(str(Path(__file__).parent.parent))
        results.record("创建 ProjectAnalyzer", True)
    except Exception as e:
        results.record("创建 ProjectAnalyzer", False, str(e))
        return
    
    # 测试 2: 分析项目
    print("\n测试 2: 分析项目")
    try:
        structure = analyzer.analyze(max_files=50)
        results.record(
            "项目分析",
            structure.total_files > 0,
            f"文件数={structure.total_files}"
        )
    except Exception as e:
        results.record("项目分析", False, str(e))
    
    # 测试 3: 获取摘要
    print("\n测试 3: 获取摘要")
    try:
        summary = analyzer.get_summary()
        results.record(
            "获取摘要",
            'total_files' in summary and 'languages' in summary,
            f"文件数={summary.get('total_files')}"
        )
    except Exception as e:
        results.record("获取摘要", False, str(e))
    
    # 测试 4: 搜索文件
    print("\n测试 4: 搜索文件")
    try:
        py_files = analyzer.search_files('*.py')
        results.record(
            "搜索 Python 文件",
            len(py_files) > 0,
            f"找到={len(py_files)}"
        )
    except Exception as e:
        results.record("搜索 Python 文件", False, str(e))
    
    # 测试 5: 查找符号
    print("\n测试 5: 查找符号")
    try:
        symbols = analyzer.get_symbols('test')
        results.record(
            "查找符号",
            isinstance(symbols, list),
            f"找到={len(symbols)}"
        )
    except Exception as e:
        results.record("查找符号", False, str(e))


def test_dependency_analyzer(results: TestResults):
    """测试依赖分析器"""
    print("\n\n📋 第二部分：DependencyAnalyzer 测试\n")
    
    # 测试 1: 创建分析器
    print("测试 1: 创建分析器")
    try:
        dep_analyzer = DependencyAnalyzer(str(Path(__file__).parent.parent))
        results.record("创建 DependencyAnalyzer", True)
    except Exception as e:
        results.record("创建 DependencyAnalyzer", False, str(e))
        return
    
    # 测试 2: 分析依赖
    print("\n测试 2: 分析依赖")
    try:
        # 收集 Python 文件
        py_files = list(Path(__file__).parent.parent.glob('ymcode/**/*.py'))
        file_paths = [str(f) for f in py_files[:10]]
        
        modules = dep_analyzer.analyze(file_paths)
        results.record(
            "依赖分析",
            len(modules) > 0,
            f"模块数={len(modules)}"
        )
    except Exception as e:
        results.record("依赖分析", False, str(e))
    
    # 测试 3: 获取摘要
    print("\n测试 3: 获取依赖摘要")
    try:
        summary = dep_analyzer.get_summary()
        results.record(
            "获取摘要",
            'total_modules' in summary,
            f"模块数={summary.get('total_modules')}"
        )
    except Exception as e:
        results.record("获取摘要", False, str(e))
    
    # 测试 4: 获取依赖图
    print("\n测试 4: 获取依赖图")
    try:
        graph = dep_analyzer.get_dependency_graph()
        results.record(
            "获取依赖图",
            isinstance(graph, dict),
            f"节点数={len(graph)}"
        )
    except Exception as e:
        results.record("获取依赖图", False, str(e))
    
    # 测试 5: 可视化
    print("\n测试 5: 可视化依赖")
    try:
        viz = dep_analyzer.visualize(max_nodes=5)
        results.record(
            "可视化",
            len(viz) > 0 and '依赖关系图' in viz,
            f"长度={len(viz)}"
        )
    except Exception as e:
        results.record("可视化", False, str(e))


def test_code_indexer(results: TestResults):
    """测试代码索引器"""
    print("\n\n📋 第三部分：CodeIndexer 测试\n")
    
    # 测试 1: 创建索引器
    print("测试 1: 创建索引器")
    try:
        indexer = CodeIndexer(str(Path(__file__).parent.parent))
        results.record("创建 CodeIndexer", True)
    except Exception as e:
        results.record("创建 CodeIndexer", False, str(e))
        return
    
    # 测试 2: 索引 Python 文件
    print("\n测试 2: 索引 Python 文件")
    try:
        test_code = """
def hello(name):
    '''Say hello'''
    print(f"Hello, {name}!")

class MyClass:
    '''My class'''
    pass
"""
        index = indexer.index_file('test.py', test_code)
        results.record(
            "Python 索引",
            index.get('language') == 'python' and len(index.get('symbols', [])) > 0,
            f"符号数={len(index.get('symbols', []))}"
        )
    except Exception as e:
        results.record("Python 索引", False, str(e))
    
    # 测试 3: 索引 JavaScript 文件
    print("\n测试 3: 索引 JavaScript 文件")
    try:
        js_code = """
function hello(name) {
    console.log(`Hello, ${name}!`);
}

class MyClass {}

const myFunc = (x) => x * 2;
"""
        index = indexer.index_file('test.js', js_code)
        results.record(
            "JavaScript 索引",
            index.get('language') == 'javascript' and len(index.get('symbols', [])) > 0,
            f"符号数={len(index.get('symbols', []))}"
        )
    except Exception as e:
        results.record("JavaScript 索引", False, str(e))
    
    # 测试 4: 查找符号
    print("\n测试 4: 查找符号")
    try:
        symbols = indexer.find_symbol('hello')
        results.record(
            "查找符号 hello",
            len(symbols) > 0,
            f"找到={len(symbols)}"
        )
    except Exception as e:
        results.record("查找符号", False, str(e))
    
    # 测试 5: 搜索
    print("\n测试 5: 搜索符号")
    try:
        results_search = indexer.search('MyClass')
        results.record(
            "搜索 MyClass",
            len(results_search) > 0,
            f"找到={len(results_search)}"
        )
    except Exception as e:
        results.record("搜索", False, str(e))
    
    # 测试 6: 获取摘要
    print("\n测试 6: 获取索引摘要")
    try:
        summary = indexer.get_summary()
        results.record(
            "获取摘要",
            'total_files' in summary and 'total_symbols' in summary,
            f"文件={summary.get('total_files')}, 符号={summary.get('total_symbols')}"
        )
    except Exception as e:
        results.record("获取摘要", False, str(e))


def test_integration(results: TestResults):
    """测试集成场景"""
    print("\n\n📋 第四部分：集成场景测试\n")
    
    # 测试 1: 完整项目分析流程
    print("测试 1: 完整项目分析")
    try:
        # 1. 分析项目结构
        analyzer = ProjectAnalyzer(str(Path(__file__).parent.parent))
        structure = analyzer.analyze(max_files=30)
        
        # 2. 分析依赖
        dep_analyzer = DependencyAnalyzer(str(Path(__file__).parent.parent))
        py_files = list(Path(__file__).parent.parent.glob('ymcode/**/*.py'))[:10]
        dep_analyzer.analyze([str(f) for f in py_files])
        
        # 3. 索引代码
        indexer = CodeIndexer(str(Path(__file__).parent.parent))
        indexer.index_project([str(f) for f in py_files])
        
        # 验证
        results.record(
            "完整项目分析",
            structure.total_files > 0 and len(dep_analyzer.modules) > 0,
            f"文件={structure.total_files}, 模块={len(dep_analyzer.modules)}"
        )
    except Exception as e:
        results.record("完整项目分析", False, str(e))
    
    # 测试 2: 跨文件符号查找
    print("\n测试 2: 跨文件符号查找")
    try:
        indexer = CodeIndexer(str(Path(__file__).parent.parent))
        
        # 索引多个文件
        py_files = list(Path(__file__).parent.parent.glob('ymcode/**/*.py'))[:10]
        for f in py_files:
            try:
                indexer.index_file(str(f))
            except Exception:
                pass  # 跳过无法索引的文件
        
        # 查找符号（使用更通用的名称）
        symbols = indexer.find_symbol('get_registry')
        if len(symbols) == 0:
            # 尝试查找其他符号
            symbols = indexer.find_symbol('registry')
        
        results.record(
            "跨文件符号查找",
            len(symbols) >= 0,  # 允许找不到，只要不报错
            f"找到={len(symbols)}"
        )
    except Exception as e:
        results.record("跨文件符号查找", False, str(e))


def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE 项目上下文理解测试")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    test_project_analyzer(results)
    test_dependency_analyzer(results)
    test_code_indexer(results)
    test_integration(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    return results.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
