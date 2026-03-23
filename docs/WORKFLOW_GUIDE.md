# YM-CODE 工作流引擎使用指南

**版本：** 1.0.0  
**最后更新：** 2026-03-19

---

## 📖 简介

YM-CODE 工作流引擎提供多 Agent 协作的核心功能：

- 📊 **State Tracker** - 任务状态追踪
- 🔗 **Cascade Cancel** - 级联取消
- 📅 **Task Scheduler** - 任务调度
- 🤖 **A2A Coordinator** - 多 Agent 协调

---

## 🚀 快速开始

### 导入模块

```python
from ymcode.workflow import (
    StateTracker,
    CascadeCanceller,
    TaskScheduler,
    A2ACoordinator
)
```

### 初始化

```python
# 状态追踪器
tracker = StateTracker()

# 级联取消器
canceller = CascadeCanceller(task_queue, tracker)

# 任务调度器
scheduler = TaskScheduler(task_queue, tracker, max_concurrent=10)

# A2A 协调器
coordinator = A2ACoordinator(agents=['ai1', 'ai2', 'ai3'])
```

---

## 📊 State Tracker - 状态追踪

### 基本用法

```python
from ymcode.workflow import StateTracker, TaskState

tracker = StateTracker()

# 记录状态变化
tracker.record_state("task-1", TaskState.PENDING)
tracker.record_state("task-1", TaskState.RUNNING)
tracker.record_state("task-1", TaskState.COMPLETED)

# 获取当前状态
state = tracker.get_current_state("task-1")

# 获取状态历史
history = tracker.get_history("task-1")

# 获取所有 PENDING 任务
pending_tasks = tracker.get_tasks_by_state(TaskState.PENDING)
```

### 状态枚举

```python
TaskState.PENDING      # 待处理
TaskState.SCHEDULED    # 已调度
TaskState.RUNNING      # 进行中
TaskState.PAUSED       # 已暂停
TaskState.COMPLETED    # 已完成
TaskState.FAILED       # 失败
TaskState.CANCELLED    # 已取消
TaskState.TIMEOUT      # 超时
```

### 状态转换规则

```
PENDING → SCHEDULED | CANCELLED
SCHEDULED → RUNNING | CANCELLED | PENDING
RUNNING → COMPLETED | FAILED | CANCELLED | TIMEOUT | PAUSED
PAUSED → RUNNING | CANCELLED
FAILED → PENDING (重试)
TIMEOUT → PENDING (重试)
COMPLETED → (终态)
CANCELLED → (终态)
```

### 持久化

```python
# 自定义存储路径
tracker = StateTracker(storage_path=Path("data/my_state.json"))

# 获取统计
stats = tracker.get_stats()
print(stats)
# {
#   "total_tasks": 100,
#   "state_distribution": {"PENDING": 10, "RUNNING": 5, ...},
#   "total_history_records": 350
# }
```

---

## 🔗 Cascade Cancel - 级联取消

### 基本用法

```python
from ymcode.workflow import CascadeCanceller

canceller = CascadeCanceller(task_queue, tracker)

# 注册父子关系
canceller.register_parent_child("parent-1", "child-1")
canceller.register_parent_child("parent-1", "child-2")

# 级联取消（自动取消所有子任务）
results = await canceller.cancel_with_children("parent-1", reason="用户取消")

# 检查结果
for task_id, success in results.items():
    print(f"{task_id}: {'成功' if success else '失败'}")
```

### 获取子任务

```python
# 获取直接子任务
children = canceller.get_children("parent-1", recursive=False)

# 获取所有后代（递归）
all_descendants = canceller.get_children("parent-1", recursive=True)

# 获取父任务
parent = canceller.get_parent("child-1")
```

### 自定义取消处理器

```python
async def cleanup_task(task_id):
    """任务取消时的清理工作"""
    print(f"清理任务 {task_id} 的资源...")

canceller.register_cancel_handler("task-1", cleanup_task)

# 取消时会自动调用处理器
await canceller.cancel_with_children("task-1")
```

---

## 📅 Task Scheduler - 任务调度

### 基本用法

```python
from ymcode.workflow import TaskScheduler, SchedulingPolicy

# 创建调度器
scheduler = TaskScheduler(
    task_queue=queue,
    state_tracker=tracker,
    max_concurrent=10,
    policy=SchedulingPolicy.PRIORITY  # 优先级优先
)

# 启动后台调度
await scheduler.start()

# 停止调度
await scheduler.stop()
```

### 调度策略

```python
SchedulingPolicy.PRIORITY       # 优先级优先
SchedulingPolicy.FAIR           # 公平调度（防饿死）
SchedulingPolicy.DEADLINE       # 截止时间优先
SchedulingPolicy.CUSTOM         # 自定义
```

### 公平调度（防饿死）

```python
scheduler = TaskScheduler(policy=SchedulingPolicy.FAIR)

# 等待时间越长的任务优先级会自动提升
# 防止低优先级任务永远得不到执行
```

### 资源配额

```python
# 设置 Agent 并发限制
scheduler.set_quota("ai1", limit=5)  # ai1 最多 5 个并发
scheduler.set_quota("ai2", limit=3)  # ai2 最多 3 个并发
```

### 自定义调度器

```python
def my_custom_scheduler(tasks):
    """自定义调度逻辑"""
    # 返回选中的任务
    return tasks[0] if tasks else None

scheduler.register_custom_scheduler("default", my_custom_scheduler)
```

### 统计信息

```python
stats = scheduler.get_stats()
print(stats)
# {
#   "running_tasks": 5,
#   "max_concurrent": 10,
#   "policy": "PRIORITY",
#   "avg_wait_time_sec": 2.5
# }
```

---

## 🤖 A2A Coordinator - 多 Agent 协调

### 基本用法

```python
from ymcode.workflow import A2ACoordinator, AssignmentStrategy

# 创建协调器
coordinator = A2ACoordinator(
    agents=['ai1', 'ai2', 'ai3'],
    strategy=AssignmentStrategy.ROUND_ROBIN  # 轮询
)

# 分配任务
from ymcode.queue import Task
task = Task(title="写代码", assigned_to=None)

agent_name = await coordinator.assign_task(task)
print(f"任务分配给：{agent_name}")
```

### 分配策略

```python
AssignmentStrategy.ROUND_ROBIN      # 轮询
AssignmentStrategy.LEAST_LOADED     # 最少负载
AssignmentStrategy.PRIORITY_BASED   # 优先级匹配
AssignmentStrategy.CUSTOM           # 自定义
```

### 注册 Agent

```python
# 注册带能力的 Agent
coordinator.register_agent(
    "ai1",
    capabilities=["coding", "testing"],
    metadata={"gpu": True}
)

# 更新 Agent 状态
coordinator.update_agent_status(
    "ai1",
    status="busy",
    tasks_assigned=5
)
```

### 任务交接（Handoff）

```python
# 从一个 Agent 转移到另一个
success = await coordinator.handoff_task(
    task_id="task-1",
    from_agent="ai1",
    to_agent="ai2",
    reason="负载均衡"
)

# 查看交接历史
handoffs = coordinator.get_handoff_history(task_id="task-1")
```

### 优先级匹配

```python
from ymcode.queue import TaskPriority

# 高优先级任务会自动分配给成功率高的 Agent
critical_task = Task(title="紧急任务", priority=TaskPriority.CRITICAL)
agent = await coordinator.assign_task(critical_task, strategy=AssignmentStrategy.PRIORITY_BASED)
```

### 统计信息

```python
stats = coordinator.get_stats()
print(stats)
# {
#   "total_agents": 3,
#   "available_agents": 2,
#   "strategy": "ROUND_ROBIN",
#   "agents": {
#     "ai1": {"status": "busy", "tasks_assigned": 10, ...},
#     "ai2": {"status": "idle", "tasks_assigned": 5, ...}
#   }
# }
```

---

## 🔧 全局单例

工作流引擎提供全局单例函数：

```python
from ymcode.workflow import (
    get_state_tracker,
    get_cascade_canceller,
    get_scheduler,
    get_a2a_coordinator
)

# 获取全局实例
tracker = get_state_tracker()
canceller = get_cascade_canceller()
scheduler = get_scheduler()
coordinator = get_a2a_coordinator(agents=['ai1', 'ai2'])
```

---

## 🧪 测试

```bash
# 运行工作流引擎测试
cd YM-CODE
pytest tests/test_workflow.py -v
```

---

## 📊 Dashboard 集成

工作流引擎已集成到 Dashboard：

- **状态追踪** - 自动记录所有任务状态变化
- **级联取消** - Dashboard 取消任务时自动触发
- **任务调度** - Dashboard 显示调度统计
- **A2A 协调** - Dashboard 显示 Agent 分配情况

访问：http://localhost:8080/dashboard

---

## ⚠️ 注意事项

### 线程安全

所有组件都是线程安全的，可以在多线程环境中使用。

### 异步支持

级联取消和 A2A 协调需要异步调用：

```python
# ✅ 正确
await canceller.cancel_with_children(task_id)

# ❌ 错误
canceller.cancel_with_children(task_id)  # 缺少 await
```

### 持久化

State Tracker 会自动持久化到磁盘，重启后恢复状态。

### 资源清理

使用完毕后清理资源：

```python
await scheduler.stop()
canceller.unregister_task(task_id)
```

---

## 📞 API 参考

### State Tracker

| 方法 | 说明 |
|------|------|
| `record_state(task_id, to_state, ...)` | 记录状态 |
| `get_current_state(task_id)` | 获取当前状态 |
| `get_history(task_id)` | 获取历史 |
| `get_tasks_by_state(state)` | 按状态查询 |
| `is_valid_transition(from, to)` | 验证转换 |

### Cascade Cancel

| 方法 | 说明 |
|------|------|
| `register_parent_child(parent, child)` | 注册关系 |
| `get_children(task_id)` | 获取子任务 |
| `get_parent(task_id)` | 获取父任务 |
| `cancel_with_children(task_id)` | 级联取消 |
| `register_cancel_handler(task_id, handler)` | 注册处理器 |

### Task Scheduler

| 方法 | 说明 |
|------|------|
| `start()` | 启动调度 |
| `stop()` | 停止调度 |
| `set_quota(resource, limit)` | 设置配额 |
| `register_custom_scheduler(name, fn)` | 自定义调度器 |
| `get_stats()` | 获取统计 |

### A2A Coordinator

| 方法 | 说明 |
|------|------|
| `register_agent(name, ...)` | 注册 Agent |
| `assign_task(task)` | 分配任务 |
| `handoff_task(task_id, from, to)` | 任务交接 |
| `get_assigned_agent(task_id)` | 获取分配 Agent |
| `get_stats()` | 获取统计 |

---

_最后更新：2026-03-19_
