# YM-CODE Session 管理优化方案

参考 Cat Café (OpenClaw) 的 Session 链管理经验

---

## 🎯 核心问题

当前 YM-CODE 的 Session 管理存在以下问题：

1. **内存存储** - Session 数据在内存中，重启丢失
2. **无任务状态** - 没有任务生命周期管理
3. **无 Handoff 协议** - Agent 之间交接不规范
4. **无 Review 机制** - 没有质量检查

---

## 📋 Cat Café 经验总结

### 1. Session 链架构

```
Session Chain:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Session 1 │ -> │   Session 2 │ -> │   Session 3 │
│   (Spec)    │    │   (Build)   │    │   (Review)  │
└─────────────┘    └─────────────┘    └─────────────┘
     ai2                ai2               ai3
```

**关键设计：**
- 每个阶段独立 Session
- Context 满 85% 自动交接班
- 新 Session 继承关键上下文

### 2. 任务生命周期

```
Task Lifecycle:
inbox → spec → build → review → done
```

**状态定义：**
- `inbox` - 新任务等待处理
- `spec` - 需求分析和规格定义
- `build` - 实现功能
- `review` - 代码审查和验证
- `done` - 完成

### 3. Handoff 5 件套

每次任务交接包含：

```markdown
1. 任务背景 (Context)
2. 已完成工作 (Done)
3. 待完成工作 (TODO)
4. 关键决策 (Decisions)
5. 参考资料 (References)
```

### 4. Review 评分标准

| 维度 | 权重 | 评分 |
|------|------|------|
| 功能完整性 | 30% | ✅/❌ |
| 代码质量 | 25% | 1-5 分 |
| 文档完善度 | 20% | 1-5 分 |
| 测试覆盖 | 15% | % |
| 性能表现 | 10% | 1-5 分 |

---

## 🚀 YM-CODE 优化方案

### Phase 1: 持久化存储

```python
# 使用 SQLite 存储 Session
import sqlite3

class SessionStore:
    def __init__(self, db_path="~/.ymcode/sessions.db"):
        self.db = sqlite3.connect(db_path)
        self._init_tables()
    
    def _init_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT,
                status TEXT
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)
```

### Phase 2: 任务状态管理

```python
class TaskStatus(Enum):
    INBOX = "inbox"
    SPEC = "spec"
    BUILD = "build"
    REVIEW = "review"
    DONE = "done"

class Task:
    def __init__(self, id: str, title: str, status: TaskStatus):
        self.id = id
        self.title = title
        self.status = status
        self.session_id = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
```

### Phase 3: Handoff 协议

```python
class Handoff:
    def __init__(self, from_agent: str, to_agent: str):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.context = ""
        self.done = []
        self.todo = []
        self.decisions = []
        self.references = []
    
    def to_markdown(self) -> str:
        return f"""
# Handoff: {self.from_agent} → {self.to_agent}

## 任务背景
{self.context}

## 已完成工作
{self.done}

## 待完成工作
{self.todo}

## 关键决策
{self.decisions}

## 参考资料
{self.references}
"""
```

### Phase 4: Review 流程

```python
class Reviewer:
    def __init__(self):
        self.criteria = {
            "功能完整性": 0.3,
            "代码质量": 0.25,
            "文档完善度": 0.2,
            "测试覆盖": 0.15,
            "性能表现": 0.1
        }
    
    def review(self, task: Task) -> dict:
        scores = {}
        for criterion in self.criteria:
            scores[criterion] = self._score(criterion, task)
        
        total = sum(scores[k] * self.criteria[k] for k in scores)
        
        return {
            "scores": scores,
            "total": total,
            "passed": total >= 4.0,
            "feedback": self._generate_feedback(scores)
        }
```

---

## 📊 实施计划

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| Phase 1 | SQLite 持久化 | 2 小时 |
| Phase 2 | 任务状态管理 | 3 小时 |
| Phase 3 | Handoff 协议 | 2 小时 |
| Phase 4 | Review 流程 | 4 小时 |
| Phase 5 | Web UI 集成 | 3 小时 |

**总计：** 14 小时

---

## 🎯 下一步行动

1. **立即实施 Phase 1** - 添加 SQLite 持久化
2. **测试 Session 恢复** - 重启后加载历史 Session
3. **实现任务状态** - 添加任务生命周期
4. **集成 Handoff** - ai2 → ai3 交接流程

---

_参考：OpenClaw Cat Café 项目经验_
_创建时间：2026-03-15_
