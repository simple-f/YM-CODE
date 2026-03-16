# YM-CODE 模型切换指南

> 支持多种大模型，随时切换使用

---

## 🎯 已支持的模型

### 默认配置

**当前默认模型：** GLM-5（阿里云百炼）

### 所有可用模型

| 模型 ID | 模型名称 | 提供商 | 最大 Token |
|--------|----------|--------|-----------|
| `glm-5` | 智谱 GLM-5 | 智谱 AI | 4000 |
| `glm-4` | 智谱 GLM-4 | 智谱 AI | 4000 |
| `gpt-4` | GPT-4 | OpenAI | 8000 |
| `gpt-3.5-turbo` | GPT-3.5 Turbo | OpenAI | 4000 |
| `moonshot-v1` | Moonshot V1 | 月之暗面 | 8000 |
| `qwen-turbo` | 通义千问 Turbo | 阿里云 | 8000 |

---

## 🔄 如何切换模型

### 方法 1：在 YM-CODE 中切换（推荐）

```bash
# 启动 YM-CODE
ym-code

# 查看当前模型
YM-CODE> model
当前模型：glm-5

# 列出所有可用模型
YM-CODE> models

# 切换到 GLM-4
YM-CODE> model glm-4
已切换到模型：glm-4 (智谱 GLM-4)

# 切换到 GPT-4
YM-CODE> model gpt-4
已切换到模型：gpt-4 (OpenAI GPT-4)

# 切换到 Moonshot
YM-CODE> model moonshot-v1
已切换到模型：moonshot-v1 (月之暗面 Moonshot V1)
```

### 方法 2：修改配置文件

编辑 `.env` 文件：

```env
# 修改模型
OPENAI_MODEL=glm-4
```

---

## 🔧 配置不同模型的 API Key

### 1. 阿里云百炼（GLM、通义千问）

**获取 API Key：**
1. 访问：https://dashscope.console.aliyun.com/
2. 登录阿里云
3. 进入「API-KEY 管理」
4. 创建 API Key

**配置 `.env`：**
```env
DASHSCOPE_API_KEY=sk-你的-key
```

**可用模型：**
- GLM-5
- GLM-4
- 通义千问 Turbo
- 通义千问 Plus

---

### 2. OpenAI

**获取 API Key：**
1. 访问：https://platform.openai.com/api-keys
2. 登录 OpenAI
3. 创建 API Key

**配置 `.env`：**
```env
OPENAI_API_KEY=sk-你的-openai-key
```

**可用模型：**
- GPT-4
- GPT-3.5 Turbo
- GPT-4 Turbo

---

### 3. 月之暗面 Moonshot

**获取 API Key：**
1. 访问：https://platform.moonshot.cn/
2. 登录月之暗面
3. 创建 API Key

**配置 `.env`：**
```env
MOONSHOT_API_KEY=sk-你的-moonshot-key
```

**可用模型：**
- Moonshot V1
- Moonshot V1-8k
- Moonshot V1-32k

---

### 4. 智谱 AI

**获取 API Key：**
1. 访问：https://open.bigmodel.cn/
2. 登录智谱 AI
3. 创建 API Key

**配置 `.env`：**
```env
ZHIPU_API_KEY=你的-zhipu-key
```

**可用模型：**
- GLM-4
- GLM-3-Turbo

---

## 📊 模型对比

| 模型 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **GLM-5** | 中文强，便宜 | 英文稍弱 | 中文编程、文档 |
| **GPT-4** | 综合最强 | 贵 | 复杂任务 |
| **Moonshot** | 长上下文 | 较新 | 长文档分析 |
| **Qwen** | 阿里生态 | 通用 | 阿里云用户 |

---

## 💡 使用技巧

### 1. 根据场景选择模型

```bash
# 写中文文档 - 用 GLM-5
YM-CODE> model glm-5
YM-CODE> 帮我写一个 Python 函数的文档

# 复杂算法 - 用 GPT-4
YM-CODE> model gpt-4
YM-CODE> 实现一个快速排序算法

# 分析长文件 - 用 Moonshot
YM-CODE> model moonshot-v1
YM-CODE> 分析这个 1000 行的代码文件
```

### 2. 快速切换

```bash
# 查看当前模型
YM-CODE> model

# 快速切换
YM-CODE> model glm-4

# 继续工作
YM-CODE> 优化这段代码
```

### 3. 成本优化

```bash
# 日常开发 - 用便宜的模型
YM-CODE> model glm-5

# 重要任务 - 用更好的模型
YM-CODE> model gpt-4
YM-CODE> 审查这个关键模块
```

---

## 🔍 添加自定义模型

编辑 `models.json` 添加新模型：

```json
{
  "models": {
    "your-model": {
      "name": "你的模型名称",
      "base_url": "https://你的-api 地址/v1",
      "api_key_env": "YOUR_API_KEY_ENV",
      "max_tokens": 4000,
      "description": "模型描述"
    }
  }
}
```

---

## 📖 相关文档

- [CONFIG_GUIDE.md](./CONFIG_GUIDE.md) - 配置指南
- [INSTALL.md](./INSTALL.md) - 安装指南
- [README.md](./README.md) - 项目说明

---

_最后更新：2026-03-13_

_作者：YM-CODE Team_
