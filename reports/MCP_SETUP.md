# YM-CODE MCP 服务器配置指南

连接外部服务（GitHub、Notion、PostgreSQL 等）的配置指南。

---

## 🚀 快速开始

### 方式 1：自动安装（推荐）

YM-CODE 会自动安装常用的 MCP 服务器：

```bash
# 运行 YM-CODE
python -m ymcode

# 首次运行时会自动提示安装
```

### 方式 2：手动安装

```bash
# 安装 GitHub MCP 服务器
npx -y @modelcontextprotocol/server-github

# 安装文件系统 MCP 服务器
npx -y @modelcontextprotocol/server-filesystem

# 安装 PostgreSQL MCP 服务器
npx -y @modelcontextprotocol/server-postgres
```

---

## 📦 可用的 MCP 服务器

### 官方服务器

| 服务器 | 安装命令 | 用途 |
|--------|----------|------|
| **GitHub** | `npx -y @modelcontextprotocol/server-github` | 管理 Issues、PRs、Repos |
| **文件系统** | `npx -y @modelcontextprotocol/server-filesystem` | 安全访问文件系统 |
| **PostgreSQL** | `npx -y @modelcontextprotocol/server-postgres` | 数据库操作 |
| **Git** | `npx -y @modelcontextprotocol/server-git` | Git 操作 |
| **Brave Search** | `npx -y @modelcontextprotocol/server-brave-search` | 网络搜索 |
| **Memory** | `npx -y @modelcontextprotocol/server-memory` | 长期记忆 |

### 第三方服务器

| 服务器 | 安装命令 | 用途 |
|--------|----------|------|
| **Notion** | `npx -y @notionhq/mcp-server` | Notion 管理 |
| **Slack** | `npx -y @slack/mcp-server` | Slack 集成 |
| **Linear** | `npx -y @linear/mcp-server` | 任务管理 |

---

## ⚙️ 配置方法

### 1. 创建配置文件

```bash
# 创建配置目录
mkdir -p ~/.ymcode/mcp

# 创建配置文件
cat > ~/.ymcode/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "/Users/yourname/workspace"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/dbname"
      }
    }
  }
}
EOF
```

### 2. 获取 API Tokens

#### GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - ✅ `repo` (完整仓库权限)
   - ✅ `workflow` (CI/CD)
   - ✅ `read:org` (读取组织)
4. 生成并复制 Token
5. 添加到配置文件

#### 其他服务

| 服务 | 获取地址 |
|------|----------|
| GitHub | https://github.com/settings/tokens |
| Notion | https://www.notion.so/my-integrations |
| Slack | https://api.slack.com/apps |
| Linear | https://linear.app/settings/api |

---

## 🔧 YM-CODE 集成

### 在 YM-CODE 中使用 MCP 服务器

```python
from ymcode.mcp import MCPClient

# 创建客户端
client = MCPClient()

# 连接 GitHub 服务器
await client.connect(
    "github",
    "stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "your_token"}
)

# 列出可用工具
tools = await client.get_tools_definition()
print(f"可用工具：{len(tools)}")

# 使用工具
result = await client.call_tool(
    "github_list_repos",
    {"username": "your-username"}
)
print(f"你的仓库：{result}")
```

### 在 CLI 中使用

```bash
# 启动 YM-CODE
python -m ymcode

# 使用 GitHub 功能
> 列出我的 GitHub 仓库

# 创建 Issue
> 在 ym-code 仓库创建一个 bug 报告
```

---

## 📝 完整配置示例

### ~/.ymcode/mcp/config.json

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "/Users/yourname/workspace:/tmp"
      }
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

---

## 🔍 验证配置

### 检查 MCP 服务器状态

```python
from ymcode.mcp import MCPClient

client = MCPClient()

# 连接服务器
await client.connect("github", "stdio", ...)

# 获取状态
status = client.get_status()
print(f"连接状态：{status}")

# 列出工具
tools = await client.get_tools_definition()
for tool in tools:
    print(f"  - {tool['name']}: {tool['description']}")
```

### 测试 GitHub 连接

```python
# 测试列出仓库
result = await client.call_tool(
    "github_list_repos",
    {"username": "your-username"}
)
print(f"找到 {len(result['repositories'])} 个仓库")
```

---

## 🛠️ 故障排查

### 问题 1：无法连接服务器

**症状：** `Connection refused`

**解决：**
```bash
# 检查 npx 是否可用
npx --version

# 重新安装 MCP 服务器
npm install -g @modelcontextprotocol/server-github

# 测试运行
npx -y @modelcontextprotocol/server-github
```

### 问题 2：Token 无效

**症状：** `Authentication failed`

**解决：**
1. 检查 Token 是否正确
2. 确认 Token 权限
3. 重新生成 Token

### 问题 3：找不到工具

**症状：** `Tool not found`

**解决：**
```python
# 列出所有可用工具
tools = await client.get_tools_definition()
print([t['name'] for t in tools])

# 检查工具名称是否正确
# 使用正确的工具名称调用
```

---

## 📚 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)
- [YM-CODE 文档](./README.md)
- [Skills 系统](./SKILLS_MCP_INTEGRATION.md)

---

**最后更新:** 2026-03-14
