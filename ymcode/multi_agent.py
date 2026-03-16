#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 Agent 协作系统

实现真正的多智能体分工与协作
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentRole(Enum):
    """Agent 角色定义"""
    ORCHESTRATOR = "orchestrator"  # 协调者 - 任务拆解和分配
    CODER = "coder"  # 代码生成 Agent
    TESTER = "tester"  # 测试 Agent
    REVIEWER = "reviewer"  # 代码审查 Agent
    DEBUGGER = "debugger"  # 调试 Agent
    DOCUMENTER = "documenter"  # 文档生成 Agent


class TaskType(Enum):
    """任务类型"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    COMPLEX = "complex"  # 复杂任务（需要多 Agent 协作）


class AgentMessage:
    """Agent 间通信消息"""
    
    def __init__(self, 
                 from_agent: str,
                 to_agent: str,
                 message_type: str,
                 content: Any,
                 metadata: Dict = None):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type  # request, response, feedback
        self.content = content
        self.metadata = metadata or {}


class MultiAgentSystem:
    """多 Agent 协作系统"""
    
    def __init__(self):
        """初始化多 Agent 系统"""
        self.agents: Dict[AgentRole, Any] = {}
        self.message_queue: List[AgentMessage] = []
        self.task_history: List[Dict] = []
        self._initialized = False
    
    def register_agent(self, role: AgentRole, agent: Any) -> bool:
        """
        注册 Agent
        
        参数:
            role: Agent 角色
            agent: Agent 实例
        
        返回:
            是否成功
        """
        if role in self.agents:
            logger.warning(f"Agent 角色已存在：{role}")
            return False
        
        self.agents[role] = agent
        logger.info(f"注册 Agent：{role.value}")
        return True
    
    def _decompose_task(self, task: str, context: Dict = None) -> List[Dict]:
        """
        任务拆解 - 将复杂任务拆解为子任务
        
        参数:
            task: 原始任务
            context: 上下文信息
        
        返回:
            子任务列表
        """
        # TODO: 使用 LLM 智能拆解任务
        # 当前使用规则-based 拆解
        
        task_lower = task.lower()
        subtasks = []
        
        # 检测任务类型
        needs_code = any(kw in task_lower for kw in ['代码', '实现', '开发', '写', 'create', 'develop'])
        needs_test = any(kw in task_lower for kw in ['测试', 'unit test', 'test case'])
        needs_review = any(kw in task_lower for kw in ['审查', 'review', '审计', 'audit'])
        needs_doc = any(kw in task_lower for kw in ['文档', 'document', '说明', 'readme'])
        
        # 拆解为子任务
        if needs_code:
            subtasks.append({
                'type': TaskType.CODE_GENERATION.value,
                'role': AgentRole.CODER.value,
                'description': f'生成代码：{task}',
                'dependencies': []
            })
        
        if needs_test:
            subtasks.append({
                'type': TaskType.TESTING.value,
                'role': AgentRole.TESTER.value,
                'description': f'编写测试：{task}',
                'dependencies': ['code_generation'] if needs_code else []
            })
        
        if needs_review:
            subtasks.append({
                'type': TaskType.CODE_REVIEW.value,
                'role': AgentRole.REVIEWER.value,
                'description': f'代码审查：{task}',
                'dependencies': ['code_generation']
            })
        
        if needs_doc:
            subtasks.append({
                'type': TaskType.DOCUMENTATION.value,
                'role': AgentRole.DOCUMENTER.value,
                'description': f'生成文档：{task}',
                'dependencies': ['code_generation']
            })
        
        # 如果没有检测到特定需求，默认只需要代码生成
        if not subtasks:
            subtasks.append({
                'type': TaskType.CODE_GENERATION.value,
                'role': AgentRole.CODER.value,
                'description': task,
                'dependencies': []
            })
        
        logger.info(f"任务拆解完成：{len(subtasks)} 个子任务")
        return subtasks
    
    async def _execute_subtask(self, subtask: Dict, context: Dict) -> Dict:
        """
        执行子任务
        
        参数:
            subtask: 子任务定义
            context: 上下文信息
        
        返回:
            执行结果
        """
        role_str = subtask.get('role', AgentRole.CODER.value)
        
        try:
            role = AgentRole(role_str)
        except ValueError:
            role = AgentRole.CODER
        
        if role not in self.agents:
            logger.error(f"Agent 未注册：{role}")
            return {
                'success': False,
                'error': f'Agent {role.value} 未注册',
                'result': None
            }
        
        agent = self.agents[role]
        description = subtask.get('description', '')
        
        logger.info(f"执行子任务：{role.value} - {description[:50]}...")
        
        # 调用 Agent 执行
        try:
            if hasattr(agent, 'execute'):
                result = await agent.execute(description, context)
            elif hasattr(agent, 'process'):
                result = await agent.process(description, context)
            else:
                result = {'error': 'Agent 没有 execute 或 process 方法'}
            
            return {
                'success': True,
                'role': role.value,
                'result': result
            }
        except Exception as e:
            logger.error(f"Agent 执行失败：{e}")
            return {
                'success': False,
                'error': str(e),
                'role': role.value
            }
    
    async def execute_task(self, task: str, context: Dict = None) -> Dict:
        """
        执行任务 - 支持单 Agent 和多 Agent 模式
        
        参数:
            task: 任务描述
            context: 上下文信息
        
        返回:
            执行结果
        """
        logger.info(f"接收任务：{task[:100]}...")
        
        # 1. 判断是否需要多 Agent 协作
        # 检测复杂任务关键词
        complex_keywords = ['完整', '整个', '全部', '开发一个', '从零开始', 'complete', 'full', 'develop a']
        is_complex = any(kw in task.lower() for kw in complex_keywords)
        
        # 检测是否包含多个需求
        task_lower = task.lower()
        needs = []
        if any(kw in task_lower for kw in ['代码', '实现', '开发']): needs.append('code')
        if any(kw in task_lower for kw in ['测试', 'unit']): needs.append('test')
        if any(kw in task_lower for kw in ['审查', 'review']): needs.append('review')
        if any(kw in task_lower for kw in ['文档', '说明']): needs.append('doc')
        
        # 如果包含 2 个以上需求，使用多 Agent 协作
        use_multi_agent = is_complex or len(needs) >= 2
        
        if use_multi_agent and len(self.agents) > 1:
            logger.info(f"使用多 Agent 协作模式，需求：{needs}")
            return await self._execute_multi_agent(task, context)
        else:
            logger.info("使用单 Agent 模式")
            return await self._execute_single_agent(task, context)
    
    async def _execute_single_agent(self, task: str, context: Dict = None) -> Dict:
        """单 Agent 执行"""
        # 使用 Orchestrator 或默认使用 Coder
        if AgentRole.ORCHESTRATOR in self.agents:
            agent = self.agents[AgentRole.ORCHESTRATOR]
        elif AgentRole.CODER in self.agents:
            agent = self.agents[AgentRole.CODER]
        else:
            # 使用第一个注册的 Agent
            agent = list(self.agents.values())[0] if self.agents else None
        
        if not agent:
            return {'success': False, 'error': '没有可用的 Agent'}
        
        try:
            if hasattr(agent, 'execute'):
                result = await agent.execute(task, context or {})
            elif hasattr(agent, 'process'):
                result = await agent.process(task, context or {})
            else:
                result = {'error': 'Agent 没有 execute 或 process 方法'}
            
            return {'success': True, 'result': result, 'mode': 'single_agent'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'mode': 'single_agent'}
    
    async def _execute_multi_agent(self, task: str, context: Dict = None) -> Dict:
        """多 Agent 协作执行"""
        # 1. 任务拆解
        subtasks = self._decompose_task(task, context)
        logger.info(f"任务拆解为 {len(subtasks)} 个子任务")
        
        # 2. 构建执行计划（拓扑排序）
        execution_plan = self._topological_sort(subtasks)
        
        # 3. 执行子任务
        results = {}
        context = context or {}
        
        for subtask in execution_plan:
            # 等待依赖完成
            for dep in subtask.get('dependencies', []):
                if dep not in results:
                    logger.error(f"依赖未完成：{dep}")
                    continue
            
            # 添加依赖结果到上下文
            for dep in subtask.get('dependencies', []):
                if dep in results:
                    context[f'{dep}_result'] = results[dep]
            
            # 执行子任务
            result = await self._execute_subtask(subtask, context)
            results[subtask['type']] = result
            
            # Agent 间通信（反馈）
            if result.get('success'):
                await self._send_feedback(subtask, result, context)
            else:
                logger.warning(f"子任务失败：{subtask['type']}")
        
        # 4. 汇总结果
        final_result = self._aggregate_results(task, results)
        
        return {
            'success': True,
            'result': final_result,
            'mode': 'multi_agent',
            'subtasks': len(subtasks),
            'details': results
        }
    
    def _topological_sort(self, subtasks: List[Dict]) -> List[Dict]:
        """拓扑排序 - 确保依赖顺序"""
        # 简单的拓扑排序实现
        task_map = {t['type']: t for t in subtasks}
        visited = set()
        result = []
        
        def visit(task_type: str):
            if task_type in visited:
                return
            visited.add(task_type)
            
            task = task_map.get(task_type)
            if task:
                for dep in task.get('dependencies', []):
                    visit(dep)
                result.append(task)
        
        for task in subtasks:
            visit(task['type'])
        
        return result
    
    async def _send_feedback(self, subtask: Dict, result: Dict, context: Dict):
        """Agent 间发送反馈"""
        # 实现 Agent 间通信
        # 例如：测试 Agent 发现 bug，通知代码生成 Agent 修复
        pass
    
    def _aggregate_results(self, task: str, results: Dict) -> Dict:
        """汇总多 Agent 执行结果"""
        # 汇总所有子任务结果
        aggregated = {
            'task': task,
            'code': None,
            'tests': None,
            'review': None,
            'documentation': None
        }
        
        for task_type, result in results.items():
            if result.get('success'):
                if task_type == 'code_generation':
                    aggregated['code'] = result.get('result')
                elif task_type == 'testing':
                    aggregated['tests'] = result.get('result')
                elif task_type == 'code_review':
                    aggregated['review'] = result.get('result')
                elif task_type == 'documentation':
                    aggregated['documentation'] = result.get('result')
        
        return aggregated
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'initialized': self._initialized,
            'agents': [role.value for role in self.agents.keys()],
            'agent_count': len(self.agents),
            'message_queue_size': len(self.message_queue),
            'task_history_count': len(self.task_history)
        }


# 全局多 Agent 系统实例
_multi_agent_system: Optional[MultiAgentSystem] = None

def get_multi_agent_system() -> MultiAgentSystem:
    """获取全局多 Agent 系统实例"""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system
