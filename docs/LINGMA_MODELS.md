# 通义灵码支持模型列表

**更新时间：** 2026-03-16  
**来源：** 阿里云百炼官方文档

---

## 🎯 通义灵码专用 API

**Base URL：**
```
https://coding.dashscope.aliyuncs.com/v1
```

**API Key：** `DASHSCOPE_API_KEY`（与百炼通用）

---

## 📋 支持的模型

### 编程专用模型（推荐）

| 模型名称 | 模型 ID | 上下文 | 价格 | 状态 |
|---------|--------|--------|------|------|
| **通义灵码** | qwen-coder-plus | 8K | ¥0.004/1k | ✅ 推荐 |
| **通义灵码 Turbo** | qwen-coder-turbo | 8K | ¥0.002/1k | ✅ 经济 |

### 通用模型（也可用于编程）

| 模型名称 | 模型 ID | 上下文 | 价格 | 状态 |
|---------|--------|--------|------|------|
| **通义千问 3.5 Plus** | qwen3.5-plus | 8K | ¥0.004/1k | ✅ 推荐 |
| **通义千问 Plus** | qwen-plus | 8K | ¥0.002/1k | ✅ 通用 |
| **通义千问 Turbo** | qwen-turbo | 8K | ¥0.001/1k | ✅ 快速 |

---

## 🚀 推荐配置

### 编程开发（最佳）

**models.json：**
```json
{
  "default": "qwen-coder-plus"
}
```

**特点：**
- ✅ 针对编程优化
- ✅ 代码生成能力强
- ✅ 理解代码上下文
- ✅ 支持代码补全、重构

---

### 经济方案

**models.json：**
```json
{
  "default": "qwen-coder-turbo"
}
```

**特点：**
- ✅ 价格更便宜（¥0.002/1k）
- ✅ 响应更快
- ✅ 编程能力良好

---

### 通用方案

**models.json：**
```json
{
  "default": "qwen3.5-plus"
}
```

**特点：**
- ✅ 通用能力强
- ✅ 适合混合任务
- ✅ 性价比高

---

## 💰 价格对比

### 灵码专用 API

| 模型 | 输入 | 输出 |
|------|------|------|
| qwen-coder-plus | ¥0.004/1k tokens | ¥0.012/1k tokens |
| qwen-coder-turbo | ¥0.002/1k tokens | ¥0.006/1k tokens |

### 通用 API

| 模型 | 输入 | 输出 |
|------|------|------|
| qwen3.5-plus | ¥0.004/1k tokens | ¥0.012/1k tokens |
| qwen-plus | ¥0.002/1k tokens | ¥0.006/1k tokens |
| qwen-turbo | ¥0.001/1k tokens | ¥0.003/1k tokens |

---

## 🔧 配置方式

### .env 文件

```bash
# 阿里云百炼 API Key
DASHSCOPE_API_KEY=sk-xxx
```

### models.json

```json
{
  "models": {
    "qwen-coder-plus": {
      "name": "通义灵码（编程专用）",
      "provider": "dashscope",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY",
      "max_tokens": 8000,
      "description": "通义灵码专用 API（编程场景优化，推荐）"
    },
    "qwen-coder-turbo": {
      "name": "通义灵码 Turbo",
      "provider": "dashscope",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY",
      "max_tokens": 8000,
      "description": "通义灵码 Turbo（经济快速）"
    }
  },
  "default": "qwen-coder-plus"
}
```

---

## 📊 能力对比

### 编程能力

| 模型 | 代码生成 | 代码理解 | 调试能力 | 综合评分 |
|------|---------|---------|---------|---------|
| qwen-coder-plus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 95/100 |
| qwen-coder-turbo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 85/100 |
| qwen3.5-plus | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 88/100 |
| qwen-plus | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 75/100 |

---

## 🎯 选择建议

### 专业开发（推荐）

**选择：** `qwen-coder-plus`

**理由：**
- ✅ 编程专用优化
- ✅ 代码能力最强
- ✅ 理解复杂代码
- ✅ 支持代码重构

**适用场景：**
- 代码生成
- 代码审查
- 代码重构
- Bug 修复

---

### 日常开发（经济）

**选择：** `qwen-coder-turbo`

**理由：**
- ✅ 价格实惠
- ✅ 响应快速
- ✅ 编程能力良好

**适用场景：**
- 简单代码生成
- 代码解释
- 日常问答

---

### 混合任务

**选择：** `qwen3.5-plus`

**理由：**
- ✅ 通用能力强
- ✅ 编程对话兼顾
- ✅ 性价比高

**适用场景：**
- 混合任务（编程 + 文档）
- 技术方案设计
- 架构讨论

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

### Q: 灵码专用 API 支持哪些功能？

**A:** 
- ✅ 代码生成
- ✅ 代码补全
- ✅ 代码解释
- ✅ 代码审查
- ✅ Bug 修复
- ✅ 代码重构
- ✅ 单元测试生成
- ✅ 技术文档生成

---

## 📝 总结

**推荐配置：**

```json
{
  "default": "qwen-coder-plus"
}
```

**理由：**
- ✅ 灵码专用 API
- ✅ 编程场景优化
- ✅ 代码能力最强
- ✅ 价格合理

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
