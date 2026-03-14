# 多 Agent + 工作空间系统指南

> 创建属于你的 AI 团队，管理多个项目上下文

---

## 🎭 多 Agent 系统

### 什么是 Agent？

Agent 是具有特定人格、专业领域和沟通风格的 AI 助手。你可以创建多个 Agent，每个负责不同的任务。

### 为什么需要多 Agent？

- **专业分工** - 代码审查用专业 Agent，日常聊天用友好 Agent
- **人格定制** - 不同项目需要不同沟通风格
- **上下文隔离** - 每个 Agent 有自己的记忆和知识
- **效率提升** - 快速切换，无需重新建立上下文

---

## 🚀 快速开始

### 1. 查看可用 Agent

```bash
# 列出所有 Agent
ym-code agents list

# 查看当前 Agent
ym-code agents show

# 查看可用模板
ym-code agents templates
```

### 2. 创建 Agent

```bash
# 使用模板创建
ym-code agents create "CodeReviewer" --template professional

# 自定义创建
ym-code agents create "Buddy" --personality friendly

# 创建幽默风格的 Agent
ym-code agents create "Joker" --template humorous
```

### 3. 切换 Agent

```bash
# 切换到指定 Agent
ym-code agents switch CodeReviewer

# 查看当前 Agent
ym-code agents show
```

---

## 📋 Agent 模板

### 可用模板

| 模板 | 名称 | 人格 | 适用场景 |
|------|------|------|----------|
| **friendly** | YM-Friend | 友好温暖 | 日常编程、新手指导 |
| **professional** | YM-Pro | 专业正式 | 代码审查、技术文档 |
| **humorous** | YM-Joker | 幽默风趣 | 轻松编程、调试 |
| **strict** | YM-Mentor | 严格导师 | 技能提升、代码优化 |
| **creative** | YM-Creator | 创意艺术 | 设计模式、架构设计 |

### 示例输出

```bash
$ ym-code agents templates

📋 可用 Agent 模板：

  🤝 friendly - Buddy
     别担心，我来帮你搞定！

  💼 professional - Expert
     根据最佳实践，建议...

  🎭 humorous - Comedy
     这个 bug 比我家的猫还难捉摸！

  🦉 strict - Sensei
     代码可以更好，再想想。

  🎨 creative - Artist
     代码也是艺术！
```

---

## 📁 工作空间系统

### 什么是工作空间？

工作空间是独立的项目环境，包含：
- 独立的配置文件
- 独立的记忆和历史
- 关联的 Agent
- 项目特定的上下文

### 为什么需要工作空间？

- **项目隔离** - 不同项目不互相干扰
- **上下文管理** - 每个项目有自己的记忆
- **配置独立** - 不同项目不同设置
- **快速切换** - 一键切换项目环境

---

## 🚀 工作空间操作

### 1. 查看工作空间

```bash
# 列出所有工作空间
ym-code workspace list

# 查看当前工作空间
ym-code workspace show
```

### 2. 创建工作空间

```bash
# 创建默认工作空间
ym-code workspace create "project-alpha"

# 创建项目工作空间（关联特定 Agent）
ym-code workspace create "code-review-project" \
  --type project \
  --agent CodeReviewer

# 从现有工作空间复制
ym-code workspace create "project-beta" \
  --copy-from project-alpha
```

### 3. 切换工作空间

```bash
# 切换到指定工作空间
ym-code workspace switch project-alpha

# 查看当前工作空间
ym-code workspace show
```

### 4. 管理工作空间

```bash
# 删除工作空间
ym-code workspace delete old-project

# 强制删除（不确认）
ym-code workspace delete old-project --force
```

---

## 💡 实战场景

### 场景 1：多项目管理

```bash
# 为每个项目创建独立工作空间
ym-code workspace create "ecommerce" --type project
ym-code workspace create "blog" --type project
ym-code workspace create "api-service" --type project

# 为不同项目分配不同 Agent
ym-code agents switch YM-Pro
ym-code workspace switch ecommerce

ym-code agents switch YM-Creator
ym-code workspace switch blog

# 工作时快速切换
ym-code workspace ecommerce  # 切换到电商项目
ym-code workspace blog       # 切换到博客项目
```

### 场景 2：代码审查流程

```bash
# 创建专业审查 Agent
ym-code agents create "SeniorReviewer" \
  --template strict

# 创建审查工作空间
ym-code workspace create "review-session" \
  --type sandbox \
  --agent SeniorReviewer

# 开始审查
ym-code workspace switch review-session
ym-code "请审查这个 PR 的代码质量"
```

### 场景 3：学习模式

```bash
# 创建导师型 Agent
ym-code agents create "PythonMentor" \
  --template strict \
  --expertise python,architecture,testing

# 创建学习工作空间
ym-code workspace create "learning-python" \
  --agent PythonMentor

# 开始学习
ym-code workspace switch learning-python
ym-code "教我 Python 异步编程的最佳实践"
```

---

## 🔧 配置文件

### Agent 配置文件

位置：`~/.ym-code/identities/{codename}.yaml`

```yaml
name: CodeReviewer
codename: code-reviewer
personality: professional
tone: formal
communication_style:
  verbosity: detailed
  emoji_usage: none
  humor_level: none
  formality: formal
expertise:
  - python
  - code-review
  - best-practices
constraints:
  - always_ask_before_destructive_actions
  - explain_reasoning
  - admit_uncertainty
quotes:
  - "根据最佳实践，建议..."
  - "从专业角度分析..."
avatar_emoji: 💼
avatar_color: "#3B82F6"
```

### 工作空间配置

位置：`~/.ym-code/workspaces/{name}/config/workspace.yaml`

```yaml
workspace:
  name: ecommerce
  type: project
  agent: CodeReviewer

project:
  auto_index: true
  ignore:
    - node_modules/
    - __pycache__/
    - .git/
```

---

## 📊 系统架构

```
~/.ym-code/
├── identities/              # Agent 身份文件
│   ├── friendly-buddy.yaml
│   ├── professional-expert.yaml
│   └── humorous-comedy.yaml
├── workspaces/              # 工作空间
│   ├── workspaces.json      # 工作空间索引
│   ├── default/             # 默认工作空间
│   │   ├── config/
│   │   ├── memory/
│   │   ├── history/
│   │   └── cache/
│   ├── project-alpha/
│   └── project-beta/
└── config.yaml              # 全局配置
```

---

## 🎯 最佳实践

### Agent 创建

1. **明确用途** - 每个 Agent 有明确的职责
2. **选择合适模板** - 基于使用场景选择人格
3. **定制专业领域** - 指定擅长的技术领域
4. **设置约束** - 定义行为边界

### 工作空间管理

1. **按项目分离** - 每个项目独立工作空间
2. **定期清理** - 删除不再需要的工作空间
3. **备份重要配置** - 导出关键工作空间配置
4. **合理命名** - 使用清晰的命名规则

### 切换策略

1. **工作前切换** - 开始工作前切换到对应环境
2. **避免混用** - 不在一个工作空间处理多个项目
3. **利用沙盒** - 测试用沙盒工作空间

---

## 🔮 高级功能

### Agent 组合

可以为不同任务创建 Agent 组合：

```bash
# 创建全栈开发团队
ym-code agents create "FrontendExpert" --expertise javascript,react,css
ym-code agents create "BackendExpert" --expertise python,database,api
ym-code agents create "DevOpsExpert" --expertise docker,k8s,ci-cd

# 为项目分配主 Agent
ym-code workspace create "fullstack-project" --agent FrontendExpert
```

### 工作空间模板

创建工作空间模板供团队使用：

```bash
# 创建标准项目模板
ym-code workspace create "standard-template" --type project

# 配置标准设置
# 编辑 ~/.ym-code/workspaces/standard-template/config/workspace.yaml

# 基于模板创建新项目
ym-code workspace create "new-project" --copy-from standard-template
```

---

## 📝 命令行速查

### Agent 命令

```bash
ym-code agents list              # 列出 Agent
ym-code agents show              # 显示当前 Agent
ym-code agents create <name>     # 创建 Agent
ym-code agents switch <name>     # 切换 Agent
ym-code agents templates         # 查看模板
```

### 工作空间命令

```bash
ym-code workspace list           # 列出工作空间
ym-code workspace show           # 显示当前工作空间
ym-code workspace create <name>  # 创建工作空间
ym-code workspace switch <name>  # 切换工作空间
ym-code workspace delete <name>  # 删除工作空间
```

---

## 🎉 总结

**多 Agent + 工作空间系统**让你可以：

- ✅ 创建多个不同人格的 AI 助手
- ✅ 为每个项目创建独立环境
- ✅ 快速切换上下文
- ✅ 保持工作整洁有序
- ✅ 提升工作效率

**让 AI 真正适应你的工作方式！** 🚀

---

_文档版本：1.0_  
_最后更新：2026-03-13_
