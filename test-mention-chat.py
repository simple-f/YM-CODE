#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试@mention 触发的多 Agent 对话
"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

url = "http://localhost:8080/api/multi-agent/chat"

print("=" * 80)
print("测试@mention 触发的多 Agent 对话")
print("=" * 80)

# 测试 1: @单个 Agent
print("\n" + "=" * 80)
print("测试 1: @单个 Agent")
print("=" * 80)

data = {
    "message": "@ai1 你好，请自我介绍",
    "rounds": 1
}

print(f"消息：{data['message']}")
try:
    response = requests.post(url, json=data, timeout=90)
    result = response.json()
    print(f"模式：{result.get('mode')}")
    print(f"Agent: {result.get('agents')}")
    print(f"消息数：{result.get('total_messages')}")
    if result.get('conversation'):
        msg = result['conversation'][0]
        print(f"\n{msg['agent']} 回复：{msg['message'][:200]}...")
except Exception as e:
    print(f"错误：{e}")

# 测试 2: @多个 Agent
print("\n" + "=" * 80)
print("测试 2: @多个 Agent 协作")
print("=" * 80)

data = {
    "message": "@ai1 和 @ai2 设计一个简单的登录功能，架构师先设计，后端再实现",
    "rounds": 1
}

print(f"消息：{data['message']}")
try:
    response = requests.post(url, json=data, timeout=180)
    result = response.json()
    print(f"模式：{result.get('mode')}")
    print(f"Agent: {result.get('agents')}")
    print(f"消息数：{result.get('total_messages')}")
    
    if result.get('conversation'):
        for msg in result['conversation']:
            print(f"\n【{msg['agent']} - 第{msg['round']}轮】")
            print(f"{msg['message'][:300]}...")
except Exception as e:
    print(f"错误：{e}")

# 测试 3: 手动指定 agent_ids（覆盖@mention）
print("\n" + "=" * 80)
print("测试 3: 手动指定 agent_ids（覆盖@mention）")
print("=" * 80)

data = {
    "message": "@ai1 你好",  # 虽然有@ai1
    "agent_ids": ["ai2"],  # 但手动指定 ai2
    "rounds": 1
}

print(f"消息：{data['message']}")
print(f"手动指定：{data['agent_ids']}")
try:
    response = requests.post(url, json=data, timeout=90)
    result = response.json()
    print(f"模式：{result.get('mode')}")
    print(f"实际 Agent: {result.get('agents')}")
except Exception as e:
    print(f"错误：{e}")

# 测试 4: 没有@任何人
print("\n" + "=" * 80)
print("测试 4: 没有@任何人（应该报错）")
print("=" * 80)

data = {
    "message": "设计一个登录系统",
    "rounds": 1
}

print(f"消息：{data['message']}")
try:
    response = requests.post(url, json=data, timeout=30)
    result = response.json()
    print(f"状态：{response.status_code}")
    print(f"响应：{result}")
except Exception as e:
    print(f"预期错误：{e}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
