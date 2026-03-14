#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行追踪器 - 详细记录 Agent 执行过程

支持：
- 调用栈追踪
- 参数/返回值记录
- 执行时间统计
- 条件断点
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from contextlib import contextmanager

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TraceEvent:
    """追踪事件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_type: str = ""  # call, return, error, log
    target: str = ""  # 目标函数/方法
    args: Dict[str, Any] = None
    result: Any = None
    error: str = None
    duration_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceSession:
    """追踪会话"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = None
    events: List[TraceEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: TraceEvent) -> None:
        self.events.append(event)
    
    def duration(self) -> float:
        """计算会话时长（秒）"""
        end = self.end_time or datetime.now().isoformat()
        start = datetime.fromisoformat(self.start_time)
        end_dt = datetime.fromisoformat(end)
        return (end_dt - start).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration(),
            'event_count': len(self.events),
            'events': [e.to_dict() for e in self.events],
            'metadata': self.metadata
        }


class ExecutionTracer:
    """执行追踪器"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化追踪器
        
        参数:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / '.ym-code' / 'debug' / 'traces'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, TraceSession] = {}
        self.current_session: Optional[str] = None
        self.enabled = False
        self.filters: List[str] = []  # 过滤的目标列表
        self.breakpoints: Dict[str, Callable] = {}  # 条件断点
        
        logger.info(f"执行追踪器初始化完成（目录：{self.storage_dir}）")
    
    def enable(self, filters: List[str] = None) -> None:
        """启用追踪"""
        self.enabled = True
        self.filters = filters or []
        self.start_session()
        logger.info("执行追踪已启用")
    
    def disable(self) -> None:
        """禁用追踪"""
        self.enabled = False
        self.stop_session()
        logger.info("执行追踪已禁用")
    
    def start_session(self, metadata: Dict[str, Any] = None) -> str:
        """开始追踪会话"""
        session = TraceSession(metadata=metadata or {})
        self.sessions[session.id] = session
        self.current_session = session.id
        
        logger.info(f"开始追踪会话：{session.id}")
        
        return session.id
    
    def stop_session(self) -> Optional[str]:
        """停止追踪会话"""
        if not self.current_session:
            return None
        
        session = self.sessions[self.current_session]
        session.end_time = datetime.now().isoformat()
        
        # 保存到文件
        self._save_session(session)
        
        session_id = self.current_session
        self.current_session = None
        
        logger.info(f"停止追踪会话：{session_id}")
        
        return session_id
    
    def _save_session(self, session: TraceSession) -> Path:
        """保存会话到文件"""
        file_path = self.storage_dir / f"{session.id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.debug(f"保存追踪会话：{file_path}")
        
        return file_path
    
    def trace(self, target: str = None):
        """
        追踪装饰器
        
        用法：
            @tracer.trace('my_function')
            def my_function(...):
                ...
        """
        def decorator(func: Callable) -> Callable:
            import functools
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                target_name = target or func.__name__
                
                # 检查过滤器
                if self.filters and not any(f in target_name for f in self.filters):
                    return await func(*args, **kwargs)
                
                # 记录调用事件
                start_time = time.time()
                event = TraceEvent(
                    event_type='call',
                    target=target_name,
                    args={'args': args, 'kwargs': kwargs}
                )
                self._record_event(event)
                
                # 检查断点
                if target_name in self.breakpoints:
                    self.breakpoints[target_name](event)
                
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # 记录返回事件
                    event = TraceEvent(
                        event_type='return',
                        target=target_name,
                        result=result,
                        duration_ms=duration_ms
                    )
                    self._record_event(event)
                    
                    return result
                    
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # 记录错误事件
                    event = TraceEvent(
                        event_type='error',
                        target=target_name,
                        error=str(e),
                        duration_ms=duration_ms
                    )
                    self._record_event(event)
                    
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                target_name = target or func.__name__
                
                # 检查过滤器
                if self.filters and not any(f in target_name for f in self.filters):
                    return func(*args, **kwargs)
                
                # 记录调用事件
                start_time = time.time()
                event = TraceEvent(
                    event_type='call',
                    target=target_name,
                    args={'args': args, 'kwargs': kwargs}
                )
                self._record_event(event)
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # 记录返回事件
                    event = TraceEvent(
                        event_type='return',
                        target=target_name,
                        result=result,
                        duration_ms=duration_ms
                    )
                    self._record_event(event)
                    
                    return result
                    
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # 记录错误事件
                    event = TraceEvent(
                        event_type='error',
                        target=target_name,
                        error=str(e),
                        duration_ms=duration_ms
                    )
                    self._record_event(event)
                    
                    raise
            
            # 判断是否是异步函数
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _record_event(self, event: TraceEvent) -> None:
        """记录事件"""
        if not self.current_session:
            return
        
        session = self.sessions[self.current_session]
        session.add_event(event)
        
        logger.debug(f"记录事件：{event.event_type} {event.target}")
    
    def set_breakpoint(self, target: str, callback: Callable) -> None:
        """设置断点"""
        self.breakpoints[target] = callback
        logger.info(f"设置断点：{target}")
    
    def remove_breakpoint(self, target: str) -> None:
        """移除断点"""
        if target in self.breakpoints:
            del self.breakpoints[target]
            logger.info(f"移除断点：{target}")
    
    def get_session(self, session_id: str = None) -> Optional[TraceSession]:
        """获取会话"""
        sid = session_id or self.current_session
        return self.sessions.get(sid)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        return [
            {
                'id': s.id,
                'start_time': s.start_time,
                'end_time': s.end_time,
                'duration': s.duration(),
                'event_count': len(s.events)
            }
            for s in self.sessions.values()
        ]
    
    def get_session_file(self, session_id: str) -> Optional[Path]:
        """获取会话文件路径"""
        file_path = self.storage_dir / f"{session_id}.json"
        return file_path if file_path.exists() else None
    
    def replay_session(self, session_id: str) -> List[TraceEvent]:
        """回放会话"""
        session = self.get_session(session_id)
        if not session:
            # 尝试从文件加载
            file_path = self.get_session_file(session_id)
            if not file_path:
                raise ValueError(f"会话不存在：{session_id}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                session = TraceSession(
                    id=data['id'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    metadata=data.get('metadata', {})
                )
                for event_data in data.get('events', []):
                    event = TraceEvent(**event_data)
                    session.add_event(event)
        
        return session.events
    
    def get_statistics(self, session_id: str = None) -> Dict[str, Any]:
        """获取统计信息"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # 按目标分组统计
        target_stats = {}
        error_count = 0
        
        for event in session.events:
            target = event.target
            
            if target not in target_stats:
                target_stats[target] = {
                    'call_count': 0,
                    'total_duration_ms': 0,
                    'error_count': 0
                }
            
            if event.event_type == 'call':
                target_stats[target]['call_count'] += 1
            elif event.event_type == 'return':
                target_stats[target]['total_duration_ms'] += event.duration_ms
            elif event.event_type == 'error':
                error_count += 1
                target_stats[target]['error_count'] += 1
        
        # 计算平均值
        for target, stats in target_stats.items():
            if stats['call_count'] > 0:
                stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['call_count']
        
        return {
            'session_id': session_id or self.current_session,
            'duration': session.duration(),
            'total_events': len(session.events),
            'error_count': error_count,
            'targets': target_stats
        }
    
    def export_session(self, session_id: str, format: str = 'json') -> str:
        """导出会话"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在：{session_id}")
        
        if format == 'json':
            return json.dumps(session.to_dict(), indent=2, ensure_ascii=False)
        elif format == 'text':
            lines = [f"Trace Session: {session.id}"]
            lines.append(f"Duration: {session.duration():.2f}s")
            lines.append(f"Events: {len(session.events)}")
            lines.append("")
            
            for event in session.events:
                lines.append(f"[{event.timestamp}] {event.event_type} {event.target}")
                if event.duration_ms > 0:
                    lines.append(f"  Duration: {event.duration_ms:.2f}ms")
            
            return '\n'.join(lines)
        else:
            raise ValueError(f"不支持的格式：{format}")


# 全局追踪器
_tracer: Optional[ExecutionTracer] = None


def get_tracer() -> ExecutionTracer:
    """获取全局追踪器"""
    global _tracer
    if _tracer is None:
        _tracer = ExecutionTracer()
    return _tracer


def trace(target: str = None):
    """便捷函数：追踪装饰器"""
    return get_tracer().trace(target)
