"""
MCP Monitoring

Performance monitoring, metrics collection, and alerting for MCP operations.
"""

# Dynamic import to avoid import errors
_available_components = []

try:
    from .metrics import MCPMetrics
    _available_components.append('MCPMetrics')
except ImportError:
    pass

try:
    from .alerts import AlertManager
    _available_components.append('AlertManager')
except ImportError:
    pass

__all__ = _available_components
