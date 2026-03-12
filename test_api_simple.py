#!/usr/bin/env python3
"""
最简单的 API 测试
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

print(f"API Key: {API_KEY[:20] if API_KEY else 'None'}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print()

try:
    from openai import OpenAI
    
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    print("正在调用 API...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ],
        max_tokens=100
    )
    
    print("成功！")
    print(f"回复：{response.choices[0].message.content}")
    
except Exception as e:
    print(f"失败：{e}")
