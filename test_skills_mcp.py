#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Skills + MCP 集成
"""

import asyncio
from ymcode.skills.self_improvement import SelfImprovementSkill
from ymcode.mcp.skills_server import SkillsMCPServer

async def main():
    print("=" * 60)
    print("Skills + MCP 集成测试")
    print("=" * 60)
    
    # 创建技能
    print("\n[步骤 1] 创建技能...")
    skill = SelfImprovementSkill()
    print(f"技能：{skill.name}")
    print(f"描述：{skill.description}")
    
    # 创建 MCP Server
    print("\n[步骤 2] 创建 MCP Server...")
    mcp_server = SkillsMCPServer({
        "self_improvement": skill
    })
    
    print(f"MCP Server 状态：{mcp_server.get_status()}")
    
    # 获取工具定义
    print("\n[步骤 3] 获取工具定义...")
    tools_def = mcp_server.get_tools_definition()
    
    for tool in tools_def:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # 测试技能调用
    print("\n[步骤 4] 测试技能调用...")
    
    # 测试 1：查询（空知识库）
    print("\n测试 1: 查询知识库...")
    result = await mcp_server.call_tool("skill_self_improvement", {
        "action": "query",
        "query": "test"
    })
    print(f"结果：{result}")
    
    # 测试 2：自我提升
    print("\n测试 2: 自我提升...")
    result = await mcp_server.call_tool("skill_self_improvement", {
        "action": "improve",
        "skill_name": "conversation",
        "feedback": "回答很详细，继续保持"
    })
    print(f"结果：{result}")
    
    # 测试 3：再次查询
    print("\n测试 3: 再次查询...")
    result = await mcp_server.call_tool("skill_self_improvement", {
        "action": "query",
        "query": "conversation"
    })
    print(f"结果：{result}")
    
    # 测试 4：重置
    print("\n测试 4: 重置数据...")
    result = await mcp_server.call_tool("skill_self_improvement", {
        "action": "reset"
    })
    print(f"结果：{result}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
