#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Manager - 状态管理

融合课程：s03 (TodoWrite)
"""

import logging
from typing import Dict, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        self.current_state = "idle"
        self.metadata = {}
    
    def set_state(self, state: str, **metadata):
        """
        设置状态
        
        参数:
            state: 状态名
            metadata: 元数据
        """
        self.current_state = state
        self.metadata = metadata
        logger.info(f"状态变更：{state}")
    
    def get_current_state(self) -> Dict:
        """
        获取当前状态
        
        返回:
            状态字典
        """
        return {
            "state": self.current_state,
            "metadata": self.metadata
        }
    
    def is_idle(self) -> bool:
        """检查是否空闲"""
        return self.current_state == "idle"
