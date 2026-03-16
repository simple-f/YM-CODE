#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动 YM-CODE Web Server
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
workspace = Path(__file__).parent
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

from ymcode.api.server import PORT, HOST, DEBUG

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("                  YM-CODE Web Server")
    print("=" * 60)
    print(f"  Web UI:    http://localhost:{PORT}")
    print(f"  API Docs:  http://localhost:{PORT}/docs")
    print(f"  Host:      {HOST}")
    print(f"  Debug:     {DEBUG}")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        "ymcode.api.server:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
