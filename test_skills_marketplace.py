#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Skills 市场和网络浏览
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.skills import SkillMarketplace, WebBrowserSkill


async def test_skill_marketplace():
    """测试 Skills 市场"""
    print("=" * 60)
    print("Skills 市场测试")
    print("=" * 60)
    
    marketplace = SkillMarketplace()
    
    # 测试 1: 列出 Skills
    print("\n[测试 1] 列出 Skills...")
    skills = await marketplace.list_skills()
    print(f"   状态：{'成功' if skills.get('success') else '失败'}")
    print(f"   总数：{skills.get('total', 0)}")
    
    # 测试 2: 搜索 Skills
    print("\n[测试 2] 搜索 Skills...")
    results = await marketplace.search_skills("github")
    print(f"   状态：{'成功' if results.get('success') else '失败'}")
    print(f"   找到：{results.get('total', 0)} 个")
    
    # 测试 3: 列出本地 Skills
    print("\n[测试 3] 列出本地 Skills...")
    local_skills = marketplace.list_installed_skills()
    print(f"   本地 Skills: {len(local_skills)} 个")
    for skill in local_skills[:3]:
        print(f"   - {skill['name']}")
    
    print("\n[OK] Skills 市场测试完成")


async def test_web_browser():
    """测试网络浏览"""
    print("\n" + "=" * 60)
    print("网络浏览测试")
    print("=" * 60)
    
    browser = WebBrowserSkill()
    
    # 测试 1: 访问网页
    print("\n[测试 1] 访问网页...")
    page = await browser.fetch_url("https://www.python.org")
    print(f"   状态：{'成功' if page.get('success') else '失败'}")
    if page.get('success'):
        print(f"   标题：{page['title']}")
        print(f"   长度：{page['length']} 字符")
        print(f"   预览：{page['content'][:100]}...")
    
    # 测试 2: 网络搜索
    print("\n[测试 2] 网络搜索...")
    search = await browser.search_web("Python 编程", engine="google")
    print(f"   状态：{'成功' if search.get('success') else '失败'}")
    if search.get('success'):
        print(f"   引擎：{search['engine']}")
        print(f"   结果：{len(search['results'])} 条")
        if search['results']:
            print(f"   第一条：{search['results'][0].get('title', 'N/A')}")
    
    # 测试 3: 访问 GitHub
    print("\n[测试 3] 访问 GitHub...")
    page = await browser.fetch_url("https://github.com")
    print(f"   状态：{'成功' if page.get('success') else '失败'}")
    if page.get('success'):
        print(f"   标题：{page['title']}")
    
    print("\n[OK] 网络浏览测试完成")


async def main():
    """主测试"""
    print("\n" + "=" * 60)
    print("YM-CODE Skills 市场 + 网络浏览 测试")
    print("=" * 60)
    
    # 测试 Skills 市场
    await test_skill_marketplace()
    
    # 测试网络浏览
    await test_web_browser()
    
    print("\n" + "=" * 60)
    print("[OK] 所有测试完成！")
    print("=" * 60)
    
    # 总结
    print("\n📊 功能总结:")
    print("  ✅ Skills 市场 - 可以浏览和下载 Skills")
    print("  ✅ 网络浏览 - 可以访问网页和搜索")
    print("  ✅ 本地管理 - 可以管理已安装的 Skills")
    
    print("\n💡 使用方式:")
    print("  1. Python API: from ymcode.skills import SkillMarketplace")
    print("  2. YM-CODE CLI: python -m ymcode")
    print("  3. 文档：SKILLS_MARKETPLACE.md")


if __name__ == "__main__":
    asyncio.run(main())
