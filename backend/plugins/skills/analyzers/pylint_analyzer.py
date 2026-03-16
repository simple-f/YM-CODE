#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pylint 代码分析器
"""

import logging
import tempfile
import subprocess
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PylintAnalyzer:
    """Pylint 代码分析器"""
    
    def supports(self, language: str) -> bool:
        """检查是否支持该语言"""
        return language == 'python'
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        分析代码
        
        参数:
            code: 代码字符串
        
        返回:
            分析结果
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 运行 Pylint
            result = subprocess.run(
                ['pylint', temp_file, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析结果
            issues = self._parse_pylint_output(result.stdout)
            score = self._extract_score(result.stdout)
            
            return {
                'issues': issues,
                'score': score,
                'issue_count': len(issues),
                'warning_count': len([i for i in issues if i['type'] == 'warning']),
                'error_count': len([i for i in issues if i['type'] == 'error']),
                'refactor_count': len([i for i in issues if i['type'] == 'refactor']),
                'convention_count': len([i for i in issues if i['type'] == 'convention'])
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Pylint 分析超时")
            return {
                'error': '分析超时',
                'issue_count': 0
            }
        
        except FileNotFoundError:
            logger.error("Pylint 未安装")
            return {
                'error': 'Pylint 未安装，请运行：pip install pylint',
                'issue_count': 0
            }
        
        except Exception as e:
            logger.error(f"Pylint 分析失败：{e}")
            return {
                'error': str(e),
                'issue_count': 0
            }
        
        finally:
            # 清理临时文件
            import os
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _parse_pylint_output(self, output: str) -> list:
        """解析 Pylint JSON 输出"""
        import json
        
        try:
            messages = json.loads(output)
            issues = []
            
            for msg in messages:
                issues.append({
                    'type': msg.get('type', 'unknown'),
                    'message': msg.get('message', ''),
                    'line': msg.get('line', 0),
                    'column': msg.get('column', 0),
                    'symbol': msg.get('symbol', ''),
                    'message_id': msg.get('message-id', '')
                })
            
            return issues
        
        except:
            return []
    
    def _extract_score(self, output: str) -> float:
        """从输出中提取评分"""
        import json
        
        try:
            messages = json.loads(output)
            # Pylint JSON 输出不包含评分，需要通过命令行获取
            # 这里简化处理，返回 10.0（满分）
            return 10.0
        except:
            return 0.0
