# 🧠 YM-CODE 知识库系统指南

> 让 Agent 拥有长期记忆和结构化知识

---

## 🎯 知识库系统功能

### 核心组件

1. **Knowledge Base** - 知识存储
   - 结构化知识条目
   - 分类体系
   - 标签系统
   - 知识关联

2. **Document Indexer** - 文档索引器
   - 自动索引文档
   - 代码结构分析
   - 关键词提取
   - 自动分类

3. **Knowledge Retriever** - 知识检索器
   - 语义搜索
   - 关键词匹配
   - 关联推荐
   - 上下文感知

---

## 🚀 快速开始

### 1. 索引文档

```bash
# 索引单个文件
ym-code knowledge index file ./docs/README.md

# 索引整个目录
ym-code knowledge index dir ./docs --pattern "*.md"

# 索引代码
ym-code knowledge index dir ./src --pattern "*.py"
```

### 2. 搜索知识

```bash
# 基本搜索
ym-code knowledge search "异步编程"

# 带分类搜索
ym-code knowledge search "best practices" --category code/python

# 带标签搜索
ym-code knowledge search "error handling" --tag python --tag async
```

### 3. 查看统计

```bash
# 查看分类树
ym-code knowledge category tree

# 查看统计信息
ym-code knowledge category stats
```

---

## 📚 知识条目

### 知识类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **concept** | 概念 | "什么是异步编程" |
| **procedure** | 流程 | "如何部署应用" |
| **fact** | 事实 | "Python 3.10 新特性" |
| **example** | 示例 | "FastAPI 示例代码" |
| **best_practice** | 最佳实践 | "RESTful API 设计规范" |
| **troubleshooting** | 故障排除 | "常见连接错误解决" |
| **code_snippet** | 代码片段 | "装饰器模板" |
| **documentation** | 文档 | "API 参考文档" |

### 知识条目结构

```python
{
    "id": "kb_20260313124500",
    "title": "Python 异步编程指南",
    "content": "...",
    "summary": "Python 异步编程的完整指南",
    "type": "best_practice",
    "category": "code/python",
    "tags": ["python", "async", "asyncio"],
    "related_to": ["kb_20260313124501"],
    "confidence": 0.95,
    "usage_count": 42
}
```

---

## 🔍 搜索功能

### 基本搜索

```bash
# 关键词搜索
ym-code knowledge search "async await"

# 短语搜索
ym-code knowledge search "error handling best practices"
```

### 高级搜索

```bash
# 分类过滤
ym-code knowledge search "decorator" --category code/python

# 标签过滤
ym-code knowledge search "testing" --tag pytest --tag unittest

# 类型过滤
ym-code knowledge search "example" --type code_snippet
```

### 搜索结果

```
找到 5 个相关知识：

╔══════════════════════════════════════════════╗
║ 📚 结果 1                                     ║
╠══════════════════════════════════════════════╣
║ 1. Python 异步编程指南                        ║
║                                              ║
║ 分类：code/python                            ║
║ 标签：python, async, asyncio                 ║
║ 相关性：0.95                                 ║
║                                              ║
║ Python 异步编程的完整指南，涵盖 async/await   ║
║ 语法、asyncio 库使用、常见模式...             ║
╚══════════════════════════════════════════════╝
```

---

## 📁 索引功能

### 索引文档

```bash
# 索引 Markdown 文档
ym-code knowledge index dir ./docs --pattern "*.md"

# 排除特定目录
ym-code knowledge index dir ./src \
  --exclude node_modules \
  --exclude __pycache__
```

### 索引代码

```bash
# 索引 Python 代码
ym-code knowledge index dir ./src --pattern "*.py"

# 索引 TypeScript 代码
ym-code knowledge index dir ./src --pattern "*.ts"
```

### 索引配置

```bash
# 索引 JSON 配置
ym-code knowledge index dir ./config --pattern "*.json"

# 索引 YAML 配置
ym-code knowledge index dir ./config --pattern "*.yaml"
```

---

## 🌐 知识图谱

### 知识关联

```bash
# 添加知识关联
ym-code knowledge entry add-relation kb_001 kb_002

# 查看相关知识
ym-code knowledge related kb_001
```

### 分类体系

```bash
# 查看分类树
ym-code knowledge category tree

# 输出示例：
# 📁 知识分类
# ├── 📂 code
# │   ├── 📄 python
# │   └── 📄 javascript
# └── 📂 docs
#     └── 📄 api
```

---

## 💡 使用场景

### 场景 1：项目文档管理

```bash
# 1. 索引项目文档
ym-code knowledge index dir ./docs

# 2. 搜索特定主题
ym-code knowledge search "API 设计"

# 3. 查看热门文档
ym-code knowledge popular --category docs
```

### 场景 2：代码知识库

```bash
# 1. 索引代码库
ym-code knowledge index dir ./src --pattern "*.py"

# 2. 查找代码示例
ym-code knowledge search "decorator example" --type code_snippet

# 3. 查看最近更新的代码
ym-code knowledge recent --limit 10
```

### 场景 3：故障排除

```bash
# 1. 搜索错误信息
ym-code knowledge search "connection timeout"

# 2. 查看相关解决方案
ym-code knowledge related kb_error_001

# 3. 查看热门故障排除
ym-code knowledge popular --category troubleshooting
```

### 场景 4：学习新知识

```bash
# 1. 搜索入门指南
ym-code knowledge search "getting started"

# 2. 查看相关知识链
ym-code knowledge related kb_intro_001

# 3. 按难度递进学习
ym-code knowledge search "advanced" --category tutorials
```

---

## 📊 CLI 命令速查

### 索引命令

```bash
ym-code knowledge index file <file>     # 索引文件
ym-code knowledge index dir <dir>       # 索引目录
```

### 搜索命令

```bash
ym-code knowledge search <query>        # 搜索知识
ym-code knowledge related <id>          # 相关知识
ym-code knowledge popular               # 热门知识
ym-code knowledge recent                # 最近知识
```

### 管理命令

```bash
ym-code knowledge entry list            # 列出条目
ym-code knowledge entry show <id>       # 显示详情
ym-code knowledge entry add-relation    # 添加关联
ym-code knowledge category tree         # 分类树
ym-code knowledge category stats        # 统计信息
```

---

## 🔮 高级功能

### 语义搜索

```python
from ymcode.knowledge import KnowledgeRetriever, KnowledgeGraph

graph = KnowledgeGraph()
retriever = KnowledgeRetriever(graph)

# 语义搜索（自动理解查询意图）
results = retriever.search("如何处理异步错误")

# 结果会包含：
# - async error handling
# - try/except in async
# - async exception best practices
```

### 关联推荐

```python
# 获取相关知识
related = retriever.get_related_knowledge('kb_001')

# 基于标签推荐
# 基于引用关系推荐
```

### 自动索引

```python
from ymcode.knowledge import DocumentIndexer

indexer = DocumentIndexer()

# 索引整个项目
count = indexer.index_directory(
    Path('./project'),
    pattern='*.{py,md,json}',
    exclude=['node_modules', '__pycache__']
)

print(f"索引了 {count} 个文件")
```

---

## 📈 统计信息

### 查看统计

```bash
ym-code knowledge category stats
```

**输出示例：**

```
╔══════════════════════════════════════════════╗
║ 📊 知识库统计                                 ║
╠══════════════════════════════════════════════╣
║ 总条目数：156                                ║
║ 总分类数：12                                 ║
║ 总关联数：89                                 ║
║                                              ║
║ 按类型分布：                                 ║
║   code_snippet: 45                           ║
║   documentation: 38                          ║
║   best_practice: 28                          ║
║   troubleshooting: 25                        ║
║   concept: 20                                ║
║                                              ║
║ Top 标签：                                   ║
║   #python: 42                                ║
║   #async: 28                                 ║
║   #api: 25                                   ║
║   #testing: 18                               ║
║   #security: 15                              ║
╚══════════════════════════════════════════════╝
```

---

## 🎯 最佳实践

### 1. 定期索引

```bash
# 添加到 cron 定时任务
0 2 * * * ym-code knowledge index dir ./src --pattern "*.py"
```

### 2. 组织分类

```bash
# 创建清晰的分类体系
# code/
#   ├── python/
#   ├── javascript/
#   └── typescript/
# docs/
#   ├── api/
#   ├── tutorials/
#   └── troubleshooting/
```

### 3. 使用标签

```bash
# 为知识添加多个标签
# 便于多维度搜索
entry.add_tag("python")
entry.add_tag("async")
entry.add_tag("best-practice")
```

### 4. 建立关联

```bash
# 关联相关知识
ym-code knowledge entry add-relation kb_001 kb_002

# 形成知识网络
```

---

## 🎉 总结

**知识库系统让你可以：**

- ✅ 索引项目文档和代码
- ✅ 智能搜索相关知识
- ✅ 建立知识关联网络
- ✅ 推荐相关内容
- ✅ 统计使用情况

**让知识不再是孤岛！** 🧠

---

_文档版本：1.0_  
_最后更新：2026-03-13_
