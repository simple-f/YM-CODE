# YM-CODE 多模型配置指南

**版本：** v1.0.0  
**更新时间：** 2026-03-16

---

## 🎯 支持的模型提供商

### 已适配的模型

| 提供商 | 模型 | 状态 |
|--------|------|------|
| **阿里云百炼** | Qwen3.5-Plus | ✅ 推荐 |
| **阿里云百炼** | Qwen-Plus | ✅ 支持 |
| **OpenAI** | GPT-4 | ✅ 支持 |
| **OpenAI** | GPT-3.5-Turbo | ✅ 支持 |
| **月之暗面** | Moonshot-v1-8K | ✅ 支持 |
| **智谱 AI** | GLM-4 | ✅ 支持 |
| **深度求索** | DeepSeek-Chat | ✅ 支持 |
| **百川智能** | Baichuan2-Turbo | ✅ 支持 |

---

## 📋 配置方式

### 方式 1：环境变量（推荐）

编辑 `.env` 文件：

```bash
# 阿里云百炼（推荐）
DASHSCOPE_API_KEY=sk-your-api-key-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# 月之暗面
MOONSHOT_API_KEY=sk-your-moonshot-key-here

# 智谱 AI
ZHIPU_API_KEY=your-zhipu-key-here

# 深度求索
DEEPSEEK_API_KEY=your-deepseek-key-here

# 百川智能
BAICHUAN_API_KEY=your-baichuan-key-here
```

### 方式 2：配置文件

编辑 `models.json`：

```json
{
  "models": {
    "gpt-4": {
      "name": "GPT-4",
      "provider": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key_env": "OPENAI_API_KEY",
      "max_tokens": 8000
    }
  },
  "default": "gpt-4"
}
```

### 方式 3：运行时指定

```python
from ymcode.core.llm_client import LLMClient

# 使用 GPT-4
client = LLMClient({
    'model': 'gpt-4',
    'api_key': 'sk-xxx',
    'base_url': 'https://api.openai.com/v1'
})

# 使用通义千问
client = LLMClient({
    'model': 'qwen3.5-plus',
    'api_key': 'sk-xxx',
    'base_url': 'https://coding.dashscope.aliyuncs.com/v1'
})
```

---

## 🔧 各平台配置详解

### 1. 阿里云百炼（推荐）

**获取 API Key：**
1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 进入 API Key 管理
4. 创建/复制 API Key

**灵码专用 API（编程优化）：**
1. 访问 https://dashscope.console.aliyun.com/lingma
2. 开通灵码服务
3. 使用相同的 API Key

**配置：**
```bash
# .env 文件
DASHSCOPE_API_KEY=sk-xxx

# models.json
{
  "default": "qwen-coder-plus"  // 灵码专用（编程推荐）
  // 或 "qwen3.5-plus"  // 通用模型
}
```

**支持模型：**
- qwen-coder-plus（灵码专用，编程推荐）⭐
- qwen3.5-plus（通用，推荐）
- qwen-plus（通用）
- qwen-turbo（快速）

**Base URL 区别：**
- 灵码专用：`https://coding.dashscope.aliyuncs.com/v1` ⭐ 编程优化
- 通用 API：`https://dashscope.aliyuncs.com/compatible-mode/v1`

**优点：**
- ✅ 中文支持好
- ✅ 价格实惠
- ✅ 国内访问快
- ✅ 支持长上下文
- ✅ 灵码专用 API 针对编程优化

---

### 2. OpenAI

**获取 API Key：**
1. 访问 https://platform.openai.com/
2. 注册/登录 OpenAI 账号
3. 进入 API Keys 页面
4. 创建新的 API Key

**配置：**
```bash
# .env 文件
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1

# models.json
{
  "default": "gpt-4"
}
```

**支持模型：**
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

**优点：**
- ✅ 能力强
- ✅ 生态完善
- ✅ 支持多语言

**注意：**
- ⚠️ 需要国际网络
- ⚠️ 价格较高

---

### 3. 月之暗面（Kimi）

**获取 API Key：**
1. 访问 https://platform.moonshot.cn/
2. 注册/登录月之暗面账号
3. 进入控制台
4. 创建 API Key

**配置：**
```bash
# .env 文件
MOONSHOT_API_KEY=sk-xxx

# models.json
{
  "default": "moonshot-v1-8k"
}
```

**支持模型：**
- moonshot-v1-8k
- moonshot-v1-32k
- moonshot-v1-128k

**优点：**
- ✅ 超长上下文（最高 128K）
- ✅ 中文支持好
- ✅ 价格合理

---

### 4. 智谱 AI（GLM）

**获取 API Key：**
1. 访问 https://open.bigmodel.cn/
2. 注册/登录智谱 AI 账号
3. 进入控制台
4. 创建 API Key

**配置：**
```bash
# .env 文件
ZHIPU_API_KEY=your-xxx

# models.json
{
  "default": "glm-4"
}
```

**支持模型：**
- glm-4
- glm-3-turbo
- glm-edge

**优点：**
- ✅ 中文能力强
- ✅ 支持多模态
- ✅ 价格适中

---

### 5. 深度求索（DeepSeek）

**获取 API Key：**
1. 访问 https://www.deepseek.com/
2. 注册/登录账号
3. 进入控制台
4. 创建 API Key

**配置：**
```bash
# .env 文件
DEEPSEEK_API_KEY=your-xxx

# models.json
{
  "default": "deepseek-chat"
}
```

**支持模型：**
- deepseek-chat
- deepseek-coder

**优点：**
- ✅ 代码能力强
- ✅ 价格实惠
- ✅ 响应快

---

### 6. 百川智能（Baichuan）

**获取 API Key：**
1. 访问 https://www.baichuan-ai.com/
2. 注册/登录账号
3. 进入控制台
4. 创建 API Key

**配置：**
```bash
# .env 文件
BAICHUAN_API_KEY=your-xxx

# models.json
{
  "default": "baichuan2-turbo"
}
```

**支持模型：**
- baichuan2-turbo
- baichuan2-turbo-192k

**优点：**
- ✅ 超长上下文（192K）
- ✅ 中文优化
- ✅ 价格低

---

## 📊 模型对比

### 性能对比

| 模型 | 上下文 | 速度 | 能力 | 价格 |
|------|--------|------|------|------|
| Qwen3.5-Plus | 8K | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT-4 | 8K | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Moonshot-v1 | 8K-128K | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| GLM-4 | 8K | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| DeepSeek | 8K | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 价格对比（每 1000 tokens）

| 模型 | 输入 | 输出 |
|------|------|------|
| Qwen3.5-Plus | ¥0.004 | ¥0.012 |
| GPT-4 | $0.03 | $0.06 |
| Moonshot-v1-8K | ¥0.012 | ¥0.012 |
| GLM-4 | ¥0.01 | ¥0.01 |
| DeepSeek | ¥0.002 | ¥0.002 |

---

## 🎯 选择建议

### 日常使用（推荐）

**配置：**
```bash
DASHSCOPE_API_KEY=sk-xxx
```

**模型：** qwen3.5-plus

**理由：**
- ✅ 中文支持好
- ✅ 价格合理
- ✅ 国内访问快
- ✅ 能力强

---

### 代码开发

**配置：**
```bash
DEEPSEEK_API_KEY=your-xxx
```

**模型：** deepseek-coder

**理由：**
- ✅ 代码能力强
- ✅ 价格实惠
- ✅ 响应快

---

### 长文档分析

**配置：**
```bash
MOONSHOT_API_KEY=sk-xxx
```

**模型：** moonshot-v1-128k

**理由：**
- ✅ 128K 超长上下文
- ✅ 文档理解好
- ✅ 价格合理

---

### 国际业务

**配置：**
```bash
OPENAI_API_KEY=sk-xxx
```

**模型：** gpt-4-turbo

**理由：**
- ✅ 多语言支持
- ✅ 全球访问
- ✅ 能力强

---

## 🔀 切换模型

### 方式 1：修改配置文件

编辑 `models.json`：

```json
{
  "default": "gpt-4"  // 改为其他模型
}
```

### 方式 2：环境变量

```bash
export YM_CODE_MODEL=gpt-4
```

### 方式 3：代码指定

```python
from ymcode.core.llm_client import LLMClient

client = LLMClient({
    'model': 'gpt-4',
    'api_key': 'sk-xxx',
    'base_url': 'https://api.openai.com/v1'
})
```

---

## 🐛 常见问题

### Q: 如何同时配置多个模型？

**A:** 在 `.env` 中配置多个 API Key：

```bash
DASHSCOPE_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
MOONSHOT_API_KEY=sk-xxx
```

然后在 `models.json` 中指定默认模型。

---

### Q: 如何切换模型？

**A:** 修改 `models.json` 中的 `default` 字段：

```json
{
  "default": "gpt-4"  // 改为其他模型名称
}
```

---

### Q: 支持自定义模型吗？

**A:** 支持！在 `models.json` 中添加：

```json
{
  "models": {
    "my-custom-model": {
      "name": "我的自定义模型",
      "provider": "custom",
      "base_url": "https://api.example.com/v1",
      "api_key_env": "CUSTOM_API_KEY",
      "max_tokens": 8000
    }
  }
}
```

---

### Q: API Key 安全吗？

**A:** 安全！

- ✅ API Key 存储在 `.env` 文件
- ✅ `.env` 已添加到 `.gitignore`
- ✅ 不会提交到 Git
- ✅ 运行时从环境变量读取

---

## 📝 总结

**推荐配置：**

```bash
# 主力模型（阿里云百炼）
DASHSCOPE_API_KEY=sk-xxx

# 备用模型（可选）
OPENAI_API_KEY=sk-xxx
MOONSHOT_API_KEY=sk-xxx
```

**默认模型：** qwen3.5-plus

**理由：**
- ✅ 中文支持好
- ✅ 价格实惠
- ✅ 国内访问快
- ✅ 能力强

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
