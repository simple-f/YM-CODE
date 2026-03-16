#!/usr/bin/env python3
"""测试 Web Session 上下文记忆"""
import asyncio
import httpx

async def test_session_context():
    """测试 Session 级别的上下文记忆"""
    print("=" * 60)
    print("测试 Web Session 上下文记忆")
    print("=" * 60)
    
    base_url = "http://localhost:18770/api"
    session_id = "test_session_" + str(asyncio.get_event_loop().time())[:5]
    
    print(f"\n使用 Session ID: {session_id}\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 第一轮对话
        print("[User] 我叫小明，喜欢编程")
        resp1 = await client.post(
            f"{base_url}/chat",
            json={"message": "我叫小明，喜欢编程", "session_id": session_id}
        )
        data1 = resp1.json()
        msg1 = data1['message'][:100].encode('gbk', errors='replace').decode('gbk')
        print(f"[AI] {msg1}...\n")
        
        # 第二轮对话
        print("[User] 我喜欢什么？")
        resp2 = await client.post(
            f"{base_url}/chat",
            json={"message": "我喜欢什么？", "session_id": session_id}
        )
        data2 = resp2.json()
        msg2 = data2['message'][:100].encode('gbk', errors='replace').decode('gbk')
        print(f"[AI] {msg2}...\n")
        
        # 检查是否有上下文
        if '小明' in data2['message'] or '编程' in data2['message']:
            print("[OK] Session 上下文记忆工作正常！\n")
        else:
            print("[ERR] Session 上下文记忆未生效\n")
        
        # 获取会话详情
        print("\n获取会话详情...")
        resp3 = await client.get(f"{base_url}/sessions/{session_id}")
        if resp3.status_code == 200:
            session_data = resp3.json()
            title = session_data['session']['title'].encode('gbk', errors='replace').decode('gbk')
            print(f"会话标题：{title}")
            print(f"消息数量：{session_data['session']['message_count']}")
            print(f"\n消息历史:")
            for msg in session_data['messages']:
                content = msg['content'][:50].encode('gbk', errors='replace').decode('gbk')
                print(f"  [{msg['role']}] {content}...")
        else:
            print(f"获取会话失败：{resp3.status_code}")
        
        # 获取会话列表
        print("\n获取会话列表...")
        resp4 = await client.get(f"{base_url}/sessions")
        if resp4.status_code == 200:
            sessions_data = resp4.json()
            print(f"总会话数：{sessions_data['total']}")
            for s in sessions_data['sessions'][:5]:
                s_title = s['title'].encode('gbk', errors='replace').decode('gbk')
                print(f"  - {s_title} ({s['message_count']} 条消息)")

if __name__ == "__main__":
    asyncio.run(test_session_context())
