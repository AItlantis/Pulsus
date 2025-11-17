"""
Pulsus routing module.

Provides MCP-aware routing for Pulsus agent with backward compatibility.
"""

from .mcp_router import MCPRouter, parse, discover
from .router import route, find_workflow

__all__ = [
    'MCPRouter',
    'parse',
    'discover',
    'route',
    'find_workflow'
]
