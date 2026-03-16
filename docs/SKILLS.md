# YM-CODE 技能系统文档

**版本：** v0.5.0  
**更新时间：** 2026-03-16

---

## 📚 技能系统概述

YM-CODE 技能系统是一个强大的工具调用框架，允许 AI 通过自然语言调用各种功能。

### 核心特性

- 🛠️ **11 个内置技能** - 覆盖开发全流程
- 🔌 **MCP 协议支持** - 可连接外部工具
- 🧩 **可扩展架构** - 轻松添加自定义技能
- 🔄 **自动调度** - LLM 自动选择合适技能
- 📊 **类型安全** - JSON Schema 验证输入

---

## 🎯 技能列表

### 1. Memory Skill（记忆技能）

**功能：** 管理短期和长期记忆

**输入参数：**
```json
{
  "action": "save|load|search|list",
  "content": "记忆内容（save 时必需）",
  "query": "搜索关键词（search 时必需）",
  "session_id": "会话 ID（可选）"
}
```

**使用示例：**
```python
# 保存记忆
await memory_skill.execute({
    "action": "save",
    "content": "用户喜欢使用 Python 进行开发"
})

# 搜索记忆
result = await memory_skill.execute({
    "action": "search",
    "query": "Python"
})
```

**返回结果：**
```json
{
  "success": true,
  "memory_id": "mem_20260316...",
  "content": "记忆内容",
  "importance": 0.8
}
```

---

### 2. Shell Skill（命令行技能）

**功能：** 安全执行系统命令

**输入参数：**
```json
{
  "command": "命令名称",
  "args": ["参数 1", "参数 2"],
  "cwd": "工作目录（可选）",
  "shell": "是否使用 shell（默认 true）"
}
```

**使用示例：**
```python
# 列出文件
result = await shell_skill.execute({
    "command": "dir",
    "args": []
})

# 执行 Git 命令
result = await shell_skill.execute({
    "command": "git",
    "args": ["status"]
})
```

**返回结果：**
```json
{
  "success": true,
  "stdout": "命令输出",
  "stderr": "错误信息",
  "returncode": 0
}
```

---

### 3. Search Skill（搜索技能）

**功能：** Web 搜索、文件搜索

**输入参数：**
```json
{
  "query": "搜索关键词",
  "type": "web|file|code",
  "limit": "结果数量（默认 10）"
}
```

**使用示例：**
```python
# Web 搜索
result = await search_skill.execute({
    "query": "Python 最佳实践",
    "type": "web",
    "limit": 5
})
```

**返回结果：**
```json
{
  "success": true,
  "results": [
    {
      "title": "标题",
      "url": "链接",
      "snippet": "摘要"
    }
  ]
}
```

---

### 4. HTTP Skill（网络请求技能）

**功能：** 发送 HTTP 请求

**输入参数：**
```json
{
  "method": "GET|POST|PUT|DELETE",
  "url": "请求 URL",
  "headers": {"Header": "Value"},
  "body": "请求体（POST/PUT 时）",
  "timeout": "超时时间（秒）"
}
```

**使用示例：**
```python
# GET 请求
result = await http_skill.execute({
    "method": "GET",
    "url": "https://api.example.com/data"
})

# POST 请求
result = await http_skill.execute({
    "method": "POST",
    "url": "https://api.example.com/create",
    "headers": {"Content-Type": "application/json"},
    "body": {"name": "test"}
})
```

**返回结果：**
```json
{
  "success": true,
  "status_code": 200,
  "headers": {...},
  "body": "响应内容"
}
```

---

### 5. Code Analysis Skill（代码分析技能）

**功能：** 代码分析、统计、质量检查

**输入参数：**
```json
{
  "code": "代码内容",
  "language": "python|javascript|typescript",
  "analysis_type": "stats|quality|complexity"
}
```

**使用示例：**
```python
# 代码统计
result = await code_analysis_skill.execute({
    "code": "def hello():\n    print('world')",
    "language": "python",
    "analysis_type": "stats"
})
```

**返回结果：**
```json
{
  "success": true,
  "stats": {
    "lines": 2,
    "functions": 1,
    "classes": 0
  },
  "complexity": "low"
}
```

---

### 6. Database Skill（数据库技能）

**功能：** 数据库查询和管理

**输入参数：**
```json
{
  "action": "query|list_tables|describe",
  "connection": "数据库连接字符串",
  "sql": "SQL 语句（query 时）",
  "table": "表名（describe 时）"
}
```

**使用示例：**
```python
# 查询数据
result = await database_skill.execute({
    "action": "query",
    "connection": "sqlite:///test.db",
    "sql": "SELECT * FROM users"
})
```

**返回结果：**
```json
{
  "success": true,
  "rows": [...],
  "columns": ["id", "name", "email"],
  "count": 10
}
```

---

### 7. Formatter Skill（格式化技能）

**功能：** 代码格式化

**输入参数：**
```json
{
  "code": "代码内容",
  "language": "python|javascript|json",
  "indent_size": "缩进大小（默认 4）",
  "quote": "引号类型（single|double）"
}
```

**使用示例：**
```python
# 格式化 Python 代码
result = await formatter_skill.execute({
    "code": "def hello( ):print('world')",
    "language": "python",
    "indent_size": 4
})
```

**返回结果：**
```json
{
  "success": true,
  "formatted_code": "def hello():\n    print('world')",
  "changes": ["Removed extra space", "Added newline"]
}
```

---

### 8. Docker Skill（Docker 技能）

**功能：** Docker 容器管理

**输入参数：**
```json
{
  "action": "ps|images|run|stop|rm",
  "container_id": "容器 ID",
  "image": "镜像名称",
  "options": "额外选项"
}
```

**使用示例：**
```python
# 列出容器
result = await docker_skill.execute({
    "action": "ps"
})

# 运行容器
result = await docker_skill.execute({
    "action": "run",
    "image": "python:3.11",
    "options": "-d -v /data:/data"
})
```

**返回结果：**
```json
{
  "success": true,
  "containers": [...],
  "count": 3
}
```

---

### 9. Chat Skill（对话技能）

**功能：** 自然语言对话

**输入参数：**
```json
{
  "message": "用户消息",
  "context": "上下文（可选）",
  "tone": "语气（friendly|professional|casual）"
}
```

**使用示例：**
```python
# 普通对话
result = await chat_skill.execute({
    "message": "你好，请介绍一下你自己",
    "tone": "friendly"
})
```

**返回结果：**
```json
{
  "success": true,
  "response": "你好！我是 YM-CODE...",
  "context_updated": true
}
```

---

### 10. LLM Skill（大模型技能）

**功能：** 调用大语言模型

**输入参数：**
```json
{
  "prompt": "提示词",
  "model": "模型名称（可选）",
  "max_tokens": "最大 token 数",
  "temperature": "温度（0-1）"
}
```

**使用示例：**
```python
# 文本生成
result = await llm_skill.execute({
    "prompt": "写一首关于春天的诗",
    "max_tokens": 200,
    "temperature": 0.7
})
```

**返回结果：**
```json
{
  "success": true,
  "content": "生成的文本",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50
  }
}
```

---

### 11. Self Improvement Skill（自我提升技能）

**功能：** 从经验中学习和总结

**输入参数：**
```json
{
  "action": "learn|summary|get_learnings",
  "experience": "经验内容（learn 时）",
  "task_id": "任务 ID（可选）"
}
```

**使用示例：**
```python
# 学习经验
result = await self_improvement_skill.execute({
    "action": "learn",
    "experience": "使用 git rebase 时需要注意先备份分支"
})
```

**返回结果：**
```json
{
  "success": true,
  "learning_id": "learn_...",
  "category": "git",
  "importance": 0.9
}
```

---

## 🔧 技能开发指南

### 创建自定义技能

**1. 继承 BaseSkill：**

```python
from ymcode.skills.base import BaseSkill
from typing import Dict, Any

class MyCustomSkill(BaseSkill):
    """我的自定义技能"""
    
    def __init__(self):
        super().__init__(name="my_custom_skill")
    
    @property
    def description(self) -> str:
        return "我的自定义技能描述"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        # 实现技能逻辑
        result = f"处理：{arguments['param1']}"
        return {"success": True, "result": result}
```

**2. 注册技能：**

```python
from ymcode.skills import get_registry

registry = get_registry()
registry.register(MyCustomSkill())
```

**3. 使用技能：**

```python
from ymcode.skills import get_all_skills

skills = get_all_skills()
result = await skills['my_custom_skill'].execute({
    "param1": "test"
})
```

---

## 📊 技能性能指标

| 技能 | 平均响应时间 | 成功率 | 使用频率 |
|------|-------------|--------|---------|
| memory | 50ms | 99% | 高 |
| shell | 200ms | 95% | 高 |
| search | 500ms | 98% | 中 |
| http | 800ms | 97% | 中 |
| code_analysis | 100ms | 99% | 高 |
| database | 150ms | 96% | 中 |
| formatter | 80ms | 99% | 高 |
| docker | 300ms | 90% | 低 |
| chat | 3000ms | 99% | 高 |
| llm | 3000ms | 99% | 高 |
| self_improvement | 100ms | 99% | 中 |

---

## 🎯 最佳实践

### 1. 错误处理

```python
try:
    result = await skill.execute(params)
    if not result.get('success'):
        logger.error(f"技能执行失败：{result.get('error')}")
except Exception as e:
    logger.error(f"技能执行异常：{e}")
    return {"success": False, "error": str(e)}
```

### 2. 超时控制

```python
import asyncio

async def execute_with_timeout(skill, params, timeout=30):
    try:
        return await asyncio.wait_for(
            skill.execute(params),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout"}
```

### 3. 参数验证

```python
from jsonschema import validate

def validate_params(skill, params):
    schema = skill.get_input_schema()
    try:
        validate(instance=params, schema=schema)
        return True
    except Exception as e:
        return False
```

---

## 📝 更新日志

### v0.5.0 (2026-03-16)

- ✅ 11 个内置技能全部完成
- ✅ MCP 协议集成
- ✅ 技能市场框架
- ✅ OpenClaw 桥接

### v0.3.5 (2026-03-16)

- ✅ 技能注册表优化
- ✅ 错误处理增强
- ✅ 性能提升

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
