#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志轮转系统

支持：
- 按大小轮转
- 按时间轮转
- 自动清理旧日志
- 压缩归档
"""

import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, List
import gzip
import shutil


class RotatingLogger:
    """
    轮转日志器
    
    特性:
    - 按大小轮转（默认 10MB）
    - 按时间轮转（默认每天）
    - 自动压缩旧日志
    - 自动清理过期日志
    
    使用示例:
        >>> logger = RotatingLogger("ymcode", log_dir="logs")
        >>> logger.info("启动系统...")
        >>> logger.error("发生错误", exc_info=True)
    """
    
    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 7,  # 保留 7 个文件
        rotation: str = "size",  # "size" 或 "time"
        compress: bool = True,
        log_format: Optional[str] = None
    ):
        """
        初始化轮转日志器
        
        参数:
            name: 日志器名称
            log_dir: 日志目录
            level: 日志级别
            max_bytes: 单个文件最大大小（字节）
            backup_count: 保留的备份文件数量
            rotation: 轮转方式（"size" 或 "time"）
            compress: 是否压缩旧日志
            log_format: 日志格式
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = level
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.rotation = rotation
        self.compress = compress
        
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 防止重复日志
        
        # 清除现有 handler
        self.logger.handlers.clear()
        
        # 创建 formatter
        if log_format is None:
            log_format = (
                "%(asctime)s | %(levelname)-8s | "
                "%(name)s | %(filename)s:%(lineno)d | "
                "%(message)s"
            )
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        
        # 创建 handler
        if rotation == "time":
            # 按时间轮转（每天）
            handler = TimedRotatingFileHandler(
                self.log_dir / f"{name}.log",
                when="midnight",
                interval=1,
                backupCount=backup_count,
                encoding="utf-8"
            )
            handler.suffix = "%Y%m%d"
        else:
            # 按大小轮转
            handler = RotatingFileHandler(
                self.log_dir / f"{name}.log",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
        
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # 添加控制台 handler（可选）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 只输出 warning 以上
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 启动日志清理任务
        self._cleanup_old_logs()
    
    def debug(self, msg, *args, **kwargs):
        """Debug 级别日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """Info 级别日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Warning 级别日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, exc_info=False, **kwargs):
        """Error 级别日志"""
        self.logger.error(msg, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, msg, *args, exc_info=True, **kwargs):
        """Critical 级别日志"""
        self.logger.critical(msg, *args, exc_info=exc_info, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        """Exception 级别日志（自动包含堆栈）"""
        self.logger.exception(msg, *args, **kwargs)
    
    def _cleanup_old_logs(self):
        """清理过期日志"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.backup_count)
            
            for log_file in self.log_dir.glob(f"{self.name}*.log*"):
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if mtime < cutoff_date:
                    # 删除过期日志
                    log_file.unlink()
                    self.logger.info(f"清理过期日志：{log_file.name}")
        
        except Exception as e:
            self.logger.error(f"清理日志失败：{e}")
    
    def compress_old_logs(self):
        """压缩旧日志"""
        if not self.compress:
            return
        
        try:
            for log_file in self.log_dir.glob(f"{self.name}*.log.*"):
                # 跳过已压缩的文件
                if log_file.suffix == ".gz":
                    continue
                
                # 压缩日志
                compressed_path = log_file.with_suffix(log_file.suffix + ".gz")
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原始文件
                log_file.unlink()
                
                self.logger.info(f"压缩日志：{log_file.name} -> {compressed_path.name}")
        
        except Exception as e:
            self.logger.error(f"压缩日志失败：{e}")
    
    def get_log_files(self) -> List[Path]:
        """获取所有日志文件"""
        return sorted(self.log_dir.glob(f"{self.name}*.log*"))
    
    def get_log_size(self) -> int:
        """获取日志总大小（字节）"""
        return sum(f.stat().st_size for f in self.get_log_files())
    
    def get_log_size_mb(self) -> float:
        """获取日志总大小（MB）"""
        return self.get_log_size() / (1024 * 1024)
    
    def get_stats(self) -> dict:
        """获取日志统计"""
        files = self.get_log_files()
        return {
            "name": self.name,
            "log_dir": str(self.log_dir),
            "file_count": len(files),
            "total_size_bytes": self.get_log_size(),
            "total_size_mb": self.get_log_size_mb(),
            "oldest_file": files[0].name if files else None,
            "newest_file": files[-1].name if files else None
        }
    
    def close(self):
        """关闭日志器"""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()


# 全局日志器实例
_global_loggers = {}


def get_rotating_logger(
    name: str,
    log_dir: str = "logs",
    **kwargs
) -> RotatingLogger:
    """
    获取全局轮转日志器
    
    参数:
        name: 日志器名称
        log_dir: 日志目录
        **kwargs: 其他参数传递给 RotatingLogger
    
    返回:
        RotatingLogger 实例
    """
    if name not in _global_loggers:
        _global_loggers[name] = RotatingLogger(name, log_dir, **kwargs)
    return _global_loggers[name]


def close_all_loggers():
    """关闭所有日志器"""
    for logger in _global_loggers.values():
        logger.close()
    _global_loggers.clear()


# 便捷函数
def setup_default_logging(log_dir: str = "logs"):
    """设置默认日志"""
    return get_rotating_logger(
        "ymcode",
        log_dir=log_dir,
        level=logging.INFO,
        rotation="size",
        max_bytes=10 * 1024 * 1024,
        backup_count=7
    )


# 使用示例
if __name__ == "__main__":
    # 创建日志器
    logger = get_rotating_logger(
        "test",
        log_dir="test_logs",
        level=logging.DEBUG
    )
    
    # 测试日志
    logger.debug("这是一条 debug 日志")
    logger.info("这是一条 info 日志")
    logger.warning("这是一条 warning 日志")
    logger.error("这是一条 error 日志")
    logger.critical("这是一条 critical 日志")
    
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("发生异常")
    
    # 查看统计
    stats = logger.get_stats()
    print(f"\n日志统计：{stats}")
    
    # 关闭
    logger.close()
