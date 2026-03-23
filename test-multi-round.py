#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多轮对话功能
"""

import requests
import json

url = "http://localhost:8080/api/multi-agent/chat"

# 测试：2 个 Agent，2 轮对话
print("=" * 60)
print("测试：2 个 Agent (架构师 + 后端), 2 轮对话")
print("=" * 60)

data = {
    "message": "设计一个用户登录 API，需要包含哪些接口？",
    "agent_ids": ["ai1", "ai2"],
    "rounds": 2
}

print(f"\n请求：{data['message']}")
print(f"Agent: {data['agent_ids']}")
print(f"轮数：{data['rounds']}")
print("\n等待响应...\n")

try:
    response = requests.post(url, json=data, timeout=300)
    print(f"状态码：{response.status_code}")
    result = response.json()
    
    # 保存到文件
    with open("multi-round-result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 成功！总计：{result.get('total_messages', 0)} 条消息")
    print(f"轮数：{result.get('rounds', 0)}")
    print(f"Agent: {', '.join(result.get('agents', []))}")
    
    # 按轮次展示
    if result.get("conversation"):
        for i, msg in enumerate(result["conversation"], 1):
            print(f"\n{'='*60}")
            print(f"【第{msg['round']}轮 - {msg['agent']} ({msg['model']})】")
            print(f"{'='*60}")
            # 显示前 800 字
            message = msg['message']
            if len(message) > 800:
                print(message[:800] + "\n...( truncated )")
            else:
                print(message)
    
    print(f"\n{'='*60}")
    print(f"完整结果已保存到：multi-round-result.json")
    print(f"{'='*60}")
    
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()
