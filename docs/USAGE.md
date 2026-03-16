# YM-CODE 使用指南

**版本：** v0.5.0  
**更新时间：** 2026-03-16

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE

# 安装依赖
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. 初始化

```bash
# 运行初始化脚本
python init.py

# 配置 API Key
# 编辑 .env 文件，设置 DASHSCOPE_API_KEY
```

### 3. 启动

```bash
# Web 模式（推荐）
python start-web.py

# 访问：http://localhost:18770
```

---

## 💬 聊天功能

### 基本对话

**Web 界面：**
1. 打开 http://localhost:18770
2. 在聊天框输入消息
3. 按 Enter 或点击发送

**示例对话：**
```
你：帮我创建一个 Python 项目
YM-CODE: 好的，我来帮你创建一个 Python 项目结构。

正在执行：mkdir my_project
正在执行：cd my_project
正在执行：python -m venv venv
...

项目创建完成！目录结构如下：
my_project/
├── venv/
├── src/
├── tests/
└── README.md
```

### 使用工具

YM-CODE 会自动判断是否需要使用工具：

```
你：查看当前目录的文件
YM-CODE: [调用 shell 技能]

执行命令：dir

目录内容：
- file1.py
- file2.py
- docs/
```

---

## 📁 文件浏览器

### 浏览文件

1. 点击左侧导航栏的 **📁 文件浏览器**
2. 在文件树中点击文件夹展开
3. 点击文件预览内容

### 文件操作

**预览文件：**
- 点击文件即可在右侧预览
- 支持代码高亮
- 支持大文件查看

**下载文件：**
1. 选择文件
2. 点击 **⬇️ 下载** 按钮

**删除文件：**
1. 选择文件
2. 点击 **🗑️ 删除** 按钮
3. 确认删除

---

## ⌨️ Web 终端

### 使用终端

1. 点击左侧导航栏的 **⌨️ Web 终端**
2. 在输入框输入命令
3. 按 Enter 执行

**支持的命令：**
```powershell
# 文件操作
dir
cd <目录>
type <文件>
mkdir <目录>
del <文件>

# Git 操作
git status
git commit -m "message"
git push

# Python
python script.py
pip install package

# 其他
npm install
docker ps
```

### 终端功能

**清屏：**
- 点击 **🧹 清屏** 按钮
- 或输入 `cls` (Windows) / `clear` (Linux)

**新建会话：**
- 点击 **➕ 新建** 按钮
- 创建独立的终端会话

---

## 📋 任务管理

### 创建任务

**通过聊天创建：**
```
你：创建一个任务，完成用户登录功能
YM-CODE: 好的，已创建任务：
- 标题：完成用户登录功能
- 状态：Inbox
- 优先级：普通
```

**通过界面创建：**
1. 点击 **📋 任务管理**
2. 在 Inbox 列点击 **+** 按钮
3. 填写任务信息

### 任务状态流转

```
Inbox → Spec → Build → Review → Done
```

**移动任务：**
1. 点击任务卡片
2. 选择新状态
3. 任务自动移动到对应列

---

## 🛠️ 技能系统

### 内置技能

YM-CODE 包含 11 个内置技能：

| 技能 | 功能 | 示例 |
|------|------|------|
| memory | 记忆管理 | "记住这个信息" |
| shell | 命令行 | "执行 git status" |
| search | 搜索 | "搜索 Python 教程" |
| http | 网络请求 | "访问这个 API" |
| code_analysis | 代码分析 | "分析这段代码" |
| database | 数据库 | "查询用户表" |
| formatter | 格式化 | "格式化这段代码" |
| docker | Docker | "列出所有容器" |
| chat | 对话 | "你好" |
| llm | 大模型 | "写一首诗" |
| self_improvement | 自我提升 | "总结经验" |

### 使用技能

**自动调用：**
```
你：帮我搜索一下 Python 最佳实践
YM-CODE: [自动调用 search 技能]

正在搜索：Python 最佳实践
找到 10 个结果：
1. Python 官方风格指南
2. Google Python 风格指南
...
```

**手动指定：**
```
你：使用 shell 技能执行 dir 命令
YM-CODE: [执行 shell 技能]

目录内容：
- file1.py
- file2.py
```

---

## 🔧 配置

### 环境变量

编辑 `.env` 文件：

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
YM_CODE_PORT=18770
YM_CODE_DEBUG=false
```

### 配置文件

编辑 `config.json`：

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

## 📊 Session 管理

### 创建 Session

**自动创建：**
- 每次新对话自动创建 Session
- Session ID 显示在顶部

**手动创建：**
1. 点击顶部 Session 列表
2. 点击 **+ 新建**
3. 输入 Session 名称

### 切换 Session

1. 点击顶部 Session 名称
2. 选择要切换的 Session
3. 历史对话自动加载

### 删除 Session

1. 点击 Session 列表
2. 点击 Session 旁的 **🗑️** 按钮
3. 确认删除

---

## 💡 高级用法

### 1. 多步骤任务

```
你：帮我完成以下任务：
1. 创建项目目录
2. 初始化 Git
3. 创建 README.md
4. 提交代码

YM-CODE: 好的，我按顺序执行：

步骤 1/4: 创建项目目录 ✓
步骤 2/4: 初始化 Git ✓
步骤 3/4: 创建 README.md ✓
步骤 4/4: 提交代码 ✓

所有任务完成！
```

### 2. 代码审查

```
你：审查这段代码：
[粘贴代码]

YM-CODE: [调用 code_analysis 技能]

代码审查结果：

✅ 优点：
- 代码结构清晰
- 命名规范

⚠️ 建议：
- 第 10 行：可以添加类型注解
- 第 25 行：建议添加错误处理

📊 复杂度：低
📏 行数：50 行
```

### 3. 批量操作

```
你：把所有 .txt 文件重命名为 .md

YM-CODE: [分析文件列表]

找到 5 个 .txt 文件：
- file1.txt → file1.md
- file2.txt → file2.md
- ...

确认执行？[是/否]

> 是

正在重命名...
完成！5 个文件已重命名。
```

---

## ❓ 常见问题

### 1. API Key 配置

**问题：** "API key not configured"

**解决：**
```bash
# 检查 .env 文件
cat .env

# 确保 API Key 正确
DASHSCOPE_API_KEY=sk-xxx
```

### 2. 端口被占用

**问题：** "Address already in use"

**解决：**
```bash
# 修改端口
echo "YM_CODE_PORT=18771" >> .env

# 或杀死占用端口的进程
netstat -ano | findstr :18770
taskkill /PID <pid> /F
```

### 3. 中文乱码

**问题：** Windows 控制台中文乱码

**解决：**
```bash
# 设置控制台编码
chcp 65001

# 或在 .env 中添加
PYTHONIOENCODING=utf-8
```

### 4. 技能调用失败

**问题：** "技能执行失败"

**解决：**
```bash
# 检查技能是否启用
# 编辑 config.json
{
  "features": {
    "shell": true,
    "search": true,
    ...
  }
}

# 检查日志
cat ~/.ymcode/logs/ymcode.log
```

---

## 🎯 最佳实践

### 1. 会话管理

- ✅ 为不同项目创建独立 Session
- ✅ 定期清理不需要的 Session
- ✅ 重要对话保存为记忆

### 2. 技能使用

- ✅ 明确指定技能名称（复杂任务）
- ✅ 提供足够的上下文信息
- ✅ 检查结果再执行下一步

### 3. 文件操作

- ✅ 操作前确认路径
- ✅ 重要文件先备份
- ✅ 使用版本控制（Git）

### 4. 性能优化

- ✅ 大文件分块处理
- ✅ 复杂任务分解为小步骤
- ✅ 使用缓存（记忆系统）

---

## 📝 更新日志

### v0.5.0 (2026-03-16)

- ✅ 完整 Web 界面
- ✅ 文件浏览器
- ✅ Web 终端
- ✅ 任务管理
- ✅ 技能市场

### v0.3.5 (2026-03-16)

- ✅ MCP 协议集成
- ✅ 技能注册表优化
- ✅ 性能提升

---

## 🆘 获取帮助

### 文档

- [快速开始](QUICKSTART.md)
- [技能系统](docs/SKILLS.md)
- [系统架构](docs/SYSTEM_ARCHITECTURE.md)
- [API 文档](http://localhost:18770/docs)

### 社区

- GitHub Issues: 提交 Bug 或功能建议
- Discord: 加入社区讨论

---

**祝你使用愉快！** 🎉

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
