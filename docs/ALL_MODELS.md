# 完整模型支持列表

**更新时间：** 2026-03-16  
**总计：** 20+ 个模型

---

## 🎯 按提供商分类

### 1. 阿里云百炼（通义系列）

**灵码专用 API（6 个）：**
- ✅ qwen-coder-plus - 通义灵码 Plus
- ✅ qwen-coder-turbo - 通义灵码 Turbo
- ✅ qwen3-coder-plus - Qwen3 Coder Plus
- ✅ qwen3-coder-turbo - Qwen3 Coder Turbo
- ✅ qwen2.5-coder-32b - Qwen2.5 Coder 32B
- ✅ qwen2.5-coder-7b - Qwen2.5 Coder 7B

**通用 API（4 个）：**
- ✅ qwen3.5-plus - 通义千问 3.5 Plus
- ✅ qwen3-plus - 通义千问 3 Plus
- ✅ qwen-plus - 通义千问 Plus
- ✅ qwen-turbo - 通义千问 Turbo

---

### 2. 智谱 AI（GLM 系列）⭐

**Base URL：** `https://open.bigmodel.cn/api/paas/v4`

**支持模型（4 个）：**
- ✅ **glm-4** - GLM-4（最强）
- ✅ **glm-4-flash** - GLM-4 Flash（快速）
- ✅ **glm-3-turbo** - GLM-3 Turbo
- ✅ **coglm-4** - CodeGLM-4（编程专用）⭐

**API Key：** `ZHIPU_API_KEY`

---

### 3. 月之暗面（Kimi 系列）⭐

**Base URL：** `https://api.moonshot.cn/v1`

**支持模型（3 个）：**
- ✅ **moonshot-v1-8k** - Kimi v1 8K
- ✅ **moonshot-v1-32k** - Kimi v1 32K（长文本）
- ✅ **moonshot-v1-128k** - Kimi v1 128K（超长文本）⭐

**API Key：** `MOONSHOT_API_KEY`

---

### 4. OpenAI（GPT 系列）

**Base URL：** `https://api.openai.com/v1`

**支持模型（2 个）：**
- ✅ **gpt-4** - GPT-4
- ✅ **gpt-3.5-turbo** - GPT-3.5 Turbo

**API Key：** `OPENAI_API_KEY`

---

### 5. 深度求索（DeepSeek 系列）

**Base URL：** `https://api.deepseek.com/v1`

**支持模型（2 个）：**
- ✅ **deepseek-chat** - DeepSeek Chat
- ✅ **deepseek-coder** - DeepSeek Coder（编程专用）⭐

**API Key：** `DEEPSEEK_API_KEY`

---

### 6. 迷你冰（MiniMax 系列）⭐ 新增

**Base URL：** `https://api.minimax.chat/v1`

**支持模型（2 个）：**
- ✅ **minimax-abab6** - MiniMax Abab6（最新）
- ✅ **minimax-abab5** - MiniMax Abab5

**API Key：** `MINIMAX_API_KEY`

---

## 📊 完整模型对比

### 编程能力排名

| 排名 | 模型 | 提供商 | 代码能力 | 综合评分 |
|------|------|--------|---------|---------|
| 1 | qwen-coder-plus | 阿里云 | ⭐⭐⭐⭐⭐ | 95/100 |
| 2 | qwen3-coder-plus | 阿里云 | ⭐⭐⭐⭐⭐ | 93/100 |
| 3 | coglm-4 | 智谱 | ⭐⭐⭐⭐⭐ | 92/100 |
| 4 | deepseek-coder | 深度求索 | ⭐⭐⭐⭐⭐ | 90/100 |
| 5 | qwen-coder-turbo | 阿里云 | ⭐⭐⭐⭐ | 85/100 |
| 6 | glm-4 | 智谱 | ⭐⭐⭐⭐ | 88/100 |
| 7 | gpt-4 | OpenAI | ⭐⭐⭐⭐⭐ | 94/100 |

---

### 长文本能力排名

| 排名 | 模型 | 上下文 | 提供商 |
|------|------|--------|--------|
| 1 | moonshot-v1-128k | 128K | 月之暗面 ⭐ |
| 2 | moonshot-v1-32k | 32K | 月之暗面 |
| 3 | qwen2.5-coder-32b | 8K | 阿里云 |
| 4 | glm-4 | 8K | 智谱 |

---

### 价格对比（每 1000 tokens）

| 模型 | 输入 | 输出 | 提供商 |
|------|------|------|--------|
| qwen2.5-coder-7b | ¥0.001 | ¥0.003 | 阿里云 |
| qwen-turbo | ¥0.001 | ¥0.003 | 阿里云 |
| glm-3-turbo | ¥0.001 | ¥0.003 | 智谱 |
| deepseek-chat | ¥0.002 | ¥0.002 | 深度求索 |
| qwen-coder-turbo | ¥0.002 | ¥0.006 | 阿里云 |
| glm-4 | ¥0.01 | ¥0.01 | 智谱 |
| moonshot-v1-8k | ¥0.012 | ¥0.012 | 月之暗面 |
| qwen-coder-plus | ¥0.004 | ¥0.012 | 阿里云 |
| gpt-4 | $0.03 | $0.06 | OpenAI |

---

## 🎯 推荐配置

### 编程开发（最强）

```json
{
  "default": "qwen-coder-plus"
}
```

**备选：**
- coglm-4（智谱编程专用）
- deepseek-coder（深度求索编程）

---

### 长文本分析

```json
{
  "default": "moonshot-v1-128k"
}
```

**理由：**
- ✅ 128K 超长上下文
- ✅ 文档理解好
- ✅ Kimi 擅长长文本

---

### 日常使用（经济）

```json
{
  "default": "glm-4-flash"
}
```

**理由：**
- ✅ 快速响应
- ✅ 价格实惠
- ✅ 能力足够

---

### 多语言支持

```json
{
  "default": "gpt-4"
}
```

**理由：**
- ✅ 多语言能力强
- ✅ 全球访问
- ✅ 生态完善

---

## 🔧 完整配置

### .env 文件

```bash
# 阿里云百炼
DASHSCOPE_API_KEY=sk-xxx

# 智谱 AI
ZHIPU_API_KEY=xxx

# 月之暗面（Kimi）
MOONSHOT_API_KEY=sk-xxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# 深度求索
DEEPSEEK_API_KEY=xxx

# 迷你冰
MINIMAX_API_KEY=xxx
```

### models.json

```json
{
  "models": {
    "qwen-coder-plus": {
      "name": "通义灵码 Plus",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "glm-4": {
      "name": "智谱 GLM-4",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "api_key_env": "ZHIPU_API_KEY"
    },
    "coglm-4": {
      "name": "智谱 CodeGLM-4",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "api_key_env": "ZHIPU_API_KEY"
    },
    "moonshot-v1-128k": {
      "name": "Kimi v1 128K",
      "base_url": "https://api.moonshot.cn/v1",
      "api_key_env": "MOONSHOT_API_KEY"
    },
    "deepseek-coder": {
      "name": "DeepSeek Coder",
      "base_url": "https://api.deepseek.com/v1",
      "api_key_env": "DEEPSEEK_API_KEY"
    },
    "minimax-abab6": {
      "name": "MiniMax Abab6",
      "base_url": "https://api.minimax.chat/v1",
      "api_key_env": "MINIMAX_API_KEY"
    }
  },
  "default": "qwen-coder-plus"
}
```

---

## 📝 总结

**支持的提供商（6 个）：**
1. ✅ 阿里云百炼（10 个模型）
2. ✅ 智谱 AI（4 个模型）⭐ GLM
3. ✅ 月之暗面（3 个模型）⭐ Kimi
4. ✅ OpenAI（2 个模型）
5. ✅ 深度求索（2 个模型）
6. ✅ 迷你冰（2 个模型）⭐ MiniMax

**总计：23 个模型**

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
