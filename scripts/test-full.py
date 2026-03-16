#!/usr/bin/env python3
"""测试 LLM 工具调用和记忆功能"""
import asyncio
import sys
from pathlib import Path

workspace = Path(__file__).parent
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

from ymcode.skills import get_registry

async def test_tool_calling():
    """测试工具调用"""
    print("=" * 60)
    print("测试 1: LLM 工具调用 - 执行 Shell 命令")
    print("=" * 60)
    
    reg = get_registry()
    llm = reg.get('llm')
    
    # 手动构建工具定义
    from ymcode.cli.app import YMCodeApp
    app = YMCodeApp()
    app.skills_registry = reg
    tools = app._build_llm_tools()
    llm.set_available_tools(tools)
    llm.set_skills_registry(reg)
    
    print(f"可用工具：{len(llm.available_tools)}")
    
    # 测试 1: Shell 命令
    print("\n请求：帮我列出当前目录的文件")
    print("-" * 60)
    
    result = await llm.execute({
        'message': '帮我列出当前目录的文件',
        'use_tools': True
    })
    
    if result.get('success'):
        resp = result.get('response', '')[:200]
        print(f"\n[OK] 响应：{resp.encode('gbk', errors='replace').decode('gbk')}...")
    else:
        err = result.get('error', '')
        print(f"\n[ERR] 错误：{err.encode('gbk', errors='replace').decode('gbk')}")
    
    print()

async def test_memory():
    """测试记忆功能"""
    print("=" * 60)
    print("测试 2: 记忆系统 - 保存和回忆")
    print("=" * 60)
    
    reg = get_registry()
    memory = reg.get('memory')
    
    # 测试 1: 保存记忆
    print("\n1. 保存记忆：我喜欢吃苹果")
    save_result = await memory.execute({
        'action': 'save',
        'session_id': 'test_session',
        'content': '我喜欢吃苹果'
    })
    print(f"[OK] 保存：{str(save_result).encode('gbk', errors='replace').decode('gbk')}")
    
    # 测试 2: 加载记忆
    print("\n2. 加载记忆")
    load_result = await memory.execute({
        'action': 'load',
        'session_id': 'test_session'
    })
    print(f"[OK] 加载：{str(load_result).encode('gbk', errors='replace').decode('gbk')}")
    
    # 测试 3: 搜索记忆
    print("\n3. 搜索记忆：苹果")
    search_result = await memory.execute({
        'action': 'search',
        'query': '苹果'
    })
    print(f"[OK] 搜索：{str(search_result).encode('gbk', errors='replace').decode('gbk')}")
    
    # 测试 4: 记忆状态
    print("\n4. 记忆状态")
    status_result = await memory.execute({'action': 'status'})
    print(f"[OK] 状态：{str(status_result).encode('gbk', errors='replace').decode('gbk')}")
    
    print()

async def test_context():
    """测试上下文对话"""
    print("=" * 60)
    print("测试 3: 上下文对话")
    print("=" * 60)
    
    reg = get_registry()
    llm = reg.get('llm')
    
    from ymcode.cli.app import YMCodeApp
    app = YMCodeApp()
    app.skills_registry = reg
    tools = app._build_llm_tools()
    llm.set_available_tools(tools)
    llm.set_skills_registry(reg)
    
    # 清空历史
    llm.clear_history()
    
    # 第一轮对话
    print("\n[User] 我叫小明")
    result1 = await llm.execute({
        'message': '我叫小明',
        'use_tools': False
    })
    r1 = result1.get('response', '')[:100]
    print(f"[AI] {r1.encode('gbk', errors='replace').decode('gbk')}...")
    
    # 第二轮对话
    print("\n[User] 我叫什么名字？")
    result2 = await llm.execute({
        'message': '我叫什么名字？',
        'use_tools': False
    })
    r2 = result2.get('response', '')[:100]
    print(f"[AI] {r2.encode('gbk', errors='replace').decode('gbk')}...")
    
    # 检查是否有上下文
    if '小明' in result2.get('response', ''):
        print("\n[OK] 有上下文记忆！")
    else:
        print("\n[ERR] 没有上下文记忆")
    
    print()

async def main():
    await test_tool_calling()
    await test_memory()
    await test_context()
    print("=" * 60)
    print("[OK] 测试完成".encode('gbk', errors='replace').decode('gbk'))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
