#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE API 测试脚本

测试 API Key 是否正确，模型是否可以调用
"""

import os
import asyncio
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取配置
API_KEY = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL = os.getenv("OPENAI_MODEL", "qwen-plus")

print("=" * 60)
print("YM-CODE API 测试")
print("=" * 60)
print(f"API Key: {API_KEY[:20] if API_KEY else 'None'}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print("=" * 60)

if not API_KEY:
    print("❌ 错误：API Key 未配置")
    print("请检查 .env 文件")
    exit(1)


async def test_openai_sdk():
    """使用 OpenAI SDK 测试"""
    print("\n[测试 1] 使用 OpenAI SDK 调用...")
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个助手"},
                {"role": "user", "content": "你好，请回复"}
            ],
            max_tokens=100
        )
        
        print(f"✅ 成功！")
        print(f"回复：{response.choices[0].message.content}")
        print(f"Token 使用：{response.usage}")
        return True
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False


async def test_dashscope_sdk():
    """使用 DashScope SDK 测试"""
    print("\n[测试 2] 使用 DashScope SDK 调用...")
    
    try:
        # 尝试导入 DashScope
        import dashscope
        from dashscope import Generation
        
        # 配置 API Key
        dashscope.api_key = API_KEY
        
        # 调用模型
        response = Generation.call(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个助手"},
                {"role": "user", "content": "你好，请回复"}
            ]
        )
        
        print(f"✅ 成功！")
        print(f"回复：{response.output.choices[0].message.content}")
        return True
        
    except ImportError:
        print("⚠️  DashScope SDK 未安装")
        print("安装命令：pip install dashscope")
        return False
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False


def test_requests():
    """使用 requests 直接测试"""
    print("\n[测试 3] 使用 requests 直接调用...")
    
    try:
        import requests
        import json
        
        url = f"{BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "你是一个助手"},
                {"role": "user", "content": "你好，请回复"}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功！")
            print(f"回复：{result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"错误：{response.text}")
            return False
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False


async def main():
    """主函数"""
    print("\n开始测试...\n")
    
    # 测试 1: OpenAI SDK
    result1 = await test_openai_sdk()
    
    # 测试 2: DashScope SDK
    result2 = await test_dashscope_sdk()
    
    # 测试 3: requests
    result3 = test_requests()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"OpenAI SDK: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"DashScope SDK: {'✅ 成功' if result2 else '⚠️ 未测试' if result2 is None else '❌ 失败'}")
    print(f"requests: {'✅ 成功' if result3 else '❌ 失败'}")
    print("=" * 60)
    
    if result1 or result3:
        print("\n✅ API Key 有效，可以正常使用")
    else:
        print("\n❌ API Key 可能无效，请检查：")
        print("1. API Key 是否正确")
        print("2. Base URL 是否正确")
        print("3. 是否有足够的额度")
        print("4. 访问：https://dashscope.console.aliyun.com/apiKey")


if __name__ == "__main__":
    asyncio.run(main())
