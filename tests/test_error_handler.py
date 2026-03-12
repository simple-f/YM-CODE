#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handler Tests - 错误处理测试
"""

import pytest
from ymcode.utils.error_handler import ErrorHandler, ErrorType, friendly_error


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_identify_file_not_found(self):
        """测试文件未找到识别"""
        error_msg = "No such file or directory: /path/to/file"
        error_type = ErrorHandler.identify_error(error_msg)
        assert error_type == ErrorType.FILE_NOT_FOUND
    
    def test_identify_permission_denied(self):
        """测试权限拒绝识别"""
        error_msg = "Permission denied: /path/to/file"
        error_type = ErrorHandler.identify_error(error_msg)
        assert error_type == ErrorType.PERMISSION_DENIED
    
    def test_identify_unknown(self):
        """测试未知错误识别"""
        error_msg = "Some unknown error occurred"
        error_type = ErrorHandler.identify_error(error_msg)
        assert error_type == ErrorType.UNKNOWN
    
    def test_get_friendly_message(self):
        """测试获取友好提示"""
        friendly_msg = ErrorHandler.get_friendly_message(ErrorType.FILE_NOT_FOUND)
        assert "文件未找到" in friendly_msg
        assert "建议操作" in friendly_msg
    
    def test_handle_error(self):
        """测试错误处理"""
        error = FileNotFoundError("No such file or directory")
        result = ErrorHandler.handle_error(error, show_panel=False)
        assert "[file_not_found]" in result
    
    def test_create_suggestion(self):
        """测试创建建议"""
        suggestion = ErrorHandler.create_suggestion(ErrorType.FILE_NOT_FOUND)
        assert "error_type" in suggestion
        assert "suggestions" in suggestion
        assert len(suggestion["suggestions"]) > 0


class TestFriendlyErrorDecorator:
    """友好错误装饰器测试"""
    
    def test_decorator_catches_error(self):
        """测试装饰器捕获错误"""
        @friendly_error(show_panel=False)
        def failing_function():
            raise FileNotFoundError("No such file")
        
        with pytest.raises(FileNotFoundError):
            failing_function()
    
    def test_decorator_allows_success(self):
        """测试装饰器允许成功"""
        @friendly_error(show_panel=False)
        def success_function():
            return "success"
        
        result = success_function()
        assert result == "success"
