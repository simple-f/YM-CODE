"""
插件 API

提供插件管理、安装、启用等接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# 临时存储
plugins_db = {}


class PluginInfo(BaseModel):
    """插件信息"""
    name: str
    version: str
    description: str
    enabled: bool
    author: Optional[str] = None


@router.get("/plugins", response_model=List[PluginInfo])
async def list_plugins(enabled: Optional[bool] = None):
    """
    查询插件列表
    
    - **enabled**: 按启用状态过滤（可选）
    """
    plugins = list(plugins_db.values())
    
    if enabled is not None:
        plugins = [p for p in plugins if p["enabled"] == enabled]
    
    return [PluginInfo(**p) for p in plugins]


@router.post("/plugins/install")
async def install_plugin(plugin_url: str):
    """
    安装插件
    
    - **plugin_url**: 插件 URL 或路径
    """
    # TODO: 实现插件安装逻辑
    return {
        "message": "插件安装成功",
        "plugin_url": plugin_url
    }


@router.post("/plugins/{plugin_name}/enable")
async def enable_plugin(plugin_name: str):
    """
    启用插件
    
    - **plugin_name**: 插件名称
    """
    if plugin_name not in plugins_db:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    plugins_db[plugin_name]["enabled"] = True
    return {"message": f"插件 {plugin_name} 已启用"}


@router.post("/plugins/{plugin_name}/disable")
async def disable_plugin(plugin_name: str):
    """
    禁用插件
    
    - **plugin_name**: 插件名称
    """
    if plugin_name not in plugins_db:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    plugins_db[plugin_name]["enabled"] = False
    return {"message": f"插件 {plugin_name} 已禁用"}
