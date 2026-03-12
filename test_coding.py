#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通义灵码 API
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

print("=" * 60)
print("通义灵码 API 测试")
print("=" * 60)
print(f"API Key: {API_KEY[:20] if API_KEY else 'None'}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print("=" * 60)

try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    print("\n正在调用通义灵码...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "你好，请用 Python 写一个 hello world"}
        ],
        max_tokens=200
    )
    
    print("成功！")
    print(f"回复：{response.choices[0].message.content}")
    print(f"Token: {response.usage}")
    
except Exception as e:
    print(f"失败：{e}")
