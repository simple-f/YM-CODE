#!/usr/bin/env python3
"""
检查通义灵码支持的模型
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

print("=" * 60)
print("通义灵码 API 配置")
print("=" * 60)
print(f"API Key: {API_KEY[:20] if API_KEY else 'None'}...")
print(f"Base URL: {BASE_URL}")
print("=" * 60)

# 尝试列出支持的模型
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    print("\n获取支持的模型列表...")
    
    models = client.models.list()
    
    print(f"\n支持 {len(models.data)} 个模型：\n")
    for model in models.data:
        print(f"  - {model.id}")
    
except Exception as e:
    print(f"失败：{e}")
    print("\n提示：通义灵码 Lite 套餐可能支持的模型：")
    print("  - qwen-coder-lite")
    print("  - qwen-coder-plus")
    print("  - qwen2.5-coder-lite")
    print("  - qwen2.5-coder-plus")
