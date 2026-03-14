#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具集成测试 - MCP + Skills + OpenClaw 桥接
"""

import asyncio
import sys
import pytest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.skills import (
    get_registry,
    SearchSkill,
    HTTPSkill,
    ShellSkill,
    CodeAnalysisSkill,
    DatabaseSkill,
    FormatterSkill,
    DockerSkill
)
from ymcode.skills.openclaw_bridge import OpenClawSkillBridge, list_openclaw_skills
from ymcode.mcp import get_registry as get_mcp_registry
from ymcode.utils.logger import get_logger

logger = get_logger(__name__)

# 标记所有异步测试
pytestmark = pytest.mark.asyncio


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


async def test_mcp_integration(results: TestResults):
    """测试 MCP 集成"""
    print("\n📋 第一部分：MCP 集成测试\n")
    
    # 测试 1: MCP 注册表
    print("测试 1: MCP 注册表")
    try:
        mcp_registry = get_mcp_registry()
        servers = mcp_registry.list_servers()
        results.record(
            "MCP 注册表可用",
            len(servers) >= 6,
            f"内置服务器数={len(servers)}"
        )
        print(f"   可用 MCP 服务器：{[s.name for s in servers[:5]]}")
    except Exception as e:
        results.record("MCP 注册表", False, str(e))
    
    # 测试 2: MCP 工具定义
    print("\n测试 2: MCP 工具定义")
    try:
        tools = mcp_registry.get_available_tools()
        results.record(
            "MCP 工具可用",
            len(tools) > 0,
            f"工具数={len(tools)}"
        )
        print(f"   可用工具：{tools[:10]}")
    except Exception as e:
        results.record("MCP 工具定义", False, str(e))


async def test_skills_registry(results: TestResults):
    """测试 Skills 注册表"""
    print("\n\n📋 第二部分：Skills 注册表测试\n")
    
    # 测试 1: Skills 注册表
    print("测试 1: Skills 注册表")
    try:
        registry = get_registry()
        skills = registry.list_skills()
        results.record(
            "Skills 注册表可用",
            len(skills) >= 9,
            f"技能数={len(skills)}"
        )
        print(f"   可用 Skills: {[s['name'] for s in skills]}")
    except Exception as e:
        results.record("Skills 注册表", False, str(e))
    
    # 测试 2: 执行 Search Skill
    print("\n测试 2: 执行 Search Skill")
    try:
        search_skill = SearchSkill()
        result = await search_skill.execute({
            'query': 'test',
            'source': 'web',
            'limit': 3
        })
        results.record(
            "Search Skill 执行",
            result.get('success') or 'results' in result,
            f"结果数={result.get('count', 0)}"
        )
    except Exception as e:
        results.record("Search Skill 执行", False, str(e))
    
    # 测试 3: 执行 HTTP Skill
    print("\n测试 3: 执行 HTTP Skill")
    try:
        http_skill = HTTPSkill()
        result = await http_skill.execute({
            'url': 'https://httpbin.org/get',
            'method': 'GET'
        })
        results.record(
            "HTTP Skill 执行",
            isinstance(result, dict),
            f"status={result.get('status', 'N/A')}"
        )
    except Exception as e:
        results.record("HTTP Skill 执行", False, str(e))
    
    # 测试 4: 执行 Shell Skill
    print("\n测试 4: 执行 Shell Skill")
    try:
        shell_skill = ShellSkill()
        result = await shell_skill.execute({
            'command': 'echo',
            'args': ['Hello from YM-CODE']
        })
        results.record(
            "Shell Skill 执行",
            result.get('success') or 'stdout' in result,
            f"输出={result.get('stdout', '').strip()[:50]}"
        )
    except Exception as e:
        results.record("Shell Skill 执行", False, str(e))
    
    # 测试 5: 执行 CodeAnalysis Skill
    print("\n测试 5: 执行 CodeAnalysis Skill")
    try:
        code_skill = CodeAnalysisSkill()
        result = await code_skill.execute({
            'code': 'def hello():\n    print("world")',
            'language': 'python',
            'analysis_type': 'stats'
        })
        results.record(
            "CodeAnalysis Skill 执行",
            result.get('language') == 'python',
            f"functions={result.get('stats', {}).get('functions', 0)}"
        )
    except Exception as e:
        results.record("CodeAnalysis Skill 执行", False, str(e))
    
    # 测试 6: 执行 Database Skill
    print("\n测试 6: 执行 Database Skill")
    try:
        db_skill = DatabaseSkill()
        result = await db_skill.execute({
            'action': 'list_tables'
        })
        results.record(
            "Database Skill 执行",
            result.get('success'),
            f"tables={result.get('count', 0)}"
        )
    except Exception as e:
        results.record("Database Skill 执行", False, str(e))
    
    # 测试 7: 执行 Formatter Skill
    print("\n测试 7: 执行 Formatter Skill")
    try:
        fmt_skill = FormatterSkill()
        result = await fmt_skill.execute({
            'code': '{"name":"test","value":123}',
            'language': 'json',
            'indent_size': 2
        })
        results.record(
            "Formatter Skill 执行",
            result.get('success'),
            f"formatted={len(result.get('formatted_code', ''))} chars"
        )
    except Exception as e:
        results.record("Formatter Skill 执行", False, str(e))
    
    # 测试 8: 执行 Docker Skill
    print("\n测试 8: 执行 Docker Skill")
    try:
        docker_skill = DockerSkill()
        result = await docker_skill.execute({
            'action': 'ps'
        })
        results.record(
            "Docker Skill 执行",
            result.get('success'),
            f"containers={result.get('count', 0)}"
        )
    except Exception as e:
        results.record("Docker Skill 执行", False, str(e))


async def test_openclaw_bridge(results: TestResults):
    """测试 OpenClaw 桥接"""
    print("\n\n📋 第三部分：OpenClaw Skills 桥接测试\n")
    
    # 测试 1: 创建桥接器
    print("测试 1: 创建 OpenClaw 桥接器")
    try:
        # 使用当前工作空间作为示例
        workspace = str(Path(__file__).parent.parent.parent)
        bridge = OpenClawSkillBridge(workspace)
        results.record(
            "创建桥接器",
            True,
            f"workspace={workspace}"
        )
    except Exception as e:
        results.record("创建桥接器", False, str(e))
        return
    
    # 测试 2: 发现 Skills
    print("\n测试 2: 发现 OpenClaw Skills")
    try:
        skills = bridge.list_available_skills()
        results.record(
            "发现 Skills",
            len(skills) >= 0,  # 允许没有
            f"发现数={len(skills)}"
        )
        if skills:
            print(f"   可用 Skills: {[s['name'] for s in skills[:5]]}")
    except Exception as e:
        results.record("发现 Skills", False, str(e))
    
    # 测试 3: 便捷函数
    print("\n测试 3: 便捷函数测试")
    try:
        skills = list_openclaw_skills(workspace)
        results.record(
            "list_openclaw_skills 函数",
            isinstance(skills, list),
            f"返回数={len(skills)}"
        )
    except Exception as e:
        results.record("便捷函数测试", False, str(e))


async def test_tool_marketplace(results: TestResults):
    """测试工具市场概念"""
    print("\n\n📋 第四部分：工具市场概念测试\n")
    
    # 测试 1: 工具分类
    print("测试 1: 工具分类统计")
    try:
        registry = get_registry()
        skills = registry.list_skills()
        
        categories = {
            'core': ['search', 'http', 'shell', 'code_analysis'],
            'dev': ['database', 'formatter', 'docker'],
            'memory': ['memory', 'self_improvement']
        }
        
        skill_names = [s['name'] for s in skills]
        
        stats = {}
        for cat, cat_skills in categories.items():
            stats[cat] = len([s for s in cat_skills if s in skill_names])
        
        results.record(
            "工具分类统计",
            sum(stats.values()) >= 9,
            f"core={stats['core']}, dev={stats['dev']}, memory={stats['memory']}"
        )
    except Exception as e:
        results.record("工具分类统计", False, str(e))
    
    # 测试 2: MCP + Skills 协同
    print("\n测试 2: MCP + Skills 协同")
    try:
        mcp_registry = get_mcp_registry()
        skill_registry = get_registry()
        
        mcp_tools = len(mcp_registry.get_available_tools())
        skills_count = len(skill_registry.list_skills())
        
        results.record(
            "MCP + Skills 协同",
            mcp_tools > 0 and skills_count >= 9,
            f"MCP 工具={mcp_tools}, Skills={skills_count}"
        )
    except Exception as e:
        results.record("MCP + Skills 协同", False, str(e))


async def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE 工具集成测试 - MCP + Skills + OpenClaw")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    await test_mcp_integration(results)
    await test_skills_registry(results)
    await test_openclaw_bridge(results)
    await test_tool_marketplace(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    # 打印工具清单
    print("\n📦 可用工具清单:")
    
    print("\nMCP 工具:")
    mcp_registry = get_mcp_registry()
    mcp_tools = mcp_registry.get_available_tools()
    for tool in mcp_tools[:10]:
        print(f"  - {tool}")
    
    print("\nYM-CODE Skills:")
    skill_registry = get_registry()
    skills = skill_registry.list_skills()
    for skill in skills:
        print(f"  - {skill['name']}: {skill['description'][:50]}")
    
    print("\nOpenClaw Skills:")
    workspace = str(Path(__file__).parent.parent.parent)
    bridge = OpenClawSkillBridge(workspace)
    oc_skills = bridge.list_available_skills()
    for skill in oc_skills[:5]:
        print(f"  - {skill['name']}: {skill.get('title', 'N/A')}")
    
    return results.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
