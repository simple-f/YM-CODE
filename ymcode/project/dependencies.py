#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Analyzer - 依赖关系分析器
"""

import logging
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Dependency:
    """依赖关系"""
    from_file: str
    to_file: str
    import_statement: str
    dependency_type: str  # direct, indirect, circular


@dataclass
class ModuleInfo:
    """模块信息"""
    path: str
    name: str
    imports: List[str]
    imported_by: List[str]
    is_circular: bool


class DependencyAnalyzer:
    """依赖关系分析器"""
    
    def __init__(self, root_path: str = None):
        """
        初始化依赖分析器
        
        参数:
            root_path: 项目根路径
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.modules: Dict[str, ModuleInfo] = {}
        self.dependencies: List[Dependency] = []
        self.circular_deps: List[List[str]] = []
        
        logger.info(f"依赖分析器初始化完成：{self.root_path}")
    
    def analyze(self, file_paths: List[str]) -> Dict[str, ModuleInfo]:
        """
        分析依赖关系
        
        参数:
            file_paths: 文件路径列表
        
        返回:
            模块信息字典
        """
        logger.info(f"开始分析依赖关系：{len(file_paths)} 个文件")
        
        # 第一步：解析所有文件的导入
        for file_path in file_paths:
            self._parse_imports(file_path)
        
        # 第二步：构建依赖关系
        self._build_dependencies()
        
        # 第三步：检测循环依赖
        self._detect_circular_dependencies()
        
        logger.info(f"依赖分析完成：{len(self.modules)} 个模块，{len(self.dependencies)} 个依赖")
        
        return self.modules
    
    def _parse_imports(self, file_path: str) -> None:
        """解析文件的导入语句"""
        try:
            path = Path(file_path)
            if not path.exists():
                return
            
            # 读取文件
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取导入
            imports = self._extract_imports(content, path.suffix.lower())
            
            # 创建模块信息
            rel_path = str(path.relative_to(self.root_path))
            self.modules[rel_path] = ModuleInfo(
                path=rel_path,
                name=path.stem,
                imports=imports,
                imported_by=[],
                is_circular=False
            )
        
        except Exception as e:
            logger.debug(f"解析导入失败 {file_path}: {e}")
    
    def _extract_imports(self, content: str, extension: str) -> List[str]:
        """提取导入语句"""
        imports = []
        
        if extension == '.py':
            # Python import
            for match in re.finditer(r'^import\s+([\w.]+)', content, re.MULTILINE):
                imports.append(match.group(1))
            for match in re.finditer(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
                imports.append(match.group(1))
        
        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript import
            for match in re.finditer(r'import\s+.*?\s+from\s+[\'"]([^\']+)[\'"]', content):
                imports.append(match.group(1))
            for match in re.finditer(r'require\([\'"]([^\']+)[\'"]\)', content):
                imports.append(match.group(1))
        
        return list(set(imports))
    
    def _build_dependencies(self) -> None:
        """构建依赖关系"""
        for file_path, module in self.modules.items():
            for import_stmt in module.imports:
                # 尝试解析为本地文件
                resolved = self._resolve_import(import_stmt, file_path)
                
                if resolved and resolved in self.modules:
                    # 添加依赖
                    self.dependencies.append(Dependency(
                        from_file=file_path,
                        to_file=resolved,
                        import_statement=import_stmt,
                        dependency_type='direct'
                    ))
                    
                    # 更新被依赖者的 imported_by
                    self.modules[resolved].imported_by.append(file_path)
    
    def _resolve_import(self, import_stmt: str, from_file: str) -> Optional[str]:
        """解析导入语句对应的文件"""
        # 简化实现：尝试匹配文件名
        import_name = import_stmt.split('.')[-1]
        
        # 尝试直接匹配
        for file_path in self.modules.keys():
            file_name = Path(file_path).stem
            if file_name == import_name:
                return file_path
        
        # 尝试路径匹配
        for file_path in self.modules.keys():
            if import_stmt in file_path:
                return file_path
        
        return None
    
    def _detect_circular_dependencies(self) -> None:
        """检测循环依赖"""
        # 使用 DFS 检测循环
        visited = set()
        rec_stack = set()
        
        def dfs(module_path: str, path: List[str]) -> bool:
            visited.add(module_path)
            rec_stack.add(module_path)
            
            module = self.modules.get(module_path)
            if not module:
                return False
            
            for dep in self.dependencies:
                if dep.from_file == module_path:
                    if dep.to_file not in visited:
                        if dfs(dep.to_file, path + [dep.to_file]):
                            return True
                    elif dep.to_file in rec_stack:
                        # 发现循环依赖
                        cycle_start = path.index(dep.to_file) if dep.to_file in path else 0
                        cycle = path[cycle_start:] + [dep.to_file]
                        self.circular_deps.append(cycle)
                        
                        # 标记相关模块
                        for m in cycle:
                            if m in self.modules:
                                self.modules[m].is_circular = True
                        
                        return True
            
            rec_stack.remove(module_path)
            return False
        
        # 对每个模块执行 DFS
        for module_path in self.modules.keys():
            if module_path not in visited:
                dfs(module_path, [module_path])
        
        if self.circular_deps:
            logger.warning(f"发现 {len(self.circular_deps)} 个循环依赖")
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """获取依赖图"""
        graph = defaultdict(list)
        for dep in self.dependencies:
            graph[dep.from_file].append(dep.to_file)
        return dict(graph)
    
    def get_reverse_dependencies(self, file_path: str) -> List[str]:
        """获取反向依赖（谁依赖这个文件）"""
        module = self.modules.get(file_path)
        if module:
            return module.imported_by
        return []
    
    def get_circular_dependencies(self) -> List[List[str]]:
        """获取循环依赖列表"""
        return self.circular_deps
    
    def get_module_info(self, file_path: str) -> Optional[ModuleInfo]:
        """获取模块信息"""
        return self.modules.get(file_path)
    
    def get_summary(self) -> Dict:
        """获取依赖摘要"""
        return {
            'total_modules': len(self.modules),
            'total_dependencies': len(self.dependencies),
            'circular_dependencies': len(self.circular_deps),
            'circular_modules': [
                m.path for m in self.modules.values() if m.is_circular
            ]
        }
    
    def visualize(self, max_nodes: int = 20) -> str:
        """可视化依赖关系（文本格式）"""
        lines = ["依赖关系图：\n"]
        
        # 选择最重要的模块（被依赖最多的）
        sorted_modules = sorted(
            self.modules.items(),
            key=lambda x: len(x[1].imported_by),
            reverse=True
        )[:max_nodes]
        
        for file_path, module in sorted_modules:
            deps = len(module.imports)
            imported_by = len(module.imported_by)
            circular = " ⚠️" if module.is_circular else ""
            
            lines.append(f"📄 {module.name}{circular}")
            lines.append(f"   导入：{deps}, 被导入：{imported_by}")
            
            if module.imported_by:
                lines.append(f"   被以下模块依赖:")
                for importer in module.imported_by[:5]:
                    lines.append(f"     - {Path(importer).name}")
            
            lines.append("")
        
        if self.circular_deps:
            lines.append("\n⚠️ 循环依赖:")
            for cycle in self.circular_deps[:3]:
                lines.append(f"  {' -> '.join(cycle)}")
        
        return '\n'.join(lines)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'summary': self.get_summary(),
            'modules': {
                path: {
                    'name': m.name,
                    'imports': m.imports,
                    'imported_by': m.imported_by,
                    'is_circular': m.is_circular
                }
                for path, m in self.modules.items()
            },
            'dependencies': [
                {
                    'from': d.from_file,
                    'to': d.to_file,
                    'type': d.dependency_type
                }
                for d in self.dependencies
            ],
            'circular': self.circular_deps
        }
