# YM-CODE VSCode 插件

**版本：** 0.8.0  
**描述：** YM-CODE AI 编程助手 VSCode 插件

---

## 🎯 功能特性

- ✅ 代码分析（Pylint、Flake8）
- ✅ 代码格式化（Black）
- ✅ 实时问题检测
- ✅ 快速修复建议
- ✅ 保存时自动分析

---

## 🚀 安装

### 方式 1：从市场安装

```bash
# 待发布到 VSCode 市场
```

### 方式 2：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE/extensions/vscode

# 2. 安装依赖
npm install

# 3. 编译
npm run compile

# 4. 打包
vsce package

# 5. 安装
code --install-extension ymcode-0.8.0.vsix
```

---

## 💡 使用方式

### 命令面板

1. 按 `Ctrl+Shift+P` (Windows/Linux) 或 `Cmd+Shift+P` (Mac)
2. 输入以下命令：

**分析代码：**
```
YM-CODE: 分析当前文件
```

**格式化代码：**
```
YM-CODE: 格式化当前文件
```

**检查代码：**
```
YM-CODE: 检查代码问题
```

### 右键菜单

1. 选中代码
2. 右键点击
3. 选择 **YM-CODE: 分析** 或 **YM-CODE: 格式化**

### 快捷键

可以在 `keybindings.json` 中自定义快捷键：

```json
[
    {
        "key": "ctrl+shift+a",
        "command": "ymcode.analyze",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+shift+f",
        "command": "ymcode.format",
        "when": "editorTextFocus"
    }
]
```

---

## ⚙️ 配置

在 `settings.json` 中添加：

```json
{
    "ymcode.autoAnalyzeOnSave": true,  // 保存时自动分析
    "ymcode.apiEndpoint": "http://localhost:18770/api",  // API 地址
    "ymcode.enabledTools": ["pylint", "black", "flake8"]  // 启用的工具
}
```

---

## 📋 前置要求

**需要运行 YM-CODE 服务：**

```bash
# 1. 启动 YM-CODE
cd /path/to/YM-CODE
python start-web.py

# 2. 确保服务在 http://localhost:18770 运行
```

**可选依赖（代码分析需要）：**

```bash
pip install pylint black flake8
```

---

## 🐛 故障排查

### 问题 1：提示 API 连接失败

**解决：**
1. 确保 YM-CODE 服务正在运行
2. 检查 API 地址是否正确
3. 检查端口 18770 是否被占用

### 问题 2：分析结果为空

**解决：**
1. 确保安装了分析工具（pylint、flake8）
2. 检查代码语言是否支持
3. 查看 YM-CODE 日志

### 问题 3：格式化无效果

**解决：**
1. 确保安装了 Black
2. 检查代码是否是 Python
3. 查看输出面板的错误信息

---

## 📝 开发指南

### 构建

```bash
npm run compile
```

### 监听模式

```bash
npm run watch
```

### 调试

1. 打开 VSCode
2. 按 `F5` 启动调试
3. 在新窗口中测试插件

### 打包

```bash
vsce package
```

---

## 🎯 路线图

### v0.8.0（当前版本）

- ✅ 代码分析
- ✅ 代码格式化
- ✅ 实时检测

### v0.9.0（计划中）

- [ ] Git 集成
- [ ] 批量处理
- [ ] 自定义规则

### v1.0.0（计划中）

- [ ] 完整功能
- [ ] 性能优化
- [ ] 市场发布

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢使用 YM-CODE VSCode 插件！

**GitHub:** https://github.com/simple-f/YM-CODE  
**文档：** https://github.com/simple-f/YM-CODE/tree/master/docs
