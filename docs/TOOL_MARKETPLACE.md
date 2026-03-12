# YM-CODE 工具市场

> 第三方工具扩展平台

---

## 🎯 什么是工具市场

工具市场是一个让开发者分享和下载 YM-CODE 工具的平台。

### 核心功能

- ✅ **工具发布** - 开发者可以发布自定义工具
- ✅ **工具搜索** - 用户可以搜索需要的工具
- ✅ **一键安装** - 简单命令即可安装工具
- ✅ **版本管理** - 支持工具版本控制
- ✅ **评分系统** - 用户可以为工具评分

---

## 🚀 使用指南

### 安装工具

```bash
# 从市场安装工具
ym-code tool install <tool-name>

# 示例：安装 GitHub 工具
ym-code tool install github-tools

# 安装指定版本
ym-code tool install github-tools@1.0.0
```

### 发布工具

```bash
# 初始化新项目
ym-code tool init my-tool

# 构建工具
ym-code tool build

# 发布到市场
ym-code tool publish
```

### 搜索工具

```bash
# 搜索工具
ym-code tool search github

# 查看工具详情
ym-code tool info github-tools
```

---

## 📁 工具结构

```
my-tool/
├── tool.json              # 工具配置
├── src/
│   └── main.py           # 工具代码
├── tests/
│   └── test_main.py      # 测试代码
├── README.md             # 工具说明
└── requirements.txt      # 依赖
```

### tool.json 示例

```json
{
  "name": "github-tools",
  "version": "1.0.0",
  "description": "GitHub 操作工具集",
  "author": "Your Name",
  "license": "MIT",
  "tools": [
    {
      "name": "github_issue",
      "description": "创建 GitHub Issue"
    },
    {
      "name": "github_pr",
      "description": "创建 Pull Request"
    }
  ],
  "repository": "https://github.com/your-username/github-tools"
}
```

---

## 🔧 开发工具

### 1. 创建工具模板

```python
# src/main.py
from ymcode.tools.base import BaseTool

class GitHubIssueTool(BaseTool):
    name = "github_issue"
    description = "创建 GitHub Issue"
    
    async def execute(self, title: str, body: str = "") -> str:
        """
        创建 Issue
        
        参数:
            title: Issue 标题
            body: Issue 内容
        
        返回:
            创建结果
        """
        # 实现代码
        return f"Issue created: {title}"
```

### 2. 编写测试

```python
# tests/test_main.py
import pytest
from src.main import GitHubIssueTool

class TestGitHubIssueTool:
    @pytest.mark.asyncio
    async def test_create_issue(self):
        tool = GitHubIssueTool()
        result = await tool.execute(
            title="Test Issue",
            body="Test Body"
        )
        assert "Issue created" in result
```

### 3. 构建和发布

```bash
# 构建
ym-code tool build

# 测试
ym-code tool test

# 发布
ym-code tool publish
```

---

## 📊 工具分类

| 分类 | 工具示例 | 数量 |
|------|----------|------|
| **版本控制** | git, github, gitlab | 3 个 |
| **数据库** | mysql, postgres, mongodb | 3 个 |
| **云服务** | aws, azure, gcp | 3 个 |
| **开发工具** | docker, k8s, terraform | 3 个 |
| **AI 工具** | openai, anthropic, huggingface | 3 个 |
| **其他** | ... | N 个 |

---

## 🏆 热门工具

| 工具 | 下载量 | 评分 | 描述 |
|------|--------|------|------|
| github-tools | 10k+ | ⭐⭐⭐⭐⭐ | GitHub 操作工具集 |
| docker-tools | 8k+ | ⭐⭐⭐⭐⭐ | Docker 容器管理 |
| aws-tools | 7k+ | ⭐⭐⭐⭐ | AWS 云服务操作 |
| database-tools | 6k+ | ⭐⭐⭐⭐ | 数据库操作工具 |

---

## 📝 审核标准

### 工具发布要求

1. ✅ 完整的文档（README）
2. ✅ 单元测试覆盖
3. ✅ 代码质量检查通过
4. ✅ 安全性扫描通过
5. ✅ 功能描述清晰

### 审核流程

```
提交 → 自动检查 → 人工审核 → 发布
         ↓           ↓
      不通过      不通过
         ↓           ↓
      修改        修改
```

---

## 🔐 安全性

### 工具安全检查

- ✅ 无恶意代码
- ✅ 无敏感信息泄露
- ✅ 无危险操作（需用户授权）
- ✅ 依赖安全扫描

### 用户权限

```bash
# 查看工具权限
ym-code tool permissions <tool-name>

# 授权工具
ym-code tool grant <tool-name> <permission>

# 撤销授权
ym-code tool revoke <tool-name> <permission>
```

---

## 📖 相关文档

- [YM-CODE 开发文档](./DEVELOPMENT.md)
- [工具开发指南](./TOOL_DEVELOPMENT.md)
- [API 参考](./API_REFERENCE.md)

---

_最后更新：2026-03-12_

_作者：YM-CODE Team_
