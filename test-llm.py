#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

workspace = Path(__file__).parent
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

from ymcode.skills import get_registry

async def test_llm():
    """测试 LLM 技能调用"""
    print("=" * 60)
    print("测试 LLM 技能调用")
    print("=" * 60)
    
    reg = get_registry()
    llm = reg.get('llm')
    
    print(f"\nAPI Key: {llm.api_key[:10] if llm.api_key else 'None'}...")
    print(f"使用 OpenAI 格式：{llm.use_openai_format}")
    print(f"模型：{llm.model}")
    
    # 手动构建工具定义（模拟 Web Server 初始化）
    from ymcode.cli.app import YMCodeApp
    app = YMCodeApp()
    app.skills_registry = reg
    tools = app._build_llm_tools()
    llm.set_available_tools(tools)
    llm.set_skills_registry(reg)
    
    print(f"可用工具：{len(llm.available_tools)}")
    for tool in llm.available_tools:
        print(f"  - {tool['function']['name']}")
    
    print("\n发送请求：帮我在 D 盘创建文件 pp")
    print("-" * 60)
    
    result = await llm.execute({
        'message': '帮我在 D 盘创建文件 pp',
        'use_tools': True
    })
    
    print("\n结果:")
    print(str(result).encode('gbk', errors='replace').decode('gbk'))
    print("=" * 60)
    
    # 检查文件是否创建成功
    import os
    if os.path.exists(r'D:\pp'):
        print("✅ 文件 D:\\pp 创建成功！")
    else:
        print("❌ 文件创建失败")

if __name__ == "__main__":
    asyncio.run(test_llm())
