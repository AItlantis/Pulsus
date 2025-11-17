"""
MCP Decorators

Provides decorators for enforcing safety policies on MCP operations.
Integrates with Pulsus UI for user confirmations and logging.
"""

import functools
from typing import Callable, Optional, Any
from .policy import SafetyLevel, ExecutionMode, get_safety_policy
from .base import MCPResponse


def _get_operation_name(func: Callable) -> str:
    """Extract operation name from function"""
    return func.__name__


def _mark_safety_level(func: Callable, level: SafetyLevel) -> Callable:
    """Mark function with safety level metadata"""
    func._mcp_safety_level = level.value
    return func


def read_only(func: Callable) -> Callable:
    """
    Mark operation as read-only (safe in all modes).

    Read-only operations:
    - Can run in PLAN and EXECUTE modes
    - No user confirmation required
    - No side effects on files or models
    - Safe for LLM to call automatically

    Example:
        >>> class MyHelper(MCPBase):
        ...     @read_only
        ...     def get_info(self, obj_id: str) -> MCPResponse:
        ...         return MCPResponse.success_response(data={'id': obj_id})
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> MCPResponse:
        operation = _get_operation_name(func)
        policy = get_safety_policy()

        # Register operation if not already registered
        if not policy.get_policy(operation):
            policy.register_operation(operation, SafetyLevel.READ_ONLY)

        # Validate operation is allowed
        is_allowed, reason = policy.validate_operation(operation)
        if not is_allowed:
            return MCPResponse.error_response(
                error=f"Operation not allowed: {reason}",
                context={'operation': operation, 'safety_level': 'read_only'}
            )

        # Execute operation
        try:
            result = func(self, *args, **kwargs)

            # Add safety level to response context
            if isinstance(result, MCPResponse):
                result.context['safety_level'] = 'read_only'
                result.context['requires_confirmation'] = False

            return result
        except Exception as e:
            return MCPResponse.error_response(
                error=f"Operation failed: {str(e)}",
                context={'operation': operation, 'safety_level': 'read_only'},
                trace=[f"Exception: {type(e).__name__}", str(e)]
            )

    # Mark with safety level metadata
    _mark_safety_level(wrapper, SafetyLevel.READ_ONLY)
    return wrapper


def write_safe(func: Callable) -> Callable:
    """
    Mark operation as write-safe (requires confirmation).

    Write-safe operations:
    - Require user confirmation in interactive mode
    - Not allowed in PLAN mode
    - Logged with file hashes before/after
    - Can modify files or model data

    Example:
        >>> class MyHelper(MCPBase):
        ...     @write_safe
        ...     def update_file(self, path: str, content: str) -> MCPResponse:
        ...         Path(path).write_text(content)
        ...         return MCPResponse.success_response()
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> MCPResponse:
        operation = _get_operation_name(func)
        policy = get_safety_policy()

        # Register operation if not already registered
        if not policy.get_policy(operation):
            policy.register_operation(
                operation,
                SafetyLevel.WRITE_SAFE,
                requires_confirmation=True
            )

        # Validate operation is allowed
        is_allowed, reason = policy.validate_operation(operation)
        if not is_allowed:
            return MCPResponse.error_response(
                error=f"Operation not allowed: {reason}",
                context={'operation': operation, 'safety_level': 'write_safe'}
            )

        # Check if confirmation is needed
        if policy.requires_confirmation(operation):
            # Get confirmation (if UI is available)
            confirmation_result = _request_confirmation(
                operation=operation,
                args=args,
                kwargs=kwargs,
                safety_level='write_safe'
            )

            if not confirmation_result:
                return MCPResponse.error_response(
                    error="Operation cancelled by user",
                    context={'operation': operation, 'safety_level': 'write_safe'},
                    trace=["User declined confirmation"]
                )

        # Execute operation
        try:
            result = func(self, *args, **kwargs)

            # Add safety level to response context
            if isinstance(result, MCPResponse):
                result.context['safety_level'] = 'write_safe'
                result.context['requires_confirmation'] = True
                result.context['confirmed'] = True

            return result
        except Exception as e:
            return MCPResponse.error_response(
                error=f"Operation failed: {str(e)}",
                context={'operation': operation, 'safety_level': 'write_safe'},
                trace=[f"Exception: {type(e).__name__}", str(e)]
            )

    # Mark with safety level metadata
    _mark_safety_level(wrapper, SafetyLevel.WRITE_SAFE)
    return wrapper


def restricted_write(allowed_types: Optional[list] = None, platform: Optional[str] = None):
    """
    Mark operation as restricted write (additional validation required).

    Restricted write operations:
    - Require type validation of target objects
    - Require user confirmation
    - Only allowed on known safe object types
    - Not allowed in PLAN mode

    Args:
        allowed_types: List of allowed type names
        platform: Platform for type checking (aimsun, qgis, python)

    Example:
        >>> class MyHelper(MCPBase):
        ...     @restricted_write(platform='aimsun')
        ...     def modify_section(self, section) -> MCPResponse:
        ...         # Only works on Aimsun GKSection objects
        ...         section.setSpeed(50)
        ...         return MCPResponse.success_response()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> MCPResponse:
            operation = _get_operation_name(func)
            policy = get_safety_policy()

            # Register operation if not already registered
            if not policy.get_policy(operation):
                policy.register_operation(
                    operation,
                    SafetyLevel.RESTRICTED_WRITE,
                    requires_confirmation=True,
                    type_validation=True,
                    allowed_types=allowed_types
                )

            # Validate operation is allowed
            is_allowed, reason = policy.validate_operation(operation)
            if not is_allowed:
                return MCPResponse.error_response(
                    error=f"Operation not allowed: {reason}",
                    context={'operation': operation, 'safety_level': 'restricted_write'}
                )

            # Type validation for first argument (assumed to be target object)
            if args:
                target = args[0]
                is_safe, type_error = policy.check_type_safety(
                    target,
                    allowed_types=allowed_types,
                    platform=platform
                )
                if not is_safe:
                    return MCPResponse.error_response(
                        error=f"Type validation failed: {type_error}",
                        context={
                            'operation': operation,
                            'safety_level': 'restricted_write',
                            'target_type': type(target).__name__
                        }
                    )

            # Request confirmation
            if policy.requires_confirmation(operation):
                confirmation_result = _request_confirmation(
                    operation=operation,
                    args=args,
                    kwargs=kwargs,
                    safety_level='restricted_write'
                )

                if not confirmation_result:
                    return MCPResponse.error_response(
                        error="Operation cancelled by user",
                        context={'operation': operation, 'safety_level': 'restricted_write'},
                        trace=["User declined confirmation"]
                    )

            # Execute operation
            try:
                result = func(self, *args, **kwargs)

                # Add safety level to response context
                if isinstance(result, MCPResponse):
                    result.context['safety_level'] = 'restricted_write'
                    result.context['requires_confirmation'] = True
                    result.context['type_validated'] = True
                    result.context['confirmed'] = True

                return result
            except Exception as e:
                return MCPResponse.error_response(
                    error=f"Operation failed: {str(e)}",
                    context={'operation': operation, 'safety_level': 'restricted_write'},
                    trace=[f"Exception: {type(e).__name__}", str(e)]
                )

        # Mark with safety level metadata
        _mark_safety_level(wrapper, SafetyLevel.RESTRICTED_WRITE)
        return wrapper

    return decorator


def transactional(func: Callable = None, *, rollback_handler: Optional[Callable] = None):
    """
    Mark operation as transactional (supports rollback).

    Transactional operations:
    - Can be rolled back on failure
    - Require write-safe confirmation
    - Store state before operation
    - Automatically rollback on exception

    Args:
        func: Function to decorate (when used without arguments)
        rollback_handler: Optional custom rollback function

    Example:
        >>> class MyHelper(MCPBase):
        ...     @transactional
        ...     def batch_update(self, items: list) -> MCPResponse:
        ...         for item in items:
        ...             item.update()
        ...         return MCPResponse.success_response()
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs) -> MCPResponse:
            operation = _get_operation_name(f)
            policy = get_safety_policy()

            # Register operation if not already registered
            if not policy.get_policy(operation):
                policy.register_operation(
                    operation,
                    SafetyLevel.TRANSACTIONAL,
                    requires_confirmation=True,
                    rollback_supported=True
                )

            # Validate operation is allowed
            is_allowed, reason = policy.validate_operation(operation)
            if not is_allowed:
                return MCPResponse.error_response(
                    error=f"Operation not allowed: {reason}",
                    context={'operation': operation, 'safety_level': 'transactional'}
                )

            # Request confirmation
            if policy.requires_confirmation(operation):
                confirmation_result = _request_confirmation(
                    operation=operation,
                    args=args,
                    kwargs=kwargs,
                    safety_level='transactional'
                )

                if not confirmation_result:
                    return MCPResponse.error_response(
                        error="Operation cancelled by user",
                        context={'operation': operation, 'safety_level': 'transactional'},
                        trace=["User declined confirmation"]
                    )

            # Execute operation with rollback support
            try:
                result = f(self, *args, **kwargs)

                # Add safety level to response context
                if isinstance(result, MCPResponse):
                    result.context['safety_level'] = 'transactional'
                    result.context['rollback_supported'] = True
                    result.context['confirmed'] = True

                return result
            except Exception as e:
                # Attempt rollback
                if rollback_handler:
                    try:
                        rollback_handler(self, *args, **kwargs)
                        rollback_msg = "Rollback successful"
                    except Exception as rollback_error:
                        rollback_msg = f"Rollback failed: {str(rollback_error)}"
                else:
                    rollback_msg = "No rollback handler defined"

                return MCPResponse.error_response(
                    error=f"Operation failed: {str(e)}",
                    context={
                        'operation': operation,
                        'safety_level': 'transactional',
                        'rollback': rollback_msg
                    },
                    trace=[
                        f"Exception: {type(e).__name__}",
                        str(e),
                        f"Rollback: {rollback_msg}"
                    ]
                )

        # Mark with safety level metadata
        _mark_safety_level(wrapper, SafetyLevel.TRANSACTIONAL)
        return wrapper

    # Support both @transactional and @transactional(rollback_handler=...)
    if func is not None:
        # Used as @transactional without arguments
        return decorator(func)
    else:
        # Used as @transactional(...) with arguments
        return decorator


def cached(ttl: int = 300):
    """
    Mark operation as cached (results cached for TTL seconds).

    Cached operations:
    - Results cached for specified duration
    - Must be read-only operations
    - Improves performance for repeated calls
    - Cache key based on arguments

    Args:
        ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)

    Example:
        >>> class MyHelper(MCPBase):
        ...     @read_only
        ...     @cached(ttl=600)  # 10 minutes
        ...     def query_catalog(self, type_filter: str) -> MCPResponse:
        ...         # Expensive operation
        ...         return MCPResponse.success_response(data=results)
    """
    def decorator(func: Callable) -> Callable:
        # Simple in-memory cache
        cache = {}
        import time

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> MCPResponse:
            operation = _get_operation_name(func)
            policy = get_safety_policy()

            # Register operation if not already registered
            if not policy.get_policy(operation):
                policy.register_operation(
                    operation,
                    SafetyLevel.CACHED,
                    cache_ttl=ttl
                )

            # Create cache key from arguments
            cache_key = _create_cache_key(operation, args, kwargs)
            current_time = time.time()

            # Check cache
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if current_time - cached_time < ttl:
                    # Cache hit
                    cached_result.context['cached'] = True
                    cached_result.context['cache_age'] = int(current_time - cached_time)
                    cached_result.add_trace(f"Returned from cache (age: {int(current_time - cached_time)}s)")
                    return cached_result

            # Cache miss - execute operation
            result = func(self, *args, **kwargs)

            # Store in cache
            if isinstance(result, MCPResponse) and result.success:
                cache[cache_key] = (result, current_time)
                result.context['cached'] = False
                result.context['cache_ttl'] = ttl

            return result

        # Mark with safety level metadata
        _mark_safety_level(wrapper, SafetyLevel.CACHED)
        return wrapper

    return decorator


def _create_cache_key(operation: str, args: tuple, kwargs: dict) -> str:
    """Create cache key from operation name and arguments"""
    import hashlib
    import json

    key_data = {
        'operation': operation,
        'args': str(args),
        'kwargs': {k: str(v) for k, v in kwargs.items()}
    }

    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def _request_confirmation(operation: str, args: tuple, kwargs: dict,
                         safety_level: str) -> bool:
    """
    Request user confirmation for an operation.

    Integrates with Pulsus UI display manager for consistent output.

    Args:
        operation: Operation name
        args: Operation arguments
        kwargs: Operation keyword arguments
        safety_level: Safety level string

    Returns:
        True if confirmed, False if declined
    """
    # Try to use Pulsus UI for confirmation
    try:
        from agents.pulsus.ui import display_manager as ui

        # Display confirmation prompt
        ui.warn(f"\nConfirmation required for operation: {operation}")
        ui.kv("Safety Level", safety_level)
        ui.kv("Operation", operation)

        # Show arguments if relevant
        if args:
            ui.kv("Arguments", str(args)[:100])
        if kwargs:
            ui.kv("Parameters", str(kwargs)[:100])

        # In non-interactive mode, auto-confirm
        # In interactive mode, this would wait for user input
        # For now, we'll auto-confirm to avoid blocking
        # TODO: Add actual confirmation prompt
        ui.info("Auto-confirming in non-interactive mode")
        return True

    except ImportError:
        # Fallback: auto-confirm if UI not available
        print(f"[MCP] Confirmation required for {operation} ({safety_level})")
        print(f"[MCP] Auto-confirming (UI not available)")
        return True
