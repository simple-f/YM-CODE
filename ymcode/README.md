# 🔮 YM-CODE

> **Your Mind, Extended.** 你的编程伙伴，你的思维延伸。

[![Version](https://img.shields.io/badge/version-0.1.0--aurora-8B5CF6)](https://github.com/ym-code/ym-code)
[![License](https://img.shields.io/badge/license-MIT-3B82F6)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-165%20passed-10B810)](tests/)
[![Skills](https://img.shields.io/badge/skills-32+-F59E0B)](skills/)

---

## ✨ 为什么选择 YM-CODE？

### 🎯 我们不一样

- **有个性** - 不是冷冰冰的工具，是懂你的编程伙伴
- **超高效** - 165 个测试 100% 通过，稳如老狗
- **无限扩展** - 32+ 内置技能 + 开放技能市场
- **长期记忆** - 越用越懂你，越用越好用
- **完全开源** - 代码透明，可定制，免费

### 🚀 核心能力

```
🔍 智能搜索     - Web/文件/代码，想搜啥搜啥
💻 代码助手     - 补全/审查/重构/调试，样样精通
🗄️ 数据库       - MySQL/PostgreSQL，一键操作
🐳 Docker       - 容器管理，轻松搞定
📝 格式化       - Python/JS/TS，自动美化
🧠 长期记忆     - 记住你的习惯，越用越顺手
⚡ 自我进化     - 每次交互都在学习成长
```

---

## 🎨 快速开始

### 安装

```bash
# Python 包安装
pip install ym-code

# 或者开发安装
pip install -e .[dev]

# 验证安装
ym-code --version
```

### 配置

```bash
# 生成配置文件
ym-code config init

# 编辑配置（推荐）
# 编辑 ~/.ym-code/config.yaml
```

### 使用

```bash
# CLI 模式
ym-code "帮我分析这个项目"

# 交互模式
ym-code interactive

# VSCode 插件
# 安装 vscode-extension/ym-code-0.1.0.vsix
```

---

## 📁 项目结构

```
ym-code/
├── core/              # 核心引擎
├── skills/            # 技能系统（32+ 技能）
├── tools/             # 工具集合
├── memory/            # 记忆系统
├── cli/               # 命令行界面
├── extensions/        # 扩展系统
├── config/            # 配置文件
│   ├── ym-settings.yaml   # 主配置
│   └── skills.yaml        # 技能配置
└── workspace/         # 工作空间
```

---

## 🛠️ 技能系统

### 内置技能（32+）

**核心技能：**
- Search - Web/文件/代码搜索
- HTTP - HTTP 请求客户端
- Shell - Shell 命令执行
- CodeAnalysis - 代码质量分析
- Database - 数据库操作
- Formatter - 代码格式化
- Docker - Docker 管理
- Memory - 记忆管理
- SelfImprovement - 自我改进

**MCP 工具（21+）：**
- filesystem, git, github, database, brave-search, memory...

**CLI 命令（8 个）：**
- help, clear, status, config, read, write, edit, search

**VSCode 命令（8 个）：**
- ask, explain, refactor, debug, test, review, showPanel, clearHistory

### 技能示例

```python
from ymcode.skills import SearchSkill, CodeAnalysisSkill

# 搜索技能
search = SearchSkill()
result = await search.execute({
    'query': 'Python async best practices',
    'source': 'web'
})

# 代码分析技能
analyzer = CodeAnalysisSkill()
result = await analyzer.execute({
    'code': 'def hello():\n    print("world")',
    'language': 'python',
    'analysis_type': 'quality'
})
```

---

## 🌟 品牌理念

**YM** = **Y**our **M**ind（你的思维）  
**CODE** = 代码、编程、创造

我们不只是写代码，我们是在：
- 延伸你的思维
- 放大你的创造力
- 释放你的潜力

**品牌色：**
- 🟣 极光紫 `#8B5CF6` - 智慧、创造力
- ⚫ 深空黑 `#0F172A` - 专业、可靠
- 🔵 电光蓝 `#3B82F6` - 科技、速度

---

## 📚 文档

- [🚀 快速开始](docs/QUICKSTART.md)
- [📖 使用指南](docs/USAGE.md)
- [🧩 技能系统](docs/SKILLS.md)
- [🔧 配置说明](docs/CONFIG.md)
- [🌐 API 文档](docs/API.md)

---

## 🤝 社区

- [GitHub Issues](https://github.com/ym-code/ym-code/issues) - 问题反馈
- [Discord](https://discord.gg/ym-code) - 社区交流
- [技能市场](https://skills.ym-code.dev) - 下载第三方技能

---

## 📊 成果展示

**今日开发（2026-03-13）：**
- ✅ 13 个核心模块完成
- ✅ 165 个测试 100% 通过
- ✅ ~9100 行代码
- ✅ 13 份完整文档
- ✅ 32+ 个工具/技能
- ✅ 最终评分 100/100

---

## 🎯 路线图

### v0.1 Aurora（当前版本）
- ✅ 核心功能完成
- ✅ 技能系统建立
- ✅ 基础文档完善

### v0.2 Nebula（下一版本）
- [ ] 技能市场上线
- [ ] VSCode 插件完善
- [ ] 性能优化

### v1.0 Galaxy（未来版本）
- [ ] 完整生态系统
- [ ] 1000+ 技能
- [ ] 100 万 + 用户

---

## 📄 许可证

MIT License - 完全开源，免费使用

---

## 👥 团队

**YM-CODE Team** - 让每个开发者都拥有 AI 超能力

---

<div align="center">

**🔮 YM-CODE - Your Mind, Extended.**

[文档](docs/) | [技能](skills/) | [社区](https://discord.gg/ym-code)

</div>
