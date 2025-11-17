"""
LangChain Integration Module

Provides adapters and utilities for integrating Pulsus MCP operations with LangChain.
This module enables MCP domains to be used as LangChain StructuredTools and provides
StateGraph integration for complex workflows.
"""

__version__ = "0.1.0"

from langchain.tool_adapter import (
    mcp_to_langchain_tool,
    create_mcp_tool_collection,
    discover_and_convert_mcp_domains,
)

__all__ = [
    'mcp_to_langchain_tool',
    'create_mcp_tool_collection',
    'discover_and_convert_mcp_domains',
]
