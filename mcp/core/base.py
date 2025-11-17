"""
MCP Base Classes

Provides the foundational MCPResponse and MCPBase classes for all MCP operations.
These classes establish a standardized interface for Model Context Protocol operations.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class MCPStatus(Enum):
    """Status of MCP operation"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    INTERRUPTED = "interrupted"


@dataclass
class MCPResponse:
    """
    Standardized MCP response structure.

    All MCP operations return this consistent format for predictable
    LLM interactions and easier debugging.

    Attributes:
        success: Whether the operation succeeded
        context: Contextual information (caller, environment, object details)
        data: Operation result data (any type)
        error: Error message if operation failed
        trace: Execution trace for debugging (list of step descriptions)
        status: Detailed status (success, error, partial, interrupted)
        metadata: Additional metadata (timestamps, performance metrics, etc.)
    """
    success: bool
    context: Dict[str, Any] = field(default_factory=dict)
    data: Any = None
    error: Optional[str] = None
    trace: List[str] = field(default_factory=list)
    status: MCPStatus = MCPStatus.SUCCESS
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set status based on success flag if not explicitly set"""
        if not self.success and self.status == MCPStatus.SUCCESS:
            self.status = MCPStatus.ERROR

        # Add timestamp to metadata if not present
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary.

        Returns:
            Dictionary representation of the response
        """
        result = asdict(self)
        result['status'] = self.status.value
        return result

    def add_trace(self, message: str) -> None:
        """
        Add a trace message to the execution trace.

        Args:
            message: Trace message describing an execution step
        """
        self.trace.append(message)

    def set_error(self, error_msg: str, status: MCPStatus = MCPStatus.ERROR) -> None:
        """
        Set error information on the response.

        Args:
            error_msg: Error message
            status: Status to set (default: ERROR)
        """
        self.success = False
        self.error = error_msg
        self.status = status
        self.add_trace(f"ERROR: {error_msg}")

    @classmethod
    def success_response(cls, data: Any = None, context: Dict[str, Any] = None,
                        trace: List[str] = None, **metadata) -> "MCPResponse":
        """
        Create a successful response.

        Args:
            data: Result data
            context: Contextual information
            trace: Execution trace
            **metadata: Additional metadata

        Returns:
            MCPResponse with success=True
        """
        return cls(
            success=True,
            data=data,
            context=context or {},
            trace=trace or [],
            status=MCPStatus.SUCCESS,
            metadata=metadata
        )

    @classmethod
    def error_response(cls, error: str, context: Dict[str, Any] = None,
                      trace: List[str] = None, status: MCPStatus = MCPStatus.ERROR,
                      **metadata) -> "MCPResponse":
        """
        Create an error response.

        Args:
            error: Error message
            context: Contextual information
            trace: Execution trace
            status: Error status (default: ERROR)
            **metadata: Additional metadata

        Returns:
            MCPResponse with success=False
        """
        return cls(
            success=False,
            error=error,
            context=context or {},
            trace=trace or [],
            status=status,
            metadata=metadata
        )


class MCPBase:
    """
    Base class for all MCP helper classes.

    Provides:
    - Standardized response format (MCPResponse)
    - Operation logging
    - Context management
    - Error handling
    - Capability introspection

    Subclasses should:
    - Implement domain-specific methods
    - Use decorators for safety policies (@read_only, @write_safe, etc.)
    - Return MCPResponse from all methods
    - Add trace messages for debugging

    Example:
        >>> class MyHelper(MCPBase):
        ...     @read_only
        ...     def get_info(self, obj_id: str) -> MCPResponse:
        ...         response = MCPResponse.success_response()
        ...         response.add_trace("Starting get_info")
        ...         # ... operation logic
        ...         return response
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize MCP base.

        Args:
            logger: Optional MCPLogger instance for operation logging
            context: Optional initial context (environment, caller info, etc.)
        """
        self.logger = logger
        self.context = context or {}
        self._capabilities_cache: Optional[List[Dict[str, Any]]] = None

    def _create_response(self, success: bool = True, data: Any = None,
                        error: Optional[str] = None,
                        trace: List[str] = None) -> MCPResponse:
        """
        Create an MCPResponse with this helper's context.

        Args:
            success: Whether operation succeeded
            data: Result data
            error: Error message if failed
            trace: Execution trace

        Returns:
            MCPResponse with helper context included
        """
        response = MCPResponse(
            success=success,
            context=self.context.copy(),
            data=data,
            error=error,
            trace=trace or [],
            status=MCPStatus.SUCCESS if success else MCPStatus.ERROR
        )

        # Add class information to context
        response.context['mcp_class'] = self.__class__.__name__

        return response

    def _log_operation(self, operation: str, params: Dict[str, Any],
                       result: MCPResponse) -> None:
        """
        Log an MCP operation.

        Args:
            operation: Operation name (method name)
            params: Operation parameters
            result: Operation result
        """
        if self.logger:
            try:
                self.logger.log_call(
                    caller=self.context.get('caller', 'unknown'),
                    mcp_class=self.__class__.__name__,
                    operation=operation,
                    params=params,
                    result=result.to_dict(),
                    success=result.success
                )
            except Exception as e:
                # Don't fail operation if logging fails
                print(f"Warning: MCP logging failed: {e}")

    def _validate_inputs(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.

        Override in subclasses for specific validation logic.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Base implementation: check for None in required params
        for key, value in kwargs.items():
            if value is None:
                return False, f"Required parameter '{key}' is None"
        return True, None

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get list of capabilities (methods) provided by this MCP helper.

        Returns:
            List of dictionaries describing each method:
            - name: Method name
            - description: Method docstring (first line)
            - safety_level: Decorator (read_only, write_safe, etc.)
            - parameters: Method parameters
            - returns: Return type

        Example:
            >>> helper = ScriptManager()
            >>> caps = helper.get_capabilities()
            >>> print(caps[0])
            {
                'name': 'read_script',
                'description': 'Read and analyze Python script',
                'safety_level': 'read_only',
                'parameters': ['path'],
                'returns': 'MCPResponse'
            }
        """
        if self._capabilities_cache is not None:
            return self._capabilities_cache

        capabilities = []

        # Introspect all public methods
        for name in dir(self):
            if name.startswith('_'):
                continue

            attr = getattr(self, name)

            # Skip non-callable attributes
            if not callable(attr):
                continue

            # Skip base class methods
            if name in ['get_capabilities']:
                continue

            # Extract method information
            method_info = {
                'name': name,
                'description': self._extract_method_description(attr),
                'safety_level': self._extract_safety_level(attr),
                'parameters': self._extract_parameters(attr),
                'returns': 'MCPResponse'
            }

            capabilities.append(method_info)

        self._capabilities_cache = capabilities
        return capabilities

    def _extract_method_description(self, method: Callable) -> str:
        """Extract first line of docstring"""
        if method.__doc__:
            return method.__doc__.strip().split('\n')[0]
        return ""

    def _extract_safety_level(self, method: Callable) -> str:
        """Extract safety level from decorator metadata"""
        # Check for decorator attributes
        if hasattr(method, '_mcp_safety_level'):
            return method._mcp_safety_level
        return "unknown"

    def _extract_parameters(self, method: Callable) -> List[str]:
        """Extract method parameters"""
        import inspect
        try:
            sig = inspect.signature(method)
            return [
                param.name for param in sig.parameters.values()
                if param.name != 'self'
            ]
        except Exception:
            return []

    def execute(self, operation: str, **kwargs) -> MCPResponse:
        """
        Execute an operation by name.

        This is a generic entry point for dynamic operation invocation.

        Args:
            operation: Name of the operation (method) to execute
            **kwargs: Parameters to pass to the operation

        Returns:
            MCPResponse from the operation

        Example:
            >>> helper = ScriptManager()
            >>> result = helper.execute('read_script', path='script.py')
        """
        # Check if method exists
        if not hasattr(self, operation):
            return MCPResponse.error_response(
                error=f"Operation '{operation}' not found on {self.__class__.__name__}",
                context={'available_operations': [cap['name'] for cap in self.get_capabilities()]}
            )

        method = getattr(self, operation)

        # Check if method is callable
        if not callable(method):
            return MCPResponse.error_response(
                error=f"'{operation}' is not a callable operation"
            )

        # Validate inputs
        is_valid, error_msg = self._validate_inputs(**kwargs)
        if not is_valid:
            return MCPResponse.error_response(
                error=f"Input validation failed: {error_msg}",
                context={'operation': operation, 'params': kwargs}
            )

        # Execute the operation
        try:
            result = method(**kwargs)

            # Log the operation
            self._log_operation(operation, kwargs, result)

            return result
        except Exception as e:
            error_response = MCPResponse.error_response(
                error=f"Operation failed: {str(e)}",
                context={'operation': operation, 'params': kwargs},
                trace=[f"Exception: {type(e).__name__}", str(e)]
            )

            # Log the failed operation
            self._log_operation(operation, kwargs, error_response)

            return error_response

    def __repr__(self) -> str:
        """String representation of the MCP helper"""
        cap_count = len(self.get_capabilities())
        return f"{self.__class__.__name__}(capabilities={cap_count})"
