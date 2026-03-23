#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由模块

基于任务内容、Agent 能力和历史准确率，自动选择最优 Agent
"""

from .smart_router import SmartRouter, RouteResult
from .routing_rules import ROUTING_RULES, KEYWORD_MAP

__all__ = ["SmartRouter", "RouteResult", "ROUTING_RULES", "KEYWORD_MAP"]
