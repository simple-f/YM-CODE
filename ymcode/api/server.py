#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE API Server - FastAPI 实现
端口：18770 (开发) / 18771 (生产)
"""

import os
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 导入 YM-CODE 模块
from ..utils.logger import get_logger
from ..skills import get_registry as get_skills_registry
from ..skills.llm import LLMSkill
from ..storage import get_store, init_store

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
    session_id: Optional[str] = None  # 会话 ID
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

# Session 管理器 - 为每个用户维护独立的 LLM 实例和对话历史
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.llm_instances: Dict[str, LLMSkill] = {}
        self.skills_registry = None
    
    def set_skills_registry(self, registry):
        self.skills_registry = registry
    
    async def get_or_create_session(self, session_id: str) -> str:
        """获取或创建会话"""
        if session_id not in self.sessions:
            now = datetime.now().isoformat()
            
            # 尝试从数据库加载
            store = get_store()
            session_data = None
            messages = []
            
            if store and store.db:
                session_data = await store.get_session(session_id)
                if session_data:
                    messages = await store.get_messages(session_id)
                    logger.info(f"从数据库加载 Session: {session_id} ({len(messages)} 条消息)")
            
            # 创建或恢复 Session
            self.sessions[session_id] = {
                "id": session_id,
                "title": session_data["title"] if session_data else f"会话 {len(self.sessions) + 1}",
                "created_at": session_data["created_at"] if session_data else now,
                "updated_at": session_data["updated_at"] if session_data else now,
                "messages": messages,
                "from_db": bool(session_data)
            }
            
            # 为这个 session 创建独立的 LLM 实例
            if self.skills_registry:
                llm = self.skills_registry.get('llm')
                if llm:
                    # 克隆 LLM 实例（独立的对话历史）
                    from ..skills.llm import LLMSkill
                    new_llm = LLMSkill()
                    new_llm.api_key = llm.api_key
                    new_llm.base_url = llm.base_url
                    new_llm.model = llm.model
                    new_llm.use_openai_format = llm.use_openai_format
                    new_llm.set_available_tools(llm.available_tools.copy())
                    new_llm.set_skills_registry(self.skills_registry)
                    
                    # 恢复对话历史
                    for msg in messages:
                        new_llm.conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    self.llm_instances[session_id] = new_llm
                    logger.info(f"为 session {session_id} 创建独立 LLM 实例")
            
            # 保存到数据库
            if store and store.db:
                await store.save_session(session_id, self.sessions[session_id]["title"])
        
        return session_id
    
    async def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        if session_id in self.sessions:
            timestamp = datetime.now().isoformat()
            
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": timestamp
            })
            self.sessions[session_id]["updated_at"] = timestamp
            
            # 保存到数据库
            store = get_store()
            if store and store.db:
                await store.save_message(session_id, role, content, timestamp)
            
            # 同步到 LLM 的对话历史
            llm = self.llm_instances.get(session_id)
            if llm:
                # 将消息添加到 LLM 的 conversation_history
                llm.conversation_history.append({"role": role, "content": content})
                # 限制历史长度
                if len(llm.conversation_history) > llm.max_history * 2:
                    llm.conversation_history = llm.conversation_history[-llm.max_history * 2:]
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[dict]:
        """列出所有会话"""
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "message_count": len(s["messages"])
            }
            for s in self.sessions.values()
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.llm_instances:
                del self.llm_instances[session_id]
            return True
        return False
    
    def get_llm(self, session_id: str) -> Optional[LLMSkill]:
        """获取 session 对应的 LLM 实例"""
        return self.llm_instances.get(session_id)

# 全局 Session 管理器
session_manager = SessionManager()

# ==================== API 路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "YM-CODE API",
        "port": PORT,
        "timestamp": datetime.now().isoformat(),
        "debug": DEBUG,
        "web_url": f"http://localhost:{PORT}",
        "skills_count": len(skills_registry.list_skills()) if skills_registry else 0
    }

# 全局技能注册表
skills_registry = None

@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global skills_registry, session_manager
    
    # 初始化存储
    await init_store()
    logger.info("存储系统已初始化")
    
    skills_registry = get_skills_registry()
    logger.info(f"技能注册表初始化完成，共 {len(skills_registry.list_skills())} 个技能")
    
    # 初始化 LLM 技能的工具
    llm_skill = skills_registry.get('llm')
    if llm_skill:
        # 构建工具定义
        from ..cli.app import YMCodeApp
        app = YMCodeApp()
        app.skills_registry = skills_registry
        tools = app._build_llm_tools()
        llm_skill.set_available_tools(tools)
        llm_skill.set_skills_registry(skills_registry)
        logger.info(f"LLM 工具已设置：{len(tools)} 个")
    
    # 初始化 Session Manager
    session_manager.set_skills_registry(skills_registry)
    logger.info("Session Manager 已初始化")
    
    # 统计信息
    store = get_store()
    if store and store.db:
        stats = await store.get_stats()
        logger.info(f"数据库统计：{stats['total_sessions']} 个会话，{stats['total_messages']} 条消息")

@app.post("/api/chat")
async def chat(request: ChatRequest, user_agent: Optional[str] = Header(None)):
    """
    聊天接口
    
    接收用户消息，返回 AI 响应
    支持 Session 级别的上下文记忆
    """
    start_time = time.time()
    
    # 生成或使用现有 Session ID
    session_id = request.session_id
    if not session_id:
        # 尝试从 User-Agent 或其他标识生成
        client_id = user_agent or str(uuid.uuid4())[:8]
        session_id = f"session_{client_id}"
    
    # 获取或创建 Session
    session_id = await session_manager.get_or_create_session(session_id)
    
    # 添加用户消息到历史
    await session_manager.add_message(session_id, "user", request.message)
    
    logger.info(f"收到聊天请求 [Session: {session_id}]: {request.message[:50]}...")
    
    try:
        # 获取这个 Session 的 LLM 实例（有独立的对话历史）
        llm = session_manager.get_llm(session_id)
        
        if llm and llm.api_key:
            # 使用带上下文的 LLM
            result = await llm.execute({
                'message': request.message,
                'use_tools': True
            })
            
            if result.get('success'):
                response_message = result.get('response', '')
                
                # 添加 AI 响应到历史
                await session_manager.add_message(session_id, "assistant", response_message)
                
                # 更新 Session 标题（如果是第一条消息）
                session = session_manager.get_session(session_id)
                if session and len(session["messages"]) == 2:
                    # 用用户的第一句话作为标题
                    session["title"] = request.message[:30] + "..." if len(request.message) > 30 else request.message
            else:
                response_message = f"LLM 错误：{result.get('error', '未知错误')}"
        else:
            # 降级到简单响应
            response_message = generate_response(request.message)
            session_manager.add_message(session_id, "assistant", response_message)
        
    except Exception as e:
        logger.error(f"聊天处理失败：{e}")
        response_message = f"处理失败：{str(e)}"
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"聊天响应完成 [Session: {session_id}]: {duration_ms}ms")
    
    return ChatResponse(
        message=response_message,
        agent="YM-CODE",
        timestamp=datetime.now().isoformat(),
        duration_ms=duration_ms,
        workspace=request.workspace
    )

@app.get("/api/sessions")
async def list_sessions():
    """获取会话列表"""
    # 优先从数据库获取
    store = get_store()
    if store and store.db:
        sessions_list = await store.list_sessions()
    else:
        sessions_list = session_manager.list_sessions()
    
    return {
        "sessions": sessions_list,
        "total": len(sessions_list)
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session": {
            "id": session["id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "message_count": len(session.get("messages", []))
        },
        "messages": session.get("messages", [])
    }

@app.post("/api/sessions")
async def create_session(title: str = "新会话"):
    """创建新会话"""
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    session_manager.get_or_create_session(session_id)
    
    # 更新标题
    session = session_manager.get_session(session_id)
    if session:
        session["title"] = title
    
    return {
        "session": {
            "id": session_id,
            "title": title,
            "created_at": session["created_at"]
        }
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "ok", "message": f"Session {session_id} deleted"}

# ==================== Web 界面 ====================

# 挂载静态文件目录
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# 注册文件 API 路由
from .files import router as files_router
app.include_router(files_router)

# 注册终端 API 路由
from .terminal import router as terminal_router
app.include_router(terminal_router)

# 注册技能市场 API 路由
from .skills_market import router as skills_market_router
app.include_router(skills_market_router)

# 注册任务管理 API 路由
from .tasks import router as tasks_router
app.include_router(tasks_router)

# 注册多 Agent 管理 API 路由
from .workspaces import router as workspaces_router
app.include_router(workspaces_router)

# 注册设置 API 路由
from .settings import router as settings_router
app.include_router(settings_router)

@app.get("/")
async def serve_web():
    """提供 Web 界面"""
    web_file = web_dir / "index.html"
    if web_file.exists():
        return FileResponse(str(web_file))
    return {"message": "Web interface not found", "web_dir": str(web_dir)}

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
    logger.info(f"   Web UI: http://localhost:{PORT}")
    logger.info(f"   API Docs: http://localhost:{PORT}/docs")
    logger.info(f"   CORS: http://localhost:5173, http://localhost:3000")
    
    uvicorn.run(
        "ymcode.api.server:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
