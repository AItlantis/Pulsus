"""
Performance Metrics

Collects and analyzes MCP operation performance metrics.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
import statistics


@dataclass
class OperationMetric:
    """Represents a single operation execution metric"""
    timestamp: str
    domain: str
    operation: str
    duration_ms: float
    success: bool
    error: Optional[str] = None
    safety_level: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MCPMetrics:
    """
    Collect and analyze MCP performance metrics.

    Example:
        >>> metrics = MCPMetrics()
        >>> metrics.track_operation(
        ...     domain='ScriptOps',
        ...     operation='read_script',
        ...     duration_ms=45.2,
        ...     success=True
        ... )
        >>> stats = metrics.get_statistics('ScriptOps')
    """

    def __init__(self, max_history: int = 10000):
        """
        Initialize metrics collector.

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics: List[OperationMetric] = []
        self._domain_stats = defaultdict(lambda: defaultdict(list))

    def track_operation(
        self,
        domain: str,
        operation: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
        safety_level: Optional[str] = None
    ) -> None:
        """
        Track an operation execution.

        Args:
            domain: Domain name (e.g., 'ScriptOps')
            operation: Operation name (e.g., 'read_script')
            duration_ms: Execution time in milliseconds
            success: Whether operation succeeded
            error: Error message if failed
            safety_level: Safety level (read_only, write_safe, etc.)
        """
        metric = OperationMetric(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            domain=domain,
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            error=error,
            safety_level=safety_level
        )

        self.metrics.append(metric)

        # Maintain max history size
        if len(self.metrics) > self.max_history:
            self.metrics = self.metrics[-self.max_history:]

        # Update domain stats
        key = f"{domain}.{operation}"
        self._domain_stats[domain][key].append(metric)

    def get_statistics(
        self,
        domain: Optional[str] = None,
        operation: Optional[str] = None,
        timeframe: str = 'all'  # 'last_hour', 'last_day', 'all'
    ) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            domain: Optional filter by domain
            operation: Optional filter by operation
            timeframe: Time window ('last_hour', 'last_day', 'all')

        Returns:
            Dictionary with statistics
        """
        # Filter metrics
        filtered_metrics = self._filter_metrics(domain, operation, timeframe)

        if not filtered_metrics:
            return {
                'count': 0,
                'timeframe': timeframe,
                'domain': domain,
                'operation': operation
            }

        # Calculate statistics
        durations = [m.duration_ms for m in filtered_metrics]
        successes = [m for m in filtered_metrics if m.success]
        failures = [m for m in filtered_metrics if not m.success]

        stats = {
            'count': len(filtered_metrics),
            'success_count': len(successes),
            'failure_count': len(failures),
            'success_rate': len(successes) / len(filtered_metrics) if filtered_metrics else 0,
            'timeframe': timeframe,
            'domain': domain,
            'operation': operation
        }

        # Duration statistics
        if durations:
            sorted_durations = sorted(durations)
            stats['duration_ms'] = {
                'min': min(durations),
                'max': max(durations),
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'p50': sorted_durations[int(len(sorted_durations) * 0.50)],
                'p95': sorted_durations[int(len(sorted_durations) * 0.95)],
                'p99': sorted_durations[int(len(sorted_durations) * 0.99)] if len(sorted_durations) > 10 else max(durations)
            }

        # Error analysis
        if failures:
            error_counts = defaultdict(int)
            for f in failures:
                error_type = f.error.split(':')[0] if f.error else 'Unknown'
                error_counts[error_type] += 1

            stats['top_errors'] = sorted(
                [{'error': k, 'count': v} for k, v in error_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:5]

        return stats

    def get_slow_operations(
        self,
        threshold_ms: float = 1000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get operations slower than threshold.

        Args:
            threshold_ms: Duration threshold in milliseconds
            limit: Maximum number of results

        Returns:
            List of slow operations
        """
        slow_ops = [
            m for m in self.metrics
            if m.duration_ms > threshold_ms
        ]

        # Sort by duration (slowest first)
        slow_ops.sort(key=lambda x: x.duration_ms, reverse=True)

        return [m.to_dict() for m in slow_ops[:limit]]

    def get_error_rate(
        self,
        domain: Optional[str] = None,
        timeframe: str = 'last_hour'
    ) -> float:
        """
        Get error rate for domain/all domains.

        Args:
            domain: Optional filter by domain
            timeframe: Time window

        Returns:
            Error rate (0.0 to 1.0)
        """
        filtered_metrics = self._filter_metrics(domain, None, timeframe)

        if not filtered_metrics:
            return 0.0

        failures = sum(1 for m in filtered_metrics if not m.success)
        return failures / len(filtered_metrics)

    def get_recent_operations(
        self,
        limit: int = 50,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent operations.

        Args:
            limit: Maximum number of results
            domain: Optional filter by domain

        Returns:
            List of recent operations
        """
        filtered = [m for m in self.metrics if domain is None or m.domain == domain]
        recent = filtered[-limit:]
        return [m.to_dict() for m in reversed(recent)]

    def get_domain_summary(self) -> Dict[str, Any]:
        """
        Get summary of all domains.

        Returns:
            Dictionary with domain summaries
        """
        domains = {}
        for metric in self.metrics:
            if metric.domain not in domains:
                domains[metric.domain] = {
                    'total_operations': 0,
                    'successful_operations': 0,
                    'failed_operations': 0,
                    'total_duration_ms': 0
                }

            domains[metric.domain]['total_operations'] += 1
            if metric.success:
                domains[metric.domain]['successful_operations'] += 1
            else:
                domains[metric.domain]['failed_operations'] += 1
            domains[metric.domain]['total_duration_ms'] += metric.duration_ms

        # Calculate averages
        for domain_stats in domains.values():
            if domain_stats['total_operations'] > 0:
                domain_stats['avg_duration_ms'] = (
                    domain_stats['total_duration_ms'] / domain_stats['total_operations']
                )
                domain_stats['success_rate'] = (
                    domain_stats['successful_operations'] / domain_stats['total_operations']
                )

        return domains

    def _filter_metrics(
        self,
        domain: Optional[str],
        operation: Optional[str],
        timeframe: str
    ) -> List[OperationMetric]:
        """
        Filter metrics by criteria.

        Args:
            domain: Optional domain filter
            operation: Optional operation filter
            timeframe: Time window

        Returns:
            Filtered list of metrics
        """
        # Apply domain and operation filters
        filtered = self.metrics

        if domain:
            filtered = [m for m in filtered if m.domain == domain]

        if operation:
            filtered = [m for m in filtered if m.operation == operation]

        # Apply timeframe filter
        if timeframe != 'all':
            cutoff = None
            if timeframe == 'last_hour':
                cutoff = datetime.utcnow() - timedelta(hours=1)
            elif timeframe == 'last_day':
                cutoff = datetime.utcnow() - timedelta(days=1)

            if cutoff:
                cutoff_iso = cutoff.isoformat() + 'Z'
                filtered = [m for m in filtered if m.timestamp >= cutoff_iso]

        return filtered

    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self._domain_stats.clear()

    def export_metrics(self) -> List[Dict[str, Any]]:
        """
        Export all metrics.

        Returns:
            List of metric dictionaries
        """
        return [m.to_dict() for m in self.metrics]


# Global metrics instance
_global_metrics = None


def get_metrics() -> MCPMetrics:
    """Get global metrics instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MCPMetrics()
    return _global_metrics
