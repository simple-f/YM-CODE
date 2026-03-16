# 工作区与 Agent 选择指南

**版本：** v0.6.0  
**更新时间：** 2026-03-16

---

## 🎯 核心概念

### 1. 工作区（Workspace）

**每个工作区是独立的项目环境**，包含：
- 独立的 Agent 团队
- 独立的会话历史
- 独立的上下文信息

**使用场景：**
- 项目 A：电商系统开发
- 项目 B：数据分析工具
- 项目 C：学习 Python

---

### 2. Agent 选择

**每个工作区可以自定义加入哪些 Agent**：

```
项目 A（电商系统）:
  ✅ PythonCoder - 后端开发
  ✅ DatabaseDesigner - 数据库设计
  ✅ APIExpert - API 设计
  ✅ Tester - 测试

项目 B（数据分析）:
  ✅ DataAnalyst - 数据分析
  ✅ VisualizationExpert - 可视化
  ✅ JupyterExpert - Notebook

项目 C（学习 Python）:
  ✅ PythonTutor - 教学
  ✅ CodeReviewer - 代码审查
```

---

## 🚀 快速开始

### 1. 创建新工作区

```python
from ymcode.workspace import create_workspace, switch_workspace

# 创建新工作区
workspace = create_workspace(
    name="电商系统开发",
    description="开发完整的电商系统"
)

# 切换到这个工作区
switch_workspace(workspace.id)
```

### 2. 查看可用 Agent

```python
from ymcode.workspace import list_available_agents

agents = list_available_agents()
for agent in agents:
    print(f"{agent['name']} - {agent['role']}")
    print(f"  能力：{', '.join(agent['capabilities'])}")
```

### 3. 添加 Agent 到工作区

```python
from ymcode.workspace import add_agent_to_current_workspace
from ymcode.agents import create_agent

# 创建 Agent
coder = create_agent(
    name="PythonCoder",
    role="code_generator",
    description="Python 代码生成",
    capabilities=["python", "fastapi", "sqlalchemy"]
)

# 添加到当前工作区
add_agent_to_current_workspace(coder)
```

### 4. 查看工作区的 Agent

```python
from ymcode.workspace import list_workspace_agents

agents = list_workspace_agents()
print(f"当前工作区有 {len(agents)} 个 Agent:")
for agent in agents:
    print(f"  - {agent['name']} ({agent['role']})")
```

---

## 📋 完整流程示例

### 场景：启动新项目

```python
from ymcode.workspace import (
    create_workspace,
    switch_workspace,
    list_available_agents,
    add_agent_to_current_workspace,
    list_workspace_agents,
    get_current_workspace
)
from ymcode.agents import create_agent

# ========== 步骤 1: 创建新工作区 ==========
print("创建新项目工作区...")
workspace = create_workspace(
    name="Flask 电商系统",
    description="开发完整的 Flask 电商系统"
)

# 切换到新工作区
switch_workspace(workspace.id)
print(f"✓ 已切换到工作区：{workspace.name}")

# ========== 步骤 2: 选择需要的 Agent ==========
print("\n选择需要的 Agent...")

# 创建后端开发 Agent
backend_dev = create_agent(
    name="FlaskDeveloper",
    role="backend_developer",
    description="Flask 后端开发专家",
    capabilities=["flask", "python", "sqlalchemy", "jwt"]
)

# 创建数据库设计 Agent
db_designer = create_agent(
    name="DatabaseDesigner",
    role="database_designer",
    description="数据库设计专家",
    capabilities=["postgresql", "sqlalchemy", "database_design"]
)

# 创建测试 Agent
tester = create_agent(
    name="TestExpert",
    role="tester",
    description="测试专家",
    capabilities=["pytest", "unittest", "integration_test"]
)

# 创建文档 Agent
documenter = create_agent(
    name="DocWriter",
    role="documenter",
    description="文档编写专家",
    capabilities=["markdown", "api_docs", "readme"]
)

# ========== 步骤 3: 添加 Agent 到工作区 ==========
print("\n添加 Agent 到工作区...")
add_agent_to_current_workspace(backend_dev)
add_agent_to_current_workspace(db_designer)
add_agent_to_current_workspace(tester)
add_agent_to_current_workspace(documenter)

# ========== 步骤 4: 确认工作区配置 ==========
print("\n当前工作区的 Agent 团队:")
agents = list_workspace_agents()
for agent in agents:
    print(f"  ✅ {agent['name']} - {agent['role']}")
    print(f"     能力：{', '.join(agent['capabilities'])}")

# ========== 步骤 5: 开始工作 ==========
print("\n开始项目...")
current = get_current_workspace()
session = current.create_session("需求分析")

print(f"✓ 创建会话：{session['name']}")
print("准备就绪！可以开始分配任务了。")
```

**输出：**
```
创建新项目工作区...
✓ 已切换到工作区：Flask 电商系统

选择需要的 Agent...

添加 Agent 到工作区...

当前工作区的 Agent 团队:
  ✅ FlaskDeveloper - backend_developer
     能力：flask, python, sqlalchemy, jwt
  ✅ DatabaseDesigner - database_designer
     能力：postgresql, sqlalchemy, database_design
  ✅ TestExpert - tester
     能力：pytest, unittest, integration_test
  ✅ DocWriter - documenter
     能力：markdown, api_docs, readme

开始项目...
✓ 创建会话：需求分析
准备就绪！可以开始分配任务了。
```

---

## 🎯 不同项目的 Agent 配置

### 项目 1：Web 应用开发

```python
# 创建工作区
workspace = create_workspace("SaaS 平台开发")
switch_workspace(workspace.id)

# 添加 Agent
agents = [
    create_agent("FrontendDev", "frontend_developer", 
                 capabilities=["react", "typescript", "tailwind"]),
    
    create_agent("BackendDev", "backend_developer",
                 capabilities=["python", "fastapi", "postgresql"]),
    
    create_agent("DevOps", "devops_engineer",
                 capabilities=["docker", "kubernetes", "ci_cd"]),
    
    create_agent("Tester", "tester",
                 capabilities=["pytest", "e2e_test", "load_test"]),
]

for agent in agents:
    add_agent_to_current_workspace(agent)
```

---

### 项目 2：数据分析

```python
# 创建工作区
workspace = create_workspace("销售数据分析")
switch_workspace(workspace.id)

# 添加 Agent
agents = [
    create_agent("DataAnalyst", "data_analyst",
                 capabilities=["pandas", "numpy", "statistics"]),
    
    create_agent("VisualizationExpert", "visualization_expert",
                 capabilities=["matplotlib", "seaborn", "plotly"]),
    
    create_agent("MLEngineer", "ml_engineer",
                 capabilities=["sklearn", "tensorflow", "prediction"]),
    
    create_agent("ReportWriter", "report_writer",
                 capabilities=["report", "insights", "presentation"]),
]

for agent in agents:
    add_agent_to_current_workspace(agent)
```

---

### 项目 3：学习 Python

```python
# 创建工作区
workspace = create_workspace("Python 学习")
switch_workspace(workspace.id)

# 添加 Agent
agents = [
    create_agent("PythonTutor", "tutor",
                 capabilities=["teaching", "python", "exercises"]),
    
    create_agent("CodeReviewer", "reviewer",
                 capabilities=["code_review", "best_practices"]),
    
    create_agent("Debugger", "debugger",
                 capabilities=["debugging", "error_explanation"]),
    
    create_agent("ProjectMentor", "mentor",
                 capabilities=["project_guidance", "career_advice"]),
]

for agent in agents:
    add_agent_to_current_workspace(agent)
```

---

### 项目 4：移动端开发

```python
# 创建工作区
workspace = create_workspace("React Native 应用")
switch_workspace(workspace.id)

# 添加 Agent
agents = [
    create_agent("ReactNativeDev", "mobile_developer",
                 capabilities=["react_native", "typescript", "mobile_ui"]),
    
    create_agent("APIDesigner", "api_designer",
                 capabilities=["rest_api", "graphql", "mobile_backend"]),
    
    create_agent("StoreExpert", "store_expert",
                 capabilities=["app_store", "play_store", "deployment"]),
]

for agent in agents:
    add_agent_to_current_workspace(agent)
```

---

## 🔄 工作区管理

### 列出所有工作区

```python
from ymcode.workspace import get_workspace_manager

manager = get_workspace_manager()
workspaces = manager.list_workspaces()

print("所有工作区:")
for ws in workspaces:
    print(f"  - {ws['name']} (ID: {ws['id']})")
    print(f"    Agent 数量：{ws['agent_count']}")
    print(f"    会话数量：{ws['session_count']}")
```

### 切换工作区

```python
# 切换到指定工作区
success = switch_workspace("workspace-id-here")
if success:
    print("✓ 切换成功")
```

### 删除工作区

```python
manager = get_workspace_manager()
manager.delete_workspace("workspace-id-here")
```

---

## 💡 最佳实践

### 1. 按项目创建工作区

```python
# ✅ 好的做法
create_workspace("项目 A - 电商系统")
create_workspace("项目 B - 数据分析")
create_workspace("项目 C - 学习 Python")

# ❌ 不好的做法
create_workspace("工作区 1")
create_workspace("工作区 2")
```

### 2. 根据需求选择 Agent

```python
# ✅ 按需选择
# Web 项目 → 前端 + 后端 + DevOps
# 数据项目 → 分析师 + 可视化 + ML
# 学习项目 → 导师 + 审查 + 调试

# ❌ 全部添加（会造成混乱）
```

### 3. 给工作区清晰的描述

```python
# ✅ 好的描述
create_workspace(
    name="Flask 电商系统",
    description="包含用户系统、商品管理、订单处理的完整电商系统"
)

# ❌ 差的描述
create_workspace(
    name="项目",
    description="做一个系统"
)
```

### 4. 定期清理不用的工作区

```python
# 删除完成的项目
manager.delete_workspace("已完成项目的 ID")

# 导出重要工作区配置
import json
workspace_data = workspace.to_dict()
with open('workspace_backup.json', 'w') as f:
    json.dump(workspace_data, f)
```

---

## 📊 工作区对比

| 维度 | 单工作区 | 多工作区 |
|------|---------|---------|
| 项目隔离 | ❌ 混合 | ✅ 完全隔离 |
| Agent 配置 | ❌ 固定 | ✅ 自定义 |
| 上下文管理 | ❌ 混乱 | ✅ 清晰 |
| 会话历史 | ❌ 混在一起 | ✅ 独立保存 |
| 适用场景 | 单一项目 | 多项目并行 |

---

## 🎯 UI/UX 建议

### Web 界面实现

```
┌─────────────────────────────────────────┐
│  工作区选择：[Flask 电商系统 ▼]  [+]   │
├─────────────────────────────────────────┤
│                                          │
│  当前工作区：Flask 电商系统              │
│  Agent 团队 (4):                         │
│  ✅ FlaskDeveloper                       │
│  ✅ DatabaseDesigner                     │
│  ✅ TestExpert                           │
│  ✅ DocWriter                            │
│                                          │
│  [+ 添加 Agent]  [配置]  [切换工作区]    │
│                                          │
├─────────────────────────────────────────┤
│  聊天区域...                             │
└─────────────────────────────────────────┘
```

### 新建项目流程

```
1. 点击 [新建工作区]
   ↓
2. 输入项目名称和描述
   ↓
3. 从 Agent 市场选择需要的 Agent
   ☑ FlaskDeveloper
   ☑ DatabaseDesigner
   ☐ MobileDeveloper (不选)
   ☑ TestExpert
   ↓
4. 点击 [创建工作区]
   ↓
5. 开始项目！
```

---

## 🔧 高级功能

### 1. 工作区模板

```python
# 定义模板
WEB_PROJECT_TEMPLATE = {
    "name": "Web 项目",
    "agents": [
        {"role": "frontend_developer", "capabilities": ["react"]},
        {"role": "backend_developer", "capabilities": ["python"]},
        {"role": "tester", "capabilities": ["pytest"]},
    ]
}

# 使用模板创建
def create_from_template(template_name: str, project_name: str):
    workspace = create_workspace(project_name)
    switch_workspace(workspace.id)
    
    template = TEMPLATES.get(template_name)
    for agent_config in template['agents']:
        agent = create_agent(**agent_config)
        add_agent_to_current_workspace(agent)
```

### 2. 导出/导入工作区

```python
# 导出
import json
workspace_data = workspace.to_dict()
with open('workspace_export.json', 'w') as f:
    json.dump(workspace_data, f, indent=2)

# 导入
with open('workspace_export.json', 'r') as f:
    data = json.load(f)
    
workspace = create_workspace(data['name'], data['description'])
switch_workspace(workspace.id)

# 重新创建 Agent
for agent_data in data['agents']:
    agent = create_agent(**agent_data)
    add_agent_to_current_workspace(agent)
```

### 3. 工作区克隆

```python
def clone_workspace(source_id: str, new_name: str):
    """克隆工作区配置"""
    source = manager.get_workspace(source_id)
    
    # 创建新工作区
    new_workspace = create_workspace(new_name, f"克隆自 {source.name}")
    switch_workspace(new_workspace.id)
    
    # 复制 Agent 配置
    for agent_data in source.list_agents():
        agent = create_agent(
            name=agent_data['name'],
            role=agent_data['role'],
            description=agent_data['description'],
            capabilities=agent_data['capabilities']
        )
        add_agent_to_current_workspace(agent)
```

---

## 📝 常见问题

### Q: 一个 Agent 可以在多个工作区吗？

**A:** 可以！Agent 注册表中的 Agent 可以被添加到多个工作区。

```python
# 创建通用 Agent
tester = create_agent("TestExpert", "tester", ...)

# 添加到多个工作区
switch_workspace("项目 A")
add_agent_to_current_workspace(tester)

switch_workspace("项目 B")
add_agent_to_current_workspace(tester)
```

---

### Q: 工作区删除后 Agent 会删除吗？

**A:** 不会！工作区删除只删除工作区本身，Agent 仍然在注册表中。

---

### Q: 可以动态添加/移除 Agent 吗？

**A:** 可以！随时添加或移除。

```python
# 项目中期需要文档
documenter = create_agent("DocWriter", "documenter", ...)
add_agent_to_current_workspace(documenter)

# 项目完成移除不需要的
workspace.remove_agent("TempAgent")
```

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
