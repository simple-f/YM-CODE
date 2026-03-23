#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE Dashboard 启动脚本

用法:
    python start_dashboard.py [--host 0.0.0.0] [--port 8080] [--reload]
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(description='启动 YM-CODE Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认：0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='监听端口 (默认：8080)')
    parser.add_argument('--reload', action='store_true', help='启用自动重载')
    parser.add_argument('--workers', type=int, default=1, help='worker 数量 (默认：1)')
    
    args = parser.parse_args()
    
    try:
        from ymcode.web.dashboard_api import run_dashboard
        
        print("=" * 60)
        print("YM-CODE Dashboard")
        print("=" * 60)
        print(f"Address: http://{args.host}:{args.port}/dashboard")
        print(f"API Docs: http://{args.host}:{args.port}/docs")
        print(f"Reload: {'Enabled' if args.reload else 'Disabled'}")
        print(f"Workers: {args.workers}")
        print("=" * 60)
        print()
        print("Press Ctrl+C to stop")
        print()
        
        # 如果 workers > 1，使用 uvicorn 直接运行
        if args.workers > 1:
            import uvicorn
            uvicorn.run(
                "ymcode.web.dashboard_api:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                workers=args.workers
            )
        else:
            run_dashboard(
                host=args.host,
                port=args.port,
                reload=args.reload
            )
            
    except ImportError as e:
        print(f"Import error: {e}")
        print()
        print("Please install dependencies:")
        print("  pip install fastapi uvicorn python-multipart")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("Service stopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
