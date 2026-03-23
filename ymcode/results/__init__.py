#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果收集器模块
"""

from .collector import ResultCollector
from ..queue.task import TaskResult

__all__ = [
    "ResultCollector",
    "TaskResult",
]
