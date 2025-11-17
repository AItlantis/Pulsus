"""
MCP Simple Domains

Classic MCP domains migrated to the MCPBase framework.
These provide standard operations for common tasks.

Available domains:
- ScriptOps: Python script operations (read, analyze, document, comment)
- RepositoryOps: Repository analysis and management (scan, analyze, report)
"""

from .script_ops import ScriptOps
from .repository_ops import RepositoryOps

__all__ = ['ScriptOps', 'RepositoryOps']
