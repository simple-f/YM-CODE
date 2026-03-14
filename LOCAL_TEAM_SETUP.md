# YM-CODE 本地团队协作配置

**无需云端，本地即可团队协作！** 🚀

---

## 🎯 现状分析

### ✅ 已有功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **本地 Skills** | ✅ 9 个 | Shell/Search/HTTP 等 |
| **工具系统** | ✅ 18 个 | 文件/Git/测试等 |
| **跨平台** | ✅ | Win/Linux/Mac |
| **测试** | ✅ 100% | 95/95 通过 |
| **文档** | ✅ 20+ | 完整文档 |

---

### ⚠️ 缺失的团队功能

| 功能 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **多用户配置** | P0 | 小 | 每个成员独立配置 |
| **共享记忆** | P0 | 中 | 团队知识库 |
| **权限管理** | P1 | 中 | 读写权限控制 |
| **审计日志** | P1 | 小 | 操作记录 |
| **项目同步** | P1 | 中 | Git 集成 |
| **任务分配** | P2 | 大 | 任务系统 |
| **实时协作** | P2 | 大 | WebSocket |

---

## 🚀 快速配置（5 分钟）

### 步骤 1：创建团队配置

为每个团队成员创建独立配置：

```bash
# 团队目录结构
team-project/
├── .ymcode/
│   ├── config.json          # 团队配置
│   ├── members/
│   │   ├── alice.json       # 成员 1 配置
│   │   ├── bob.json         # 成员 2 配置
│   │   └── charlie.json     # 成员 3 配置
│   └── shared/
│       ├── memories.json    # 共享记忆
│       └── projects.json    # 项目配置
├── src/
├── tests/
└── README.md
```

---

### 步骤 2：配置团队成员

创建 `team-project/.ymcode/members/alice.json`：

```json
{
  "name": "Alice",
  "role": "developer",
  "skills": ["shell", "search", "formatter", "code-analysis"],
  "permissions": {
    "read": true,
    "write": true,
    "execute": true,
    "admin": false
  },
  "preferences": {
    "theme": "dark",
    "language": "zh-CN"
  }
}
```

---

### 步骤 3：配置共享记忆

创建 `team-project/.ymcode/shared/memories.json`：

```json
{
  "team_name": "YM-CODE Team",
  "created": "2026-03-14",
  "members": ["Alice", "Bob", "Charlie"],
  "shared_knowledge": [
    {
      "key": "api_endpoint",
      "value": "https://api.example.com",
      "created_by": "Alice",
      "created_at": "2026-03-14"
    },
    {
      "key": "database_url",
      "value": "postgresql://localhost:5432/ymcode",
      "created_by": "Bob",
      "created_at": "2026-03-14"
    }
  ],
  "project_notes": [
    "项目使用 Python 3.13",
    "测试框架：pytest",
    "代码风格：PEP 8"
  ]
}
```

---

### 步骤 4：配置团队权限

创建 `team-project/.ymcode/config.json`：

```json
{
  "team_mode": true,
  "team_name": "YM-CODE Team",
  "permissions": {
    "default_role": "developer",
    "roles": {
      "admin": {
        "read": true,
        "write": true,
        "execute": true,
        "admin": true,
        "manage_members": true
      },
      "developer": {
        "read": true,
        "write": true,
        "execute": true,
        "admin": false,
        "manage_members": false
      },
      "viewer": {
        "read": true,
        "write": false,
        "execute": false,
        "admin": false,
        "manage_members": false
      }
    }
  },
  "audit_log": {
    "enabled": true,
    "file": "logs/audit.log",
    "max_age_days": 30
  }
}
```

---

## 💡 团队协作场景

### 场景 1：共享配置

```bash
# Alice 配置 API 端点
> 记住 API 端点：https://api.example.com

# Bob 查看共享记忆
> 查看团队配置

# Charlie 使用共享配置
> 调用 API 获取数据
```

---

### 场景 2：代码审查

```bash
# Alice 提交代码
> 格式化 src/main.py
> 运行测试 tests/

# Bob 审查代码
> 分析 src/main.py 的代码质量
> 检查复杂度

# Charlie 合并
> 执行 git add src/main.py
> 执行 git commit -m "feat: 添加新功能"
> 执行 git push
```

---

### 场景 3：知识共享

```bash
# Alice 添加项目笔记
> 记住：项目使用 pytest 测试框架

# Bob 查询笔记
> 搜索关于测试的记忆

# Charlie 更新笔记
> 更新记忆：测试框架是 pytest 7.4+
```

---

## 🔧 立即可用的功能

### 1. 本地多用户（无需配置）

每个用户有自己的配置目录：

```bash
# 用户 A
~/.ymcode/  # A 的配置和记忆

# 用户 B
~/.ymcode/  # B 的配置和记忆
```

**隔离：** ✅ 完全独立  
**共享：** ❌ 需要手动配置

---

### 2. Git 协作（已有）

```bash
# 所有人都可以
> 执行 git status
> 执行 git pull
> 执行 git push

# 查看变更
> 执行 git diff
> 读取 CHANGELOG.md
```

---

### 3. 文件共享（已有）

```bash
# 读取共享文件
> 读取 docs/README.md

# 写入共享文档
> 写入 "会议记录" 到 docs/meeting-2026-03-14.md

# 搜索共享知识
> 搜索项目中的 TODO
```

---

## 📋 配置检查清单

### P0 - 立即配置（5 分钟）

- [ ] 创建团队目录
- [ ] 配置团队成员
- [ ] 设置共享记忆
- [ ] 测试 Git 协作

### P1 - 本周内（30 分钟）

- [ ] 配置权限管理
- [ ] 启用审计日志
- [ ] 设置项目同步
- [ ] 团队培训

### P2 - 可选功能

- [ ] 任务分配系统
- [ ] 实时协作
- [ ] Web 界面
- [ ] CI/CD 集成

---

## 🎯 最小可行团队配置

### 3 人团队快速启动

```bash
# 1. 克隆项目
git clone <repo-url> team-project
cd team-project

# 2. 创建团队配置
mkdir -p .ymcode/members
mkdir -p .ymcode/shared

# 3. 每个成员创建自己的配置
# Alice
cat > .ymcode/members/alice.json << 'EOF'
{
  "name": "Alice",
  "role": "admin",
  "skills": ["shell", "search", "formatter"]
}
EOF

# Bob
cat > .ymcode/members/bob.json << 'EOF'
{
  "name": "Bob",
  "role": "developer",
  "skills": ["shell", "test-runner", "git"]
}
EOF

# Charlie
cat > .ymcode/members/charlie.json << 'EOF'
{
  "name": "Charlie",
  "role": "developer",
  "skills": ["shell", "code-analysis", "http"]
}
EOF

# 4. 创建共享记忆
cat > .ymcode/shared/memories.json << 'EOF'
{
  "team_name": "YM-CODE Team",
  "members": ["Alice", "Bob", "Charlie"],
  "shared_knowledge": []
}
EOF

# 5. 测试
python -m ymcode
> 执行 git status
> 搜索团队成员
```

**完成！** 🎉

---

## 📊 对比：个人 vs 团队

| 功能 | 个人使用 | 团队使用 |
|------|----------|----------|
| **配置** | 无需配置 | 需要团队配置 |
| **记忆** | 个人记忆 | 共享记忆 |
| **权限** | 完全权限 | 角色权限 |
| **审计** | 可选 | 推荐启用 |
| **同步** | 本地 | Git + 共享 |

---

## 🚀 现在就能做的

### ✅ 立即可用

1. **Git 协作** - 已有 ✅
2. **文件共享** - 已有 ✅
3. **独立配置** - 已有 ✅
4. **代码审查** - 已有 ✅

### ⏳ 需要配置

1. **共享记忆** - 5 分钟
2. **权限管理** - 10 分钟
3. **审计日志** - 5 分钟

### 🔮 未来功能

1. **任务系统** - 开发中
2. **实时协作** - 计划中
3. **Web 界面** - 计划中

---

## 📝 总结

### 现状

**✅ 可以立即开始本地团队协作！**

- 个人配置独立
- Git 协作完整
- 文件共享可用
- 代码审查支持

### 缺失

**⚠️ 需要简单配置：**

- 共享记忆（5 分钟）
- 权限管理（10 分钟）
- 审计日志（5 分钟）

### 推荐

**3 人团队快速启动：**

```bash
# 1. 克隆项目
git clone <repo>
cd team-project

# 2. 创建成员配置
mkdir -p .ymcode/members

# 3. 每人创建自己的配置
# 4. 创建共享记忆
# 5. 开始协作！
```

---

**需要我帮你创建团队配置吗？** 🚀

告诉我团队成员名字，我帮你生成配置文件！
