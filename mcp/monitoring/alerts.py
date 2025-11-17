"""
Alerting System

Provides alerting capabilities for MCP operations.
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert"""
    name: str
    severity: AlertSeverity
    message: str
    timestamp: str
    context: Dict[str, Any]
    triggered_by: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


class AlertCondition:
    """Represents an alert condition"""

    def __init__(
        self,
        name: str,
        condition_fn: Callable[[], bool],
        severity: AlertSeverity,
        message_fn: Callable[[], str],
        action_fn: Optional[Callable[[Alert], None]] = None,
        cooldown_seconds: int = 300
    ):
        """
        Initialize alert condition.

        Args:
            name: Alert name
            condition_fn: Function that returns True when alert should fire
            severity: Alert severity level
            message_fn: Function that returns alert message
            action_fn: Optional function to execute when alert fires
            cooldown_seconds: Minimum seconds between alerts
        """
        self.name = name
        self.condition_fn = condition_fn
        self.severity = severity
        self.message_fn = message_fn
        self.action_fn = action_fn
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered: Optional[datetime] = None

    def check(self) -> Optional[Alert]:
        """
        Check if condition is met.

        Returns:
            Alert if condition is met, None otherwise
        """
        # Check cooldown
        if self.last_triggered:
            time_since_last = (datetime.utcnow() - self.last_triggered).total_seconds()
            if time_since_last < self.cooldown_seconds:
                return None

        # Evaluate condition
        try:
            if self.condition_fn():
                # Create alert
                alert = Alert(
                    name=self.name,
                    severity=self.severity,
                    message=self.message_fn(),
                    timestamp=datetime.utcnow().isoformat() + 'Z',
                    context={},
                    triggered_by='condition_check'
                )

                self.last_triggered = datetime.utcnow()

                # Execute action if provided
                if self.action_fn:
                    try:
                        self.action_fn(alert)
                    except Exception as e:
                        print(f"Alert action failed for '{self.name}': {e}")

                return alert
        except Exception as e:
            # Condition evaluation failed
            print(f"Alert condition check failed for '{self.name}': {e}")

        return None


class AlertManager:
    """
    Alert system for MCP operations.

    Example:
        >>> from mcp.monitoring.metrics import get_metrics
        >>> alerts = AlertManager()
        >>> metrics = get_metrics()
        >>>
        >>> # Register high error rate alert
        >>> alerts.register_alert(
        ...     name='high_error_rate',
        ...     condition=lambda: metrics.get_error_rate() > 0.1,
        ...     severity=AlertSeverity.ERROR,
        ...     message=lambda: f"Error rate: {metrics.get_error_rate():.1%}",
        ...     action=lambda alert: print(f"ALERT: {alert.message}")
        ... )
        >>>
        >>> # Check alerts periodically
        >>> triggered = alerts.check_all()
    """

    def __init__(self):
        """Initialize alert manager"""
        self.conditions: Dict[str, AlertCondition] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000

    def register_alert(
        self,
        name: str,
        condition: Callable[[], bool],
        severity: AlertSeverity,
        message: Callable[[], str],
        action: Optional[Callable[[Alert], None]] = None,
        cooldown_seconds: int = 300
    ) -> None:
        """
        Register an alert condition.

        Args:
            name: Unique alert name
            condition: Function that returns True when alert should fire
            severity: Alert severity level
            message: Function that returns alert message
            action: Optional function to execute when alert fires
            cooldown_seconds: Minimum seconds between alerts
        """
        self.conditions[name] = AlertCondition(
            name=name,
            condition_fn=condition,
            severity=severity,
            message_fn=message,
            action_fn=action,
            cooldown_seconds=cooldown_seconds
        )

    def unregister_alert(self, name: str) -> bool:
        """
        Unregister an alert condition.

        Args:
            name: Alert name

        Returns:
            True if alert was unregistered, False if not found
        """
        if name in self.conditions:
            del self.conditions[name]
            return True
        return False

    def check_all(self) -> List[Alert]:
        """
        Check all registered alert conditions.

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        for condition in self.conditions.values():
            alert = condition.check()
            if alert:
                triggered_alerts.append(alert)
                self._add_to_history(alert)

        return triggered_alerts

    def check_alert(self, name: str) -> Optional[Alert]:
        """
        Check a specific alert condition.

        Args:
            name: Alert name

        Returns:
            Alert if triggered, None otherwise
        """
        if name in self.conditions:
            alert = self.conditions[name].check()
            if alert:
                self._add_to_history(alert)
            return alert
        return None

    def get_history(
        self,
        limit: int = 50,
        severity: Optional[AlertSeverity] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alert history.

        Args:
            limit: Maximum number of alerts to return
            severity: Optional filter by severity

        Returns:
            List of alerts
        """
        filtered = self.alert_history

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        recent = filtered[-limit:]
        return [a.to_dict() for a in reversed(recent)]

    def get_alert_counts(self) -> Dict[str, int]:
        """
        Get count of alerts by severity.

        Returns:
            Dictionary mapping severity to count
        """
        counts = {
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }

        for alert in self.alert_history:
            counts[alert.severity.value] += 1

        return counts

    def clear_history(self) -> None:
        """Clear alert history"""
        self.alert_history.clear()

    def _add_to_history(self, alert: Alert) -> None:
        """
        Add alert to history.

        Args:
            alert: Alert to add
        """
        self.alert_history.append(alert)

        # Maintain max history size
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]


# Global alert manager instance
_global_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager
