#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能市场 API - 技能发现、安装、管理
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import json

from ..utils.logger import get_logger
from ..skills import get_registry

logger = get_logger(__name__)

router = APIRouter(prefix="/api/skills", tags=["skills"])


# ==================== 数据模型 ====================

class SkillInfo(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    enabled: bool = True
    installed: bool = True
    category: str = "builtin"


class SkillMarketItem(BaseModel):
    id: str
    name: str
    description: str
    version: str
    author: str
    downloads: int = 0
    rating: float = 0.0
    category: str
    installed: bool = False


class SkillInstallRequest(BaseModel):
    skill_id: str
    version: Optional[str] = None


# ==================== 内置技能数据 ====================

BUILTIN_SKILLS = {
    "memory": {
        "id": "memory",
        "name": "记忆管理",
        "description": "管理短期记忆、长期记忆和工作记忆",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "core",
        "downloads": 1000,
        "rating": 4.9
    },
    "shell": {
        "id": "shell",
        "name": "Shell 命令",
        "description": "安全地执行系统命令",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "system",
        "downloads": 950,
        "rating": 4.8
    },
    "search": {
        "id": "search",
        "name": "网络搜索",
        "description": "搜索网络信息和文档",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "tools",
        "downloads": 900,
        "rating": 4.7
    },
    "http": {
        "id": "http",
        "name": "HTTP 请求",
        "description": "发送 HTTP/HTTPS 请求",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "tools",
        "downloads": 850,
        "rating": 4.6
    },
    "code_analysis": {
        "id": "code_analysis",
        "name": "代码分析",
        "description": "分析代码结构和质量",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "dev",
        "downloads": 800,
        "rating": 4.8
    },
    "database": {
        "id": "database",
        "name": "数据库",
        "description": "数据库查询和管理",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "dev",
        "downloads": 750,
        "rating": 4.5
    },
    "formatter": {
        "id": "formatter",
        "name": "格式化",
        "description": "代码和文本格式化",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "dev",
        "downloads": 700,
        "rating": 4.4
    },
    "docker": {
        "id": "docker",
        "name": "Docker",
        "description": "Docker 容器操作",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "devops",
        "downloads": 650,
        "rating": 4.6
    },
    "chat": {
        "id": "chat",
        "name": "自然对话",
        "description": "自然语言对话技能",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "ai",
        "downloads": 1000,
        "rating": 4.9
    },
    "llm": {
        "id": "llm",
        "name": "大模型",
        "description": "阿里云百炼大模型接入",
        "version": "1.0.0",
        "author": "YM-CODE Team",
        "category": "ai",
        "downloads": 980,
        "rating": 4.9
    }
}


# ==================== API 端点 ====================

@router.get("/list")
async def list_skills():
    """获取已安装技能列表"""
    registry = get_registry()
    skills = registry.list_skills()
    
    result = []
    for skill in skills:
        market_info = BUILTIN_SKILLS.get(skill['name'], {})
        result.append({
            **skill,
            **market_info,
            "installed": True
        })
    
    return {
        "skills": result,
        "total": len(result)
    }


@router.get("/market")
async def get_skill_market(category: str = None):
    """获取技能市场列表"""
    skills = list(BUILTIN_SKILLS.values())
    
    if category:
        skills = [s for s in skills if s.get('category') == category]
    
    # 检查安装状态
    registry = get_registry()
    installed_skills = [s['name'] for s in registry.list_skills()]
    
    for skill in skills:
        skill['installed'] = skill['id'] in installed_skills
    
    return {
        "skills": skills,
        "total": len(skills),
        "categories": ["core", "system", "tools", "dev", "devops", "ai"]
    }


@router.get("/detail/{skill_id}")
async def get_skill_detail(skill_id: str):
    """获取技能详情"""
    if skill_id not in BUILTIN_SKILLS:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    skill = BUILTIN_SKILLS[skill_id]
    
    # 检查安装状态
    registry = get_registry()
    installed_skills = [s['name'] for s in registry.list_skills()]
    
    return {
        **skill,
        "installed": skill_id in installed_skills,
        "usage": get_skill_usage(skill_id)
    }


@router.post("/install")
async def install_skill(request: SkillInstallRequest):
    """安装技能"""
    if request.skill_id not in BUILTIN_SKILLS:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    # 检查是否已安装
    registry = get_registry()
    skill = registry.get(request.skill_id)
    
    if skill:
        return {
            "success": False,
            "message": "技能已安装"
        }
    
    # 内置技能默认已安装，这里模拟安装过程
    return {
        "success": True,
        "message": f"技能 {request.skill_id} 安装成功（模拟）",
        "skill": BUILTIN_SKILLS[request.skill_id]
    }


@router.post("/uninstall")
async def uninstall_skill(skill_id: str):
    """卸载技能"""
    if skill_id not in BUILTIN_SKILLS:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    # 核心技能不允许卸载
    if skill_id in ['memory', 'llm', 'chat']:
        raise HTTPException(status_code=400, detail="核心技能不能卸载")
    
    # 模拟卸载
    return {
        "success": True,
        "message": f"技能 {skill_id} 已卸载（模拟）"
    }


@router.post("/enable")
async def enable_skill(skill_id: str):
    """启用技能"""
    registry = get_registry()
    skill = registry.get(skill_id)
    
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    # 模拟启用
    return {
        "success": True,
        "message": f"技能 {skill_id} 已启用"
    }


@router.post("/disable")
async def disable_skill(skill_id: str):
    """禁用技能"""
    registry = get_registry()
    skill = registry.get(skill_id)
    
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    # 核心技能不允许禁用
    if skill_id in ['memory', 'llm']:
        raise HTTPException(status_code=400, detail="核心技能不能禁用")
    
    # 模拟禁用
    return {
        "success": True,
        "message": f"技能 {skill_id} 已禁用"
    }


def get_skill_usage(skill_id: str) -> str:
    """获取技能使用说明"""
    usage_examples = {
        "memory": "保存记忆：action=save, content=内容\n加载记忆：action=load, session_id=会话 ID",
        "shell": "执行命令：command=ls, args=['-la']",
        "search": "搜索：query=关键词",
        "http": "GET 请求：method=GET, url=https://api.example.com",
        "code_analysis": "分析代码：path=文件路径",
        "database": "查询：sql=SELECT * FROM table",
        "formatter": "格式化：code=代码内容, lang=python",
        "docker": "容器操作：action=list",
        "chat": "对话：message=你好",
        "llm": "LLM 调用：message=问题，use_tools=True"
    }
    
    return usage_examples.get(skill_id, "暂无使用说明")


@router.get("/categories")
async def list_categories():
    """获取技能分类"""
    return {
        "categories": [
            {"id": "core", "name": "核心技能", "icon": "⭐"},
            {"id": "system", "name": "系统工具", "icon": "🔧"},
            {"id": "tools", "name": "实用工具", "icon": "🛠️"},
            {"id": "dev", "name": "开发工具", "icon": "💻"},
            {"id": "devops", "name": "DevOps", "icon": "🐳"},
            {"id": "ai", "name": "AI 技能", "icon": "🤖"}
        ]
    }
