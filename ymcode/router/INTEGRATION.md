# ⚡ 快速集成指南

5 分钟将智能路由集成到 ymcode 主流程

---

## 前置条件

- ✅ Python 3.8+
- ✅ ymcode 已安装
- ✅ router 模块已创建

---

## Step 1: 导入模块 (30 秒)

在 `ymcode/cli.py` 顶部添加：

```python
from router import SmartRouter
```

---

## Step 2: 初始化路由器 (30 秒)

在 `YMCodeCLI.__init__()` 中添加：

```python
class YMCodeCLI:
    def __init__(self):
        # ... 现有代码 ...
        
        # 初始化智能路由器
        self.router = SmartRouter()
```

---

## Step 3: 添加路由逻辑 (2 分钟)

修改 `handle_task()` 或类似方法：

```python
async def handle_task(self, task):
    """处理用户任务"""
    
    # ========== 新增：路由决策 ==========
    route_result = self.router.route(task)
    
    # 显示路由信息
    console.print(f"\n[bold blue]🎯 智能路由[/]")
    console.print(f"  选定：{route_result.agent_name} ({route_result.selected_agent})")
    console.print(f"  置信度：{route_result.confidence:.0%}")
    console.print(f"  预计响应：{route_result.response_time_estimate}s")
    console.print(f"  匹配关键词：{', '.join(route_result.matched_keywords) or '无'}\n")
    # ===================================
    
    # ========== 修改：调用选定的 Agent ==========
    start_time = time.time()
    
    # 原来：调用所有 Agent 或固定 Agent
    # response = await self.agent.run(task)
    
    # 现在：调用路由选定的 Agent
    response = await self.call_agent(route_result.selected_agent, task)
    
    response_time = time.time() - start_time
    # ===================================
    
    # ========== 新增：记录结果 ==========
    success = response.get("success", False)
    self.router.record_result(
        route_result.selected_agent,
        success,
        response_time
    )
    # ===================================
    
    return response
```

---

## Step 4: 添加 API 端点 (可选，2 分钟)

在 `web/dashboard_api.py` 中添加：

```python
from ..router import SmartRouter

@app.get("/api/agents/capabilities")
async def get_agent_capabilities():
    """获取 Agent 能力列表"""
    router = SmartRouter()
    return {"agents": router.get_all_agents()}

@app.post("/api/router/route")
async def route_task(request: TaskRouteRequest):
    """路由任务到最优 Agent"""
    router = SmartRouter()
    result = router.route(request.task)
    return {
        "agent_id": result.selected_agent,
        "agent_name": result.agent_name,
        "confidence": result.confidence,
        "estimated_time": result.response_time_estimate
    }
```

---

## Step 5: 测试验证 (1 分钟)

```bash
# 运行测试
cd ymcode
python router/test_router.py

# 运行演示
python router/demo.py

# 测试集成
python cli.py
```

---

## 验证清单

- [ ] 路由决策显示正常
- [ ] Agent 调用正确
- [ ] 统计数据保存成功
- [ ] Hub API 返回正确数据

---

## 故障排查

### 问题：导入失败
```
ModuleNotFoundError: No module named 'router'
```
**解决：** 确保在 ymcode 目录下运行，或添加路径：
```python
import sys
sys.path.insert(0, str(Path(__file__).parent))
```

### 问题：统计数据未保存
**解决：** 检查 `data/router_stats.json` 目录是否存在，权限是否正确

### 问题：路由结果总是默认
**解决：** 检查 `routing_rules.py` 中的关键词映射，添加更多关键词

---

## 性能优化建议

1. **缓存路由器实例** - 不要每次请求都创建新实例
2. **异步保存统计** - 使用后台线程保存，避免阻塞
3. **定期清理统计** - 保留最近 30 天数据

---

## 下一步

集成完成后，继续实现：

1. **Hub 可视化** - 展示 Agent 能力
2. **技能按需加载** - 根据任务动态加载技能
3. **Rich Blocks** - 结构化回复

---

**预计总时间：** 5-10 分钟  
**难度：** ⭐⭐ (简单)
