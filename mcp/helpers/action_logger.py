"""
MCP Action Logger

Logs all MCP tool actions for reproducibility and rollback.
Provides audit trail of all script operations performed via MCP.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MCPAction:
    """Represents a single MCP action."""
    action_id: str
    timestamp: str
    tool_name: str
    operation: str
    target_path: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    file_hash_before: Optional[str] = None
    file_hash_after: Optional[str] = None


class MCPActionLogger:
    """
    Logs MCP actions for reproducibility and rollback.

    Features:
    - Records all MCP tool calls with parameters and results
    - Tracks file state before/after operations
    - Enables rollback of operations
    - Provides audit trail for compliance
    - Supports querying action history
    """

    def __init__(self, log_dir: str = "logs/mcp"):
        """
        Initialize MCP action logger.

        Args:
            log_dir: Directory to store MCP action logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.actions_dir = self.log_dir / "actions"
        self.actions_dir.mkdir(exist_ok=True)

        self.sessions_dir = self.log_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        # Daily log file
        today = datetime.date.today().isoformat()
        self.daily_log = self.log_dir / f"mcp_{today}.jsonl"

        # Current session
        self.session_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.session_log = self.sessions_dir / f"session_{self.session_id}.jsonl"

    def _generate_action_id(self) -> str:
        """Generate unique action ID."""
        timestamp = datetime.datetime.utcnow().isoformat()
        unique_str = f"{timestamp}_{id(self)}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def _compute_file_hash(self, file_path: Path) -> Optional[str]:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hash string or None if file doesn't exist
        """
        if not file_path.exists():
            return None

        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except Exception:
            return None

    def log_action(
        self,
        tool_name: str,
        operation: str,
        target_path: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        success: bool,
        error: Optional[str] = None,
        compute_hash: bool = True
    ) -> MCPAction:
        """
        Log an MCP action.

        Args:
            tool_name: Name of MCP tool (e.g., "mcp_read_script")
            operation: Operation type (e.g., "read", "write", "comment")
            target_path: Path to target file
            parameters: Tool parameters
            result: Operation result
            success: Whether operation succeeded
            error: Error message if failed
            compute_hash: Whether to compute file hashes (for write operations)

        Returns:
            MCPAction object representing the logged action
        """
        action_id = self._generate_action_id()
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

        file_hash_before = None
        file_hash_after = None

        # Compute hashes for write operations
        if compute_hash and target_path:
            target = Path(target_path)

            # For write operations, we need the before hash from parameters
            # or compute it now for safety
            if operation in ["write_md", "add_comments", "write"]:
                file_hash_before = self._compute_file_hash(target)

                # After operation completed
                if success:
                    file_hash_after = self._compute_file_hash(target)

        action = MCPAction(
            action_id=action_id,
            timestamp=timestamp,
            tool_name=tool_name,
            operation=operation,
            target_path=str(target_path) if target_path else "",
            parameters=parameters,
            result=result,
            success=success,
            error=error,
            file_hash_before=file_hash_before,
            file_hash_after=file_hash_after
        )

        # Write to logs
        self._write_action(action)

        return action

    def _write_action(self, action: MCPAction) -> None:
        """
        Write action to log files.

        Args:
            action: MCPAction to write
        """
        action_dict = asdict(action)
        log_line = json.dumps(action_dict, ensure_ascii=False)

        # Write to daily log
        with self.daily_log.open('a', encoding='utf-8') as f:
            f.write(log_line + '\n')

        # Write to session log
        with self.session_log.open('a', encoding='utf-8') as f:
            f.write(log_line + '\n')

        # Write individual action file for easy lookup
        action_file = self.actions_dir / f"{action.action_id}.json"
        with action_file.open('w', encoding='utf-8') as f:
            json.dump(action_dict, f, indent=2, ensure_ascii=False)

    def get_action(self, action_id: str) -> Optional[MCPAction]:
        """
        Retrieve a specific action by ID.

        Args:
            action_id: Action ID to retrieve

        Returns:
            MCPAction or None if not found
        """
        action_file = self.actions_dir / f"{action_id}.json"

        if not action_file.exists():
            return None

        try:
            with action_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                return MCPAction(**data)
        except Exception:
            return None

    def get_actions_for_file(self, file_path: str) -> List[MCPAction]:
        """
        Get all actions performed on a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of MCPAction objects for the file
        """
        actions = []

        # Read from daily log (more efficient than reading all action files)
        if self.daily_log.exists():
            with self.daily_log.open('r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if data.get('target_path') == str(file_path):
                            actions.append(MCPAction(**data))
                    except Exception:
                        continue

        return sorted(actions, key=lambda a: a.timestamp)

    def get_session_actions(self) -> List[MCPAction]:
        """
        Get all actions from current session.

        Returns:
            List of MCPAction objects from current session
        """
        actions = []

        if self.session_log.exists():
            with self.session_log.open('r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        actions.append(MCPAction(**data))
                    except Exception:
                        continue

        return actions

    def get_recent_actions(self, limit: int = 20) -> List[MCPAction]:
        """
        Get most recent actions.

        Args:
            limit: Maximum number of actions to return

        Returns:
            List of recent MCPAction objects
        """
        actions = []

        if self.daily_log.exists():
            with self.daily_log.open('r', encoding='utf-8') as f:
                lines = f.readlines()

                # Get last N lines
                for line in lines[-limit:]:
                    try:
                        data = json.loads(line.strip())
                        actions.append(MCPAction(**data))
                    except Exception:
                        continue

        return sorted(actions, key=lambda a: a.timestamp, reverse=True)

    def verify_file_integrity(self, action_id: str, file_path: str) -> Dict[str, Any]:
        """
        Verify file integrity by comparing current hash with logged hash.

        Args:
            action_id: Action ID to verify against
            file_path: Path to file

        Returns:
            Dict with verification results
        """
        action = self.get_action(action_id)

        if not action:
            return {
                "verified": False,
                "error": f"Action {action_id} not found"
            }

        current_hash = self._compute_file_hash(Path(file_path))

        return {
            "verified": current_hash == action.file_hash_after,
            "current_hash": current_hash,
            "expected_hash": action.file_hash_after,
            "action": asdict(action)
        }

    def export_session_report(self, output_path: Optional[str] = None) -> str:
        """
        Export human-readable session report.

        Args:
            output_path: Optional path to save report

        Returns:
            Path to generated report
        """
        actions = self.get_session_actions()

        if not output_path:
            output_path = self.sessions_dir / f"report_{self.session_id}.md"
        else:
            output_path = Path(output_path)

        # Generate markdown report
        report = f"# MCP Session Report\n\n"
        report += f"**Session ID**: {self.session_id}\n"
        report += f"**Generated**: {datetime.datetime.utcnow().isoformat()}\n"
        report += f"**Total Actions**: {len(actions)}\n\n"

        report += "## Actions\n\n"

        for action in actions:
            report += f"### {action.tool_name} - {action.operation}\n\n"
            report += f"- **Action ID**: `{action.action_id}`\n"
            report += f"- **Timestamp**: {action.timestamp}\n"
            report += f"- **Target**: `{action.target_path}`\n"
            report += f"- **Success**: {'✓' if action.success else '✗'}\n"

            if action.error:
                report += f"- **Error**: {action.error}\n"

            if action.file_hash_before:
                report += f"- **Hash Before**: `{action.file_hash_before[:16]}...`\n"
            if action.file_hash_after:
                report += f"- **Hash After**: `{action.file_hash_after[:16]}...`\n"

            report += "\n"

        output_path.write_text(report, encoding='utf-8')

        return str(output_path)


# Global logger instance
_global_logger: Optional[MCPActionLogger] = None


def get_mcp_logger() -> MCPActionLogger:
    """
    Get or create global MCP action logger.

    Returns:
        Global MCPActionLogger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = MCPActionLogger()

    return _global_logger


def log_mcp_action(
    tool_name: str,
    operation: str,
    target_path: str,
    parameters: Dict[str, Any],
    result: Dict[str, Any],
    success: bool,
    error: Optional[str] = None
) -> MCPAction:
    """
    Convenience function to log an MCP action using global logger.

    Args:
        tool_name: Name of MCP tool
        operation: Operation type
        target_path: Target file path
        parameters: Tool parameters
        result: Operation result
        success: Success status
        error: Optional error message

    Returns:
        MCPAction object
    """
    logger = get_mcp_logger()
    return logger.log_action(
        tool_name=tool_name,
        operation=operation,
        target_path=target_path,
        parameters=parameters,
        result=result,
        success=success,
        error=error
    )
