# YM-CODE Skills 市场和网络浏览

**下载 Skills + 浏览网络！** 🚀

---

## ✅ 已实现功能

### 1. Skills 市场

| 功能 | 状态 | 说明 |
|------|------|------|
| **浏览 Skills** | ✅ | 列出所有可用 Skills |
| **搜索 Skills** | ✅ | 关键词搜索 |
| **下载 Skills** | ✅ | 下载到本地 |
| **安装 Skills** | ✅ | 自动验证 |
| **查看信息** | ✅ | Skill 详情 |

---

### 2. 网络浏览

| 功能 | 状态 | 说明 |
|------|------|------|
| **访问网页** | ✅ | 提取内容 |
| **网络搜索** | ✅ | Google/Bing/Baidu |
| **网页截图** | ⏳ 计划中 | 需要浏览器 |

---

## 🚀 使用方式

### 方式 1：Python API

```python
from ymcode.skills import SkillMarketplace, WebBrowserSkill
import asyncio

async def main():
    # Skills 市场
    marketplace = SkillMarketplace()
    
    # 浏览所有 Skills
    skills = await marketplace.list_skills()
    print(f"可用 Skills: {skills['total']}")
    
    # 搜索 Skills
    results = await marketplace.search_skills("github")
    print(f"找到 {results['total']} 个 GitHub 相关 Skills")
    
    # 下载 Skill
    result = await marketplace.download_skill("github-tools")
    print(f"下载：{result['message']}")
    
    # 网络浏览
    browser = WebBrowserSkill()
    
    # 访问网页
    page = await browser.fetch_url("https://github.com")
    print(f"标题：{page['title']}")
    
    # 网络搜索
    search = await browser.search_web("Python 编程", engine="google")
    print(f"搜索结果：{len(search['results'])} 条")

asyncio.run(main())
```

---

### 方式 2：YM-CODE CLI

```bash
python -m ymcode

# 浏览 Skills
> 列出可用的 Skills

# 搜索 Skills
> 搜索 GitHub 相关的 Skills

# 下载 Skill
> 下载 github-tools Skill

# 访问网页
> 访问 https://github.com

# 网络搜索
> 搜索 Python 编程
```

---

## 📋 Skills 市场功能

### 1. 浏览 Skills

```python
marketplace = SkillMarketplace()

# 列出所有
skills = await marketplace.list_skills()

# 按分类
skills = await marketplace.list_skills(category="development")
```

**输出示例：**
```json
{
  "success": true,
  "skills": [
    {
      "name": "github-tools",
      "description": "GitHub 操作工具",
      "category": "development",
      "downloads": 1234,
      "rating": 4.8
    },
    {
      "name": "notion-integration",
      "description": "Notion 集成",
      "category": "productivity",
      "downloads": 567,
      "rating": 4.5
    }
  ],
  "total": 50
}
```

---

### 2. 搜索 Skills

```python
# 关键词搜索
results = await marketplace.search_skills("github")

# 多关键词
results = await marketplace.search_skills("git version control")
```

---

### 3. 下载 Skill

```python
# 下载
result = await marketplace.download_skill("github-tools")

if result["success"]:
    print(f"下载成功：{result['path']}")
else:
    print(f"下载失败：{result['error']}")
```

**下载位置：**
```
~/.ymcode/skills/custom/
├── github-tools.py
└── github-tools.meta.json
```

---

### 4. 安装 Skill

```python
# 下载 + 验证
result = await marketplace.install_skill("github-tools")

if result["success"]:
    print("安装成功！重启 YM-CODE 后生效")
else:
    print(f"安装失败：{result['error']}")
```

---

### 5. 查看 Skill 信息

```python
# 获取详情
info = await marketplace.get_skill_info("github-tools")

print(f"名称：{info['skill']['name']}")
print(f"描述：{info['skill']['description']}")
print(f"版本：{info['skill']['version']}")
print(f"作者：{info['skill']['author']}")
```

---

## 🌐 网络浏览功能

### 1. 访问网页

```python
browser = WebBrowserSkill()

# 获取网页内容
page = await browser.fetch_url("https://github.com")

print(f"标题：{page['title']}")
print(f"内容：{page['content'][:500]}")
print(f"长度：{page['length']} 字符")
```

**输出示例：**
```json
{
  "success": true,
  "url": "https://github.com",
  "title": "GitHub: Let's build from here",
  "content": "GitHub is where over 100 million developers...",
  "length": 50000
}
```

---

### 2. 网络搜索

```python
browser = WebBrowserSkill()

# Google 搜索
results = await browser.search_web("Python 编程", engine="google")

# Bing 搜索
results = await browser.search_web("AI 教程", engine="bing")

# 百度搜索
results = await browser.search_web("机器学习", engine="baidu")
```

**输出示例：**
```json
{
  "success": true,
  "query": "Python 编程",
  "engine": "google",
  "search_url": "https://www.google.com/search?q=Python 编程",
  "results": [
    {"title": "Python 入门教程"},
    {"title": "Python 官方文档"},
    ...
  ]
}
```

---

### 3. 网页截图（计划中）

```python
# TODO: 需要集成 Playwright
result = await browser.take_screenshot("https://github.com")
```

---

## 📦 本地 Skills 管理

### 查看已安装

```python
marketplace = SkillMarketplace()

# 列出本地 Skills
skills = marketplace.list_installed_skills()

for skill in skills:
    print(f"- {skill['name']}: {skill['path']}")
```

---

### 删除 Skill

```python
from pathlib import Path

skills_dir = Path.home() / ".ymcode" / "skills" / "custom"

# 删除文件
(skills_dir / "github-tools.py").unlink()
(skills_dir / "github-tools.meta.json").unlink()
```

---

## 🔧 配置

### 自定义市场 URL

```python
marketplace = SkillMarketplace()
marketplace.marketplace_url = "https://your-marketplace.com"
```

### 超时设置

```python
marketplace.timeout = 60  # 60 秒
browser.timeout = 30  # 30 秒
```

---

## 📋 使用示例

### 示例 1：搜索并安装 GitHub Skill

```python
from ymcode.skills import SkillMarketplace
import asyncio

async def main():
    marketplace = SkillMarketplace()
    
    # 搜索
    results = await marketplace.search_skills("github")
    print(f"找到 {results['total']} 个 Skills")
    
    # 选择第一个
    if results['skills']:
        skill = results['skills'][0]
        print(f"安装：{skill['name']}")
        
        # 安装
        result = await marketplace.install_skill(skill['name'])
        print(result['message'])

asyncio.run(main())
```

---

### 示例 2：浏览新闻网站

```python
from ymcode.skills import WebBrowserSkill
import asyncio

async def main():
    browser = WebBrowserSkill()
    
    # 访问新闻网站
    page = await browser.fetch_url("https://news.ycombinator.com")
    
    print(f"标题：{page['title']}")
    print(f"内容预览：{page['content'][:300]}...")

asyncio.run(main())
```

---

### 示例 3：研究技术文档

```python
from ymcode.skills import WebBrowserSkill
import asyncio

async def main():
    browser = WebBrowserSkill()
    
    # 访问 Python 文档
    urls = [
        "https://docs.python.org/3/tutorial/index.html",
        "https://requests.readthedocs.io/",
    ]
    
    for url in urls:
        page = await browser.fetch_url(url)
        print(f"\n{page['title']}")
        print(f"长度：{page['length']} 字符")

asyncio.run(main())
```

---

## 🎯 实际应用场景

### 场景 1：查找第三方库

```bash
# 搜索 PyPI
> 访问 https://pypi.org/search/?q=requests

# 查看文档
> 访问 https://requests.readthedocs.io/
```

---

### 场景 2：研究问题解决方案

```bash
# Stack Overflow 搜索
> 搜索 "Python HTTP request timeout"

# 访问相关页面
> 访问 https://stackoverflow.com/questions/xxx
```

---

### 场景 3：学习新技术

```bash
# 搜索教程
> 搜索 "FastAPI 教程"

# 访问官方文档
> 访问 https://fastapi.tiangolo.com/
```

---

## ⚠️ 注意事项

### 1. 网络访问

- ✅ 需要网络连接
- ⚠️ 注意超时设置
- ⚠️ 某些网站可能禁止爬虫

---

### 2. 安全性

- ✅ 验证下载的 Skills
- ✅ 检查代码来源
- ⚠️ 不要运行不可信代码

---

### 3. 性能

- ⚠️ 网络请求可能较慢
- ⚠️ 大页面可能超时
- ✅ 建议设置合理超时

---

## 🔮 计划功能

### Skills 市场

- [ ] 评分系统
- [ ] 评论功能
- [ ] 自动更新
- [ ] 依赖管理

### 网络浏览

- [ ] 网页截图
- [ ] PDF 导出
- [ ] 深度爬取
- [ ] 内容过滤

---

## 📝 总结

### 已实现

- ✅ Skills 浏览
- ✅ Skills 搜索
- ✅ Skills 下载
- ✅ Skills 安装
- ✅ 网页访问
- ✅ 网络搜索

### 可以使用

```python
# Skills 市场
from ymcode.skills import SkillMarketplace

# 网络浏览
from ymcode.skills import WebBrowserSkill
```

---

**开始使用 Skills 市场和网络浏览吧！** 🚀
