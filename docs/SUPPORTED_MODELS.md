# YM-CODE 支持模型列表

**更新时间：** 2026-03-16  
**版本：** v1.0.1

---

## 🎯 支持的模型（12 个）

### 阿里云百炼（通义千问系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **qwen3.5-plus** | dashscope.aliyuncs.com | 文本生成、深度思考、视觉理解 | ✅ 推荐 |
| **qwen3-max-2026-01-23** | dashscope.aliyuncs.com | 文本生成、深度思考 | ✅ 支持 |
| **qwen3-coder-next** | coding.dashscope.aliyuncs.com | 文本生成、编程 | ✅ 推荐 |
| **qwen3-coder-plus** | coding.dashscope.aliyuncs.com | 文本生成、编程专用 | ✅ 推荐 |
| **qwen-coder-plus** | coding.dashscope.aliyuncs.com | 编程专用 | ✅ 支持 |
| **qwen-coder-turbo** | coding.dashscope.aliyuncs.com | 编程专用、快速 | ✅ 经济 |

---

### 智谱 AI（GLM 系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **glm-5** | open.bigmodel.cn | 文本生成、深度思考 | ✅ 最新 |
| **glm-4.7** | open.bigmodel.cn | 文本生成、深度思考 | ✅ 支持 |

---

### 月之暗面（Kimi 系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **kimi-k2.5** | api.moonshot.cn | 文本生成、深度思考、视觉理解 | ✅ 最新 |

---

### 迷你冰（MiniMax 系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **minimax-m2.5** | api.minimax.chat | 文本生成、深度思考 | ✅ 最新 |

---

### 深度求索（DeepSeek 系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **deepseek-coder** | api.deepseek.com | 编程专用 | ✅ 支持 |

---

### OpenAI（GPT 系列）

| 模型 | Base URL | 能力 | 状态 |
|------|---------|------|------|
| **gpt-4** | api.openai.com | 文本生成、深度思考 | ✅ 支持 |

---

## 🎯 推荐配置

### 日常使用（推荐）

```json
{
  "default": "qwen3.5-plus"
}
```

**理由：**
- ✅ 文本生成
- ✅ 深度思考
- ✅ 视觉理解
- ✅ 价格实惠

---

### 编程开发（推荐）

```json
{
  "default": "qwen3-coder-plus"
}
```

**理由：**
- ✅ 编程专用
- ✅ 代码理解强
- ✅ 灵码专用 API

---

### 深度思考

```json
{
  "default": "glm-5"
}
```

**理由：**
- ✅ GLM-5 最新
- ✅ 深度思考强
- ✅ 复杂任务适用

---

### 长文本分析

```json
{
  "default": "kimi-k2.5"
}
```

**理由：**
- ✅ Kimi 长文本强
- ✅ 视觉理解
- ✅ 深度思考

---

## 🔧 配置方式

### .env 文件

```bash
# 阿里云百炼
DASHSCOPE_API_KEY=sk-xxx

# 智谱 AI
ZHIPU_API_KEY=xxx

# 月之暗面（Kimi）
MOONSHOT_API_KEY=sk-xxx

# 迷你冰（MiniMax）
MINIMAX_API_KEY=xxx

# 深度求索
DEEPSEEK_API_KEY=xxx

# OpenAI
OPENAI_API_KEY=sk-xxx
```

### models.json

```json
{
  "models": {
    "qwen3.5-plus": {
      "name": "通义千问 3.5 Plus",
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "glm-5": {
      "name": "智谱 GLM-5",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "api_key_env": "ZHIPU_API_KEY"
    },
    "kimi-k2.5": {
      "name": "Kimi K2.5",
      "base_url": "https://api.moonshot.cn/v1",
      "api_key_env": "MOONSHOT_API_KEY"
    },
    "minimax-m2.5": {
      "name": "MiniMax M2.5",
      "base_url": "https://api.minimax.chat/v1",
      "api_key_env": "MINIMAX_API_KEY"
    }
  },
  "default": "qwen3.5-plus"
}
```

---

## 📊 能力对比

### 文本生成

| 模型 | 能力 | 评分 |
|------|------|------|
| qwen3.5-plus | 文本生成、深度思考、视觉理解 | ⭐⭐⭐⭐⭐ |
| glm-5 | 文本生成、深度思考 | ⭐⭐⭐⭐⭐ |
| kimi-k2.5 | 文本生成、深度思考、视觉理解 | ⭐⭐⭐⭐⭐ |
| minimax-m2.5 | 文本生成、深度思考 | ⭐⭐⭐⭐ |

### 编程能力

| 模型 | 能力 | 评分 |
|------|------|------|
| qwen3-coder-plus | 编程专用 | ⭐⭐⭐⭐⭐ |
| qwen-coder-plus | 编程专用 | ⭐⭐⭐⭐⭐ |
| deepseek-coder | 编程专用 | ⭐⭐⭐⭐⭐ |

---

## 📝 总结

**支持的提供商（6 个）：**
1. ✅ 阿里云百炼（6 个模型）
2. ✅ 智谱 AI（2 个模型）
3. ✅ 月之暗面（1 个模型）
4. ✅ 迷你冰（1 个模型）
5. ✅ 深度求索（1 个模型）
6. ✅ OpenAI（1 个模型）

**总计：12 个模型**

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
