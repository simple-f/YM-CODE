# M5 Web 界面开发计划

**创建时间：** 2026-03-19 14:35  
**负责人：** ai2 (Builder) + ai3 (Reviewer)  
**优先级：** P0

---

## 📋 开发目标

完成 YM-CODE 多 Agent 协作系统的 Web 监控 Dashboard，实现：
1. Agent 状态实时监控
2. 任务管理看板
3. 系统指标可视化
4. 知识库检索界面

---

## 🏗️ 技术选型

### 前端框架
- **方案：** 纯 HTML/CSS/JS (轻量级，无需构建)
- **理由：** 快速开发、易于部署、与现有架构一致
- **UI 库：** Tailwind CSS (CDN) + Alpine.js (响应式)

### 后端 API
- **框架：** FastAPI (已实现)
- **路径：** `ymcode/web/dashboard_api.py`
- **端口：** 8080

### 实时通信
- **协议：** WebSocket
- **端点：** `/ws/events`
- **心跳：** 30 秒

---

## 📐 页面结构

```
/dashboard
├── 概览面板 (Overview)
│   ├── 系统状态卡片
│   ├── 任务统计图表
│   └── 活跃告警列表
│
├── Agent 监控 (Agents)
│   ├── Agent 状态网格
│   ├── 任务分配情况
│   └── 性能指标图表
│
├── 任务看板 (Tasks)
│   ├── 任务列表 (可筛选)
│   ├── 任务详情面板
│   └── 创建/取消任务
│
├── 知识库 (Knowledge)
│   ├── 文档搜索框
│   ├── 检索结果列表
│   └── 文档预览
│
└── 系统设置 (Settings)
    ├── MCP 服务器配置
    ├── 告警规则管理
    └── 日志查看器
```

---

## 🎨 UI 设计规范

### 配色方案
- **主色：** #2196F3 (Material Blue)
- **成功：** #4CAF50 (Green)
- **警告：** #FF9800 (Orange)
- **错误：** #F44336 (Red)
- **背景：** #F5F5F5 (Light Gray)
- **卡片：** #FFFFFF (White)

### 布局
- **导航：** 左侧固定侧边栏
- **内容：** 右侧主内容区
- **响应式：** 支持桌面/平板/手机

### 组件
- **卡片：** 圆角 8px，阴影 0 2px 4px rgba(0,0,0,0.1)
- **按钮：** 圆角 4px，悬停效果
- **表格：** 斑马纹，悬停高亮
- **图表：** Chart.js (CDN)

---

## 📝 开发任务

### Phase 1: 基础架构 (2h)
- [ ] 创建 `frontend/dashboard/index.html`
- [ ] 创建 `frontend/dashboard/styles.css`
- [ ] 创建 `frontend/dashboard/app.js`
- [ ] 配置静态文件路由

### Phase 2: 概览面板 (3h)
- [ ] 系统状态卡片组件
- [ ] 任务统计图表 (Chart.js)
- [ ] 活跃告警列表
- [ ] WebSocket 实时连接

### Phase 3: Agent 监控 (3h)
- [ ] Agent 状态网格
- [ ] 任务分配进度条
- [ ] 性能指标趋势图
- [ ] Agent 详情弹窗

### Phase 4: 任务看板 (3h)
- [ ] 任务列表 (筛选/排序)
- [ ] 任务详情面板
- [ ] 创建任务表单
- [ ] 取消任务确认

### Phase 5: 知识库 (2h)
- [ ] 搜索框组件
- [ ] 检索结果列表
- [ ] 文档预览面板
- [ ] 分页/加载更多

### Phase 6: 集成测试 (1h)
- [ ] API 连接测试
- [ ] WebSocket 重连测试
- [ ] 响应式布局测试
- [ ] 浏览器兼容性测试

---

## 📊 验收标准

### 功能要求
- [ ] 所有 API 端点正常调用
- [ ] WebSocket 实时推送正常
- [ ] 任务创建/取消功能正常
- [ ] 知识库检索功能正常

### 性能要求
- [ ] 首屏加载 < 2s
- [ ] 数据刷新 < 500ms
- [ ] WebSocket 延迟 < 100ms

### 用户体验
- [ ] 响应式布局适配
- [ ] 加载状态提示
- [ ] 错误处理友好
- [ ] 操作反馈及时

---

## 📁 文件结构

```
YM-CODE/
├── frontend/dashboard/
│   ├── index.html          # 主页面
│   ├── styles.css          # 样式表
│   ├── app.js              # 主逻辑
│   ├── components/         # 组件
│   │   ├── overview.js
│   │   ├── agents.js
│   │   ├── tasks.js
│   │   └── knowledge.js
│   └── utils/              # 工具函数
│       ├── api.js
│       └── websocket.js
│
├── ymcode/web/
│   ├── dashboard_api.py    # 后端 API (已有)
│   └── static/             # 静态文件
│       └── dashboard/      # 前端文件 symlink
│
└── docs/
    └── DASHBOARD_GUIDE.md  # 使用指南
```

---

## 🚀 启动命令

```bash
# 启动 Dashboard API
cd YM-CODE
python -m ymcode.web.dashboard_api

# 访问
http://localhost:8080/dashboard
```

---

## 📅 时间估算

| 阶段 | 工时 | 累计 |
|------|------|------|
| Phase 1 | 2h | 2h |
| Phase 2 | 3h | 5h |
| Phase 3 | 3h | 8h |
| Phase 4 | 3h | 11h |
| Phase 5 | 2h | 13h |
| Phase 6 | 1h | 14h |

**总计：** 14 小时

---

## ⚠️ 风险与依赖

### 风险
1. WebSocket 连接稳定性
2. 大数据量渲染性能
3. 浏览器兼容性

### 依赖
1. FastAPI 后端 API 稳定
2. 任务队列模块正常
3. 指标收集器正常

---

_下一步：开始 Phase 1 基础架构开发_
