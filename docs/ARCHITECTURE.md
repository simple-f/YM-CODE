# YM-CODE 代码架构规范

**版本：** v0.7.0  
**时间：** 2026-03-16  
**目标：** 清晰、整洁、易维护

---

## 🏗️ 架构分层

### 核心分层

```
YM-CODE/
├── 核心层 (core/)        # 核心引擎，不依赖具体功能
│   ├── LLM 客户端
│   ├── Agent 引擎
│   ├── 上下文管理
│   └── 状态管理
│
├── 功能层 (skills/)      # 技能系统，实现具体能力
│   ├── 基础技能
│   ├── 开发技能
│   └── 扩展技能
│
├── 工具层 (tools/)       # 工具函数，被技能调用
│   ├── 文件工具
│   ├── Git 工具
│   └── 测试工具
│
├── 接口层 (api/, cli/)   # 对外接口
│   ├── REST API
│   ├── Web 界面
│   └── CLI 工具
│
└── 支持层 (utils/)       # 辅助功能
    ├── 日志
    ├── 配置
    └── 工具函数
```

---

## 📁 目录结构规范

### 标准模块结构

```
module_name/
├── __init__.py        # 模块导出
├── base.py            # 基类定义
├── core.py            # 核心实现
├── config.py          # 配置管理
├── utils.py           # 工具函数
└── tests/             # 测试文件
    ├── test_core.py
    └── test_utils.py
```

### 文件命名规范

**✅ 好的命名：**
- `llm_client.py` - 清晰表达用途
- `context_manager.py` - 明确功能
- `code_analyzer.py` - 一目了然

**❌ 避免的命名：**
- `utils.py` - 太泛，应该具体化
- `helper.py` - 不够明确
- `temp.py` - 临时文件不应提交

---

## 🎨 代码风格规范

### 1. 导入规范

```python
# 顺序：标准库 → 第三方 → 本地模块
import os
import sys
from typing import Dict, List

import requests
from fastapi import FastAPI

from ..utils.logger import get_logger
from .base import BaseSkill
```

### 2. 类设计

```python
class BaseSkill:
    """技能基类（所有技能必须继承）"""
    
    def __init__(self, name: str):
        self.name = name
    
    @property
    def description(self) -> str:
        """技能描述（必须实现）"""
        raise NotImplementedError
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能（必须实现）"""
        raise NotImplementedError
```

### 3. 函数设计

```python
# ✅ 好的函数
def process_user_message(message: str, context: Dict) -> str:
    """处理用户消息"""
    pass

# ❌ 避免的函数
def do_something(data, flag=False, **kwargs):  # 参数不明确
    pass
```

### 4. 错误处理

```python
# ✅ 好的错误处理
try:
    result = await self.model.chat(prompt)
    return result
except ModelError as e:
    logger.error(f"模型调用失败：{e}")
    return {"error": str(e)}
except Exception as e:
    logger.error(f"未知错误：{e}")
    raise

# ❌ 避免的错误处理
try:
    do_something()
except:  # 捕获所有异常
    pass  # 静默失败
```

---

## 📝 文档规范

### 1. 模块文档

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 客户端模块

提供统一的 LLM 调用接口，支持 API 和本地模型。

使用示例:
    >>> from ymcode.core.llm_client import LLMClient
    >>> client = LLMClient()
    >>> response = client.chat("你好")
"""
```

### 2. 类文档

```python
class ContextManager:
    """
    上下文管理器
    
    自动处理长上下文，支持压缩和分片。
    
    属性:
        max_tokens (int): 最大 token 数
        compression_threshold (float): 压缩阈值
    
    使用示例:
        >>> manager = ContextManager(max_tokens=8000)
        >>> processed = manager.process(context)
    """
```

### 3. 函数文档

```python
def process_context(context: Any, max_tokens: int = 8000) -> Any:
    """
    处理上下文
    
    参数:
        context: 原始上下文
        max_tokens: 最大 token 数
    
    返回:
        处理后的上下文
    
    异常:
        ValueError: 当上下文格式错误时
    """
```

---

## 🧪 测试规范

### 1. 测试文件组织

```
tests/
├── unit/              # 单元测试
│   ├── test_llm.py
│   ├── test_skills.py
│   └── test_tools.py
│
├── integration/       # 集成测试
│   ├── test_api.py
│   └── test_workspace.py
│
└── e2e/              # 端到端测试
    └── test_full_workflow.py
```

### 2. 测试命名

```python
# ✅ 好的命名
def test_llm_client_chat():
    """测试 LLM 聊天功能"""
    pass

def test_context_manager_compress():
    """测试上下文压缩功能"""
    pass

# ❌ 避免的命名
def test1():  # 不明确
    pass

def test_stuff():  # 太泛
    pass
```

### 3. 测试结构

```python
import pytest
from ymcode.core.llm_client import LLMClient

class TestLLMClient:
    """LLM 客户端测试"""
    
    def test_chat_success(self):
        """测试聊天成功"""
        client = LLMClient()
        response = client.chat("你好")
        assert response is not None
    
    def test_chat_with_context(self):
        """测试带上下文的聊天"""
        client = LLMClient()
        context = [{"role": "user", "content": "之前的问题"}]
        response = client.chat("继续", context)
        assert response is not None
```

---

## 🔄 重构指南

### 何时重构

**✅ 应该重构的情况：**
- 函数超过 50 行
- 类超过 300 行
- 文件超过 500 行
- 重复代码出现 3 次以上
- 一个类有超过 7 个方法

**❌ 不需要重构的情况：**
- 代码能工作且清晰
- 重构风险大于收益
- 即将被替换的旧代码

### 重构步骤

1. **确保测试覆盖** - 先写测试
2. **小步重构** - 每次只改一点
3. **频繁测试** - 每步都验证
4. **提交代码** - 重构完成就提交

---

## 📊 代码质量指标

### 复杂度指标

| 指标 | 目标值 | 警告值 |
|------|--------|--------|
| 函数行数 | < 50 | > 100 |
| 类行数 | < 300 | > 500 |
| 文件行数 | < 500 | > 1000 |
| 圈复杂度 | < 10 | > 20 |
| 测试覆盖 | > 80% | < 60% |

### 检查工具

```bash
# 安装工具
pip install pylama radon coverage

# 检查代码质量
pylama ymcode/

# 检查复杂度
radon cc ymcode/ -a

# 检查测试覆盖
coverage run -m pytest
coverage report
```

---

## 🎯 维护清单

### 每日维护

- [ ] 清理临时文件
- [ ] 检查日志输出
- [ ] 审查代码提交

### 每周维护

- [ ] 运行代码质量检查
- [ ] 更新依赖
- [ ] 清理废弃代码

### 每月维护

- [ ] 重构复杂模块
- [ ] 更新文档
- [ ] 性能优化

---

## ✅ 检查清单

### 提交前检查

- [ ] 代码通过质量检查
- [ ] 测试全部通过
- [ ] 文档已更新
- [ ] 无临时文件
- [ ] 无调试代码

### 发布前检查

- [ ] 所有功能测试通过
- [ ] 性能测试通过
- [ ] 文档完整
- [ ] 变更日志更新
- [ ] 版本号更新

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team  
**状态：** ✅ 生效中
