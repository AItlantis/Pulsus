"""
MCP Helper Modules

Core helper modules for script operations, documentation, metadata, and optimization.
Includes both legacy procedural helpers and new class-based MCP helpers (Phase 2).
"""

# Legacy procedural helpers
try:
    from .script_ops import ScriptOps
except ImportError:
    ScriptOps = None

try:
    from .repository_analyzer import RepositoryAnalyzer
except ImportError:
    RepositoryAnalyzer = None

# New class-based MCP helpers (Phase 2)
try:
    from .script_manager import ScriptManager
except ImportError:
    ScriptManager = None

try:
    from .repository_manager import RepositoryManager
except ImportError:
    RepositoryManager = None

try:
    from .model_inspector import ModelInspector
except ImportError:
    ModelInspector = None

try:
    from .layer_manager import LayerManager
except ImportError:
    LayerManager = None

try:
    from .data_analyzer import DataAnalyzer
except ImportError:
    DataAnalyzer = None

__all__ = [
    # Legacy
    'ScriptOps',
    'RepositoryAnalyzer',
    # New class-based (Phase 2)
    'ScriptManager',
    'RepositoryManager',
    'ModelInspector',
    'LayerManager',
    'DataAnalyzer'
]
