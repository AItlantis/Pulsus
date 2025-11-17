"""
MCP Core Module

Provides the foundational classes, decorators, and utilities for the
MCP (Model Context Protocol) class-based architecture.
"""

from .base import MCPBase, MCPResponse, MCPStatus
from .decorators import read_only, write_safe, restricted_write, transactional, cached
from .logger import MCPLogger, get_mcp_logger
from .policy import SafetyPolicy, ExecutionMode, SafetyLevel, get_safety_policy

__all__ = [
    # Base classes
    'MCPBase',
    'MCPResponse',
    'MCPStatus',

    # Decorators
    'read_only',
    'write_safe',
    'restricted_write',
    'transactional',
    'cached',

    # Logging
    'MCPLogger',
    'get_mcp_logger',

    # Policy
    'SafetyPolicy',
    'ExecutionMode',
    'SafetyLevel',
    'get_safety_policy',
]
