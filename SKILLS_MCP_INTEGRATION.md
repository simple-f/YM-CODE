# Skills + MCP 集成指南

> 核心 Skills 与 MCP 协议完美融合

---

## ✅ 完成状态

| 功能 | 状态 | 说明 |
|------|------|------|
| **Skills 基类** | ✅ 完成 | BaseSkill 抽象类 |
| **自我提升技能** | ✅ 完成 | SelfImprovementSkill |
| **MCP Skills Server** | ✅ 完成 | SkillsMCPServer |
| **工具暴露** | ✅ 完成 | Skills → MCP Tools |
| **测试验证** | ✅ 完成 | 全部通过 |

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────┐
│         YM-CODE Agent               │
├─────────────────────────────────────┤
│  核心 Skills (本地实现)             │
│  ┌─────────────────────────────┐   │
│  │ SelfImprovementSkill        │   │
│  │ - 自我总结                  │   │
│  │ - 自我提升                  │   │
│  │ - 知识库查询                │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ MemorySkill (待实现)        │   │
│  │ - 记忆管理                  │   │
│  │ - 上下文管理                │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│  MCP Layer (统一接口)               │
│  ┌─────────────────────────────┐   │
│  │ SkillsMCPServer             │   │
│  │ - skill_self_improvement    │   │
│  │ - skill_memory              │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│  MCP Client (外部扩展)              │
│  - filesystem                      │
│  - database                        │
│  - github                          │
│  - ...                             │
└─────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 创建技能

```python
from ymcode.skills.base import BaseSkill

class MyCustomSkill(BaseSkill):
    """自定义技能"""
    
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
        return {"result": "success"}
```

### 2. 注册到 MCP

```python
from ymcode.mcp.skills_server import SkillsMCPServer

# 创建技能
skill = MyCustomSkill()

# 创建 MCP Server
mcp_server = SkillsMCPServer({
    "my_custom": skill
})

# 获取工具定义
tools_def = mcp_server.get_tools_definition()
```

### 3. 集成到 Agent

```python
from ymcode.core.agent import Agent
from ymcode.skills.self_improvement import SelfImprovementSkill
from ymcode.mcp.skills_server import SkillsMCPServer

# 创建 Agent
agent = Agent()

# 创建核心 Skills
skills = {
    "self_improvement": SelfImprovementSkill()
}

# 创建 MCP Skills Server
mcp_server = SkillsMCPServer(skills)

# 将 MCP 工具注册到 Agent
for tool_def in mcp_server.get_tools_definition():
    agent.tools.register_mcp_tool(tool_def)

# 现在 Agent 可以使用 Skills
result = await agent.run("请总结一下刚才的对话")
```

---

## 📊 已实现 Skills

### SelfImprovementSkill

**功能：**
- ✅ 自我总结
- ✅ 自我提升
- ✅ 知识库查询
- ✅ 数据持久化

**操作：**

```python
# 自我总结
await mcp_server.call_tool("skill_self_improvement", {
    "action": "summary",
    "session_id": "session_123"
})

# 自我提升
await mcp_server.call_tool("skill_self_improvement", {
    "action": "improve",
    "skill_name": "conversation",
    "feedback": "回答很详细"
})

# 查询知识库
await mcp_server.call_tool("skill_self_improvement", {
    "action": "query",
    "query": "conversation"
})

# 重置数据
await mcp_server.call_tool("skill_self_improvement", {
    "action": "reset"
})
```

---

## 🎯 待实现 Skills

### MemorySkill（待实现）

```python
class MemorySkill(BaseSkill):
    """记忆技能"""
    
    @property
    def description(self) -> str:
        return "记忆管理和上下文管理"
    
    async def execute(self, arguments: Dict) -> Any:
        action = arguments.get("action")
        
        if action == "save":
            return await self.save_memory(arguments)
        elif action == "load":
            return await self.load_memory(arguments)
        elif action == "search":
            return await self.search_memory(arguments)
        else:
            return {"error": "未知操作"}
```

### LearningSkill（待实现）

```python
class LearningSkill(BaseSkill):
    """学习技能"""
    
    @property
    def description(self) -> str:
        return "从经验中学习和改进"
```

---

## 💡 最佳实践

### 1. 技能设计原则

- ✅ **单一职责** - 一个技能只做一件事
- ✅ **无状态优先** - 尽量无状态，便于扩展
- ✅ **持久化** - 重要数据要持久化
- ✅ **错误处理** - 完善的错误处理

### 2. MCP 集成

- ✅ **统一命名** - `skill_{skill_name}`
- ✅ **完整描述** - 清晰的工具描述
- ✅ **Schema 验证** - 严格的输入验证
- ✅ **日志记录** - 完善的日志

### 3. 性能优化

- ✅ **缓存** - 频繁访问的数据缓存
- ✅ **异步** - 使用异步 IO
- ✅ **批量** - 批量操作减少 IO
- ✅ **懒加载** - 按需加载数据

---

## 🐛 故障排查

### 问题 1：技能未注册

**错误：** `技能不存在：xxx`

**解决：**
```python
# 检查技能是否注册
print(mcp_server.get_status())

# 重新注册
mcp_server.add_skill("name", skill)
```

### 问题 2：工具调用失败

**错误：** `工具调用失败`

**解决：**
```python
# 检查工具名称
print(mcp_server.get_tools_definition())

# 检查参数格式
print(skill.get_input_schema())
```

### 问题 3：数据未持久化

**解决：**
```python
# 检查数据目录
from pathlib import Path
data_dir = Path.home() / ".ymcode" / "skills"
print(data_dir.exists())

# 手动保存
skill._save_data()
```

---

## 📖 参考资料

- [MCP 官方文档](https://github.com/anthropics/mcp)
- [Skills 基类](./ymcode/skills/base.py)
- [SelfImprovementSkill](./ymcode/skills/self_improvement.py)
- [SkillsMCPServer](./ymcode/mcp/skills_server.py)

---

_最后更新：2026-03-13_

_作者：YM-CODE Team_
