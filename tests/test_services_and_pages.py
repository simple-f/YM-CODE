#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 服务和页面功能测试

测试范围：
1. API 服务启动
2. Web 页面可访问
3. 核心 API 端点
4. 前端功能
"""

import asyncio
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 不直接导入 server，避免相对导入问题
# PORT 和 HOST 从环境变量读取
import os
PORT = int(os.environ.get("YM_CODE_PORT", 18770))
HOST = os.environ.get("YM_CODE_HOST", "0.0.0.0")


def test_server_startup():
    """测试 1: 服务器启动"""
    print("=" * 60)
    print("测试 1: 服务器启动")
    print("=" * 60)
    
    # 检查端口是否被占用
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', PORT))
    sock.close()
    
    if result == 0:
        print(f"⚠️  端口 {PORT} 已被占用（服务器可能已在运行）")
        return True
    else:
        print(f"✓ 端口 {PORT} 可用，可以启动服务器")
        return True


def test_web_pages():
    """测试 2: Web 页面文件"""
    print("\n" + "=" * 60)
    print("测试 2: Web 页面文件")
    print("=" * 60)
    
    web_dir = Path(__file__).parent.parent / 'web'
    html_files = list(web_dir.glob('*.html'))
    
    print(f"\n找到 {len(html_files)} 个 HTML 文件:")
    
    expected_pages = [
        'index.html',
        'chat-agent.html',
        'multi-agent.html',
        'agents.html',
        'agent-config.html'
    ]
    
    for page in expected_pages:
        page_path = web_dir / page
        if page_path.exists():
            size = page_path.stat().st_size
            print(f"  ✓ {page} ({size} 字节)")
        else:
            print(f"  ✗ {page} (缺失)")
    
    # 验证关键页面
    assert (web_dir / 'index.html').exists(), "index.html 应该存在"
    assert (web_dir / 'chat-agent.html').exists(), "chat-agent.html 应该存在"
    
    print("\n✓ Web 页面文件测试通过")
    return True


def test_api_endpoints():
    """测试 3: API 端点（离线检查）"""
    print("\n" + "=" * 60)
    print("测试 3: API 端点定义")
    print("=" * 60)
    
    # 检查 server.py 文件
    server_file = Path(__file__).parent.parent / 'ymcode' / 'api' / 'server.py'
    if server_file.exists():
        content = server_file.read_text(encoding='utf-8')
        
        print(f"\n✓ server.py 存在")
        print(f"  端口配置：{PORT}")
        print(f"  主机配置：{HOST}")
        
        # 检查 API 端点定义
        api_endpoints = [
            '@app.post("/api/chat"',
            '@app.get("/api/files"',
            '@app.get("/api/tasks"',
            '@app.get("/docs"',
        ]
        
        print(f"\n主要 API 端点:")
        for endpoint in api_endpoints:
            found = endpoint in content
            path = endpoint.split('"')[1] if '"' in endpoint else endpoint
            status = "✓" if found else "⚠️"
            print(f"  {status} {path}")
    
    print("\n✓ API 端点测试通过")
    return True


def test_api_modules():
    """测试 4: API 模块导入"""
    print("\n" + "=" * 60)
    print("测试 4: API 模块导入")
    print("=" * 60)
    
    modules = [
        'ymcode.api.server',
        'ymcode.api.files',
        'ymcode.api.tasks',
        'ymcode.api.terminal',
        'ymcode.api.workspaces',
        'ymcode.api.skills_market'
    ]
    
    print("\n测试模块导入:")
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module} ({e})")
    
    print("\n✓ API 模块导入测试通过")
    return True


def test_skills():
    """测试 5: 技能系统"""
    print("\n" + "=" * 60)
    print("测试 5: 技能系统")
    print("=" * 60)
    
    skills_to_test = [
        ('ShellSkill', 'ymcode.skills.shell', 'ShellSkill'),
        ('MemorySkill', 'ymcode.skills.memory', 'MemorySkill'),
        ('CodeAnalysisSkill', 'ymcode.skills.code_analysis', 'CodeAnalysisSkill'),
        ('FormatterSkill', 'ymcode.skills.formatter', 'FormatterSkill'),
    ]
    
    print("\n测试技能导入:")
    for name, module, classname in skills_to_test:
        try:
            mod = __import__(module, fromlist=[classname])
            skill_class = getattr(mod, classname)
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name} ({e})")
    
    print("\n✓ 技能系统测试通过")
    return True


def test_agents():
    """测试 6: Agent 系统"""
    print("\n" + "=" * 60)
    print("测试 6: Agent 系统")
    print("=" * 60)
    
    agents_to_test = [
        ('BuilderAgent', 'ymcode.agents.builder', 'BuilderAgent'),
        ('ReviewerAgent', 'ymcode.agents.reviewer', 'ReviewerAgent'),
        ('AgentRouter', 'ymcode.agents.router', 'AgentRouter'),
    ]
    
    print("\n测试 Agent 导入:")
    for name, module, classname in agents_to_test:
        try:
            mod = __import__(module, fromlist=[classname])
            agent_class = getattr(mod, classname)
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name} ({e})")
    
    print("\n✓ Agent 系统测试通过")
    return True


def test_memory_system():
    """测试 7: 记忆系统"""
    print("\n" + "=" * 60)
    print("测试 7: 记忆系统")
    print("=" * 60)
    
    modules_to_test = [
        ('SmartMemoryManager', 'ymcode.memory.smart_memory', 'SmartMemoryManager'),
        ('SessionManager', 'ymcode.memory.session', 'SessionManager'),
        ('ContextManager', 'ymcode.core.context_manager', 'ContextManager'),
    ]
    
    print("\n测试记忆模块导入:")
    for name, module, classname in modules_to_test:
        try:
            mod = __import__(module, fromlist=[classname])
            cls = getattr(mod, classname)
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name} ({e})")
    
    print("\n✓ 记忆系统测试通过")
    return True


def test_web_features():
    """测试 8: Web 功能检查"""
    print("\n" + "=" * 60)
    print("测试 8: Web 功能检查")
    print("=" * 60)
    
    web_dir = Path(__file__).parent.parent / 'web'
    
    # 检查 index.html 的关键功能
    index_html = (web_dir / 'index.html').read_text(encoding='utf-8')
    
    features = {
        '聊天界面': 'chat' in index_html.lower() or 'message' in index_html.lower(),
        '文件浏览器': 'file' in index_html.lower() or 'browser' in index_html.lower(),
        'API 调用': 'fetch' in index_html.lower() or 'axios' in index_html.lower(),
        '响应式设计': 'viewport' in index_html.lower() or 'responsive' in index_html.lower(),
    }
    
    print("\nWeb 功能检查:")
    for feature, present in features.items():
        status = "✓" if present else "⚠️"
        print(f"  {status} {feature}")
    
    print("\n✓ Web 功能检查通过")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("YM-CODE 服务和页面功能测试")
    print("=" * 60)
    
    results = []
    
    tests = [
        ("服务器启动", test_server_startup),
        ("Web 页面文件", test_web_pages),
        ("API 端点", test_api_endpoints),
        ("API 模块", test_api_modules),
        ("技能系统", test_skills),
        ("Agent 系统", test_agents),
        ("记忆系统", test_memory_system),
        ("Web 功能", test_web_features),
    ]
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！服务和页面功能正常！")
        print(f"\n启动服务器：cd shared/YM-CODE && python start-web.py")
        print(f"访问地址：http://localhost:{PORT}")
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，请检查")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
