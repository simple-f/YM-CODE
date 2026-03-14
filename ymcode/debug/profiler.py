#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析器 - 分析代码执行性能

支持：
- 函数执行时间
- 内存使用分析
- 调用热点分析
- 性能报告生成
"""

import time
import cProfile
import pstats
import io
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import contextmanager

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProfileResult:
    """性能分析结果"""
    id: str
    start_time: str
    end_time: str
    total_duration: float
    call_count: int
    functions: List[Dict[str, Any]]
    top_functions: List[Dict[str, Any]]
    memory_usage: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化分析器
        
        参数:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / '.ym-code' / 'debug' / 'profiles'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.results: Dict[str, ProfileResult] = {}
        self.current_profile: Optional[str] = None
        
        logger.info(f"性能分析器初始化完成（目录：{self.storage_dir}）")
    
    @contextmanager
    def profile(self, name: str = None):
        """
        性能分析上下文
        
        用法：
            with profiler.profile('my_operation'):
                # 执行代码
        """
        import uuid
        
        profile_id = name or str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        start_perf = time.perf_counter()
        
        # 启动 cProfile
        pr = cProfile.Profile()
        pr.enable()
        
        try:
            yield profile_id
        finally:
            pr.disable()
            
            end_time = datetime.now().isoformat()
            end_perf = time.perf_counter()
            total_duration = end_perf - start_perf
            
            # 解析分析结果
            stream = io.StringIO()
            ps = pstats.Stats(pr, stream=stream)
            ps.sort_stats('cumulative')
            ps.print_stats(50)  # 前 50 个函数
            
            # 提取函数统计
            functions = []
            for (file, line, func), (cc, nc, tt, ct, callers) in ps.stats.items():
                functions.append({
                    'file': file,
                    'line': line,
                    'function': func,
                    'call_count': nc,
                    'total_time': tt,
                    'cumulative_time': ct,
                    'avg_time': tt / nc if nc > 0 else 0
                })
            
            # 排序获取 top 函数
            top_functions = sorted(
                functions,
                key=lambda x: x['cumulative_time'],
                reverse=True
            )[:20]
            
            # 创建结果
            result = ProfileResult(
                id=profile_id,
                start_time=start_time,
                end_time=end_time,
                total_duration=total_duration,
                call_count=sum(f['call_count'] for f in functions),
                functions=functions,
                top_functions=top_functions
            )
            
            self.results[profile_id] = result
            self._save_result(result)
            
            logger.info(f"性能分析完成：{profile_id} ({total_duration:.3f}s)")
    
    def profile_function(self, func: Callable) -> Callable:
        """
        分析函数性能装饰器
        
        用法：
            @profiler.profile_function
            def my_function():
                ...
        """
        import functools
        import inspect
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with self.profile(func.__name__):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with self.profile(func.__name__):
                return func(*args, **kwargs)
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def _save_result(self, result: ProfileResult) -> Path:
        """保存分析结果"""
        file_path = self.storage_dir / f"{result.id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.debug(f"保存性能分析结果：{file_path}")
        
        return file_path
    
    def get_result(self, profile_id: str) -> Optional[ProfileResult]:
        """获取分析结果"""
        return self.results.get(profile_id)
    
    def list_results(self) -> List[Dict[str, Any]]:
        """列出所有分析结果"""
        return [
            {
                'id': r.id,
                'start_time': r.start_time,
                'duration': r.total_duration,
                'call_count': r.call_count
            }
            for r in self.results.values()
        ]
    
    def compare(self, profile_ids: List[str]) -> Dict[str, Any]:
        """比较多个分析结果"""
        if len(profile_ids) < 2:
            raise ValueError("至少需要 2 个分析结果进行比较")
        
        results = [self.get_result(pid) for pid in profile_ids]
        results = [r for r in results if r is not None]
        
        if len(results) < 2:
            raise ValueError("有效的分析结果不足 2 个")
        
        comparison = {
            'profiles': [],
            'duration_diff': 0,
            'call_count_diff': 0,
            'top_functions_common': [],
            'top_functions_diff': []
        }
        
        for result in results:
            comparison['profiles'].append({
                'id': result.id,
                'duration': result.total_duration,
                'call_count': result.call_count,
                'top_function': result.top_functions[0]['function'] if result.top_functions else None
            })
        
        # 计算差异
        if len(results) >= 2:
            comparison['duration_diff'] = results[1].total_duration - results[0].total_duration
            comparison['call_count_diff'] = results[1].call_count - results[0].call_count
        
        return comparison
    
    def generate_report(self, profile_id: str, format: str = 'text') -> str:
        """生成性能报告"""
        result = self.get_result(profile_id)
        if not result:
            raise ValueError(f"分析结果不存在：{profile_id}")
        
        if format == 'text':
            lines = [
                f"Performance Profile Report",
                f"=" * 50,
                f"ID: {result.id}",
                f"Duration: {result.total_duration:.3f}s",
                f"Total Calls: {result.call_count}",
                f"",
                f"Top Functions (by cumulative time):",
                f"-" * 50
            ]
            
            for i, func in enumerate(result.top_functions[:10], 1):
                lines.append(
                    f"{i}. {func['function']} "
                    f"({func['call_count']} calls, "
                    f"{func['cumulative_time']:.3f}s cumulative, "
                    f"{func['avg_time']*1000:.3f}ms avg)"
                )
            
            return '\n'.join(lines)
        
        elif format == 'html':
            return self._generate_html_report(result)
        
        elif format == 'json':
            return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        
        else:
            raise ValueError(f"不支持的格式：{format}")
    
    def _generate_html_report(self, result: ProfileResult) -> str:
        """生成 HTML 报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Profile: {result.id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #8B5CF6; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #8B5CF6; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>🔍 Performance Profile Report</h1>
    
    <div class="metrics">
        <div class="metric">
            <strong>ID:</strong> {result.id}
        </div>
        <div class="metric">
            <strong>Duration:</strong> {result.total_duration:.3f}s
        </div>
        <div class="metric">
            <strong>Total Calls:</strong> {result.call_count}
        </div>
    </div>
    
    <h2>Top Functions</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Function</th>
            <th>Calls</th>
            <th>Total Time</th>
            <th>Cumulative Time</th>
            <th>Avg Time</th>
        </tr>
"""
        
        for i, func in enumerate(result.top_functions[:20], 1):
            html += f"""
        <tr>
            <td>{i}</td>
            <td>{func['function']}</td>
            <td>{func['call_count']}</td>
            <td>{func['total_time']:.3f}s</td>
            <td>{func['cumulative_time']:.3f}s</td>
            <td>{func['avg_time']*1000:.3f}ms</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        return html
    
    def export_report(self, profile_id: str, output_path: str) -> Path:
        """导出报告到文件"""
        report = self.generate_report(profile_id, format='html')
        
        output = Path(output_path)
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"导出性能报告：{output}")
        
        return output


# 全局分析器
_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """获取全局分析器"""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler


def profile(name: str = None):
    """便捷函数：性能分析上下文"""
    return get_profiler().profile(name)


def profile_function(func: Callable):
    """便捷函数：函数性能分析装饰器"""
    return get_profiler().profile_function(func)
