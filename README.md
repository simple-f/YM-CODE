# YM-CODE - 下一代 AI 编程助手

> **全面对标 Claude Code，打造更强大的 AI 编程体验**

---

## 🎯 项目愿景

**YM-CODE** 是一个**生产级 AI 编程助手**，基于 learn-claude-code 12 课的核心知识，融合 Final Agent 的完整架构，**全面对标 Claude Code**。

**设计目标：**
- ✅ **功能完整** - 20+ 内置工具，覆盖开发全流程
- ✅ **用户体验** - 精美 CLI 界面，实时进度反馈
- ✅ **工程完善** - npm 包管理，自动更新，插件系统
- ✅ **生态丰富** - MCP 协议支持，工具市场，IDE 集成

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         YM-CODE System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Core       │  │   Tools      │  │   Memory     │          │
│  │   核心引擎   │  │   工具系统   │  │   记忆系统   │          │
│  │              │  │              │  │              │          │
│  │ - Agent Loop │  │ - 20+ Tools  │  │ - Session    │          │
│  │ - LLM Client │  │ - MCP Client │  │ - Context    │          │
│  │ - State Mgr  │  │ - Registry   │  │ - Compress   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI        │  │   Skills     │  │   Utils      │          │
│  │   命令行界面 │  │   技能系统   │  │   工具库     │          │
│  │              │  │              │  │              │          │
│  │ - TUI        │  │ - Code Review│  │ - Logger     │          │
│  │ - Progress   │  │ - Debug      │  │ - Metrics    │          │
│  │ - AutoComplete│ │ - Test       │  │ - Helpers    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 核心特性

### 1. 精美 CLI 界面

```bash
$ ym-code

┌────────────────────────────────────────────┐
│  YM-CODE v1.0.0                            │
│  AI Programming Assistant                  │
└────────────────────────────────────────────┘

🤖 Ready to help! Type your request or 'help' for commands.

> 帮我修复这个 bug
```

**特性：**
- ✅ 彩色输出
- ✅ 进度条显示
- ✅ 实时状态更新
- ✅ 错误友好提示

---

### 2. 20+ 内置工具

| 类别 | 工具 | 说明 |
|------|------|------|
| **文件操作** | `read_file` | 读取文件 |
| | `write_file` | 写入文件 |
| | `edit_file` | 编辑文件 |
| | `smart_edit` | 智能编辑（局部修改） |
| | `list_dir` | 列出目录 |
| | `search_file` | 搜索文件 |
| **Git 操作** | `git_status` | Git 状态 |
| | `git_diff` | Git 差异 |
| | `git_commit` | Git 提交 |
| | `git_push` | Git 推送 |
| | `git_log` | Git 日志 |
| **开发工具** | `bash` | 执行命令 |
| | `run_test` | 运行测试 |
| | `run_linter` | 运行 linter |
| | `debug` | 调试代码 |
| | `explain` | 解释代码 |
| **网络工具** | `fetch` | HTTP 请求 |
| | `search_web` | 网络搜索 |

---

### 3. 智能技能系统

```python
# 内置技能示例
skills = {
    "code-review": "代码审查",
    "bug-fix": "Bug 修复",
    "refactor": "代码重构",
    "test-gen": "测试生成",
    "doc-gen": "文档生成",
    "security-audit": "安全审计",
}
```

**每个技能包含：**
- 多步骤流程
- 业务逻辑
- 最佳实践
- 领域知识

---

### 4. MCP 协议支持

```python
# 接入 MCP 工具市场
from ymcode import MCPClient

client = MCPClient()
await client.connect("https://mcp.example.com")

# 获取远程工具
tools = await client.list_tools()

# 调用远程工具
result = await client.call_tool("advanced-tool", param="value")
```

**好处：**
- ✅ 接入丰富工具生态
- ✅ 支持第三方工具
- ✅ 持续扩展

---

## 📁 项目结构

```
YM-CODE/
├── README.md                 # 本文件
├── pyproject.toml           # Python 项目配置
├── requirements.txt         # 依赖
├── setup.py                 # 安装脚本
│
├── ymcode/                  # 主模块
│   ├── __init__.py
│   ├── cli.py               # CLI 入口
│   │
│   ├── core/                # 核心引擎
│   │   ├── agent.py
│   │   ├── llm.py
│   │   └── state.py
│   │
│   ├── tools/               # 工具系统
│   │   ├── registry.py
│   │   ├── base.py
│   │   ├── file_tools.py
│   │   ├── git_tools.py
│   │   └── dev_tools.py
│   │
│   ├── skills/              # 技能系统
│   │   ├── base.py
│   │   ├── code_review.py
│   │   ├── bug_fix.py
│   │   └── test_gen.py
│   │
│   ├── memory/              # 记忆系统
│   │   ├── session.py
│   │   └── compressor.py
│   │
│   ├── mcp/                 # MCP 客户端
│   │   ├── client.py
│   │   └── protocol.py
│   │
│   └── utils/               # 工具库
│       ├── logger.py
│       ├── progress.py
│       └── helpers.py
│
├── tests/                   # 测试
│   ├── test_core.py
│   ├── test_tools.py
│   └── test_skills.py
│
└── docs/                    # 文档
    ├── installation.md
    ├── usage.md
    └── api.md
```

---

## 🚀 快速开始

### 1. 安装（开发中）

```bash
# 方式 1：pip 安装（计划中）
pip install ym-code

# 方式 2：源码安装
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE
pip install -e .

# 方式 3：npm 安装（计划中）
npm install -g ym-code
```

### 2. 配置

```bash
# 初始化配置
ym-code init

# 编辑配置
vim ~/.ymcode/config.yaml
```

### 3. 使用

```bash
# 交互式
ym-code

# 单次执行
ym-code "帮我修复这个 bug"

# 指定文件
ym-code "审查这个文件" --file main.py

# 使用技能
ym-code "审查代码" --skill code-review
```

---

## 📊 对比 Claude Code

| 特性 | Claude Code | YM-CODE | 状态 |
|------|-------------|---------|------|
| **Agent 循环** | ✅ | ✅ | ✅ 持平 |
| **工具数量** | 20+ | 20+（计划） | 🔄 开发中 |
| **CLI 界面** | ✅ 精美 | ✅ 精美（计划） | 🔄 开发中 |
| **Git 集成** | ✅ 深度 | ✅ 深度（计划） | 🔄 开发中 |
| **测试运行** | ✅ | ✅（计划） | 🔄 开发中 |
| **智能编辑** | ✅ | ✅（计划） | 🔄 开发中 |
| **MCP 协议** | ✅ | ✅（计划） | 🔄 开发中 |
| **插件系统** | ✅ | ✅（计划） | 🔄 开发中 |
| **自动更新** | ✅ | ✅（计划） | 🔄 开发中 |
| **IDE 集成** | ✅ VSCode | ✅ VSCode（计划） | 🔄 开发中 |

**我们的优势：**
- ✅ 开源免费
- ✅ 可定制性强
- ✅ 学习友好
- ✅ 社区驱动

---

## 🗺️ 开发路线图

### Phase 1：核心功能（2 周）

- [x] 项目创建
- [ ] CLI 界面美化（rich 库）
- [ ] Git 深度集成
- [ ] 测试运行器
- [ ] 智能文件编辑

### Phase 2：工程完善（2 周）

- [ ] npm 包管理
- [ ] 自动更新
- [ ] 配置管理优化
- [ ] 错误友好提示
- [ ] 进度显示

### Phase 3：生态建设（4 周）

- [ ] MCP 协议支持
- [ ] 工具市场
- [ ] VSCode 插件
- [ ] GitHub Actions
- [ ] 文档完善

### Phase 4：社区运营（持续）

- [ ] 社区建设
- [ ] 工具征集
- [ ] 最佳实践
- [ ] 案例分享

---

## 🤝 贡献指南

欢迎贡献！

```bash
# 1. Fork 项目
git fork https://github.com/simple-f/YM-CODE

# 2. 克隆到本地
git clone git@github.com:your-username/YM-CODE.git

# 3. 创建分支
git checkout -b feature/your-feature

# 4. 开发 + 测试
# ...

# 5. 提交 PR
git push origin feature/your-feature
```

---

## 📜 许可证

MIT

---

## 🙏 致谢

- [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) - 12 课教程
- [OpenClaw](https://github.com/openclaw/openclaw) - 生产经验
- [Claude Code](https://claude.ai/code) - 对标目标

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/simple-f/YM-CODE/issues
- **Discord**: （待创建）
- **微信群**: （待创建）

---

_最后更新：2026-03-12_

_作者：付艺锦 + ai2 (claw 后端机器人)_

_状态：开发中 🚧_
