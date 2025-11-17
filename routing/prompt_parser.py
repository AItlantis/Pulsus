"""
DEPRECATED: This module has been replaced by mcp_router.py

The functionality of this module has been consolidated into the new MCPRouter
class in mcp_router.py, which provides:
- More flexible intent parsing using semantic matching
- Better integration with MCP tools
- Unified routing logic

Please use:
    from .mcp_router import MCPRouter, parse

Instead of directly importing from this module.

This file is kept for backward compatibility but will be removed in a future version.
"""

# Backward compatibility imports
from .mcp_router import parse, ParsedIntent

__all__ = ['parse', 'ParsedIntent']
