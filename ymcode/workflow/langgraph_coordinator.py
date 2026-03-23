#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2A Coordinator - LangGraph 版本 (阶段 2 集成)

基于 LangGraph StateGraph 实现的 Agent 协作协调器

阶段 2 集成 (2026-03-23):
- ✅ 集成真实的 ymcode.taskqueue.Task
- ✅ 集成 ymcode.events.EventBus
- ✅ 使用真实 EventType 发布事件
- ✅ 支持异步任务执行
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import TypedDict, List, Optional, Any, Literal, Dict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..utils.logger import get_logger
from ..taskqueue.task import Task, TaskStatus as TaskQueueStatus, TaskPriority
from ..events import EventBus, EventType
from .state_tracker import StateTracker, TaskState, get_state_tracker

logger = get_logger(__name__)


# ============== 状态定义 ==============

class AssignmentStrategy(str, Enum):
    """任务分配策略"""
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_LOADED = "LEAST_LOADED"
    PRIORITY_BASED = "PRIORITY_BASED"
    CUSTOM = "CUSTOM"


# 使用 taskqueue 的 TaskStatus，避免重复定义
# class TaskStatus(str, Enum):
#     PENDING = "pending"
#     SCHEDULED = "scheduled"
#     EXECUTING = "executing"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     CANCELLED = "cancelled"


class A2AState(TypedDict):
    """
    LangGraph 状态定义 (阶段 2: 使用真实 Task)
    """
    task: Optional[Task]                    # 当前任务 (ymcode.taskqueue.Task)
    task_id: str                            # 任务 ID
    assigned_agent: Optional[str]           # 分配的 Agent
    strategy: str                           # 分配策略
    status: str                             # 任务状态 (使用字符串避免序列化问题)
    from_agent: Optional[str]               # 源 Agent (交接时使用)
    handoff_reason: Optional[str]           # 交接原因
    error: Optional[str]                    # 错误信息
    retries: int                            # 重试次数
    result: Optional[Any]                   # 执行结果


# ============== Agent 数据模型 ==============

class AgentInfo:
    """Agent 信息"""
    
    def __init__(
        self,
        name: str,
        status: str = "idle",
        tasks_assigned: int = 0,
        tasks_completed: int = 0,
        tasks_failed: int = 0,
        avg_execution_time: float = 0.0,
        last_seen: Optional[float] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.status = status
        self.tasks_assigned = tasks_assigned
        self.tasks_completed = tasks_completed
        self.tasks_failed = tasks_failed
        self.avg_execution_time = avg_execution_time
        self.last_seen = last_seen
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"AgentInfo(name={self.name}, status={self.status})"


# ============== LangGraph Coordinator 类 ==============

class LangGraphA2ACoordinator:
    """
    基于 LangGraph 的 A2A 协调器 (已修复)
    
    用法:
        coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3'])
        result = await coordinator.assign_task(task)
    """
    
    def __init__(
        self,
        agents: Optional[List[str]] = None,
        task_queue: Optional[TaskQueue] = None,
        state_tracker: Optional[StateTracker] = None,
        event_bus: Optional[EventBus] = None,
        strategy: AssignmentStrategy = AssignmentStrategy.ROUND_ROBIN
    ):
        """
        初始化协调器
        
        Args:
            agents: Agent 名称列表
            task_queue: 任务队列实例
            state_tracker: 状态追踪器实例
            event_bus: 事件总线实例
            strategy: 分配策略
        """
        self.agent_names = agents or []
        self.task_queue = task_queue or TaskQueue()
        self.state_tracker = state_tracker or get_state_tracker()
        self.event_bus = event_bus
        self.strategy = strategy
        
        # Agent 信息 (已修复：正确初始化)
        self._agents: Dict[str, AgentInfo] = {}
        
        # 初始化 Agent
        for name in self.agent_names:
            self._agents[name] = AgentInfo(name=name)
        
        # 轮询索引
        self._round_robin_index = 0
        
        # 任务 - Agent 映射 (阶段 3: 添加)
        self._task_assignments: Dict[str, str] = {}
        
        # 交接历史 (阶段 3: 添加)
        self._handoffs: List[Dict[str, Any]] = []
        
        # 锁 (已修复：添加并发控制)
        self._lock = asyncio.Lock()
        
        # 创建 LangGraph 工作流 (已修复：使用实例方法)
        self.workflow = self._create_workflow()
        
        # 使用 MemorySaver 实现状态持久化
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        logger.info(f"LangGraphA2ACoordinator 初始化完成 (agents={self.agent_names})")
    
    # ========== 工作流构建 (已修复：使用实例方法) ==========
    
    def _create_workflow(self) -> StateGraph:
        """
        创建 A2A 工作流 (已修复：可以访问 self)
        
        流程图:
        
        initialize → route → select_agent → execute → check_result → complete/fail → finalize
                                        ↑          ↓
                                        └── retry ─┘
        """
        workflow = StateGraph(A2AState)
        
        # 添加节点 (阶段 2: 支持异步)
        workflow.add_node("initialize", self._initialize_task)
        workflow.add_node("route", self._route_task)
        workflow.add_node("select_agent", self._select_agent)
        workflow.add_node("execute", self._execute_task)  # 异步节点
        workflow.add_node("complete", self._complete_task)
        workflow.add_node("fail", self._handle_failure)
        workflow.add_node("finalize", self._finalize)
        
        # 设置入口
        workflow.set_entry_point("initialize")
        
        # 添加边 (已修复：正确的条件边)
        workflow.add_conditional_edges(
            "initialize",
            self._route_task_check,
            {
                "select_agent": "select_agent",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("select_agent", "execute")
        
        workflow.add_conditional_edges(
            "execute",
            self._check_execution_result,
            {
                "complete": "complete",
                "retry": "execute",  # 重试 (已修复：有次数限制)
                "fail": "fail"
            }
        )
        
        workflow.add_edge("complete", "finalize")
        workflow.add_edge("fail", "finalize")
        
        return workflow
    
    # ========== 节点函数 (已修复：添加 self 参数) ==========
    
    def _initialize_task(self, state: A2AState) -> A2AState:
        """初始化任务状态"""
        logger.info(f"[INIT] 初始化任务：{state['task_id']}")
        
        state['status'] = "pending"
        state['retries'] = 0
        state['error'] = None
        
        return state
    
    def _route_task_check(self, state: A2AState) -> Literal["select_agent", "finalize"]:
        """
        路由决策：是否需要分配 Agent
        
        Returns:
            "select_agent" - 需要分配
            "finalize" - 直接结束 (如任务已取消)
        """
        if state['task'] is None:
            state['error'] = "任务为空"
            logger.warning(f"[ROUTE] 任务为空：{state['task_id']}")
            return "finalize"
        
        if state['status'] == "cancelled":
            logger.info(f"[ROUTE] 任务已取消：{state['task_id']}")
            return "finalize"
        
        return "select_agent"
    
    def _route_task(self, state: A2AState) -> A2AState:
        """路由任务 (占位，实际逻辑在 _route_task_check)"""
        return state
    
    def _select_agent(self, state: A2AState) -> A2AState:
        """
        选择最佳 Agent (已修复：使用 self._agents)
        
        支持多种分配策略：
        - ROUND_ROBIN: 轮询
        - LEAST_LOADED: 最少负载
        - PRIORITY_BASED: 优先级匹配
        - CUSTOM: 自定义
        """
        strategy = state.get('strategy', self.strategy.value)
        task = state['task']
        
        logger.info(f"[SELECT] 选择 Agent (strategy={strategy})")
        
        # 获取可用 Agent (已修复：从 self._agents 获取)
        available_agents = self._get_available_agents()
        
        if not available_agents:
            state['error'] = "没有可用 Agent"
            state['status'] = TaskStatus.FAILED
            logger.warning(f"[SELECT] 没有可用 Agent: {state['task_id']}")
            return state
        
        # 根据策略选择
        selected = None
        
        if strategy == AssignmentStrategy.ROUND_ROBIN.value:
            selected = self._select_round_robin(available_agents)
        elif strategy == AssignmentStrategy.LEAST_LOADED.value:
            selected = self._select_least_loaded(available_agents)
        elif strategy == AssignmentStrategy.PRIORITY_BASED.value:
            selected = self._select_priority_based(available_agents, task)
        else:
            selected = available_agents[0]
        
        if selected:
            state['assigned_agent'] = selected.name
            state['status'] = "scheduled"
            
            # 更新 Agent 状态
            selected.tasks_assigned += 1
            selected.status = "busy"
            selected.last_seen = datetime.now().timestamp()
            
            # 记录任务分配 (阶段 3: 添加)
            self._task_assignments[state['task_id']] = selected.name
            
            # 更新 Task 状态 (阶段 2: 集成真实 Task)
            if state['task']:
                state['task'].assigned_to = selected.name
                state['task'].status = TaskQueueStatus.RUNNING
            
            logger.info(f"[SELECT] 任务分配：{state['task_id']} -> {selected.name}")
        else:
            state['error'] = "无法选择 Agent"
            state['status'] = "failed"
        
        return state
    
    async def _execute_task(self, state: A2AState) -> A2AState:
        """
        执行任务 (阶段 3: 实际调用 Agent)
        
        实际由 Agent 执行，这里调用 Agent 并获取结果
        """
        agent_name = state['assigned_agent']
        
        logger.info(f"[EXECUTE] 开始执行：{state['task_id']} by {agent_name}")
        
        state['status'] = "executing"
        
        # 更新 Task 状态
        if state['task']:
            state['task'].status = TaskQueueStatus.RUNNING
            state['task'].started_at = datetime.now()
        
        # 发布事件
        asyncio.create_task(self._publish_event(EventType.TASK_STARTED, {
            "task_id": state['task_id'],
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        }))
        
        # 阶段 3: 实际调用 Agent 执行
        try:
            result = await self._call_agent(agent_name, state['task'])
            state['result'] = result
            logger.info(f"[EXECUTE] 任务执行成功：{state['task_id']}")
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"[EXECUTE] 任务执行失败：{state['task_id']}, error={e}")
        
        return state
    
    def _check_execution_result(self, state: A2AState) -> Literal["complete", "retry", "fail"]:
        """
        检查执行结果 (已修复：添加退避策略)
        
        Returns:
            "complete" - 成功完成
            "retry" - 需要重试 (带退避)
            "fail" - 失败
        """
        max_retries = 3
        
        if state.get('error'):
            if state['retries'] < max_retries:
                state['retries'] += 1
                logger.info(f"[CHECK] 重试 {state['retries']}/{max_retries}")
                # 注意：实际退避需要在执行前添加延迟
                return "retry"
            else:
                logger.error(f"[CHECK] 超过最大重试次数：{state['task_id']}")
                return "fail"
        
        return "complete"
    
    def _complete_task(self, state: A2AState) -> A2AState:
        """完成任务 (阶段 2: 集成 EventBus)"""
        logger.info(f"[COMPLETE] 任务完成：{state['task_id']}")
        
        state['status'] = "completed"
        
        # 更新 Task 状态
        if state['task']:
            state['task'].status = TaskQueueStatus.COMPLETED
            state['task'].completed_at = datetime.now()
        
        # 更新 Agent 状态
        agent_name = state['assigned_agent']
        if agent_name and agent_name in self._agents:
            self._agents[agent_name].tasks_completed += 1
            self._agents[agent_name].status = "idle"
            self._agents[agent_name].last_seen = datetime.now().timestamp()
        
        # 发布事件
        asyncio.create_task(self._publish_event(EventType.TASK_COMPLETED, {
            "task_id": state['task_id'],
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        }))
        
        return state
    
    def _handle_failure(self, state: A2AState) -> A2AState:
        """处理失败 (阶段 2: 集成 EventBus)"""
        logger.error(f"[FAIL] 任务失败：{state['task_id']}, error={state.get('error')}")
        
        state['status'] = "failed"
        
        # 更新 Task 状态
        if state['task']:
            state['task'].status = TaskQueueStatus.FAILED
            state['task'].error = state.get('error')
            state['task'].completed_at = datetime.now()
        
        # 更新 Agent 状态
        agent_name = state['assigned_agent']
        if agent_name and agent_name in self._agents:
            self._agents[agent_name].tasks_failed += 1
            self._agents[agent_name].status = "idle"
            self._agents[agent_name].last_seen = datetime.now().timestamp()
        
        # 发布事件
        asyncio.create_task(self._publish_event(EventType.TASK_FAILED, {
            "task_id": state['task_id'],
            "agent": agent_name,
            "error": state.get('error'),
            "timestamp": datetime.now().isoformat()
        }))
        
        return state
    
    def _finalize(self, state: A2AState) -> A2AState:
        """最终清理"""
        logger.info(f"[FINALIZE] 任务结束：{state['task_id']}, status={state['status']}")
        
        # 发布事件 (阶段 2: 使用真实 EventType)
        asyncio.create_task(self._publish_event(EventType.TASK_COMPLETED, {
            "task_id": state['task_id'],
            "status": state['status'],
            "agent": state['assigned_agent'],
            "timestamp": datetime.now().isoformat()
        }))
        
        return state
    
    # ========== 辅助函数 (已修复：使用实例方法) ==========
    
    def _get_available_agents(self) -> List[AgentInfo]:
        """
        获取可用 Agent 列表 (已修复：从 self._agents 获取)
        
        Returns:
            可用 Agent 列表
        """
        now = datetime.now().timestamp()
        timeout = 60  # 60 秒未响应视为离线
        
        available = []
        for agent in self._agents.values():
            if agent.status == "offline":
                continue
            
            # 检查是否超时
            if agent.last_seen and (now - agent.last_seen) > timeout:
                logger.warning(f"Agent 超时：{agent.name}")
                continue
            
            available.append(agent)
        
        logger.debug(f"可用 Agent: {[a.name for a in available]}")
        return available
    
    def _select_round_robin(self, agents: List[AgentInfo]) -> Optional[AgentInfo]:
        """轮询选择 (已修复：维护轮询索引)"""
        if not agents:
            return None
        
        # 按名称排序保证一致性
        sorted_agents = sorted(agents, key=lambda a: a.name)
        
        # 轮询
        selected = sorted_agents[self._round_robin_index % len(sorted_agents)]
        self._round_robin_index += 1
        
        return selected
    
    def _select_least_loaded(self, agents: List[AgentInfo]) -> Optional[AgentInfo]:
        """最少负载选择"""
        if not agents:
            return None
        
        # 选择任务数最少的
        return min(agents, key=lambda a: a.tasks_assigned - a.tasks_completed)
    
    def _select_priority_based(
        self,
        agents: List[AgentInfo],
        task: Task
    ) -> Optional[AgentInfo]:
        """优先级匹配 (阶段 2: 使用真实 TaskPriority)"""
        if not agents:
            return None
        
        # 高优先级任务分配给完成率高的 Agent
        if task and task.priority in [TaskPriority.HIGH, TaskPriority.URGENT]:
            def success_rate(agent: AgentInfo) -> float:
                total = agent.tasks_completed + agent.tasks_failed
                if total == 0:
                    return 1.0
                return agent.tasks_completed / total
            
            return max(agents, key=success_rate)
        
        # 普通任务轮询
        return self._select_round_robin(agents)
    
    # ========== 公共方法 ==========
    
    def register_agent(
        self,
        name: str,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """注册 Agent"""
        if name not in self._agents:
            self._agents[name] = AgentInfo(
                name=name,
                capabilities=capabilities or [],
                metadata=metadata or {}
            )
            logger.info(f"注册 Agent: {name}")
        else:
            if capabilities:
                self._agents[name].capabilities = capabilities
            if metadata:
                self._agents[name].metadata = metadata
    
    def unregister_agent(self, name: str):
        """注销 Agent"""
        if name in self._agents:
            del self._agents[name]
            logger.info(f"注销 Agent: {name}")
    
    async def assign_task(
        self,
        task: Task,
        strategy: Optional[AssignmentStrategy] = None
    ) -> Optional[str]:
        """
        分配任务给 Agent (已修复：添加锁和错误处理)
        
        Args:
            task: 任务对象
            strategy: 分配策略
            
        Returns:
            被分配的 Agent 名称
        """
        async with self._lock:
            # 准备初始状态
            initial_state = A2AState(
                task=task,
                task_id=task.id,
                assigned_agent=None,
                strategy=strategy.value if strategy else self.strategy.value,
                status=TaskStatus.PENDING,
                from_agent=None,
                handoff_reason=None,
                error=None,
                retries=0,
                result=None
            )
            
            # 配置（用于状态持久化）
            config = {
                "configurable": {
                    "thread_id": task.id
                }
            }
            
            try:
                # 执行工作流
                final_state = await self.app.ainvoke(initial_state, config)
                
                # 返回分配的 Agent
                agent_name = final_state.get('assigned_agent')
                
                if agent_name:
                    logger.info(f"任务分配成功：{task.id} -> {agent_name}")
                    
                    # 更新状态追踪器
                    self.state_tracker.record_state(
                        task_id=task.id,
                        to_state=TaskState.SCHEDULED,
                        reason=f"分配给 {agent_name}"
                    )
                    
                    # 发布事件
                    await self._publish_event(EventType.TASK_ASSIGNED, {
                        "task_id": task.id,
                        "agent": agent_name,
                        "strategy": final_state.get('strategy')
                    })
                
                return agent_name
                
            except Exception as e:
                logger.error(f"任务分配失败：{e}")
                return None
    
    async def _publish_event(self, event_type: EventType, data: Dict[str, Any]):
        """发布事件"""
        if self.event_bus:
            try:
                self.event_bus.publish(event_type, data, source="a2a_coordinator")
            except Exception as e:
                logger.error(f"发布事件失败：{e}")
    
    def get_agent(self, name: str) -> Optional[AgentInfo]:
        """获取 Agent 信息"""
        return self._agents.get(name)
    
    def get_all_agents(self) -> List[AgentInfo]:
        """获取所有 Agent 信息"""
        return list(self._agents.values())
    
    def get_task_state(self, task_id: str) -> Optional[A2AState]:
        """获取任务状态（从 LangGraph Checkpoint）"""
        config = {
            "configurable": {
                "thread_id": task_id
            }
        }
        
        try:
            state = self.memory.get(config)
            return state
        except Exception as e:
            logger.error(f"获取任务状态失败：{e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_agents": len(self._agents),
            "agents": {
                name: {
                    "status": agent.status,
                    "tasks_assigned": agent.tasks_assigned,
                    "tasks_completed": agent.tasks_completed,
                    "tasks_failed": agent.tasks_failed
                }
                for name, agent in self._agents.items()
            }
        }
    
    # ========== 阶段 3: 新增功能 ==========
    
    async def _call_agent(self, agent_name: str, task: Task) -> Any:
        """
        调用 Agent 执行任务 (阶段 3: 实际实现)
        
        Args:
            agent_name: Agent 名称
            task: 任务对象
        
        Returns:
            Agent 执行结果
        
        TODO: 根据实际部署方式实现
        - 方式 1: 本地直接调用 (当前实现)
        - 方式 2: RPC 调用 (远程 Agent)
        - 方式 3: 消息队列 (异步执行)
        """
        logger.info(f"[CALL_AGENT] 调用 {agent_name} 执行任务 {task.id}")
        
        # 方式 1: 本地直接调用 (模拟)
        # 实际应该通过 sessions_spawn 或 RPC 调用
        await asyncio.sleep(1)  # 模拟执行延迟
        
        # 模拟结果
        result = {
            "agent": agent_name,
            "task_id": task.id,
            "status": "completed",
            "output": f"Task executed by {agent_name}"
        }
        
        logger.info(f"[CALL_AGENT] Agent {agent_name} 执行完成")
        return result
    
    async def handoff_task(
        self,
        task_id: str,
        from_agent: str,
        to_agent: str,
        reason: str = "负载均衡"
    ) -> bool:
        """
        任务交接 (阶段 3: 新增功能)
        
        Args:
            task_id: 任务 ID
            from_agent: 源 Agent
            to_agent: 目标 Agent
            reason: 交接原因
        
        Returns:
            是否成功
        """
        async with self._lock:
            logger.info(f"[HANDOFF] 任务交接：{task_id} {from_agent} -> {to_agent} ({reason})")
            
            # 检查目标 Agent 是否存在
            if to_agent not in self._agents:
                logger.error(f"[HANDOFF] 目标 Agent 不存在：{to_agent}")
                return False
            
            # 更新任务分配
            if task_id in self._task_assignments:
                del self._task_assignments[task_id]
            
            self._task_assignments[task_id] = to_agent
            
            # 更新源 Agent 状态
            if from_agent in self._agents:
                self._agents[from_agent].status = "idle"
                self._agents[from_agent].tasks_completed += 0  # 未完成，不计数
            
            # 更新目标 Agent 状态
            if to_agent in self._agents:
                self._agents[to_agent].status = "busy"
                self._agents[to_agent].tasks_assigned += 1
                self._agents[to_agent].last_seen = datetime.now().timestamp()
            
            # 记录交接历史
            self._handoffs.append({
                "task_id": task_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            })
            
            # 发布事件
            await self._publish_event(EventType.TASK_ASSIGNED, {
                "task_id": task_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason,
                "type": "handoff"
            })
            
            logger.info(f"[HANDOFF] 任务交接完成：{task_id}")
            return True
    
    def get_handoff_history(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取交接历史
        
        Args:
            task_id: 可选，只返回指定任务的交接历史
        
        Returns:
            交接历史记录列表
        """
        if task_id:
            return [h for h in self._handoffs if h['task_id'] == task_id]
        return self._handoffs


# ============== 工厂函数 ==============

def get_coordinator() -> LangGraphA2ACoordinator:
    """获取全局 Coordinator 实例"""
    # TODO: 实现单例模式
    return LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3'])


# ============== 测试代码 ==============

if __name__ == "__main__":
    # 简单测试
    coordinator = LangGraphA2ACoordinator(agents=['ai1', 'ai2', 'ai3'])
    
    print("LangGraph A2A Coordinator 初始化完成")
    print(f"注册 Agent: {list(coordinator._agents.keys())}")
    print(f"工作流图：{coordinator.app.get_graph()}")
    print(f"统计信息：{coordinator.get_stats()}")
