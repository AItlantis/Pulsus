"""
MCP Composition

Provides tools for composing multiple MCP operations into workflows.
Supports chaining, parallel execution, and conditional flows.
"""

# Dynamic import to avoid import errors
_available_components = []

try:
    from .chain import OperationChain
    _available_components.append('OperationChain')
except ImportError:
    pass

try:
    from .parallel import ParallelOperations
    _available_components.append('ParallelOperations')
except ImportError:
    pass

try:
    from .conditional import ConditionalFlow
    _available_components.append('ConditionalFlow')
except ImportError:
    pass

__all__ = _available_components
