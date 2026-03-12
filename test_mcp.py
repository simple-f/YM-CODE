#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MCP Client
"""

import asyncio
import os
from ymcode.mcp.client import MCPClient

async def main():
    print("=" * 60)
    print("MCP Client 测试")
    print("=" * 60)
    
    # 创建 MCP Client
    client = MCPClient()
    
    print("\n[测试 1] 连接到 MCP 服务器...")
    
    # 连接本地文件系统服务器
    success = await client.connect(
        server_name="local-filesystem",
        url="file:///tmp/mcp-filesystem"
    )
    
    print(f"连接结果：{'成功' if success else '失败'}")
    print(f"状态：{client.get_status()}")
    
    print("\n[测试 2] 获取工具定义...")
    tools_def = client.get_tools_definition()
    print(f"可用工具：{len(tools_def)} 个")
    for tool in tools_def:
        print(f"  - {tool['function']['name']}: {tool['function']['description']}")
    
    print("\n[测试 3] 调用工具...")
    
    # 测试文件读取
    print("\n测试读取文件...")
    result = await client.call_tool(
        tool_name="read_file",
        arguments={"path": "test.txt"}
    )
    print(f"结果：{result}")
    
    # 测试文件写入
    print("\n测试写入文件...")
    result = await client.call_tool(
        tool_name="write_file",
        arguments={
            "path": "D:\\ym\\mcp_test.txt",
            "content": "Hello from MCP!"
        }
    )
    print(f"结果：{result}")
    
    print("\n[测试 4] 断开连接...")
    await client.disconnect()
    print(f"状态：{client.get_status()}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
