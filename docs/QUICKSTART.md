# YM-CODE 快速开始指南

**更新时间：** 2026-03-19

---

## 🚀 访问地址

| 功能 | URL | 说明 |
|------|-----|------|
| **主界面** | http://localhost:8080/web/index.html | 聊天、文件、终端 |
| **Agent 配置** | http://localhost:8080/web/agent-config.html | 配置 Agent 团队 |
| **多 Agent 协作** | http://localhost:8080/web/multi-agent.html | 多 Agent 对话 |
| **Dashboard API** | http://localhost:8080/docs | API 文档 |

---

## 📋 快速配置

### 1. 检查 API Key

确保 `.env` 文件已配置：

```bash
OPENAI_API_KEY=sk-sp-90fc02607ed448be9d251333e9524876
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 2. 启动服务

```bash
cd C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE
python start_dashboard.py
```

### 3. 测试聊天

访问 http://localhost:8080/web/index.html，输入消息测试。

---

## 🤖 多 Agent 使用

### 方法 1：使用配置文件

1. 配置文件已在 `configs/team.json`
2. 包含 7 个预配置 Agent
3. 访问多 Agent 协作页面即可使用

### 方法 2：手动选择

1. 访问 http://localhost:8080/web/agent-config.html
2. 点击 Agent 卡片选择
3. 保存工作区配置

---

## 📁 目录结构

```
YM-CODE/
├── ymcode/              # 核心 Python 包
│   ├── core/           # Agent、LLM
│   ├── web/            # Dashboard API
│   ├── workflow/       # 工作流引擎
│   └── ...
├── web/                 # Web 前端
│   ├── index.html      # 主界面
│   ├── multi-agent.html # 多 Agent
│   └── ...
├── configs/             # 配置文件
│   ├── team.json       # Agent 团队配置 ✅
│   └── workspaces.json # 工作空间（自动生成）
└── docs/                # 文档
```

---

## ✅ 已配置 Agent

| 名称 | 模型 | 角色 |
|------|------|------|
| 架构师 | qwen3.5-plus | system |
| 后端开发 | qwen3-coder-plus | developer |
| 前端开发 | qwen3-coder-next | developer |
| 全栈开发 | glm-5 | developer |
| 测试工程师 | kimi-k2.5 | reviewer |
| 技术顾问 | qwen3-max-2026-01-23 | advisor |
| 产品顾问 | MiniMax-M2.5 | advisor |

---

## 🔧 故障排查

### 聊天无响应
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看服务器日志

### Agent 列表为空
1. 检查 `configs/team.json` 是否存在
2. 刷新页面（Ctrl + F5）

---

_完整文档见 `docs/` 目录_
