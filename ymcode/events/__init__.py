#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线模块
"""

from .types import Event, EventType
from .bus import EventBus

# 便捷函数
from .types import (
    agent_registered,
    agent_unregistered,
    agent_status_changed,
    task_created,
    task_started,
    task_completed,
    task_failed,
    handoff_completed
)

__all__ = [
    "Event",
    "EventType",
    "EventBus",
    "agent_registered",
    "agent_unregistered",
    "agent_status_changed",
    "task_created",
    "task_started",
    "task_completed",
    "task_failed",
    "handoff_completed",
]
