# YM-CODE 跨平台使用说明

支持 **Windows**、**Linux**、**macOS** 三大平台。

---

## 🖥️ 系统要求

| 平台 | 版本要求 | Python 版本 |
|------|----------|-------------|
| Windows | 10/11 | 3.10+ |
| Linux | Ubuntu 20.04+, CentOS 7+, Debian 10+ | 3.10+ |
| macOS | 11+ (Big Sur 及更高) | 3.10+ |

---

## 📦 安装步骤

### 通用安装

```bash
# 克隆项目
git clone <repo-url>
cd YM-CODE

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 🚀 运行方式

### 方式 1: 直接运行

```bash
# 所有平台通用
python -m ymcode
```

### 方式 2: 调试模式

```bash
# 显示系统信息
python -m ymcode --debug
```

---

## 🔧 跨平台特性

### 1. Shell 命令自动转换

YM-CODE 会自动检测操作系统并转换命令：

| Unix 命令 | Windows 等价命令 |
|-----------|------------------|
| `ls` | `dir` |
| `cat` | `type` |
| `pwd` | `cd` |
| `rm` | `del` |
| `cp` | `copy` |
| `mv` | `move` |
| `grep` | `findstr` |

**示例：**
```python
# 代码中统一使用 Unix 风格
await shell.execute({'command': 'ls', 'args': ['-la']})

# Windows 上自动转换为: dir -la
# Linux/macOS 上保持：ls -la
```

### 2. 路径处理

使用 `pathlib.Path` 自动处理路径分隔符：

```python
from pathlib import Path

# 正确 ✅
config_path = Path.home() / ".ymcode" / "config.json"

# 避免 ❌
config_path = "~/.ymcode/config.json"  # 不要硬编码 /
```

### 3. 环境变量

所有平台统一使用 UTF-8 编码：

```bash
# 自动设置，无需手动配置
PYTHONIOENCODING=utf-8
```

### 4. 终端颜色

- **Windows**: 自动检测终端能力，保守模式（无颜色）
- **Linux/macOS**: 启用彩色输出

---

## 📋 平台特定说明

### Windows

**控制台编码：**
- 自动设置为 UTF-8 (代码页 65001)
- 如遇中文乱码，手动执行：`chcp 65001`

**PowerShell 兼容性：**
```powershell
# PowerShell 中运行
python -m ymcode

# 或 CMD 中运行
python -m ymcode
```

**注意事项：**
- 部分 Unix 命令不可用（如 `chmod`, `chown`）
- 使用 `shell=True` 执行内置命令（如 `dir`, `cd`）

---

### Linux

**依赖安装：**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# CentOS/RHEL
sudo yum install -y python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

**权限问题：**
```bash
# 如遇权限错误，使用 sudo
sudo python -m ymcode

# 或修改目录权限
chmod -R 755 ~/.ymcode
```

---

### macOS

**安装 Python：**
```bash
# 使用 Homebrew
brew install python@3.13

# 或使用系统自带 Python
python3 -m ymcode
```

**终端.app 设置：**
- 偏好设置 → 描述文件 → 高级
- 勾选 "使用 Unicode UTF-8"

---

## 🐛 常见问题

### Q1: 中文乱码

**Windows:**
```bash
chcp 65001
python -m ymcode
```

**Linux/macOS:**
```bash
export LANG=zh_CN.UTF-8
python -m ymcode
```

### Q2: 命令找不到

检查命令是否在当前平台可用：

```python
# 跨平台命令
python --version  # ✅ 所有平台
node --version    # ✅ 所有平台
git --version     # ✅ 所有平台

# 平台特定命令
dir               # ⚠️ Windows only
ls                # ⚠️ Linux/macOS only
```

### Q3: 权限错误

**Linux/macOS:**
```bash
# 修改数据目录权限
chmod -R 755 ~/.ymcode
```

**Windows:**
```powershell
# 以管理员身份运行 PowerShell
Start-Process powershell -Verb RunAs
```

---

## 📊 跨平台测试

运行跨平台测试脚本：

```bash
python test_cross_platform.py
```

输出示例：
```
============================================================
YM-CODE 跨平台兼容性测试
============================================================

系统信息:
  操作系统：Windows
  版本：10.0.19045
  机器：AMD64
  Python: 3.13.2
  平台：win32

测试 Shell 技能跨平台命令转换:
  检测到系统：Windows
  命令别名配置：['Windows', 'Linux', 'Darwin']
  ls -> dir
  pwd -> cd
  cat -> type
  grep -> findstr

测试模块导入:
  [OK] cli.app
  [OK] core.agent
  [OK] mcp.registry
  [OK] skills.registry

============================================================
测试完成！
============================================================
```

---

## 📝 开发者注意

编写跨平台代码的准则：

1. **使用 `pathlib.Path`** 而非字符串拼接路径
2. **使用 `os.path.join`** 如果必须用字符串
3. **避免硬编码路径分隔符** (`/` 或 `\`)
4. **使用 `platform.system()`** 检测操作系统
5. **使用 `sys.platform`** 判断平台特定逻辑
6. **避免平台特定 API** 除非有 fallback

```python
# 推荐 ✅
from pathlib import Path
config_dir = Path.home() / ".ymcode"

# 不推荐 ❌
config_dir = os.path.expanduser("~/.ymcode")
```

---

## 🔄 更新日志

### v0.1.0 (2026-03-14)

- ✅ 添加 Linux/macOS 支持
- ✅ Shell 命令自动转换
- ✅ 跨平台路径处理
- ✅ 统一 UTF-8 编码
- ✅ 自动终端颜色检测

---

**支持平台：** Windows 10/11 | Linux (Ubuntu/CentOS/Debian) | macOS 11+
