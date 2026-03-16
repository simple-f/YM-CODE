#!/usr/bin/env python3
"""添加静态文件路由"""

import sys
from pathlib import Path

server_file = Path("ymcode/api/server.py")

with open(server_file, "r", encoding="utf-8") as f:
    content = f.read()

# 添加路由
new_routes = '''
@app.get("/agent-config.html")
async def agent_config():
    """Agent 配置页面"""
    return FileResponse(Path(__file__).parent.parent / "web" / "agent-config.html")

@app.get("/")
async def root():
    """根路径"""
    return FileResponse(Path(__file__).parent.parent / "web" / "index.html")
'''

# 在文件末尾添加
if "@app.get(\"/agent-config.html\")" not in content:
    content = content.rstrip() + "\n" + new_routes
    with open(server_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 已添加静态文件路由")
else:
    print("✅ 路由已存在")
