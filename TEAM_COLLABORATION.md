# YM-CODE 团队协作功能

**权限管理 + 任务分配 + 评论系统！** 🚀

---

## 🎉 已实现功能

### 1. 权限管理 ✅

| 角色 | 权限 | 说明 |
|------|------|------|
| **Admin** | 所有权限 | 团队管理 |
| **Developer** | 读写执行 + 任务管理 | 开发者 |
| **Viewer** | 只读 | 观察者 |
| **Guest** | 有限访问 | 访客 |

---

### 2. 任务系统 ✅

| 功能 | 说明 |
|------|------|
| **创建任务** | 标题/描述/优先级/截止日期 |
| **分配任务** | 分配给团队成员 |
| **任务状态** | pending/in_progress/completed/cancelled |
| **优先级** | low/normal/high/urgent |
| **标签** | 自定义标签分类 |
| **评论** | 任务讨论 |
| **附件** | 文件链接 |

---

### 3. 评论系统 ✅

| 功能 | 说明 |
|------|------|
| **添加评论** | 任务讨论 |
| **回复评论** | 嵌套回复 |
| **编辑评论** | 更新内容 |
| **删除评论** | 移除评论 |

---

## 🚀 使用方式

### CLI 命令

#### 团队成员管理

```bash
# 添加成员
python -m ymcode team add-member "张三" --user-id zhangsan --role developer

# 列出成员
python -m ymcode team list-members

# 按角色筛选
python -m ymcode team list-members --role developer

# 更新角色
python -m ymcode team update-role zhangsan admin

# 查看成员信息
python -m ymcode team member-info zhangsan

# 移除成员
python -m ymcode team remove-member zhangsan
```

---

#### 任务管理

```bash
# 创建任务
python -m ymcode task create "实现用户认证" \
  --desc "添加登录和注册功能" \
  --assign-to zhangsan \
  --priority high \
  --due 2026-03-20 \
  --tag backend \
  --tag security

# 列出任务
python -m ymcode task list

# 按状态筛选
python -m ymcode task list --status completed

# 按优先级筛选
python -m ymcode task list --priority urgent

# 查看任务详情
python -m ymcode task show 1

# 分配任务
python -m ymcode task assign 1 lisi

# 完成任务
python -m ymcode task complete 1 --result "功能已完成"

# 添加评论
python -m ymcode task comment 1 "这个功能很重要"

# 搜索任务
python -m ymcode task search "认证"

# 查看统计
python -m ymcode task stats
```

---

## 📋 详细示例

### 示例 1：创建团队

```python
from ymcode.team import TeamManager, Role

# 创建团队
team_mgr = TeamManager("YM-CODE Team")

# 添加成员
team_mgr.add_member("zhangsan", "张三", Role.ADMIN)
team_mgr.add_member("lisi", "李四", Role.DEVELOPER)
team_mgr.add_member("wangwu", "王五", Role.DEVELOPER)
team_mgr.add_member("zhaoliu", "赵六", Role.VIEWER)
```

---

### 示例 2：权限检查

```python
from ymcode.team import AccessControl

access = AccessControl(team_mgr)

# 检查权限
if access.can_write("zhangsan"):
    print("张三可以写文件")

if access.can_manage_tasks("lisi"):
    print("李四可以管理任务")

if access.can_admin("wangwu"):
    print("王五是管理员")
else:
    print("王五不是管理员")
```

---

### 示例 3：任务工作流

```python
from ymcode.team import TaskManager

task_mgr = TaskManager()

# 1. 创建任务
task = task_mgr.create_task(
    title="实现用户认证",
    description="添加登录和注册功能",
    assigned_to="zhangsan",
    priority="high",
    due_date="2026-03-20",
    tags=["backend", "security"]
)

# 2. 添加评论
task_mgr.add_comment(
    task.id,
    "lisi",
    "李四",
    "需要注意安全性"
)

# 3. 更新状态
task_mgr.update_task(
    task.id,
    status="in_progress"
)

# 4. 完成任务
task_mgr.complete_task(
    task.id,
    "zhangsan",
    "功能已完成，测试通过"
)
```

---

### 示例 4：任务筛选

```python
# 列出所有任务
all_tasks = task_mgr.list_tasks()

# 按状态筛选
pending_tasks = task_mgr.list_tasks(status="pending")
completed_tasks = task_mgr.list_tasks(status="completed")

# 按分配用户筛选
zhangsan_tasks = task_mgr.list_tasks(assigned_to="zhangsan")

# 按优先级筛选
urgent_tasks = task_mgr.list_tasks(priority="urgent")

# 按标签筛选
backend_tasks = task_mgr.list_tasks(tags=["backend"])
```

---

### 示例 5：任务统计

```python
stats = task_mgr.get_task_stats()

print(f"总任务数：{stats['total']}")
print(f"按状态：{stats['by_status']}")
print(f"按优先级：{stats['by_priority']}")
print(f"按用户：{stats['by_user']}")
```

**输出示例：**
```
总任务数：20
按状态：{'pending': 5, 'in_progress': 3, 'completed': 10, 'cancelled': 2}
按优先级：{'low': 3, 'normal': 10, 'high': 5, 'urgent': 2}
按用户：{'zhangsan': 8, 'lisi': 7, 'wangwu': 5}
```

---

## 🎯 实际应用场景

### 场景 1：敏捷开发

```bash
# 1. 创建 Sprint 任务
python -m ymcode task create "Sprint 26-1" --tag sprint

# 2. 分配任务
python -m ymcode task assign 1 zhangsan
python -m ymcode task assign 2 lisi

# 3. 每日站会查看
python -m ymcode task list --status in_progress

# 4. 完成时更新
python -m ymcode task complete 1 --result "已完成"
```

---

### 场景 2：代码审查流程

```bash
# 1. 创建审查任务
python -m ymcode task create "代码审查 - PR #123" \
  --assign-to lisi \
  --priority high \
  --tag review

# 2. 添加评论
python -m ymcode task comment 3 "发现 2 个问题需要修复"

# 3. 审查完成
python -m ymcode task complete 3 --result "审查通过"
```

---

### 场景 3：Bug 追踪

```bash
# 1. 报告 Bug
python -m ymcode task create "登录页面崩溃" \
  --priority urgent \
  --assign-to zhangsan \
  --tag bug \
  --tag frontend

# 2. 修复中
python -m ymcode task assign 4 zhangsan

# 3. 修复完成
python -m ymcode task complete 4 --result "已修复"
```

---

## 📊 团队协作最佳实践

### 1. 角色分配

- **Admin**: 1-2 人（团队负责人）
- **Developer**: 核心成员
- **Viewer**: 产品/测试
- **Guest**: 临时成员

---

### 2. 任务优先级

| 优先级 | 使用场景 | 响应时间 |
|--------|----------|----------|
| **Urgent** 🔴 | 生产事故 | 立即 |
| **High** 🟡 | 重要功能 | 24 小时 |
| **Normal** 🟢 | 日常任务 | 1 周 |
| **Low** 🔵 | 优化建议 | 有空时 |

---

### 3. 任务状态流转

```
pending → in_progress → completed
              ↓
         cancelled
```

---

### 4. 评论规范

```bash
# 清晰的评论
python -m ymcode task comment 1 "已完成前端开发，待测试"

# 包含上下文
python -m ymcode task comment 1 "发现性能问题，需要优化数据库查询"

# @提及相关人员
python -m ymcode task comment 1 "@zhangsan 请审查代码"
```

---

## 🔧 高级功能

### 导出数据

```python
# 导出团队配置
team_mgr.export_config("team-backup.json")

# 导出任务
task_mgr.export_tasks("tasks-backup.json")

# 导出特定任务
task_mgr.export_tasks("important-tasks.json", task_ids=[1, 2, 3])
```

---

### 导入数据

```python
# 导入团队配置
team_mgr.import_config("team-backup.json")

# 导入任务（合并）
task_mgr.import_tasks("tasks-backup.json", merge=True)

# 导入任务（替换）
task_mgr.import_tasks("tasks-backup.json", merge=False)
```

---

### 搜索功能

```python
# 搜索任务
results = task_mgr.search_tasks("认证")

# 搜索结果包含：
# - 标题匹配
# - 描述匹配
# - 标签匹配
# - 评论匹配
```

---

## ⚠️ 注意事项

### 1. 权限安全

- ✅ 定期检查权限分配
- ✅ Admin 角色限制在 2 人以内
- ✅ 离职成员及时移除

---

### 2. 数据备份

- ✅ 每周导出备份
- ✅ 重要任务单独导出
- ✅ 保留历史版本

---

### 3. 性能优化

- ⚠️ 大量任务时使用筛选
- ⚠️ 定期清理已完成任务
- ✅ 使用标签分类

---

## 📝 总结

### 已实现

- ✅ 权限管理（4 个角色）
- ✅ 任务系统（完整工作流）
- ✅ 评论系统（嵌套回复）
- ✅ CLI 命令（10+ 个）
- ✅ 搜索功能
- ✅ 统计功能
- ✅ 导出/导入

### 可以使用

```bash
# 团队管理
python -m ymcode team add-member "张三" --user-id zhangsan

# 任务管理
python -m ymcode task create "新功能" --assign-to zhangsan

# 查看统计
python -m ymcode task stats
```

---

**团队协作功能让 YM-CODE 更适合企业使用！** 🏢🚀
