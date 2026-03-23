#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作空间 API - 管理工作空间和 Agent 团队
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

WORKSPACE_FILE = Path(__file__).parent.parent.parent / "configs" / "workspaces.json"
TEAM_FILE = Path(__file__).parent.parent.parent / "configs" / "team.json"


def load_workspaces() -> List[Dict[str, Any]]:
    """加载工作空间列表"""
    if not WORKSPACE_FILE.exists():
        # 创建默认工作空间
        default_workspaces = [
            {
                "id": "ws_default",
                "name": "默认工作空间",
                "description": "默认工作空间",
                "created_at": datetime.now().isoformat(),
                "agents": ["ai1", "ai2", "ai3", "ai4", "ai5", "ai6", "ai7"],
                "settings": {
                    "rounds": 5,
                    "auto_dialogue": True
                }
            }
        ]
        save_workspaces(default_workspaces)
        return default_workspaces
    
    with open(WORKSPACE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_workspaces(workspaces: List[Dict[str, Any]]):
    """保存工作空间列表"""
    WORKSPACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACE_FILE, 'w', encoding='utf-8') as f:
        json.dump(workspaces, f, ensure_ascii=False, indent=2)


def load_team() -> Dict[str, Any]:
    """加载 Agent 团队配置"""
    if not TEAM_FILE.exists():
        return {"agents": []}
    
    with open(TEAM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_agent_by_id(agent_id: str) -> Dict[str, Any]:
    """根据 ID 获取 Agent 信息"""
    team = load_team()
    for agent in team.get('agents', []):
        if agent.get('id') == agent_id:
            return agent
    return {}
