#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆技能 - 记忆管理、上下文管理、长期记忆
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MemorySkill(BaseSkill):
    """记忆技能"""
    
    def __init__(self):
        super().__init__("memory")
        
        # 短期记忆（会话级）
        self.short_term_memory: Dict[str, List[Dict]] = {}
        
        # 长期记忆（持久化）
        self.long_term_memory: List[Dict] = []
        
        # 工作记忆（当前上下文）
        self.working_memory: Dict = {}
        
        # 持久化路径
        self.data_dir = Path.home() / ".ymcode" / "skills" / "memory"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载长期记忆
        self._load_long_term_memory()
    
    @property
    def description(self) -> str:
        return "记忆管理和上下文管理技能，支持短期记忆、长期记忆和工作记忆"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["save", "load", "search", "forget", "clear", "status"]
                },
                "session_id": {
                    "type": "string",
                    "description": "会话 ID（save/load 操作需要）"
                },
                "content": {
                    "type": "string",
                    "description": "记忆内容（save 操作需要）"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（search 操作需要）"
                },
                "memory_id": {
                    "type": "string",
                    "description": "记忆 ID（forget 操作需要）"
                },
                "memory_type": {
                    "type": "string",
                    "description": "记忆类型",
                    "enum": ["short", "long", "working"]
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能"""
        action = arguments.get("action")
        
        if action == "save":
            return await self.save_memory(
                arguments.get("session_id", "default"),
                arguments.get("content", "")
            )
        elif action == "load":
            return await self.load_memory(arguments.get("session_id", "default"))
        elif action == "search":
            return await self.search_memory(arguments.get("query", ""))
        elif action == "forget":
            return await self.forget_memory(arguments.get("memory_id", ""))
        elif action == "clear":
            return await self.clear_memory(arguments.get("memory_type", "working"))
        elif action == "status":
            return self.get_status()
        else:
            return {"error": f"未知操作：{action}"}
    
    async def save_memory(self, session_id: str, content: str) -> Dict:
        """
        保存记忆
        
        参数:
            session_id: 会话 ID
            content: 记忆内容
        
        返回:
            保存结果
        """
        logger.info(f"保存记忆：{session_id}")
        
        # 创建记忆记录
        memory = {
            "id": f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "session_id": session_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "importance": 1.0  # 重要性评分
        }
        
        # 保存到短期记忆
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        
        self.short_term_memory[session_id].append(memory)
        
        # 保存到长期记忆（重要记忆）
        if memory["importance"] > 0.5:
            self.long_term_memory.append(memory)
            self._save_long_term_memory()
        
        logger.info(f"记忆保存成功：{memory['id']}")
        
        return {
            "success": True,
            "memory_id": memory["id"],
            "session_id": session_id
        }
    
    async def load_memory(self, session_id: str) -> Dict:
        """
        加载记忆
        
        参数:
            session_id: 会话 ID
        
        返回:
            记忆列表
        """
        logger.info(f"加载记忆：{session_id}")
        
        # 从短期记忆加载
        memories = self.short_term_memory.get(session_id, [])
        
        return {
            "success": True,
            "session_id": session_id,
            "memories": memories,
            "count": len(memories)
        }
    
    async def search_memory(self, query: str) -> Dict:
        """
        搜索记忆
        
        参数:
            query: 搜索关键词
        
        返回:
            搜索结果
        """
        logger.info(f"搜索记忆：{query}")
        
        results = []
        
        # 搜索长期记忆
        for memory in self.long_term_memory:
            if query.lower() in memory["content"].lower():
                results.append({
                    "type": "long_term",
                    "memory": memory,
                    "relevance": 1.0
                })
        
        # 搜索短期记忆
        for session_id, memories in self.short_term_memory.items():
            for memory in memories:
                if query.lower() in memory["content"].lower():
                    results.append({
                        "type": "short_term",
                        "memory": memory,
                        "relevance": 0.8
                    })
        
        # 按相关性排序
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return {
            "success": True,
            "query": query,
            "results": results[:10],  # 返回前 10 个
            "count": len(results)
        }
    
    async def forget_memory(self, memory_id: str) -> Dict:
        """
        忘记记忆
        
        参数:
            memory_id: 记忆 ID
        
        返回:
            删除结果
        """
        logger.info(f"忘记记忆：{memory_id}")
        
        # 从长期记忆删除
        for i, memory in enumerate(self.long_term_memory):
            if memory["id"] == memory_id:
                del self.long_term_memory[i]
                self._save_long_term_memory()
                return {"success": True, "message": "已从长期记忆删除"}
        
        # 从短期记忆删除
        for session_id, memories in self.short_term_memory.items():
            for i, memory in enumerate(memories):
                if memory["id"] == memory_id:
                    del self.short_term_memory[session_id][i]
                    return {"success": True, "message": "已从短期记忆删除"}
        
        return {"success": False, "message": "记忆不存在"}
    
    async def clear_memory(self, memory_type: str) -> Dict:
        """
        清空记忆
        
        参数:
            memory_type: 记忆类型
        
        返回:
            清空结果
        """
        logger.info(f"清空记忆：{memory_type}")
        
        if memory_type == "short":
            self.short_term_memory.clear()
            return {"success": True, "type": "short", "message": "短期记忆已清空"}
        elif memory_type == "long":
            self.long_term_memory.clear()
            self._save_long_term_memory()
            return {"success": True, "type": "long", "message": "长期记忆已清空"}
        elif memory_type == "working":
            self.working_memory.clear()
            return {"success": True, "type": "working", "message": "工作记忆已清空"}
        else:
            return {"success": False, "message": "未知记忆类型"}
    
    def get_status(self) -> Dict:
        """获取记忆状态"""
        return {
            "short_term_count": sum(len(m) for m in self.short_term_memory.values()),
            "long_term_count": len(self.long_term_memory),
            "working_memory_keys": list(self.working_memory.keys()),
            "sessions": list(self.short_term_memory.keys())
        }
    
    # ========== 内部方法 ==========
    
    def _load_long_term_memory(self) -> None:
        """加载长期记忆"""
        data_file = self.data_dir / "long_term_memory.json"
        
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.long_term_memory = json.load(f)
                
                logger.info(f"加载长期记忆：{len(self.long_term_memory)} 条")
            except Exception as e:
                logger.error(f"加载长期记忆失败：{e}")
    
    def _save_long_term_memory(self) -> None:
        """保存长期记忆"""
        data_file = self.data_dir / "long_term_memory.json"
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存长期记忆：{len(self.long_term_memory)} 条")
        except Exception as e:
            logger.error(f"保存长期记忆失败：{e}")
