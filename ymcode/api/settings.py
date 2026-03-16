#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户配置管理 API
"""

import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


# ==================== 配置模型 ====================

class UserSettings(BaseModel):
    api_key: Optional[str] = None
    model: str = "qwen3.5-plus"
    theme: str = "dark"
    auto_save: bool = True


# ==================== 配置文件管理 ====================

CONFIG_DIR = Path.home() / ".ymcode"
CONFIG_FILE = CONFIG_DIR / "user_settings.json"


def get_config_path() -> Path:
    """获取配置文件路径"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_FILE


def load_settings() -> UserSettings:
    """加载用户配置"""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserSettings(**data)
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
    
    # 从 .env 文件加载 API Key
    from dotenv import load_dotenv
    load_dotenv()
    
    return UserSettings(
        api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "qwen3.5-plus")
    )


def save_settings(settings: UserSettings):
    """保存用户配置"""
    config_path = get_config_path()
    
    # 加密 API Key（简单 Base64 编码）
    import base64
    if settings.api_key:
        encrypted_key = base64.b64encode(settings.api_key.encode()).decode()
    else:
        encrypted_key = ""
    
    data = {
        "api_key": encrypted_key,
        "model": settings.model,
        "theme": settings.theme,
        "auto_save": settings.auto_save
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"配置已保存：{config_path}")


# ==================== API 端点 ====================

@router.get("/user")
async def get_user_settings():
    """获取用户配置"""
    settings = load_settings()
    
    # 不返回完整的 API Key（只显示前缀）
    if settings.api_key:
        settings.api_key = settings.api_key[:8] + "..." if len(settings.api_key) > 8 else settings.api_key
    
    return {
        "settings": settings.dict()
    }


@router.post("/user")
async def save_user_settings(settings: UserSettings):
    """保存用户配置"""
    try:
        save_settings(settings)
        return {
            "success": True,
            "message": "配置已保存"
        }
    except Exception as e:
        logger.error(f"保存配置失败：{e}")
        raise HTTPException(status_code=500, detail=f"保存失败：{str(e)}")


@router.post("/test-api-key")
async def test_api_key(api_key: str):
    """测试 API Key 是否有效"""
    import httpx
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen3.5-plus",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://coding.dashscope.aliyuncs.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {"valid": True, "message": "API Key 有效"}
            else:
                return {"valid": False, "message": f"API Key 无效：{response.status_code}"}
                
    except Exception as e:
        return {"valid": False, "message": f"测试失败：{str(e)}"}


@router.get("/system")
async def get_system_info():
    """获取系统信息"""
    import platform
    from ..storage.session_store import get_store
    
    store = get_store()
    stats = await store.get_stats() if store and store.db else {"total_sessions": 0, "total_messages": 0}
    
    return {
        "system": {
            "version": "v0.2.0",
            "python": platform.python_version(),
            "platform": platform.system(),
            "api_status": "online",
            "database": "connected" if store and store.db else "disconnected",
            "sessions": stats.get("total_sessions", 0),
            "messages": stats.get("total_messages", 0)
        }
    }
