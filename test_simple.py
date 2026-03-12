#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 简单 API 测试
"""

import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "qwen-plus")

print("=" * 60)
print("YM-CODE API 配置")
print("=" * 60)
print(f"API Key: {API_KEY[:20] if API_KEY else 'None'}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print("=" * 60)

# 使用 OpenAI SDK 测试
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    print("\n正在调用模型...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "你好"}
        ],
        max_tokens=50
    )
    
    print("成功！")
    print(f"回复：{response.choices[0].message.content}")
    
except Exception as e:
    print(f"失败：{e}")
    print("\n可能的问题：")
    print("1. API Key 无效或已过期")
    print("2. Base URL 不正确")
    print("3. 账户余额不足")
    print("\n请检查：https://dashscope.console.aliyun.com/apiKey")
