# YM-CODE LLM 配置指南

## 阿里云百炼接入

### 1. 获取 API Key

1. 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
2. 进入"API-KEY 管理"页面
3. 创建新的 API Key

### 2. 设置环境变量

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_API_KEY="sk-your-api-key-here"
```

**Windows (CMD):**
```cmd
set DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export DASHSCOPE_API_KEY="sk-your-api-key-here"
```

### 3. 永久配置（推荐）

创建 `.env` 文件在 YM-CODE 根目录：
```
DASHSCOPE_API_KEY=sk-your-api-key-here
```

### 4. 测试

启动 YM-CODE:
```bash
ym-code
```

输入自然语言问题，例如：
- "帮我搜索 Python 异步编程的最佳实践"
- "分析当前目录的代码结构"
- "执行 ls -la 命令"

## 可用模型

- `qwen-turbo` - 快速响应，适合简单任务
- `qwen-plus` - 平衡性能和成本（默认）
- `qwen-max` - 最强能力，适合复杂任务

## 工作原理

1. **用户输入** → 自然语言命令
2. **LLM 分析** → 理解意图，决定是否需要调用技能
3. **技能执行** → 调用相应的本地技能（搜索、shell、代码分析等）
4. **结果整合** → LLM 将技能执行结果整合成自然语言回复

## 支持的技能调用

LLM 可以自动调用以下技能：

| 技能 | 功能 | 示例 |
|------|------|------|
| search | 搜索信息 | "搜索 Python 教程" |
| shell | 执行命令 | "列出当前目录文件" |
| code_analysis | 代码分析 | "分析这个项目结构" |
| memory | 记忆管理 | "记住这个信息" |
| http | HTTP 请求 | "访问这个 API" |
| database | 数据库操作 | "查询用户数据" |
| formatter | 格式化 | "格式化这段代码" |
| docker | Docker 操作 | "列出运行中的容器" |

## 故障排查

### 问题：提示"未配置 DASHSCOPE_API_KEY"

**解决：** 确保环境变量已正确设置

### 问题：API 请求失败

**解决：** 
1. 检查 API Key 是否有效
2. 检查网络连接
3. 确认账户余额充足

### 问题：技能调用失败

**解决：**
1. 检查技能是否可用
2. 查看日志输出
3. 确认技能参数正确
