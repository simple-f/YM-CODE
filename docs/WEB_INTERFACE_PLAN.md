# 🔮 YM-CODE Web 界面开发计划

> 后端 (ai2) & 前端 (ai3) 对接文档

---

## 📋 项目概述

**目标：** 为 YM-CODE 打造现代化的 Web 界面，降低使用门槛，提升用户体验。

**定位：**
- 🎨 美观 - 现代化 UI 设计
- ⚡ 高效 - 快速响应，流畅交互
- 🔧 实用 - 核心功能完整
- 📱 响应式 - 支持多种设备

---

## 🎯 功能需求

### 1. 首页/仪表盘

**功能：**
- 当前 Agent 显示（头像、人格、状态）
- 工作空间切换器
- 快速搜索框
- 最近活动列表
- 系统统计卡片

**UI 组件：**
```
┌────────────────────────────────────────────┐
│  YM-CODE  🔮 Aurora          [工作空间▼]  │
├────────────────────────────────────────────┤
│  [🔍 快速搜索...]                           │
├────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ 知识条目 │ │ 会话数  │ │ 技能数  │     │
│  │   156   │ │   42    │ │   32    │     │
│  └─────────┘ └─────────┘ └─────────┘     │
├────────────────────────────────────────────┤
│  最近活动                                   │
│  • 创建了知识条目 "异步编程指南"           │
│  • 切换到工作空间 "project-alpha"          │
│  • 执行了代码分析                          │
└────────────────────────────────────────────┘
```

---

### 2. 聊天界面

**功能：**
- 对话历史展示
- 代码高亮显示
- Markdown 渲染
- 文件上传/拖拽
- 快捷命令输入

**UI 组件：**
```
┌────────────────────────────────────────────┐
│  💬 对话                      [清空] [导出]│
├────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐ │
│  │ 👤 用户                               │ │
│  │ 帮我分析这个项目的代码结构            │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ 🔮 YM-Pro                             │ │
│  │ 这个项目包含以下结构：                │ │
│  │ ```python                             │ │
│  │ def main():                           │ │
│  │     ...                               │ │
│  │ ```                                   │ │
│  └──────────────────────────────────────┘ │
├────────────────────────────────────────────┤
│  [📎] [输入消息...]                  [发送]│
└────────────────────────────────────────────┘
```

---

### 3. 知识库页面

**功能：**
- 知识条目列表
- 搜索/过滤（分类、标签、类型）
- 分类树展示
- 知识详情查看
- 知识图谱可视化

**UI 组件：**
```
┌────────────────────────────────────────────┐
│  📚 知识库          [搜索...] [新建条目]   │
├──────────────┬─────────────────────────────┤
│  分类树      │  知识列表                   │
│  📁 code     │  ┌─────────────────────┐   │
│  ├── python  │  │ Python 异步编程指南  │   │
│  └── js      │  │ code/python ⭐ best..│   │
│  📁 docs     │  └─────────────────────┘   │
│  ├── api     │  ┌─────────────────────┐   │
│  └── guides  │  │ RESTful API 设计     │   │
│              │  │ code/python ⭐ best..│   │
│              │  └─────────────────────┘   │
└──────────────┴─────────────────────────────┘
```

---

### 4. 调试页面

**功能：**
- 追踪会话列表
- 执行追踪详情（时间线展示）
- 性能分析报告
- 图表可视化（调用热点、性能对比）

**UI 组件：**
```
┌────────────────────────────────────────────┐
│  🔧 调试系统               [开始追踪] [停止]│
├──────────────┬─────────────────────────────┤
│  会话列表    │  追踪详情：session_abc123   │
│  • session_1 │  ┌─────────────────────┐   │
│  • session_2 │  │ 📞 call skills.search│   │
│  • session_3 │  │    2.3ms             │   │
│              │  ├─────────────────────┤   │
│              │  │ ✅ return skills...  │   │
│              │  │    5.6ms             │   │
│              │  └─────────────────────┘   │
│              │  [回放] [导出] [分析]       │
└──────────────┴─────────────────────────────┘
```

---

### 5. 设置页面

**功能：**
- Agent 管理（创建、切换、配置）
- 工作空间管理
- 主题切换（5 种主题）
- 系统配置

**UI 组件：**
```
┌────────────────────────────────────────────┐
│  ⚙️ 设置                                   │
├────────────────────────────────────────────┤
│  🎭 Agent 管理                              │
│  当前：YM-Pro (professional)     [切换▼]  │
│  [创建新 Agent]                             │
├────────────────────────────────────────────┤
│  📁 工作空间                                │
│  当前：default                   [切换▼]  │
│  [创建工作空间]                             │
├────────────────────────────────────────────┤
│  🎨 主题                                    │
│  ◉ Aurora  ○ Light  ○ Dark  ○ Matrix      │
└────────────────────────────────────────────┘
```

---

## 🔌 API 接口设计

### RESTful API 规范

**基础 URL:** `/api/v1`

**认证:** Bearer Token (可选，初期可不用)

**响应格式:**
```typescript
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

### 聊天接口

```typescript
// POST /api/chat
interface ChatRequest {
  message: string;
  workspace?: string;
  agent?: string;
  context?: Message[];
}

interface ChatResponse {
  message: string;
  agent: string;
  timestamp: string;
  metadata?: {
    duration_ms: number;
    tokens_used: number;
  };
}
```

### 知识库接口

```typescript
// GET /api/knowledge
interface KnowledgeSearchRequest {
  query: string;
  category?: string;
  tags?: string[];
  type?: KnowledgeType;
  limit?: number;
}

interface KnowledgeSearchResponse {
  results: SearchResult[];
  total: number;
}

// GET /api/knowledge/:id
interface KnowledgeDetailResponse {
  entry: KnowledgeEntry;
  related: KnowledgeEntry[];
}
```

### 调试接口

```typescript
// GET /api/debug/traces
interface TraceListResponse {
  sessions: TraceSession[];
}

// GET /api/debug/traces/:id
interface TraceDetailResponse {
  session: TraceSession;
  events: TraceEvent[];
  statistics: TraceStatistics;
}

// GET /api/debug/profiles/:id/report
interface ProfileReportResponse {
  profile_id: string;
  duration: number;
  top_functions: FunctionStats[];
  html_report?: string;
}
```

### Agent 接口

```typescript
// GET /api/agents
interface AgentListResponse {
  agents: AgentIdentity[];
  current: string;
}

// POST /api/agents
interface CreateAgentRequest {
  name: string;
  template?: string;
  personality?: string;
}

// PUT /api/agents/:name/switch
interface SwitchAgentRequest {
  name: string;
}
```

### 工作空间接口

```typescript
// GET /api/workspaces
interface WorkspaceListResponse {
  workspaces: Workspace[];
  current: string;
}

// POST /api/workspaces
interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  type?: 'default' | 'project' | 'sandbox';
  agent?: string;
  copy_from?: string;
}
```

---

## 🎨 技术栈

### 推荐方案

```json
{
  "framework": "React 18.2",
  "language": "TypeScript 5.0",
  "ui": {
    "framework": "TailwindCSS 3.3",
    "components": "shadcn/ui",
    "icons": "Lucide React"
  },
  "state": {
    "global": "Zustand 4.3",
    "server": "TanStack Query 5"
  },
  "routing": "React Router 6.11",
  "http": "Axios 1.4",
  "forms": "React Hook Form 7.44",
  "markdown": "react-markdown + remark-gfm",
  "code_highlight": "Prism.js + prism-react-renderer",
  "charts": "Recharts 2.6",
  "build": "Vite 4.3",
  "testing": "Vitest + React Testing Library"
}
```

### 项目结构

```
ym-code-web/
├── public/
│   ├── icon.svg
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui 基础组件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── chat/            # 聊天组件
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── CodeBlock.tsx
│   │   ├── knowledge/       # 知识库组件
│   │   │   ├── KnowledgeList.tsx
│   │   │   ├── KnowledgeCard.tsx
│   │   │   ├── CategoryTree.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── debug/           # 调试组件
│   │   │   ├── TraceList.tsx
│   │   │   ├── TraceTimeline.tsx
│   │   │   └── ProfileChart.tsx
│   │   └── layout/          # 布局组件
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Chat.tsx
│   │   ├── Knowledge.tsx
│   │   ├── Debug.tsx
│   │   └── Settings.tsx
│   ├── stores/
│   │   ├── chatStore.ts
│   │   ├── knowledgeStore.ts
│   │   ├── agentStore.ts
│   │   └── workspaceStore.ts
│   ├── api/
│   │   ├── client.ts        # Axios 实例
│   │   ├── chat.ts
│   │   ├── knowledge.ts
│   │   ├── debug.ts
│   │   ├── agents.ts
│   │   └── workspaces.ts
│   ├── types/
│   │   ├── api.ts
│   │   ├── knowledge.ts
│   │   └── debug.ts
│   ├── utils/
│   │   ├── cn.ts            # className 工具
│   │   └── format.ts        # 格式化工具
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

---

## 📅 开发计划

### Phase 1: 基础框架 (1-2 天)

**任务：**
- [ ] 项目初始化 (Vite + React + TS)
- [ ] 安装依赖 (Tailwind, shadcn/ui, etc.)
- [ ] 配置路由 (React Router)
- [ ] 创建基础布局 (Header, Sidebar, Main)
- [ ] 配置 Axios 客户端
- [ ] 创建 Zustand stores

**交付：** 可运行的基础框架

---

### Phase 2: 聊天界面 (2-3 天)

**任务：**
- [ ] 聊天页面布局
- [ ] 消息列表组件
- [ ] 消息气泡组件
- [ ] 代码高亮组件 (Prism.js)
- [ ] Markdown 渲染 (react-markdown)
- [ ] 输入框组件
- [ ] 文件上传组件
- [ ] API 对接 (POST /api/chat)

**交付：** 完整的聊天界面

---

### Phase 3: 知识库界面 (2-3 天)

**任务：**
- [ ] 知识库页面布局
- [ ] 知识列表组件
- [ ] 知识卡片组件
- [ ] 分类树组件
- [ ] 搜索栏组件
- [ ] 过滤组件
- [ ] 知识详情弹窗
- [ ] API 对接 (GET /api/knowledge)

**交付：** 完整的知识库界面

---

### Phase 4: 调试界面 (2-3 天)

**任务：**
- [ ] 调试页面布局
- [ ] 追踪列表组件
- [ ] 追踪时间线组件
- [ ] 性能图表组件 (Recharts)
- [ ] 性能报告展示
- [ ] API 对接 (GET /api/debug/*)

**交付：** 完整的调试界面

---

### Phase 5: 设置与其他 (1-2 天)

**任务：**
- [ ] 设置页面布局
- [ ] Agent 管理组件
- [ ] 工作空间切换器
- [ ] 主题切换组件
- [ ] 系统配置表单
- [ ] API 对接

**交付：** 完整的设置界面

---

### Phase 6: 优化与测试 (1-2 天)

**任务：**
- [ ] 响应式适配
- [ ] 性能优化
- [ ] 单元测试
- [ ] E2E 测试
- [ ] 文档编写

**交付：** 生产就绪的 Web 应用

---

## 🤝 前后端对接

### 后端负责 (ai2)

- [ ] 实现 RESTful API
- [ ] 提供 TypeScript 类型定义
- [ ] CORS 配置
- [ ] API 文档 (OpenAPI/Swagger)
- [ ] 联调测试

### 前端负责 (ai3)

- [ ] UI 设计与实现
- [ ] 前端路由
- [ ] 状态管理
- [ ] API 调用
- [ ] 响应式适配
- [ ] 性能优化

### 共同负责

- [ ] 接口定义确认
- [ ] 数据类型对齐
- [ ] 联调测试
- [ ] Bug 修复

---

## 📊 进度追踪

| Phase | 任务 | 前端 | 后端 | 状态 |
|-------|------|------|------|------|
| 1 | 基础框架 | ⏳ | ⏳ | 待开始 |
| 2 | 聊天界面 | ⏳ | ⏳ | 待开始 |
| 3 | 知识库界面 | ⏳ | ⏳ | 待开始 |
| 4 | 调试界面 | ⏳ | ⏳ | 待开始 |
| 5 | 设置与其他 | ⏳ | ⏳ | 待开始 |
| 6 | 优化测试 | ⏳ | ⏳ | 待开始 |

---

## 🎯 成功标准

### MVP (最小可行产品)

- ✅ 聊天界面可用
- ✅ 知识库搜索可用
- ✅ Agent 切换可用
- ✅ 工作空间切换可用

### V1.0

- ✅ 所有核心功能完成
- ✅ 响应式设计
- ✅ 性能达标
- ✅ 测试覆盖 >80%

### V2.0 (未来)

- ⏳ 知识图谱可视化
- ⏳ 实时协作
- ⏳ PWA 支持
- ⏳ 移动端 App

---

**文档版本：** 1.0  
**创建时间：** 2026-03-13  
**作者：** ai2 (后端机器人)  
**对接人：** ai3 (前端机器人)
