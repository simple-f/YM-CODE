# YM-CODE API 文档

**版本：** v0.5.0  
**更新时间：** 2026-03-16  
**基础 URL:** `http://localhost:18770/api`

---

## 📋 目录

- [认证](#认证)
- [聊天 API](#聊天-api)
- [文件 API](#文件-api)
- [终端 API](#终端-api)
- [技能 API](#技能-api)
- [任务 API](#任务-api)
- [Session API](#session-api)
- [错误处理](#错误处理)

---

## 🔐 认证

> **注意：** v0.5.0 暂不需要认证，后续版本将添加 JWT 认证

---

## 💬 聊天 API

### POST /chat

发送消息并获取 AI 响应

**请求：**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "你好，请帮我创建一个 Python 项目",
  "session_id": "session_123"  // 可选
}
```

**响应：**
```json
{
  "success": true,
  "response": "好的，我来帮你创建一个 Python 项目...",
  "session_id": "session_123",
  "tool_calls": [
    {
      "name": "shell",
      "arguments": {"command": "mkdir my_project"}
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "error": "API key not configured",
  "code": "CONFIG_ERROR"
}
```

---

## 📁 文件 API

### GET /files/list

列出目录内容

**请求：**
```http
GET /api/files/list?path=/home/user&include_hidden=false
```

**响应：**
```json
{
  "success": true,
  "path": "/home/user",
  "files": [
    {
      "name": "file1.py",
      "type": "file",
      "size": 1024,
      "modified": "2026-03-16T10:00:00Z"
    },
    {
      "name": "docs",
      "type": "folder",
      "modified": "2026-03-16T09:00:00Z"
    }
  ]
}
```

---

### GET /files/read

读取文件内容

**请求：**
```http
GET /api/files/read?path=/home/user/file.py&encoding=utf-8
```

**响应：**
```json
{
  "success": true,
  "path": "/home/user/file.py",
  "content": "def hello():\n    print('world')",
  "encoding": "utf-8",
  "size": 1024
}
```

**下载文件：**
```http
GET /api/files/read?path=/home/user/file.py&download=1
```

---

### POST /files/create

创建文件或目录

**请求：**
```http
POST /api/files/create
Content-Type: application/json

{
  "path": "/home/user/new_file.py",
  "content": "print('hello')",
  "type": "file",  // 或 "folder"
  "encoding": "utf-8"
}
```

**响应：**
```json
{
  "success": true,
  "path": "/home/user/new_file.py",
  "message": "文件创建成功"
}
```

---

### POST /files/delete

删除文件或目录

**请求：**
```http
POST /api/files/delete
Content-Type: application/json

{
  "path": "/home/user/old_file.py",
  "recursive": false  // 删除目录时需要
}
```

**响应：**
```json
{
  "success": true,
  "path": "/home/user/old_file.py",
  "message": "文件删除成功"
}
```

---

### POST /files/rename

重命名文件或目录

**请求：**
```http
POST /api/files/rename
Content-Type: application/json

{
  "old_path": "/home/user/old_name.py",
  "new_path": "/home/user/new_name.py"
}
```

**响应：**
```json
{
  "success": true,
  "old_path": "/home/user/old_name.py",
  "new_path": "/home/user/new_name.py",
  "message": "重命名成功"
}
```

---

### POST /files/move

移动文件或目录

**请求：**
```http
POST /api/files/move
Content-Type: application/json

{
  "source": "/home/user/file.py",
  "destination": "/home/user/docs/file.py"
}
```

**响应：**
```json
{
  "success": true,
  "message": "移动成功"
}
```

---

## ⌨️ 终端 API

### POST /terminal/execute

执行命令

**请求：**
```http
POST /api/terminal/execute
Content-Type: application/json

{
  "command": "dir",
  "args": [],
  "cwd": "/home/user",
  "shell": true,
  "session_id": "term_123"
}
```

**响应：**
```json
{
  "success": true,
  "output": "文件列表...",
  "stdout": "标准输出",
  "stderr": "错误输出",
  "returncode": 0,
  "session_id": "term_123"
}
```

---

### WS /terminal/ws

WebSocket 实时终端

**连接：**
```javascript
const ws = new WebSocket('ws://localhost:18770/api/terminal/ws');

ws.onopen = () => {
  console.log('终端连接成功');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('输出:', data.output);
};

// 发送命令
ws.send(JSON.stringify({
  "command": "dir",
  "session_id": "term_123"
}));
```

---

### GET /terminal/sessions

列出终端会话

**请求：**
```http
GET /api/terminal/sessions
```

**响应：**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "term_123",
      "created_at": "2026-03-16T10:00:00Z",
      "last_activity": "2026-03-16T10:05:00Z"
    }
  ]
}
```

---

### POST /terminal/close

关闭终端会话

**请求：**
```http
POST /api/terminal/close
Content-Type: application/json

{
  "session_id": "term_123"
}
```

**响应：**
```json
{
  "success": true,
  "message": "会话已关闭"
}
```

---

## 🛠️ 技能 API

### GET /skills/list

列出已安装技能

**请求：**
```http
GET /api/skills/list
```

**响应：**
```json
{
  "success": true,
  "skills": [
    {
      "name": "memory",
      "description": "记忆管理",
      "version": "1.0.0",
      "author": "YM-CODE Team",
      "enabled": true
    },
    {
      "name": "shell",
      "description": "Shell 命令执行",
      "version": "1.0.0",
      "enabled": true
    }
  ]
}
```

---

### GET /skills/market

获取技能市场

**请求：**
```http
GET /api/skills/market?category=all
```

**响应：**
```json
{
  "success": true,
  "skills": [
    {
      "name": "github",
      "description": "GitHub 集成",
      "version": "1.0.0",
      "author": "Community",
      "downloads": 1000,
      "rating": 4.8
    }
  ]
}
```

---

### POST /skills/install

安装技能

**请求：**
```http
POST /api/skills/install
Content-Type: application/json

{
  "skill_name": "github",
  "version": "1.0.0"
}
```

**响应：**
```json
{
  "success": true,
  "message": "技能安装成功",
  "skill": {
    "name": "github",
    "version": "1.0.0"
  }
}
```

---

### POST /skills/uninstall

卸载技能

**请求：**
```http
POST /api/skills/uninstall
Content-Type: application/json

{
  "skill_name": "github"
}
```

**响应：**
```json
{
  "success": true,
  "message": "技能卸载成功"
}
```

---

### POST /skills/enable

启用技能

**请求：**
```http
POST /api/skills/enable
Content-Type: application/json

{
  "skill_name": "shell"
}
```

**响应：**
```json
{
  "success": true,
  "message": "技能已启用"
}
```

---

### POST /skills/disable

禁用技能

**请求：**
```http
POST /api/skills/disable
Content-Type: application/json

{
  "skill_name": "shell"
}
```

**响应：**
```json
{
  "success": true,
  "message": "技能已禁用"
}
```

---

## 📋 任务 API

### GET /tasks/list

列出所有任务

**请求：**
```http
GET /api/tasks/list?status=all&limit=50
```

**响应：**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task_123",
      "title": "完成用户登录功能",
      "description": "实现 JWT 认证",
      "status": "build",
      "priority": "high",
      "created_at": "2026-03-16T10:00:00Z",
      "updated_at": "2026-03-16T10:05:00Z"
    }
  ],
  "total": 10
}
```

---

### POST /tasks/create

创建任务

**请求：**
```http
POST /api/tasks/create
Content-Type: application/json

{
  "title": "完成用户登录功能",
  "description": "实现 JWT 认证",
  "status": "inbox",
  "priority": "high",
  "assignee": "user123"
}
```

**响应：**
```json
{
  "success": true,
  "task": {
    "id": "task_123",
    "title": "完成用户登录功能",
    "status": "inbox"
  }
}
```

---

### POST /tasks/move/{id}

移动任务（改变状态）

**请求：**
```http
POST /api/tasks/move/task_123
Content-Type: application/json

{
  "status": "build",
  "comment": "开始开发"
}
```

**响应：**
```json
{
  "success": true,
  "task": {
    "id": "task_123",
    "status": "build",
    "updated_at": "2026-03-16T10:10:00Z"
  }
}
```

---

### DELETE /tasks/{id}

删除任务

**请求：**
```http
DELETE /api/tasks/task_123
```

**响应：**
```json
{
  "success": true,
  "message": "任务已删除"
}
```

---

### GET /tasks/stats/summary

获取任务统计

**请求：**
```http
GET /api/tasks/stats/summary
```

**响应：**
```json
{
  "success": true,
  "stats": {
    "total": 50,
    "inbox": 10,
    "spec": 5,
    "build": 15,
    "review": 10,
    "done": 10
  }
}
```

---

## 🔑 Session API

### GET /sessions/list

列出所有 Session

**请求：**
```http
GET /api/sessions/list?limit=20
```

**响应：**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "session_123",
      "title": "Python 项目开发",
      "created_at": "2026-03-16T10:00:00Z",
      "last_message_at": "2026-03-16T10:30:00Z",
      "message_count": 25
    }
  ]
}
```

---

### GET /sessions/{id}/messages

获取 Session 消息历史

**请求：**
```http
GET /api/sessions/session_123/messages?limit=50
```

**响应：**
```json
{
  "success": true,
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "帮我创建一个 Python 项目",
      "timestamp": "2026-03-16T10:00:00Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "好的，我来帮你创建...",
      "timestamp": "2026-03-16T10:00:05Z"
    }
  ]
}
```

---

### DELETE /sessions/{id}

删除 Session

**请求：**
```http
DELETE /api/sessions/session_123
```

**响应：**
```json
{
  "success": true,
  "message": "Session 已删除"
}
```

---

## ❌ 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE",
  "details": {
    "field": "具体字段错误"
  }
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `CONFIG_ERROR` | 500 | 配置错误（如 API Key 未配置） |
| `NOT_FOUND` | 404 | 资源不存在 |
| `INVALID_PARAMS` | 400 | 参数无效 |
| `UNAUTHORIZED` | 401 | 未授权（后续版本） |
| `FORBIDDEN` | 403 | 禁止访问 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `TIMEOUT` | 504 | 请求超时 |

### 错误示例

**参数无效：**
```json
{
  "success": false,
  "error": "缺少必需参数：path",
  "code": "INVALID_PARAMS",
  "details": {
    "path": "此字段为必需"
  }
}
```

**资源不存在：**
```json
{
  "success": false,
  "error": "文件不存在：/home/user/not_found.py",
  "code": "NOT_FOUND"
}
```

---

## 📊 速率限制

> **注意：** v0.5.0 暂无速率限制，后续版本将添加

---

## 🧪 测试示例

### 使用 curl 测试

**聊天：**
```bash
curl -X POST http://localhost:18770/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

**文件列表：**
```bash
curl http://localhost:18770/api/files/list?path=.
```

**技能列表：**
```bash
curl http://localhost:18770/api/skills/list
```

---

### 使用 Python 测试

```python
import requests

# 聊天
response = requests.post(
    'http://localhost:18770/api/chat',
    json={'message': '你好'}
)
print(response.json())

# 文件列表
response = requests.get(
    'http://localhost:18770/api/files/list',
    params={'path': '.'}
)
print(response.json())
```

---

## 📝 更新日志

### v0.5.0 (2026-03-16)

- ✅ 完整的 REST API
- ✅ WebSocket 实时终端
- ✅ 文件操作 API
- ✅ 技能管理 API
- ✅ 任务管理 API

---

## 🆘 获取帮助

- **Swagger UI:** http://localhost:18770/docs
- **ReDoc:** http://localhost:18770/redoc
- **GitHub Issues:** 提交 Bug 或功能建议

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
