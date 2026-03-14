# YM-CODE CLI 使用指南

**命令行管理 Agent 和任务！** 🚀

---

## 🎉 新增功能

### Agent CLI 命令

| 命令 | 功能 | 示例 |
|------|------|------|
| **status** | 查看 Agent 状态 | `ymcode agent status` |
| **memory** | 查看共享记忆 | `ymcode agent memory` |
| **tasks** | 查看任务列表 | `ymcode agent tasks` |
| **create** | 创建任务 | `ymcode agent create "任务"` |
| **complete** | 完成任务 | `ymcode agent complete 1` |
| **search** | 搜索记忆 | `ymcode agent search "关键词"` |
| **stats** | 查看统计 | `ymcode agent stats` |
| **export** | 导出数据 | `ymcode agent export` |
| **import** | 导入数据 | `ymcode agent import backup.json` |
| **clean** | 清理旧数据 | `ymcode agent clean` |

---

## 🚀 快速开始

### 1. 查看 Agent 状态

```bash
python -m ymcode agent status
```

**输出示例：**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          Agent 状态                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 名称   │ 角色     │ 状态 │ 记忆 │ 完成任务 │
├────────┼──────────┼──────┼──────┼──────────┤
│ builder│ Builder  │ idle │  5   │    10    │
│ reviewer│ Reviewer│ idle │  3   │     8    │
└────────┴──────────┴──────┴──────┴──────────┘
```

---

### 2. 查看共享记忆

```bash
# 查看最近 10 条
python -m ymcode agent memory

# 查看最近 20 条
python -m ymcode agent memory --limit 20
```

**输出示例：**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    共享记忆 (最近 10 条)              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ • [note] 项目使用 Python 3.13       │
│ • [note] 测试框架是 pytest          │
│ • [task] 创建任务 #1: 实现登录      │
└─────────────────────────────────────┘
```

---

### 3. 查看任务列表

```bash
python -m ymcode agent tasks
```

**输出示例：**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              任务列表                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ID │ 标题        │ 状态     │ 分配给 │ 完成时间│
├────┼─────────────┼──────────┼────────┼─────────┤
│ 1  │ 实现登录    │ completed│ builder│ 14:00   │
│ 2  │ 代码审查    │ pending  │ -      │ -       │
└────┴─────────────┴──────────┴────────┴─────────┘
```

---

### 4. 创建任务

```bash
# 创建任务
python -m ymcode agent create "实现用户认证"

# 分配给特定 Agent
python -m ymcode agent create "代码审查" --assign-to reviewer
```

**输出：**
```
✅ 任务已创建 #1
   标题：实现用户认证
   分配给：builder
```

---

### 5. 完成任务

```bash
# 完成任务
python -m ymcode agent complete 1

# 添加结果说明
python -m ymcode agent complete 1 --result "已完成所有功能"
```

**输出：**
```
✅ 任务 #1 已完成
   结果：已完成所有功能
```

---

### 6. 搜索记忆

```bash
# 搜索关键词
python -m ymcode agent search "Python"

# 限制显示数量
python -m ymcode agent search "测试" --limit 5
```

**输出示例：**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    搜索结果：Python                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ • [builder] 项目使用 Python 3.13    │
│ • [reviewer] Python 代码规范        │
└─────────────────────────────────────┘
```

---

### 7. 查看统计

```bash
python -m ymcode agent stats
```

**输出示例：**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          统计信息                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 总记忆数：50                         │
│ 任务状态：                           │
│   - pending: 5                       │
│   - completed: 20                    │
│ 活跃 Agent: 2                        │
└─────────────────────────────────────┘
```

---

### 8. 导出数据

```bash
# 导出到 backup.json
python -m ymcode agent export

# 导出到指定文件
python -m ymcode agent export --output my-backup.json
```

**输出：**
```
✅ 数据已导出到 backup.json
```

---

### 9. 导入数据

```bash
# 导入数据
python -m ymcode agent import backup.json

# 导入前清空现有数据
python -m ymcode agent import backup.json --clear
```

**输出：**
```
✅ 数据已从 backup.json 导入
```

---

### 10. 清理旧数据

```bash
# 清理 30 天前的记忆
python -m ymcode agent clean
```

**输出：**
```
✅ 已清理 15 条旧记忆（>30 天）
```

---

## 📋 完整命令列表

### 基本信息

```bash
# 查看所有命令
python -m ymcode agent --help

# 查看具体命令帮助
python -m ymcode agent status --help
```

---

### Agent 管理

```bash
# 查看状态
python -m ymcode agent status

# 查看记忆
python -m ymcode agent memory [--limit N]

# 查看任务
python -m ymcode agent tasks [--limit N]
```

---

### 任务管理

```bash
# 创建任务
python -m ymcode agent create "任务标题" [--assign-to agent]

# 完成任务
python -m ymcode agent complete TASK_ID [--result "结果"]
```

---

### 数据管理

```bash
# 搜索记忆
python -m ymcode agent search "关键词" [--limit N]

# 查看统计
python -m ymcode agent stats

# 导出数据
python -m ymcode agent export [--output FILE]

# 导入数据
python -m ymcode agent import FILE [--clear]

# 清理旧数据
python -m ymcode agent clean
```

---

## 🎯 使用场景

### 场景 1：日常工作流程

```bash
# 1. 早上查看状态
python -m ymcode agent status

# 2. 查看待办任务
python -m ymcode agent tasks

# 3. 创建新任务
python -m ymcode agent create "实现功能 A"

# 4. 完成的任务标记
python -m ymcode agent complete 5 --result "已完成"

# 5. 下班前查看统计
python -m ymcode agent stats
```

---

### 场景 2：项目交接

```bash
# 1. 导出所有数据
python -m ymcode agent export project-backup.json

# 2. 交给同事
# 同事导入
python -m ymcode agent import project-backup.json
```

---

### 场景 3：查找历史信息

```bash
# 搜索相关记忆
python -m ymcode agent search "用户认证"

# 查看相关任务
python -m ymcode agent tasks | findstr "认证"
```

---

### 场景 4：定期维护

```bash
# 1. 清理旧数据
python -m ymcode agent clean

# 2. 导出备份
python -m ymcode agent export monthly-backup.json

# 3. 查看统计
python -m ymcode agent stats
```

---

## 🔧 高级用法

### 组合命令

```bash
# 创建任务并查看
python -m ymcode agent create "新功能" && python -m ymcode agent tasks

# 搜索并导出
python -m ymcode agent search "Python" && python -m ymcode agent export search-results.json
```

---

### 脚本自动化

```bash
#!/bin/bash
# daily-backup.sh

# 导出备份
python -m ymcode agent export backup-$(date +%Y%m%d).json

# 清理旧数据
python -m ymcode agent clean

# 发送通知（示例）
echo "YM-CODE 备份完成"
```

---

## 📊 输出格式

### JSON 输出（计划中）

```bash
# 未来支持
python -m ymcode agent status --json
python -m ymcode agent tasks --json
```

---

### CSV 导出（计划中）

```bash
# 未来支持
python -m ymcode agent tasks --csv > tasks.csv
```

---

## ⚠️ 注意事项

### 1. 数据备份

- ✅ 定期导出数据
- ✅ 备份到安全位置
- ✅ 保留多个版本

---

### 2. 性能优化

- ⚠️ 大量数据时使用 --limit
- ⚠️ 定期清理旧数据
- ✅ 使用搜索而非全量查看

---

### 3. 数据安全

- ✅ 导入前确认来源
- ✅ 使用 --clear 前备份
- ✅ 检查导出文件权限

---

## 🎉 总结

### 常用命令

```bash
# 查看状态
python -m ymcode agent status

# 创建任务
python -m ymcode agent create "任务"

# 完成任务
python -m ymcode agent complete ID

# 搜索记忆
python -m ymcode agent search "关键词"

# 导出备份
python -m ymcode agent export
```

---

**CLI 让 Agent 管理更简单！** 🚀
