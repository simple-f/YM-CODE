# 模块整合计划

**时间：** 2026-03-16 18:20  
**目标：** 将 v1.0 已有模块整合到 v2.0 架构

---

## 📦 需要整合的模块

### 1. 记忆系统 ✅ v1.0

**原位置：** `ymcode/memory/`

**文件：**
- `__init__.py`
- `session.py` - Session 管理
- `context.py` - 上下文管理
- `compressor.py` - 上下文压缩
- `memory.py` - 长期记忆

**整合方案：**
```
backend/
└── services/
    └── memory_service.py  # 记忆服务
```

---

### 2. 技能系统 ✅ v1.0

**原位置：** `ymcode/skills/`

**文件：**
- 11+ 个内置技能
- `base.py` - 技能基类
- `registry.py` - 技能注册表

**整合方案：**
```
backend/
└── plugins/
    └── skills/  # 技能作为插件
        ├── skill_plugin.py  # 技能插件适配器
        └── ...  # 原有技能
```

---

### 3. LLM 客户端 ✅ v1.0

**原位置：** `ymcode/core/llm_client.py`

**文件：**
- `llm_client.py` - 统一 LLM 客户端
- `api_model.py` - API 模型
- `context_manager.py` - 上下文管理

**整合方案：**
```
backend/
└── core/
    └── llm/
        ├── llm_client.py  # 保持不变
        └── models.py      # 模型配置
```

---

### 4. Agent 系统 ✅ v1.0

**原位置：** `ymcode/agents/`

**文件：**
- `builder.py` - Builder Agent
- `reviewer.py` - Reviewer Agent
- `router.py` - A2A 路由器

**整合方案：**
```
backend/
└── agents/
    ├── builder_agent.py  # Builder Agent
    ├── reviewer_agent.py # Reviewer Agent
    └── ...               # 其他 Agent
```

---

### 5. MCP 协议 ✅ v1.0

**原位置：** `ymcode/mcp/`

**文件：**
- `client_v2.py` - MCP 客户端
- `server_registry.py` - 服务器注册表
- `skills_server.py` - 技能服务器

**整合方案：**
```
backend/
└── plugins/
    └── mcp/
        ├── mcp_plugin.py  # MCP 插件
        └── ...            # MCP 相关
```

---

### 6. 工作区管理 ✅ v1.0

**原位置：** `ymcode/workspace.py`

**整合方案：**
```
backend/
└── services/
    └── workspace_service.py  # 工作区服务
```

---

## 🔄 整合步骤

### 步骤 1：复制核心模块

```bash
# 复制 LLM 客户端
cp ymcode/core/llm_client.py backend/core/llm/
cp ymcode/core/api_model.py backend/core/llm/
cp ymcode/core/context_manager.py backend/core/llm/

# 复制记忆系统
cp -r ymcode/memory/ backend/services/memory/

# 复制技能系统
cp -r ymcode/skills/ backend/plugins/skills/

# 复制 Agent
cp ymcode/agents/*.py backend/agents/
```

### 步骤 2：适配新架构

- 更新导入路径
- 适配新的基类
- 实现插件接口

### 步骤 3：测试验证

- 单元测试
- 集成测试
- 功能验证

---

## 📊 整合进度

- [ ] LLM 客户端
- [ ] 记忆系统
- [ ] 技能系统
- [ ] Agent 系统
- [ ] MCP 协议
- [ ] 工作区管理

---

**开始整合时间：** 2026-03-16 18:20
