#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger - 日志系统

融合课程：生产级日志设计
"""

import logging
import sys
import os
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
    
    # 控制台处理器（Windows 兼容，简单格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器（延迟打开，避免文件占用问题）
    log_dir = Path.home() / ".ymcode" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Windows 兼容：延迟打开 + 捕获轮转异常
        file_handler = RotatingFileHandler(
            log_dir / "ymcode.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8',
            delay=True  # 延迟打开文件（关键！）
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 覆盖 rotate 方法，忽略文件占用错误
        original_rotate = file_handler.rotate
        def safe_rotate(source, dest):
            try:
                original_rotate(source, dest)
            except PermissionError:
                # 文件被占用，跳过轮转（不影响日志写入）
                pass
        file_handler.rotate = safe_rotate
        
        logger.addHandler(file_handler)
    except Exception as e:
        # 静默失败，不影响主程序
        logger.debug(f"文件日志初始化失败：{e}")
    
    # 简单格式（避免编码问题）
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger
