"""
MCP Advanced Domains

Advanced, platform-specific MCP domains for specialized operations.
Extends the simple MCP domains with more complex functionality.
"""

from pathlib import Path

# Dynamic import to avoid import errors when modules don't exist yet
_available_domains = []

try:
    from .git_ops import GitOps
    _available_domains.append('GitOps')
except ImportError:
    pass

try:
    from .workflow_ops import WorkflowOps
    _available_domains.append('WorkflowOps')
except ImportError:
    pass

__all__ = _available_domains
