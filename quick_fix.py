#!/usr/bin/env python3
"""快速修复并重启脚本"""

import os
import sys

print("=" * 60)
print("YM-CODE v0.6.0 快速修复")
print("=" * 60)
print()

# 修复 1: 更新版本号
print("修复 1: 更新版本号...")
with open("web/index.html", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("v0.3.5", "v0.6.0")
with open("web/index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("  ✅ 版本号已更新为 v0.6.0")

# 修复 2: 检查 Agent 配置菜单
print("\n修复 2: 检查 Agent 配置菜单...")
with open("web/index.html", "r", encoding="utf-8") as f:
    content = f.read()
if "Agent 配置" in content:
    print("  ✅ Agent 配置菜单已存在")
else:
    print("  ⚠️ Agent 配置菜单不存在，需要手动添加")

# 修复 3: 检查新建按钮
print("\n修复 3: 检查新建项目按钮...")
if "new-project-btn" in content:
    print("  ✅ 新建项目按钮已存在")
else:
    print("  ⚠️ 新建项目按钮不存在，需要手动添加")

print()
print("=" * 60)
print("修复完成！请重启服务：")
print("  python start-web.py")
print("=" * 60)
