#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner Tests - 测试运行器测试
"""

import pytest
from ymcode.tools.test_runner import TestRunner, RunTestTool


class TestTestRunner:
    """测试运行器测试"""
    
    @pytest.mark.asyncio
    async def test_run_pytest(self, tmp_path):
        """测试运行 pytest"""
        # 创建测试文件
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("""
def test_pass():
    assert True

def test_fail():
    assert False
""")
        
        runner = TestRunner()
        result = await runner.run_tests(str(tmp_path), framework="pytest")
        
        assert isinstance(result.passed, bool)
        assert result.total >= 2
    
    @pytest.mark.asyncio
    async def test_run_unittest(self, tmp_path):
        """测试运行 unittest"""
        # 创建测试文件
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("""
import unittest

class TestSample(unittest.TestCase):
    def test_pass(self):
        self.assertTrue(True)
    
    def test_fail(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
""")
        
        runner = TestRunner()
        result = await runner.run_tests(str(tmp_path), framework="unittest")
        
        assert isinstance(result.passed, bool)
    
    def test_generate_report(self):
        """测试生成报告"""
        from ymcode.tools.test_runner import TestResult
        
        runner = TestRunner()
        result = TestResult(
            passed=True,
            total=10,
            failures=0,
            errors=0,
            duration=1.23
        )
        
        report = runner.generate_report(result)
        
        assert "✅ 通过" in report
        assert "10" in report


class TestRunTestTool:
    """运行测试工具测试"""
    
    @pytest.mark.asyncio
    async def test_execute(self, tmp_path):
        """测试执行"""
        # 创建测试文件
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("def test_pass(): assert True")
        
        tool = RunTestTool()
        result = await tool.execute(test_path=str(tmp_path))
        
        assert isinstance(result, str)
        assert "测试报告" in result or "Test report" in result
