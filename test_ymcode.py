#!/usr/bin/env python3
"""
测试 YM-CODE 完整功能
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# 设置环境变量
os.environ['OPENAI_API_KEY'] = os.getenv('DASHSCOPE_API_KEY')
os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL', 'https://coding.dashscope.aliyuncs.com/v1')
os.environ['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'qwen3.5-plus')

print("=" * 60)
print("YM-CODE 完整测试")
print("=" * 60)
print(f"API Key: {os.environ['OPENAI_API_KEY'][:20]}...")
print(f"Base URL: {os.environ['OPENAI_BASE_URL']}")
print(f"Model: {os.environ['OPENAI_MODEL']}")
print("=" * 60)

from ymcode.core.agent import Agent

async def test():
    # 创建 Agent
    agent = Agent(config={
        'max_iterations': 5,
        'timeout': 60
    })
    
    print("\nAgent 已初始化")
    print(f"工具数量：{len(agent.tools)}")
    
    # 测试对话
    print("\n测试 1: 简单对话...")
    result = await agent.run("你好，请介绍一下自己")
    print(f"回复：{result[:200].encode('gbk', 'ignore').decode('gbk')}")
    
    # 测试文件创建
    print("\n测试 2: 创建文件...")
    result = await agent.run("在 D:\\ym 目录创建文件 test.py，写入 print('hello world')")
    print(f"回复：{result[:200].encode('gbk', 'ignore').decode('gbk')}")

asyncio.run(test())
