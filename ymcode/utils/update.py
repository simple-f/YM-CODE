#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新检查器
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx

from ..__version__ import __version__
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UpdateChecker:
    """自动更新检查器"""
    
    UPDATE_CHECK_INTERVAL = timedelta(hours=24)  # 24 小时检查一次
    GITHUB_API_URL = "https://api.github.com/repos/ym-code/ym-code/releases/latest"
    
    def __init__(self, cache_file: str = None):
        """
        初始化更新检查器
        
        参数:
            cache_file: 缓存文件路径
        """
        self.cache_file = Path(cache_file) if cache_file else Path.home() / '.ymcode' / 'update_cache.json'
        self.last_check: Optional[datetime] = None
        self.latest_version: Optional[str] = None
        self.update_info: Optional[Dict] = None
        
        # 确保缓存目录存在
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载缓存
        self._load_cache()
        
        logger.info(f"更新检查器初始化完成（当前版本：{__version__}）")
    
    def _load_cache(self) -> None:
        """加载缓存"""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            self.last_check = datetime.fromisoformat(cache.get('last_check')) if cache.get('last_check') else None
            self.latest_version = cache.get('latest_version')
            self.update_info = cache.get('update_info')
            
            logger.debug(f"加载更新缓存：{self.latest_version}")
        except Exception as e:
            logger.warning(f"加载更新缓存失败：{e}")
    
    def _save_cache(self) -> None:
        """保存缓存"""
        try:
            cache = {
                'last_check': self.last_check.isoformat() if self.last_check else None,
                'latest_version': self.latest_version,
                'update_info': self.update_info
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            
            logger.debug("保存更新缓存")
        except Exception as e:
            logger.warning(f"保存更新缓存失败：{e}")
    
    def should_check(self) -> bool:
        """判断是否应该检查更新"""
        if not self.last_check:
            return True
        
        return datetime.now() - self.last_check > self.UPDATE_CHECK_INTERVAL
    
    async def check_update(self, force: bool = False) -> Dict[str, Any]:
        """
        检查更新
        
        参数:
            force: 强制检查（忽略缓存）
        
        返回:
            更新信息
        """
        # 检查是否需要更新
        if not force and not self.should_check():
            logger.debug("未到检查时间，使用缓存")
            return self._get_update_status()
        
        try:
            logger.info("检查更新...")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.GITHUB_API_URL)
                
                if response.status_code != 200:
                    logger.warning(f"GitHub API 请求失败：{response.status_code}")
                    return self._get_update_status()
                
                data = response.json()
                
                self.latest_version = data.get('tag_name', '').lstrip('v')
                self.update_info = {
                    'version': self.latest_version,
                    'published_at': data.get('published_at'),
                    'url': data.get('html_url'),
                    'name': data.get('name'),
                    'body': data.get('body', '')
                }
                
                self.last_check = datetime.now()
                self._save_cache()
                
                logger.info(f"最新版本：{self.latest_version}")
                
        except Exception as e:
            logger.error(f"检查更新失败：{e}")
        
        return self._get_update_status()
    
    def _get_update_status(self) -> Dict[str, Any]:
        """获取更新状态"""
        if not self.latest_version:
            return {
                'current_version': __version__,
                'latest_version': None,
                'has_update': False,
                'message': '无法获取最新版本信息'
            }
        
        # 版本比较
        has_update = self._compare_versions(self.latest_version, __version__) > 0
        
        return {
            'current_version': __version__,
            'latest_version': self.latest_version,
            'has_update': has_update,
            'update_info': self.update_info,
            'message': f'发现新版本 {self.latest_version}' if has_update else '已是最新版本'
        }
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        比较版本号
        
        参数:
            v1: 版本 1
            v2: 版本 2
        
        返回:
            >0 如果 v1 > v2
            0  如果 v1 == v2
            <0 如果 v1 < v2
        """
        def parse_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                p1 = v1_parts[i] if i < len(v1_parts) else 0
                p2 = v2_parts[i] if i < len(v2_parts) else 0
                
                if p1 != p2:
                    return p1 - p2
            
            return 0
        except Exception:
            return 0
    
    def get_changelog(self) -> str:
        """获取更新日志"""
        if not self.update_info:
            return "无更新日志"
        
        return self.update_info.get('body', '无更新日志')
    
    def clear_cache(self) -> None:
        """清空缓存"""
        if self.cache_file.exists():
            self.cache_file.unlink()
        
        self.last_check = None
        self.latest_version = None
        self.update_info = None
        
        logger.info("更新缓存已清空")


# 全局实例
_checker: Optional[UpdateChecker] = None


def get_checker() -> UpdateChecker:
    """获取全局检查器实例"""
    global _checker
    if _checker is None:
        _checker = UpdateChecker()
    return _checker


async def check_update(force: bool = False) -> Dict[str, Any]:
    """便捷函数：检查更新"""
    return await get_checker().check_update(force)
