"""
SafeNet Dashboard

Web-based dashboard for monitoring MCP operations, performance metrics,
and system health.
"""

# Dynamic import to avoid import errors
_available_components = []

try:
    from .dashboard import app, run_dashboard
    _available_components.extend(['app', 'run_dashboard'])
except ImportError:
    pass

__all__ = _available_components
