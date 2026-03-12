#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner - 测试运行器

融合课程：s08 (Background Tasks) + 生产级测试
"""

import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from .base import BaseTool


@dataclass
class TestResult:
    """测试结果"""
    passed: bool
    total: int = 0
    failures: int = 0
    errors: int = 0
    output: str = ""
    duration: float = 0.0


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.supported_frameworks = ["pytest", "unittest", "nose"]
    
    async def run_tests(
        self,
        test_path: str = ".",
        framework: str = "pytest",
        verbose: bool = True
    ) -> TestResult:
        """
        运行测试
        
        参数:
            test_path: 测试路径
            framework: 测试框架
            verbose: 是否详细输出
        
        返回:
            测试结果
        """
        if framework == "pytest":
            return await self._run_pytest(test_path, verbose)
        elif framework == "unittest":
            return await self._run_unittest(test_path, verbose)
        else:
            return TestResult(
                passed=False,
                output=f"不支持的测试框架：{framework}"
            )
    
    async def _run_pytest(self, test_path: str, verbose: bool) -> TestResult:
        """
        运行 pytest
        
        参数:
            test_path: 测试路径
            verbose: 是否详细输出
        """
        import time
        start_time = time.time()
        
        args = ["pytest"]
        
        if verbose:
            args.append("-v")
        
        args.append(test_path)
        
        try:
            result = await asyncio.create_subprocess_exec(
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            duration = time.time() - start_time
            
            # 解析输出
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            
            # 解析测试结果
            total, failures, errors = self._parse_pytest_output(output)
            
            return TestResult(
                passed=result.returncode == 0,
                total=total,
                failures=failures,
                errors=errors,
                output=output + error_output,
                duration=duration
            )
            
        except Exception as e:
            return TestResult(
                passed=False,
                output=f"测试运行失败：{e}"
            )
    
    async def _run_unittest(self, test_path: str, verbose: bool) -> TestResult:
        """
        运行 unittest
        
        参数:
            test_path: 测试路径
            verbose: 是否详细输出
        """
        import time
        start_time = time.time()
        
        args = ["python", "-m", "unittest", "discover"]
        
        if verbose:
            args.append("-v")
        
        args.append("-s")
        args.append(test_path)
        
        try:
            result = await asyncio.create_subprocess_exec(
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            duration = time.time() - start_time
            
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            
            # 解析测试结果
            total, failures, errors = self._parse_unittest_output(output)
            
            return TestResult(
                passed=result.returncode == 0,
                total=total,
                failures=failures,
                errors=errors,
                output=output + error_output,
                duration=duration
            )
            
        except Exception as e:
            return TestResult(
                passed=False,
                output=f"测试运行失败：{e}"
            )
    
    def _parse_pytest_output(self, output: str) -> tuple:
        """
        解析 pytest 输出
        
        参数:
            output: pytest 输出
        
        返回:
            (total, failures, errors)
        """
        total = failures = errors = 0
        
        # 查找测试总结行
        for line in output.split('\n'):
            if 'passed' in line or 'failed' in line:
                # 示例：=== 10 passed, 2 failed in 1.23s ===
                if 'passed' in line:
                    try:
                        total += int(line.split('passed')[0].split()[-1])
                    except:
                        pass
                
                if 'failed' in line:
                    try:
                        failures += int(line.split('failed')[0].split()[-1])
                    except:
                        pass
                
                if 'error' in line:
                    try:
                        errors += int(line.split('error')[0].split()[-1])
                    except:
                        pass
        
        return total, failures, errors
    
    def _parse_unittest_output(self, output: str) -> tuple:
        """
        解析 unittest 输出
        
        参数:
            output: unittest 输出
        
        返回:
            (total, failures, errors)
        """
        total = failures = errors = 0
        
        # 查找测试总结行
        for line in output.split('\n'):
            if line.startswith('Ran'):
                # 示例：Ran 10 tests in 1.234s
                try:
                    total = int(line.split()[1])
                except:
                    pass
            
            if line.startswith('FAILED'):
                failures += 1
            elif line.startswith('ERROR'):
                errors += 1
        
        return total, failures, errors
    
    def generate_report(self, result: TestResult) -> str:
        """
        生成测试报告
        
        参数:
            result: 测试结果
        
        返回:
            测试报告
        """
        status = "✅ 通过" if result.passed else "❌ 失败"
        
        report = f"""
## 测试报告

**状态**: {status}

**统计**:
- 总计：{result.total} 个测试
- 失败：{result.failures} 个
- 错误：{result.errors} 个
- 耗时：{result.duration:.2f} 秒

**输出**:
```
{result.output[:2000]}  # 限制长度
```
"""
        
        return report


class RunTestTool(BaseTool):
    """运行测试工具"""
    
    name = "run_test"
    description = "运行测试用例（支持 pytest/unittest）"
    
    async def execute(
        self,
        test_path: str = ".",
        framework: str = "pytest",
        verbose: bool = True
    ) -> str:
        """
        运行测试
        
        参数:
            test_path: 测试路径
            framework: 测试框架
            verbose: 是否详细输出
        
        返回:
            测试报告
        """
        runner = TestRunner()
        result = await runner.run_tests(test_path, framework, verbose)
        return runner.generate_report(result)
    
    def get_input_schema(self) -> Dict:
        """获取输入 schema"""
        return {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "测试路径"
                },
                "framework": {
                    "type": "string",
                    "description": "测试框架",
                    "enum": ["pytest", "unittest"]
                },
                "verbose": {
                    "type": "boolean",
                    "description": "是否详细输出"
                }
            },
            "required": ["test_path"]
        }
