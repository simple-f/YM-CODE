#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Dashboard API - 最小化版本
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Any, Dict

app = FastAPI(title="YM-CODE Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"
TEAM_FILE = CONFIG_DIR / "team.json"


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回 Dashboard 页面"""
    # HTML 文件在共享目录的 web 文件夹
    html_path = Path(__file__).parent.parent.parent / "web" / "agents.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return {"error": "Dashboard page not found"}


@app.get("/agents.html", response_class=HTMLResponse)
async def agents_page():
    """Agent 管理页面"""
    html_path = Path(__file__).parent.parent.parent / "web" / "agents.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/api/team/list")
async def get_team():
    """获取 Agent 团队配置"""
    if not TEAM_FILE.exists():
        raise HTTPException(status_code=404, detail="Team config not found")
    
    try:
        with open(TEAM_FILE, 'r', encoding='utf-8') as f:
            team = json.load(f)
        return {"team": team}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON: {str(e)}")


@app.get("/api/workspaces/list")
async def get_workspaces():
    """获取工作空间列表"""
    workspace_file = CONFIG_DIR / "workspaces.json"
    if not workspace_file.exists():
        return {"workspaces": []}
    
    try:
        with open(workspace_file, 'r', encoding='utf-8') as f:
            workspaces = json.load(f)
        return {"workspaces": workspaces}
    except json.JSONDecodeError:
        return {"workspaces": []}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
