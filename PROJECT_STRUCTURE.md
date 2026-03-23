# YM-CODE 项目结构

**整理时间：** 2026-03-19  
**版本：** v0.7.0

---

## 📁 目录结构

```
YM-CODE/
├── ymcode/                 # 核心 Python 包
│   ├── core/              # 核心引擎（Agent、LLM）
│   ├── cli/               # 命令行界面
│   ├── web/               # Web Dashboard API
│   ├── workflow/          # 工作流引擎（新增）
│   │   ├── state_tracker.py    # 状态追踪
│   │   ├── cascade_cancel.py   # 级联取消
│   │   ├── scheduler.py        # 任务调度
│   │   └── a2a_coordinator.py  # A2A 协调
│   ├── skills/            # 技能系统
│   ├── tools/             # 工具集
│   ├── mcp/               # MCP 协议
│   ├── knowledge/         # 知识库（RAG）
│   ├── queue/             # 任务队列
│   ├── metrics/           # 指标监控
│   ├── events/            # 事件总线
│   ├── storage/           # 数据库持久化
│   └── utils/             # 工具函数
│
├── web/                    # Web 前端（旧版主界面）
│   ├── index.html         # 主界面（聊天、文件、终端等）
│   ├── agents.html        # Agent 管理
│   ├── agent-config.html  # Agent 配置
│   └── multi-agent.html   # 多 Agent 协作
│
├── docs/                   # 文档
├── tests/                  # 测试
├── scripts/                # 脚本工具
├── reports/                # 报告
├── configs/                # 配置文件
├── extensions/             # 扩展
├── plugins/                # 插件
├── todo/                   # 待办事项
├── vscode-extension/       # VSCode 插件
├── deprecated/             # 已弃用代码
│
├── .env                    # 环境变量（API Key 等）
├── config.json             # 配置文件
├── start_dashboard.py      # Dashboard 启动脚本
└── PROJECT_STRUCTURE.md    # 本文档
```

---

## 🗑️ 已清理的冗余目录

| 目录 | 操作 | 说明 |
|------|------|------|
| `ym-code/` | ❌ 删除 | 已合并到 `ymcode/` |
| `backend/` | ❌ 删除 | 已整合到 `ymcode/` |
| `frontend/` | ❌ 删除 | 已整合到 `web/` |
| `worker/` | ❌ 删除 | 已整合到 `ymcode/` |

---

## 📝 核心模块说明

### ymcode/ (核心包)

| 模块 | 说明 |
|------|------|
| `core/` | Agent、LLM 核心引擎 |
| `cli/` | 命令行界面 |
| `web/` | Web Dashboard API |
| `workflow/` | 工作流引擎（状态追踪、级联取消、调度、A2A） |
| `skills/` | 技能系统 |
| `tools/` | 工具集（文件、Shell、Git 等） |
| `mcp/` | MCP 协议（Model Context Protocol） |
| `knowledge/` | 知识库（RAG 检索增强生成） |
| `queue/` | 任务队列管理 |
| `metrics/` | 指标收集与监控 |
| `events/` | 事件总线 |
| `storage/` | 数据库持久化（SQLAlchemy） |
| `utils/` | 工具函数（日志、加密等） |

### web/ (前端)

| 文件 | 说明 |
|------|------|
| `index.html` | 旧版主界面（聊天、文件浏览器、Web 终端、任务管理） |
| `agents.html` | Agent 管理页面 |
| `agent-config.html` | Agent 配置页面 |
| `multi-agent.html` | 多 Agent 协作页面 |

---

## 🔧 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量（API Key、数据库 URL 等） |
| `config.json` | 应用配置（模型、功能开关等） |

---

## 🚀 启动方式

```bash
# 启动 Dashboard API
python start_dashboard.py

# 访问
# 旧版主界面：http://localhost:8080/web/index.html
# Dashboard API: http://localhost:8080/docs
```

---

## 📋 清理记录

**2026-03-19:**
- ✅ 合并 `ym-code/` 到 `ymcode/`
- ✅ 删除 `backend/`
- ✅ 删除 `frontend/`
- ✅ 删除 `worker/`
- ✅ 删除 `web/chat.html`（重复）
- ✅ 删除 `frontend/dashboard/`（重复）

---

_最后更新：2026-03-19_
