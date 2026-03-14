# YM-CODE 快速开始

**无需配置，开箱即用！** 🚀

---

## 🎯 立即开始

### 1. 启动 YM-CODE

```bash
cd C:\Users\Administrator\.openclaw\workspace-ai1\YM-CODE
python -m ymcode
```

### 2. 开始使用

```
YM-CODE v0.1.0
AI Programming Assistant
Port: 18770

ym-code> 
```

---

## 💡 可用的本地技能（9 个）

### 📁 文件操作

```bash
# 读取文件
> 读取 src/main.py

# 搜索文件
> 搜索项目中的 Python 文件
> 查找所有包含 TODO 的文件

# 创建/编辑文件
> 在 output 目录创建 test.txt
> 写入 "Hello World" 到 test.txt
```

### 🐚 命令执行

```bash
# 执行系统命令
> 运行 python --version
> 执行 git status
> 运行 pip list

# 执行脚本
> 运行 tests/test_main.py
> 执行 npm install
```

### 🔍 代码分析

```bash
# 代码质量检查
> 分析 src/main.py 的代码质量

# 复杂度分析
> 检查这个文件的复杂度

# 统计信息
> 统计项目的代码行数
```

### 🎨 代码格式化

```bash
# 格式化代码
> 格式化 src/main.py
> 美化这段 Python 代码

# 支持的语言
- Python ✅
- JavaScript ✅
- TypeScript ✅
- JSON ✅
```

### 🌐 HTTP 请求

```bash
# GET 请求
> 访问 https://api.github.com/users/octocat

# POST 请求
> 发送 POST 请求到 https://httpbin.org/post
```

### 🗄️ 数据库

```bash
# MySQL/PostgreSQL
> 连接到本地 MySQL
> 执行 SELECT * FROM users
```

### 🐳 Docker

```bash
# 容器管理
> 列出运行中的容器
> 停止容器 my-app

# 镜像管理
> 列出所有镜像
> 拉取 python:3.13
```

### 🧠 记忆管理

```bash
# 保存记忆
> 记住这个配置：API_KEY=12345

# 加载记忆
> 加载上次会话的记忆

# 搜索记忆
> 搜索关于 API 的记忆
```

### 📈 自我提升

```bash
# 总结会话
> 总结这次会话的收获

# 学习改进
> 从这次错误中学习
```

---

## 🎯 常用场景

### 场景 1：查看项目状态

```bash
ym-code> 执行 git status
ym-code> 列出当前目录的文件
ym-code> 读取 README.md
```

### 场景 2：代码审查

```bash
ym-code> 分析 src/main.py 的代码质量
ym-code> 检查这个文件的复杂度
ym-code> 格式化 src/utils.py
```

### 场景 3：运行测试

```bash
ym-code> 运行 pytest tests/
ym-code> 执行 python -m pytest tests/test_main.py -v
ym-code> 查看测试报告
```

### 场景 4：文件搜索

```bash
ym-code> 搜索项目中的 TODO 注释
ym-code> 查找所有 Python 文件
ym-code> 搜索包含 "error" 的文件
```

---

## ⚙️ 环境变量（可选）

### 配置 API Key（如需使用 AI 功能）

创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

**没有 API Key 也能使用！** 只是部分 AI 功能会受限。

---

## 📁 数据目录

YM-CODE 会在以下位置创建数据：

```
~/.ymcode/
├── logs/          # 日志文件
├── sessions/      # 会话记忆
├── skills/        # 技能数据
│   └── memory/    # 长期记忆
└── mcp/           # MCP 配置（如配置）
```

---

## 🛠️ 故障排查

### 问题 1：启动失败

```bash
# 检查 Python 版本
python --version  # 需要 3.10+

# 检查依赖
pip install -r requirements.txt
```

### 问题 2：中文乱码

```bash
# Windows 设置控制台编码
chcp 65001
python -m ymcode
```

### 问题 3：命令找不到

```bash
# 检查是否在正确目录
cd C:\Users\Administrator\.openclaw\workspace-ai1\YM-CODE
python -m ymcode
```

---

## 📚 更多文档

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 项目介绍 |
| [SETUP.md](./SETUP.md) | 安装指南 |
| [CROSS_PLATFORM.md](./CROSS_PLATFORM.md) | 跨平台说明 |
| [SKILLS_MCP_INTEGRATION.md](./SKILLS_MCP_INTEGRATION.md) | Skills 详解 |
| [MCP_QUICKSTART.md](./MCP_QUICKSTART.md) | MCP 配置（可选） |

---

## 🎉 开始使用

```bash
cd C:\Users\Administrator\.openclaw\workspace-ai1\YM-CODE
python -m ymcode
```

**就这么简单！** 🚀

---

**最后更新:** 2026-03-14  
**版本:** v0.1.0
