#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线

发布/订阅模式的事件系统
"""

import json
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set, Any
from collections import defaultdict
from dataclasses import dataclass, field
import queue

from .types import Event, EventType
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(eq=False)
class Subscription:
    """订阅信息"""
    callback: Callable[[Event], None]
    event_types: Optional[Set[EventType]] = None  # None 表示订阅所有事件
    created_at: datetime = field(default_factory=datetime.now)


class EventBus:
    """
    事件总线
    
    功能:
    - 发布/订阅模式
    - 事件过滤
    - 事件持久化
    - 事件回放
    - 异步处理
    
    使用示例:
        >>> bus = EventBus()
        >>> bus.subscribe(EventType.TASK_COMPLETED, lambda e: print(e))
        >>> bus.publish(EventType.TASK_COMPLETED, {"task_id": "123"})
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        retention_hours: int = 24,
        max_events: int = 10000
    ):
        """
        初始化事件总线
        
        参数:
            storage_path: 持久化路径
            retention_hours: 事件保留时间（小时）
            max_events: 最大事件数量
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.retention_hours = retention_hours
        self.max_events = max_events
        
        # 订阅者：event_type -> Set[Subscription]
        self._subscribers: Dict[EventType, Set[Subscription]] = defaultdict(set)
        
        # 全局订阅者（接收所有事件）
        self._global_subscribers: Set[Subscription] = set()
        
        # 事件存储
        self._events: List[Event] = []
        
        # 事件索引：event_id -> Event
        self._index: Dict[str, Event] = {}
        
        # 异步处理队列
        self._async_queue: queue.Queue = queue.Queue()
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 运行状态
        self._running = True
        
        # 启动异步处理线程
        self._start_async_processor()
        
        # 加载持久化数据
        if self.storage_path:
            self._load()
        
        logger.info(f"EventBus 初始化完成 (storage={self.storage_path})")
    
    def subscribe(
        self,
        event_type: Optional[EventType],
        callback: Callable[[Event], None]
    ) -> str:
        """
        订阅事件
        
        参数:
            event_type: 事件类型（None 表示订阅所有）
            callback: 回调函数
        
        返回:
            订阅 ID
        """
        with self._lock:
            subscription = Subscription(callback=callback, event_types={event_type} if event_type else None)
            
            if event_type:
                self._subscribers[event_type].add(subscription)
            else:
                self._global_subscribers.add(subscription)
            
            logger.debug(f"订阅事件：{event_type}")
            return str(id(subscription))
    
    def unsubscribe(self, callback: Callable[[Event], None]) -> bool:
        """
        取消订阅
        
        参数:
            callback: 回调函数
        
        返回:
            是否成功
        """
        with self._lock:
            removed = False
            
            # 从类型订阅中移除
            for subscribers in self._subscribers.values():
                to_remove = [s for s in subscribers if s.callback == callback]
                for s in to_remove:
                    subscribers.remove(s)
                    removed = True
            
            # 从全局订阅中移除
            to_remove = [s for s in self._global_subscribers if s.callback == callback]
            for s in to_remove:
                self._global_subscribers.remove(s)
                removed = True
            
            return removed
    
    def publish(self, event_type: EventType, data: Dict[str, Any], source: str = "system", metadata: Optional[Dict] = None):
        """
        发布事件
        
        参数:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
            metadata: 元数据
        """
        event = Event(
            type=event_type,
            source=source,
            data=data,
            metadata=metadata or {}
        )
        
        self.publish_event(event)
    
    def publish_event(self, event: Event):
        """
        发布事件对象
        
        参数:
            event: 事件对象
        """
        with self._lock:
            # 存储事件
            self._events.append(event)
            self._index[event.id] = event
            
            # 限制事件数量
            if len(self._events) > self.max_events:
                old_event = self._events.pop(0)
                if old_event.id in self._index:
                    del self._index[old_event.id]
            
            # 持久化
            if self.storage_path:
                self._save()
            
            logger.debug(f"发布事件：{event.type.value} from {event.source}")
        
        # 异步通知订阅者
        self._async_queue.put(event)
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        获取事件
        
        参数:
            event_type: 事件类型过滤
            source: 来源过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
        
        返回:
            事件列表
        """
        with self._lock:
            results = []
            
            for event in reversed(self._events):  # 从新到旧
                # 类型过滤
                if event_type and event.type != event_type:
                    continue
                
                # 来源过滤
                if source and event.source != source:
                    continue
                
                # 时间过滤
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                
                results.append(event)
                
                if len(results) >= limit:
                    break
            
            return results
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """
        获取单个事件
        
        参数:
            event_id: 事件 ID
        
        返回:
            事件对象
        """
        with self._lock:
            return self._index.get(event_id)
    
    def replay(
        self,
        from_time: datetime,
        to_time: Optional[datetime] = None,
        callback: Optional[Callable[[Event], None]] = None,
        event_type: Optional[EventType] = None
    ) -> int:
        """
        回放事件
        
        参数:
            from_time: 开始时间
            to_time: 结束时间（默认当前时间）
            callback: 回调函数（默认使用订阅者）
            event_type: 事件类型过滤
        
        返回:
            回放的事件数量
        """
        with self._lock:
            to_time = to_time or datetime.now()
            count = 0
            
            for event in self._events:
                if event.timestamp < from_time:
                    continue
                if event.timestamp > to_time:
                    break
                
                if event_type and event.type != event_type:
                    continue
                
                if callback:
                    callback(event)
                else:
                    self._notify_subscriber(event)
                
                count += 1
            
            logger.info(f"回放事件：{count} 个 ({from_time} - {to_time})")
            return count
    
    def clear_old_events(self, older_than_hours: Optional[int] = None) -> int:
        """
        清理旧事件
        
        参数:
            older_than_hours: 清理早于此时间的事件
        
        返回:
            清理的事件数量
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=older_than_hours or self.retention_hours)
            
            old_events = [e for e in self._events if e.timestamp < cutoff]
            new_events = [e for e in self._events if e.timestamp >= cutoff]
            
            # 更新索引
            for event in old_events:
                if event.id in self._index:
                    del self._index[event.id]
            
            self._events = new_events
            
            logger.info(f"清理旧事件：{len(old_events)} 个")
            return len(old_events)
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        返回:
            统计信息字典
        """
        with self._lock:
            # 按类型统计
            type_counts = defaultdict(int)
            for event in self._events:
                type_counts[event.type.value] += 1
            
            return {
                "total_events": len(self._events),
                "subscriber_count": sum(len(s) for s in self._subscribers.values()) + len(self._global_subscribers),
                "events_by_type": dict(type_counts),
                "oldest_event": self._events[0].timestamp.isoformat() if self._events else None,
                "newest_event": self._events[-1].timestamp.isoformat() if self._events else None
            }
    
    def shutdown(self):
        """关闭事件总线"""
        self._running = False
        self._async_queue.put(None)  # 停止信号
        logger.info("EventBus 已关闭")
    
    def _start_async_processor(self):
        """启动异步处理线程"""
        def process():
            while self._running:
                try:
                    event = self._async_queue.get(timeout=1)
                    if event is None:  # 停止信号
                        break
                    
                    self._notify_subscribers(event)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"异步处理事件失败：{e}")
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _notify_subscribers(self, event: Event):
        """通知订阅者"""
        with self._lock:
            # 通知类型订阅者
            for subscription in self._subscribers.get(event.type, set()):
                try:
                    subscription.callback(event)
                except Exception as e:
                    logger.error(f"通知订阅者失败：{e}")
            
            # 通知全局订阅者
            for subscription in self._global_subscribers:
                try:
                    subscription.callback(event)
                except Exception as e:
                    logger.error(f"通知全局订阅者失败：{e}")
    
    def _save(self):
        """持久化数据"""
        if not self.storage_path:
            return
        
        try:
            # 只保存最近的事件
            recent_events = self._events[-1000:]
            
            data = {
                "events": [e.to_dict() for e in recent_events],
                "saved_at": datetime.now().isoformat()
            }
            
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"事件数据已保存：{self.storage_path}")
            
        except Exception as e:
            logger.error(f"保存事件数据失败：{e}")
    
    def _load(self):
        """加载持久化数据"""
        if not self.storage_path or not self.storage_path.exists():
            logger.info("无持久化数据，使用空总线")
            return
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._events = [Event.from_dict(e) for e in data.get("events", [])]
            self._index = {e.id: e for e in self._events}
            
            logger.info(f"已加载 {len(self._events)} 个事件")
            
        except Exception as e:
            logger.error(f"加载事件数据失败：{e}")
            self._events = []
            self._index = {}
