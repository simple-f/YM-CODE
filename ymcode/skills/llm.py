#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 技能 - 阿里云百炼大模型接入
支持通义千问等模型，可调用其他技能
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

import httpx
from dotenv import load_dotenv

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LLMSkill(BaseSkill):
    """LLM 技能 - 阿里云百炼接入"""
    
    def __init__(self):
        super().__init__("llm")
        
        # 从 .env 文件和环境变量加载配置
        # 优先加载项目根目录的 .env 文件
        workspace = Path(__file__).parent.parent.parent
        env_file = workspace / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"已加载 .env 文件：{env_file}")
        
        # 用户目录的 .env 文件
        user_env = Path.home() / ".ymcode" / ".env"
        if user_env.exists():
            load_dotenv(user_env)
            logger.info(f"已加载用户 .env 文件：{user_env}")
        
        # 获取 API Key（支持多种环境变量名）
        self.api_key = (
            os.getenv("DASHSCOPE_API_KEY") or
            os.getenv("DASHSCOPE_KEY") or
            os.getenv("ALIBABA_API_KEY") or
            os.getenv("QWEN_API_KEY") or
            ""
        )
        
        if self.api_key:
            key_preview = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
            logger.info(f"API Key 已加载：{key_preview}")
        else:
            logger.warning("未找到 API Key，LLM 功能将不可用")
        
        # 检测 API Key 类型并设置对应的接口
        if self.api_key.startswith("sk-sp-"):
            # 通义灵码 key，使用 OpenAI 兼容接口
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
            self.model = os.getenv("OPENAI_MODEL", "qwen3.5-plus")
            self.use_openai_format = True
            logger.info(f"检测到通义灵码 Key，使用 OpenAI 兼容接口：{self.base_url}")
        else:
            # 百炼标准 key
            self.base_url = "https://dashscope.aliyuncs.com/api/v1"
            self.model = "qwen-plus"
            self.use_openai_format = False
            logger.info(f"使用百炼标准接口：{self.base_url}")
        
        # 工具/技能定义（供大模型调用）
        self.available_tools = []
        
        # 对话历史
        self.conversation_history: List[Dict] = []
        self.max_history = 10  # 最多保留 10 轮对话
        
        # 数据目录
        self.data_dir = Path.home() / ".ymcode" / "skills" / "llm"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LLM 技能初始化完成 (模型：{self.model})")
    
    @property
    def description(self) -> str:
        return "阿里云百炼大模型接入，支持自然语言理解和技能调用"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "用户消息"
                },
                "use_tools": {
                    "type": "boolean",
                    "description": "是否启用工具调用",
                    "default": True
                },
                "model": {
                    "type": "string",
                    "description": "指定模型名称",
                    "default": "qwen-plus"
                }
            },
            "required": ["message"]
        }
    
    def set_available_tools(self, tools: List[Dict]) -> None:
        """设置可用的工具/技能列表"""
        self.available_tools = tools
        logger.info(f"设置可用工具：{len(tools)} 个")
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能"""
        if not self.api_key:
            return {
                "success": False,
                "error": "未配置 DASHSCOPE_API_KEY，请在环境变量中设置",
                "help": "export DASHSCOPE_API_KEY='your-api-key'"
            }
        
        message = arguments.get("message", "")
        use_tools = arguments.get("use_tools", True)
        model = arguments.get("model", self.model)
        
        try:
            # 调用大模型
            response = await self.call_llm(message, use_tools, model)
            
            # 处理响应
            if response.get("need_tool_call"):
                # 需要调用工具
                tool_result = await self.execute_tool(
                    response["tool_name"],
                    response["tool_args"]
                )
                
                # 检查工具执行是否成功
                is_success = tool_result.get('success', False) or tool_result.get('returncode', 0) == 0
                stdout = tool_result.get('stdout', '')
                stderr = tool_result.get('stderr', '')
                
                logger.info(f"工具执行结果：success={is_success}, returncode={tool_result.get('returncode')}, stdout_len={len(stdout)}, stderr_len={len(stderr)}")
                
                # 如果成功且有输出，直接返回输出内容（不经过 LLM）
                if is_success and stdout and stdout.strip():
                    logger.info(f"直接返回 stdout（前 100 字符）：{stdout[:100]}...")
                    # 有标准输出，直接返回
                    return {
                        "success": True,
                        "response": f"执行成功！\n\n```\n{stdout}\n```",
                        "model": model,
                        "tool_used": response["tool_name"],
                        "type": "tool_result_direct"
                    }
                
                # 执行失败或无输出，让 LLM 生成友好提示
                final_response = await self.process_tool_result(
                    message,
                    response["tool_name"],
                    tool_result,
                    model
                )
                return final_response
            else:
                # 直接返回大模型响应
                return {
                    "success": True,
                    "response": response.get("content", ""),
                    "model": model,
                    "type": "llm_response"
                }
                
        except Exception as e:
            logger.error(f"LLM 调用失败：{e}", exc_info=True)
            return {
                "success": False,
                "error": f"LLM 调用失败：{str(e)}",
                "type": "llm_error"
            }
    
    async def call_llm(self, message: str, use_tools: bool = True, model: str = None) -> Dict:
        """调用大模型"""
        if not model:
            model = self.model
        
        # 构建消息
        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": message})
        
        # 构建请求
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # 添加工具定义
        if use_tools and self.available_tools:
            payload["tools"] = self.available_tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 根据接口类型选择 URL
        if self.use_openai_format:
            # OpenAI 兼容接口（通义灵码）
            url = f"{self.base_url}/chat/completions"
            logger.debug(f"使用 OpenAI 兼容接口：{url}")
        else:
            # 百炼标准接口
            url = f"{self.base_url}/services/aigc/text-generation/generation"
            headers["X-DashScope-SSE"] = "disable"
            logger.debug(f"使用百炼标准接口：{url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.debug(f"发送请求到：{url}")
            logger.debug(f"请求 payload: {json.dumps(payload, ensure_ascii=False)[:200]}...")
            
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"API 请求失败：{response.status_code} - {response.text}")
                raise Exception(f"API 请求失败：{response.status_code} - {response.text[:200]}")
            
            result = response.json()
            
            # 解析响应（支持两种格式）
            if self.use_openai_format:
                # OpenAI 格式响应
                choices = result.get("choices", [])
                if not choices:
                    raise Exception("大模型返回为空")
                message_data = choices[0].get("message", {})
                content = message_data.get("content", "")
                tool_calls = message_data.get("tool_calls", [])
            else:
                # 百炼标准格式响应
                output = result.get("output", {})
                choices = output.get("choices", [])
                if not choices:
                    raise Exception("大模型返回为空")
                message_data = choices[0].get("message", {})
                content = message_data.get("content", "")
                tool_calls = message_data.get("tool_calls", [])
            
            if not choices:
                raise Exception("大模型返回为空")
            
            # 检查是否需要调用工具
            if tool_calls:
                tool_call = tool_calls[0]
                return {
                    "need_tool_call": True,
                    "tool_name": tool_call.get("function", {}).get("name", ""),
                    "tool_args": json.loads(tool_call.get("function", {}).get("arguments", "{}")),
                    "content": content
                }
            else:
                # 更新对话历史
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": content})
                
                # 限制历史长度
                if len(self.conversation_history) > self.max_history * 2:
                    self.conversation_history = self.conversation_history[-self.max_history * 2:]
                
                return {
                    "need_tool_call": False,
                    "content": content
                }
    
    async def execute_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """执行工具调用"""
        logger.info(f"执行工具：{tool_name}, 参数：{tool_args}")
        
        # 移除 skill_ 前缀
        skill_name = tool_name.replace("skill_", "")
        
        # 从全局注册表获取技能（需要外部设置）
        if hasattr(self, '_skills_registry') and self._skills_registry:
            skill = self._skills_registry.get(skill_name)
            if skill:
                try:
                    result = await skill.execute(tool_args)
                    logger.info(f"工具执行成功：{skill_name}")
                    return result
                except Exception as e:
                    logger.error(f"工具执行失败：{e}")
                    return {"error": str(e)}
            else:
                logger.warning(f"技能不存在：{skill_name}")
                return {"error": f"技能不存在：{skill_name}"}
        else:
            logger.warning("技能注册表未设置")
            return {"error": "技能注册表未设置"}
    
    def set_skills_registry(self, registry) -> None:
        """设置技能注册表（用于工具调用）"""
        self._skills_registry = registry
        logger.info("技能注册表已设置")
    
    async def process_tool_result(self, original_message: str, tool_name: str, tool_result: Any, model: str) -> Dict:
        """处理工具执行结果，让大模型生成最终响应"""
        try:
            # 简化处理：直接构建包含工具结果的提示
            tool_result_str = json.dumps(tool_result, ensure_ascii=False)
            
            # 判断工具执行是否成功
            is_success = tool_result.get('success', False) or tool_result.get('returncode', 0) == 0
            
            # 如果有 stdout，优先展示
            if is_success and tool_result.get('stdout'):
                return {
                    "success": True,
                    "response": f"执行成功！\n\n```\n{tool_result.get('stdout')}\n```",
                    "model": model,
                    "tool_used": tool_name,
                    "type": "tool_result_direct"
                }
            
            prompt = f"""用户请求：{original_message}

工具名称：{tool_name}
工具执行结果：
{tool_result_str}

执行状态：{"成功" if is_success else "失败"}

请根据工具执行结果，给用户一个友好的回复：
- 如果执行成功：直接展示结果内容，简洁明了
- 如果执行失败：解释原因并提供替代方案
- 如果有输出内容（stdout/stderr）：优先展示给用户"""
            
            messages = [
                {"role": "system", "content": "你是一个友好的 AI 助手，擅长使用各种工具帮助用户完成任务。你会清晰、简洁地展示工具执行结果。"},
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            # 使用 OpenAI 兼容接口
            url = f"{self.base_url}/chat/completions"
            
            logger.info(f"调用 LLM 处理工具结果：{url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                logger.info(f"LLM 响应状态：{response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"API 请求失败：{response.status_code} - {response.text[:200]}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "model": model,
                        "tool_used": tool_name
                    }
                
                result = response.json()
                logger.debug(f"LLM 响应：{result}")
                
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    error_msg = "大模型返回为空"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "model": model,
                        "tool_used": tool_name
                    }
                
                return {
                    "success": True,
                    "response": content,
                    "model": model,
                    "tool_used": tool_name,
                    "type": "llm_with_tool"
                }
                
        except Exception as e:
            logger.error(f"process_tool_result 异常：{e}", exc_info=True)
            return {
                "success": False,
                "error": f"处理工具结果时出错：{str(e)}",
                "model": model,
                "tool_used": tool_name
            }
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info("对话历史已清空")
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history.copy()
