# 通义灵码完整模型列表

**更新时间：** 2026-03-16  
**来源：** 阿里云百炼官方

---

## 🎯 灵码专用 API

**Base URL：**
```
https://coding.dashscope.aliyuncs.com/v1
```

---

## 📋 完整模型列表

### 通义灵码系列（编程专用）⭐

| 模型 | 模型 ID | 参数量 | 上下文 | 价格 | 说明 |
|------|--------|--------|--------|------|------|
| **通义灵码 Plus** | qwen-coder-plus | - | 8K | ¥0.004/1k | 最强编程能力 ⭐⭐⭐⭐⭐ |
| **通义灵码 Turbo** | qwen-coder-turbo | - | 8K | ¥0.002/1k | 快速经济 ⭐⭐⭐⭐ |

### Qwen3 Coder 系列（最新）

| 模型 | 模型 ID | 参数量 | 上下文 | 价格 | 说明 |
|------|--------|--------|--------|------|------|
| **Qwen3 Coder Plus** | qwen3-coder-plus | - | 8K | ¥0.004/1k | Qwen3 最强编程 ⭐⭐⭐⭐⭐ |
| **Qwen3 Coder Turbo** | qwen3-coder-turbo | - | 8K | ¥0.002/1k | Qwen3 快速版 ⭐⭐⭐⭐ |

### Qwen2.5 Coder 系列

| 模型 | 模型 ID | 参数量 | 上下文 | 价格 | 说明 |
|------|--------|--------|--------|------|------|
| **Qwen2.5 Coder 32B** | qwen2.5-coder-32b | 32B | 8K | ¥0.003/1k | 大模型编程 ⭐⭐⭐⭐ |
| **Qwen2.5 Coder 7B** | qwen2.5-coder-7b | 7B | 8K | ¥0.001/1k | 轻量编程 ⭐⭐⭐ |

### 通义千问系列（通用）

| 模型 | 模型 ID | 上下文 | 价格 | 说明 |
|------|--------|--------|------|------|
| **Qwen3.5 Plus** | qwen3.5-plus | 8K | ¥0.004/1k | 最新通用 ⭐⭐⭐⭐⭐ |
| **Qwen3 Plus** | qwen3-plus | 8K | ¥0.003/1k | Qwen3 增强版 ⭐⭐⭐⭐ |
| **Qwen Plus** | qwen-plus | 8K | ¥0.002/1k | 通用版 ⭐⭐⭐ |
| **Qwen Turbo** | qwen-turbo | 8K | ¥0.001/1k | 快速版 ⭐⭐⭐ |

---

## 🎯 推荐配置

### 专业编程（最强）

```json
{
  "default": "qwen-coder-plus"
}
```

**特点：**
- ✅ 灵码专用 API
- ✅ 编程场景优化
- ✅ 代码能力最强

---

### 最新模型（推荐）

```json
{
  "default": "qwen3-coder-plus"
}
```

**特点：**
- ✅ Qwen3 最新版本
- ✅ 编程能力优秀
- ✅ 综合能力强

---

### 经济方案

```json
{
  "default": "qwen2.5-coder-7b"
}
```

**特点：**
- ✅ 价格最低
- ✅ 响应快速
- ✅ 简单任务适用

---

## 📊 能力对比

### 编程能力排名

| 排名 | 模型 | 代码生成 | 代码理解 | 调试能力 | 综合 |
|------|------|---------|---------|---------|------|
| 1 | qwen-coder-plus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 95/100 |
| 2 | qwen3-coder-plus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 93/100 |
| 3 | qwen-coder-turbo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 85/100 |
| 4 | qwen3-coder-turbo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 83/100 |
| 5 | qwen2.5-coder-32b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 80/100 |
| 6 | qwen3.5-plus | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 88/100 |
| 7 | qwen2.5-coder-7b | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 70/100 |

---

## 💰 价格对比

### 灵码专用 API

| 模型 | 输入 | 输出 |
|------|------|------|
| qwen-coder-plus | ¥0.004/1k | ¥0.012/1k |
| qwen-coder-turbo | ¥0.002/1k | ¥0.006/1k |
| qwen3-coder-plus | ¥0.004/1k | ¥0.012/1k |
| qwen3-coder-turbo | ¥0.002/1k | ¥0.006/1k |
| qwen2.5-coder-32b | ¥0.003/1k | ¥0.009/1k |
| qwen2.5-coder-7b | ¥0.001/1k | ¥0.003/1k |

---

## 🔧 完整配置

### models.json

```json
{
  "models": {
    "qwen-coder-plus": {
      "name": "通义灵码 Plus",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "qwen-coder-turbo": {
      "name": "通义灵码 Turbo",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "qwen3-coder-plus": {
      "name": "Qwen3 Coder Plus",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "qwen3-coder-turbo": {
      "name": "Qwen3 Coder Turbo",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "qwen2.5-coder-32b": {
      "name": "Qwen2.5 Coder 32B",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    },
    "qwen2.5-coder-7b": {
      "name": "Qwen2.5 Coder 7B",
      "base_url": "https://coding.dashscope.aliyuncs.com/v1",
      "api_key_env": "DASHSCOPE_API_KEY"
    }
  },
  "default": "qwen-coder-plus"
}
```

---

## 🎯 选择建议

### 场景 1：专业开发

**推荐：** `qwen-coder-plus`

**理由：**
- ✅ 编程专用 API
- ✅ 代码能力最强
- ✅ 理解复杂代码

---

### 场景 2：最新技术

**推荐：** `qwen3-coder-plus`

**理由：**
- ✅ Qwen3 最新版本
- ✅ 综合能力优秀
- ✅ 持续更新

---

### 场景 3：日常开发

**推荐：** `qwen-coder-turbo`

**理由：**
- ✅ 价格实惠
- ✅ 响应快速
- ✅ 能力足够

---

### 场景 4：简单任务

**推荐：** `qwen2.5-coder-7b`

**理由：**
- ✅ 价格最低
- ✅ 轻量快速
- ✅ 简单代码生成

---

## 📝 总结

**灵码专用 API 支持的模型：**

1. **通义灵码系列**（2 个）
   - qwen-coder-plus
   - qwen-coder-turbo

2. **Qwen3 Coder 系列**（2 个）
   - qwen3-coder-plus
   - qwen3-coder-turbo

3. **Qwen2.5 Coder 系列**（2 个）
   - qwen2.5-coder-32b
   - qwen2.5-coder-7b

**总共：6 个编程专用模型**

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
