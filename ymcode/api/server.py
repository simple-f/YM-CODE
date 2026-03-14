#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE API Server - FastAPI 实现
端口：18770 (开发) / 18771 (生产)
"""

import os
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入 YM-CODE 模块
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 配置
PORT = int(os.environ.get("YM_CODE_PORT", 18770))
HOST = os.environ.get("YM_CODE_HOST", "0.0.0.0")
DEBUG = os.environ.get("YM_CODE_DEBUG", "false").lower() == "true"

# 创建 FastAPI 应用
app = FastAPI(
    title="YM-CODE API",
    description="YM-CODE AI Programming Assistant API",
    version="0.1.0"
)

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发
        "http://localhost:3000",  # 生产环境
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:18772",  # 生产 Web
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class ChatRequest(BaseModel):
    message: str
    workspace: Optional[str] = None
    agent: Optional[str] = None
    context: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    message: str
    agent: str
    timestamp: str
    duration_ms: Optional[int] = None
    workspace: Optional[str] = None

class Session(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: Optional[str] = None
    message_count: int

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

# ==================== 全局状态 ====================

# 内存存储（临时，后续替换为数据库）
sessions_store = {
    "session_001": {
        "id": "session_001",
        "title": "第一次对话",
        "created_at": datetime.now().isoformat(),
        "messages": [
            {"role": "user", "content": "你好", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "你好！我是 YM-CODE，你的编程伙伴。", "timestamp": datetime.now().isoformat()}
        ]
    }
}

# ==================== API 路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "YM-CODE API",
        "port": PORT,
        "timestamp": datetime.now().isoformat(),
        "debug": DEBUG
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    聊天接口
    
    接收用户消息，返回 AI 响应
    """
    start_time = time.time()
    
    logger.info(f"收到聊天请求：{request.message[:50]}...")
    
    # TODO: 调用实际 Agent 处理
    # 这里是临时实现，后续会集成 YM-CODE Agent
    
    response_message = generate_response(request.message)
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"聊天响应完成：{duration_ms}ms")
    
    return ChatResponse(
        message=response_message,
        agent="YM-Pro",
        timestamp=datetime.now().isoformat(),
        duration_ms=duration_ms,
        workspace=request.workspace
    )

@app.get("/api/sessions")
async def list_sessions():
    """获取会话列表"""
    sessions_list = [
        Session(
            id=s["id"],
            title=s["title"],
            created_at=s["created_at"],
            message_count=len(s.get("messages", []))
        )
        for s in sessions_store.values()
    ]
    
    return {
        "sessions": sessions_list,
        "total": len(sessions_list)
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions_store[session_id]
    
    return {
        "session": {
            "id": session["id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "message_count": len(session.get("messages", []))
        },
        "messages": session.get("messages", [])
    }

@app.post("/api/sessions")
async def create_session(title: str = "新会话"):
    """创建新会话"""
    import uuid
    
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    sessions_store[session_id] = {
        "id": session_id,
        "title": title,
        "created_at": now,
        "messages": []
    }
    
    return {
        "session": {
            "id": session_id,
            "title": title,
            "created_at": now
        }
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions_store[session_id]
    
    return {"status": "ok", "message": f"Session {session_id} deleted"}

# ==================== 辅助函数 ====================

def generate_response(message: str) -> str:
    """
    生成响应（临时实现）
    
    TODO: 后续集成 YM-CODE Agent
    """
    message_lower = message.lower()
    
    # 简单关键词匹配
    if "你好" in message or "hello" in message:
        return "你好！我是 YM-CODE，你的 AI 编程伙伴。有什么可以帮助你的吗？"
    
    elif "帮助" in message or "help" in message:
        return """我可以帮你：
- 💻 代码编写和审查
- 🐛 调试问题
- 📝 生成测试
- 📚 解释代码
- 🔧 重构优化

请告诉我具体需要什么帮助！"""
    
    elif "代码" in message or "code" in message:
        return "当然！请分享你的代码，我会帮你分析、审查或优化。"
    
    else:
        return f"""收到你的消息："{message}"

这是一个临时响应，后续会集成真实的 YM-CODE Agent。

当前功能：
- ✅ API 接口已就绪
- ✅ 前后端联调中
- ⏳ Agent 集成中"""

# ==================== 主程序 ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting YM-CODE API Server...")
    logger.info(f"   Host: {HOST}")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Debug: {DEBUG}")
    logger.info(f"   CORS: http://localhost:5173, http://localhost:3000")
    
    uvicorn.run(
        "ymcode.api.server:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
