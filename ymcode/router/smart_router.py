#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由器

基于任务内容、Agent 能力和历史准确率，自动选择最优 Agent
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from .routing_rules import KEYWORD_MAP, ROUTING_RULES


@dataclass
class RouteResult:
    """路由结果"""
    selected_agent: str
    agent_name: str
    confidence: float  # 置信度 0-1
    matched_keywords: List[str]
    alternative_agents: List[str]
    reason: str
    response_time_estimate: float  # 预计响应时间（秒）


@dataclass
class AgentStats:
    """Agent 统计信息"""
    agent_id: str
    total_tasks: int = 0
    successful_tasks: int = 0
    avg_response_time: float = 0.0
    accuracy_rate: float = 0.95  # 默认 95%
    last_used: Optional[datetime] = None


class SmartRouter:
    """智能路由器"""
    
    def __init__(self, stats_file: Optional[str] = None):
        """
        初始化路由器
        
        Args:
            stats_file: 统计数据文件路径
        """
        self.stats_file = stats_file or Path(__file__).parent.parent / "data" / "router_stats.json"
        self.agent_stats: Dict[str, AgentStats] = {}
        self._load_stats()
    
    def _load_stats(self):
        """加载历史统计数据"""
        if Path(self.stats_file).exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for agent_id, stats in data.items():
                    self.agent_stats[agent_id] = AgentStats(
                        agent_id=agent_id,
                        total_tasks=stats.get('total_tasks', 0),
                        successful_tasks=stats.get('successful_tasks', 0),
                        avg_response_time=stats.get('avg_response_time', 0.0),
                        accuracy_rate=stats.get('accuracy_rate', 0.95)
                    )
            except Exception as e:
                print(f"加载统计数据失败：{e}")
        
        # 确保所有 Agent 都有统计
        for agent_id in ROUTING_RULES["agent_capabilities"]:
            if agent_id not in self.agent_stats:
                self.agent_stats[agent_id] = AgentStats(agent_id=agent_id)
    
    def _save_stats(self):
        """保存统计数据"""
        try:
            data = {
                agent_id: {
                    'total_tasks': stats.total_tasks,
                    'successful_tasks': stats.successful_tasks,
                    'avg_response_time': stats.avg_response_time,
                    'accuracy_rate': stats.accuracy_rate
                }
                for agent_id, stats in self.agent_stats.items()
            }
            Path(self.stats_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存统计数据失败：{e}")
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        keywords = []
        text_lower = text.lower()
        
        # 匹配中文关键词（2-4 个字）
        chinese_keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        keywords.extend(chinese_keywords)
        
        # 匹配英文关键词
        english_keywords = re.findall(r'\b[a-zA-Z]{2,}\b', text_lower)
        keywords.extend(english_keywords)
        
        # 匹配技术术语（带连字符）
        tech_terms = re.findall(r'\b[a-zA-Z]+-[a-zA-Z]+\b', text_lower)
        keywords.extend(tech_terms)
        
        return list(set(keywords))  # 去重
    
    def match_agents(self, keywords: List[str]) -> Dict[str, Tuple[int, List[str]]]:
        """
        匹配关键词到 Agent
        
        Args:
            keywords: 关键词列表
            
        Returns:
            {agent_id: (匹配分数，匹配的关键词)}
        """
        agent_scores: Dict[str, Tuple[int, List[str]]] = {}
        
        for keyword in keywords:
            # 检查高优先级规则
            for rule_name, agents in ROUTING_RULES["high_priority"].items():
                if keyword in rule_name or rule_name in keyword:
                    for agent in agents:
                        if agent not in agent_scores:
                            agent_scores[agent] = (0, [])
                        score, matched = agent_scores[agent]
                        agent_scores[agent] = (score + 3, matched + [keyword])  # 高优先级权重 3
            
            # 检查普通关键词映射
            for kw, agents in KEYWORD_MAP.items():
                if keyword in kw or kw in keyword:
                    for agent in agents:
                        if agent not in agent_scores:
                            agent_scores[agent] = (0, [])
                        score, matched = agent_scores[agent]
                        agent_scores[agent] = (score + 1, matched + [keyword])
        
        return agent_scores
    
    def calculate_confidence(self, score: int, matched_keywords: List[str]) -> float:
        """
        计算置信度
        
        Args:
            score: 匹配分数
            matched_keywords: 匹配的关键词
            
        Returns:
            置信度 0-1
        """
        if score == 0:
            return 0.3  # 默认置信度
        
        # 基础置信度
        base_confidence = min(0.7, 0.3 + score * 0.1)
        
        # 关键词多样性奖励
        diversity_bonus = min(0.2, len(matched_keywords) * 0.05)
        
        return min(1.0, base_confidence + diversity_bonus)
    
    def route(self, task: str, context: Optional[Dict] = None) -> RouteResult:
        """
        路由任务到最优 Agent
        
        Args:
            task: 任务描述
            context: 上下文信息（可选）
            
        Returns:
            路由结果
        """
        # 1. 提取关键词
        keywords = self.extract_keywords(task)
        
        # 2. 匹配 Agent
        agent_scores = self.match_agents(keywords)
        
        # 3. 如果没有匹配，使用默认路由
        if not agent_scores:
            default_agent = ROUTING_RULES["default"][0]
            agent_info = ROUTING_RULES["agent_capabilities"][default_agent]
            return RouteResult(
                selected_agent=default_agent,
                agent_name=agent_info["name"],
                confidence=0.5,
                matched_keywords=[],
                alternative_agents=ROUTING_RULES["default"][1:],
                reason="无关键词匹配，使用默认路由",
                response_time_estimate=agent_info["target_response_time"]
            )
        
        # 4. 计算综合得分（考虑历史准确率）
        scored_agents = []
        for agent_id, (score, matched) in agent_scores.items():
            stats = self.agent_stats.get(agent_id)
            accuracy_bonus = stats.accuracy_rate if stats else 0.95
            total_score = score * (0.7 + 0.3 * accuracy_bonus)
            scored_agents.append((agent_id, total_score, matched))
        
        # 5. 排序
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        # 6. 选择最优 Agent
        best_agent_id, best_score, matched_keywords = scored_agents[0]
        agent_info = ROUTING_RULES["agent_capabilities"][best_agent_id]
        
        # 7. 计算置信度
        confidence = self.calculate_confidence(int(best_score), matched_keywords)
        
        # 8. 准备备选 Agent
        alternatives = [aid for aid, _, _ in scored_agents[1:3]]
        
        return RouteResult(
            selected_agent=best_agent_id,
            agent_name=agent_info["name"],
            confidence=confidence,
            matched_keywords=list(set(matched_keywords)),
            alternative_agents=alternatives,
            reason=f"匹配 {len(matched_keywords)} 个关键词，综合得分 {best_score:.2f}",
            response_time_estimate=agent_info["target_response_time"]
        )
    
    def record_result(self, agent_id: str, success: bool, response_time: float):
        """
        记录路由结果
        
        Args:
            agent_id: Agent ID
            success: 是否成功
            response_time: 响应时间
        """
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = AgentStats(agent_id=agent_id)
        
        stats = self.agent_stats[agent_id]
        stats.total_tasks += 1
        
        if success:
            stats.successful_tasks += 1
        
        # 更新平均响应时间
        stats.avg_response_time = (
            (stats.avg_response_time * (stats.total_tasks - 1) + response_time)
            / stats.total_tasks
        )
        
        # 更新准确率
        stats.accuracy_rate = stats.successful_tasks / stats.total_tasks
        stats.last_used = datetime.now()
        
        self._save_stats()
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """获取 Agent 信息"""
        return ROUTING_RULES["agent_capabilities"].get(agent_id)
    
    def get_all_agents(self) -> List[Dict]:
        """获取所有 Agent 信息"""
        agents = []
        for agent_id, info in ROUTING_RULES["agent_capabilities"].items():
            stats = self.agent_stats.get(agent_id)
            agents.append({
                "id": agent_id,
                **info,
                "stats": {
                    "total_tasks": stats.total_tasks if stats else 0,
                    "accuracy_rate": stats.accuracy_rate if stats else 0.95,
                    "avg_response_time": stats.avg_response_time if stats else 0.0
                } if stats else None
            })
        return agents
