#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 配置管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from .utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Config:
    """配置数据类"""
    
    # API 配置
    api_endpoint: str = 'http://localhost:8080'
    api_key: str = ''
    model: str = 'qwen3.5-plus'
    max_tokens: int = 4000
    timeout: int = 30
    
    # MCP 配置
    mcp_enabled: bool = True
    mcp_servers: list = field(default_factory=list)
    
    # LSP 配置
    lsp_enabled: bool = True
    lsp_servers: dict = field(default_factory=dict)
    
    # UI 配置
    theme: str = 'auto'  # auto, light, dark
    language: str = 'zh-CN'
    
    # 高级配置
    debug: bool = False
    log_level: str = 'INFO'
    auto_update: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        data = asdict(self)
        data.pop('api_key', None)  # 不暴露 API key
        return data


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_FILE = Path.home() / '.ymcode' / 'config.json'
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        参数:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file) if config_file else self.DEFAULT_CONFIG_FILE
        self.config = Config()
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_config()
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
        
        logger.info(f"配置管理器初始化完成（配置文件：{self.config_file}）")
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if not self.config_file.exists():
            logger.info("配置文件不存在，使用默认配置")
            self._save_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新配置
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            logger.info("配置加载成功")
        except Exception as e:
            logger.warning(f"加载配置文件失败：{e}，使用默认配置")
            self._save_config()
    
    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败：{e}")
    
    def _apply_env_overrides(self) -> None:
        """应用环境变量覆盖"""
        env_mapping = {
            'YM_CODE_API_ENDPOINT': 'api_endpoint',
            'YM_CODE_API_KEY': 'api_key',
            'YM_CODE_MODEL': 'model',
            'YM_CODE_MAX_TOKENS': 'max_tokens',
            'YM_CODE_TIMEOUT': 'timeout',
            'YM_CODE_THEME': 'theme',
            'YM_CODE_LANGUAGE': 'language',
            'YM_CODE_DEBUG': 'debug',
            'YM_CODE_LOG_LEVEL': 'log_level',
        }
        
        for env_var, config_attr in env_mapping.items():
            value = os.environ.get(env_var)
            if value:
                # 类型转换
                if config_attr in ['max_tokens', 'timeout']:
                    value = int(value)
                elif config_attr in ['debug', 'mcp_enabled', 'lsp_enabled', 'auto_update']:
                    value = value.lower() in ['true', '1', 'yes']
                
                setattr(self.config, config_attr, value)
                logger.debug(f"环境变量覆盖：{env_var}={value}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """设置配置项"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            if save:
                self._save_config()
        else:
            logger.warning(f"未知配置项：{key}")
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.to_dict()
    
    def reset(self) -> None:
        """重置为默认配置"""
        self.config = Config()
        self._save_config()
        logger.info("配置已重置为默认值")
    
    def validate(self) -> bool:
        """验证配置"""
        # 验证 API 端点
        if not self.config.api_endpoint.startswith(('http://', 'https://')):
            logger.error(f"无效的 API 端点：{self.config.api_endpoint}")
            return False
        
        # 验证模型
        if not self.config.model:
            logger.error("模型不能为空")
            return False
        
        # 验证 token 数
        if self.config.max_tokens <= 0:
            logger.error("max_tokens 必须大于 0")
            return False
        
        # 验证超时
        if self.config.timeout <= 0:
            logger.error("timeout 必须大于 0")
            return False
        
        logger.info("配置验证通过")
        return True
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取 API 配置"""
        return {
            'endpoint': self.config.api_endpoint,
            'api_key': self.config.api_key,
            'model': self.config.model,
            'max_tokens': self.config.max_tokens,
            'timeout': self.config.timeout
        }
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """获取 MCP 配置"""
        return {
            'enabled': self.config.mcp_enabled,
            'servers': self.config.mcp_servers
        }
    
    def get_lsp_config(self) -> Dict[str, Any]:
        """获取 LSP 配置"""
        return {
            'enabled': self.config.lsp_enabled,
            'servers': self.config.lsp_servers
        }


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> ConfigManager:
    """重新加载配置"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager
