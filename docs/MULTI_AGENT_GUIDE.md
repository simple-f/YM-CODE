# YM-CODE 多 Agent 使用指南

**更新时间：** 2026-03-19

---

## 🚀 快速开始

### 1. 访问 Agent 配置页面

打开浏览器访问：
- **Agent 配置：** http://localhost:8080/web/agent-config.html
- **多 Agent 协作：** http://localhost:8080/web/multi-agent.html

### 2. 创建 Agent 团队

#### 方法一：通过配置文件

在 `configs/team.json` 创建配置文件：

```json
{
  "name": "开发团队",
  "description": "全栈开发 Agent 团队",
  "agents": [
    {
      "id": "ai1",
      "name": "架构师",
      "role": "system",
      "description": "负责系统架构设计",
      "model": "qwen3.5-plus",
      "temperature": 0.7,
      "system_prompt": "你是一位资深软件架构师，负责系统设计和架构决策。"
    },
    {
      "id": "ai2",
      "name": "后端开发",
      "role": "developer",
      "description": "负责后端代码实现",
      "model": "qwen3.5-plus",
      "temperature": 0.5,
      "system_prompt": "你是一位资深后端开发工程师，擅长 Python、Go 等后端技术。"
    },
    {
      "id": "ai3",
      "name": "前端开发",
      "role": "developer",
      "description": "负责前端界面实现",
      "model": "qwen3.5-plus",
      "temperature": 0.5,
      "system_prompt": "你是一位资深前端开发工程师，擅长 React、Vue、TypeScript 等前端技术。"
    },
    {
      "id": "ai4",
      "name": "测试工程师",
      "role": "reviewer",
      "description": "负责代码审查和测试",
      "model": "qwen3.5-plus",
      "temperature": 0.3,
      "system_prompt": "你是一位资深测试工程师，负责代码审查、测试用例编写和质量保证。"
    }
  ]
}
```

#### 方法二：通过 API 创建

```bash
# 创建 Agent 团队
curl -X POST http://localhost:8080/api/team/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "开发团队",
    "agents": [
      {"name": "架构师", "role": "system"},
      {"name": "后端开发", "role": "developer"},
      {"name": "前端开发", "role": "developer"},
      {"name": "测试工程师", "role": "reviewer"}
    ]
  }'
```

### 3. 使用多 Agent 协作

1. **打开多 Agent 协作页面**
   - 访问：http://localhost:8080/web/multi-agent.html

2. **选择工作区**
   - 在左侧选择已配置的工作区

3. **选择参与对话的 Agent**
   - 可以选择多个 Agent（如：架构师 + 后端 + 前端）

4. **输入问题**
   - 例如："帮我设计一个用户登录系统"

5. **开始协作**
   - Agent 们会自动协作讨论并解决问题
   - 可以设置对话轮数（默认 5 轮）
   - 可以开启/关闭自动对话

---

## 📋 预设 Agent 角色

### 架构师 (Architect)
- **职责：** 系统架构设计、技术选型
- **特点：** 高屋建瓴，考虑全面
- **适用场景：** 系统设计、技术决策

### 后端开发 (Backend Developer)
- **职责：** 后端代码实现、API 设计
- **特点：** 逻辑严谨，注重性能
- **适用场景：** API 开发、数据库设计

### 前端开发 (Frontend Developer)
- **职责：** 前端界面实现、用户体验
- **特点：** 注重视觉效果，关注用户体验
- **适用场景：** UI 开发、交互设计

### 测试工程师 (QA Engineer)
- **职责：** 代码审查、测试用例编写
- **特点：** 细致入微，善于发现问题
- **适用场景：** 代码审查、质量保证

### 产品经理 (Product Manager)
- **职责：** 需求分析、产品规划
- **特点：** 用户导向，商业敏感
- **适用场景：** 需求讨论、产品规划

---

## 🔧 工作流引擎集成

YM-CODE 工作流引擎提供多 Agent 协作支持：

### State Tracker（状态追踪）
- 记录每个 Agent 的状态变化
- 追踪任务执行进度

### Cascade Cancel（级联取消）
- 取消任务时自动通知所有相关 Agent
- 清理相关资源

### Task Scheduler（任务调度）
- 根据 Agent 能力分配任务
- 负载均衡，防止单个 Agent 过载

### A2A Coordinator（A2A 协调器）
- 管理 Agent 之间的通信
- 协调多 Agent 协作流程

---

## 💡 使用示例

### 示例 1：开发一个 Web 应用

```
用户：帮我开发一个博客系统

架构师：我来设计整体架构...
  - 前端：React + TypeScript
  - 后端：Python FastAPI
  - 数据库：PostgreSQL

后端开发：我来实现 API...
  - 用户认证：JWT
  - 文章管理：CRUD 接口
  - 评论系统：嵌套评论

前端开发：我来实现界面...
  - 响应式设计
  - 暗色模式
  - Markdown 编辑器

测试工程师：我来编写测试...
  - 单元测试覆盖率 > 80%
  - 端到端测试
  - 性能测试
```

### 示例 2：代码审查

```
用户：审查这段代码

测试工程师：发现以下问题...
  1. 缺少错误处理
  2. 变量命名不规范
  3. 缺少注释

后端开发：我来修复...
  - 添加 try-catch
  - 重命名变量
  - 添加文档字符串

测试工程师：审查通过 ✅
```

---

## ⚙️ 配置选项

### Agent 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `name` | Agent 名称 | 必填 |
| `role` | 角色（system/developer/reviewer） | developer |
| `model` | 使用的模型 | qwen3.5-plus |
| `temperature` | 温度（0-1） | 0.7 |
| `system_prompt` | 系统提示词 | 无 |
| `max_tokens` | 最大输出长度 | 2048 |

### 协作配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `rounds` | 对话轮数 | 5 |
| `auto_dialogue` | 自动对话 | true |
| `timeout` | 超时时间（秒） | 300 |

---

## 🔍 故障排查

### 问题：Agent 列表为空

**解决：**
1. 检查 `configs/team.json` 是否存在
2. 检查 API 服务是否正常运行
3. 刷新页面（Ctrl + F5）

### 问题：多 Agent 对话无响应

**解决：**
1. 检查 API Key 是否配置正确
2. 检查网络连接
3. 查看服务器日志

### 问题：Agent 回复质量差

**解决：**
1. 调整 `temperature` 参数（降低更稳定）
2. 优化 `system_prompt`
3. 使用更强大的模型

---

## 📞 技术支持

- **文档：** `docs/` 目录
- **日志：** 查看服务器输出
- **问题反馈：** GitHub Issues

---

_最后更新：2026-03-19_
