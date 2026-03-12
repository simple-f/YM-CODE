# MCP 协议支持指南

> Model Context Protocol 完整实现

---

## ✅ 当前状态

| 功能 | 状态 | 说明 |
|------|------|------|
| **MCP Client** | ✅ 已实现 | 基础连接功能 |
| **工具发现** | ✅ 已实现 | 自动发现工具 |
| **工具调用** | ✅ 已实现 | 支持远程调用 |
| **MCP Server** | ⏳ 待实现 | 可以连接现有 Server |
| **SSE 传输** | ⏳ 待实现 | 目前仅支持本地 |
| **Streamable HTTP** | ⏳ 待实现 | 下一步实现 |

---

## 🚀 快速开始

### 1. 创建 MCP Client

```python
from ymcode.mcp import MCPClient

# 创建客户端
client = MCPClient()
```

### 2. 连接到 MCP 服务器

```python
# 连接本地文件系统
await client.connect(
    server_name="local-filesystem",
    url="file:///tmp/mcp-filesystem"
)

# 连接远程服务器
await client.connect(
    server_name="remote-server",
    url="https://mcp.example.com/sse"
)
```

### 3. 获取工具列表

```python
# 获取所有工具
tools = client.get_tools_definition()

for tool in tools:
    print(f"{tool['function']['name']}: {tool['function']['description']}")
```

### 4. 调用工具

```python
# 调用文件读取
result = await client.call_tool(
    tool_name="read_file",
    arguments={"path": "test.txt"}
)

print(result)
```

### 5. 断开连接

```python
# 断开特定服务器
await client.disconnect("local-filesystem")

# 断开所有连接
await client.disconnect()
```

---

## 📊 支持的 MCP 服务器

### 已测试

| 服务器 | URL | 状态 | 工具数 |
|--------|-----|------|--------|
| 本地文件系统 | file:///... | ✅ | 2 |
| 数据库 | postgres://... | ⏳ | - |
| 远程 HTTP | https://... | ⏳ | - |

### 计划支持

- [ ] GitHub MCP Server
- [ ] Google Drive MCP Server
- [ ] Slack MCP Server
- [ ] Notion MCP Server
- [ ] 自定义 MCP Server

---

## 🔧 高级用法

### 集成到 Agent

```python
from ymcode.core.agent import Agent
from ymcode.mcp import MCPClient

# 创建 Agent 和 MCP Client
agent = Agent()
mcp_client = MCPClient()

# 连接 MCP 服务器
await mcp_client.connect("local-filesystem", "file:///...")

# 获取 MCP 工具定义
mcp_tools = mcp_client.get_tools_definition()

# 将 MCP 工具添加到 Agent
for tool_def in mcp_tools:
    agent.tools.register_mcp_tool(tool_def)

# 现在 Agent 可以使用 MCP 工具
result = await agent.run("读取 test.txt 文件")
```

### 多服务器管理

```python
# 连接多个服务器
await client.connect("filesystem", "file:///...")
await client.connect("database", "postgres://...")
await client.connect("github", "https://...")

# 查看所有连接状态
status = client.get_status()
print(f"连接数：{status['servers']}")
print(f"工具数：{status['tools']}")

# 按服务器筛选工具
for server_name, server in client.servers.items():
    print(f"\n{server_name}:")
    for tool in server.tools:
        print(f"  - {tool.name}")
```

---

## 📝 实现细节

### MCP Client 架构

```
┌─────────────────────────────────────┐
│         MCP Client                  │
├─────────────────────────────────────┤
│  Connection Manager                 │
│  - 连接管理                         │
│  - 心跳检测                         │
│  - 自动重连                         │
├─────────────────────────────────────┤
│  Tool Discovery                     │
│  - 工具发现                         │
│  - 工具注册                         │
│  - 工具描述                         │
├─────────────────────────────────────┤
│  Tool Invocation                    │
│  - 参数验证                         │
│  - 远程调用                         │
│  - 结果解析                         │
└─────────────────────────────────────┘
```

### 消息协议

```json
// 请求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}

// 响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "read_file",
        "description": "读取文件内容",
        "inputSchema": {...}
      }
    ]
  }
}
```

---

## 🐛 故障排查

### 问题 1：连接失败

**错误：** `Connection refused`

**解决：**
1. 检查服务器地址是否正确
2. 确认服务器已启动
3. 检查防火墙设置

### 问题 2：工具调用失败

**错误：** `Tool not found`

**解决：**
1. 检查工具名称是否正确
2. 确认服务器已连接
3. 检查工具参数格式

### 问题 3：超时

**错误：** `Connection timeout`

**解决：**
1. 增加超时时间
2. 检查网络连接
3. 确认服务器响应正常

---

## 📖 参考资料

- [MCP 官方文档](https://github.com/anthropics/mcp)
- [MCP 规范](https://modelcontextprotocol.io/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

---

_最后更新：2026-03-13_

_作者：YM-CODE Team_
