#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flake8 代码检查器
"""

import logging
import tempfile
import subprocess
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class Flake8Checker:
    """Flake8 代码检查器"""
    
    def supports(self, language: str) -> bool:
        """检查是否支持该语言"""
        return language == 'python'
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        检查代码
        
        参数:
            code: 代码字符串
        
        返回:
            检查结果
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 运行 Flake8
            result = subprocess.run(
                ['flake8', temp_file, '--count', '--show-source', '--statistics'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析结果
            issues = self._parse_flake8_output(result.stdout)
            
            return {
                'issues': issues,
                'issue_count': len(issues),
                'warning_count': len([i for i in issues if i['code'].startswith('W')]),
                'error_count': len([i for i in issues if i['code'].startswith('E')]),
                'suggestions': self._generate_suggestions(issues)
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Flake8 检查超时")
            return {
                'error': '检查超时',
                'issue_count': 0
            }
        
        except FileNotFoundError:
            logger.error("Flake8 未安装")
            return {
                'error': 'Flake8 未安装，请运行：pip install flake8',
                'issue_count': 0
            }
        
        except Exception as e:
            logger.error(f"Flake8 检查失败：{e}")
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
    
    def _parse_flake8_output(self, output: str) -> list:
        """解析 Flake8 输出"""
        issues = []
        
        for line in output.split('\n'):
            if ':' in line and not line.endswith(':'):
                parts = line.split(':')
                if len(parts) >= 4:
                    issues.append({
                        'file': parts[0],
                        'line': int(parts[1]),
                        'column': int(parts[2]),
                        'code': parts[3].strip().split()[0],
                        'message': ':'.join(parts[3:]).strip()
                    })
        
        return issues
    
    def _generate_suggestions(self, issues: list) -> list:
        """生成改进建议"""
        suggestions = []
        
        # 统计问题类型
        codes = [i['code'] for i in issues]
        
        if any(c.startswith('E501') for c in codes):
            suggestions.append('存在过长的行，建议拆分（E501）')
        
        if any(c.startswith('W391') for c in codes):
            suggestions.append('文件末尾有多余空行（W391）')
        
        if any(c.startswith('F401') for c in codes):
            suggestions.append('存在未使用的导入（F401）')
        
        if not suggestions:
            suggestions.append('代码质量良好')
        
        return suggestions
