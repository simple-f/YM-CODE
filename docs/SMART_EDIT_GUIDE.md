# 智能编辑系统文档

**版本：** v1.0.0  
**创建日期：** 2026-03-18  
**状态：** ✅ 已完成

---

## 📚 概述

YM-CODE 智能编辑系统提供三种强大的文件编辑能力：

1. **Smart Edit** - 智能文本替换（支持模糊匹配）
2. **Regex Edit** - 正则表达式替换（支持复杂模式）
3. **Edit History** - 编辑历史管理（支持撤销/重做）

---

## 🛠️ Smart Edit - 智能编辑

### 功能特性

- ✅ 精确匹配替换
- ✅ 模糊匹配（fuzzy matching）
- ✅ 多位置替换（all_occurrences）
- ✅ 自动生成 diff
- ✅ 安全保护（文件存在性检查）

### 使用方法

```python
# 基本用法
result = await smart_edit.execute(
    path="src/example.py",
    old_text="def old_function():",
    new_text="def new_function():"
)

# 模糊匹配
result = await smart_edit.execute(
    path="src/example.py",
    old_text="def old_func():",  # 近似匹配
    new_text="def new_function():",
    fuzzy=True
)

# 替换所有匹配项
result = await smart_edit.execute(
    path="src/example.py",
    old_text="print('debug')",
    new_text="pass",
    all_occurrences=True
)
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | str | ✅ | 文件路径 |
| old_text | str | ✅ | 原文本 |
| new_text | str | ✅ | 新文本 |
| fuzzy | bool | ❌ | 是否模糊匹配（默认 False） |
| all_occurrences | bool | ❌ | 是否替换所有匹配（默认 False） |

### 返回值

```
✓ 文件已编辑：src/example.py

--- a/src/example.py
+++ b/src/example.py
@@ -10,7 +10,7 @@
 def old_function():
     pass
```

---

## 🔣 Regex Edit - 正则编辑

### 功能特性

- ✅ 完整正则表达式支持
- ✅ 反向引用（\1, \2, ...）
- ✅ 多标志支持（i/m/s）
- ✅ 匹配预览（显示前 5 个匹配）
- ✅ 批量替换

### 使用方法

```python
# 基本替换
result = await regex_edit.execute(
    path="src/example.py",
    pattern=r"def (\w+)\(\):",
    replacement=r"def \1_new():"
)

# 忽略大小写
result = await regex_edit.execute(
    path="src/example.py",
    pattern=r"TODO",
    replacement=r"DONE",
    flags="i"  # 忽略大小写
)

# 限制替换次数
result = await regex_edit.execute(
    path="src/example.py",
    pattern=r"old",
    replacement=r"new",
    count=3  # 只替换前 3 处
)
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | str | ✅ | 文件路径 |
| pattern | str | ✅ | 正则表达式模式 |
| replacement | str | ✅ | 替换文本 |
| count | int | ❌ | 替换次数（0=全部） |
| flags | str | ❌ | 正则标志（i/m/s） |

### 正则标志

| 标志 | 说明 | 示例 |
|------|------|------|
| i | 忽略大小写 | `pattern="TODO", flags="i"` |
| m | 多行模式 | `^` 和 `$` 匹配行首尾 |
| s | 单行模式 | `.` 匹配包括换行符 |

### 返回值

```
✓ 正则替换完成：src/example.py

找到 3 处匹配：

1. 位置 120-170: `def process_data():...`
2. 位置 450-500: `def validate_input():...`
3. 位置 780-830: `def save_results():...`

替换了 3 处，文件变化 +5 行
```

---

## 📜 Edit History - 编辑历史

### 功能特性

- ✅ 自动记录所有编辑
- ✅ 支持撤销（undo）
- ✅ 支持重做（redo）
- ✅ 历史记录持久化
- ✅ 差异对比

### 使用方法

```python
# 查看编辑历史
history = edit_history.get_history("src/example.py")

# 撤销上一次编辑
result = await edit_history.undo("src/example.py")

# 重做已撤销的编辑
result = await edit_history.redo("src/example.py")

# 清除历史记录
edit_history.clear_history("src/example.py")
```

### API 接口

```python
class EditHistory:
    def record_edit(self, path, old_content, new_content) -> None
    def get_history(self, path) -> List[EditRecord]
    async def undo(self, path) -> str
    async def redo(self, path) -> str
    def clear_history(self, path) -> None
```

---

## 🧪 测试用例

### Smart Edit 测试

```bash
# 运行测试
pytest tests/test_smart_edit.py -v

# 测试用例
- test_exact_match: 精确匹配替换
- test_fuzzy_match: 模糊匹配
- test_all_occurrences: 多位置替换
- test_file_not_found: 文件不存在处理
- test_generate_diff: diff 生成
```

### Regex Edit 测试

```bash
# 运行测试
pytest tests/test_regex_edit.py -v

# 测试用例
- test_basic_replace: 基本替换
- test_regex_flags: 正则标志
- test_back_reference: 反向引用
- test_invalid_pattern: 无效模式处理
- test_count_limit: 替换次数限制
```

### Edit History 测试

```bash
# 运行测试
pytest tests/test_edit_history.py -v

# 测试用例
- test_record_edit: 记录编辑
- test_undo: 撤销功能
- test_redo: 重做功能
- test_persistence: 持久化
- test_clear_history: 清除历史
```

---

## 🎯 最佳实践

### 1. 精确匹配优先

```python
# ✅ 推荐：提供足够上下文
old_text = "def process_data(self, items: List[str]):"

# ❌ 避免：太短容易误匹配
old_text = "def process_data():"
```

### 2. 模糊匹配慎用

```python
# ✅ 适用场景：重构、重命名
result = await smart_edit.execute(
    path="src/legacy.py",
    old_text="old_api_call",
    new_text="new_api_call",
    fuzzy=True,
    all_occurrences=True
)

# ❌ 不适用：精确结构修改
```

### 3. 正则表达式测试

```python
# ✅ 推荐：先测试正则
import re
pattern = r"def (\w+)\(\):"
test_text = "def example():"
assert re.match(pattern, test_text)

# 然后再执行替换
```

### 4. 编辑历史记录

```python
# ✅ 推荐：重要编辑前手动备份
import shutil
shutil.copy("src/example.py", "src/example.py.bak")

# 然后执行编辑
```

---

## ⚠️ 注意事项

### 安全警告

1. **编码问题** - 默认使用 UTF-8，非 UTF-8 文件需特殊处理
2. **大文件** - 超过 10MB 的文件建议分块处理
3. **并发编辑** - 避免多个进程同时编辑同一文件
4. **符号链接** - 符号链接会被解析为真实路径

### 性能建议

1. **批量编辑** - 多次小编辑合并为一次大编辑
2. **正则优化** - 避免灾难性回溯（如 `(a+)+`）
3. **历史清理** - 定期清理不再需要的编辑历史

---

## 📊 性能指标

| 操作 | 平均耗时 | 适用场景 |
|------|----------|----------|
| 精确匹配替换 | <10ms | 小文件（<1MB） |
| 模糊匹配替换 | <100ms | 中等文件（<5MB） |
| 正则替换 | <50ms | 复杂模式 |
| 撤销/重做 | <5ms | 即时回滚 |

---

## 🚀 未来计划

- [ ] 支持多文件批量编辑
- [ ] 支持二进制文件编辑
- [ ] 支持远程文件编辑
- [ ] AI 辅助编辑建议
- [ ] 编辑冲突检测

---

**文档完成时间：** 2026-03-18  
**P0-4 状态：** ✅ 已完成
