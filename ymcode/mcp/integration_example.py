#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client v2 完整集成示例
展示如何使用 MCP 客户端与 Agent 集成
"""

import asyncio
from typing import Optional
from .client_v2 import MCPClientV2
from .server_registry import get_registry, MCPServerConfig
from .prompts import get_templates, render_template
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MCPIntegration:
    """MCP 与 Agent 集成管理器"""
    
    def __init__(self):
        """初始化集成管理器"""
        self.client: Optional[MCPClientV2] = None
        self.registry = get_registry()
        self.templates = get_templates()
        self.initialized = False
        
        logger.info("MCP 集成管理器初始化完成")
    
    async def initialize(self) -> bool:
        """
        初始化 MCP 客户端
        
        返回:
            是否成功
        """
        logger.info("初始化 MCP 客户端...")
        
        try:
            # 创建客户端
            self.client = MCPClientV2()
            
            # 连接默认的 MCP 服务器
            servers_to_connect = [
                ("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem"]),
            ]
            
            for name, command, args in servers_to_connect:
                success = await self.client.connect_stdio(name, command, args)
                if success:
                    logger.info(f"MCP 服务器连接成功：{name}")
                else:
                    logger.warning(f"MCP 服务器连接失败：{name}")
            
            self.initialized = True
            
            # 生成工具发现提示
            if self.client.tools:
                tools_list = "\n".join([
                    f"  - {tool.name}: {tool.description}"
                    for tool in self.client.tools.values()
                ])
                
                prompt = render_template(
                    'tool_discovery',
                    server_name="filesystem",
                    tools_list=tools_list,
                    tools_capabilities="文件读写、目录浏览、文件搜索"
                )
                
                logger.info(f"工具发现提示：\n{prompt}")
            
            return True
            
        except Exception as e:
            logger.error(f"MCP 初始化失败：{e}")
            return False
    
    async def shutdown(self) -> None:
        """关闭 MCP 连接"""
        if self.client:
            await self.client.disconnect()
            logger.info("MCP 客户端已关闭")
    
    def get_tools_for_agent(self) -> list:
        """
        获取传递给 Agent 的工具定义
        
        返回:
            工具定义列表
        """
        if not self.client:
            return []
        
        return self.client.get_tools_definition()
    
    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        执行 MCP 工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数
        
        返回:
            执行结果
        """
        if not self.client:
            return {"error": "MCP 客户端未初始化"}
        
        try:
            # 生成工具调用提示
            tool = self.client.tools.get(tool_name)
            if tool:
                prompt = render_template(
                    'tool_call',
                    tool_name=tool_name,
                    tool_description=tool.description,
                    tool_arguments=str(arguments)
                )
                logger.debug(f"工具调用提示：\n{prompt}")
            
            # 执行工具
            result = await self.client.call_tool(tool_name, arguments)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"工具执行失败：{e}")
            
            # 生成错误处理提示
            prompt = render_template(
                'error_handling',
                tool_name=tool_name,
                error_message=str(e),
                error_type=type(e).__name__,
                possible_cause_1="参数格式错误",
                possible_cause_2="服务器未连接",
                possible_cause_3="工具不存在",
                suggested_solution="请检查参数并重试"
            )
            logger.debug(f"错误处理提示：\n{prompt}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> dict:
        """
        获取集成状态
        
        返回:
            状态字典
        """
        return {
            "initialized": self.initialized,
            "client_status": self.client.get_status() if self.client else None,
            "available_servers": len(self.registry.list_servers()),
            "available_templates": len(self.templates.list_templates())
        }


async def demo():
    """演示 MCP 集成"""
    
    print("=" * 60)
    print("MCP Client v2 集成演示")
    print("=" * 60)
    
    # 创建集成管理器
    integration = MCPIntegration()
    
    # 初始化
    print("\n📦 初始化 MCP 客户端...")
    success = await integration.initialize()
    
    if success:
        print("✅ 初始化成功")
        
        # 显示状态
        status = integration.get_status()
        print(f"\n📊 状态:")
        print(f"   已连接服务器：{status['client_status']['servers']}")
        print(f"   可用工具：{status['client_status']['tools']}")
        print(f"   可用资源：{status['client_status']['resources']}")
        
        # 获取工具定义
        print(f"\n🔧 工具定义:")
        tools_def = integration.get_tools_for_agent()
        for tool in tools_def:
            print(f"   - {tool['function']['name']}: {tool['function']['description']}")
        
        # 演示工具调用（如果已连接）
        if status['client_status']['tools'] > 0:
            print(f"\n🚀 演示工具调用...")
            # 这里可以添加实际的调用示例
        
    else:
        print("❌ 初始化失败")
    
    # 关闭
    print("\n🛑 关闭连接...")
    await integration.shutdown()
    print("✅ 完成")


if __name__ == "__main__":
    asyncio.run(demo())
