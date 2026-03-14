#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE CLI 主题系统
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Theme:
    """主题配置"""
    name: str
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    success_color: str
    error_color: str
    warning_color: str
    info_color: str


# YM-CODE 官方主题
THEMES: Dict[str, Theme] = {
    # 极光主题（默认）
    "aurora": Theme(
        name="aurora",
        primary_color="#8B5CF6",      # 极光紫
        secondary_color="#3B82F6",    # 电光蓝
        background_color="#0F172A",   # 深空黑
        text_color="#F8FAFC",         # 云白
        success_color="#10B981",      # 翠绿
        error_color="#EF4444",        # 鲜红
        warning_color="#F59E0B",      # 琥珀
        info_color="#60A5FA"          # 天蓝
    ),
    
    # 日间主题
    "light": Theme(
        name="light",
        primary_color="#7C3AED",
        secondary_color="#2563EB",
        background_color="#FFFFFF",
        text_color="#1F2937",
        success_color="#059669",
        error_color="#DC2626",
        warning_color="#D97706",
        info_color="#3B82F6"
    ),
    
    # 夜间主题
    "dark": Theme(
        name="dark",
        primary_color="#A78BFA",
        secondary_color="#60A5FA",
        background_color="#1F2937",
        text_color="#F9FAFB",
        success_color="#34D399",
        error_color="#F87171",
        warning_color="#FBBF24",
        info_color="#93C5FD"
    ),
    
    # 黑客帝国主题
    "matrix": Theme(
        name="matrix",
        primary_color="#00FF00",
        secondary_color="#008800",
        background_color="#000000",
        text_color="#00FF00",
        success_color="#00FF00",
        error_color="#FF0000",
        warning_color="#FFFF00",
        info_color="#00FFFF"
    ),
    
    # 赛博朋克主题
    "cyberpunk": Theme(
        name="cyberpunk",
        primary_color="#FF00FF",
        secondary_color="#00FFFF",
        background_color="#0D0221",
        text_color="#FFFFFF",
        success_color="#00FF00",
        error_color="#FF0000",
        warning_color="#FFFF00",
        info_color="#00BFFF"
    ),
}


def get_theme(name: str = "aurora") -> Theme:
    """获取主题"""
    return THEMES.get(name, THEMES["aurora"])


def list_themes() -> list:
    """列出所有主题"""
    return list(THEMES.keys())


def create_theme(name: str, colors: Dict[str, str]) -> Theme:
    """创建自定义主题"""
    theme = Theme(name=name, **colors)
    THEMES[name] = theme
    return theme
