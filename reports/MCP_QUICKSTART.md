# YM-CODE MCP 服务器快速配置

## 🚀 方式 1：手动配置（推荐，无需 Node.js）

### 步骤 1：获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限：
   - ✅ `repo` (完整仓库权限)
   - ✅ `workflow` (CI/CD)
   - ✅ `read:org` (读取组织)
4. 生成并复制 Token

### 步骤 2：创建配置文件

创建文件：`C:\Users\Administrator\.ymcode\mcp\config.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_你的 Token"
      }
    }
  }
}
```

### 步骤 3：使用

```bash
python -m ymcode
# 然后说：列出我的 GitHub 仓库
```

---

## 🚀 方式 2：使用 Python 脚本（推荐，自动配置）

### 创建配置脚本

保存为 `setup_mcp_simple.py`：

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from getpass import getpass

def setup():
    print("YM-CODE MCP 配置")
    print("=" * 50)
    
    # 获取 Token
    print("\n获取 GitHub Token:")
    print("1. 访问：https://github.com/settings/tokens")
    print("2. Generate new token (classic)")
    print("3. 勾选：repo, workflow, read:org")
    print()
    
    token = getpass("输入 GitHub Token: ")
    
    # 创建配置
    config_dir = Path.home() / ".ymcode" / "mcp"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "mcpServers": {
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": token}
            }
        }
    }
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置完成！")
    print(f"配置文件：{config_file}")
    print(f"\n使用：python -m ymcode")

if __name__ == "__main__":
    setup()
```

### 运行

```bash
python setup_mcp_simple.py
```

---

## 🚀 方式 3：直接使用 Python API（最简单）

在 YM-CODE 中直接使用：

```python
from ymcode.mcp import MCPClient

# 创建客户端
client = MCPClient()

# 连接 GitHub
await client.connect(
    "github",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "ghp_你的 Token"}
)

# 使用
tools = await client.get_tools_definition()
print(f"可用工具：{len(tools)}")
```

---

## 📦 无需 Node.js 的替代方案

如果不想安装 Node.js，可以使用 **Python 原生 MCP 客户端**：

### 安装

```bash
pip install mcp
```

### 使用

```python
from mcp import Client

client = Client()
# 直接使用 HTTP 连接到 MCP 服务器
```

---

## 🎯 推荐方案

**对于个人使用：**

1. **最简单** - 使用 YM-CODE 本地 Skills（无需配置）
   - ShellSkill - 命令执行
   - SearchSkill - 文件搜索
   - HTTPSkill - HTTP 请求
   - 等 9 个技能

2. **需要 GitHub** - 手动配置 config.json
   - 获取 Token
   - 创建配置文件
   - 直接使用

3. **团队协作** - 安装 Node.js + 完整 MCP
   - 安装 Node.js
   - 运行自动配置脚本
   - 使用所有 MCP 服务器

---

## 📝 配置文件位置

| 系统 | 路径 |
|------|------|
| Windows | `C:\Users\你的用户名\.ymcode\mcp\config.json` |
| Linux | `~/.ymcode/mcp/config.json` |
| macOS | `~/.ymcode/mcp/config.json` |

---

## ✅ 验证配置

创建测试文件 `test_mcp_config.py`：

```python
#!/usr/bin/env python3
import json
from pathlib import Path

config_file = Path.home() / ".ymcode" / "mcp" / "config.json"

if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
    
    print("✅ 配置文件存在")
    print(f"配置的服务器：{list(config['mcpServers'].keys())}")
    
    if 'github' in config['mcpServers']:
        token = config['mcpServers']['github']['env']['GITHUB_TOKEN']
        print(f"GitHub Token: {token[:10]}...{token[-4:]}")
else:
    print("❌ 配置文件不存在")
    print(f"创建：{config_file}")
```

运行：

```bash
python test_mcp_config.py
```

---

**选择适合你的方式开始使用吧！** 🚀
