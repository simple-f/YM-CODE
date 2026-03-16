#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Skills 桥接器

实现 YM-CODE Skills 与 OpenClaw Skills 的互操作
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import BaseSkill
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OpenClawSkillBridge:
    """OpenClaw Skills 桥接器"""
    
    def __init__(self, openclaw_workspace: str = None):
        """
        初始化桥接器
        
        参数:
            openclaw_workspace: OpenClaw 工作空间路径
        """
        self.openclaw_workspace = Path(openclaw_workspace) if openclaw_workspace else None
        self.available_skills: List[Dict] = []
        
        # 自动发现 OpenClaw Skills
        if self.openclaw_workspace:
            self._discover_skills()
        
        logger.info(f"OpenClaw Skills 桥接器初始化完成")
    
    def _discover_skills(self) -> None:
        """发现 OpenClaw Skills"""
        if not self.openclaw_workspace:
            return
        
        skills_dir = self.openclaw_workspace / 'skills'
        if not skills_dir.exists():
            logger.warning(f"Skills 目录不存在：{skills_dir}")
            return
        
        # 扫描技能目录
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    skill_info = self._parse_skill_md(skill_md)
                    self.available_skills.append(skill_info)
                    logger.info(f"发现 OpenClaw Skill: {skill_info.get('name')}")
    
    def _parse_skill_md(self, skill_md_path: Path) -> Dict:
        """解析 SKILL.md 文件"""
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析 frontmatter
            skill_info = {
                'name': skill_md_path.parent.name,
                'path': str(skill_md_path.parent),
                'description': content[:200]  # 取前 200 字符作为描述
            }
            
            # 提取标题
            for line in content.split('\n'):
                if line.startswith('# '):
                    skill_info['title'] = line[2:].strip()
                    break
            
            return skill_info
        except Exception as e:
            logger.error(f"解析 SKILL.md 失败：{e}")
            return {
                'name': skill_md_path.parent.name,
                'path': str(skill_md_path.parent),
                'description': '解析失败'
            }
    
    def list_available_skills(self) -> List[Dict]:
        """列出可用的 OpenClaw Skills"""
        return self.available_skills
    
    def get_skill_script(self, skill_name: str) -> Optional[Path]:
        """
        获取技能脚本路径
        
        参数:
            skill_name: 技能名称
        
        返回:
            脚本路径
        """
        for skill in self.available_skills:
            if skill['name'] == skill_name:
                skill_path = Path(skill['path'])
                
                # 查找脚本文件
                for script_name in ['script.py', 'main.py', 'run.py']:
                    script = skill_path / script_name
                    if script.exists():
                        return script
                
                # 查找 references 目录
                references = skill_path / 'references'
                if references.exists():
                    for script in references.glob('*.py'):
                        return script
        
        return None
    
    async def execute_skill(self, skill_name: str, arguments: Dict) -> Any:
        """
        执行 OpenClaw Skill
        
        参数:
            skill_name: 技能名称
            arguments: 输入参数
        
        返回:
            执行结果
        """
        script_path = self.get_skill_script(skill_name)
        
        if not script_path:
            return {
                'error': f'未找到技能 {skill_name} 的脚本',
                'available_skills': [s['name'] for s in self.available_skills]
            }
        
        try:
            import subprocess
            import asyncio
            
            # 构建命令
            cmd = ['python', str(script_path)]
            
            # 添加参数
            if arguments:
                cmd.extend(['--args', json.dumps(arguments)])
            
            # 执行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(script_path.parent)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'output': stdout.decode('utf-8'),
                    'skill': skill_name
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode('utf-8'),
                    'skill': skill_name
                }
        
        except Exception as e:
            return {
                'error': f'执行技能失败：{e}',
                'skill': skill_name
            }
    
    def import_skill(self, skill_name: str, target_dir: str = None) -> bool:
        """
        导入 OpenClaw Skill 到 YM-CODE
        
        参数:
            skill_name: 技能名称
            target_dir: 目标目录
        
        返回:
            是否成功
        """
        skill_info = None
        for skill in self.available_skills:
            if skill['name'] == skill_name:
                skill_info = skill
                break
        
        if not skill_info:
            logger.error(f'技能不存在：{skill_name}')
            return False
        
        import shutil
        
        target_dir = Path(target_dir) if target_dir else Path.cwd() / 'imported_skills'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 复制技能目录
            source = Path(skill_info['path'])
            target = target_dir / skill_name
            
            if target.exists():
                shutil.rmtree(target)
            
            shutil.copytree(source, target)
            
            logger.info(f'技能 {skill_name} 已导入到 {target}')
            return True
        
        except Exception as e:
            logger.error(f'导入技能失败：{e}')
            return False


class OpenClawBridgeSkill(BaseSkill):
    """OpenClaw 桥接技能（YM-CODE Skill 包装器）"""
    
    def __init__(self, bridge: OpenClawSkillBridge, skill_name: str):
        """
        初始化桥接技能
        
        参数:
            bridge: OpenClaw 桥接器
            skill_name: 技能名称
        """
        super().__init__(f'openclaw_{skill_name}')
        self.bridge = bridge
        self.skill_name = skill_name
    
    @property
    def description(self) -> str:
        return f"OpenClaw Skill: {self.skill_name}"
    
    def get_input_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "args": {
                    "type": "object",
                    "description": "技能参数"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict) -> Any:
        """执行技能"""
        args = arguments.get('args', {})
        return await self.bridge.execute_skill(self.skill_name, args)


# 便捷函数
def create_bridge(openclaw_workspace: str = None) -> OpenClawSkillBridge:
    """创建 OpenClaw Skills 桥接器"""
    return OpenClawSkillBridge(openclaw_workspace)


def list_openclaw_skills(openclaw_workspace: str = None) -> List[Dict]:
    """列出可用的 OpenClaw Skills"""
    bridge = create_bridge(openclaw_workspace)
    return bridge.list_available_skills()
