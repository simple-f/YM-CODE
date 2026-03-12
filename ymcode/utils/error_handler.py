#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handler - 错误处理系统

融合课程：生产级错误处理 + 友好提示
"""

from typing import Dict, Optional
from enum import Enum
from rich.console import Console
from rich.panel import Panel

console = Console()


class ErrorType(Enum):
    """错误类型"""
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_ARGUMENT = "invalid_argument"
    COMMAND_FAILED = "command_failed"
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    UNKNOWN = "unknown"


class ErrorHandler:
    """错误处理器"""
    
    # 错误类型识别规则
    ERROR_PATTERNS = {
        ErrorType.FILE_NOT_FOUND: [
            "No such file or directory",
            "文件不存在",
            "找不到文件"
        ],
        ErrorType.PERMISSION_DENIED: [
            "Permission denied",
            "权限被拒绝",
            "访问被拒绝"
        ],
        ErrorType.INVALID_ARGUMENT: [
            "Invalid argument",
            "无效参数",
            "参数错误"
        ],
        ErrorType.COMMAND_FAILED: [
            "Command failed",
            "命令执行失败",
            "返回码非零"
        ],
        ErrorType.NETWORK_ERROR: [
            "Network is unreachable",
            "Connection refused",
            "网络不可达"
        ],
        ErrorType.API_ERROR: [
            "API error",
            "API 错误",
            "请求失败"
        ]
    }
    
    # 友好提示模板
    FRIENDLY_MESSAGES = {
        ErrorType.FILE_NOT_FOUND: """
📁 **文件未找到**

找不到指定的文件，请检查：
- 文件路径是否正确
- 文件是否已被删除或移动
- 当前工作目录是否正确

**建议操作：**
1. 使用 `list_dir` 查看当前目录
2. 使用绝对路径而非相对路径
3. 确认文件确实存在
""",
        
        ErrorType.PERMISSION_DENIED: """
🔒 **权限被拒绝**

没有权限执行此操作，请检查：
- 文件/目录权限设置
- 是否需要 sudo/admin 权限
- 是否在正确的用户上下文中

**建议操作：**
1. 检查文件权限：`ls -la <文件>`
2. 修改权限：`chmod +x <文件>`
3. 使用管理员权限运行
""",
        
        ErrorType.INVALID_ARGUMENT: """
❌ **参数错误**

提供的参数无效，请检查：
- 参数类型是否正确
- 参数值是否在有效范围内
- 必需参数是否都已提供

**建议操作：**
1. 查看工具文档确认参数要求
2. 检查参数类型和格式
3. 提供完整的必需参数
""",
        
        ErrorType.COMMAND_FAILED: """
💥 **命令执行失败**

命令执行失败，可能的原因：
- 命令本身有错误
- 缺少依赖项
- 环境变量未配置

**建议操作：**
1. 检查命令语法是否正确
2. 确认依赖已安装
3. 查看详细错误信息
""",
        
        ErrorType.NETWORK_ERROR: """
🌐 **网络错误**

网络连接失败，请检查：
- 网络连接是否正常
- 目标服务是否可用
- 防火墙/代理设置

**建议操作：**
1. 测试网络连接：`ping <目标>`
2. 检查代理设置
3. 稍后重试
""",
        
        ErrorType.API_ERROR: """
🔌 **API 错误**

API 调用失败，可能的原因：
- API Key 无效或过期
- 请求频率超限
- 服务端点错误

**建议操作：**
1. 检查 API Key 配置
2. 查看 API 文档确认端点
3. 检查请求频率限制
""",
        
        ErrorType.UNKNOWN: """
❓ **未知错误**

发生未知错误，请提供以下信息：
- 完整的错误信息
- 执行的操作步骤
- 环境信息

**建议操作：**
1. 查看详细日志
2. 重试操作
3. 如持续失败，请报告问题
"""
    }
    
    @classmethod
    def identify_error(cls, error_message: str) -> ErrorType:
        """
        识别错误类型
        
        参数:
            error_message: 错误信息
        
        返回:
            错误类型
        """
        for error_type, patterns in cls.ERROR_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in error_message.lower():
                    return error_type
        
        return ErrorType.UNKNOWN
    
    @classmethod
    def get_friendly_message(cls, error_type: ErrorType) -> str:
        """
        获取友好提示
        
        参数:
            error_type: 错误类型
        
        返回:
            友好提示信息
        """
        return cls.FRIENDLY_MESSAGES.get(error_type, cls.FRIENDLY_MESSAGES[ErrorType.UNKNOWN])
    
    @classmethod
    def handle_error(cls, error: Exception, show_panel: bool = True) -> str:
        """
        处理错误
        
        参数:
            error: 异常对象
            show_panel: 是否显示面板
        
        返回:
            处理后的错误信息
        """
        error_message = str(error)
        error_type = cls.identify_error(error_message)
        friendly_message = cls.get_friendly_message(error_type)
        
        if show_panel:
            # 显示友好提示面板
            console.print(Panel(
                friendly_message,
                title="❌ 错误提示",
                style="red"
            ))
        
        # 返回原始错误信息（用于日志）
        return f"[{error_type.value}] {error_message}"
    
    @classmethod
    def create_suggestion(cls, error_type: ErrorType, context: Dict = None) -> Dict:
        """
        创建错误建议
        
        参数:
            error_type: 错误类型
            context: 上下文信息
        
        返回:
            建议字典
        """
        suggestions = {
            ErrorType.FILE_NOT_FOUND: [
                {"action": "check_path", "description": "检查文件路径"},
                {"action": "list_directory", "description": "列出目录内容"},
                {"action": "use_absolute_path", "description": "使用绝对路径"}
            ],
            ErrorType.PERMISSION_DENIED: [
                {"action": "check_permissions", "description": "检查文件权限"},
                {"action": "run_as_admin", "description": "以管理员身份运行"},
                {"action": "change_permissions", "description": "修改文件权限"}
            ],
            ErrorType.INVALID_ARGUMENT: [
                {"action": "check_documentation", "description": "查看文档"},
                {"action": "validate_parameters", "description": "验证参数"},
                {"action": "check_types", "description": "检查类型"}
            ]
        }
        
        return {
            "error_type": error_type.value,
            "suggestions": suggestions.get(error_type, []),
            "context": context or {}
        }


def friendly_error(show_panel: bool = True):
    """
    友好错误装饰器
    
    参数:
        show_panel: 是否显示面板
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_error(e, show_panel)
                raise
        return wrapper
    return decorator
