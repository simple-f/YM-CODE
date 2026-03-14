# YM-CODE 多 Agent 系统设计

**轻量级多 Agent，独立运行 + OpenClaw 集成！** 🚀

---

## 🎯 设计目标

### 原则

1. **轻量级** - 不依赖复杂基础设施
2. **可独立** - 可以脱离 OpenClaw 运行
3. **可集成** - 可以与 OpenClaw 协作
4. **模块化** - 易于扩展新 Agent

---

## 🏗️ 架构设计

### 方案 1：独立模式（推荐）

```
┌─────────────────────────────────────┐
│         YM-CODE Multi-Agent         │
├─────────────────────────────────────┤
│  Agent Router (本地)                │
├──────────┬──────────┬───────────────┤
│  Builder │ Reviewer │  Specialist   │
│  (ai2)   │  (ai3)   │  (可扩展)     │
└──────────┴──────────┴───────────────┘
        ↓
┌─────────────────────────────────────┐
│      共享记忆 (本地 SQLite)          │
└─────────────────────────────────────┘
```

**特点：**
- ✅ 独立运行，无需 OpenClaw
- ✅ 本地 SQLite 共享记忆
- ✅ 简单高效

---

### 方案 2：混合模式

```
┌─────────────────┐         ┌─────────────────┐
│  YM-CODE        │         │  OpenClaw       │
│  本地 Agent     │←------→│  路由/渠道      │
└─────────────────┘         └─────────────────┘
```

**特点：**
- ✅ 可以与 OpenClaw 协作
- ✅ 保持独立性
- ✅ 灵活部署

---

## 🤖 Agent 角色设计

### 核心 Agent（3 个）

| Agent | 角色 | 职责 | 优先级 |
|-------|------|------|--------|
| **Router** | 路由 | 任务分发/协调 | P0 |
| **Builder** | 构建 | 代码实现/测试 | P0 |
| **Reviewer** | 审查 | 代码审查/质量 | P0 |

### 扩展 Agent（可选）

| Agent | 角色 | 职责 | 优先级 |
|-------|------|------|--------|
| **Specialist** | 专家 | 特定领域支持 | P1 |
| **Tester** | 测试 | 测试执行 | P2 |
| **Documenter** | 文档 | 文档生成 | P2 |

---

## 📦 实现方案

### 阶段 1：基础架构（1 小时）

**目标：** 实现本地多 Agent 基础

#### 1.1 Agent 基类

创建 `ymcode/agents/base.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 基类
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Agent 消息"""
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory = []  # 短期记忆
        self.state = "idle"  # idle, busy, error
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentMessage:
        """处理消息"""
        pass
    
    def add_to_memory(self, message: str):
        """添加到短期记忆"""
        self.memory.append({
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近 100 条
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
    
    def get_memory(self, limit: int = 10) -> list:
        """获取最近记忆"""
        return self.memory[-limit:]
    
    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
```

---

#### 1.2 Agent 路由器

创建 `ymcode/agents/router.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 路由器
"""

import logging
from typing import Dict, List, Optional
from .base import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)


class AgentRouter:
    """Agent 路由器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_memory = []  # 共享记忆
    
    def register_agent(self, name: str, agent: BaseAgent):
        """注册 Agent"""
        self.agents[name] = agent
        logger.info(f"注册 Agent: {name} ({agent.role})")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict]:
        """列出所有 Agent"""
        return [
            {"name": name, "role": agent.role, "state": agent.state}
            for name, agent in self.agents.items()
        ]
    
    async def route(self, message: AgentMessage, target: str = None) -> AgentMessage:
        """路由消息到 Agent"""
        if target:
            # 指定 Agent
            agent = self.get_agent(target)
            if not agent:
                return AgentMessage(
                    sender="router",
                    content=f"Agent 不存在：{target}"
                )
            
            logger.info(f"路由到 {target}")
            return await agent.process(message)
        else:
            # 自动路由（根据内容）
            return await self._auto_route(message)
    
    async def _auto_route(self, message: AgentMessage) -> AgentMessage:
        """自动路由"""
        content = message.content.lower()
        
        # 简单规则路由
        if any(word in content for word in ["创建", "实现", "编写", "build"]):
            target = "builder"
        elif any(word in content for word in ["审查", "review", "检查", "分析"]):
            target = "reviewer"
        else:
            target = "builder"  # 默认
        
        agent = self.get_agent(target)
        if agent:
            logger.info(f"自动路由到 {target}")
            return await agent.process(message)
        else:
            return AgentMessage(
                sender="router",
                content="没有可用的 Agent"
            )
    
    def add_to_shared_memory(self, data: Dict):
        """添加到共享记忆"""
        self.shared_memory.append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近 1000 条
        if len(self.shared_memory) > 1000:
            self.shared_memory = self.shared_memory[-1000:]
    
    def get_shared_memory(self, limit: int = 100) -> list:
        """获取共享记忆"""
        return self.shared_memory[-limit:]
```

---

#### 1.3 Builder Agent

创建 `ymcode/agents/builder.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builder Agent - 负责代码实现
"""

import logging
from .base import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)


class BuilderAgent(BaseAgent):
    """Builder Agent"""
    
    def __init__(self):
        super().__init__("builder", "Builder")
        self.skills = {}  # 技能注册
    
    async def process(self, message: AgentMessage) -> AgentMessage:
        """处理构建请求"""
        self.state = "busy"
        self.add_to_memory(message.content)
        
        try:
            # 分析请求
            content = message.content
            
            # 调用技能执行
            result = await self._execute_task(content)
            
            response = AgentMessage(
                sender=self.name,
                content=result
            )
            
            self.state = "idle"
            return response
            
        except Exception as e:
            logger.error(f"Builder 错误：{e}")
            self.state = "error"
            return AgentMessage(
                sender=self.name,
                content=f"构建失败：{str(e)}"
            )
    
    async def _execute_task(self, task: str) -> str:
        """执行任务"""
        # 这里集成 YM-CODE 的 Skills
        # 示例：
        if "创建文件" in task or "写入" in task:
            return await self._create_file(task)
        elif "运行测试" in task:
            return await self._run_tests(task)
        else:
            return f"任务已接收：{task}"
    
    async def _create_file(self, task: str) -> str:
        """创建文件"""
        # 集成 file_write 工具
        return "✅ 文件已创建"
    
    async def _run_tests(self, task: str) -> str:
        """运行测试"""
        # 集成 test_runner 工具
        return "✅ 测试已通过"
```

---

#### 1.4 Reviewer Agent

创建 `ymcode/agents/reviewer.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reviewer Agent - 负责代码审查
"""

import logging
from .base import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """Reviewer Agent"""
    
    def __init__(self):
        super().__init__("reviewer", "Reviewer")
        self.checklist = [
            "代码规范",
            "测试覆盖",
            "性能优化",
            "安全性",
            "可维护性"
        ]
    
    async def process(self, message: AgentMessage) -> AgentMessage:
        """处理审查请求"""
        self.state = "busy"
        self.add_to_memory(message.content)
        
        try:
            content = message.content
            
            # 执行审查
            review_result = await self._review_code(content)
            
            response = AgentMessage(
                sender=self.name,
                content=review_result
            )
            
            self.state = "idle"
            return response
            
        except Exception as e:
            logger.error(f"Reviewer 错误：{e}")
            self.state = "error"
            return AgentMessage(
                sender=self.name,
                content=f"审查失败：{str(e)}"
            )
    
    async def _review_code(self, content: str) -> str:
        """审查代码"""
        # 集成 code_analysis 技能
        return """
📊 代码审查报告

✅ 代码规范：通过
✅ 测试覆盖：85%
⚠️ 性能优化：建议改进
✅ 安全性：通过
✅ 可维护性：良好

评分：90/100
"""
```

---

### 阶段 2：共享记忆（30 分钟）

**目标：** 实现本地共享记忆

#### 2.1 SQLite 存储

创建 `ymcode/agents/memory_store.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享记忆存储（SQLite）
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MemoryStore:
    """共享记忆存储"""
    
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".ymcode" / "agents" / "memory.db"
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                assigned_to TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_memory(self, agent: str, content: str, metadata: Dict = None):
        """添加记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shared_memory (agent, content, metadata, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            agent,
            content,
            json.dumps(metadata or {}, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_memories(self, limit: int = 100, agent: str = None) -> List[Dict]:
        """获取记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent:
            cursor.execute('''
                SELECT agent, content, metadata, timestamp
                FROM shared_memory
                WHERE agent = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (agent, limit))
        else:
            cursor.execute('''
                SELECT agent, content, metadata, timestamp
                FROM shared_memory
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "agent": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]),
                "timestamp": row[3]
            }
            for row in rows
        ]
    
    def create_task(self, title: str, assigned_to: str = None):
        """创建任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, assigned_to, created_at)
            VALUES (?, ?, ?)
        ''', (title, assigned_to, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_tasks(self, status: str = None) -> List[Dict]:
        """获取任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM tasks WHERE status = ?
            ''', (status,))
        else:
            cursor.execute('SELECT * FROM tasks')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "assigned_to": row[3],
                "created_at": row[4],
                "completed_at": row[5]
            }
            for row in rows
        ]
```

---

### 阶段 3：CLI 集成（30 分钟）

**目标：** 在 YM-CODE CLI 中使用多 Agent

#### 3.1 CLI 命令

创建 `ymcode/cli/agent_commands.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent CLI 命令
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_agent_status(router):
    """显示 Agent 状态"""
    agents = router.list_agents()
    
    table = Table(title="Agent 状态")
    table.add_column("名称", style="cyan")
    table.add_column("角色", style="green")
    table.add_column("状态", style="yellow")
    
    for agent in agents:
        table.add_row(
            agent["name"],
            agent["role"],
            agent["state"]
        )
    
    console.print(table)


def show_shared_memory(memory_store, limit: int = 10):
    """显示共享记忆"""
    memories = memory_store.get_memories(limit=limit)
    
    console.print(Panel.fit("共享记忆", style="bold magenta"))
    
    for memory in memories:
        console.print(f"[cyan]{memory['timestamp']}[/cyan] [{memory['agent']}] {memory['content']}")


def show_tasks(memory_store):
    """显示任务"""
    tasks = memory_store.get_tasks()
    
    table = Table(title="任务列表")
    table.add_column("ID", style="cyan")
    table.add_column("标题", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("分配给", style="blue")
    
    for task in tasks:
        table.add_row(
            str(task["id"]),
            task["title"],
            task["status"],
            task["assigned_to"] or "未分配"
        )
    
    console.print(table)
```

---

## 🎯 使用示例

### 独立模式

```bash
# 启动 YM-CODE Multi-Agent
python -m ymcode --multi-agent

# 查看 Agent 状态
> agent status

# 查看共享记忆
> memory show

# 创建任务
> task create "实现用户认证" --assign builder

# Builder 执行任务
> 实现用户认证功能

# Reviewer 审查
> review 用户认证代码
```

---

### OpenClaw 集成模式

```bash
# OpenClaw 路由到 YM-CODE Agent
@claw 后端机器人 实现登录功能

# YM-CODE Builder 处理
# 结果通过 OpenClaw 返回
```

---

## 📋 实施计划

### P0 - 核心功能（2 小时）

- [ ] Agent 基类 - 30 分钟
- [ ] Agent 路由器 - 30 分钟
- [ ] Builder Agent - 30 分钟
- [ ] Reviewer Agent - 30 分钟

### P1 - 共享记忆（1 小时）

- [ ] SQLite 存储 - 30 分钟
- [ ] CLI 集成 - 30 分钟

### P2 - 扩展功能

- [ ] Specialist Agent - 1 小时
- [ ] 任务系统 - 1 小时
- [ ] Web 界面 - 4 小时

---

## ✅ 总结

### YM-CODE 多 Agent 特点

**✅ 轻量级** - 无需复杂基础设施  
**✅ 可独立** - 脱离 OpenClaw 运行  
**✅ 可集成** - 与 OpenClaw 协作  
**✅ 模块化** - 易于扩展

---

**需要我立即开始实现吗？** 🚀

我可以先实现核心的 Router + Builder + Reviewer！
