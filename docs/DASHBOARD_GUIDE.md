# YM-CODE Dashboard 使用指南

**版本：** 1.0.0  
**最后更新：** 2026-03-19

---

## 📖 简介

YM-CODE Dashboard 是一个现代化的多 Agent 协作系统监控面板，提供：

- 📊 **实时系统监控** - 任务统计、Agent 状态、性能指标
- 🤖 **Agent 管理** - 查看 Agent 状态、任务分配、性能分析
- 📋 **任务看板** - 创建、查看、取消任务，支持筛选和搜索
- 📚 **知识库检索** - 语义搜索文档、查看检索结果
- ⚙️ **系统设置** - MCP 配置、告警管理、日志查看

---

## 🚀 快速启动

### 前置要求

- Python 3.8+
- FastAPI
- Uvicorn

### 安装依赖

```bash
cd YM-CODE
pip install fastapi uvicorn python-multipart
```

### 启动 Dashboard

```bash
# 方式 1: 直接运行
python -m ymcode.web.dashboard_api

# 方式 2: 使用 CLI
ymcode dashboard start

# 方式 3: 生产环境
uvicorn ymcode.web.dashboard_api:app --host 0.0.0.0 --port 8080
```

### 访问地址

启动后访问：**http://localhost:8080/dashboard**

---

## 📐 功能说明

### 1. 概览面板 (Overview)

**系统状态卡片：**
- 总任务数
- 已完成任务
- 失败任务
- 活跃 Agent 数量

**图表展示：**
- 任务趋势图（按时间）
- Agent 性能对比图

**活跃告警：**
- 实时显示系统告警
- 支持一键确认告警

### 2. Agent 监控 (Agents)

**功能：**
- 实时查看所有 Agent 状态
- 显示任务完成/失败统计
- 平均执行时间监控

**状态说明：**
- 🟢 **idle** - 空闲，可接受新任务
- 🔵 **busy** - 忙碌，正在执行任务
- 🔴 **error** - 错误，需要关注

### 3. 任务看板 (Tasks)

**功能：**
- 任务列表展示（支持分页）
- 按状态/优先级筛选
- 关键词搜索
- 创建新任务
- 取消待处理/进行中任务

**任务状态：**
- 🟡 **PENDING** - 待处理
- 🔵 **RUNNING** - 进行中
- 🟢 **COMPLETED** - 已完成
- 🔴 **FAILED** - 失败

**优先级：**
- ⚪ **LOW** - 低
- 🔵 **NORMAL** - 普通
- 🟠 **HIGH** - 高
- 🔴 **CRITICAL** - 紧急

### 4. 知识库 (Knowledge)

**功能：**
- 语义搜索文档
- 显示相似度评分
- 显示文档来源
- 支持分页加载

**使用方法：**
1. 输入搜索关键词
2. 点击搜索或按回车
3. 查看检索结果
4. 点击结果查看详情

### 5. 系统设置 (Settings)

**功能：**
- MCP 状态监控
- MCP 服务器配置
- 告警规则管理
- 系统日志查看

---

## 🔌 API 接口

### 基础信息

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 根路径 |
| `/health` | GET | 健康检查 |
| `/dashboard` | GET | Dashboard 页面 |

### 任务管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/tasks` | GET | 列出任务 |
| `/api/tasks` | POST | 创建任务 |
| `/api/tasks/{id}` | GET | 获取任务详情 |
| `/api/tasks/{id}` | DELETE | 取消任务 |

**查询参数：**
- `status` - 按状态筛选
- `assigned_to` - 按分配对象筛选
- `limit` - 返回数量限制

### 系统指标

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/metrics/system` | GET | 系统指标 |
| `/api/metrics/agents` | GET | Agent 指标 |
| `/api/metrics/history` | GET | 指标历史 |

### 告警管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/alerts` | GET | 获取告警 |
| `/api/alerts/{name}/acknowledge` | POST | 确认告警 |
| `/api/alerts/{name}/resolve` | POST | 恢复告警 |

### MCP 管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/mcp/status` | GET | MCP 状态 |
| `/api/mcp/tools` | GET | MCP 工具列表 |

### WebSocket

| 端点 | 说明 |
|------|------|
| `/ws/events` | 实时事件推送 |

**心跳：** 每 30 秒发送 `ping`，服务器回复 `pong`

---

## 🎨 自定义

### 修改配色

编辑 `frontend/dashboard/index.html`：

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#2196F3',  // 主色
                success: '#4CAF50',  // 成功
                warning: '#FF9800',  // 警告
                error: '#F44336',    // 错误
            }
        }
    }
}
```

### 修改布局

编辑 `frontend/dashboard/styles.css` 添加自定义样式。

### 添加新页面

1. 在 `frontend/dashboard/` 创建新 HTML 文件
2. 在 `index.html` 添加导航链接
3. 在 `app.js` 添加对应逻辑

---

## 🔧 故障排查

### Dashboard 无法访问

**检查：**
```bash
# 确认服务已启动
ps aux | grep uvicorn

# 检查端口占用
netstat -an | grep 8080

# 查看日志
tail -f logs/dashboard.log
```

### WebSocket 连接失败

**可能原因：**
- 防火墙阻止 WebSocket
- 反向代理未配置 WebSocket
- 服务端未启动

**解决方案：**
```bash
# 检查防火墙
ufw allow 8080/tcp

# Nginx 配置
location /ws/events {
    proxy_pass http://localhost:8080/ws/events;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### 数据不刷新

**检查：**
1. 浏览器控制台是否有错误
2. API 端点是否正常响应
3. WebSocket 是否已连接

**手动刷新：** 点击右上角 🔄 刷新按钮

---

## 📊 性能优化

### 生产环境部署

```bash
# 使用多 worker
uvicorn ymcode.web.dashboard_api:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 4

# 使用 Gunicorn + Uvicorn
gunicorn ymcode.web.dashboard_api:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080
```

### 反向代理配置

**Nginx 示例：**

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 安全建议

### 生产环境

1. **启用 HTTPS**
   ```bash
   # 使用 Let's Encrypt
   certbot --nginx -d dashboard.example.com
   ```

2. **配置认证**
   - 添加 JWT/OAuth2 认证
   - 限制访问 IP

3. **限制速率**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

4. **日志审计**
   - 记录所有操作日志
   - 定期审查异常访问

---

## 📝 开发指南

### 项目结构

```
YM-CODE/
├── frontend/dashboard/
│   ├── index.html      # 主页面
│   ├── styles.css      # 样式表
│   └── app.js          # 主逻辑
│
├── ymcode/web/
│   └── dashboard_api.py # 后端 API
│
└── docs/
    └── DASHBOARD_GUIDE.md # 本文档
```

### 添加新功能

1. **后端 API：** 在 `dashboard_api.py` 添加新端点
2. **前端页面：** 在 `index.html` 添加新组件
3. **交互逻辑：** 在 `app.js` 添加对应函数
4. **测试：** 验证功能正常

### 调试技巧

**浏览器控制台：**
```javascript
// 查看当前状态
console.log(dashboard())

// 手动刷新数据
dashboard().refreshData()

// 查看 WebSocket 状态
dashboard().wsConnected
```

**后端日志：**
```bash
# 启用调试日志
export LOG_LEVEL=debug
python -m ymcode.web.dashboard_api
```

---

## 🆘 常见问题

### Q: Dashboard 加载很慢？
**A:** 检查网络连接，CDN 资源可能需要科学上网。可考虑本地部署 Tailwind 和 Chart.js。

### Q: 如何禁用 WebSocket？
**A:** WebSocket 用于实时推送，禁用后需手动刷新。可在 `app.js` 注释 `connectWebSocket()`。

### Q: 支持移动端吗？
**A:** 已支持响应式布局，可在手机/平板访问。

### Q: 如何导出数据？
**A:** 目前不支持，计划添加导出 CSV/Excel 功能。

---

## 📞 技术支持

- **文档：** `/docs` 目录
- **日志：** `logs/dashboard.log`
- **问题反馈：** GitHub Issues

---

_最后更新：2026-03-19_
