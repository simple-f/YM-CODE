# YM-CODE 快速开始指南

> 5 分钟快速上手，像 Claude Code 一样好用的 AI 编程助手

---

## ✅ 配置完成状态

**当前配置：**
- ✅ API Key: `sk-sp-90fc02607ed448...`
- ✅ 模型：通义千问 Plus（qwen-plus）
- ✅ Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- ✅ 模型切换：已实现

---

## 🚀 快速使用

### 1. 启动 YM-CODE

```bash
ym-code
```

### 2. 测试对话

```bash
YM-CODE> 你好
YM-CODE> 你是什么模型
YM-CODE> 帮我创建一个文件 test.py
```

### 3. 切换模型

```bash
# 查看当前模型
YM-CODE> model
当前模型：qwen-plus

# 列出所有模型
YM-CODE> models

# 切换到通义千问 Turbo（更快）
YM-CODE> model qwen-turbo
已切换到模型：qwen-turbo

# 切换到通义千问 Max（最强）
YM-CODE> model qwen-max
已切换到模型：qwen-max
```

---

## 📊 可用模型列表

| 模型 ID | 模型名称 | Base URL | 特点 |
|--------|----------|----------|------|
| `qwen-plus` | 通义千问 Plus | dashscope | 平衡（默认） |
| `qwen-turbo` | 通义千问 Turbo | dashscope | 快速 |
| `qwen-max` | 通义千问 Max | dashscope | 最强 |
| `glm-5` | 智谱 GLM-5 | bigmodel.cn | 中文强 |
| `glm-4` | 智谱 GLM-4 | bigmodel.cn | 中文强 |
| `moonshot-v1` | Moonshot V1 | moonshot.cn | 长上下文 |

---

## 🔧 命令速查

### 基本命令

```bash
YM-CODE> help              # 查看帮助
YM-CODE> clear             # 清屏
YM-CODE> quit              # 退出程序
```

### 模型切换

```bash
YM-CODE> model             # 查看当前模型
YM-CODE> models            # 列出所有模型
YM-CODE> model qwen-plus   # 切换模型
```

### 编程任务

```bash
YM-CODE> 帮我创建 test.py
YM-CODE> 写入 print("hello")
YM-CODE> 读取 test.py
YM-CODE> 运行 python test.py
YM-CODE> 解释这段代码
YM-CODE> 优化这个函数
YM-CODE> 添加注释
```

### Git 操作

```bash
YM-CODE> git status
YM-CODE> git add .
YM-CODE> git commit -m "更新代码"
YM-CODE> git push
```

---

## 📝 配置文件

**位置：** `C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE\.env`

**配置项：**

```env
# API Key
DASHSCOPE_API_KEY=sk-sp-xxx

# 模型配置
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus

# YM-CODE 配置
YM_CODE_MAX_ITERATIONS=30
YM_CODE_TIMEOUT=300
```

---

## 💡 使用技巧

### 1. 根据场景选择模型

```bash
# 日常开发 - 用 qwen-plus（平衡）
YM-CODE> model qwen-plus

# 快速响应 - 用 qwen-turbo
YM-CODE> model qwen-turbo

# 复杂任务 - 用 qwen-max
YM-CODE> model qwen-max
```

### 2. 文件操作

```bash
# 创建并写入
YM-CODE> 创建 test.py，写入 print("hello")

# 读取文件
YM-CODE> 读取 test.py

# 修改文件
YM-CODE> 在 test.py 中添加一个函数
```

### 3. 代码审查

```bash
YM-CODE> 审查这个文件
YM-CODE> 检查代码规范
YM-CODE> 找出潜在 bug
```

---

## 🐛 故障排查

### 问题 1：API Key 错误

**错误信息：** `Error code: 401 - Incorrect API key provided`

**解决：**
1. 检查 `.env` 文件中的 API Key 是否正确
2. 访问 https://dashscope.console.aliyun.com/apiKey 确认 Key 有效
3. 确认有足够的额度

### 问题 2：模型不存在

**错误信息：** `Model not found`

**解决：**
```bash
# 查看可用模型
YM-CODE> models

# 使用正确的模型 ID
YM-CODE> model qwen-plus
```

### 问题 3：命令不生效

**解决：**
```bash
# 重启 YM-CODE
YM-CODE> quit

# 重新启动
ym-code
```

---

## 📖 相关文档

- [MODELS_GUIDE.md](./MODELS_GUIDE.md) - 模型切换指南
- [CONFIG_GUIDE.md](./CONFIG_GUIDE.md) - 配置指南
- [INSTALL.md](./INSTALL.md) - 安装指南
- [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) - 测试指南

---

_最后更新：2026-03-13_

_作者：YM-CODE Team_
