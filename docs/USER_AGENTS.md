# 用户自定义 Agent 指南

**版本：** v0.6.0  
**更新时间：** 2026-03-16

---

## 🎯 设计理念

**YM-CODE 不预设 Agent，而是提供框架让用户自己创建！**

你可以：
- ✅ 创建任意角色的 Agent
- ✅ 定义专属能力
- ✅ 实现自定义逻辑
- ✅ 组合多个 Agent 协作

---

## 🚀 快速开始

### 1. 创建简单的 Agent

```python
from ymcode.agents import create_agent, get_agent_registry

# 创建代码生成 Agent
coder = create_agent(
    name="PythonCoder",
    role="code_generator",
    description="专注于 Python 代码生成",
    capabilities=["python", "fastapi", "sqlalchemy"]
)

# 注册 Agent
registry = get_agent_registry()
registry.register(coder)
```

### 2. 创建带自定义逻辑的 Agent

```python
async def my_execute_func(task: str, context: dict):
    """自定义执行逻辑"""
    # 这里写你的业务逻辑
    result = f"完成任务：{task}"
    return {
        "success": True,
        "result": result,
        "metadata": {"custom": "data"}
    }

# 创建 Agent 并指定执行函数
agent = create_agent(
    name="MyCustomAgent",
    role="custom",
    description="我的自定义 Agent",
    capabilities=["custom_logic"],
    execute_func=my_execute_func
)

registry.register(agent)
```

### 3. 继承 BaseAgent 创建复杂 Agent

```python
from ymcode.agents.base import BaseAgent

class CodeReviewAgent(BaseAgent):
    """代码审查 Agent"""
    
    def __init__(self):
        super().__init__(
            name="CodeReviewer",
            description="专业代码审查，发现潜在问题"
        )
    
    @property
    def role(self) -> str:
        return "reviewer"
    
    @property
    def capabilities(self) -> list:
        return ["code_review", "security", "performance", "best_practices"]
    
    async def execute(self, task: str, context: dict = None):
        """执行代码审查"""
        code = context.get('code', '') if context else ''
        
        # 实现审查逻辑
        issues = []
        
        # 检查 1: 代码规范
        if len(code.split('\n')) > 100:
            issues.append("文件过长，建议拆分")
        
        # 检查 2: 安全问题
        if 'eval(' in code:
            issues.append("使用 eval() 存在安全风险")
        
        # 检查 3: 性能问题
        # ... 更多检查
        
        return {
            "success": True,
            "issues": issues,
            "suggestions": ["建议 1", "建议 2"],
            "score": 85
        }

# 注册 Agent
reviewer = CodeReviewAgent()
registry.register(reviewer)
```

---

## 📋 Agent 角色示例

### 1. 代码生成 Agent

```python
coder = create_agent(
    name="FastAPICoder",
    role="code_generator",
    description="FastAPI 代码生成专家",
    capabilities=["python", "fastapi", "pydantic", "asyncio"]
)
```

### 2. 测试 Agent

```python
tester = create_agent(
    name="TestExpert",
    role="tester",
    description="单元测试和集成测试专家",
    capabilities=["pytest", "unittest", "mocking", "tdd"]
)
```

### 3. 调试 Agent

```python
debugger = create_agent(
    name="BugHunter",
    role="debugger",
    description="Bug 定位和修复专家",
    capabilities=["debugging", "log_analysis", "error_tracking"]
)
```

### 4. 文档 Agent

```python
documenter = create_agent(
    name="DocWriter",
    role="documenter",
    description="技术文档生成专家",
    capabilities=["markdown", "api_docs", "readme", "comments"]
)
```

### 5. 安全审计 Agent

```python
security_auditor = create_agent(
    name="SecurityAuditor",
    role="security_auditor",
    description="安全漏洞扫描和审计",
    capabilities=["security", "vulnerability_scan", "owasp", "encryption"]
)
```

### 6. 性能优化 Agent

```python
optimizer = create_agent(
    name="PerformanceOptimizer",
    role="optimizer",
    description="性能分析和优化专家",
    capabilities=["performance", "profiling", "optimization", "caching"]
)
```

---

## 🔄 多 Agent 协作

### 示例：完整开发流程

```python
from ymcode.agents import create_agent, get_agent_registry
from ymcode.multi_agent import MultiAgentSystem

# 1. 创建 Agent 团队
coder = create_agent(
    name="PythonCoder",
    role="code_generator",
    description="Python 代码生成",
    capabilities=["python", "fastapi"]
)

tester = create_agent(
    name="TestExpert",
    role="tester",
    description="测试编写",
    capabilities=["pytest", "unittest"]
)

reviewer = create_agent(
    name="CodeReviewer",
    role="reviewer",
    description="代码审查",
    capabilities=["code_review", "best_practices"]
)

documenter = create_agent(
    name="DocWriter",
    role="documenter",
    description="文档生成",
    capabilities=["markdown", "api_docs"]
)

# 2. 注册 Agent
registry = get_agent_registry()
registry.register(coder)
registry.register(tester)
registry.register(reviewer)
registry.register(documenter)

# 3. 创建多 Agent 系统
system = MultiAgentSystem()
system.register_agent("code_generator", coder)
system.register_agent("tester", tester)
system.register_agent("reviewer", reviewer)
system.register_agent("documenter", documenter)

# 4. 执行复杂任务
task = "开发一个完整的用户认证 API，包含测试和文档"
result = await system.execute_task(task)

# result 包含：
# - code: 生成的代码
# - tests: 测试用例
# - review: 审查意见
# - documentation: API 文档
```

---

## 💡 最佳实践

### 1. 单一职责

每个 Agent 专注于一个特定领域：

```python
# ✅ 好的设计
create_agent(name="PythonCoder", role="code_generator", ...)
create_agent(name="TestExpert", role="tester", ...)

# ❌ 不好的设计
create_agent(
    name="DoEverything",
    role="everything",  # 太宽泛
    capabilities=["coding", "testing", "reviewing", "documenting"]
)
```

### 2. 明确能力边界

```python
# ✅ 清晰的能力定义
tester = create_agent(
    name="PythonTester",
    role="tester",
    description="Python 单元测试专家",
    capabilities=["pytest", "unittest", "mocking"]  # 具体明确
)

# ❌ 模糊的能力定义
tester = create_agent(
    name="Tester",
    role="tester",
    description="测试人员",
    capabilities=["testing"]  # 太模糊
)
```

### 3. 提供详细描述

```python
# ✅ 好的描述
create_agent(
    name="FastAPICoder",
    role="code_generator",
    description="专注于 FastAPI 框架的代码生成，包括路由、模型、中间件等",
    capabilities=["python", "fastapi", "pydantic", "asyncio", "sqlalchemy"]
)

# ❌ 差的描述
create_agent(
    name="Coder",
    role="code_generator",
    description="写代码",
    capabilities=["coding"]
)
```

### 4. 实现错误处理

```python
class RobustAgent(BaseAgent):
    """健壮的 Agent，包含错误处理"""
    
    async def execute(self, task: str, context: dict = None):
        try:
            # 执行任务
            result = await self._do_work(task, context)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _do_work(self, task: str, context: dict):
        # 具体实现
        pass
```

---

## 📊 Agent 管理

### 列出所有 Agent

```python
registry = get_agent_registry()

# 列出所有
all_agents = registry.list_agents()

# 按角色筛选
coders = registry.list_agents(role="code_generator")
testers = registry.list_agents(role="tester")

# 获取数量
count = registry.count()
```

### 查询 Agent 信息

```python
registry = get_agent_registry()

# 获取特定 Agent
agent = registry.get("PythonCoder")

# 获取 Agent 信息
info = agent.to_dict()
# {
#     "name": "PythonCoder",
#     "role": "code_generator",
#     "description": "...",
#     "capabilities": [...],
#     "enabled": True
# }
```

### 启用/禁用 Agent

```python
agent = registry.get("PythonCoder")

# 禁用
agent.enabled = False

# 启用
agent.enabled = True
```

### 注销 Agent

```python
registry = get_agent_registry()
registry.unregister("PythonCoder")
```

---

## 🎯 实际应用场景

### 场景 1：团队开发

```python
# 为团队创建专属 Agent 团队

# 前端专家
frontend_dev = create_agent(
    name="FrontendExpert",
    role="frontend_developer",
    description="React/Vue 前端开发专家",
    capabilities=["react", "vue", "typescript", "css", "webpack"]
)

# 后端专家
backend_dev = create_agent(
    name="BackendExpert",
    role="backend_developer",
    description="Python/Go后端开发专家",
    capabilities=["python", "go", "fastapi", "gin", "postgresql"]
)

# DevOps 专家
devops = create_agent(
    name="DevOpsExpert",
    role="devops_engineer",
    description="CI/CD 和部署专家",
    capabilities=["docker", "kubernetes", "ci_cd", "aws", "terraform"]
)

# 注册
registry = get_agent_registry()
registry.register(frontend_dev)
registry.register(backend_dev)
registry.register(devops)
```

### 场景 2：代码审查流程

```python
# 创建多级审查 Agent

# 一级：代码规范审查
style_reviewer = create_agent(
    name="StyleReviewer",
    role="reviewer",
    description="代码规范审查（PEP8、命名等）",
    capabilities=["pep8", "naming", "formatting"]
)

# 二级：安全检查
security_reviewer = create_agent(
    name="SecurityReviewer",
    role="security_auditor",
    description="安全漏洞审查",
    capabilities=["security", "owasp", "vulnerability"]
)

# 三级：性能审查
perf_reviewer = create_agent(
    name="PerformanceReviewer",
    role="optimizer",
    description="性能优化建议",
    capabilities=["performance", "profiling", "optimization"]
)

# 注册
registry.register(style_reviewer)
registry.register(security_reviewer)
registry.register(perf_reviewer)

# 使用：代码提交时自动触发多级审查
```

### 场景 3：自动化测试

```python
# 创建测试 Agent 团队

unit_tester = create_agent(
    name="UnitTester",
    role="tester",
    description="单元测试专家",
    capabilities=["pytest", "unittest", "mocking"]
)

integration_tester = create_agent(
    name="IntegrationTester",
    role="tester",
    description="集成测试专家",
    capabilities=["integration_test", "api_test", "e2e"]
)

performance_tester = create_agent(
    name="PerformanceTester",
    role="tester",
    description="性能测试专家",
    capabilities=["load_test", "stress_test", "benchmark"]
)

registry.register(unit_tester)
registry.register(integration_tester)
registry.register(performance_tester)
```

---

## 🔧 高级功能

### 1. Agent 配置

```python
class ConfigurableAgent(BaseAgent):
    """可配置的 Agent"""
    
    def __init__(self, config: dict = None):
        super().__init__(name="ConfigurableAgent")
        self.config = config or {}
    
    async def execute(self, task: str, context: dict = None):
        # 根据配置调整行为
        if self.config.get('verbose'):
            logger.info(f"执行任务：{task}")
        
        if self.config.get('timeout'):
            result = await asyncio.wait_for(
                self._execute(task, context),
                timeout=self.config['timeout']
            )
        else:
            result = await self._execute(task, context)
        
        return result
```

### 2. Agent 组合

```python
class CompositeAgent(BaseAgent):
    """组合多个 Agent"""
    
    def __init__(self, name: str, agents: List[BaseAgent]):
        super().__init__(name)
        self.agents = agents
    
    async def execute(self, task: str, context: dict = None):
        results = []
        for agent in self.agents:
            result = await agent.execute(task, context)
            results.append(result)
        
        return {
            "success": all(r.get('success', False) for r in results),
            "results": results,
            "composite": True
        }
```

### 3. Agent 链

```python
class AgentChain(BaseAgent):
    """Agent 责任链"""
    
    def __init__(self, name: str, agents: List[BaseAgent]):
        super().__init__(name)
        self.agents = agents
    
    async def execute(self, task: str, context: dict = None):
        current_context = context or {}
        
        for agent in self.agents:
            result = await agent.execute(task, current_context)
            
            if not result.get('success'):
                return result
            
            # 将结果传递给下一个 Agent
            current_context[f'{agent.name}_result'] = result
        
        return {
            "success": True,
            "chain_completed": True,
            "final_context": current_context
        }
```

---

## 📝 常见问题

### Q: Agent 和 Skill 有什么区别？

**A:**
- **Skill（技能）** - 工具函数，被 Agent 调用
- **Agent（智能体）** - 有独立角色和决策能力

```python
# Skill: 工具函数
shell_skill.execute({"command": "ls -la"})

# Agent: 独立智能体
coder_agent.execute("生成一个 Flask API")
```

### Q: 如何持久化 Agent 配置？

**A:**

```python
import json

# 保存
registry = get_agent_registry()
agents_data = [a.to_dict() for a in registry.agents.values()]
with open('agents.json', 'w') as f:
    json.dump(agents_data, f)

# 加载
with open('agents.json', 'r') as f:
    agents_data = json.load(f)
for data in agents_data:
    agent = UserAgent(**data)
    registry.register(agent)
```

### Q: 可以在运行时动态创建 Agent 吗？

**A:** 可以！

```python
# 根据用户需求动态创建
def create_agent_for_task(task: str):
    if "测试" in task:
        return create_agent(
            name="DynamicTester",
            role="tester",
            capabilities=["pytest"]
        )
    elif "文档" in task:
        return create_agent(
            name="DynamicDocumenter",
            role="documenter",
            capabilities=["markdown"]
        )
```

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
