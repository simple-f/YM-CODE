#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@mention 解析器 - 从消息中提取被提到的 Agent

支持格式：
- @ai1
- @架构师
- @后端开发
- @ai1 和 @ai2
- 请 @架构师 设计这个功能
"""

import re
from typing import List, Dict, Optional, Set
from pathlib import Path
import json

# Agent ID 到名称的映射（从 team.json 加载）
TEAM_FILE = Path(__file__).parent.parent.parent / "configs" / "team.json"


def load_agent_mapping() -> Dict[str, str]:
    """
    加载 Agent ID 和名称的映射
    
    返回：
        {
            "ai1": "架构师",
            "架构师": "ai1",
            "后端开发": "ai2",
            ...
        }
    """
    if not TEAM_FILE.exists():
        # 默认映射
        return {
            "ai1": "架构师",
            "ai2": "后端开发",
            "ai3": "前端开发",
            "ai4": "全栈开发",
            "ai5": "测试工程师",
            "ai6": "技术顾问",
            "ai7": "产品顾问",
            "架构师": "ai1",
            "后端开发": "ai2",
            "前端开发": "ai3",
            "全栈开发": "ai4",
            "测试工程师": "ai5",
            "技术顾问": "ai6",
            "产品顾问": "ai7",
        }
    
    with open(TEAM_FILE, 'r', encoding='utf-8') as f:
        team_data = json.load(f)
    
    mapping = {}
    for agent in team_data.get('agents', []):
        agent_id = agent.get('id')
        agent_name = agent.get('name')
        if agent_id and agent_name:
            mapping[agent_id] = agent_name
            mapping[agent_name] = agent_id
            # 支持小写
            mapping[agent_name.lower()] = agent_id
    
    return mapping


def parse_mentions(message: str, agent_mapping: Optional[Dict] = None) -> List[str]:
    """
    从消息中解析被@的 Agent ID
    
    参数：
        message: 用户消息
        agent_mapping: Agent 映射字典（可选，默认自动加载）
    
    返回：
        ["ai1", "ai2"] 被提到的 Agent ID 列表
    
    示例：
        >>> parse_mentions("@ai1 和 @架构师 设计这个功能")
        ["ai1", "ai1"]  # 都指向架构师
        
        >>> parse_mentions("请 @后端开发 实现 API")
        ["ai2"]
    """
    if agent_mapping is None:
        agent_mapping = load_agent_mapping()
    
    # 正则表达式匹配 @mention
    # 支持：@ai1, @架构师，@后端开发
    mention_pattern = r'@([a-zA-Z0-9_\u4e00-\u9fa5]+)'
    
    matches = re.findall(mention_pattern, message)
    
    mentioned_ids = []
    for match in matches:
        # 尝试匹配 Agent ID 或名称
        if match in agent_mapping:
            target = agent_mapping[match]
            # 如果是名称转 ID，如果是 ID 保持不变
            if target.startswith('ai'):
                mentioned_ids.append(target)
            else:
                mentioned_ids.append(match)
    
    # 去重，保持顺序
    seen = set()
    unique_ids = []
    for agent_id in mentioned_ids:
        if agent_id not in seen:
            seen.add(agent_id)
            unique_ids.append(agent_id)
    
    return unique_ids


def parse_mentions_with_details(message: str, agent_mapping: Optional[Dict] = None) -> List[Dict]:
    """
    解析@mention 并返回详细信息
    
    返回：
        [
            {
                "agent_id": "ai1",
                "agent_name": "架构师",
                "mention_text": "@ai1",
                "position": 0  # 在消息中的位置
            },
            ...
        ]
    """
    if agent_mapping is None:
        agent_mapping = load_agent_mapping()
    
    mention_pattern = r'@([a-zA-Z0-9_\u4e00-\u9fa5]+)'
    
    results = []
    for match in re.finditer(mention_pattern, message):
        mention_text = match.group(0)  # 包括@
        mention_target = match.group(1)  # 不包括@
        position = match.start()
        
        if mention_target in agent_mapping:
            target = agent_mapping[mention_target]
            
            # 判断是 ID 还是名称
            if mention_target.startswith('ai'):
                agent_id = mention_target
                agent_name = target
            else:
                agent_id = target
                agent_name = mention_target
            
            results.append({
                "agent_id": agent_id,
                "agent_name": agent_name,
                "mention_text": mention_text,
                "position": position
            })
    
    return results


def remove_mentions(message: str) -> str:
    """
    从消息中移除所有@mention，保留纯文本内容
    
    示例：
        >>> remove_mentions("@ai1 请设计这个功能")
        "请设计这个功能"
    """
    mention_pattern = r'@[a-zA-Z0-9_\u4e00-\u9fa5]+\s*'
    return re.sub(mention_pattern, '', message).strip()


def extract_task_for_agent(message: str, agent_id: str, agent_mapping: Optional[Dict] = None) -> str:
    """
    提取针对特定 Agent 的任务描述
    
    策略：
    1. 找到@该 Agent 的位置
    2. 提取@之后到下一个@或句尾的内容
    
    参数：
        message: 完整消息
        agent_id: 目标 Agent ID
        agent_mapping: Agent 映射
    
    返回：
        针对该 Agent 的任务描述
    """
    if agent_mapping is None:
        agent_mapping = load_agent_mapping()
    
    # 获取该 Agent 的所有可能称呼
    agent_names = [agent_id]
    for key, value in agent_mapping.items():
        if value == agent_id:
            agent_names.append(key)
    
    # 构建正则
    pattern = r'@(' + '|'.join(re.escape(name) for name in agent_names) + r')\s*([^@]+?)(?=@|$)'
    
    matches = re.findall(pattern, message, re.DOTALL)
    
    if matches:
        # 提取所有针对该 Agent 的任务，合并
        tasks = [match[1].strip() for match in matches]
        return ' '.join(tasks)
    
    # 如果没有专门的任务，返回去除@后的完整消息
    return remove_mentions(message)


class MentionRouter:
    """
    @mention 路由器
    
    用法：
        router = MentionRouter()
        result = router.route("@ai1 和 @ai2 设计登录系统")
        # result = {
        #     "agent_ids": ["ai1", "ai2"],
        #     "clean_message": "设计登录系统",
        #     "should_respond": True,
        #     "details": [...]
        # }
    """
    
    def __init__(self, agent_mapping: Optional[Dict] = None):
        self.agent_mapping = agent_mapping or load_agent_mapping()
    
    def route(self, message: str) -> Dict:
        """
        路由消息到对应的 Agent
        
        返回：
            {
                "agent_ids": ["ai1", "ai2"],  # 需要响应的 Agent
                "clean_message": "设计登录系统",  # 清理后的消息
                "should_respond": True,  # 是否应该响应
                "mentions": [...],  # 详细的@信息
                "mode": "mention"  # 或 "broadcast" 如果没有@任何人
            }
        """
        mentions = parse_mentions_with_details(message, self.agent_mapping)
        agent_ids = parse_mentions(message, self.agent_mapping)
        clean_message = remove_mentions(message)
        
        if agent_ids:
            return {
                "agent_ids": agent_ids,
                "clean_message": clean_message,
                "should_respond": True,
                "mentions": mentions,
                "mode": "mention"
            }
        else:
            # 没有@任何人，根据策略决定
            return {
                "agent_ids": [],  # 或者返回所有 Agent IDs
                "clean_message": message,
                "should_respond": False,  # 或者 True
                "mentions": [],
                "mode": "broadcast"
            }
    
    def get_agent_tasks(self, message: str) -> Dict[str, str]:
        """
        为每个被@的 Agent 提取任务
        
        返回：
            {
                "ai1": "设计这个功能",
                "ai2": "实现 API 接口"
            }
        """
        mentions = parse_mentions_with_details(message, self.agent_mapping)
        
        tasks = {}
        for mention in mentions:
            agent_id = mention['agent_id']
            task = extract_task_for_agent(message, agent_id, self.agent_mapping)
            tasks[agent_id] = task
        
        return tasks


# ============ 测试 ============

if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "@ai1 设计一个登录系统",
        "请 @架构师 和 @后端开发 协作完成",
        "@ai1 设计架构，@ai2 实现代码，@ai5 测试",
        "没有@任何人",
        "@ai1 @ai2 @ai3 全部参与",
    ]
    
    router = MentionRouter()
    
    print("=" * 60)
    print("Mention Parser 测试")
    print("=" * 60)
    
    for message in test_cases:
        print(f"\n消息：{message}")
        result = router.route(message)
        print(f"  Agent IDs: {result['agent_ids']}")
        print(f"  清理后：{result['clean_message']}")
        print(f"  模式：{result['mode']}")
        
        if result['agent_ids']:
            tasks = router.get_agent_tasks(message)
            print(f"  任务分配:")
            for agent_id, task in tasks.items():
                print(f"    {agent_id}: {task[:50]}...")
