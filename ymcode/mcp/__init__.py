# MCP module - MCP 协议客户端

from .client import MCPClient, MCPTool, MCPServer
from .client_v2 import MCPClientV2
from .server_registry import MCPServerRegistry, MCPServerConfig, get_registry
from .prompts import MCPPromptTemplates, PromptTemplate, get_templates, render_template

__all__ = [
    # v1
    "MCPClient",
    "MCPTool", 
    "MCPServer",
    # v2
    "MCPClientV2",
    # Registry
    "MCPServerRegistry",
    "MCPServerConfig",
    "get_registry",
    # Prompts
    "MCPPromptTemplates",
    "PromptTemplate",
    "get_templates",
    "render_template"
]
