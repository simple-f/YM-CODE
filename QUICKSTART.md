# YM-CODE 快速开始

**版本：** v0.5.0  
**更新时间：** 2026-03-16

---

## 🚀 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ym-code.git
cd ym-code
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，配置你的 API Key
# DASHSCOPE_API_KEY=sk-your-api-key-here
```

### 4. 初始化系统

```bash
# 运行初始化脚本
python init.py
```

### 5. 启动服务

```bash
# 启动 Web 服务
python start-web.py

# 或使用 CLI
ym-code start
```

访问 http://localhost:18770

---

## 📋 系统要求

### 最低要求

- **Python:** 3.10+
- **内存:** 2GB
- **磁盘:** 500MB

### 推荐配置

- **Python:** 3.13
- **内存:** 4GB+
- **磁盘:** 1GB+

---

## 🔧 配置说明

### 环境变量（.env）

```bash
# LLM API 配置（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here

# 可选配置
OPENAI_API_KEY=sk-xxx
MOONSHOT_API_KEY=sk-xxx

# YM-CODE 配置
YM_CODE_MAX_ITERATIONS=30
YM_CODE_TIMEOUT=300
YM_CODE_LOG_LEVEL=INFO

# 服务器配置
YM_CODE_HOST=0.0.0.0
YM_CODE_PORT=18770
YM_CODE_DEBUG=false
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
    "task_manager": true,
    "skills_market": true
  },
  "storage": {
    "sessions_db": "~/.ymcode/sessions.db",
    "memory_dir": "~/.ymcode/memory"
  }
}
```

---

## 📁 目录结构

```
ym-code/
├── ymcode/              # 核心代码
│   ├── agents/          # 多 Agent 系统
│   ├── api/             # Web API
│   ├── cli/             # 命令行工具
│   ├── core/            # 核心引擎
│   ├── mcp/             # MCP 协议
│   ├── skills/          # 技能系统
│   └── storage/         # 数据存储
├── tests/               # 测试套件
├── web/                 # Web 前端
├── docs/                # 文档
├── .env.example         # 环境配置模板
├── config.json          # 配置文件
├── init.py              # 初始化脚本
├── requirements.txt     # Python 依赖
└── start-web.py         # 启动脚本
```

---

## 🧪 验证安装

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_mcp_server.py -v
```

### 检查系统状态

```bash
# 使用 CLI 检查
ym-code doctor

# 或手动检查
python -c "from ymcode import check_system; check_system()"
```

---

## ❓ 常见问题

### 1. API Key 配置错误

**错误：** `API key not configured`

**解决：**
```bash
# 检查 .env 文件
cat .env

# 确保 API Key 正确
DASHSCOPE_API_KEY=sk-xxx
```

### 2. 端口被占用

**错误：** `Address already in use`

**解决：**
```bash
# 修改端口
echo "YM_CODE_PORT=18771" >> .env

# 或杀死占用端口的进程
netstat -ano | findstr :18770
taskkill /PID <pid> /F
```

### 3. 依赖安装失败

**错误：** `Failed to install dependencies`

**解决：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 4. 中文乱码

**错误：** Windows 控制台中文乱码

**解决：**
```bash
# 设置控制台编码
chcp 65001

# 或在 .env 中添加
PYTHONIOENCODING=utf-8
```

---

## 🆘 获取帮助

### 文档

- [系统架构](docs/SYSTEM_ARCHITECTURE.md)
- [API 文档](http://localhost:18770/docs)
- [使用指南](docs/USAGE.md)

### 社区

- GitHub Issues: 提交 Bug 或功能建议
- Discord: 加入社区讨论

---

## 📝 下一步

- ✅ 完成快速安装
- ✅ 配置 API Key
- ✅ 启动 Web 服务
- 📖 阅读 [使用指南](docs/USAGE.md)
- 🛠️ 探索 [技能系统](docs/SKILLS.md)

---

**祝你使用愉快！** 🎉
