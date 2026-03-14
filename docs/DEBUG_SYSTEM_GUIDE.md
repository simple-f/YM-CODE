# 🔧 YM-CODE 调试系统指南

> 让黑盒变透明，让调试变简单

---

## 🎯 调试系统功能

### 核心组件

1. **Execution Tracer** - 执行追踪器
   - 记录所有函数调用
   - 参数/返回值追踪
   - 错误捕获
   - 执行时间统计

2. **Performance Profiler** - 性能分析器
   - CPU 性能分析
   - 函数调用统计
   - 热点函数识别
   - HTML 报告生成

3. **Debug CLI** - 调试命令行
   - 追踪控制
   - 性能分析
   - 会话回放
   - 报告导出

---

## 🚀 快速开始

### 1. 启用追踪

```bash
# 开始追踪
ym-code debug trace start

# 带过滤器开始追踪
ym-code debug trace start --filter skills --filter mcp

# 查看追踪状态
ym-code debug trace status
```

### 2. 执行代码

```bash
# 正常执行你的代码
ym-code "帮我分析这个项目"
```

### 3. 停止追踪

```bash
# 停止追踪
ym-code debug trace stop
```

### 4. 查看结果

```bash
# 列出追踪会话
ym-code debug trace list

# 查看追踪详情
ym-code debug trace show <session_id>

# 查看统计信息
ym-code debug trace stats <session_id>
```

---

## 📋 追踪功能

### 基本用法

```python
from ymcode.debug import trace, get_tracer

# 方法 1：使用装饰器
@trace('my_function')
async def my_function(arg1, arg2):
    return arg1 + arg2

# 方法 2：手动控制
tracer = get_tracer()
tracer.enable()

# 执行代码
result = await my_function(1, 2)

tracer.disable()
```

### 追踪事件类型

| 事件类型 | 说明 | 记录内容 |
|---------|------|---------|
| **call** | 函数调用 | 函数名、参数 |
| **return** | 函数返回 | 函数名、返回值、执行时间 |
| **error** | 函数错误 | 函数名、错误信息、执行时间 |
| **log** | 手动日志 | 自定义消息 |

### 设置断点

```python
from ymcode.debug import get_tracer

tracer = get_tracer()

# 设置断点回调
def on_skill_call(event):
    print(f"Skill 被调用：{event.target}")
    print(f"参数：{event.args}")

tracer.set_breakpoint('skills.*', on_skill_call)

# 移除断点
tracer.remove_breakpoint('skills.*')
```

---

## 📊 性能分析

### 基本用法

```python
from ymcode.debug import profile, get_profiler

# 方法 1：使用上下文
profiler = get_profiler()

with profiler.profile('my_operation'):
    # 执行代码
    result = await my_function()

# 方法 2：使用装饰器
@profiler.profile_function
async def my_function():
    # 执行代码
    pass

# 方法 3：CLI 命令
# ym-code debug profile report <profile_id>
```

### 性能报告

```bash
# 生成文本报告
ym-code debug profile report <profile_id> --format text

# 生成 HTML 报告（可视化）
ym-code debug profile report <profile_id> --format html --output report.html

# 生成 JSON 报告
ym-code debug profile report <profile_id> --format json
```

### 性能比较

```bash
# 比较两个性能分析结果
ym-code debug profile compare profile1 profile2

# 输出示例：
# Duration 差异：+0.234s
# Call Count 差异：+15
```

---

## 🔍 调试场景

### 场景 1：定位性能瓶颈

```bash
# 1. 开始性能分析
ym-code debug trace start --filter skills

# 2. 执行慢操作
ym-code "分析整个项目"

# 3. 停止追踪
ym-code debug trace stop

# 4. 查看统计
ym-code debug trace stats <session_id>

# 5. 找出最慢的函数
ym-code debug trace show <session_id>
```

### 场景 2：调试错误

```bash
# 1. 启用详细追踪
ym-code debug trace start

# 2. 重现错误
ym-code "执行某个操作"

# 3. 回放会话
ym-code debug trace replay <session_id>

# 4. 导出错误日志
ym-code debug trace export <session_id> --format json --output error.json
```

### 场景 3：优化代码性能

```bash
# 1. 分析优化前
with profiler.profile('before_optimization'):
    # 原始代码

# 2. 优化代码
# ... 优化 ...

# 3. 分析优化后
with profiler.profile('after_optimization'):
    # 优化后代码

# 4. 比较结果
ym-code debug profile compare before_optimization after_optimization
```

---

## 📁 数据存储

### 追踪数据

```
~/.ym-code/debug/traces/
├── <session_id>.json    # 追踪会话数据
├── <session_id>.json    # 追踪会话数据
└── ...
```

### 性能分析数据

```
~/.ym-code/debug/profiles/
├── <profile_id>.json    # 性能分析结果
├── <profile_id>.html    # HTML 报告
└── ...
```

---

## 🎯 CLI 命令速查

### 追踪命令

```bash
ym-code debug trace start          # 开始追踪
ym-code debug trace start -f skills # 带过滤器
ym-code debug trace stop           # 停止追踪
ym-code debug trace status         # 查看状态
ym-code debug trace list           # 列出会话
ym-code debug trace show <id>      # 查看详情
ym-code debug trace stats <id>     # 查看统计
ym-code debug trace replay <id>    # 回放会话
ym-code debug trace export <id>    # 导出会话
```

### 性能分析命令

```bash
ym-code debug profile report <id>  # 生成报告
ym-code debug profile report <id> -f html -o report.html
ym-code debug profile list         # 列出结果
ym-code debug profile compare <id1> <id2>  # 比较结果
```

---

## 💡 最佳实践

### 1. 选择性追踪

```bash
# 只追踪关键模块
ym-code debug trace start --filter skills --filter mcp

# 避免追踪底层库
ym-code debug trace start --filter ymcode --exclude site-packages
```

### 2. 定期清理

```bash
# 清理旧的追踪数据
rm ~/.ym-code/debug/traces/*.json
rm ~/.ym-code/debug/profiles/*.json
```

### 3. 性能影响最小化

```python
# 生产环境禁用追踪
if os.environ.get('YM_CODE_DEBUG'):
    tracer.enable()

# 使用采样追踪
tracer.enable(sample_rate=0.1)  # 只追踪 10%
```

### 4. 报告分析

```python
# 生成可视化报告
profiler.export_report(profile_id, 'report.html')

# 在浏览器打开
import webbrowser
webbrowser.open('report.html')
```

---

## 🔮 高级功能

### 自定义事件

```python
from ymcode.debug.tracer import TraceEvent, get_tracer

tracer = get_tracer()

# 记录自定义事件
event = TraceEvent(
    event_type='log',
    target='custom_event',
    metadata={'key': 'value'}
)
tracer._record_event(event)
```

### 条件追踪

```python
from ymcode.debug import get_tracer

tracer = get_tracer()

# 只在特定条件下追踪
def should_trace(target):
    return 'expensive_operation' in target

tracer.enable(filters=['expensive_operation'])
```

### 性能基线

```python
# 建立性能基线
with profiler.profile('baseline'):
    # 正常操作

# 后续比较
with profiler.profile('current'):
    # 当前操作

# 比较
comparison = profiler.compare(['baseline', 'current'])
print(f"性能变化：{comparison['duration_diff']:+.3f}s")
```

---

## 📊 示例输出

### 追踪状态

```
╔══════════════════════════════════════════════╗
║  📊 追踪状态                                  ║
╠══════════════════════════════════════════════╣
║  ✅ 追踪进行中                                ║
║  Session: abc123...                          ║
║  Events: 156                                 ║
║  Duration: 2.34s                             ║
╚══════════════════════════════════════════════╝
```

### 性能报告

```
Performance Profile Report
==================================================
ID: my_operation
Duration: 1.234s
Total Calls: 456

Top Functions (by cumulative time):
--------------------------------------------------
1. process_data (100 calls, 0.890s cumulative, 8.90ms avg)
2. parse_input (50 calls, 0.234s cumulative, 4.68ms avg)
3. validate (200 calls, 0.110s cumulative, 0.55ms avg)
```

---

## 🎉 总结

**调试系统让你可以：**

- ✅ 追踪所有函数调用
- ✅ 分析性能瓶颈
- ✅ 回放错误场景
- ✅ 生成可视化报告
- ✅ 比较性能差异

**让调试不再是黑盒！** 🔧

---

_文档版本：1.0_  
_最后更新：2026-03-13_
