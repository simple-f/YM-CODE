# YM-CODE 项目设置指南

> 快速开始指南

---

## 📋 前提条件

- Python 3.10+
- Git
- GitHub 账号

---

## 🚀 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`YM-CODE`
3. 描述：`YM-CODE - Next Generation AI Programming Assistant`
4. 可见性：**Public**
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

---

## 🚀 步骤 2：推送代码到 GitHub

```bash
# 进入项目目录
cd /path/to/YM-CODE

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/your-username/YM-CODE.git

# 推送到 GitHub
git push -u origin master
```

---

## 🚀 步骤 3：安装开发依赖

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -e ".[dev]"
```

---

## 🚀 步骤 4：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入 API Key
ANTHROPIC_API_KEY=sk-xxx
```

---

## 🚀 步骤 5：运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_core.py
```

---

## 🚀 步骤 6：运行 CLI（开发中）

```bash
# 运行 CLI
python -m ymcode.cli

# 或使用安装后的命令（计划中）
ym-code
```

---

## 📞 遇到问题？

- **GitHub Issues**: https://github.com/simple-f/YM-CODE/issues
- **Discord**: （待创建）
- **微信群**: （待创建）

---

_最后更新：2026-03-12_
