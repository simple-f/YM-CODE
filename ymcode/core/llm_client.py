#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一 LLM 客户端

支持 API 调用和本地模型，向后兼容
"""

import logging
from typing import Dict, Optional, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    统一 LLM 客户端
    
    根据配置自动选择 API 模式或本地模式
    向后兼容现有代码
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 LLM 客户端
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.model = None
        self._initialized = False
        
        logger.info("LLM 客户端初始化")
    
    def _initialize(self):
        """延迟初始化"""
        if self._initialized:
            return
        
        # 根据配置选择模型类型
        if self.config.get('use_local'):
            logger.info("使用本地模型模式")
            self.model = self._init_local_model()
        else:
            logger.info("使用 API 模式")
            self.model = self._init_api_model()
        
        self._initialized = True
    
    def _init_local_model(self):
        """
        初始化本地模型
        
        返回:
            LocalModel 实例
        """
        try:
            from .local_model import LocalModel
            return LocalModel(self.config)
        except ImportError as e:
            logger.warning(f"本地模型依赖未安装：{e}，回退到 API 模式")
            return self._init_api_model()
        except Exception as e:
            logger.error(f"本地模型初始化失败：{e}，回退到 API 模式")
            return self._init_api_model()
    
    def _init_api_model(self):
        """
        初始化 API 模型
        
        返回:
            APIModel 实例
        """
        from .api_model import APIModel
        return APIModel(self.config)
    
    def chat(self, prompt: str, context: Optional[Any] = None) -> str:
        """
        聊天接口（向后兼容）
        
        参数:
            prompt: 用户提示
            context: 上下文信息
        
        返回:
            AI 响应
        """
        self._initialize()
        
        if not self.model:
            raise RuntimeError("模型未初始化")
        
        try:
            response = self.model.chat(prompt, context)
            return response
        except Exception as e:
            logger.error(f"LLM 调用失败：{e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本（向后兼容）
        
        参数:
            prompt: 提示文本
            **kwargs: 其他参数
        
        返回:
            生成的文本
        """
        self._initialize()
        
        if not self.model:
            raise RuntimeError("模型未初始化")
        
        try:
            return self.model.generate(prompt, **kwargs)
        except Exception as e:
            logger.error(f"文本生成失败：{e}")
            raise
    
    def get_model_info(self) -> Dict:
        """
        获取模型信息
        
        返回:
            模型信息字典
        """
        self._initialize()
        
        if not self.model:
            return {'error': '模型未初始化'}
        
        return {
            'type': 'local' if self.config.get('use_local') else 'api',
            'model': self.model.get_info() if hasattr(self.model, 'get_info') else 'unknown'
        }


# 便捷函数（向后兼容）
_default_client: Optional[LLMClient] = None

def get_llm_client(config: Optional[Dict] = None) -> LLMClient:
    """
    获取全局 LLM 客户端实例
    
    参数:
        config: 配置字典
    
    返回:
        LLMClient 实例
    """
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(config)
    return _default_client


def chat(prompt: str, context: Optional[Any] = None) -> str:
    """
    便捷聊天函数（向后兼容）
    
    参数:
        prompt: 用户提示
        context: 上下文信息
    
    返回:
        AI 响应
    """
    client = get_llm_client()
    return client.chat(prompt, context)
