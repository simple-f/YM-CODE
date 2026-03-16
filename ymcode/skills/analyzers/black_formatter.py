#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black 代码格式化器
"""

import logging
import black
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BlackFormatter:
    """Black 代码格式化器"""
    
    def supports(self, language: str) -> bool:
        """检查是否支持该语言"""
        return language == 'python'
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        格式化代码
        
        参数:
            code: 代码字符串
        
        返回:
            格式化结果
        """
        try:
            # 使用 Black 格式化
            formatted = black.format_str(
                code,
                mode=black.FileMode(
                    line_length=88,
                    target_versions={black.TargetVersion.PY38}
                )
            )
            
            # 比较差异
            is_changed = formatted != code
            
            return {
                'formatted_code': formatted,
                'is_changed': is_changed,
                'original_length': len(code),
                'formatted_length': len(formatted),
                'issue_count': 1 if is_changed else 0,
                'warning_count': 0,
                'suggestions': ['代码已格式化'] if is_changed else ['代码格式良好']
            }
        
        except black.NothingChanged:
            return {
                'formatted_code': code,
                'is_changed': False,
                'issue_count': 0,
                'warning_count': 0,
                'suggestions': ['代码格式良好']
            }
        
        except Exception as e:
            logger.error(f"Black 格式化失败：{e}")
            return {
                'error': str(e),
                'issue_count': 0
            }
