#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 Agent 管理 API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from ..utils.logger import get_logger
from ..storage.agent_manager import get_manager, init_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


# ==================== 数据模型 ====================

class WorkspaceCreate(BaseModel):
    name: str
    description: str = ""


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AgentCreate(BaseModel):
    name: str
    workspace_id: str
    config: Dict = {}


class AgentUpdate(BaseModel):
    config: Dict


# ==================== Workspace API ====================

@router.on_event("startup")
async def startup():
    """初始化 Agent Manager"""
    await init_manager()
    logger.info("Agent Manager 已初始化")


@router.get("/list")
async def list_workspaces():
    """获取工作空间列表"""
    manager = get_manager()
    workspaces = await manager.list_workspaces()
    
    result = []
    for ws in workspaces:
        agent_count = await manager.get_workspace_agents_count(ws.id)
        result.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "agent_count": agent_count,
            "created_at": ws.created_at
        })
    
    return {"workspaces": result, "total": len(result)}


@router.post("/create")
async def create_workspace(data: WorkspaceCreate):
    """创建工作空间"""
    manager = get_manager()
    workspace = await manager.create_workspace(
        name=data.name,
        description=data.description
    )
    
    return {
        "success": True,
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description
        }
    }


@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str):
    """获取工作空间详情"""
    manager = get_manager()
    workspace = await manager.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="工作空间不存在")
    
    agents = await manager.list_agents(workspace_id)
    
    return {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "created_at": workspace.created_at
        },
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "model": a.model,
                "personality": a.personality,
                "enabled": a.enabled
            }
            for a in agents
        ]
    }


@router.post("/{workspace_id}/update")
async def update_workspace(workspace_id: str, data: WorkspaceUpdate):
    """更新工作空间"""
    manager = get_manager()
    await manager.update_workspace(
        workspace_id,
        name=data.name,
        description=data.description
    )
    
    return {"success": True, "message": "工作空间已更新"}


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """删除工作空间"""
    manager = get_manager()
    await manager.delete_workspace(workspace_id)
    
    return {"success": True, "message": "工作空间已删除"}


# ==================== Agent API ====================

@router.get("/{workspace_id}/agents")
async def list_agents(workspace_id: str):
    """获取工作空间的所有 Agent"""
    manager = get_manager()
    agents = await manager.list_agents(workspace_id)
    
    return {
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "model": a.model,
                "system_prompt": a.system_prompt,
                "personality": a.personality,
                "enabled": a.enabled,
                "created_at": a.created_at
            }
            for a in agents
        ],
        "total": len(agents)
    }


@router.post("/agents/create")
async def create_agent(data: AgentCreate):
    """创建 Agent"""
    manager = get_manager()
    
    # 验证工作空间
    workspace = await manager.get_workspace(data.workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="工作空间不存在")
    
    agent = await manager.create_agent(
        workspace_id=data.workspace_id,
        name=data.name,
        config=data.config
    )
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "workspace_id": agent.workspace_id
        }
    }


@router.post("/agents/{agent_id}/update")
async def update_agent(agent_id: str, data: AgentUpdate):
    """更新 Agent 配置"""
    manager = get_manager()
    await manager.update_agent(agent_id, data.config)
    
    return {"success": True, "message": "Agent 配置已更新"}


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """删除 Agent"""
    manager = get_manager()
    await manager.delete_agent(agent_id)
    
    return {"success": True, "message": "Agent 已删除"}


@router.get("/agents/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """获取 Agent 完整配置"""
    manager = get_manager()
    agent = await manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    return {
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "workspace_id": agent.workspace_id,
            "system_prompt": agent.system_prompt,
            "model": agent.model,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
            "personality": agent.personality,
            "enabled": agent.enabled
        }
    }


# ==================== 多 Agent 聊天 API ====================

from pydantic import BaseModel
from typing import List

class AgentChatRequest(BaseModel):
    agent_id: str
    message: str
    history: List[dict] = []

class AgentChatResponse(BaseModel):
    message: str
    agent_name: str
    model: str

@router.post("/agents/chat")
async def agent_chat(request: AgentChatRequest):
    """使用指定 Agent 配置进行聊天"""
    import httpx
    import os
    from dotenv import load_dotenv
    
    manager = get_manager()
    agent = await manager.get_agent(request.agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    if not agent.enabled:
        raise HTTPException(status_code=400, detail="Agent 已禁用")
    
    # 加载环境变量获取全局 API Key
    load_dotenv()
    
    # 使用 Agent 的 API Key 或全局 API Key
    api_key = agent.api_key or os.getenv("DASHSCOPE_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="未配置 API Key")
    
    # 构建消息
    messages = [
        {"role": "system", "content": f"{agent.system_prompt}\n\n你是{agent.name}，性格：{agent.personality}。请参与团队讨论。"},
        *request.history,
        {"role": "user", "content": request.message}
    ]
    
    # 调用 LLM API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": agent.model,
        "messages": messages,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "stream": False
    }
    
    # 通义灵码 OpenAI 兼容接口
    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LLM API 调用失败：{response.text[:200]}"
                )
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                raise HTTPException(status_code=500, detail="LLM 返回为空")
            
            return {
                "message": content,
                "agent_name": agent.name,
                "model": agent.model
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"网络请求失败：{str(e)}")
