#!/usr/bin/env python3
import asyncio
import httpx

async def test_api():
    """测试 LLM API 连接"""
    api_key = "sk-sp-90fc02607ed448be9d251333e9524876"
    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen3.5-plus",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "stream": False
    }
    
    print("测试 LLM API 连接...")
    print(f"URL: {url}")
    print(f"Model: qwen3.5-plus")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"\nHTTP 状态：{response.status_code}")
            print(f"响应：{response.text[:500]}")
    except Exception as e:
        print(f"\n错误：{e}")

asyncio.run(test_api())
