# 阿里云百炼配置说明

**版本：** v1.0.1  
**更新时间：** 2026-03-16

---

## ⚠️ 重要：Base URL 区别

阿里云百炼有**两个不同的 API 地址**：

### 1. 灵码专用 API（编程推荐）⭐

**Base URL：**
```
https://coding.dashscope.aliyuncs.com/v1
```

**特点：**
- ✅ 针对编程场景优化
- ✅ 代码生成能力更强
- ✅ 理解代码上下文更好
- ✅ 支持代码补全、重构等

**配置：**
```json
{
  "default": "qwen-coder-plus"
}
```

**开通方式：**
1. 访问 https://dashscope.console.aliyun.com/lingma
2. 开通通义灵码服务
3. 使用相同的 API Key

---

### 2. 通用 API（日常对话）

**Base URL：**
```
https://dashscope.aliyuncs.com/compatible-mode/v1
```

**特点：**
- ✅ 通用对话能力强
- ✅ 支持多种任务
- ✅ 价格更便宜

**配置：**
```json
{
  "default": "qwen3.5-plus"
}
```

---

## 📊 模型对比

| 模型 | Base URL | 适用场景 | 价格 |
|------|---------|---------|------|
| qwen-coder-plus | coding.dashscope... | 编程开发 ⭐ | ¥0.004/1k |
| qwen3.5-plus | dashscope... | 通用对话 | ¥0.004/1k |
| qwen-plus | dashscope... | 日常使用 | ¥0.002/1k |

---

## 🎯 推荐配置

### 编程开发（推荐）

**.env：**
```bash
DASHSCOPE_API_KEY=sk-xxx
```

**models.json：**
```json
{
  "default": "qwen-coder-plus"
}
```

**理由：**
- ✅ 灵码专用 API
- ✅ 编程场景优化
- ✅ 代码能力更强

---

### 日常使用

**.env：**
```bash
DASHSCOPE_API_KEY=sk-xxx
```

**models.json：**
```json
{
  "default": "qwen3.5-plus"
}
```

**理由：**
- ✅ 通用能力强
- ✅ 性价比高
- ✅ 响应快

---

## 🔧 切换方式

### 方式 1：修改 models.json

```json
{
  "default": "qwen-coder-plus"  // 切换到灵码
}
```

### 方式 2：运行时指定

```python
from ymcode.core.llm_client import LLMClient

# 使用灵码专用 API
client = LLMClient({
    'model': 'qwen-coder-plus',
    'api_key': 'sk-xxx',
    'base_url': 'https://coding.dashscope.aliyuncs.com/v1'
})

# 使用通用 API
client = LLMClient({
    'model': 'qwen3.5-plus',
    'api_key': 'sk-xxx',
    'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
})
```

---

## 🐛 常见问题

### Q: 灵码专用 API 和普通 API 有什么区别？

**A:** 
- **灵码专用**：针对编程场景优化，代码能力更强
- **普通 API**：通用对话，适合日常使用

### Q: API Key 是同一个吗？

**A:** 是的！都是 `DASHSCOPE_API_KEY`，只是 Base URL 不同。

### Q: 如何开通灵码服务？

**A:** 
1. 访问 https://dashscope.console.aliyun.com/lingma
2. 登录阿里云账号
3. 点击"开通服务"
4. 免费开通

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
