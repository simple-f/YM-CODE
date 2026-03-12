#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger - 日志系统

融合课程：生产级日志设计
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器
    
    参数:
        name: 日志器名称
    
    返回:
        日志器实例
    """
    logger = logging.getLogger(name)
    
    # 如果已有处理器，直接返回
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器
    log_dir = Path.home() / ".ymcode" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_dir / "ymcode.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
