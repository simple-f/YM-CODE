# YM-CODE VSCode Extension

**AI Programming Assistant** - 下一代 AI 编程助手

---

## 🎯 功能特性

### 核心功能

- 🤖 **AI 对话** - 与 AI 助手实时对话
- 📖 **代码解释** - 理解复杂代码逻辑
- 🔧 **代码重构** - 提高代码质量
- 🐛 **调试助手** - 找出并修复 bug
- ✅ **测试生成** - 自动编写单元测试
- 📝 **Code Review** - 提供改进建议

### 便捷操作

- **右键菜单** - 选中代码后右键快速操作
- **快捷键** - `Ctrl+Shift+Y` 快速提问
- **侧边栏** - 集成到 VSCode 侧边栏
- **上下文感知** - 自动获取选中代码

---

## 🚀 快速开始

### 安装

1. 下载 `.vsix` 文件
2. 在 VSCode 中：`Extensions` → `...` → `Install from VSIX...`
3. 选择下载的 `.vsix` 文件

### 配置

打开设置 (`Ctrl+,`)，搜索 `YM-CODE`：

- **API Endpoint** - YM-CODE API 地址（默认：`http://localhost:8080`）
- **Model** - AI 模型（默认：`qwen3.5-plus`）
- **Max Tokens** - 最大 Token 数（默认：4000）
- **Theme** - 主题（默认：auto）

### 使用

#### 方法 1：侧边栏

1. 点击侧边栏的 **YM-CODE** 图标
2. 在输入框中输入问题
3. 按 `Ctrl+Enter` 或点击 **发送**

#### 方法 2：右键菜单

1. 选中一段代码
2. 右键选择：
   - **YM-CODE: Explain Code** - 解释代码
   - **YM-CODE: Refactor Code** - 重构代码
   - **YM-CODE: Debug Code** - 调试代码

#### 方法 3：快捷键

- `Ctrl+Shift+Y` - 快速提问（基于选中代码）
- `Ctrl+Shift+M` - 打开 YM-CODE 面板

---

## 📋 命令列表

| 命令 | 快捷键 | 说明 |
|------|--------|------|
| `YM-CODE: Ask AI` | `Ctrl+Shift+Y` | 向 AI 提问 |
| `YM-CODE: Explain Code` | - | 解释选中的代码 |
| `YM-CODE: Refactor Code` | - | 重构选中的代码 |
| `YM-CODE: Debug Code` | - | 调试选中的代码 |
| `YM-CODE: Generate Tests` | - | 为当前文件生成测试 |
| `YM-CODE: Code Review` | - | 对当前文件进行 Code Review |
| `YM-CODE: Show Panel` | `Ctrl+Shift+M` | 显示 YM-CODE 面板 |
| `YM-CODE: Clear History` | - | 清空对话历史 |

---

## 🔧 开发

### 环境要求

- Node.js >= 18.0.0
- VSCode >= 1.85.0

### 安装依赖

```bash
cd vscode-extension
npm install
```

### 编译

```bash
npm run compile
```

### 调试

1. 按 `F5` 启动扩展开发主机
2. 在新窗口中测试扩展

### 打包

```bash
npm install -g vsce
vsce package
```

### 发布

```bash
vsce publish
```

---

## 📁 项目结构

```
vscode-extension/
├── src/
│   ├── extension.ts      # 扩展入口
│   ├── provider.ts       # Webview 提供者
│   └── api.ts            # API 客户端
├── media/
│   ├── styles.css        # 样式文件
│   └── script.js         # 前端脚本
├── resources/
│   └── icon.svg          # 图标
├── package.json          # 扩展配置
├── tsconfig.json         # TypeScript 配置
└── README.md             # 本文档
```

---

## 🎨 界面预览

### 侧边栏

YM-CODE 集成在 VSCode 侧边栏，提供完整的对话界面。

### 右键菜单

选中代码后，右键菜单包含：
- Explain Code
- Refactor Code
- Debug Code

### 快捷键

- `Ctrl+Shift+Y` - 快速提问
- `Ctrl+Shift+M` - 打开面板

---

## 📖 使用示例

### 示例 1：解释代码

1. 选中一段复杂代码
2. 右键 → **YM-CODE: Explain Code**
3. AI 会详细解释代码逻辑

### 示例 2：重构代码

1. 选中需要重构的代码
2. 右键 → **YM-CODE: Refactor Code**
3. AI 提供重构建议和代码

### 示例 3：调试问题

1. 选中问题代码
2. 右键 → **YM-CODE: Debug Code**
3. AI 分析可能的问题并提供解决方案

### 示例 4：生成测试

1. 打开代码文件
2. `Ctrl+Shift+Y` → 输入"为这个文件生成测试"
3. AI 生成完整的单元测试

---

## ⚠️ 注意事项

1. **API 连接** - 需要配置正确的 API 端点
2. **网络要求** - 需要能访问 API 服务器
3. **代码隐私** - 敏感代码请注意安全

---

## 🐛 问题反馈

如有问题或建议，请：

1. 查看 [GitHub Issues](https://github.com/ym-code/vscode-extension/issues)
2. 提交新的 Issue

---

## 📄 许可证

MIT License

---

## 👥 团队

YM-CODE Team

---

**Enjoy Coding with AI!** 🚀
