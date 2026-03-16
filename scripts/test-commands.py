#!/usr/bin/env python3
"""测试所有 Shell 命令"""
import asyncio
import sys
from pathlib import Path

workspace = Path(__file__).parent
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

from ymcode.skills import get_registry

async def test_commands():
    """测试常用命令"""
    print("=" * 60)
    print("测试 Shell 命令支持")
    print("=" * 60)
    
    reg = get_registry()
    shell = reg.get('shell')
    
    tests = [
        # 文件操作
        ("列出 D 盘", {'command': 'dir', 'args': ['D:\\']}),
        ("列出当前目录", {'command': 'dir'}),
        ("创建文件夹", {'command': 'mkdir', 'args': ['test_dir']}),
        ("删除文件夹", {'command': 'rmdir', 'args': ['test_dir']}),
        ("创建文件 - type", {'command': 'type', 'args': ['nul', '>', 'test.txt']}),
        ("查看文件", {'command': 'type', 'args': ['test.txt']}),
        ("删除文件", {'command': 'del', 'args': ['test.txt']}),
        # 系统信息
        ("系统信息", {'command': 'systeminfo'}),
        ("IP 配置", {'command': 'ipconfig'}),
    ]
    
    for name, params in tests:
        print(f"\n{name}...")
        print("-" * 60)
        result = await shell.execute(params)
        
        if result.get('success'):
            print(f"[OK] {name}")
            stdout = result.get('stdout', '')[:200]
            if stdout:
                print(f"    输出：{stdout}...")
        else:
            print(f"[FAIL] {name}")
            error = result.get('error', '')
            print(f"    错误：{error}")

if __name__ == "__main__":
    asyncio.run(test_commands())
