#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Tests - CLI 测试
"""

import pytest
from ymcode.cli import YMCodeCLI


class TestYMCodeCLI:
    """CLI 测试"""
    
    def test_init(self):
        """测试初始化"""
        cli = YMCodeCLI()
        assert cli is not None
        assert cli.agent is None
        assert cli.running is False
    
    @pytest.mark.asyncio
    async def test_help_command(self):
        """测试 help 命令"""
        cli = YMCodeCLI()
        # 应该不抛出异常
        cli.show_help()
    
    def test_banner(self):
        """测试横幅显示"""
        cli = YMCodeCLI()
        # 应该不抛出异常
        cli.show_banner()
