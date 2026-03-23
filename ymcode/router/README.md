# 🎯 智能路由系统

基于任务内容、Agent 能力和历史准确率，自动选择最优 Agent。

## 快速开始

```python
from router import SmartRouter

# 创建路由器实例
router = SmartRouter()

# 路由任务
result = router.route("帮我设计一个微服务架构")

print(f"选定 Agent: {result.agent_name} ({result.selected_agent})")
print(f"置信度：{result.confidence:.2f}")
print(f"预计响应时间：{result.response_time_estimate}s")
print(f"匹配关键词：{result.matched_keywords}")
```

## 核心功能

### 1. 关键词匹配
- 自动提取中英文关键词
- 支持技术术语识别（如 ci/cd、rest-api）
- 高优先级规则匹配

### 2. 智能评分
- 基础匹配分
- 历史准确率加权
- 关键词多样性奖励

### 3. 动态学习
- 记录每次路由结果
- 自动更新 Agent 准确率
- 持续优化路由决策

## Agent 能力矩阵

| Agent | 角色 | 专长 | 目标响应 | 模型 |
|-------|------|------|----------|------|
| ai1 | 架构师 | 系统架构、技术选型 | 5s | qwen3.5-plus |
| ai2 | 后端开发 | API、数据库 | 3s | qwen3-coder-plus |
| ai3 | 前端开发 | UI、交互 | 3s | qwen3-coder-next |
| ai4 | 全栈开发 | 集成、快速原型 | 3s | glm-5 |
| ai5 | 测试工程师 | 代码审查、测试 | 4s | kimi-k2.5 |
| ai6 | 技术顾问 | 技术咨询、最佳实践 | 5s | qwen3-max |
| ai7 | 产品顾问 | 产品设计、用户体验 | 4s | MiniMax-M2.5 |

## 路由规则示例

```python
# 高优先级规则（权重 3）
"审查代码": ["ai5"],
"架构设计": ["ai1"],
"产品设计": ["ai7"],

# 普通规则（权重 1）
"架构": ["ai1", "ai6"],
"api": ["ai2", "ai4"],
"前端": ["ai3", "ai4"],
"测试": ["ai5"],
```

## 性能指标

- **路由准确率**: >90%（基于测试集）
- **响应时间**: <10ms（路由决策）
- **关键词覆盖**: 50+ 技术术语

## 集成到 ymcode

```python
# 在 ymcode/cli.py 或相关文件中
from router import SmartRouter

router = SmartRouter()

# 在任务处理前添加路由
async def handle_task(self, task):
    # 1. 路由决策
    route_result = router.route(task)
    
    # 2. 显示路由信息
    console.print(f"[blue]🎯 路由到：{route_result.agent_name}[/]")
    console.print(f"   置信度：{route_result.confidence:.0%}")
    console.print(f"   预计响应：{route_result.response_time_estimate}s")
    
    # 3. 调用选定的 Agent
    start_time = time.time()
    response = await self.call_agent(route_result.selected_agent, task)
    response_time = time.time() - start_time
    
    # 4. 记录结果
    success = response.get("success", False)
    router.record_result(route_result.selected_agent, success, response_time)
```

## 测试

```bash
cd ymcode
python router/test_router.py
```

## 配置文件

- `routing_rules.py` - 路由规则和关键词映射
- `router_stats.json` - 历史统计数据（自动生成）

## 优化建议

1. **定期更新关键词库** - 根据实际使用情况添加新术语
2. **监控准确率** - 每周检查 router_stats.json
3. **调整权重** - 根据反馈优化高优先级规则
4. **添加上下文感知** - 考虑对话历史进行路由

## 故障排查

### 问题：总是路由到默认 Agent
**原因：** 关键词库未覆盖
**解决：** 在 routing_rules.py 中添加新关键词

### 问题：置信度过低
**原因：** 匹配关键词太少
**解决：** 检查任务描述是否清晰，或添加更多同义词

### 问题：响应时间慢
**原因：** 统计数据文件过大
**解决：** 定期清理 router_stats.json 或添加归档机制
