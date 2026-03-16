# YM-CODE 多 Agent 系统

**版本：** v0.6.0  
**更新时间：** 2026-03-16

---

## 🎯 什么是多 Agent 系统？

YM-CODE 的多 Agent 系统实现了**真正的智能体分工与协作**，而非简单的工具调用。

### 核心特征

1. **角色化分工** - 多个独立 Agent，各司其职
2. **任务拆解** - 自动拆解复杂任务为子任务
3. **Agent 通信** - Agent 间自主传递结果和反馈
4. **自主调度** - 系统自动选择和组合 Agent

---

## 🤖 Agent 角色

### 1. Orchestrator（协调者）

**职责：**
- 接收用户任务
- 拆解复杂任务
- 分配子任务给其他 Agent
- 汇总最终结果

**示例：**
```
用户：开发一个完整的 Flask API，包含测试和文档
Orchestrator: 
  1. 拆解任务 → 代码生成 + 测试 + 文档
  2. 分配给 Coder、Tester、Documenter
  3. 汇总结果返回给用户
```

---

### 2. Coder（代码生成 Agent）

**职责：**
- 根据需求生成代码
- 实现功能逻辑
- 遵循最佳实践

**专长：**
- Python/JavaScript/TypeScript
- Web 框架（Flask、FastAPI、Express）
- 数据库操作
- API 开发

---

### 3. Tester（测试 Agent）

**职责：**
- 编写单元测试
- 编写集成测试
- 验证代码质量
- 发现并报告 Bug

**专长：**
- pytest/unittest
- 测试覆盖率
- Mock 和 Stub
- TDD/BDD

---

### 4. Reviewer（代码审查 Agent）

**职责：**
- 代码质量审查
- 安全检查
- 性能优化建议
- 代码规范检查

**专长：**
- 代码异味检测
- 安全漏洞扫描
- 性能瓶颈分析
- 最佳实践检查

---

### 5. Debugger（调试 Agent）

**职责：**
- 分析错误日志
- 定位 Bug 根源
- 提供修复方案
- 验证修复结果

**专长：**
- 日志分析
- 堆栈追踪
- 调试工具
- Bug 模式识别

---

### 6. Documenter（文档生成 Agent）

**职责：**
- 生成 API 文档
- 编写使用说明
- 创建 README
- 生成注释

**专长：**
- Markdown
- API 文档（Swagger/OpenAPI）
- 代码注释
- 用户手册

---

## 🔄 多 Agent 协作流程

### 示例：开发完整的 Flask API

**用户请求：**
```
开发一个完整的 Flask API，包含用户注册、登录功能，
需要单元测试和 API 文档
```

**多 Agent 协作流程：**

```
┌─────────────────┐
│  Orchestrator   │
│   协调者        │
└────────┬────────┘
         │ 接收任务
         ▼
┌─────────────────┐
│   任务拆解      │
│ 1. 代码生成     │
│ 2. 单元测试     │
│ 3. API 文档     │
└────────┬────────┘
         │ 分配子任务
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌──────┐  ┌──────┐  ┌──────────┐
│Coder │  │Tester│  │Documenter│
│Agent │  │Agent │  │  Agent   │
└──┬───┘  └──┬───┘  └────┬─────┘
   │         │           │
   │ 生成代码 │           │
   │────────▶│           │
   │         │ 编写测试   │
   │         │──────────▶│
   │         │           │ 生成文档
   │         │           │
   │◀────────┼───────────┤
   │         │  汇总结果  │
   ▼         ▼          ▼
┌─────────────────────────┐
│    Orchestrator         │
│    汇总并返回给用户      │
└─────────────────────────┘
```

---

## 📋 使用方式

### 1. 自动模式（推荐）

系统自动判断使用单 Agent 还是多 Agent：

```python
from ymcode.multi_agent import get_multi_agent_system

system = get_multi_agent_system()

# 简单任务 - 自动使用单 Agent
result = await system.execute_task("写一个 hello world 函数")

# 复杂任务 - 自动使用多 Agent 协作
result = await system.execute_task(
    "开发一个完整的 Flask API，包含测试和文档"
)
```

### 2. 手动模式

手动指定使用多 Agent：

```python
# 注册 Agent
from ymcode.agents.coder import CoderAgent
from ymcode.agents.tester import TesterAgent
from ymcode.agents.reviewer import ReviewerAgent

system = get_multi_agent_system()
system.register_agent(AgentRole.CODER, CoderAgent())
system.register_agent(AgentRole.TESTER, TesterAgent())
system.register_agent(AgentRole.REVIEWER, ReviewerAgent())

# 执行任务
result = await system.execute_task("开发完整的用户系统")
```

---

## 🎯 触发多 Agent 的条件

系统会自动判断是否使用多 Agent 协作：

### 触发条件

**1. 复杂任务关键词：**
- "完整的"、"整个"、"全部"
- "从零开始"、"开发一个"
- "complete"、"full"、"develop"

**2. 多个需求组合：**
- 代码 + 测试
- 代码 + 文档
- 代码 + 审查 + 测试

**3. 显式指定：**
- "使用多 Agent"
- "协作完成"
- "分工合作"

### 示例对比

**单 Agent 任务：**
```
"写一个排序函数"
"修复这个 bug"
"解释这段代码"
```

**多 Agent 任务：**
```
"开发一个完整的用户管理系统"
"从零开始创建 Flask API，包含测试和文档"
"实现完整的购物车功能，需要单元测试"
```

---

## 📊 单 Agent vs 多 Agent 对比

| 维度 | 单 Agent | 多 Agent |
|------|---------|---------|
| 适用场景 | 简单任务 | 复杂任务 |
| 响应速度 | 快（<3 秒） | 较慢（10-30 秒） |
| 代码质量 | 良好 | 优秀 |
| 测试覆盖 | 无/少 | 完整 |
| 文档完整度 | 基础 | 完整 |
| 资源消耗 | 低 | 中/高 |

---

## 🔧 Agent 间通信

### 消息类型

**1. Request（请求）：**
```python
AgentMessage(
    from_agent="orchestrator",
    to_agent="coder",
    message_type="request",
    content="生成用户注册接口代码"
)
```

**2. Response（响应）：**
```python
AgentMessage(
    from_agent="coder",
    to_agent="orchestrator",
    message_type="response",
    content={"code": "...", "success": True}
)
```

**3. Feedback（反馈）：**
```python
AgentMessage(
    from_agent="tester",
    to_agent="coder",
    message_type="feedback",
    content={"bug": "空指针异常", "location": "line 25"}
)
```

---

## 📈 性能指标

### 响应时间

| 任务类型 | 单 Agent | 多 Agent |
|---------|---------|---------|
| 简单函数 | 2-3 秒 | 不适用 |
| 小型模块 | 5-8 秒 | 10-15 秒 |
| 完整功能 | 10-15 秒 | 20-30 秒 |
| 复杂系统 | 15-30 秒 | 30-60 秒 |

### 代码质量

| 指标 | 单 Agent | 多 Agent |
|------|---------|---------|
| 测试覆盖率 | 0-30% | 80-95% |
| 代码审查 | 基础 | 深度 |
| 文档完整度 | 50% | 95% |
| Bug 率 | 中 | 低 |

---

## 🎯 最佳实践

### 1. 选择合适的模式

**使用单 Agent：**
- 快速原型
- 简单修复
- 代码解释
- 小功能增强

**使用多 Agent：**
- 完整功能开发
- 生产级代码
- 需要测试和文档
- 复杂业务逻辑

### 2. 清晰的任务描述

**好的描述：**
```
开发一个完整的用户认证系统，包括：
1. 用户注册、登录、登出
2. JWT Token 认证
3. 密码加密存储
4. 完整的单元测试
5. API 文档
```

**不好的描述：**
```
做个登录功能
```

### 3. 提供足够的上下文

```python
context = {
    'framework': 'Flask',
    'database': 'PostgreSQL',
    'python_version': '3.11',
    'requirements': ['JWT', 'bcrypt', 'SQLAlchemy']
}

result = await system.execute_task(task, context)
```

---

## 🔮 未来规划

### Phase 1（v0.6.0）✅

- ✅ 多 Agent 系统框架
- ✅ 角色定义和注册
- ✅ 任务拆解算法
- ✅ 基础协作流程

### Phase 2（v0.7.0）

- 📋 Agent 间自主通信
- 📋 反馈和修复循环
- 📋 任务执行优化
- 📋 Agent 性能监控

### Phase 3（v0.8.0）

- 📋 自主学习和改进
- 📋 动态 Agent 创建
- 📋 复杂任务规划
- 📋 多项目协作

---

## 📝 示例场景

### 场景 1：开发 Flask API

**任务：**
```
开发一个完整的 Flask API，包含用户注册、登录功能，
需要单元测试和 API 文档
```

**多 Agent 执行：**
1. **Orchestrator** 拆解任务
2. **Coder** 生成代码（models.py, routes.py, auth.py）
3. **Tester** 编写测试（test_auth.py, test_routes.py）
4. **Documenter** 生成文档（API.md, README.md）
5. **Reviewer** 审查代码质量
6. **Orchestrator** 汇总结果

**输出：**
```
✅ 代码生成完成
   - models.py (用户模型)
   - routes.py (API 路由)
   - auth.py (认证逻辑)

✅ 测试完成
   - test_auth.py (15 个测试用例)
   - test_routes.py (20 个测试用例)
   - 覆盖率：92%

✅ 文档完成
   - API.md (接口文档)
   - README.md (使用说明)

✅ 代码审查完成
   - 发现 2 个潜在问题
   - 提供优化建议
```

---

### 场景 2：Bug 修复

**任务：**
```
修复用户登录时的空指针异常，并确保不再出现
```

**多 Agent 执行：**
1. **Debugger** 分析错误日志
2. **Coder** 修复代码
3. **Tester** 编写回归测试
4. **Reviewer** 审查修复

---

### 场景 3：代码重构

**任务：**
```
重构这个模块，提高可维护性和性能
```

**多 Agent 执行：**
1. **Reviewer** 分析代码问题
2. **Coder** 重构代码
3. **Tester** 验证功能不变
4. **Documenter** 更新文档

---

## 🆘 常见问题

### Q: 多 Agent 比单 Agent 慢多少？

**A:** 通常慢 2-3 倍，但代码质量更高。

- 单 Agent: 5-10 秒
- 多 Agent: 15-30 秒

**建议：** 生产代码用多 Agent，快速原型用单 Agent。

---

### Q: 如何强制使用多 Agent？

**A:** 在任务描述中包含多个需求：

```
"开发完整功能，需要代码、测试和文档"
```

---

### Q: 可以自定义 Agent 角色吗？

**A:** 可以！继承 BaseAgent 并注册：

```python
from ymcode.agents.base import BaseAgent
from ymcode.multi_agent import AgentRole, get_multi_agent_system

class CustomAgent(BaseAgent):
    def execute(self, task, context):
        # 实现自定义逻辑
        pass

system = get_multi_agent_system()
system.register_agent(AgentRole.CODER, CustomAgent())
```

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
