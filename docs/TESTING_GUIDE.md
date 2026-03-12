# YM-CODE 测试指南

> 完整测试流程和使用说明

---

## 📋 目录

1. [快速开始](#快速开始)
2. [安装 YM-CODE](#安装-ym-code)
3. [基础功能测试](#基础功能测试)
4. [工具系统测试](#工具系统测试)
5. [VSCode 插件测试](#vscode-插件测试)
6. [集成测试](#集成测试)
7. [性能测试](#性能测试)
8. [故障排查](#故障排查)

---

## 🚀 快速开始

### 前提条件

- ✅ Python 3.10+
- ✅ Git
- ✅ VSCode（可选，用于插件测试）

### 测试概览

```bash
# 1. 克隆项目
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE

# 2. 安装依赖
pip install -e .

# 3. 运行测试
pytest tests/ -v

# 4. 测试 CLI
ym-code --help
```

---

## 💻 安装 YM-CODE

### 方法 1：pip 安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE

# 安装
pip install -e .

# 验证安装
ym-code --version
```

### 方法 2：Docker 安装（计划中）

```bash
# 构建镜像
docker build -t ym-code .

# 运行容器
docker run -it ym-code
```

---

## 🧪 基础功能测试

### 1. 测试 CLI 界面

```bash
# 查看帮助
ym-code --help

# 查看版本
ym-code --version

# 启动交互式 CLI
ym-code
```

**预期输出：**
```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   YM-CODE v0.2.0 - AI Programming Assistant          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

🤖 Ready to help! Type your request or 'help' for commands.

>
```

### 2. 测试 Agent 核心

```python
# 创建测试脚本 test_agent.py
from ymcode.core.agent import Agent
import asyncio

async def test_agent():
    # 初始化 Agent（Mock 模式）
    agent = Agent(config={"mock_mode": True})
    
    # 测试基本对话
    result = await agent.run("你好")
    print(f"Agent 响应：{result}")
    
    # 测试工具调用
    result = await agent.run("读取当前目录文件")
    print(f"工具调用结果：{result}")

# 运行测试
python test_agent.py
```

### 3. 测试工具系统

```python
# 创建测试脚本 test_tools.py
from ymcode.tools.registry import ToolRegistry
import asyncio

async def test_tools():
    tools = ToolRegistry()
    
    # 测试 bash 工具
    result = await tools.execute([{
        "name": "bash",
        "input": {"command": "echo hello"}
    }])
    print(f"Bash 工具：{result}")
    
    # 测试文件工具
    result = await tools.execute([{
        "name": "list_dir",
        "input": {"path": "."}
    }])
    print(f"文件工具：{result}")

# 运行测试
python test_tools.py
```

---

## 🛠️ 工具系统测试

### 1. 测试文件操作工具

```python
from ymcode.tools.file_tools import ReadFileTool, WriteFileTool
import asyncio
from pathlib import Path

async def test_file_tools():
    # 测试写入
    write_tool = WriteFileTool()
    result = await write_tool.execute(
        path="test.txt",
        content="hello world"
    )
    print(f"写入结果：{result}")
    
    # 测试读取
    read_tool = ReadFileTool()
    result = await read_tool.execute(path="test.txt")
    print(f"读取结果：{result}")
    
    # 清理
    Path("test.txt").unlink()

# 运行测试
python -c "import asyncio; asyncio.run(test_file_tools())"
```

### 2. 测试 Git 工具

```python
from ymcode.tools.git_tools import GitTool
import asyncio
import subprocess
from pathlib import Path

async def test_git_tools():
    # 创建临时 Git 仓库
    test_dir = Path("test_repo")
    test_dir.mkdir(exist_ok=True)
    subprocess.run(["git", "init"], cwd=test_dir, check=True, capture_output=True)
    
    # 测试 git status
    git_tool = GitTool()
    result = await git_tool.execute(operation="status")
    print(f"Git Status: {result}")
    
    # 清理
    import shutil
    shutil.rmtree(test_dir)

# 运行测试
python -c "import asyncio; asyncio.run(test_git_tools())"
```

### 3. 测试智能编辑工具

```python
from ymcode.tools.smart_edit import SmartEditTool
import asyncio
from pathlib import Path

async def test_smart_edit():
    # 创建测试文件
    test_file = Path("test.txt")
    test_file.write_text("hello world hello")
    
    # 测试智能替换
    edit_tool = SmartEditTool()
    result = await edit_tool.execute(
        path=str(test_file),
        old_text="hello",
        new_text="hi"
    )
    print(f"智能编辑结果：{result}")
    
    # 验证结果
    content = test_file.read_text()
    print(f"文件内容：{content}")
    
    # 清理
    test_file.unlink()

# 运行测试
python -c "import asyncio; asyncio.run(test_smart_edit())"
```

---

## 🎨 VSCode 插件测试

### 1. 安装插件

```bash
cd extensions/vscode

# 安装依赖
npm install

# 编译
npm run compile
```

### 2. 运行和调试

1. 在 VSCode 中打开 `extensions/vscode` 目录
2. 按 `F5` 启动调试
3. 在新窗口中测试插件功能

### 3. 测试功能

#### 测试代码解释

1. 选中一段代码
2. 右键点击
3. 选择 "YM-CODE: Explain Code"
4. 查看侧边栏的解释

#### 测试代码审查

1. 选中一段代码
2. 右键点击
3. 选择 "YM-CODE: Review Code"
4. 查看审查报告

#### 测试快捷键

1. 选中代码
2. 按 `Ctrl+Shift+Y` (Mac: `Cmd+Shift+Y`)
3. 查看 AI 运行结果

---

## 🔗 集成测试

### 1. 完整工作流测试

```python
# 创建集成测试脚本 test_integration.py
from ymcode.core.agent import Agent
from ymcode.tools.registry import ToolRegistry
import asyncio
from pathlib import Path

async def test_full_workflow():
    """测试完整工作流"""
    # 1. 初始化 Agent
    agent = Agent(config={"mock_mode": True})
    
    # 2. 创建测试文件
    test_file = Path("integration_test.txt")
    test_file.write_text("initial content")
    
    # 3. 测试文件操作
    result = await agent.run(f"读取 {test_file} 的内容")
    print(f"读取结果：{result}")
    
    # 4. 测试智能编辑
    result = await agent.run(f"将 {test_file} 中的 'initial' 替换为 'updated'")
    print(f"编辑结果：{result}")
    
    # 5. 验证结果
    content = test_file.read_text()
    assert "updated" in content
    print(f"最终内容：{content}")
    
    # 6. 清理
    test_file.unlink()
    
    print("✅ 集成测试通过！")

# 运行测试
python test_integration.py
```

### 2. 运行官方集成测试

```bash
# 运行所有集成测试
pytest tests/test_integration.py -v

# 运行特定测试
pytest tests/test_integration.py::TestAgentIntegration::test_agent_basic_workflow -v
```

---

## ⚡ 性能测试

### 1. 工具性能测试

```python
# 创建性能测试脚本 test_performance.py
import asyncio
import time
from ymcode.tools.registry import ToolRegistry

async def test_tool_performance():
    tools = ToolRegistry()
    
    # 测试 bash 工具性能
    start = time.time()
    for i in range(100):
        await tools.execute([{
            "name": "bash",
            "input": {"command": "echo test"}
        }])
    end = time.time()
    
    avg_time = (end - start) / 100 * 1000  # 毫秒
    print(f"Bash 工具平均响应时间：{avg_time:.2f}ms")
    
    # 测试文件工具性能
    start = time.time()
    for i in range(100):
        await tools.execute([{
            "name": "read_file",
            "input": {"path": __file__}
        }])
    end = time.time()
    
    avg_time = (end - start) / 100 * 1000  # 毫秒
    print(f"ReadFile 工具平均响应时间：{avg_time:.2f}ms")

# 运行测试
python -c "import asyncio; asyncio.run(test_performance())"
```

### 2. 并发性能测试

```python
# 创建并发测试脚本 test_concurrency.py
import asyncio
import time
from ymcode.tools.registry import ToolRegistry

async def test_concurrency():
    tools = ToolRegistry()
    
    # 并发执行 10 个任务
    tasks = []
    for i in range(10):
        task = tools.execute([{
            "name": "bash",
            "input": {"command": f"echo task_{i}"}
        }])
        tasks.append(task)
    
    start = time.time()
    await asyncio.gather(*tasks)
    end = time.time()
    
    total_time = end - start
    print(f"并发执行 10 个任务耗时：{total_time:.2f}s")
    print(f"平均每个任务：{total_time/10*1000:.2f}ms")

# 运行测试
python -c "import asyncio; asyncio.run(test_concurrency())"
```

---

## 🔍 故障排查

### 常见问题

#### 1. 安装失败

**问题：** `pip install -e .` 失败

**解决：**
```bash
# 升级 pip
pip install --upgrade pip

# 清除缓存
pip cache purge

# 重新安装
pip install -e .
```

#### 2. 测试失败

**问题：** pytest 测试失败

**解决：**
```bash
# 安装测试依赖
pip install -e .[dev]

# 清除 pytest 缓存
pytest --cache-clear

# 重新运行测试
pytest tests/ -v
```

#### 3. CLI 无法启动

**问题：** `ym-code` 命令找不到

**解决：**
```bash
# 检查安装
pip show ym-code

# 检查 PATH
echo $PATH

# 重新安装
pip uninstall ym-code
pip install -e .
```

#### 4. VSCode 插件不工作

**问题：** 插件命令无响应

**解决：**
1. 检查 VSCode 版本（需要 1.85.0+）
2. 重新编译插件：`npm run compile`
3. 重新加载窗口：`Ctrl+Shift+P` → "Reload Window"

### 获取帮助

```bash
# 查看帮助
ym-code --help

# 查看版本
ym-code --version

# 查看日志
cat ~/.ymcode/logs/ymcode.log
```

---

## 📝 测试报告模板

```markdown
# YM-CODE 测试报告

**测试日期：** 2026-03-12
**测试环境：** Python 3.12, Windows 11
**测试版本：** v0.2.0

## 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| CLI 界面 | ✅ 通过 | - |
| Agent 核心 | ✅ 通过 | - |
| 工具系统 | ✅ 通过 | 18 个工具 |
| VSCode 插件 | ✅ 通过 | - |
| 集成测试 | ✅ 通过 | - |
| 性能测试 | ✅ 通过 | 平均响应<50ms |

## 性能指标

- 工具平均响应时间：XX ms
- 并发性能：XX 任务/秒
- 内存占用：XX MB

## 问题汇总

无

## 结论

YM-CODE v0.2.0 所有测试通过，可以发布！
```

---

_最后更新：2026-03-12_

_作者：YM-CODE Team_
