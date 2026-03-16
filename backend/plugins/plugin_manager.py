"""
插件管理器

负责插件的加载、注册和管理
"""

import logging
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Type
from .base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_path: Optional[str] = None):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self.plugin_path = plugin_path
    
    def register(self, plugin: BasePlugin) -> bool:
        """
        注册插件
        
        参数:
            plugin: 插件实例
        
        返回:
            是否成功
        """
        if plugin.name in self.plugins:
            logger.warning(f"插件已存在：{plugin.name}")
            return False
        
        self.plugins[plugin.name] = plugin
        logger.info(f"注册插件：{plugin.name}")
        return True
    
    def register_class(self, plugin_class: Type[BasePlugin]) -> bool:
        """
        注册插件类
        
        参数:
            plugin_class: 插件类
        
        返回:
            是否成功
        """
        try:
            instance = plugin_class()
            name = instance.name
            self.plugin_classes[name] = plugin_class
            logger.info(f"注册插件类：{name}")
            return True
        except Exception as e:
            logger.error(f"注册插件类失败：{e}")
            return False
    
    def get(self, name: str) -> Optional[BasePlugin]:
        """
        获取插件
        
        参数:
            name: 插件名称
        
        返回:
            插件实例
        """
        if name not in self.plugins:
            if name in self.plugin_classes:
                try:
                    plugin = self.plugin_classes[name]()
                    self.plugins[name] = plugin
                    return plugin
                except Exception as e:
                    logger.error(f"创建插件失败：{e}")
                    return None
            return None
        
        return self.plugins[name]
    
    def list_plugins(self) -> List[Dict]:
        """
        列出所有插件
        
        返回:
            插件信息列表
        """
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author
            }
            for plugin in self.plugins.values()
        ]
    
    async def load_from_directory(self, directory: str) -> int:
        """
        从目录加载插件
        
        参数:
            directory: 插件目录路径
        
        返回:
            加载的插件数量
        """
        loaded_count = 0
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists():
            logger.warning(f"插件目录不存在：{directory}")
            return 0
        
        for item in plugin_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # 尝试加载插件
                plugin_file = item / 'plugin.py'
                if plugin_file.exists():
                    try:
                        # 动态导入
                        spec = importlib.util.spec_from_file_location(
                            f"plugins.{item.name}",
                            plugin_file
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 查找插件类
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BasePlugin) and 
                                attr is not BasePlugin):
                                self.register_class(attr)
                                loaded_count += 1
                    
                    except Exception as e:
                        logger.error(f"加载插件失败 {item.name}: {e}")
        
        logger.info(f"从目录加载了 {loaded_count} 个插件：{directory}")
        return loaded_count
    
    async def initialize_all(self) -> None:
        """初始化所有插件"""
        for plugin in self.plugins.values():
            try:
                await plugin.initialize()
                logger.info(f"插件初始化完成：{plugin.name}")
            except Exception as e:
                logger.error(f"插件初始化失败 {plugin.name}: {e}")
    
    async def cleanup_all(self) -> None:
        """清理所有插件"""
        for plugin in self.plugins.values():
            try:
                await plugin.cleanup()
                logger.info(f"插件清理完成：{plugin.name}")
            except Exception as e:
                logger.error(f"插件清理失败 {plugin.name}: {e}")
