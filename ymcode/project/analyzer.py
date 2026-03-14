#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Analyzer - 项目结构分析器
"""

import os
import json
import logging
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    name: str
    size: int
    extension: str
    language: str
    lines: int
    imports: List[str]
    classes: List[str]
    functions: List[str]


@dataclass
class ProjectStructure:
    """项目结构"""
    root: str
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    directories: Dict[str, int]
    files: List[FileInfo]


class ProjectAnalyzer:
    """项目分析器"""
    
    # 语言映射
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.vue': 'vue',
        '.svelte': 'svelte',
    }
    
    # 忽略的目录
    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git', '.svn', '.hg',
        'venv', '.venv', 'env', '.env',
        'dist', 'build', 'target', 'out',
        '.idea', '.vscode', '.vs',
        'coverage', '.nyc_output',
        'vendor', 'Pods',
        '*.egg-info', '.tox'
    }
    
    # 忽略的文件
    IGNORE_FILES = {
        '*.pyc', '*.pyo', '*.class', '*.o', '*.a',
        '*.so', '*.dylib', '*.dll',
        '*.min.js', '*.min.css',
        '*.map', '*.lock',
        'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'
    }
    
    def __init__(self, root_path: str = None):
        """
        初始化项目分析器
        
        参数:
            root_path: 项目根路径
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.files: Dict[str, FileInfo] = {}
        self.structure: Optional[ProjectStructure] = None
        
        logger.info(f"项目分析器初始化完成：{self.root_path}")
    
    def analyze(self, max_files: int = 1000) -> ProjectStructure:
        """
        分析项目结构
        
        参数:
            max_files: 最大分析文件数
        
        返回:
            项目结构信息
        """
        logger.info(f"开始分析项目：{self.root_path}")
        
        self.files.clear()
        file_count = 0
        
        # 遍历项目目录
        for root, dirs, files in os.walk(self.root_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if not self._should_ignore(d, root)]
            
            # 处理文件
            for filename in files:
                if self._should_ignore(filename, root):
                    continue
                
                file_path = Path(root) / filename
                
                # 检查文件数限制
                if file_count >= max_files:
                    logger.warning(f"达到最大文件数限制：{max_files}")
                    break
                
                # 分析文件
                try:
                    file_info = self._analyze_file(file_path)
                    if file_info:
                        self.files[str(file_path)] = file_info
                        file_count += 1
                except Exception as e:
                    logger.debug(f"分析文件失败 {file_path}: {e}")
        
        # 构建项目结构
        self.structure = self._build_structure()
        
        logger.info(f"项目分析完成：{self.structure.total_files} 个文件，{self.structure.total_lines} 行代码")
        
        return self.structure
    
    def _should_ignore(self, name: str, parent_path: str = "") -> bool:
        """检查是否应该忽略"""
        # 检查目录黑名单
        if name in self.IGNORE_DIRS:
            return True
        
        # 检查通配符模式
        for pattern in self.IGNORE_DIRS:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
        
        # 检查文件黑名单
        for pattern in self.IGNORE_FILES:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            if pattern == name:
                return True
        
        # 检查隐藏文件
        if name.startswith('.'):
            return True
        
        return False
    
    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """分析单个文件"""
        try:
            # 获取文件信息
            stat = file_path.stat()
            extension = file_path.suffix.lower()
            language = self.LANGUAGE_MAP.get(extension, 'unknown')
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                return None
            
            lines = content.split('\n')
            line_count = len(lines)
            
            # 分析导入、类、函数
            imports = self._extract_imports(content, language)
            classes = self._extract_classes(content, language)
            functions = self._extract_functions(content, language)
            
            return FileInfo(
                path=str(file_path.relative_to(self.root_path)),
                name=file_path.name,
                size=stat.st_size,
                extension=extension,
                language=language,
                lines=line_count,
                imports=imports,
                classes=classes,
                functions=functions
            )
        
        except Exception as e:
            logger.debug(f"分析文件失败 {file_path}: {e}")
            return None
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """提取导入语句"""
        imports = []
        
        if language == 'python':
            import re
            # import xxx
            for match in re.finditer(r'^import\s+([\w.]+)', content, re.MULTILINE):
                imports.append(match.group(1))
            # from xxx import
            for match in re.finditer(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
                imports.append(match.group(1))
        
        elif language in ['javascript', 'typescript']:
            import re
            # import ... from 'xxx'
            for match in re.finditer(r'import\s+.*?\s+from\s+[\'"]([^\']+)[\'"]', content):
                imports.append(match.group(1))
            # require('xxx')
            for match in re.finditer(r'require\([\'"]([^\']+)[\'"]\)', content):
                imports.append(match.group(1))
        
        return list(set(imports))
    
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """提取类定义"""
        classes = []
        
        if language == 'python':
            import re
            for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                classes.append(match.group(1))
        
        elif language in ['javascript', 'typescript']:
            import re
            for match in re.finditer(r'class\s+(\w+)', content):
                classes.append(match.group(1))
        
        return classes
    
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """提取函数定义"""
        functions = []
        
        if language == 'python':
            import re
            for match in re.finditer(r'^def\s+(\w+)\s*\(', content, re.MULTILINE):
                functions.append(match.group(1))
        
        elif language in ['javascript', 'typescript']:
            import re
            # function xxx()
            for match in re.finditer(r'function\s+(\w+)\s*\(', content):
                functions.append(match.group(1))
            # const xxx = () =>
            for match in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', content):
                functions.append(match.group(1))
        
        return functions
    
    def _build_structure(self) -> ProjectStructure:
        """构建项目结构"""
        # 统计语言分布
        languages = defaultdict(int)
        for file_info in self.files.values():
            languages[file_info.language] += file_info.lines
        
        # 统计目录分布
        directories = defaultdict(int)
        for file_info in self.files.values():
            dir_path = str(Path(file_info.path).parent)
            directories[dir_path] += 1
        
        return ProjectStructure(
            root=str(self.root_path),
            total_files=len(self.files),
            total_lines=sum(f.lines for f in self.files.values()),
            languages=dict(languages),
            directories=dict(directories),
            files=list(self.files.values())
        )
    
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        """获取文件信息"""
        return self.files.get(path)
    
    def search_files(self, pattern: str) -> List[FileInfo]:
        """搜索文件"""
        import fnmatch
        results = []
        for file_info in self.files.values():
            if fnmatch.fnmatch(file_info.name, pattern):
                results.append(file_info)
        return results
    
    def get_symbols(self, name: str) -> List[Dict]:
        """获取符号（类/函数）"""
        results = []
        for file_info in self.files.values():
            # 查找类
            if name in file_info.classes:
                results.append({
                    'type': 'class',
                    'name': name,
                    'file': file_info.path,
                    'language': file_info.language
                })
            # 查找函数
            if name in file_info.functions:
                results.append({
                    'type': 'function',
                    'name': name,
                    'file': file_info.path,
                    'language': file_info.language
                })
        return results
    
    def get_summary(self) -> Dict:
        """获取项目摘要"""
        if not self.structure:
            self.analyze()
        
        return {
            'root': str(self.root_path),
            'total_files': self.structure.total_files,
            'total_lines': self.structure.total_lines,
            'languages': self.structure.languages,
            'top_directories': sorted(
                self.structure.directories.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        if not self.structure:
            self.analyze()
        
        return {
            'structure': asdict(self.structure),
            'summary': self.get_summary()
        }
    
    def save_to_file(self, output_path: str) -> None:
        """保存分析结果到文件"""
        data = self.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"项目分析结果已保存到：{output_path}")
