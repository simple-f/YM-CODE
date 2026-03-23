# 已归档代码说明

**归档时间：** 2026-03-17  
**归档原因：** P0-P3 优化完成，v3.0 架构生产就绪

---

## 📦 归档文件清单

| 文件 | 原路径 | 归档原因 | 替代方案 |
|------|--------|----------|----------|
| `engine.py.bak` | `backend/core/engine.py` | TODO 未实现 | `ymcode/core/agent.py` |
| `agent_manager.py.bak` | `backend/agents/agent_manager.py` | select_for_task 未实现 | `ymcode/mcp/host.py` |
| `task_service.py.bak` | `backend/services/task_service.py` | 内存存储，重启丢失 | `storage/database.py` |

---

## 🏗️ 架构演进

### V1.0（已归档）

**问题：**
- ❌ `backend/` 和 `ymcode/` 双后端结构
- ❌ 职责不清，功能重复
- ❌ 配置分散

### V2.0（已优化）

**改进：**
- ✅ 统一为 `ymcode/` 后端
- ✅ 清晰的分层架构
- ✅ 模块化设计

### V3.0（生产就绪）

**特性：**
- ✅ P0-P3 优化完成
- ✅ 线程安全 + 超时控制
- ✅ 数据库持久化 + RAG 知识库
- ✅ 监控告警 + 日志轮转
- ✅ Docker 一键部署

---

## 📋 迁移指南

### 从 V1.0 迁移到 V3.0

**1. ExecutionEngine**
```python
# 旧代码（已归档）
from backend.core.engine import ExecutionEngine
engine = ExecutionEngine()  # TODO 未实现

# 新代码
from ymcode.core.agent import Agent
agent = Agent()  # ✅ 完整实现
```

**2. AgentManager**
```python
# 旧代码（已归档）
from backend.agents.agent_manager import AgentManager
manager = AgentManager()
manager.select_for_task(task)  # TODO 未实现

# 新代码
from ymcode.mcp import CLIHost
host = CLIHost()
await host.initialize()
client = await host._select_client("task_name")  # ✅ 已实现
```

**3. TaskService**
```python
# 旧代码（已归档）
from backend.services.task_service import TaskService
service = TaskService()  # 内存存储

# 新代码
from ymcode.storage.database import DatabaseManager, TaskModel
db = DatabaseManager("sqlite:///ymcode.db")
db.init_db()
session = db.get_session()
task = TaskModel(...)  # ✅ 数据库存储
```

---

## 🎯 建议

**对于新用户：**
- ✅ 直接使用 `ymcode/` 目录
- ✅ 参考 `DEPLOY.md` 部署指南
- ✅ 使用 Docker 一键部署

**对于老用户：**
- 🔄 逐步迁移到 v3.0 架构
- 📋 参考本迁移指南
- ⚠️ 归档代码仅供参考，不再维护

---

_归档时间：2026-03-17_
