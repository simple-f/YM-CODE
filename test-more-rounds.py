#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更多轮次的多 Agent 对话
"""

import requests
import json
import sys
import io

# 设置 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

url = "http://localhost:8080/api/multi-agent/chat"

# 测试：3 个 Agent，3 轮对话
print("=" * 80)
print("测试：3 个 Agent (架构师 + 后端 + 测试), 3 轮对话")
print("=" * 80)

data = {
    "message": "设计一个用户注册功能，需要考虑哪些安全和用户体验问题？",
    "agent_ids": ["ai1", "ai2", "ai5"],
    "rounds": 3
}

print(f"\n问题：{data['message']}")
print(f"Agent: {data['agent_ids']}")
print(f"轮数：{data['rounds']}")
print(f"预计消息数：{len(data['agent_ids']) * data['rounds']} = 9 条")
print("\n开始测试，这可能需要几分钟...\n")

try:
    response = requests.post(url, json=data, timeout=600)
    print(f"状态码：{response.status_code}")
    result = response.json()
    
    # 保存到文件
    with open("multi-round-3result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n成功！总计：{result.get('total_messages', 0)} 条消息")
    print(f"轮数：{result.get('rounds', 0)}")
    print(f"Agent: {', '.join(result.get('agents', []))}")
    
    # 按轮次和 Agent 展示摘要
    if result.get("conversation"):
        print("\n" + "=" * 80)
        print("对话摘要")
        print("=" * 80)
        
        for round_num in range(1, result['rounds'] + 1):
            print(f"\n{'='*80}")
            print(f"第 {round_num} 轮")
            print(f"{'='*80}")
            
            for msg in result["conversation"]:
                if msg['round'] == round_num:
                    print(f"\n【{msg['agent']} - {msg['model']}】")
                    # 显示前 500 字摘要
                    message = msg['message']
                    if len(message) > 500:
                        print(message[:500] + "\n...( truncated, 查看完整结果文件)")
                    else:
                        print(message)
    
    print(f"\n{'='*80}")
    print(f"完整结果已保存到：multi-round-3result.json")
    print(f"{'='*80}")
    
except requests.exceptions.Timeout:
    print("请求超时（600 秒），LLM 调用时间较长")
    print("请查看日志文件或使用更少的轮数测试")
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
