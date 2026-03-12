#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regex Edit Tool - 正则表达式编辑工具

融合课程：s02 (Tool Use) + 生产级正则编辑
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from .base import BaseTool


class RegexReplaceTool(BaseTool):
    """正则表达式替换工具"""
    
    name = "regex_replace"
    description = "使用正则表达式替换文件内容（支持复杂模式匹配）"
    
    async def execute(
        self,
        path: str,
        pattern: str,
        replacement: str,
        count: int = 0,
        flags: str = ""
    ) -> str:
        """
        正则表达式替换
        
        参数:
            path: 文件路径
            pattern: 正则表达式模式
            replacement: 替换文本（支持反向引用）
            count: 替换次数（0=全部）
            flags: 正则标志（i=忽略大小写，m=多行，s=单行）
        
        返回:
            替换结果
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            # 读取文件
            content = file_path.read_text(encoding='utf-8')
            
            # 编译正则标志
            re_flags = 0
            if 'i' in flags.lower():
                re_flags |= re.IGNORECASE
            if 'm' in flags.lower():
                re_flags |= re.MULTILINE
            if 's' in flags.lower():
                re_flags |= re.DOTALL
            
            # 编译正则
            try:
                compiled_pattern = re.compile(pattern, re_flags)
            except re.error as e:
                return f"错误：正则表达式无效 {e}"
            
            # 查找匹配
            matches = list(compiled_pattern.finditer(content))
            
            if not matches:
                return f"警告：未找到匹配的模式"
            
            # 显示匹配结果
            match_info = f"找到 {len(matches)} 处匹配：\n\n"
            for i, match in enumerate(matches[:5], 1):  # 只显示前 5 个
                match_info += f"{i}. 位置 {match.start()}-{match.end()}: `{match.group()[:50]}...`\n"
            
            if len(matches) > 5:
                match_info += f"... 还有 {len(matches) - 5} 处匹配\n"
            
            # 执行替换
            if count > 0:
                new_content = compiled_pattern.sub(replacement, content, count=count)
            else:
                new_content = compiled_pattern.sub(replacement, content)
            
            # 写回文件
            file_path.write_text(new_content, encoding='utf-8')
            
            # 生成摘要
            diff_lines = new_content.count('\n') - content.count('\n')
            
            return f"✓ 正则替换完成：{path}\n\n{match_info}\n替换了 {len(matches)} 处，文件变化 {diff_lines:+d} 行"
            
        except Exception as e:
            return f"替换失败：{e}"
    
    def get_input_schema(self) -> Dict:
        """获取输入 schema"""
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "pattern": {
                    "type": "string",
                    "description": "正则表达式模式"
                },
                "replacement": {
                    "type": "string",
                    "description": "替换文本（支持 \\1, \\2 等反向引用）"
                },
                "count": {
                    "type": "integer",
                    "description": "替换次数（0=全部替换）",
                    "default": 0
                },
                "flags": {
                    "type": "string",
                    "description": "正则标志（i=忽略大小写，m=多行，s=单行）",
                    "default": ""
                }
            },
            "required": ["path", "pattern", "replacement"]
        }


class RegexSearchTool(BaseTool):
    """正则表达式搜索工具"""
    
    name = "regex_search"
    description = "使用正则表达式搜索文件内容"
    
    async def execute(
        self,
        path: str,
        pattern: str,
        flags: str = "",
        context_lines: int = 2
    ) -> str:
        """
        正则表达式搜索
        
        参数:
            path: 文件路径
            pattern: 正则表达式模式
            flags: 正则标志
            context_lines: 上下文行数
        
        返回:
            搜索结果
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return f"错误：文件不存在 {path}"
            
            # 读取文件
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # 编译正则标志
            re_flags = 0
            if 'i' in flags.lower():
                re_flags |= re.IGNORECASE
            if 'm' in flags.lower():
                re_flags |= re.MULTILINE
            
            # 编译正则
            try:
                compiled_pattern = re.compile(pattern, re_flags)
            except re.error as e:
                return f"错误：正则表达式无效 {e}"
            
            # 查找匹配
            results = []
            for line_num, line in enumerate(lines, 1):
                matches = compiled_pattern.finditer(line)
                for match in matches:
                    # 获取上下文
                    start_line = max(1, line_num - context_lines)
                    end_line = min(len(lines), line_num + context_lines)
                    context = lines[start_line - 1:end_line]
                    
                    results.append({
                        "line": line_num,
                        "column": match.start() + 1,
                        "match": match.group(),
                        "context": context
                    })
            
            if not results:
                return f"未找到匹配"
            
            # 生成报告
            report = f"## 正则搜索结果：{path}\n\n"
            report += f"模式：`{pattern}`\n"
            report += f"找到 {len(results)} 处匹配：\n\n"
            
            for i, result in enumerate(results[:10], 1):  # 只显示前 10 个
                report += f"### {i}. 第 {result['line']} 行，列 {result['column']}\n\n"
                report += f"**匹配**: `{result['match'][:100]}`\n\n"
                report += "**上下文**:\n```\n"
                report += "\n".join(result['context'])
                report += "\n```\n\n"
            
            if len(results) > 10:
                report += f"... 还有 {len(results) - 10} 处匹配\n"
            
            return report
            
        except Exception as e:
            return f"搜索失败：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "pattern": {
                    "type": "string",
                    "description": "正则表达式模式"
                },
                "flags": {
                    "type": "string",
                    "description": "正则标志",
                    "default": ""
                },
                "context_lines": {
                    "type": "integer",
                    "description": "上下文行数",
                    "default": 2
                }
            },
            "required": ["path", "pattern"]
        }


class RegexValidateTool(BaseTool):
    """正则表达式验证工具"""
    
    name = "regex_validate"
    description = "验证正则表达式是否有效"
    
    async def execute(self, pattern: str, test_text: str = "", flags: str = "") -> str:
        """
        验证正则表达式
        
        参数:
            pattern: 正则表达式
            test_text: 测试文本（可选）
            flags: 正则标志
        
        返回:
            验证结果
        """
        try:
            # 编译正则标志
            re_flags = 0
            if 'i' in flags.lower():
                re_flags |= re.IGNORECASE
            if 'm' in flags.lower():
                re_flags |= re.MULTILINE
            if 's' in flags.lower():
                re_flags |= re.DOTALL
            
            # 尝试编译
            compiled = re.compile(pattern, re_flags)
            
            result = f"✅ 正则表达式有效\n\n"
            result += f"**模式**: `{pattern}`\n"
            result += f"**标志**: {flags or '无'}\n"
            
            # 如果有测试文本，显示匹配结果
            if test_text:
                matches = list(compiled.finditer(test_text))
                if matches:
                    result += f"\n**测试文本匹配结果** ({len(matches)} 处):\n\n"
                    for i, match in enumerate(matches[:5], 1):
                        result += f"{i}. `{match.group()}` (位置 {match.start()}-{match.end()})\n"
                else:
                    result += f"\n**测试文本**: 无匹配\n"
            
            return result
            
        except re.error as e:
            return f"❌ 正则表达式无效\n\n错误：{e}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "正则表达式"
                },
                "test_text": {
                    "type": "string",
                    "description": "测试文本（可选）"
                },
                "flags": {
                    "type": "string",
                    "description": "正则标志",
                    "default": ""
                }
            },
            "required": ["pattern"]
        }
