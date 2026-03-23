#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多 Agent API
"""

import requests
import json

url = "http://localhost:8080/api/multi-agent/chat"
data = {
    "message": "设计一个用户登录 API",
    "agent_ids": ["ai1"],
    "rounds": 1
}

print("发送请求...")
response = requests.post(url, json=data, timeout=120)
print(f"状态码：{response.status_code}")
print("\n响应结果:")
result = response.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
