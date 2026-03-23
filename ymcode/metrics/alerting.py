#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控告警系统

支持：
- 阈值告警
- 趋势告警
- 告警通知
- 告警历史
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态"""
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """告警对象"""
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "labels": self.labels,
            "annotations": self.annotations
        }


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "=="
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    duration: int = 0  # 持续时间（秒），0 表示立即告警
    cooldown: int = 300  # 冷却时间（秒），防止告警风暴
    enabled: bool = True
    labels: Dict[str, str] = field(default_factory=dict)
    message_template: str = ""
    
    def check(self, value: float) -> bool:
        """检查是否触发告警"""
        if self.condition == ">":
            return value > self.threshold
        elif self.condition == "<":
            return value < self.threshold
        elif self.condition == ">=":
            return value >= self.threshold
        elif self.condition == "<=":
            return value <= self.threshold
        elif self.condition == "==":
            return value == self.threshold
        return False
    
    def get_message(self, value: float, labels: Dict[str, str] = None) -> str:
        """生成告警消息"""
        if self.message_template:
            return self.message_template.format(
                name=self.name,
                metric_name=self.metric_name,
                value=value,
                threshold=self.threshold,
                labels=labels or {}
            )
        
        return (
            f"告警：{self.name}\n"
            f"指标：{self.metric_name} = {value}\n"
            f"阈值：{self.condition}{self.threshold}\n"
            f"严重程度：{self.severity.value}"
        )


class AlertManager:
    """
    告警管理器
    
    功能:
    - 告警规则管理
    - 告警触发与恢复
    - 告警通知
    - 告警历史
    
    使用示例:
        >>> manager = AlertManager()
        >>> manager.add_rule(AlertRule(
        ...     name="高 CPU 使用率",
        ...     metric_name="system.cpu_usage",
        ...     condition=">",
        ...     threshold=80.0,
        ...     severity=AlertSeverity.WARNING
        ... ))
        >>> manager.check_metric("system.cpu_usage", 85.0)
    """
    
    def __init__(self):
        """初始化告警管理器"""
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000  # 最多保留 1000 条历史
        
        # 告警触发时间记录（用于 duration 检查）
        self._trigger_times: Dict[str, datetime] = {}
        
        # 告警冷却时间记录
        self._last_alert_times: Dict[str, datetime] = {}
        
        # 通知回调
        self._notification_callbacks: List[Callable[[Alert], None]] = []
        
        # 线程锁
        self._lock = threading.RLock()
        
        logger.info("AlertManager 初始化完成")
    
    def add_rule(self, rule: AlertRule) -> bool:
        """
        添加告警规则
        
        参数:
            rule: 告警规则
        
        返回:
            是否成功
        """
        with self._lock:
            if rule.name in self.rules:
                logger.warning(f"告警规则已存在：{rule.name}")
                return False
            
            self.rules[rule.name] = rule
            logger.info(f"添加告警规则：{rule.name}")
            return True
    
    def remove_rule(self, rule_name: str) -> bool:
        """移除告警规则"""
        with self._lock:
            if rule_name not in self.rules:
                logger.warning(f"告警规则不存在：{rule_name}")
                return False
            
            del self.rules[rule_name]
            logger.info(f"移除告警规则：{rule_name}")
            return True
    
    def enable_rule(self, rule_name: str) -> bool:
        """启用告警规则"""
        with self._lock:
            if rule_name not in self.rules:
                return False
            self.rules[rule_name].enabled = True
            return True
    
    def disable_rule(self, rule_name: str) -> bool:
        """禁用告警规则"""
        with self._lock:
            if rule_name not in self.rules:
                return False
            self.rules[rule_name].enabled = False
            return True
    
    def check_metric(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> List[Alert]:
        """
        检查指标是否触发告警
        
        参数:
            metric_name: 指标名称
            value: 指标值
            labels: 标签
        
        返回:
            触发的告警列表
        """
        triggered_alerts = []
        now = datetime.now()
        
        with self._lock:
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                if rule.metric_name != metric_name:
                    continue
                
                # 检查是否满足条件
                if not rule.check(value):
                    # 条件不满足，检查是否可以恢复告警
                    self._try_resolve_alert(rule, metric_name, labels)
                    continue
                
                # 检查冷却时间
                if self._in_cooldown(rule, now):
                    continue
                
                # 检查持续时间
                if not self._check_duration(rule, now):
                    continue
                
                # 触发告警
                alert = self._create_alert(rule, value, labels)
                triggered_alerts.append(alert)
                
                # 发送通知
                self._send_notification(alert)
        
        return triggered_alerts
    
    def acknowledge_alert(self, alert_name: str) -> bool:
        """确认告警"""
        with self._lock:
            if alert_name not in self.active_alerts:
                logger.warning(f"告警不存在：{alert_name}")
                return False
            
            alert = self.active_alerts[alert_name]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.updated_at = datetime.now()
            
            logger.info(f"告警已确认：{alert_name}")
            return True
    
    def resolve_alert(self, alert_name: str) -> bool:
        """恢复告警"""
        with self._lock:
            if alert_name not in self.active_alerts:
                logger.warning(f"告警不存在：{alert_name}")
                return False
            
            alert = self.active_alerts[alert_name]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.updated_at = datetime.now()
            
            # 移到历史
            self.alert_history.append(alert)
            del self.active_alerts[alert_name]
            
            # 清理历史
            self._cleanup_history()
            
            logger.info(f"告警已恢复：{alert_name}")
            return True
    
    def get_active_alerts(self) -> List[Alert]:
        """获取所有活跃告警"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """获取告警历史"""
        with self._lock:
            alerts = self.alert_history
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            # 按时间倒序
            alerts.sort(key=lambda a: a.created_at, reverse=True)
            
            return alerts[:limit]
    
    def add_notification_callback(
        self,
        callback: Callable[[Alert], None]
    ) -> None:
        """添加通知回调"""
        self._notification_callbacks.append(callback)
    
    def get_stats(self) -> Dict:
        """获取告警统计"""
        with self._lock:
            return {
                "rule_count": len(self.rules),
                "active_alert_count": len(self.active_alerts),
                "history_count": len(self.alert_history),
                "alerts_by_severity": self._count_by_severity()
            }
    
    def _create_alert(
        self,
        rule: AlertRule,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> Alert:
        """创建告警"""
        alert_key = f"{rule.name}:{labels or {}}"
        
        alert = Alert(
            name=rule.name,
            severity=rule.severity,
            status=AlertStatus.FIRING,
            message=rule.get_message(value, labels),
            metric_name=rule.metric_name,
            metric_value=value,
            threshold=rule.threshold,
            labels=labels or {},
            annotations=rule.labels
        )
        
        self.active_alerts[alert_key] = alert
        self._last_alert_times[rule.name] = datetime.now()
        
        logger.warning(f"告警触发：{alert.name} - {alert.message}")
        
        return alert
    
    def _try_resolve_alert(
        self,
        rule: AlertRule,
        metric_name: str,
        labels: Optional[Dict[str, str]] = None
    ):
        """尝试恢复告警"""
        alert_key = f"{rule.name}:{labels or {}}"
        
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            
            # 自动恢复
            if alert.status == AlertStatus.FIRING:
                self.resolve_alert(alert_key)
                logger.info(f"告警自动恢复：{alert.name}")
    
    def _in_cooldown(self, rule: AlertRule, now: datetime) -> bool:
        """检查是否在冷却期"""
        if rule.name not in self._last_alert_times:
            return False
        
        last_time = self._last_alert_times[rule.name]
        elapsed = (now - last_time).total_seconds()
        
        return elapsed < rule.cooldown
    
    def _check_duration(self, rule: AlertRule, now: datetime) -> bool:
        """检查持续时间"""
        if rule.duration == 0:
            return True
        
        if rule.name not in self._trigger_times:
            self._trigger_times[rule.name] = now
            return False
        
        elapsed = (now - self._trigger_times[rule.name]).total_seconds()
        return elapsed >= rule.duration
    
    def _send_notification(self, alert: Alert):
        """发送通知"""
        for callback in self._notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"发送通知失败：{e}")
    
    def _count_by_severity(self) -> Dict[str, int]:
        """按严重程度统计"""
        counts = {s.value: 0 for s in AlertSeverity}
        for alert in self.active_alerts.values():
            counts[alert.severity.value] += 1
        return counts
    
    def _cleanup_history(self):
        """清理历史记录"""
        if len(self.alert_history) > self.max_history:
            # 删除最旧的一半
            self.alert_history = self.alert_history[-self.max_history // 2:]
            logger.debug(f"清理告警历史，保留{len(self.alert_history)}条")


# 便捷函数
_default_alert_manager = None


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器"""
    global _default_alert_manager
    if _default_alert_manager is None:
        _default_alert_manager = AlertManager()
    return _default_alert_manager


def setup_default_alerts():
    """设置默认告警规则"""
    manager = get_alert_manager()
    
    # 系统告警规则
    default_rules = [
        AlertRule(
            name="高任务队列大小",
            metric_name="system.queue_size",
            condition=">",
            threshold=100.0,
            severity=AlertSeverity.WARNING,
            duration=60,  # 持续 1 分钟
            message_template="任务队列过大：{value}（阈值：{threshold}）"
        ),
        AlertRule(
            name="高任务失败率",
            metric_name="system.task_failure_rate",
            condition=">",
            threshold=0.1,  # 10%
            severity=AlertSeverity.ERROR,
            duration=300,  # 持续 5 分钟
            message_template="任务失败率过高：{value:.2%}（阈值：{threshold:.2%}）"
        ),
        AlertRule(
            name="Agent 离线",
            metric_name="agent.status",
            condition="<=",
            threshold=0.0,
            severity=AlertSeverity.CRITICAL,
            message_template="Agent 离线：{labels}"
        ),
    ]
    
    for rule in default_rules:
        manager.add_rule(rule)
    
    logger.info("默认告警规则已设置")
    
    return manager


if __name__ == "__main__":
    # 测试告警系统
    manager = setup_default_alerts()
    
    # 添加通知回调
    def notify(alert):
        print(f"\n🚨 告警通知：")
        print(f"  名称：{alert.name}")
        print(f"  严重程度：{alert.severity.value}")
        print(f"  消息：{alert.message}")
    
    manager.add_notification_callback(notify)
    
    # 测试触发告警
    print("测试触发告警...")
    manager.check_metric("system.queue_size", 150.0)
    manager.check_metric("system.task_failure_rate", 0.15)
    
    # 查看活跃告警
    print("\n活跃告警:")
    for alert in manager.get_active_alerts():
        print(f"  - {alert.name} ({alert.severity.value})")
    
    # 查看统计
    print("\n告警统计:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
