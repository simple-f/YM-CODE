# YM-CODE 缺失的团队功能补充

**YM-CODE 专注本地，但需要这些团队增强功能！** 🚀

---

## ✅ 分工明确

| 功能 | YM-CODE | OpenClaw |
|------|---------|----------|
| **共享记忆** | ❌ 不需要 | ✅ 负责 |
| **权限管理** | ⚠️ 基础版 | ✅ 完整版 |
| **审计日志** | ⚠️ 本地版 | ✅ 团队版 |
| **多 Agent** | ❌ 不需要 | ✅ 负责 |
| **Git 协作** | ✅ 完整 | ⚠️ 路由 |

---

## ⚠️ YM-CODE 需要补充的功能

### P1 - 基础团队功能（30 分钟）

| 功能 | 说明 | 工作量 |
|------|------|--------|
| **1. 项目级配置** | 每个项目独立配置 | 10 分钟 |
| **2. 本地审计日志** | 记录操作历史 | 10 分钟 |
| **3. Git 工作流** | 团队 Git 规范 | 5 分钟 |
| **4. 导出/导入** | 配置迁移 | 5 分钟 |

---

## 🔧 功能 1：项目级配置

### 现状

```bash
# 当前配置在用户目录
~/.ymcode/config.json  # 全局配置
```

**问题：** 不同项目需要不同配置

### 改进

```bash
# 支持项目级配置
project/
├── .ymcode/
│   └── config.json  # 项目配置（优先级高）
└── src/

# 配置加载顺序
1. 项目配置 (.ymcode/config.json)
2. 用户配置 (~/.ymcode/config.json)
3. 默认配置
```

### 实现

创建 `ymcode/config/project_config.py`：

```python
#!/usr/bin/env python3
from pathlib import Path
import json

class ProjectConfig:
    """项目配置管理器"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.project_config_file = self.project_path / ".ymcode" / "config.json"
        self.user_config_file = Path.home() / ".ymcode" / "config.json"
    
    def load(self) -> dict:
        """加载配置（项目优先）"""
        config = {}
        
        # 1. 加载用户配置
        if self.user_config_file.exists():
            with open(self.user_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 2. 加载项目配置（覆盖）
        if self.project_config_file.exists():
            with open(self.project_config_file, 'r', encoding='utf-8') as f:
                project_config = json.load(f)
                config.update(project_config)
        
        return config
    
    def save_project_config(self, config: dict):
        """保存项目配置"""
        self.project_config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.project_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
```

---

## 🔧 功能 2：本地审计日志

### 现状

```bash
# 只有普通日志
~/.ymcode/logs/ymcode.log
```

**问题：** 无法追踪用户操作

### 改进

```bash
# 添加审计日志
~/.ymcode/logs/
├── ymcode.log         # 系统日志
└── audit.log          # 审计日志（用户操作）
```

### 实现

创建 `ymcode/utils/audit_logger.py`：

```python
#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_file: str = None):
        if log_file:
            self.log_file = Path(log_file)
        else:
            self.log_file = Path.home() / ".ymcode" / "logs" / "audit.log"
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, action: str, user: str = "default", details: dict = None):
        """记录审计日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "details": details or {}
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def log_command(self, command: str, user: str = "default"):
        """记录命令执行"""
        self.log("command_execute", user, {"command": command})
    
    def log_file_read(self, file_path: str, user: str = "default"):
        """记录文件读取"""
        self.log("file_read", user, {"file": file_path})
    
    def log_file_write(self, file_path: str, user: str = "default"):
        """记录文件写入"""
        self.log("file_write", user, {"file": file_path})
    
    def log_git_operation(self, operation: str, user: str = "default"):
        """记录 Git 操作"""
        self.log("git_operation", user, {"operation": operation})
    
    def get_history(self, limit: int = 100) -> list:
        """获取审计历史"""
        if not self.log_file.exists():
            return []
        
        entries = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
        
        return entries[-limit:]
```

---

## 🔧 功能 3：Git 工作流增强

### 现状

```bash
# 基础 Git 命令
> 执行 git status
> 执行 git commit -m "xxx"
```

**问题：** 缺少团队 Git 规范

### 改进

创建 `ymcode/tools/git_workflow.py`：

```python
#!/usr/bin/env python3
from .git_tools import GitTool

class GitWorkflow:
    """团队 Git 工作流"""
    
    def __init__(self):
        self.git = GitTool()
    
    async def start_feature(self, feature_name: str):
        """开始新功能"""
        # 1. 创建分支
        await self.git.execute("checkout", "-b", f"feature/{feature_name}")
        
        # 2. 记录
        print(f"✅ 开始功能：{feature_name}")
        print(f"   分支：feature/{feature_name}")
    
    async def commit_changes(self, message: str):
        """提交变更"""
        # 1. 添加文件
        await self.git.execute("add", ".")
        
        # 2. 提交
        await self.git.execute("commit", "-m", message)
        
        # 3. 记录
        print(f"✅ 提交：{message}")
    
    async def create_pull_request(self, title: str, description: str = ""):
        """创建 PR（GitHub）"""
        # 1. 推送分支
        await self.git.execute("push", "-u", "origin", "HEAD")
        
        # 2. 创建 PR（需要 GitHub API）
        print(f"✅ 创建 PR: {title}")
        print(f"   {description}")
    
    async def code_review(self, pr_url: str):
        """代码审查"""
        # 1. 获取 PR 变更
        # 2. 运行测试
        # 3. 代码质量检查
        pass
```

---

## 🔧 功能 4：配置导出/导入

### 现状

```bash
# 配置在 ~/.ymcode/
# 换电脑需要重新配置
```

**问题：** 配置迁移困难

### 改进

创建 `ymcode/utils/config_migration.py`：

```python
#!/usr/bin/env python3
import json
from pathlib import Path
import shutil

class ConfigMigration:
    """配置迁移工具"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".ymcode"
    
    def export_config(self, output_file: str):
        """导出配置"""
        export_data = {
            "version": "1.0",
            "config": {},
            "memories": []
        }
        
        # 导出配置
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                export_data["config"] = json.load(f)
        
        # 导出记忆
        memory_file = self.config_dir / "skills" / "memory" / "long_term.json"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                export_data["memories"] = json.load(f)
        
        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已导出：{output_file}")
    
    def import_config(self, input_file: str):
        """导入配置"""
        with open(input_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # 导入配置
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(import_data["config"], f, indent=2, ensure_ascii=False)
        
        # 导入记忆
        memory_dir = self.config_dir / "skills" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        memory_file = memory_dir / "long_term.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(import_data["memories"], f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已导入")
```

---

## 📋 实施清单

### P1 - 本周内（30 分钟）

- [ ] **项目级配置** - 10 分钟
  - 创建 `ymcode/config/project_config.py`
  - 支持项目配置覆盖
  - 测试配置加载

- [ ] **本地审计日志** - 10 分钟
  - 创建 `ymcode/utils/audit_logger.py`
  - 集成到工具执行
  - 添加查询命令

- [ ] **Git 工作流** - 5 分钟
  - 创建 `ymcode/tools/git_workflow.py`
  - 添加团队命令
  - 文档说明

- [ ] **配置迁移** - 5 分钟
  - 创建 `ymcode/utils/config_migration.py`
  - 导出/导入命令
  - 测试迁移

---

## 🎯 使用示例

### 项目级配置

```bash
# 项目 A（Python 项目）
project-a/
└── .ymcode/
    └── config.json
        {
          "default_language": "python",
          "test_framework": "pytest"
        }

# 项目 B（Node.js 项目）
project-b/
└── .ymcode/
    └── config.json
        {
          "default_language": "javascript",
          "test_framework": "jest"
        }
```

---

### 审计日志

```bash
# 查看操作历史
> 查看审计日志

# 输出
[2026-03-14 13:40:00] user:alice action:file_read file:src/main.py
[2026-03-14 13:41:00] user:alice action:command_execute command:pytest tests/
[2026-03-14 13:42:00] user:alice action:git_operation operation:commit
```

---

### Git 工作流

```bash
# 开始新功能
> 开始功能 user-authentication

# 提交变更
> 提交 "添加用户认证"

# 创建 PR
> 创建 PR "用户认证功能"
```

---

### 配置迁移

```bash
# 导出配置
> 导出配置到 backup.json

# 导入配置（新电脑）
> 导入配置从 backup.json
```

---

## 📊 对比：之前 vs 之后

| 功能 | 之前 | 之后 |
|------|------|------|
| **项目配置** | ❌ 全局统一 | ✅ 项目独立 |
| **审计日志** | ❌ 无 | ✅ 本地记录 |
| **Git 工作流** | ⚠️ 基础命令 | ✅ 团队规范 |
| **配置迁移** | ❌ 手动 | ✅ 一键导出 |

---

## ✅ 总结

### YM-CODE 专注本地团队增强

**✅ 需要补充：**
1. 项目级配置 - 10 分钟
2. 本地审计日志 - 10 分钟
3. Git 工作流增强 - 5 分钟
4. 配置导出/导入 - 5 分钟

**❌ 不需要：**
- 共享记忆 → OpenClaw
- 多 Agent → OpenClaw
- 权限管理 → OpenClaw
- 团队审计 → OpenClaw

---

**需要我立即实现这些功能吗？** 🚀

告诉我优先级，我马上开始！
