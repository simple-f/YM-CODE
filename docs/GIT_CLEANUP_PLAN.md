# Git 仓库清理计划

**分析时间：** 2026-03-16 15:58  
**目标：** 删除无用文件，保持仓库整洁

---

## 📋 待删除文件清单

### P0 - 立即删除

#### 1. 临时脚本文件 (scripts/)

**文件：**
- `scripts/add_routes.py` - 临时路由脚本（已无用）
- `scripts/quick_fix.py` - 临时修复脚本（已无用）
- `scripts/test_api.py` - 临时测试脚本（已无用）

**理由：** 临时脚本，功能已集成到主代码

**操作：** 删除整个 `scripts/` 目录

---

#### 2. 构建产物

**文件：**
- `ym_code.egg-info/` - Python 包构建产物

**理由：** 构建产物，不应提交到 Git

**操作：** 删除并添加到 .gitignore

---

### P1 - 建议删除

#### 3. 重复/过时的文档

**文件：**
- `docs/ARCHITECTURE_REVIEW.md` - 架构评审（已过时）
- `docs/CLI_SUMMARY.md` - CLI 总结（临时报告）
- `docs/COMPREHENSIVE_REVIEW.md` - 综合评审（临时报告）
- `docs/D_DRIVE_FIX_PLAN.md` - D 盘修复计划（已完成）
- `docs/D_DRIVE_FIX_REPORT.md` - D 盘修复报告（已完成）
- `docs/ENGINEERING_IMPROVEMENTS.md` - 工程改进（临时）
- `docs/LSP_COMPLETION_SUMMARY.md` - LSP 总结（临时）
- `docs/MCP_CLIENT_V2_SUMMARY.md` - MCP 总结（临时）
- `docs/MEMORY_SYSTEM_SUMMARY.md` - 记忆系统总结（临时）
- `docs/MISSING_FEATURES_ANALYSIS.md` - 缺失功能分析（临时）
- `docs/MULTI_AGENT_WORKSPACE_GUIDE.md` - 多 Agent 工作区（重复）
- `docs/P0-*.md` 系列 - P0 修复报告（已完成）
- `docs/PHASE3_SUMMARY.md` - Phase3 总结（已完成）
- `docs/PROJECT_CONTEXT_SUMMARY.md` - 项目上下文（临时）
- `docs/SHELL_FIX_REPORT.md` - Shell 修复报告（已完成）
- `docs/SHELL_FIX_SUMMARY.md` - Shell 修复总结（已完成）
- `docs/SKILLS_SYSTEM_SUMMARY.md` - 技能系统总结（临时）
- `docs/SYSTEM_DEFECTS_ANALYSIS.md` - 系统缺陷（临时）
- `docs/TASKS_FULL_REVIEW.md` - 任务评审（临时）
- `docs/TEST_FIX_SUMMARY.md` - 测试修复总结（已完成）
- `docs/TOOLS_EXPANSION_SUMMARY.md` - 工具扩展总结（临时）
- `docs/TOOLS_TEST_REPORT.md` - 工具测试报告（临时）
- `docs/WEB_INTERFACE_PLAN.md` - Web 界面计划（已完成）
- `docs/YM_CODE_IDENTITY.md` - 身份文档（临时）

**理由：** 临时报告、已完成的任务文档、重复内容

**操作：** 移动到 `docs/archive/` 或删除

---

#### 4. 已归档的旧文档

**文件：**
- `docs/archive/` 下的所有文件（已在 archive 中）

**理由：** 已归档，可以考虑彻底删除

**操作：** 保留 archive 或彻底删除

---

### P2 - 可选删除

#### 5. 过度详细的进度报告

**文件：**
- `docs/GITHUB_REFRESH_REPORT.md` - GitHub 刷新报告（可选）
- `docs/CODE_CLEANUP_REPORT.md` - 代码清理报告（可选）

**理由：** 过于详细的内部报告

**操作：** 可选删除

---

## 📊 删除统计

### 删除前

| 类型 | 数量 | 大小 |
|------|------|------|
| Python 文件 | 163 个 | ~1 MB |
| 文档文件 | 48 个 | ~500 KB |
| 临时文件 | 3 个 | ~10 KB |
| 构建产物 | 1 个目录 | ~50 KB |

### 删除后（预计）

| 类型 | 数量 | 减少 |
|------|------|------|
| Python 文件 | 160 个 | -3 |
| 文档文件 | 20 个 | -28 |
| 临时文件 | 0 个 | -100% |
| 构建产物 | 0 个 | -100% |

**总减少：** ~35 个文件，~200 KB

---

## ✅ 删除清单

### 立即删除（P0）

```bash
# 临时脚本
rm -rf scripts/

# 构建产物
rm -rf ym_code.egg-info/

# 添加到 .gitignore
echo "*.egg-info/" >> .gitignore
```

### 建议删除（P1）

```bash
# 临时/过时文档
rm docs/ARCHITECTURE_REVIEW.md
rm docs/CLI_SUMMARY.md
rm docs/COMPREHENSIVE_REVIEW.md
rm docs/D_DRIVE_FIX_*.md
rm docs/ENGINEERING_IMPROVEMENTS.md
rm docs/*_SUMMARY.md (保留核心)
rm docs/P0-*.md
rm docs/*_FIX_*.md
rm docs/*_ANALYSIS.md (临时分析)
```

### 保留的核心文档

```
docs/
├── ARCHITECTURE.md          ⭐ 核心架构
├── API.md                   ⭐ API 文档
├── SKILLS.md                ⭐ 技能文档
├── USAGE.md                 ⭐ 使用指南
├── SYSTEM_ARCHITECTURE.md   ⭐ 系统架构
├── MULTI_AGENT.md           ⭐ 多 Agent
├── WORKSPACE_GUIDE.md       ⭐ 工作区
├── AGENT_CONFIG_UI.md       ⭐ Agent 配置
├── DOCKER_USAGE.md          ⭐ Docker
├── v0.7.0_PLAN.md           ⭐ 版本计划
├── v0.7.0_PROGRESS.md       ⭐ 开发进度
├── REVIEW_FRAMEWORK.md      ⭐ 评审框架
├── TESTING_GUIDE.md         ⭐ 测试指南
├── GAP_ANALYSIS.md          ⭐ 差距分析
├── KNOWLEDGE_SYSTEM_GUIDE.md ⭐ 知识系统
├── GITHUB_REFRESH_REPORT.md ⭐ 仓库刷新
└── archive/                 归档文档
```

---

## 🎯 执行步骤

### 第 1 步：删除临时文件

```bash
# 删除 scripts 目录
Remove-Item -Recurse -Force scripts/

# 删除构建产物
Remove-Item -Recurse -Force ym_code.egg-info/
```

### 第 2 步：删除临时文档

```bash
# 删除临时报告
Get-ChildItem docs -Filter "*_SUMMARY.md" | Remove-Item
Get-ChildItem docs -Filter "P0-*.md" | Remove-Item
Get-ChildItem docs -Filter "*_FIX_*.md" | Remove-Item
Get-ChildItem docs -Filter "*_ANALYSIS.md" | Remove-Item -Exclude "GAP_ANALYSIS.md"
```

### 第 3 步：更新 .gitignore

```bash
# 添加构建产物
echo "*.egg-info/" >> .gitignore
echo "*.egg" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
```

### 第 4 步：提交清理

```bash
git add -A
git commit -m "chore: 删除无用文件

- 删除临时脚本 (scripts/)
- 删除构建产物 (ym_code.egg-info/)
- 删除临时文档 (*_SUMMARY.md, P0-*.md 等)
- 更新 .gitignore

清理效果:
✅ 减少 35+ 个文件
✅ 减少 200+ KB
✅ 仓库更整洁"
```

---

## ✅ 预期效果

**删除前：**
- 文档文件：48 个
- Python 文件：163 个
- 临时文件：3 个
- 构建产物：1 个目录

**删除后：**
- 文档文件：20 个（-58%）
- Python 文件：160 个（-2%）
- 临时文件：0 个（-100%）
- 构建产物：0 个（-100%）

**仓库更整洁，核心文档更突出！** ✅

---

**分析完成时间：** 2026-03-16 15:58  
**建议执行：** 立即删除 P0，建议删除 P1
