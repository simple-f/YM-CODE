#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MCP 服务器启动和连接
"""

import asyncio
import sys
import os
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.mcp.skills_server import SkillsMCPServer
from ymcode.skills import get_all_skills
from ymcode.utils.logger import get_logger

logger = get_logger(__name__)


def test_mcp_server():
    """测试 MCP 服务器"""
    print("\n[TEST] Starting MCP Skills Server...\n")
    
    # 1. 获取所有技能
    print("1. Loading all skills...")
    skills = get_all_skills()
    assert len(skills) > 0, "应该加载至少一个技能"
    print(f"   [OK] Loaded {len(skills)} skills")
    
    # 2. 创建 MCP 服务器
    print("\n2. Creating MCP server...")
    server = SkillsMCPServer(skills)
    assert server is not None, "MCP 服务器应该成功创建"
    assert len(server.server.tools) > 0, "应该有至少一个可用工具"
    print(f"   [OK] MCP server started")
    print(f"   [INFO] Available tools: {len(server.server.tools)}")
    
    # 列出所有工具
    print("\n   Tools list:")
    for i, tool in enumerate(server.server.tools[:10], 1):
        desc = tool.description[:50] if tool.description else "No description"
        print(f"     {i}. {tool.name}: {desc}...")
    
    if len(server.server.tools) > 10:
        print(f"     ... and {len(server.server.tools) - 10} more tools")
    
    print("\n[SUCCESS] MCP server test passed!\n")


if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
