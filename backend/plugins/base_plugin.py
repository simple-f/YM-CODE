"""
插件基类

所有插件必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePlugin(ABC):
    """插件基类"""
    
    name: str = "base"
    version: str = "1.0.0"
    description: str = ""
    author: Optional[str] = None
    
    @abstractmethod
    async def run(self, params: Dict[str, Any]) -> Any:
        """
        运行插件
        
        参数:
            params: 参数
        
        返回:
            执行结果
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取参数 Schema
        
        返回:
            JSON Schema
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取插件配置
        
        返回:
            配置字典
        """
        return {}
    
    async def initialize(self) -> None:
        """初始化插件（可选）"""
        pass
    
    async def cleanup(self) -> None:
        """清理资源（可选）"""
        pass
