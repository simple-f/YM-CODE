# YM-CODE 平台型架构重构

**重构时间：** 2026-03-16  
**版本：** v2.0.0

---

## 🎯 重构目标

将 YM-CODE 从脚本仓库重构为**平台型 AI Agent 系统**

---

## 📁 新架构

### 目录结构

```
ym-code/
├── backend/                      # 后端核心
│   ├── api/                      # API 层
│   │   ├── task_api.py           # 任务 API
│   │   ├── plugin_api.py         # 插件 API
│   │   └── agent_api.py          # Agent API
│   │
│   ├── core/                     # 核心引擎
│   │   └── engine.py             # 执行引擎
│   │
│   ├── agents/                   # Agent 系统
│   │   ├── base_agent.py         # Agent 基类
│   │   └── ...                   # 各种 Agent
│   │
│   ├── plugins/                  # 插件系统
│   │   ├── base_plugin.py        # 插件基类
│   │   └── ...                   # 各种插件
│   │
│   ├── scheduler/                # 任务调度
│   │   └── ...                   # 调度器
│   │
│   ├── services/                 # 服务层
│   │   └── ...                   # 业务服务
│   │
│   └── models/                   # 数据模型
│       ├── task.py               # 任务模型
│       └── ...                   # 其他模型
│
├── worker/                       # 执行节点
│   └── worker.py                 # Worker 进程
│
├── plugins/                      # 外部插件目录
│   └── custom_plugin/            # 用户自定义插件
│
├── configs/                      # 配置文件
│   └── config.yaml               # 主配置
│
├── frontend/                     # 前端界面
│   ├── dashboard/                # 管理面板
│   └── chat/                     # 聊天界面
│
├── scripts/                      # 工具脚本
├── tests/                        # 测试
└── docs/                         # 文档
```

---

## 🏗️ 核心模块

### 1. API 层

**功能：**
- 任务管理 API
- 插件管理 API
- Agent 管理 API
- 系统管理 API

**技术：** FastAPI

**示例：**
```python
POST /api/tasks      # 创建任务
GET  /api/tasks      # 查询任务
GET  /api/tasks/{id} # 查询任务详情
```

---

### 2. Core 核心引擎

**功能：**
- 任务调度
- Agent 选择
- 插件调用
- 执行流程控制

**核心类：**
```python
class ExecutionEngine:
    async def execute(task: Task) -> TaskResult
    async def plan_task(task: Task) -> List[Step]
```

---

### 3. Agent 系统

**功能：**
- 任务执行
- 智能决策
- 工具调用

**基类：**
```python
class BaseAgent(ABC):
    @abstractmethod
    async def execute(task: Task) -> TaskResult
```

---

### 4. 插件系统

**功能：**
- 工具扩展
- 功能增强
- 第三方集成

**基类：**
```python
class BasePlugin(ABC):
    @abstractmethod
    async def run(params: Dict) -> Any
```

---

### 5. 任务调度

**功能：**
- 任务队列
- 定时任务
- 优先级调度

**技术：** Celery / Redis Queue

---

### 6. Worker 节点

**功能：**
- 任务执行
- 并发处理
- 资源管理

---

## 🔄 执行流程

```
用户请求
   ↓
API 创建任务
   ↓
TaskManager
   ↓
Scheduler（队列）
   ↓
Worker（拉取）
   ↓
Agent（执行）
   ↓
Plugin（工具）
   ↓
结果存储
   ↓
返回用户
```

---

## 📊 数据模型

### Task 任务

```python
class Task:
    id: str
    name: str
    status: TaskStatus  # pending, running, completed, failed
    agent: str
    plugins: List[str]
    params: Dict
    result: TaskResult
```

### Plugin 插件

```python
class Plugin:
    name: str
    version: str
    enabled: bool
    config: Dict
```

---

## 🎯 重构进度

### 已完成

- ✅ 目录结构创建
- ✅ API 层框架（task_api, plugin_api）
- ✅ Core 引擎框架（engine.py）
- ✅ Agent 基类（base_agent.py）
- ✅ Plugin 基类（base_plugin.py）
- ✅ Task 模型（task.py）
- ✅ Worker 框架（worker.py）
- ✅ 配置文件（config.yaml）

### 待完成

- ⏳ 完整 API 实现
- ⏳ Agent 实现
- ⏳ Plugin 实现
- ⏳ 调度器实现
- ⏳ 数据库集成
- ⏳ 前端界面

---

## 🚀 下一步

1. 实现完整的 API 接口
2. 实现 Agent 系统
3. 实现插件系统
4. 实现任务调度
5. 集成数据库
6. 开发前端界面

---

**重构开始时间：** 2026-03-16  
**目标版本：** v2.0.0  
**状态：** 🚀 重构中
