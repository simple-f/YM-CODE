# YM-CODE 安装指南

> 快速安装和测试指南

---

## 📋 前提条件

- ✅ Python 3.10+ (推荐 3.11 或 3.12)
- ✅ Git
- ✅ pip

---

## 🚀 安装步骤

### 方法 1：本地安装（推荐）

```bash
# 1. 进入项目目录
cd C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE

# 2. 安装依赖
pip install -e .

# 3. 验证安装
python -c "from ymcode import Agent; print('YM-CODE 安装成功！')"
```

### 方法 2：复制到其他目录

```bash
# 1. 复制项目到目标目录
xcopy /E /I C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE C:\Users\Administrator\YM-CODE

# 2. 进入目标目录
cd C:\Users\Administrator\YM-CODE

# 3. 安装
pip install -e .
```

---

## 🧪 快速测试

### 测试 1：导入测试

```bash
python -c "from ymcode import Agent; print('✅ 导入成功')"
```

### 测试 2：工具测试

```bash
python -c "
from ymcode.tools.registry import ToolRegistry
tools = ToolRegistry()
print(f'✅ 工具注册表初始化成功，已加载 {len(tools)} 个工具')
"
```

### 测试 3：Agent 测试

```bash
python -c "
from ymcode.core.agent import Agent
agent = Agent(config={'mock_mode': True})
print('✅ Agent 初始化成功')
"
```

---

## ⚠️ 常见问题

### 问题 1：UnicodeDecodeError

**错误信息：**
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x80
```

**解决方法：**
```bash
# 确保使用正确的编码
chcp 65001  # 设置控制台编码为 UTF-8
pip install -e .
```

### 问题 2：找不到模块

**错误信息：**
```
ModuleNotFoundError: No module named 'ymcode'
```

**解决方法：**
```bash
# 确保在项目目录
cd C:\Users\Administrator\.openclaw\workspace-ai2\shared\YM-CODE

# 重新安装
pip uninstall ym-code
pip install -e .
```

### 问题 3：CLI 无法启动

**错误信息：**
```
'ym-code' is not recognized
```

**解决方法：**
```bash
# 检查 Python Scripts 路径
python -c "import sys; print(sys.path)"

# 将 Scripts 添加到 PATH
# Windows: 添加 C:\Users\Administrator\AppData\Local\Programs\Python\Python313\Scripts
```

---

## 🎯 使用示例

### 示例 1：文件操作

```python
from ymcode.tools.file_tools import ReadFileTool, WriteFileTool
import asyncio

async def test():
    # 写入
    write = WriteFileTool()
    await write.execute(path="test.txt", content="hello")
    
    # 读取
    read = ReadFileTool()
    result = await read.execute(path="test.txt")
    print(result)

asyncio.run(test())
```

### 示例 2：Git 操作

```python
from ymcode.tools.git_tools import GitTool
import asyncio

async def test():
    git = GitTool()
    result = await git.execute(operation="status")
    print(result)

asyncio.run(test())
```

### 示例 3：Agent 工作流

```python
from ymcode.core.agent import Agent
import asyncio

async def test():
    agent = Agent(config={"mock_mode": True})
    result = await agent.run("帮我创建一个文件")
    print(result)

asyncio.run(test())
```

---

## 📖 相关文档

- [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) - 完整测试指南
- [PHASE3_SUMMARY.md](./docs/PHASE3_SUMMARY.md) - Phase 3 总结
- [README.md](./README.md) - 项目说明

---

_最后更新：2026-03-12_

_作者：YM-CODE Team_
