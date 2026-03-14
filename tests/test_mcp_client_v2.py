#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client v2 测试脚本
测试所有核心功能
"""

import asyncio
import sys
import pytest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.mcp import (
    MCPClientV2,
    MCPServerRegistry,
    MCPServerConfig,
    MCPPromptTemplates,
    get_registry,
    get_templates,
    render_template
)
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


async def test_client_v2(results: TestResults):
    """测试 MCP Client v2"""
    print("\n📋 第一部分：MCP Client v2 测试\n")
    
    # 测试 1: 创建客户端
    print("测试 1: 创建客户端")
    try:
        client = MCPClientV2()
        results.record("创建 MCP Client v2", True)
    except Exception as e:
        results.record("创建 MCP Client v2", False, str(e))
        return
    
    # 测试 2: 初始状态
    print("\n测试 2: 初始状态")
    status = client.get_status()
    results.record(
        "初始状态正确",
        status["connected"] == False and status["servers"] == 0,
        f"connected={status['connected']}, servers={status['servers']}"
    )
    
    # 测试 3: 获取工具定义（空）
    print("\n测试 3: 获取工具定义")
    tools_def = client.get_tools_definition()
    results.record(
        "空工具列表",
        isinstance(tools_def, list) and len(tools_def) == 0,
        f"工具数={len(tools_def)}"
    )
    
    # 测试 4: 断开连接（无连接时）
    print("\n测试 4: 断开连接")
    try:
        await client.disconnect()
        results.record("断开空连接", True)
    except Exception as e:
        results.record("断开空连接", False, str(e))


def test_server_registry(results: TestResults):
    """测试服务器注册表"""
    print("\n\n📋 第二部分：MCP Server Registry 测试\n")
    
    # 测试 1: 创建注册表
    print("测试 1: 创建注册表")
    try:
        registry = get_registry()
        results.record("创建注册表", True)
    except Exception as e:
        results.record("创建注册表", False, str(e))
        return
    
    # 测试 2: 获取内置服务器
    print("\n测试 2: 获取内置服务器")
    builtin_servers = registry.BUILTIN_SERVERS
    results.record(
        "内置服务器数量",
        len(builtin_servers) >= 5,
        f"数量={len(builtin_servers)}"
    )
    
    # 测试 3: 获取特定服务器
    print("\n测试 3: 获取特定服务器")
    fs_server = registry.get_server("filesystem")
    results.record(
        "获取 filesystem 服务器",
        fs_server is not None and fs_server.type == "stdio",
        f"type={fs_server.type if fs_server else None}"
    )
    
    # 测试 4: 列出所有服务器
    print("\n测试 4: 列出所有服务器")
    all_servers = registry.list_servers()
    results.record(
        "列出服务器",
        len(all_servers) >= len(builtin_servers),
        f"数量={len(all_servers)}"
    )
    
    # 测试 5: 获取可用工具
    print("\n测试 5: 获取可用工具")
    tools = registry.get_available_tools()
    results.record(
        "获取可用工具",
        isinstance(tools, list) and len(tools) > 0,
        f"工具数={len(tools)}"
    )
    
    # 测试 6: 添加自定义服务器
    print("\n测试 6: 添加自定义服务器")
    try:
        custom_server = MCPServerConfig(
            name="test-server",
            type="stdio",
            command="echo",
            args=["test"],
            description="测试服务器"
        )
        success = registry.add_server(custom_server)
        results.record("添加自定义服务器", success)
        
        # 验证添加
        retrieved = registry.get_server("test-server")
        results.record(
            "验证自定义服务器",
            retrieved is not None and retrieved.name == "test-server",
            f"name={retrieved.name if retrieved else None}"
        )
    except Exception as e:
        results.record("添加自定义服务器", False, str(e))


def test_prompts(results: TestResults):
    """测试 Prompt 模板"""
    print("\n\n📋 第三部分：MCP Prompt 模板测试\n")
    
    # 测试 1: 创建模板集合
    print("测试 1: 创建模板集合")
    try:
        templates = get_templates()
        results.record("创建模板集合", True)
    except Exception as e:
        results.record("创建模板集合", False, str(e))
        return
    
    # 测试 2: 内置模板数量
    print("\n测试 2: 内置模板数量")
    template_list = templates.list_templates()
    results.record(
        "内置模板数量",
        len(template_list) >= 5,
        f"数量={len(template_list)}"
    )
    
    # 测试 3: 获取特定模板
    print("\n测试 3: 获取特定模板")
    tool_call_template = templates.get_template("tool_call")
    results.record(
        "获取 tool_call 模板",
        tool_call_template is not None,
        f"name={tool_call_template.name if tool_call_template else None}"
    )
    
    # 测试 4: 渲染模板
    print("\n测试 4: 渲染模板")
    try:
        rendered = render_template(
            "tool_call",
            tool_name="read_file",
            tool_description="读取文件内容",
            tool_arguments='{"path": "test.txt"}'
        )
        results.record(
            "渲染模板",
            len(rendered) > 0 and "read_file" in rendered,
            f"长度={len(rendered)}"
        )
    except Exception as e:
        results.record("渲染模板", False, str(e))
    
    # 测试 5: 渲染错误处理模板
    print("\n测试 5: 渲染错误处理模板")
    try:
        error_prompt = render_template(
            "error_handling",
            tool_name="write_file",
            error_message="Permission denied",
            error_type="PermissionError",
            possible_cause_1="文件权限不足",
            possible_cause_2="文件被占用",
            possible_cause_3="路径不存在",
            suggested_solution="检查文件权限和路径"
        )
        results.record(
            "渲染错误处理模板",
            len(error_prompt) > 0 and "Permission denied" in error_prompt,
            f"长度={len(error_prompt)}"
        )
    except Exception as e:
        results.record("渲染错误处理模板", False, str(e))


async def test_integration(results: TestResults):
    """测试集成功能"""
    print("\n\n📋 第四部分：MCP 集成测试\n")
    
    # 测试 1: 创建集成管理器
    print("测试 1: 创建集成管理器")
    try:
        from ymcode.mcp.integration_example import MCPIntegration
        integration = MCPIntegration()
        results.record("创建集成管理器", True)
    except Exception as e:
        results.record("创建集成管理器", False, str(e))
        return
    
    # 测试 2: 获取状态（未初始化）
    print("\n测试 2: 获取状态（未初始化）")
    status = integration.get_status()
    results.record(
        "未初始化状态",
        status["initialized"] == False,
        f"initialized={status['initialized']}"
    )
    
    # 测试 3: 获取工具定义（未初始化）
    print("\n测试 3: 获取工具定义（未初始化）")
    tools = integration.get_tools_for_agent()
    results.record(
        "未初始化时工具列表为空",
        isinstance(tools, list) and len(tools) == 0,
        f"工具数={len(tools)}"
    )


async def main():
    """主测试函数"""
    print("=" * 60)
    print("YM-CODE MCP Client v2 完整测试")
    print("=" * 60)
    
    results = TestResults()
    
    # 运行所有测试
    await test_client_v2(results)
    test_server_registry(results)
    test_prompts(results)
    await test_integration(results)
    
    # 打印总结
    print("\n" + "=" * 60)
    results.summary()
    print("=" * 60)
    
    return results.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
