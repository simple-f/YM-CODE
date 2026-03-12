# YM-CODE VSCode 插件

> Next Generation AI Programming Assistant - 全面对标 Claude Code

## 🎯 功能特性

- ✅ **代码解释** - 选中代码，右键选择 "YM-CODE: Explain Code"
- ✅ **代码审查** - 选中代码，右键选择 "YM-CODE: Review Code"
- ✅ **AI 运行** - 快捷键 `Ctrl+Shift+Y` (Mac: `Cmd+Shift+Y`)

## 🚀 安装方法

### 方法 1：从市场安装（计划中）

```bash
# VSCode 扩展市场搜索 "YM-CODE"
```

### 方法 2：本地安装

```bash
cd extensions/vscode
npm install
npm run compile
# 在 VSCode 中按 F5 运行
```

## 📖 使用说明

### 代码解释

1. 选中一段代码
2. 右键点击
3. 选择 "YM-CODE: Explain Code"
4. 在侧边栏查看解释

### 代码审查

1. 选中一段代码
2. 右键点击
3. 选择 "YM-CODE: Review Code"
4. 查看审查报告（包含评分和改进建议）

### AI 运行

1. 选中代码
2. 按 `Ctrl+Shift+Y` (Mac: `Cmd+Shift+Y`)
3. AI 自动执行并提供建议

## 🔧 配置

在 `settings.json` 中添加：

```json
{
  "ym-code.apiUrl": "http://localhost:8000/api",
  "ym-code.timeout": 30000,
  "ym-code.showNotifications": true
}
```

## 📊 截图

（待添加）

## 🙏 致谢

- 基于 YM-CODE 项目
- 全面对标 Claude Code

## 📜 许可证

MIT
