"""
MCP Enhanced Logger

Enhanced logging with SafeNet integration and caller tracking.
Extends the existing MCPActionLogger with additional capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

# Import existing action logger
try:
    from agents.mcp.helpers.action_logger import MCPActionLogger, MCPAction
except ImportError:
    # Fallback for testing
    MCPActionLogger = None
    MCPAction = None


class MCPLogger:
    """
    Enhanced MCP logger with SafeNet integration.

    Extends MCPActionLogger with:
    - Caller tracking (Pulse, Shell, Compass)
    - MCP class tracking
    - Execution context
    - SafeNet report generation

    Example:
        >>> logger = MCPLogger()
        >>> logger.log_call(
        ...     caller='Pulse',
        ...     mcp_class='ScriptManager',
        ...     operation='read_script',
        ...     params={'path': 'script.py'},
        ...     result={'success': True},
        ...     success=True
        ... )
    """

    def __init__(self, log_dir: str = "logs/mcp"):
        """
        Initialize MCP logger.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize base action logger if available
        if MCPActionLogger:
            self.action_logger = MCPActionLogger(log_dir=log_dir)
        else:
            self.action_logger = None

        # Enhanced logs
        self.safenet_log = self.log_dir / "safenet.jsonl"
        self.call_history: List[Dict[str, Any]] = []

    def log_call(
        self,
        caller: str,
        mcp_class: str,
        operation: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an MCP method call.

        Args:
            caller: Calling agent (Pulse, Shell, Compass, etc.)
            mcp_class: MCP helper class name
            operation: Operation/method name
            params: Operation parameters
            result: Operation result
            success: Whether operation succeeded
            context: Optional additional context

        Returns:
            Call ID for this log entry
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Create call record
        call_record = {
            'call_id': self._generate_call_id(),
            'timestamp': timestamp,
            'caller': caller,
            'mcp_class': mcp_class,
            'operation': operation,
            'params': params,
            'result': result,
            'success': success,
            'context': context or {}
        }

        # Add to call history
        self.call_history.append(call_record)

        # Write to SafeNet log
        self._write_safenet_log(call_record)

        # Also log to base action logger if available
        if self.action_logger and 'target_path' in params:
            try:
                self.action_logger.log_action(
                    tool_name=f"{mcp_class}.{operation}",
                    operation=operation,
                    target_path=params.get('target_path', ''),
                    parameters=params,
                    result=result,
                    success=success,
                    error=result.get('error')
                )
            except Exception as e:
                print(f"Warning: Failed to log to action logger: {e}")

        return call_record['call_id']

    def _generate_call_id(self) -> str:
        """Generate unique call ID"""
        import hashlib
        import uuid
        unique_str = f"{datetime.utcnow().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def _write_safenet_log(self, record: Dict[str, Any]) -> None:
        """Write record to SafeNet log file"""
        with self.safenet_log.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    def get_history(
        self,
        caller: Optional[str] = None,
        mcp_class: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get call history with optional filters.

        Args:
            caller: Filter by caller
            mcp_class: Filter by MCP class
            operation: Filter by operation
            limit: Maximum number of records to return

        Returns:
            List of call records
        """
        filtered = self.call_history.copy()

        # Apply filters
        if caller:
            filtered = [r for r in filtered if r['caller'] == caller]
        if mcp_class:
            filtered = [r for r in filtered if r['mcp_class'] == mcp_class]
        if operation:
            filtered = [r for r in filtered if r['operation'] == operation]

        # Return most recent first, up to limit
        return list(reversed(filtered[-limit:]))

    def get_calls_by_caller(self, caller: str) -> List[Dict[str, Any]]:
        """
        Get all calls from a specific caller.

        Args:
            caller: Caller name (Pulse, Shell, Compass)

        Returns:
            List of call records
        """
        return self.get_history(caller=caller)

    def get_calls_by_class(self, mcp_class: str) -> List[Dict[str, Any]]:
        """
        Get all calls to a specific MCP class.

        Args:
            mcp_class: MCP class name

        Returns:
            List of call records
        """
        return self.get_history(mcp_class=mcp_class)

    def export_safenet_report(
        self,
        output_path: Optional[str] = None,
        caller: Optional[str] = None,
        timeframe: Optional[str] = None
    ) -> str:
        """
        Export SafeNet report in Markdown format.

        Args:
            output_path: Optional output path
            caller: Filter by caller
            timeframe: Time filter (e.g., 'last_hour', 'today')

        Returns:
            Path to generated report
        """
        if not output_path:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.log_dir / f"safenet_report_{timestamp}.md"
        else:
            output_path = Path(output_path)

        # Get filtered history
        history = self.get_history(caller=caller)

        # Apply timeframe filter
        if timeframe:
            history = self._filter_by_timeframe(history, timeframe)

        # Generate report
        report = self._generate_safenet_report(history, caller)

        # Write to file
        output_path.write_text(report, encoding='utf-8')

        return str(output_path)

    def _filter_by_timeframe(self, history: List[Dict[str, Any]], timeframe: str) -> List[Dict[str, Any]]:
        """Filter history by timeframe"""
        from datetime import timedelta

        now = datetime.utcnow()

        if timeframe == 'last_hour':
            cutoff = now - timedelta(hours=1)
        elif timeframe == 'today':
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timeframe == 'last_24h':
            cutoff = now - timedelta(hours=24)
        else:
            return history

        filtered = []
        for record in history:
            record_time = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            if record_time >= cutoff:
                filtered.append(record)

        return filtered

    def _generate_safenet_report(self, history: List[Dict[str, Any]], caller: Optional[str]) -> str:
        """Generate SafeNet report in Markdown"""
        report = "# SafeNet MCP Action Report\n\n"

        # Header
        report += f"**Generated**: {datetime.utcnow().isoformat()}\n"
        if caller:
            report += f"**Caller**: {caller}\n"
        report += f"**Total Actions**: {len(history)}\n\n"

        # Statistics
        report += "## Statistics\n\n"
        stats = self._calculate_statistics(history)

        report += f"- **Success Rate**: {stats['success_rate']:.1f}%\n"
        report += f"- **Total Calls**: {stats['total_calls']}\n"
        report += f"- **Successful**: {stats['successful']}\n"
        report += f"- **Failed**: {stats['failed']}\n\n"

        # By caller
        report += "### By Caller\n\n"
        for caller_name, count in stats['by_caller'].items():
            report += f"- **{caller_name}**: {count} calls\n"
        report += "\n"

        # By MCP class
        report += "### By MCP Class\n\n"
        for class_name, count in stats['by_class'].items():
            report += f"- **{class_name}**: {count} calls\n"
        report += "\n"

        # By operation
        report += "### By Operation\n\n"
        for operation, count in stats['by_operation'].items():
            report += f"- **{operation}**: {count} calls\n"
        report += "\n"

        # Action history
        report += "## Action History\n\n"

        for record in history:
            report += f"### [{record['timestamp']}] {record['mcp_class']}.{record['operation']}\n\n"
            report += f"- **Caller**: {record['caller']}\n"
            report += f"- **Call ID**: `{record['call_id']}`\n"
            report += f"- **Success**: {'✓' if record['success'] else '✗'}\n"

            # Parameters
            if record['params']:
                report += f"- **Parameters**: `{self._format_params(record['params'])}`\n"

            # Result summary
            if record['result']:
                if 'error' in record['result'] and record['result']['error']:
                    report += f"- **Error**: {record['result']['error']}\n"

            # Context
            if record.get('context'):
                safety_level = record['context'].get('safety_level')
                if safety_level:
                    report += f"- **Safety Level**: `{safety_level}`\n"

            report += "\n"

        return report

    def _calculate_statistics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from history"""
        total = len(history)
        successful = sum(1 for r in history if r['success'])
        failed = total - successful

        by_caller = {}
        by_class = {}
        by_operation = {}

        for record in history:
            # By caller
            caller = record['caller']
            by_caller[caller] = by_caller.get(caller, 0) + 1

            # By class
            mcp_class = record['mcp_class']
            by_class[mcp_class] = by_class.get(mcp_class, 0) + 1

            # By operation
            operation = record['operation']
            by_operation[operation] = by_operation.get(operation, 0) + 1

        return {
            'total_calls': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'by_caller': dict(sorted(by_caller.items(), key=lambda x: x[1], reverse=True)),
            'by_class': dict(sorted(by_class.items(), key=lambda x: x[1], reverse=True)),
            'by_operation': dict(sorted(by_operation.items(), key=lambda x: x[1], reverse=True))
        }

    def _format_params(self, params: Dict[str, Any]) -> str:
        """Format parameters for display (truncate if too long)"""
        param_str = str(params)
        if len(param_str) > 100:
            return param_str[:97] + "..."
        return param_str

    def clear_history(self) -> None:
        """Clear in-memory call history"""
        self.call_history.clear()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of logging activity.

        Returns:
            Dictionary with summary statistics
        """
        return self._calculate_statistics(self.call_history)


# Global logger instance
_global_logger: Optional[MCPLogger] = None


def get_mcp_logger() -> MCPLogger:
    """
    Get or create global MCP logger instance.

    Returns:
        Global MCPLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = MCPLogger()
    return _global_logger
