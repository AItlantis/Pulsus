"""
MCP Simple Domains

Classic MCP domains migrated to the MCPBase framework.
These provide standard operations for common tasks.

Available domains:
- ScriptOps: Python script operations (read, analyze, document, comment)
- RepositoryOps: Repository analysis and management (scan, analyze, report)
- FileManager: File system operations (create, delete, move, copy, list)
- DataReader: Data loading and analysis (CSV, JSON, Parquet, Excel)
- TextProcessor: Text manipulation and analysis (search, replace, extract, count)
"""

from .script_ops import ScriptOps
from .repository_ops import RepositoryOps
from .file_manager import FileManager
from .data_reader import DataReader
from .text_processor import TextProcessor

__all__ = ['ScriptOps', 'RepositoryOps', 'FileManager', 'DataReader', 'TextProcessor']
