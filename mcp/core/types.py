"""
MCP Core Type Definitions

Centralized type definitions for type safety and clarity across the MCP framework.
"""

from typing import TypedDict, Protocol, Any, Dict, List, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
from enum import Enum


# ========== Type Aliases ==========

PathLike = Union[str, Path]
"""Path-like type (string or Path object)"""

JsonDict = Dict[str, Any]
"""JSON-compatible dictionary"""

Timestamp = str
"""ISO 8601 timestamp string"""


# ========== TypedDict Definitions ==========

class MCPResponseDict(TypedDict, total=False):
    """
    Type definition for MCPResponse dictionary representation.

    Attributes:
        success: Whether the operation succeeded
        context: Contextual information
        data: Operation result data
        error: Error message if failed
        trace: Execution trace
        status: Status code
        metadata: Additional metadata
    """
    success: bool
    context: JsonDict
    data: Any
    error: Optional[str]
    trace: List[str]
    status: str
    metadata: JsonDict


class OperationParams(TypedDict, total=False):
    """
    Type definition for operation parameters.

    Common parameters used across MCP operations.
    """
    path: PathLike
    target_path: PathLike
    content: str
    encoding: str
    mode: str
    recursive: bool
    force: bool


class CapabilityInfo(TypedDict):
    """
    Type definition for capability information.

    Attributes:
        name: Method/operation name
        description: Human-readable description
        safety_level: Safety level (read_only, write_safe, etc.)
        parameters: List of parameter names
        returns: Return type description
    """
    name: str
    description: str
    safety_level: str
    parameters: List[str]
    returns: str


class LogRecord(TypedDict):
    """
    Type definition for log records.

    Attributes:
        call_id: Unique call identifier
        timestamp: ISO 8601 timestamp
        caller: Calling agent/system
        mcp_class: MCP class name
        operation: Operation name
        params: Operation parameters
        result: Operation result
        success: Whether operation succeeded
        context: Additional context
    """
    call_id: str
    timestamp: Timestamp
    caller: str
    mcp_class: str
    operation: str
    params: JsonDict
    result: JsonDict
    success: bool
    context: JsonDict


class PolicyInfo(TypedDict, total=False):
    """
    Type definition for operation policy information.

    Attributes:
        name: Operation name
        safety_level: Safety level
        requires_confirmation: Whether confirmation is needed
        allowed_modes: List of allowed execution modes
        type_validation: Whether type validation is required
        allowed_types: List of allowed type names
        rollback_supported: Whether rollback is supported
        cache_ttl: Cache time-to-live in seconds
    """
    name: str
    safety_level: str
    requires_confirmation: bool
    allowed_modes: List[str]
    type_validation: bool
    allowed_types: List[str]
    rollback_supported: bool
    cache_ttl: Optional[int]


class SafetyPolicySummary(TypedDict):
    """
    Type definition for safety policy summary.

    Attributes:
        total_operations: Total number of registered operations
        current_mode: Current execution mode
        by_safety_level: Operations grouped by safety level
        platforms: Registered platforms
    """
    total_operations: int
    current_mode: str
    by_safety_level: Dict[str, List[str]]
    platforms: List[str]


class LoggerSummary(TypedDict):
    """
    Type definition for logger summary statistics.

    Attributes:
        total_calls: Total number of calls logged
        successful: Number of successful calls
        failed: Number of failed calls
        success_rate: Success rate percentage
        by_caller: Calls grouped by caller
        by_class: Calls grouped by MCP class
        by_operation: Calls grouped by operation
    """
    total_calls: int
    successful: int
    failed: int
    success_rate: float
    by_caller: Dict[str, int]
    by_class: Dict[str, int]
    by_operation: Dict[str, int]


# ========== Protocol Definitions ==========

class MCPOperationProtocol(Protocol):
    """
    Protocol for MCP operations.

    Any callable that accepts keyword arguments and returns an MCPResponse.
    """
    def __call__(self, **kwargs) -> 'MCPResponse':
        """Execute the operation"""
        ...


class MCPLoggerProtocol(Protocol):
    """
    Protocol for MCP loggers.

    Defines the interface that logger implementations must follow.
    """
    def log_call(
        self,
        caller: str,
        mcp_class: str,
        operation: str,
        params: JsonDict,
        result: JsonDict,
        success: bool,
        context: Optional[JsonDict] = None
    ) -> str:
        """Log an MCP call"""
        ...

    def get_history(
        self,
        caller: Optional[str] = None,
        mcp_class: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[LogRecord]:
        """Get call history"""
        ...

    def get_summary(self) -> LoggerSummary:
        """Get summary statistics"""
        ...


class SafetyPolicyProtocol(Protocol):
    """
    Protocol for safety policies.

    Defines the interface for policy enforcement.
    """
    def validate_operation(
        self,
        operation: str,
        mode: Optional['ExecutionMode'] = None,
        target: Optional[Any] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate if operation is allowed"""
        ...

    def requires_confirmation(self, operation: str) -> bool:
        """Check if operation requires confirmation"""
        ...

    def check_type_safety(
        self,
        obj: Any,
        allowed_types: Optional[List[str]] = None,
        platform: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """Check type safety"""
        ...


class MCPHelperProtocol(Protocol):
    """
    Protocol for MCP helper classes.

    Defines the interface that all MCP helpers must implement.
    """
    def get_capabilities(self) -> List[CapabilityInfo]:
        """Get list of capabilities"""
        ...

    def execute(self, operation: str, **kwargs) -> 'MCPResponse':
        """Execute operation by name"""
        ...


# ========== Callback Types ==========

RollbackHandler = Callable[[Any, ...], None]
"""Type for rollback handler functions"""

ConfirmationHandler = Callable[[str, tuple, dict, str], bool]
"""Type for confirmation handler functions"""

ValidationHandler = Callable[[Any], tuple[bool, Optional[str]]]
"""Type for validation handler functions"""


# ========== Constants ==========

DEFAULT_CACHE_TTL = 300
"""Default cache TTL in seconds (5 minutes)"""

DEFAULT_LOG_DIR = "logs/mcp"
"""Default directory for MCP logs"""

MAX_TRACE_LENGTH = 1000
"""Maximum number of trace messages to keep"""

MAX_HISTORY_LENGTH = 10000
"""Maximum number of history records to keep in memory"""


# ========== Utility Types ==========

class PlatformType(str, Enum):
    """Known platform types for type validation"""
    AIMSUN = "aimsun"
    QGIS = "qgis"
    PYTHON = "python"
    CUSTOM = "custom"


# Forward references (resolved at import time)
if False:  # TYPE_CHECKING equivalent
    from .base import MCPResponse, MCPBase
    from .policy import ExecutionMode, SafetyLevel, SafetyPolicy
    from .logger import MCPLogger


__all__ = [
    # Type aliases
    'PathLike',
    'JsonDict',
    'Timestamp',

    # TypedDict definitions
    'MCPResponseDict',
    'OperationParams',
    'CapabilityInfo',
    'LogRecord',
    'PolicyInfo',
    'SafetyPolicySummary',
    'LoggerSummary',

    # Protocol definitions
    'MCPOperationProtocol',
    'MCPLoggerProtocol',
    'SafetyPolicyProtocol',
    'MCPHelperProtocol',

    # Callback types
    'RollbackHandler',
    'ConfirmationHandler',
    'ValidationHandler',

    # Constants
    'DEFAULT_CACHE_TTL',
    'DEFAULT_LOG_DIR',
    'MAX_TRACE_LENGTH',
    'MAX_HISTORY_LENGTH',

    # Enums
    'PlatformType',
]
