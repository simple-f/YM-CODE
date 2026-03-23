#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由规则配置

定义关键词到 Agent 的映射关系
"""

# 关键词到 Agent 的映射
KEYWORD_MAP = {
    # 架构相关
    "架构": ["ai1", "ai6"],
    "微服务": ["ai1", "ai2"],
    "系统": ["ai1", "ai2", "ai6"],
    "技术选型": ["ai1"],  # 高优先级，只路由到架构师
    "选型": ["ai1"],
    "postgresql": ["ai2"],  # 具体技术实现归后端
    "mongodb": ["ai2"],
    "数据库": ["ai2", "ai6"],
    "sql": ["ai2"],
    "api": ["ai2", "ai4"],
    "rest api": ["ai2"],
    "jwt": ["ai2"],
    "oauth": ["ai2"],
    "redis": ["ai2"],
    "缓存": ["ai2"],
    "后端": ["ai2", "ai4"],
    "性能瓶颈": ["ai2", "ai6"],
    "性能优化": ["ai2", "ai6"],
    
    # 前端相关
    "前端": ["ai3", "ai4"],
    "ui": ["ai3", "ai7"],
    "ux": ["ai3", "ai7"],
    "界面": ["ai3"],
    "交互": ["ai3", "ai7"],
    "react": ["ai3"],
    "vue": ["ai3"],
    "vue3": ["ai3"],  # 高优先级
    "typescript": ["ai3", "ai2"],
    "css": ["ai3"],
    "html": ["ai3"],
    "移动端": ["ai3"],
    "适配": ["ai3"],
    "组件": ["ai3"],
    
    # 全栈相关
    "全栈": ["ai4"],
    "集成": ["ai4"],
    "部署": ["ai4"],
    "devops": ["ai4"],
    "ci/cd": ["ai4"],
    
    # 测试相关
    "测试": ["ai5"],
    "review": ["ai5", "ai6"],
    "审查": ["ai5"],
    "质量": ["ai5"],
    "bug": ["ai4", "ai5"],  # bug 修复优先全栈
    "调试": ["ai4", "ai5"],
    "单元测试": ["ai5"],
    "代码审查": ["ai5"],
    "覆盖率": ["ai5"],
    
    # 产品相关
    "产品": ["ai7"],
    "需求": ["ai7", "ai1"],
    "用户": ["ai7", "ai3"],
    "体验": ["ai7", "ai3"],
    "功能": ["ai7", "ai1"],
    
    # 咨询相关
    "咨询": ["ai6", "ai7"],
    "建议": ["ai6", "ai7"],
    "最佳实践": ["ai6"],
    "方案": ["ai1", "ai6"],
    "技术债务": ["ai6"],
    "技术趋势": ["ai6"],
    "债务": ["ai6"],
    "趋势": ["ai6"],
}

# 路由规则
ROUTING_RULES = {
    # 默认路由（无匹配时使用）
    "default": ["ai4"],  # 全栈开发作为默认
    
    # 高优先级规则（精确匹配）
    "high_priority": {
        "审查代码": ["ai5"],
        "代码审查": ["ai5"],
        "架构设计": ["ai1"],
        "技术方案": ["ai1"],
        "产品设计": ["ai7"],
        "技术选型": ["ai1"],  # 技术选型优先架构师
        "选型建议": ["ai1"],
        "认证系统": ["ai2"],
        "缓存策略": ["ai2"],
        "单元测试": ["ai5"],
        "vue3": ["ai3"],
        "移动端适配": ["ai3"],
        "性能瓶颈": ["ai6"],
        "性能分析": ["ai6"],
    },
    
    # Agent 能力配置
    "agent_capabilities": {
        "ai1": {
            "name": "架构师",
            "role": "system",
            "strengths": ["系统架构", "技术选型", "方案设计"],
            "max_context": 8000,
            "target_response_time": 5,
            "model": "qwen3.5-plus"
        },
        "ai2": {
            "name": "后端开发",
            "role": "developer",
            "strengths": ["API 开发", "数据库", "性能优化"],
            "max_context": 6000,
            "target_response_time": 3,
            "model": "qwen3-coder-plus"
        },
        "ai3": {
            "name": "前端开发",
            "role": "developer",
            "strengths": ["UI 开发", "交互设计", "前端优化"],
            "max_context": 6000,
            "target_response_time": 3,
            "model": "qwen3-coder-next"
        },
        "ai4": {
            "name": "全栈开发",
            "role": "developer",
            "strengths": ["全栈开发", "集成", "快速原型"],
            "max_context": 6000,
            "target_response_time": 3,
            "model": "glm-5"
        },
        "ai5": {
            "name": "测试工程师",
            "role": "reviewer",
            "strengths": ["代码审查", "测试", "质量保证"],
            "max_context": 8000,
            "target_response_time": 4,
            "model": "kimi-k2.5"
        },
        "ai6": {
            "name": "技术顾问",
            "role": "advisor",
            "strengths": ["技术咨询", "最佳实践", "方案评审"],
            "max_context": 8000,
            "target_response_time": 5,
            "model": "qwen3-max-2026-01-23"
        },
        "ai7": {
            "name": "产品顾问",
            "role": "advisor",
            "strengths": ["产品设计", "用户体验", "需求分析"],
            "max_context": 8000,
            "target_response_time": 4,
            "model": "MiniMax-M2.5"
        }
    }
}
