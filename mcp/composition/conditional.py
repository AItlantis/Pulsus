"""
Conditional Flows

Provides tools for conditional execution of MCP operations.
"""

from typing import Callable, Dict, Any, Optional

from mcp.core.base import MCPBase, MCPResponse


class ConditionalFlow:
    """
    Conditional operation execution.

    Example:
        >>> from mcp.simple import ScriptOps
        >>> script_ops = ScriptOps()
        >>> flow = ConditionalFlow()
        >>>
        >>> def check_file_size(path):
        ...     return Path(path).stat().st_size > 1000
        >>>
        >>> result = flow.if_then_else(
        ...     condition_fn=lambda: check_file_size('main.py'),
        ...     then_domain=script_ops,
        ...     then_operation='format_script',
        ...     then_params={'path': 'main.py'},
        ...     else_domain=script_ops,
        ...     else_operation='read_script',
        ...     else_params={'path': 'main.py'}
        ... )
    """

    def if_then_else(
        self,
        condition_fn: Callable[[], bool],
        then_domain: MCPBase,
        then_operation: str,
        then_params: Optional[Dict[str, Any]] = None,
        else_domain: Optional[MCPBase] = None,
        else_operation: Optional[str] = None,
        else_params: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """
        Execute operation based on condition.

        Args:
            condition_fn: Function that returns boolean
            then_domain: Domain to execute if condition is True
            then_operation: Operation to execute if condition is True
            then_params: Parameters for then operation
            else_domain: Optional domain to execute if condition is False
            else_operation: Optional operation to execute if condition is False
            else_params: Optional parameters for else operation

        Returns:
            MCPResponse from executed operation
        """
        then_params = then_params or {}
        else_params = else_params or {}

        try:
            # Evaluate condition
            condition_result = condition_fn()

            if condition_result:
                # Execute then branch
                result = then_domain.execute(then_operation, **then_params)
                result.context['conditional'] = {
                    'condition': True,
                    'branch': 'then'
                }
                result.add_trace("Conditional: condition was True, executed 'then' branch")
                return result
            else:
                # Execute else branch (if provided)
                if else_domain and else_operation:
                    result = else_domain.execute(else_operation, **else_params)
                    result.context['conditional'] = {
                        'condition': False,
                        'branch': 'else'
                    }
                    result.add_trace("Conditional: condition was False, executed 'else' branch")
                    return result
                else:
                    # No else branch, return success with skip
                    return MCPResponse.success_response(
                        data={'skipped': True},
                        context={
                            'conditional': {
                                'condition': False,
                                'branch': 'none'
                            }
                        },
                        trace=["Conditional: condition was False, no 'else' branch defined"]
                    )

        except Exception as e:
            return MCPResponse.error_response(
                error=f"Conditional execution failed: {str(e)}",
                context={
                    'exception_type': type(e).__name__
                },
                trace=[
                    "Conditional execution error",
                    f"Exception: {type(e).__name__}",
                    str(e)
                ]
            )

    def if_then(
        self,
        condition_fn: Callable[[], bool],
        then_domain: MCPBase,
        then_operation: str,
        then_params: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """
        Execute operation only if condition is True.

        Args:
            condition_fn: Function that returns boolean
            then_domain: Domain to execute if condition is True
            then_operation: Operation to execute if condition is True
            then_params: Parameters for operation

        Returns:
            MCPResponse from executed operation or skip response
        """
        return self.if_then_else(
            condition_fn=condition_fn,
            then_domain=then_domain,
            then_operation=then_operation,
            then_params=then_params
        )

    def switch(
        self,
        value_fn: Callable[[], Any],
        cases: Dict[Any, tuple[MCPBase, str, Dict[str, Any]]],
        default: Optional[tuple[MCPBase, str, Dict[str, Any]]] = None
    ) -> MCPResponse:
        """
        Switch-case style conditional execution.

        Args:
            value_fn: Function that returns value to match
            cases: Dictionary mapping values to (domain, operation, params)
            default: Optional default case (domain, operation, params)

        Returns:
            MCPResponse from executed operation

        Example:
            >>> def get_file_ext():
            ...     return Path('script.py').suffix
            >>>
            >>> result = flow.switch(
            ...     value_fn=get_file_ext,
            ...     cases={
            ...         '.py': (script_ops, 'format_script', {'path': 'script.py'}),
            ...         '.md': (script_ops, 'write_md', {'path': 'script.py'}),
            ...     },
            ...     default=(script_ops, 'read_script', {'path': 'script.py'})
            ... )
        """
        try:
            # Evaluate value
            value = value_fn()

            # Check if value matches any case
            if value in cases:
                domain, operation, params = cases[value]
                result = domain.execute(operation, **params)
                result.context['switch'] = {
                    'value': str(value),
                    'matched': True,
                    'case': str(value)
                }
                result.add_trace(f"Switch: matched case '{value}'")
                return result
            elif default:
                # Execute default case
                domain, operation, params = default
                result = domain.execute(operation, **params)
                result.context['switch'] = {
                    'value': str(value),
                    'matched': False,
                    'case': 'default'
                }
                result.add_trace(f"Switch: no match for '{value}', executed default")
                return result
            else:
                # No match and no default
                return MCPResponse.success_response(
                    data={'skipped': True},
                    context={
                        'switch': {
                            'value': str(value),
                            'matched': False,
                            'case': 'none'
                        }
                    },
                    trace=[f"Switch: no match for '{value}' and no default case"]
                )

        except Exception as e:
            return MCPResponse.error_response(
                error=f"Switch execution failed: {str(e)}",
                context={
                    'exception_type': type(e).__name__
                },
                trace=[
                    "Switch execution error",
                    f"Exception: {type(e).__name__}",
                    str(e)
                ]
            )
