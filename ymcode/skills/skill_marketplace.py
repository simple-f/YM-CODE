#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 市场 - 浏览、下载、安装 Skills
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
import httpx

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


# 默认 Skills 市场
DEFAULT_MARKETPLACE_URL = "https://clawhub.ai"
SKILLS_API = "/api/v1/skills"


class SkillMarketplace(BaseSkill):
    """Skills 市场技能"""
    
    def __init__(self):
        """初始化 Skills 市场"""
        super().__init__('skill_marketplace')
        self.marketplace_url = DEFAULT_MARKETPLACE_URL
        self.timeout = 30
        self.local_skills_dir = Path.home() / ".ymcode" / "skills" / "custom"
        self.local_skills_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def description(self) -> str:
        return "Skills 市场 - 浏览、下载、安装第三方 Skills"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "download", "install", "info"],
                    "description": "操作类型"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（search 需要）"
                },
                "skill_name": {
                    "type": "string",
                    "description": "Skill 名称（download/install 需要）"
                },
                "skill_id": {
                    "type": "string",
                    "description": "Skill ID（info 需要）"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict) -> any:
        """执行技能"""
        action = arguments.get("action")
        
        if action == "list":
            return await self.list_skills()
        elif action == "search":
            return await self.search_skills(arguments.get("query", ""))
        elif action == "download":
            return await self.download_skill(arguments.get("skill_name", ""))
        elif action == "install":
            return await self.install_skill(arguments.get("skill_name", ""))
        elif action == "info":
            return await self.get_skill_info(arguments.get("skill_id", ""))
        else:
            return {"error": f"未知操作：{action}"}
    
    async def list_skills(self, category: str = None) -> Dict:
        """列出所有 Skills"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.marketplace_url}{SKILLS_API}"
                if category:
                    url += f"?category={category}"
                
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "skills": data.get("skills", []),
                    "total": data.get("total", 0)
                }
        except Exception as e:
            logger.error(f"列出 Skills 失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "skills": self._get_local_skills()
            }
    
    async def search_skills(self, query: str) -> Dict:
        """搜索 Skills"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.marketplace_url}{SKILLS_API}/search?q={query}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "skills": data.get("skills", []),
                    "total": data.get("total", 0)
                }
        except Exception as e:
            logger.error(f"搜索 Skills 失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "skills": self._search_local_skills(query)
            }
    
    async def download_skill(self, skill_name: str) -> Dict:
        """下载 Skill"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.marketplace_url}{SKILLS_API}/{skill_name}/download"
                response = await client.get(url)
                response.raise_for_status()
                
                skill_data = response.json()
                
                # 保存到本地
                skill_file = self.local_skills_dir / f"{skill_name}.py"
                with open(skill_file, 'w', encoding='utf-8') as f:
                    f.write(skill_data.get("code", ""))
                
                # 保存元数据
                meta_file = self.local_skills_dir / f"{skill_name}.meta.json"
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(skill_data.get("metadata", {}), f, indent=2)
                
                logger.info(f"Skill 已下载：{skill_file}")
                
                return {
                    "success": True,
                    "message": f"Skill '{skill_name}' 已下载到 {skill_file}",
                    "path": str(skill_file)
                }
        except Exception as e:
            logger.error(f"下载 Skill 失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def install_skill(self, skill_name: str) -> Dict:
        """安装 Skill（下载 + 注册）"""
        # 1. 下载
        download_result = await self.download_skill(skill_name)
        if not download_result.get("success"):
            return download_result
        
        # 2. 验证
        skill_file = self.local_skills_dir / f"{skill_name}.py"
        if not skill_file.exists():
            return {
                "success": False,
                "error": "Skill 文件不存在"
            }
        
        # 3. 导入验证
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(skill_name, skill_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {
                "success": True,
                "message": f"Skill '{skill_name}' 安装成功",
                "path": str(skill_file),
                "note": "重启 YM-CODE 后生效"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Skill 验证失败：{e}"
            }
    
    async def get_skill_info(self, skill_id: str) -> Dict:
        """获取 Skill 信息"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.marketplace_url}{SKILLS_API}/{skill_id}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "skill": data
                }
        except Exception as e:
            logger.error(f"获取 Skill 信息失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_local_skills(self) -> List[Dict]:
        """获取本地 Skills"""
        skills = []
        for file in self.local_skills_dir.glob("*.py"):
            if file.stem != "__init__":
                skills.append({
                    "name": file.stem,
                    "source": "local",
                    "path": str(file)
                })
        return skills
    
    def _search_local_skills(self, query: str) -> List[Dict]:
        """搜索本地 Skills"""
        skills = self._get_local_skills()
        query_lower = query.lower()
        return [
            skill for skill in skills
            if query_lower in skill["name"].lower()
        ]
    
    def list_installed_skills(self) -> List[Dict]:
        """列出已安装的 Skills"""
        return self._get_local_skills()


class WebBrowserSkill(BaseSkill):
    """网页浏览技能"""
    
    def __init__(self):
        """初始化网页浏览"""
        super().__init__('web_browser')
        self.timeout = 30
    
    @property
    def description(self) -> str:
        return "网页浏览 - 访问网页、提取内容、搜索信息"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["fetch", "search", "screenshot"],
                    "description": "操作类型"
                },
                "url": {
                    "type": "string",
                    "description": "URL（fetch/screenshot 需要）"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（search 需要）"
                },
                "engine": {
                    "type": "string",
                    "enum": ["google", "bing", "baidu"],
                    "description": "搜索引擎",
                    "default": "google"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict) -> any:
        """执行技能"""
        action = arguments.get("action")
        
        if action == "fetch":
            return await self.fetch_url(arguments.get("url"))
        elif action == "search":
            return await self.search_web(arguments.get("query"), arguments.get("engine"))
        elif action == "screenshot":
            return await self.take_screenshot(arguments.get("url"))
        else:
            return {"error": f"未知操作：{action}"}
    
    async def fetch_url(self, url: str) -> Dict:
        """获取网页内容"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # 简单提取文本内容
                content = response.text
                
                # 移除 HTML 标签（简单处理）
                import re
                text = re.sub(r'<[^>]+>', '', content)
                text = re.sub(r'\s+', ' ', text).strip()
                
                return {
                    "success": True,
                    "url": url,
                    "title": self._extract_title(content),
                    "content": text[:5000],  # 限制长度
                    "length": len(text)
                }
        except Exception as e:
            logger.error(f"获取网页失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_web(self, query: str, engine: str = "google") -> Dict:
        """网络搜索"""
        search_urls = {
            "google": f"https://www.google.com/search?q={query}",
            "bing": f"https://www.bing.com/search?q={query}",
            "baidu": f"https://www.baidu.com/s?wd={query}"
        }
        
        search_url = search_urls.get(engine, search_urls["google"])
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(search_url)
                response.raise_for_status()
                content = response.text
                
                # 简单提取搜索结果
                results = self._extract_search_results(content, engine)
                
                return {
                    "success": True,
                    "query": query,
                    "engine": engine,
                    "search_url": search_url,
                    "results": results[:10]  # 前 10 个结果
                }
        except Exception as e:
            logger.error(f"搜索失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def take_screenshot(self, url: str) -> Dict:
        """网页截图（需要浏览器）"""
        # TODO: 集成 Playwright 或 Selenium
        return {
            "success": False,
            "error": "截图功能需要浏览器支持，计划中"
        }
    
    def _extract_title(self, html: str) -> str:
        """提取网页标题"""
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def _extract_search_results(self, html: str, engine: str) -> List[Dict]:
        """提取搜索结果"""
        # 简单实现，实际需要更复杂的解析
        results = []
        
        # 这里只是示例，实际需要针对每个引擎解析
        if engine == "google":
            # Google 搜索结果解析
            import re
            matches = re.findall(r'<h3.*?>(.*?)</h3>', html, re.IGNORECASE)
            for match in matches[:10]:
                text = re.sub(r'<[^>]+>', '', match).strip()
                if text:
                    results.append({"title": text})
        
        return results
