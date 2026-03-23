#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Host - CLI 应用的 MCP Host 实现
"""

import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path

from .host import MCPHost, HostConfig
from .client import MCPClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CLIHost(MCPHost):
    """
    CLI 应用 Host
    
    继承自 MCPHost，添加 CLI 特定功能：
    - 交互式配置
    - 进度显示
    - 错误提示
    
    使用示例:
        >>> host = CLIHost()
        >>> await host.initialize()
        >>> await host.connect_client("fs", "filesystem", "npx -y @mcp/server-filesystem")
        >>> tools = await host.list_all_tools()
        >>> await host.shutdown()
    """
    
    def __init__(self, config: Optional[HostConfig] = None):
        """初始化 CLI Host"""
        # 使用 CLI 默认配置
        cli_config = config or HostConfig(
            name="ym-code-cli",
            version="1.0.0",
            max_clients=5,
            connection_timeout=30,
            retry_attempts=3
        )
        
        super().__init__(cli_config)
        
        self._verbose = False
        self._show_progress = True
        
        logger.info("CLIHost 初始化完成")
    
    def set_verbose(self, verbose: bool):
        """设置详细模式"""
        self._verbose = verbose
        if verbose:
            logging.getLogger("ymcode").setLevel(logging.DEBUG)
    
    async def connect_client(
        self,
        client_id: str,
        server_name: str,
        server_url: str,
        retry: bool = True,
        show_progress: bool = True
    ) -> bool:
        """
        连接 Client（CLI 增强版）
        
        参数:
            client_id: Client ID
            server_name: Server 名称
            server_url: Server URL
            retry: 是否重试
            show_progress: 显示进度
        
        返回:
            是否成功
        """
        if show_progress and self._show_progress:
            print(f"🔌 正在连接 {server_name}...")
        
        success = await super().connect_client(
            client_id,
            server_name,
            server_url,
            retry
        )
        
        if show_progress and self._show_progress:
            if success:
                print(f"✅ {server_name} 已连接")
            else:
                print(f"❌ {server_name} 连接失败")
        
        return success
    
    async def disconnect_all(self, show_progress: bool = True):
        """断开所有 Client"""
        if show_progress and self._show_progress:
            print(f"\n🔌 正在断开 {len(self.clients)} 个连接...")
        
        await self.shutdown()
        
        if show_progress and self._show_progress:
            print("✅ 所有连接已断开")
    
    def show_status(self):
        """显示 Host 状态"""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("MCP Host 状态")
        print("=" * 50)
        print(f"名称：{status['name']}")
        print(f"版本：{status['version']}")
        print(f"状态：{'✅ 运行中' if status['running'] else '⏸️ 已停止'}")
        print(f"Client 数量：{status['client_count']}/{status['max_clients']}")
        
        if status['clients']:
            print("\n已连接的 Client:")
            for client_id in status['clients']:
                print(f"  - {client_id}")
        
        print("=" * 50)
    
    async def interactive_connect(self) -> bool:
        """交互式连接 Client"""
        print("\n=== MCP Client 连接 ===\n")
        
        # 显示可用 Server
        servers = self.server_registry.list_servers()
        print("可用的 MCP Server:")
        for i, server in enumerate(servers, 1):
            print(f"  {i}. {server['name']} - {server.get('description', '')}")
        
        # 获取用户输入
        try:
            choice = input("\n选择 Server 编号（或输入 'q' 退出）: ")
            
            if choice.lower() == 'q':
                return False
            
            server_idx = int(choice) - 1
            if 0 <= server_idx < len(servers):
                server = servers[server_idx]
                client_id = server['name']
                
                # 构建连接命令
                if server['type'] == 'stdio':
                    url = f"{server['command']} {' '.join(server.get('args', []))}"
                else:
                    url = server.get('url', '')
                
                return await self.connect_client(client_id, server['name'], url)
            else:
                print("无效的选择")
                return False
                
        except Exception as e:
            print(f"错误：{e}")
            return False
    
    async def list_tools_interactive(self):
        """交互式列出工具"""
        tools = await self.list_all_tools()
        
        if not tools:
            print("\n没有找到可用工具")
            return
        
        print("\n" + "=" * 50)
        print("可用工具列表")
        print("=" * 50)
        
        for i, tool in enumerate(tools, 1):
            print(f"\n{i}. {tool['name']}")
            print(f"   描述：{tool.get('description', '无')}")
            print(f"   Client: {tool.get('client_id', 'unknown')}")
            
            # 显示参数 schema
            if 'inputSchema' in tool:
                schema = tool['inputSchema']
                if 'properties' in schema:
                    print("   参数:")
                    for param_name, param_info in schema['properties'].items():
                        required = param_name in schema.get('required', [])
                        marker = "*" if required else " "
                        print(f"     {marker} {param_name}: {param_info.get('description', '无')}")
        
        print("\n" + "=" * 50)


async def main():
    """CLI Host 演示"""
    print("🤖 YM-CODE MCP CLI Host\n")
    
    host = CLIHost()
    
    # 初始化
    print("正在初始化 MCP Host...")
    await host.initialize()
    
    # 显示状态
    host.show_status()
    
    # 交互式连接
    await host.interactive_connect()
    
    # 列出工具
    await host.list_tools_interactive()
    
    # 断开连接
    await host.disconnect_all()
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())
