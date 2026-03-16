#!/usr/bin/env python3
"""
测试工具调用
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

print("=" * 60)
print("工具调用测试")
print("=" * 60)
print(f"API Key: {API_KEY[:20]}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print("=" * 60)

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["path", "content"]
            }
        }
    }
]

async def test():
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    print("\n测试 1: 不使用工具...")
    response1 = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "帮我创建一个文件 D:\\ym\\test.py，写入 print('hello')"}
        ]
    )
    
    print(f"回复：{response1.choices[0].message.content[:200]}")
    print(f"Finish reason: {response1.choices[0].finish_reason}")
    
    print("\n测试 2: 使用工具...")
    response2 = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "帮我创建一个文件 D:\\ym\\test.py，写入 print('hello')"}
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    message = response2.choices[0].message
    print(f"回复：{message.content}")
    print(f"Finish reason: {response2.choices[0].finish_reason}")
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print(f"工具调用：{len(message.tool_calls)} 个")
        for tc in message.tool_calls:
            print(f"  - {tc.function.name}: {tc.function.arguments}")
    else:
        print("没有工具调用")

asyncio.run(test())
