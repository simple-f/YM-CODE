#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search Skill - 搜索技能

支持多种搜索源：Web、文件、代码等
"""

import logging
from typing import Dict, Any, List, Optional
import re

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SearchSkill(BaseSkill):
    """搜索技能"""
    
    def __init__(self):
        """初始化搜索技能"""
        super().__init__('search')
        self.search_engines = {
            'web': self._search_web,
            'file': self._search_file,
            'code': self._search_code,
        }
    
    @property
    def description(self) -> str:
        return "搜索技能 - 支持 Web、文件、代码搜索"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "source": {
                    "type": "string",
                    "enum": ["web", "file", "code"],
                    "description": "搜索源"
                },
                "path": {
                    "type": "string",
                    "description": "搜索路径（文件/代码搜索用）"
                },
                "limit": {
                    "type": "integer",
                    "description": "结果数量限制",
                    "default": 10
                }
            },
            "required": ["query", "source"]
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """
        执行搜索
        
        参数:
            arguments: 输入参数
        
        返回:
            搜索结果
        """
        query = arguments.get('query', '')
        source = arguments.get('source', 'web')
        path = arguments.get('path', '.')
        limit = arguments.get('limit', 10)
        
        if not query:
            return {"error": "搜索关键词不能为空"}
        
        search_func = self.search_engines.get(source)
        if not search_func:
            return {"error": f"不支持的搜索源：{source}"}
        
        logger.info(f"搜索：{query} (source={source})")
        
        try:
            results = await search_func(query, path, limit)
            return {
                "success": True,
                "query": query,
                "source": source,
                "count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"搜索失败：{e}")
            return {"error": str(e)}
    
    async def _search_web(self, query: str, path: str, limit: int) -> List[Dict]:
        """Web 搜索"""
        # TODO: 集成实际的搜索引擎 API
        results = []
        
        # 模拟结果
        for i in range(min(limit, 5)):
            results.append({
                "title": f"搜索结果 {i+1}: {query}",
                "url": f"https://example.com/result/{i}",
                "snippet": f"这是关于 '{query}' 的搜索结果..."
            })
        
        return results
    
    async def _search_file(self, query: str, path: str, limit: int) -> List[Dict]:
        """文件搜索"""
        import os
        from pathlib import Path
        
        results = []
        search_path = Path(path)
        
        if not search_path.exists():
            return results
        
        # 简单文件名匹配
        for file_path in search_path.rglob(f'*{query}*'):
            if file_path.is_file():
                results.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def _search_code(self, query: str, path: str, limit: int) -> List[Dict]:
        """代码搜索（支持正则）"""
        import os
        from pathlib import Path
        
        results = []
        search_path = Path(path)
        
        if not search_path.exists():
            return results
        
        # 代码文件扩展名
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h'}
        
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error:
            # 如果不是有效正则，使用普通字符串匹配
            pattern = None
        
        for file_path in search_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        if pattern:
                            matches = pattern.findall(content)
                        else:
                            # 简单字符串匹配
                            if query.lower() in content.lower():
                                matches = [query]
                            else:
                                matches = []
                        
                        if matches:
                            # 获取匹配的行
                            lines = content.split('\n')
                            match_lines = []
                            for i, line in enumerate(lines):
                                if (pattern and pattern.search(line)) or \
                                   (not pattern and query.lower() in line.lower()):
                                    match_lines.append({
                                        "line": i + 1,
                                        "content": line.strip()[:100]
                                    })
                            
                            results.append({
                                "file": str(file_path),
                                "matches": len(match_lines),
                                "preview": match_lines[:3]
                            })
                            
                            if len(results) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"读取文件失败 {file_path}: {e}")
        
        return results
