#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 主入口 - 跨平台版本 (Windows/Linux/macOS)
"""

import sys
import os
import platform

# 全局设置 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Windows 特定设置
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# 检测系统信息
SYSTEM_INFO = {
    'os': platform.system(),  # Windows, Linux, Darwin
    'os_version': platform.version(),
    'machine': platform.machine(),
    'python_version': platform.python_version()
}

# 根据系统决定是否启用颜色
if SYSTEM_INFO['os'] == 'Windows':
    # Windows 终端可能不支持彩色，保守处理
    os.environ.setdefault('RICH_COLOR', 'false')
else:
    # Linux/macOS 启用彩色输出
    os.environ.setdefault('RICH_COLOR', 'true')

from ymcode.cli.app import main

if __name__ == "__main__":
    # 显示系统信息（调试模式）
    if '--debug' in sys.argv:
        print(f"System: {SYSTEM_INFO['os']} {SYSTEM_INFO['os_version']}")
        print(f"Machine: {SYSTEM_INFO['machine']}")
        print(f"Python: {SYSTEM_INFO['python_version']}")
    
    main()
