# M6 工作流引擎开发计划

**创建时间：** 2026-03-19 20:30  
**负责人：** ai2 (Builder) + ai3 (Reviewer)  
**优先级：** P0  
**预计工时：** 16-20 小时

---

## 📋 开发目标

完善 YM-CODE 工作流引擎，实现：
1. State Tracker 状态追踪
2. 级联取消功能
3. 任务调度优化
4. A2A 协作流程

---

## 🏗️ 技术架构

### 核心模块

```
ymcode/workflow/
├── state_tracker.py      # 状态追踪器
├── cascade_cancel.py     # 级联取消
├── scheduler.py          # 任务调度器
├── a2a_coordinator.py    # A2A 协调器
└── __init__.py
```

### 依赖关系

- ✅ `ymcode/queue/task_queue.py` - 任务队列
- ✅ `ymcode/metrics/collector.py` - 指标收集
- ✅ `ymcode/events/bus.py` - 事件总线
- ✅ `ymcode/mcp/host.py` - MCP Host
- ⏳ `ymcode/workflow/` - 工作流引擎（新建）

---

## 📝 开发任务

### Phase 1: State Tracker (4h)

**目标：** 实现任务状态追踪器

**功能：**
- [ ] 任务状态历史记录
- [ ] 状态转换验证
- [ ] 状态查询 API
- [ ] 状态持久化

**文件：**
- `ymcode/workflow/state_tracker.py`

**API：**
```python
tracker = StateTracker()
tracker.record_state(task_id, "PENDING")
tracker.get_history(task_id)
tracker.get_current_state(task_id)
```

### Phase 2: 级联取消 (4h)

**目标：** 实现任务取消的级联处理

**功能：**
- [ ] 父子任务关系追踪
- [ ] 取消传播逻辑
- [ ] 取消确认机制
- [ ] 取消事件通知

**文件：**
- `ymcode/workflow/cascade_cancel.py`

**API：**
```python
canceller = CascadeCanceller(task_queue)
await canceller.cancel_with_children(task_id)
```

### Phase 3: 任务调度优化 (4h)

**目标：** 优化任务调度策略

**功能：**
- [ ] 优先级调度
- [ ] 公平调度（防饿死）
- [ ] 并发控制
- [ ] 资源配额管理

**文件：**
- `ymcode/workflow/scheduler.py`

**调度策略：**
- 优先级队列（高优先级优先）
- 时间片轮转（防饿死）
- 并发限制（最多 N 个并行任务）

### Phase 4: A2A 协调器 (4h)

**目标：** 实现多 Agent 协作流程

**功能：**
- [ ] 任务分配策略
- [ ] Agent 负载均衡
- [ ] 任务交接协议
- [ ] 协作事件通知

**文件：**
- `ymcode/workflow/a2a_coordinator.py`

**API：**
```python
coordinator = A2ACoordinator(agents=['ai1', 'ai2', 'ai3'])
await coordinator.assign_task(task, strategy='round_robin')
```

### Phase 5: 集成测试 (2h)

**目标：** 完整的功能测试

**测试用例：**
- [ ] State Tracker 状态记录
- [ ] 级联取消功能
- [ ] 调度策略验证
- [ ] A2A 任务分配
- [ ] 性能基准测试

**文件：**
- `tests/test_workflow.py`

### Phase 6: 文档 (2h)

**目标：** 完整的使用文档

**文档：**
- [ ] `docs/WORKFLOW_GUIDE.md` - 使用指南
- [ ] `reports/M6-COMPLETE-REPORT.md` - 完成报告
- [ ] API 文档（自动生成）

---

## 📊 验收标准

### 功能要求

- [ ] State Tracker 准确记录所有状态变化
- [ ] 级联取消正确传播到子任务
- [ ] 调度器支持优先级 + 公平调度
- [ ] A2A 协调器正确分配任务

### 性能要求

- [ ] 状态记录延迟 < 10ms
- [ ] 级联取消传播 < 100ms
- [ ] 调度决策 < 50ms
- [ ] 支持 1000+ 并发任务

### 代码质量

- [ ] 测试覆盖 > 90%
- [ ] 代码审查通过
- [ ] 文档完整

---

## 📁 文件结构

```
YM-CODE/
├── ymcode/workflow/
│   ├── __init__.py
│   ├── state_tracker.py
│   ├── cascade_cancel.py
│   ├── scheduler.py
│   └── a2a_coordinator.py
│
├── tests/test_workflow.py
├── docs/WORKFLOW_GUIDE.md
└── reports/M6-COMPLETE-REPORT.md
```

---

## 🚀 启动命令

```bash
# 运行工作流引擎测试
pytest tests/test_workflow.py -v

# 启动 Dashboard（包含工作流 API）
python start_dashboard.py
```

---

## ⚠️ 风险与依赖

### 风险
1. 级联取消可能导致大量任务同时取消
2. 调度策略可能影响现有任务执行
3. A2A 协调需要所有 Agent 支持

### 依赖
1. 任务队列模块稳定
2. 事件总线正常
3. MCP Host 正常

---

## 📅 时间估算

| 阶段 | 工时 | 累计 |
|------|------|------|
| Phase 1 | 4h | 4h |
| Phase 2 | 4h | 8h |
| Phase 3 | 4h | 12h |
| Phase 4 | 4h | 16h |
| Phase 5 | 2h | 18h |
| Phase 6 | 2h | 20h |

**总计：** 20 小时

---

_下一步：开始 Phase 1 State Tracker 实现_
