# YM-CODE 配置指南

> 快速配置大模型 API

---

## 📝 已配置 OpenAI 兼容接口

**配置文件位置：** `.env`

**当前配置：**
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=glm-5
```

**说明：**
- 使用 **阿里云百炼** 的 OpenAI 兼容接口
- 模型：**GLM-5**
- 基础 URL：`https://dashscope.aliyuncs.com/compatible-mode/v1`

---

## 🔧 如何获取 API Key

### 方法 1：阿里云百炼（推荐）

1. 访问：https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 进入「API-KEY 管理」
4. 创建新的 API Key
5. 复制到 `.env` 文件

### 方法 2：OpenAI 官方

1. 访问：https://platform.openai.com/api-keys
2. 登录 OpenAI 账号
3. 创建新的 API Key
4. 修改 `.env`：
   ```env
   OPENAI_API_KEY=sk-你的-openai-key
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4
   ```

### 方法 3：其他兼容接口

YM-CODE 支持任何 OpenAI 兼容的 API：

```env
OPENAI_API_KEY=你的-key
OPENAI_BASE_URL=https://你的-api 地址/v1
OPENAI_MODEL=模型名称
```

**支持的模型：**
- ✅ OpenAI GPT 系列
- ✅ 阿里云百炼 GLM 系列
- ✅ Moonshot（月之暗面）
- ✅ 智谱 AI
- ✅ 其他 OpenAI 兼容接口

---

## 📁 配置文件说明

**文件位置：** `C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE\.env`

**配置项：**

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | API Key | `sk-xxx` |
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 模型名称 | `gpt-4` |
| `YM_CODE_MAX_ITERATIONS` | 最大迭代次数 | `30` |
| `YM_CODE_TIMEOUT` | 超时时间（秒） | `300` |
| `YM_CODE_LOG_LEVEL` | 日志级别 | `INFO` |

---

## ✅ 验证配置

**测试配置是否正确：**

```bash
# 进入项目目录
cd C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE

# 启动 YM-CODE
ym-code

# 测试对话
YM-CODE> 你好
```

**如果看到 AI 响应，说明配置成功！**

---

## 🐛 故障排查

### 问题 1：提示未配置 API Key

**解决：**
```bash
# 检查 .env 文件是否存在
dir .env

# 如果不存在，创建它
copy .env.example .env

# 编辑 .env 填入 API Key
notepad .env
```

### 问题 2：API 调用失败

**解决：**
1. 检查 API Key 是否正确
2. 检查 BASE_URL 是否正确
3. 检查网络连接
4. 查看日志：
   ```bash
   type .env
   ```

### 问题 3：模型不支持

**解决：**
```env
# 修改模型名称
OPENAI_MODEL=glm-5  # 或 gpt-4, moonshot-v1 等
```

---

## 📖 相关文档

- [INSTALL.md](./INSTALL.md) - 安装指南
- [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) - 测试指南
- [README.md](./README.md) - 项目说明

---

_最后更新：2026-03-13_

_作者：YM-CODE Team_
