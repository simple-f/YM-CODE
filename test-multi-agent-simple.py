#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多 Agent API - 简化版
"""

import requests
import json
import sys

url = "http://localhost:8080/api/multi-agent/chat"

# 测试 1: 单个 Agent，单轮
print("=" * 60)
print("测试 1: 单个 Agent (架构师), 单轮对话")
print("=" * 60)

data = {
    "message": "你好，请自我介绍",
    "agent_ids": ["ai1"],
    "rounds": 1
}

try:
    response = requests.post(url, json=data, timeout=90)
    print(f"状态码：{response.status_code}")
    result = response.json()
    
    if result.get("conversation"):
        for msg in result["conversation"]:
            print(f"\n[{msg['agent']} - {msg['model']}]:")
            print(msg['message'][:500] + "..." if len(msg['message']) > 500 else msg['message'])
    
    print(f"\n总计：{result.get('total_messages', 0)} 条消息")
    
except Exception as e:
    print(f"错误：{e}")

# 测试 2: 三个 Agent，单轮
print("\n" + "=" * 60)
print("测试 2: 三个 Agent (架构师 + 后端 + 测试), 单轮对话")
print("=" * 60)

data = {
    "message": "设计一个用户登录 API",
    "agent_ids": ["ai1", "ai2", "ai5"],
    "rounds": 1
}

try:
    response = requests.post(url, json=data, timeout=180)
    print(f"状态码：{response.status_code}")
    result = response.json()
    
    # 保存到文件
    with open("multi-agent-result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n完整结果已保存到：multi-agent-result.json")
    
    if result.get("conversation"):
        for msg in result["conversation"]:
            print(f"\n{'='*50}")
            print(f"[{msg['agent']} - {msg['model']} - 第{msg['round']}轮]:")
            print(f"{'='*50}")
            print(msg['message'])
    
    print(f"\n总计：{result.get('total_messages', 0)} 条消息")
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
