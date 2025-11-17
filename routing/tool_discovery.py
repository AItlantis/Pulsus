"""
DEPRECATED: This module has been replaced by mcp_router.py

The functionality of this module has been consolidated into the new MCPRouter
class in mcp_router.py, which provides:
- Dynamic tool discovery from MCP tools registry
- Workflow-based tool matching
- Better scoring and ranking of candidates

Please use:
    from .mcp_router import MCPRouter, discover

Instead of directly importing from this module.

This file is kept for backward compatibility but will be removed in a future version.
"""

# Backward compatibility imports
from .mcp_router import discover, ToolSpec

__all__ = ['discover', 'ToolSpec']
