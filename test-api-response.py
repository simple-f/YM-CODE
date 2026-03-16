#!/usr/bin/env python3
"""测试 Web API 响应内容"""
import asyncio
import httpx

async def test_api_response():
    """测试 API 实际返回内容"""
    print("=" * 60)
    print("测试 API 响应内容")
    print("=" * 60)
    
    base_url = "http://localhost:18770/api"
    session_id = "test_debug_session"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 测试请求
        print("\n发送请求：帮我列出 D 盘的文件")
        print("-" * 60)
        
        resp = await client.post(
            f"{base_url}/chat",
            json={"message": "帮我列出 D 盘的文件", "session_id": session_id}
        )
        
        print(f"HTTP 状态：{resp.status_code}")
        data = resp.json()
        
        print(f"\n完整响应:")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查响应内容
        message = data.get('message', '')
        if 'stdout' in str(data) or 'stderr' in str(data):
            print("\n[OK] 响应包含命令输出")
        else:
            print("\n[WARN] 响应可能不包含命令输出")
        
        if len(message) < 50:
            print(f"[WARN] 响应消息过短：{len(message)} 字符")

if __name__ == "__main__":
    asyncio.run(test_api_response())
