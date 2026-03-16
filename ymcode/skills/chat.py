#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天技能 - 处理自然语言对话
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChatSkill(BaseSkill):
    """聊天技能"""
    
    def __init__(self):
        super().__init__("chat")
    
    @property
    def description(self) -> str:
        return "自然语言对话技能，处理问候、闲聊和一般性问题"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "用户消息"
                }
            },
            "required": ["message"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能"""
        message = arguments.get("message", "").strip()
        message_lower = message.lower()
        
        # 问候语
        if any(greeting in message_lower for greeting in ["你好", "hello", "hi", "hey", "早上好", "下午好", "晚上好", "nihao"]):
            hour = datetime.now().hour
            if hour < 12:
                greeting = "早上好！"
            elif hour < 18:
                greeting = "下午好！"
            else:
                greeting = "晚上好！"
            
            return {
                "success": True,
                "response": f"{greeting} 我是 YM-CODE 助手，有什么可以帮您的吗？",
                "type": "greeting"
            }
        
        # 告别语
        if any(farewell in message_lower for farewell in ["再见", "bye", "goodbye", "拜拜"]):
            return {
                "success": True,
                "response": "再见！祝您有美好的一天！",
                "type": "farewell"
            }
        
        # 感谢
        if any(thanks in message_lower for thanks in ["谢谢", "thank", "thanks", "多谢"]):
            return {
                "success": True,
                "response": "不客气！随时为您服务。",
                "type": "acknowledgment"
            }
        
        # 自我介绍/身份问题
        if any(question in message_lower for question in ["你是谁", "你是啥", "what are you", "who are you", "自我介绍", "介绍一下自己", "哪个模型", "什么模型", "based on", "built on"]):
            return {
                "success": True,
                "response": "我是 YM-CODE，一个智能编程助手。\n\n" +
                          "我可以帮您：\n" +
                          "• 🔍 搜索信息和技术文档\n" +
                          "• 💻 执行 shell 命令和脚本\n" +
                          "• 📊 分析代码结构和质量\n" +
                          "• 🧠 管理记忆和上下文\n" +
                          "• 🌐 发送 HTTP 请求\n" +
                          "• 🗄️ 操作数据库\n" +
                          "• 🎨 格式化代码和文本\n" +
                          "• 🐳 管理 Docker 容器\n\n" +
                          "直接告诉我您需要什么帮助！",
                "type": "introduction"
            }
        
        # 帮助请求
        if any(help_word in message_lower for help_word in ["帮助", "help", "怎么用", "如何使用", "能做什么"]):
            return {
                "success": True,
                "response": "我是 YM-CODE 助手，可以帮助您：\n" +
                          "• 搜索信息 (search)\n" +
                          "• 执行 shell 命令 (shell)\n" +
                          "• 代码分析 (code_analysis)\n" +
                          "• 记忆管理 (memory)\n" +
                          "• HTTP 请求 (http)\n" +
                          "• 数据库操作 (database)\n" +
                          "• 格式化 (formatter)\n" +
                          "• Docker 操作 (docker)\n\n" +
                          "直接告诉我您需要什么帮助！",
                "type": "help"
            }
        
        # 默认响应
        return {
            "success": True,
            "response": f"收到您的消息：\"{message}\"\n\n" +
                       "我还在学习中，目前可以帮您执行特定任务。\n" +
                       "输入 'help' 查看可用功能，或者问我'你是谁'了解更多。",
            "type": "default"
        }
