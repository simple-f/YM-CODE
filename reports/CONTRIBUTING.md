# Contributing to YM-CODE

首先，感谢你愿意为 YM-CODE 做出贡献！

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [提交指南](#提交指南)
- [代码风格](#代码风格)
- [测试](#测试)

---

## 行为准则

本项目采用 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。
我们期望所有贡献者都能尊重他人，保持友好和包容的社区环境。

---

## 如何贡献

### 报告 Bug

1. 搜索现有的 [Issues](https://github.com/your-org/ym-code/issues) 确认是否已报告
2. 如果没有，创建新 Issue 并提供：
   - 清晰的标题
   - 详细的复现步骤
   - 期望行为和实际行为
   - 环境信息（OS、Python 版本等）

### 提出新功能

1. 先查看 [ROADMAP.md](ROADMAP.md) 确认是否在计划中
2. 创建 Issue 描述新功能：
   - 使用场景
   - 预期效果
   - 可能的实现方案

### 提交代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/your-org/ym-code.git
cd ym-code
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 4. 运行测试

```bash
pytest tests/
```

---

## 提交指南

### Commit Message 格式

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

#### 示例

```
feat(shell): 添加跨平台命令转换

- 实现 Windows/Linux/macOS 命令自动映射
- ls -> dir (Windows)
- cat -> type (Windows)

Closes #123
```

### Branch 命名

- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 重构

---

## 代码风格

### Python

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 空格缩进
- 最大行宽 100 字符
- 使用 type hints

```python
# ✅ 推荐
def greet(name: str, greeting: str = "Hello") -> str:
    """Return a greeting message."""
    return f"{greeting}, {name}!"

# ❌ 避免
def greet(name,greeting="Hello"):
    return f"{greeting}, {name}!"
```

### 文档字符串

使用 Google 风格：

```python
def calculate_sum(numbers: list) -> int:
    """计算数字列表的总和。
    
    Args:
        numbers: 数字列表
        
    Returns:
        总和
        
    Raises:
        TypeError: 如果输入不是数字列表
    """
    return sum(numbers)
```

---

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试

```bash
pytest tests/test_shell.py -v
```

### 测试覆盖率

```bash
pytest --cov=ymcode tests/
```

### 编写测试

- 测试文件命名：`test_<module>.py`
- 测试函数命名：`test_<function>_<scenario>`
- 使用 `assert` 进行断言
- 保持测试独立

```python
def test_shell_command_translation_windows():
    """测试 Windows 平台命令转换。"""
    shell = ShellSkill()
    shell.os_type = "Windows"
    
    # 验证 ls 转换为 dir
    assert shell._translate_command("ls") == "dir"
```

---

## Pull Request 流程

1. **创建 PR**: 填写 PR 模板
2. **Code Review**: 至少需要 1 个维护者批准
3. **测试**: CI 自动运行测试
4. **合并**: 维护者合并到主分支

### PR 模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 重构

## 描述
简要描述此 PR 的变更内容。

## 相关 Issue
Closes #123

## 测试
- [ ] 已添加单元测试
- [ ] 已手动测试
- [ ] 测试通过

## 检查清单
- [ ] 代码符合风格指南
- [ ] 已更新文档
- [ ] 无破坏性变更
```

---

## 问题？

有任何问题欢迎：
- 创建 Issue
- 在讨论区提问
- 联系维护者

再次感谢你的贡献！🎉
