#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自我提升技能 - 自我总结、自我学习、持续改进
"""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SelfImprovementSkill(BaseSkill):
    """自我提升技能"""
    
    def __init__(self):
        super().__init__("self_improvement")
        
        # 状态管理
        self.summary_history: List[Dict] = []
        self.knowledge_base: Dict = {}
        self.lesson_learned: List[Dict] = []
        
        # 持久化路径
        self.data_dir = Path.home() / ".ymcode" / "skills" / "self_improvement"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载历史数据
        self._load_data()
    
    @property
    def description(self) -> str:
        return "自我总结和提升技能，从经验中学习并持续改进"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["summary", "improve", "query", "reset"]
                },
                "session_id": {
                    "type": "string",
                    "description": "会话 ID（summary 操作需要）"
                },
                "skill_name": {
                    "type": "string",
                    "description": "技能名称（improve 操作需要）"
                },
                "feedback": {
                    "type": "string",
                    "description": "反馈内容（improve 操作需要）"
                },
                "query": {
                    "type": "string",
                    "description": "查询内容（query 操作需要）"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能"""
        action = arguments.get("action")
        
        if action == "summary":
            return await self.summary(arguments.get("session_id", ""))
        elif action == "improve":
            return await self.improve(
                arguments.get("skill_name", ""),
                arguments.get("feedback", "")
            )
        elif action == "query":
            return await self.query(arguments.get("query", ""))
        elif action == "reset":
            return await self.reset()
        else:
            return {"error": f"未知操作：{action}"}
    
    async def summary(self, session_id: str) -> Dict:
        """
        自我总结
        
        参数:
            session_id: 会话 ID
        
        返回:
            总结结果
        """
        logger.info(f"执行自我总结：{session_id}")
        
        # TODO: 从会话加载对话历史
        # 目前先模拟
        conversation = await self._load_conversation(session_id)
        
        # 分析对话
        analysis = self._analyze_conversation(conversation)
        
        # 提取经验教训
        lessons = self._extract_lessons(conversation)
        
        # 保存总结
        summary_result = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "lessons": lessons
        }
        
        self.summary_history.append(summary_result)
        self.lesson_learned.extend(lessons)
        
        # 持久化
        self._save_data()
        
        logger.info(f"自我总结完成：{len(lessons)} 条经验")
        
        return summary_result
    
    async def improve(self, skill_name: str, feedback: str) -> Dict:
        """
        自我提升
        
        参数:
            skill_name: 技能名称
            feedback: 反馈内容
        
        返回:
            提升结果
        """
        logger.info(f"执行自我提升：{skill_name}")
        
        # 更新知识库
        if skill_name not in self.knowledge_base:
            self.knowledge_base[skill_name] = {
                "created": datetime.now().isoformat(),
                "feedbacks": []
            }
        
        self.knowledge_base[skill_name]["feedbacks"].append({
            "timestamp": datetime.now().isoformat(),
            "content": feedback
        })
        
        # 分析反馈
        improvement = self._analyze_feedback(skill_name, feedback)
        
        # 持久化
        self._save_data()
        
        logger.info(f"自我提升完成：{skill_name}")
        
        return {
            "success": True,
            "skill_name": skill_name,
            "improvement": improvement
        }
    
    async def query(self, query: str) -> Dict:
        """
        查询知识库
        
        参数:
            query: 查询内容
        
        返回:
            查询结果
        """
        logger.info(f"查询知识库：{query}")
        
        # 简单关键词匹配
        results = []
        
        # 搜索经验教训
        for lesson in self.lesson_learned:
            if query.lower() in str(lesson).lower():
                results.append({
                    "type": "lesson",
                    "content": lesson
                })
        
        # 搜索知识库
        for skill_name, data in self.knowledge_base.items():
            if query.lower() in skill_name.lower():
                results.append({
                    "type": "skill",
                    "name": skill_name,
                    "data": data
                })
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def reset(self) -> Dict:
        """重置所有数据"""
        logger.info("重置自我提升数据")
        
        self.summary_history.clear()
        self.knowledge_base.clear()
        self.lesson_learned.clear()
        
        # 删除持久化文件
        data_file = self.data_dir / "data.json"
        if data_file.exists():
            data_file.unlink()
        
        return {"success": True, "message": "已重置所有数据"}
    
    # ========== 内部方法 ==========
    
    async def _load_conversation(self, session_id: str) -> List[Dict]:
        """加载会话对话"""
        # TODO: 实际从会话管理器加载
        # 目前返回模拟数据
        return [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
        ]
    
    def _analyze_conversation(self, conversation: List[Dict]) -> Dict:
        """分析对话"""
        # 简单统计
        user_messages = [m for m in conversation if m["role"] == "user"]
        assistant_messages = [m for m in conversation if m["role"] == "assistant"]
        
        return {
            "total_messages": len(conversation),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "avg_response_length": sum(len(m["content"]) for m in assistant_messages) / max(len(assistant_messages), 1)
        }
    
    def _extract_lessons(self, conversation: List[Dict]) -> List[Dict]:
        """提取经验教训"""
        # TODO: 使用 LLM 分析提取
        # 目前返回空列表
        return []
    
    def _analyze_feedback(self, skill_name: str, feedback: str) -> Dict:
        """分析反馈"""
        # TODO: 使用 LLM 分析反馈
        return {
            "sentiment": "positive",
            "key_points": ["反馈已记录"],
            "action_items": ["持续改进"]
        }
    
    def _load_data(self) -> None:
        """加载持久化数据"""
        data_file = self.data_dir / "data.json"
        
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.summary_history = data.get("summary_history", [])
                self.knowledge_base = data.get("knowledge_base", {})
                self.lesson_learned = data.get("lesson_learned", [])
                
                logger.info(f"加载自我提升数据：{len(self.summary_history)} 条总结")
            except Exception as e:
                logger.error(f"加载数据失败：{e}")
    
    def _save_data(self) -> None:
        """保存持久化数据"""
        data_file = self.data_dir / "data.json"
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary_history": self.summary_history,
                    "knowledge_base": self.knowledge_base,
                    "lesson_learned": self.lesson_learned
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存自我提升数据：{len(self.summary_history)} 条总结")
        except Exception as e:
            logger.error(f"保存数据失败：{e}")
