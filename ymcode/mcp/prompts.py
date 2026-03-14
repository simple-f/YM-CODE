#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Prompt 模板
提供 MCP 工具使用的 Prompt 模板
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    name: str
    description: str
    template: str
    variables: List[str] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []
    
    def render(self, **kwargs) -> str:
        """
        渲染模板
        
        参数:
            **kwargs: 模板变量
        
        返回:
            渲染后的文本
        """
        result = self.template
        
        for var in self.variables:
            value = kwargs.get(var, f"{{{var}}}")
            result = result.replace(f"{{{var}}}", str(value))
        
        return result


class MCPPromptTemplates:
    """MCP Prompt 模板集合"""
    
    def __init__(self):
        """初始化模板集合"""
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_builtin_templates()
        
        logger.info(f"MCP Prompt 模板初始化完成，共 {len(self.templates)} 个模板")
    
    def _load_builtin_templates(self) -> None:
        """加载内置模板"""
        
        # 工具调用模板
        self.templates['tool_call'] = PromptTemplate(
            name="tool_call",
            description="调用 MCP 工具的 Prompt 模板",
            template="""我将使用以下工具来完成任务：

工具名称：{tool_name}
工具描述：{tool_description}
工具参数：{tool_arguments}

请按照以下步骤执行：
1. 验证参数的正确性
2. 调用工具
3. 解析返回结果
4. 如有错误，提供清晰的错误信息

执行结果：""",
            variables=["tool_name", "tool_description", "tool_arguments"]
        )
        
        # 工具发现模板
        self.templates['tool_discovery'] = PromptTemplate(
            name="tool_discovery",
            description="发现和注册 MCP 工具的 Prompt 模板",
            template="""我已连接到 MCP 服务器：{server_name}

可用的工具列表：
{tools_list}

这些工具可以用于：
{tools_capabilities}

请在后续对话中记住这些工具，并在需要时主动推荐使用。""",
            variables=["server_name", "tools_list", "tools_capabilities"]
        )
        
        # 资源访问模板
        self.templates['resource_access'] = PromptTemplate(
            name="resource_access",
            description="访问 MCP 资源的 Prompt 模板",
            template="""我将访问以下 MCP 资源：

资源 URI: {resource_uri}
资源类型：{resource_type}
资源描述：{resource_description}

请读取该资源的内容并提供给用户。""",
            variables=["resource_uri", "resource_type", "resource_description"]
        )
        
        # 错误处理模板
        self.templates['error_handling'] = PromptTemplate(
            name="error_handling",
            description="MCP 工具调用错误处理模板",
            template="""工具调用失败：

工具名称：{tool_name}
错误信息：{error_message}
错误类型：{error_type}

可能的原因：
1. {possible_cause_1}
2. {possible_cause_2}
3. {possible_cause_3}

建议的解决方案：
{suggested_solution}""",
            variables=["tool_name", "error_message", "error_type", 
                      "possible_cause_1", "possible_cause_2", "possible_cause_3", 
                      "suggested_solution"]
        )
        
        # 多服务器协调模板
        self.templates['multi_server'] = PromptTemplate(
            name="multi_server",
            description="多 MCP 服务器协调模板",
            template="""我已连接到多个 MCP 服务器：

{server_status}

当前任务需要跨服务器协作：
{task_description}

请协调以下服务器完成：
{required_servers}

执行计划：
{execution_plan}""",
            variables=["server_status", "task_description", "required_servers", "execution_plan"]
        )
        
        # 工具链模板
        self.templates['tool_chain'] = PromptTemplate(
            name="tool_chain",
            description="工具链调用模板",
            template="""我将执行一个工具链：

步骤 1: {step1_tool} - {step1_description}
步骤 2: {step2_tool} - {step2_description}
步骤 3: {step3_tool} - {step3_description}

每个步骤的输出将作为下一步的输入。

开始执行...""",
            variables=["step1_tool", "step1_description", "step2_tool", "step2_description", 
                      "step3_tool", "step3_description"]
        )
        
        # 上下文增强模板
        self.templates['context_enhance'] = PromptTemplate(
            name="context_enhance",
            description="使用 MCP 资源增强上下文的模板",
            template="""为了更好理解当前任务，我已加载以下上下文信息：

来源：{context_source}
类型：{context_type}
内容摘要：
{context_summary}

请结合这些上下文信息来回答用户的问题。""",
            variables=["context_source", "context_type", "context_summary"]
        )
        
        # 权限请求模板
        self.templates['permission_request'] = PromptTemplate(
            name="permission_request",
            description="请求用户授权执行敏感操作",
            template="""即将执行需要授权的操作：

操作：{operation}
目标：{target}
原因：{reason}
风险等级：{risk_level}

请确认是否继续？(是/否)""",
            variables=["operation", "target", "reason", "risk_level"]
        )
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取模板
        
        参数:
            name: 模板名称
        
        返回:
            模板对象，不存在返回 None
        """
        return self.templates.get(name)
    
    def add_template(self, template: PromptTemplate) -> None:
        """
        添加自定义模板
        
        参数:
            template: 模板对象
        """
        self.templates[template.name] = template
        logger.info(f"添加自定义模板：{template.name}")
    
    def list_templates(self) -> List[str]:
        """
        列出所有模板名称
        
        返回:
            模板名称列表
        """
        return list(self.templates.keys())
    
    def render(self, name: str, **kwargs) -> str:
        """
        获取并渲染模板
        
        参数:
            name: 模板名称
            **kwargs: 模板变量
        
        返回:
            渲染后的文本
        """
        template = self.get_template(name)
        if not template:
            logger.warning(f"模板不存在：{name}")
            return ""
        
        return template.render(**kwargs)


# 全局模板实例
_templates: Optional[MCPPromptTemplates] = None


def get_templates() -> MCPPromptTemplates:
    """获取全局模板实例"""
    global _templates
    if _templates is None:
        _templates = MCPPromptTemplates()
    return _templates


def render_template(name: str, **kwargs) -> str:
    """便捷函数：获取并渲染模板"""
    return get_templates().render(name, **kwargs)
