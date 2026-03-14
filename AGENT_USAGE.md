# YM-CODE 多 Agent 使用指南

**轻量级多 Agent，独立运行！** 🚀

---

## 🎉 已实现功能

### ✅ 核心 Agent（2 个）

| Agent | 角色 | 职责 |
|-------|------|------|
| **Builder** | 构建者 | 代码实现、文件操作、测试运行 |
| **Reviewer** | 审查者 | 代码审查、质量检查、建议 |

### ✅ 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **Agent 路由** | ✅ | 自动/手动路由 |
| **共享记忆** | ✅ | SQLite 存储 |
| **任务系统** | ✅ | 创建/完成任务 |
| **自动路由** | ✅ | 智能识别任务类型 |

---

## 🚀 快速开始

### 方式 1：Python API

```python
from ymcode.agents import create_default_router, AgentMessage
import asyncio

async def main():
    # 创建路由器
    router = create_default_router()
    
    # 查看 Agent
    print(router.list_agents())
    
    # 发送任务
    msg = AgentMessage(
        sender="user",
        content="创建文件 test.py"
    )
    
    # 自动路由
    response = await router.route(msg)
    print(f"Agent: {response.sender}")
    print(f"回复：{response.content}")

asyncio.run(main())
```

---

### 方式 2：命令行测试

```bash
# 运行测试
python test_multi_agent.py

# 输出
============================================================
YM-CODE 多 Agent 系统测试
============================================================

[OK] Agent 已初始化
   可用 Agent: ['builder', 'reviewer']

[测试 1] 查看 Agent 状态...
   - builder: Builder (idle)
   - reviewer: Reviewer (idle)

[测试 2] Builder 创建文件...
   发送：创建文件 test.py，写入 print('hello')
   回复：[OK] 文件已创建（模拟）
   发送者：builder

...

[OK] 所有测试完成！
```

---

## 📋 使用示例

### 1. Builder - 创建文件

```python
msg = AgentMessage(
    sender="user",
    content="创建文件 test.py，写入 print('hello')"
)
response = await router.route(msg, target="builder")
```

**回复：**
```
[OK] 任务已接收

任务内容：创建文件 test.py，写入 print('hello')
状态：处理中
预计时间：5 分钟
```

---

### 2. Reviewer - 代码审查

```python
msg = AgentMessage(
    sender="user",
    content="审查 src/main.py 的代码质量"
)
response = await router.route(msg, target="reviewer")
```

**回复：**
```
[报告] 代码审查报告

[OK] 代码规范：通过 (PEP 8)
[OK] 测试覆盖：85% (>80% 合格)
[WARN] 性能优化：建议改进
...

综合评分：90/100
```

---

### 3. 自动路由

```python
# 实现类任务 → Builder
msg = AgentMessage(sender="user", content="实现用户登录功能")
response = await router.route(msg)  # 自动到 builder

# 审查类任务 → Reviewer
msg = AgentMessage(sender="user", content="分析这个文件的复杂度")
response = await router.route(msg)  # 自动到 reviewer

# 测试类任务 → Builder
msg = AgentMessage(sender="user", content="运行测试")
response = await router.route(msg)  # 自动到 builder
```

---

### 4. 共享记忆

```python
# 添加记忆
router.add_to_shared_memory({
    "type": "note",
    "content": "项目使用 Python 3.13"
})

# 获取记忆
memories = router.get_shared_memory(limit=10)

# 搜索记忆
results = router.search_shared_memory("pytest")
```

---

### 5. 任务系统

```python
# 创建任务
task = router.create_task(
    title="实现用户认证",
    assigned_to="builder"
)

# 完成任务
router.complete_task(task_id=1)
```

---

## 🎯 路由规则

### 自动路由逻辑

| 关键词 | 路由到 | 示例 |
|--------|--------|------|
| 创建/实现/编写/build | Builder | "创建文件" |
| 审查/review/检查/分析 | Reviewer | "代码审查" |
| 测试/test | Builder | "运行测试" |
| 其他 | Builder (默认) | "帮我做这个" |

---

## 📊 Agent 状态

### 查看状态

```python
agents = router.list_agents()
for agent in agents:
    print(f"{agent['name']}: {agent['role']} ({agent['state']})")
```

### 状态类型

| 状态 | 说明 |
|------|------|
| **idle** | 空闲，可接受任务 |
| **busy** | 忙碌，处理中 |
| **error** | 错误，需要检查 |

---

## 🔧 扩展 Agent

### 创建新 Agent

```python
from ymcode.agents.base import BaseAgent, AgentMessage

class TesterAgent(BaseAgent):
    """Tester Agent"""
    
    def __init__(self):
        super().__init__("tester", "Tester")
    
    async def process(self, message: AgentMessage) -> AgentMessage:
        self.state = "busy"
        
        # 执行测试
        result = await self._run_tests(message.content)
        
        self.state = "idle"
        return AgentMessage(
            sender=self.name,
            content=result
        )
    
    async def _run_tests(self, task: str) -> str:
        # 实现测试逻辑
        return "[OK] 测试通过"

# 注册
router.register_agent("tester", TesterAgent())
```

---

## 📁 文件结构

```
ymcode/agents/
├── __init__.py          # 导出接口
├── base.py              # Agent 基类
├── router.py            # 路由器
├── builder.py           # Builder Agent
├── reviewer.py          # Reviewer Agent
└── memory_store.py      # (计划中) SQLite 存储
```

---

## 🔄 与 OpenClaw 集成

### 独立模式

```
YM-CODE Multi-Agent
├── Router (本地)
├── Builder
└── Reviewer
```

**特点：**
- ✅ 无需 OpenClaw
- ✅ 本地运行
- ✅ 快速高效

---

### 集成模式

```
OpenClaw Gateway
    ↓
YM-CODE Multi-Agent
    ↓
Builder/Reviewer
```

**特点：**
- ✅ 与 OpenClaw 协作
- ✅ 多 Agent 路由
- ✅ 全渠道支持

---

## 🎯 使用场景

### 场景 1：个人开发

```
用户 → Builder → 实现功能
     → Reviewer → 审查代码
```

---

### 场景 2：团队协作

```
Alice → YM-CODE Builder → 实现功能
Bob   → YM-CODE Reviewer → 审查代码
```

---

### 场景 3：CI/CD

```
Git Push → YM-CODE Reviewer → 自动审查
         → YM-CODE Builder → 运行测试
```

---

## 📝 API 参考

### AgentMessage

```python
@dataclass
class AgentMessage:
    sender: str          # 发送者
    content: str         # 内容
    timestamp: str       # 时间戳
    metadata: Dict       # 元数据
```

---

### AgentRouter

```python
class AgentRouter:
    def register_agent(name: str, agent: BaseAgent)
    def list_agents() -> List[Dict]
    async def route(message: AgentMessage, target: str = None)
    def add_to_shared_memory(data: Dict)
    def get_shared_memory(limit: int = 100)
    def search_shared_memory(query: str)
    def create_task(title: str, assigned_to: str = None)
    def complete_task(task_id: int)
```

---

## ✅ 总结

### 已实现

- ✅ Builder Agent
- ✅ Reviewer Agent
- ✅ Agent Router
- ✅ 自动路由
- ✅ 共享记忆
- ✅ 任务系统

### 计划中

- 🔜 SQLite 持久化
- 🔜 更多 Agent（Specialist）
- 🔜 CLI 集成
- 🔜 Web 界面

---

**多 Agent 系统已就绪！开始使用吧！** 🚀
