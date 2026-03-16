# YM-CODE

**你的 AI 编程助手** - 本地部署、功能强大、安全可控

![Version](https://img.shields.io/badge/version-0.5.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-138%20passed-brightgreen)

---

## 🌟 特性

- 🤖 **AI 驱动** - 基于 LLM 的智能编程助手
- 🛠️ **11 个技能** - 文件操作、代码分析、Shell 命令等
- 💬 **自然对话** - 理解你的需求，自动调用工具
- 📁 **文件管理** - 可视化文件浏览器
- ⌨️ **Web 终端** - 浏览器中的命令行
- 📋 **任务管理** - 看板视图，追踪进度
- 🔐 **本地部署** - 数据完全可控，安全隐私
- 🚀 **开箱即用** - 一键初始化，快速上手

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ym-code.git
cd ym-code
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化系统

```bash
# 运行初始化脚本
python init.py

# 编辑 .env 文件，配置你的 API Key
# DASHSCOPE_API_KEY=sk-your-api-key-here
```

### 4. 启动服务

```bash
python start-web.py
```

访问 http://localhost:18770

---

## 📖 文档

- [快速开始](QUICKSTART.md) - 安装和配置指南
- [系统架构](docs/SYSTEM_ARCHITECTURE.md) - 技术架构说明
- [使用指南](docs/USAGE.md) - 功能使用说明
- [技能系统](docs/SKILLS.md) - 技能开发指南
- [API 文档](http://localhost:18770/docs) - REST API 文档

---

## 🛠️ 功能模块

### 1. AI 聊天
- 自然语言对话
- 自动工具调用
- 上下文记忆
- 多 Session 管理

### 2. 文件浏览器
- 文件树导航
- 文件预览
- 文件操作（读/写/删除）
- 目录管理

### 3. Web 终端
- PowerShell 集成
- 实时命令执行
- 多会话支持
- 历史记录

### 4. 任务管理
- 看板视图
- 状态流转（Inbox → Done）
- 优先级管理
- 任务追踪

### 5. 技能市场
- 11 个内置技能
- 技能扩展系统
- MCP 协议支持
- 自定义技能

---

## 📊 测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=ymcode --cov-report=html

# 运行特定测试
pytest tests/test_mcp_server.py -v
```

**当前状态：** 138 个测试通过，2 个跳过，0 个失败 ✅

---

## 🔧 配置

### 环境变量（.env）

```bash
# LLM API 配置（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here

# 服务器配置
YM_CODE_PORT=18770
YM_CODE_DEBUG=false

# 功能开关
YM_CODE_FEATURE_FILE_BROWSER=true
YM_CODE_FEATURE_WEB_TERMINAL=true
```

### 配置文件（config.json）

```json
{
  "model": {
    "primary": "qwen3.5-plus",
    "fallback": "qwen-plus"
  },
  "features": {
    "file_browser": true,
    "web_terminal": true,
    "task_manager": true
  }
}
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│          Web UI (React/Vue)             │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│          FastAPI Server                  │
│  /api/chat  /api/files  /api/terminal   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│          Core Agent Engine              │
│  - Agent Loop  - State Manager          │
│  - LLM Client - Context Manager         │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│          Skills Layer (11 skills)       │
│  memory, search, shell, code_analysis   │
│  http, database, formatter, docker      │
│  chat, llm, self_improvement            │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│          Data Layer                     │
│  SQLite (sessions) + File System        │
└─────────────────────────────────────────┘
```

---

## 🤝 贡献

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/simple-f/ym-code.git
cd ym-code

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/ -v

# 代码格式化
black ymcode/
flake8 ymcode/
```

### 提交规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

---

## 📝 更新日志

### v0.5.0 (2026-03-16)

**新功能：**
- ✅ 完整 Web 界面（聊天、文件、终端、任务、技能）
- ✅ 文件浏览器（文件树 + 预览 + 操作）
- ✅ Web 终端（PowerShell + 命令执行）
- ✅ 任务管理看板
- ✅ 技能市场展示

**改进：**
- ✅ 现代化深色主题 UI
- ✅ 响应式布局
- ✅ 性能优化

**测试：**
- ✅ 138 个测试通过
- ✅ 98.6% 通过率

### v0.3.5 (2026-03-16)

- ✅ MCP 服务器本地化
- ✅ 集成测试修复
- ✅ 测试覆盖率提升

### v0.1.0 (2026-03-07)

- ✅ 核心功能完成
- ✅ 11 个内置技能
- ✅ CLI 工具

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- **阿里云百炼** - LLM 支持
- **OpenClaw** - 架构参考
- **社区贡献者** - 感谢所有贡献

---

## 📬 联系方式

- **GitHub Issues:** 提交 Bug 或功能建议
- **Email:** your-email@example.com
- **Discord:** 加入社区讨论

---

**🌟 如果这个项目对你有帮助，请给个 Star！**
