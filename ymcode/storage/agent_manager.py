#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 Agent 管理 - 工作空间和 Agent 配置
"""

import aiosqlite
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Agent 配置"""
    id: str
    name: str
    workspace_id: str
    system_prompt: str = "你是一个友好的 AI 助手。"
    model: str = "qwen3.5-plus"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2000
    personality: str = "friendly"  # friendly, professional, humorous, strict
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Workspace:
    """工作空间"""
    id: str
    name: str
    description: str = ""
    owner: str = "default"
    created_at: str = ""
    updated_at: str = ""


class AgentManager:
    """Agent 管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = Path.home() / ".ymcode"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "agents.db")
        
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
        logger.info(f"AgentManager 初始化：{db_path}")
    
    async def connect(self):
        """连接数据库"""
        self.db = await aiosqlite.connect(self.db_path)
        await self._init_tables()
        logger.info("AgentManager 数据库连接成功")
    
    async def close(self):
        """关闭数据库"""
        if self.db:
            await self.db.close()
            logger.info("AgentManager 数据库连接已关闭")
    
    async def _init_tables(self):
        """初始化数据表"""
        # 工作空间表
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                owner TEXT DEFAULT 'default',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Agent 表
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                workspace_id TEXT NOT NULL,
                system_prompt TEXT,
                model TEXT DEFAULT 'qwen3.5-plus',
                api_key TEXT,
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2000,
                personality TEXT DEFAULT 'friendly',
                enabled INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_agents_workspace 
            ON agents(workspace_id)
        """)
        
        await self.db.commit()
        logger.info("AgentManager 数据表初始化完成")
    
    # ========== Workspace 操作 ==========
    
    async def create_workspace(self, name: str, description: str = "", owner: str = "default") -> Workspace:
        """创建工作空间"""
        workspace_id = f"ws_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        workspace = Workspace(
            id=workspace_id,
            name=name,
            description=description,
            owner=owner,
            created_at=now,
            updated_at=now
        )
        
        await self.db.execute(
            """INSERT INTO workspaces (id, name, description, owner, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (workspace_id, name, description, owner, now, now)
        )
        await self.db.commit()
        
        logger.info(f"创建工作空间：{name} ({workspace_id})")
        return workspace
    
    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """获取工作空间"""
        cursor = await self.db.execute(
            "SELECT * FROM workspaces WHERE id = ?",
            (workspace_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        return Workspace(*row)
    
    async def list_workspaces(self, owner: str = "default") -> List[Workspace]:
        """列出工作空间"""
        cursor = await self.db.execute(
            "SELECT * FROM workspaces WHERE owner = ? ORDER BY created_at DESC",
            (owner,)
        )
        rows = await cursor.fetchall()
        await cursor.close()
        
        return [Workspace(*row) for row in rows]
    
    async def update_workspace(self, workspace_id: str, name: str = None, description: str = None):
        """更新工作空间"""
        updates = []
        values = []
        
        if name:
            updates.append("name = ?")
            values.append(name)
        if description:
            updates.append("description = ?")
            values.append(description)
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(workspace_id)
        
        await self.db.execute(
            f"UPDATE workspaces SET {', '.join(updates)} WHERE id = ?",
            values
        )
        await self.db.commit()
    
    async def delete_workspace(self, workspace_id: str):
        """删除工作空间"""
        await self.db.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
        await self.db.commit()
    
    # ========== Agent 操作 ==========
    
    async def create_agent(self, workspace_id: str, name: str, config: Dict = None) -> Agent:
        """创建 Agent"""
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        config = config or {}
        agent = Agent(
            id=agent_id,
            name=name,
            workspace_id=workspace_id,
            system_prompt=config.get("system_prompt", "你是一个友好的 AI 助手。"),
            model=config.get("model", "qwen3.5-plus"),
            api_key=config.get("api_key", ""),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            personality=config.get("personality", "friendly"),
            enabled=config.get("enabled", True),
            created_at=now,
            updated_at=now
        )
        
        await self.db.execute(
            """INSERT INTO agents (id, name, workspace_id, system_prompt, model, api_key, 
               temperature, max_tokens, personality, enabled, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (agent_id, name, workspace_id, agent.system_prompt, agent.model, agent.api_key,
             agent.temperature, agent.max_tokens, agent.personality, 1 if agent.enabled else 0,
             now, now)
        )
        await self.db.commit()
        
        logger.info(f"创建 Agent: {name} ({agent_id}) in {workspace_id}")
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        cursor = await self.db.execute(
            "SELECT * FROM agents WHERE id = ?",
            (agent_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        # 转换 enabled 字段
        agent_dict = dict(zip([col[0] for col in cursor.description], row))
        agent_dict['enabled'] = bool(agent_dict['enabled'])
        
        return Agent(**agent_dict)
    
    async def list_agents(self, workspace_id: str = None) -> List[Agent]:
        """列出 Agent"""
        if workspace_id:
            cursor = await self.db.execute(
                "SELECT * FROM agents WHERE workspace_id = ? ORDER BY created_at DESC",
                (workspace_id,)
            )
        else:
            cursor = await self.db.execute("SELECT * FROM agents ORDER BY created_at DESC")
        
        rows = await cursor.fetchall()
        await cursor.close()
        
        agents = []
        for row in rows:
            agent_dict = dict(zip([col[0] for col in cursor.description], row))
            agent_dict['enabled'] = bool(agent_dict['enabled'])
            agents.append(Agent(**agent_dict))
        
        return agents
    
    async def update_agent(self, agent_id: str, config: Dict):
        """更新 Agent 配置"""
        updates = []
        values = []
        
        allowed_fields = ['name', 'system_prompt', 'model', 'api_key', 'temperature', 
                         'max_tokens', 'personality', 'enabled']
        
        for field in allowed_fields:
            if field in config:
                updates.append(f"{field} = ?")
                value = config[field]
                if field == 'enabled':
                    value = 1 if value else 0
                values.append(value)
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(agent_id)
        
        await self.db.execute(
            f"UPDATE agents SET {', '.join(updates)} WHERE id = ?",
            values
        )
        await self.db.commit()
        
        logger.info(f"更新 Agent: {agent_id}")
    
    async def delete_agent(self, agent_id: str):
        """删除 Agent"""
        await self.db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        await self.db.commit()
    
    async def get_workspace_agents_count(self, workspace_id: str) -> int:
        """获取工作空间的 Agent 数量"""
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM agents WHERE workspace_id = ?",
            (workspace_id,)
        )
        count = (await cursor.fetchone())[0]
        await cursor.close()
        return count


# 全局管理器实例
_manager: Optional[AgentManager] = None


def get_manager() -> AgentManager:
    """获取全局管理器"""
    global _manager
    if _manager is None:
        _manager = AgentManager()
    return _manager


async def init_manager():
    """初始化管理器"""
    manager = get_manager()
    await manager.connect()
    return manager
