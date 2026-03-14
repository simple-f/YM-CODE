#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 系统测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.skills import (
    SkillRegistry,
    SearchSkill,
    HTTPSkill,
    ShellSkill,
    CodeAnalysisSkill,
    get_registry
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


async def test_skill_registry(results: TestResults):
    """测试技能注册表"""
    print("\n📋 第一部分：技能注册表测试\n")
    
    # 测试 1: 创建注册表
    print("测试 1: 创建注册表")
    try:
        registry = SkillRegistry()
        results.record("创建技能注册表", True)
    except Exception as e:
        results.record("创建技能注册表", False, str(e))
        return
    
    # 测试 2: 注册表状态
    print("\n测试 2: 注册表状态")
    status = registry.get_status()
    results.record(
        "注册表状态包含 total_skills",
        'total_skills' in status,
        f"total_skills={status.get('total_skills')}"
    )
    
    # 测试 3: 注册技能实例
    print("\n测试 3: 注册技能实例")
    try:
        search_skill = SearchSkill()
        success = registry.register(search_skill)
        results.record("注册 SearchSkill", success)
    except Exception as e:
        results.record("注册 SearchSkill", False, str(e))
    
    # 测试 4: 列出技能
    print("\n测试 4: 列出技能")
    skills = registry.list_skills()
    results.record(
        "列出技能",
        len(skills) > 0,
        f"技能数={len(skills)}"
    )
    
    # 测试 5: 获取 MCP 工具定义
    print("\n测试 5: 获取 MCP 工具定义")
    tools = registry.get_tools_definition()
    results.record(
        "获取工具定义",
        isinstance(tools, list) and len(tools) > 0,
        f"工具数={len(tools)}"
    )


async def test_search_skill(results: TestResults):
    """测试搜索技能"""
    print("\n\n📋 第二部分：SearchSkill 测试\n")
    
    # 测试 1: 创建技能
    print("测试 1: 创建 SearchSkill")
    try:
        skill = SearchSkill()
        results.record("创建 SearchSkill", True)
    except Exception as e:
        results.record("创建 SearchSkill", False, str(e))
        return
    
    # 测试 2: 技能描述
    print("\n测试 2: 技能描述")
    results.record(
        "技能描述存在",
        len(skill.description) > 0,
        f"description={skill.description}"
    )
    
    # 测试 3: 输入 schema
    print("\n测试 3: 输入 schema")
    schema = skill.get_input_schema()
    results.record(
        "schema 包含 required 字段",
        'required' in schema and 'query' in schema['required'],
        f"required={schema.get('required')}"
    )
    
    # 测试 4: Web 搜索
    print("\n测试 4: Web 搜索")
    result = await skill.execute({
        'query': 'test',
        'source': 'web',
        'limit': 3
    })
    results.record(
        "Web 搜索执行",
        result.get('success') or 'results' in result,
        f"结果数={result.get('count', 0)}"
    )
    
    # 测试 5: 文件搜索
    print("\n测试 5: 文件搜索")
    result = await skill.execute({
        'query': '.py',
        'source': 'file',
        'path': str(Path(__file__).parent),
        'limit': 3
    })
    results.record(
        "文件搜索执行",
        isinstance(result, dict),
        f"结果数={result.get('count', 0)}"
    )


async def test_http_skill(results: TestResults):
    """测试 HTTP 技能"""
    print("\n\n📋 第三部分：HTTPSkill 测试\n")
    
    # 测试 1: 创建技能
    print("测试 1: 创建 HTTPSkill")
    try:
        skill = HTTPSkill()
        results.record("创建 HTTPSkill", True)
    except Exception as e:
        results.record("创建 HTTPSkill", False, str(e))
        return
    
    # 测试 2: 技能描述
    print("\n测试 2: 技能描述")
    results.record(
        "技能描述存在",
        len(skill.description) > 0
    )
    
    # 测试 3: 输入 schema
    print("\n测试 3: 输入 schema")
    schema = skill.get_input_schema()
    results.record(
        "schema 包含 url 字段",
        'url' in schema['properties'] and 'url' in schema['required']
    )
    
    # 测试 4: GET 请求（模拟）
    print("\n测试 4: GET 请求测试")
    result = await skill.execute({
        'url': 'https://httpbin.org/get',
        'method': 'GET'
    })
    # 不要求实际网络请求成功，只要返回格式正确即可
    results.record(
        "GET 请求执行",
        isinstance(result, dict),
        f"status={result.get('status', 'N/A')}"
    )


async def test_shell_skill(results: TestResults):
    """测试 Shell 技能"""
    print("\n\n📋 第四部分：ShellSkill 测试\n")
    
    # 测试 1: 创建技能
    print("测试 1: 创建 ShellSkill")
    try:
        skill = ShellSkill()
        results.record("创建 ShellSkill", True)
    except Exception as e:
        results.record("创建 ShellSkill", False, str(e))
        return
    
    # 测试 2: 安全检查
    print("\n测试 2: 安全检查")
    safe_check = skill._check_safety('ls', ['-la'])
    results.record(
        "安全命令检查通过",
        safe_check['safe'] == True
    )
    
    # 测试 3: 危险命令检测
    print("\n测试 3: 危险命令检测")
    dangerous_check = skill._check_safety('rm', ['-rf', '/'])
    results.record(
        "危险命令检测",
        dangerous_check['safe'] == False
    )
    
    # 测试 4: 执行安全命令
    print("\n测试 4: 执行安全命令")
    result = await skill.execute({
        'command': 'echo',
        'args': ['hello world']
    })
    results.record(
        "echo 命令执行",
        result.get('success') or 'stdout' in result,
        f"stdout={result.get('stdout', '').strip()}"
    )
    
    # 测试 5: 允许的命令列表
    print("\n测试 5: 允许的命令列表")
    allowed = skill.get_allowed_commands()
    results.record(
        "获取允许命令列表",
        isinstance(allowed, list) and len(allowed) > 0,
        f"命令数={len(allowed)}"
    )


async def test_code_analysis_skill(results: TestResults):
    """测试代码分析技能"""
    print("\n\n📋 第五部分：CodeAnalysisSkill 测试\n")
    
    # 测试 1: 创建技能
    print("测试 1: 创建 CodeAnalysisSkill")
    try:
        skill = CodeAnalysisSkill()
        results.record("创建 CodeAnalysisSkill", True)
    except Exception as e:
        results.record("创建 CodeAnalysisSkill", False, str(e))
        return
    
    # 测试 2: Python 代码分析
    print("\n测试 2: Python 代码分析")
    python_code = """
def hello(name):
    '''Say hello'''
    print(f"Hello, {name}!")

class MyClass:
    pass
"""
    result = await skill.execute({
        'code': python_code,
        'language': 'python',
        'analysis_type': 'full'
    })
    results.record(
        "Python 代码分析",
        result.get('language') == 'python' and 'stats' in result,
        f"functions={result.get('stats', {}).get('functions', 0)}"
    )
    
    # 测试 3: JavaScript 代码分析
    print("\n测试 3: JavaScript 代码分析")
    js_code = """
function hello(name) {
    console.log(`Hello, ${name}!`);
}

class MyClass {}
"""
    result = await skill.execute({
        'code': js_code,
        'language': 'javascript',
        'analysis_type': 'stats'
    })
    results.record(
        "JavaScript 代码分析",
        result.get('language') == 'javascript' and 'stats' in result,
        f"functions={result.get('stats', {}).get('functions', 0)}"
    )
    
    # 测试 4: 代码质量检查
    print("\n测试 4: 代码质量检查")
    bad_code = "x=1+2*3\n" * 60  # 60 行重复代码
    result = await skill.execute({
        'code': bad_code,
        'language': 'python',
        'analysis_type': 'quality'
    })
    results.record(
        "代码质量检查",
        'quality' in result and 'score' in result['quality'],
        f"score={result.get('quality', {}).get('score', 'N/A')}"
    )


async def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE Skills 系统测试")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    await test_skill_registry(results)
    await test_search_skill(results)
    await test_http_skill(results)
    await test_shell_skill(results)
    await test_code_analysis_skill(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    return results.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
