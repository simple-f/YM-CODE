#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试@mention 功能并展示完整返回结果
"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

url = "http://localhost:8080/api/multi-agent/chat"

print("=" * 80)
print("@mention 功能测试 - 完整返回结果")
print("=" * 80)

# 测试：@2 个 Agent，1 轮对话
data = {
    "message": "@ai1 和 @ai2 设计一个简单的用户登录 API，架构师先设计，后端再实现",
    "rounds": 1
}

print(f"\n请求消息：{data['message']}")
print(f"轮数：{data['rounds']}")
print("\n等待响应（这可能需要 1-2 分钟）...\n")

try:
    response = requests.post(url, json=data, timeout=180)
    
    print("=" * 80)
    print(f"HTTP 状态码：{response.status_code}")
    print("=" * 80)
    
    result = response.json()
    
    # 打印完整 JSON（缩进格式）
    print("\n完整返回结果:")
    print("-" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("-" * 80)
    
    # 打印摘要
    print("\n结果摘要:")
    print(f"  - 模式：{result.get('mode')}")
    print(f"  - 参与 Agent: {result.get('agents')}")
    print(f"  - 总消息数：{result.get('total_messages')}")
    print(f"  - 对话轮数：{result.get('rounds')}")
    
    if result.get('mentions'):
        print(f"  - @mention 详情:")
        for m in result['mentions']:
            print(f"      • {m['mention_text']} → {m['agent_name']} ({m['agent_id']})")
    
    # 打印每条消息的摘要
    if result.get('conversation'):
        print(f"\n对话内容摘要:")
        for i, msg in enumerate(result['conversation'], 1):
            print(f"\n  [{i}] {msg['agent']} (第{msg['round']}轮)")
            print(f"      模型：{msg['model']}")
            print(f"      角色：{msg['role']}")
            # 显示前 300 字
            message_text = msg['message']
            if len(message_text) > 300:
                print(f"      内容：{message_text[:300]}...")
            else:
                print(f"      内容：{message_text}")
    
    # 保存到文件
    output_file = "mention-test-result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ 完整结果已保存到：{output_file}")
    print(f"{'='*80}")
    
except requests.exceptions.Timeout:
    print("❌ 请求超时（180 秒），LLM 调用时间较长")
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()
