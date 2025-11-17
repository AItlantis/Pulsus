"""
Operation Chaining

Provides tools for chaining multiple MCP operations together with
error recovery and rollback support.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.core.base import MCPBase, MCPResponse, MCPStatus


class OperationChain:
    """
    Chain multiple MCP operations together with error recovery.

    Example:
        >>> from mcp.simple import ScriptOps
        >>> script_ops = ScriptOps()
        >>> chain = OperationChain("process_script")
        >>> chain.add(script_ops, 'read_script', path='main.py')
        >>> chain.add(script_ops, 'add_comments', path='main.py')
        >>> chain.add(script_ops, 'format_script', path='main.py')
        >>> result = chain.execute()
    """

    def __init__(self, name: str = None):
        """
        Initialize operation chain.

        Args:
            name: Optional name for the chain
        """
        self.name = name or "unnamed_chain"
        self.operations = []
        self.rollback_handlers = {}

    def add(
        self,
        domain: MCPBase,
        operation: str,
        rollback_handler: Optional[callable] = None,
        **kwargs
    ) -> 'OperationChain':
        """
        Add operation to chain.

        Args:
            domain: MCP domain instance
            operation: Operation name to execute
            rollback_handler: Optional function to call for rollback
            **kwargs: Parameters to pass to the operation

        Returns:
            Self (for chaining)
        """
        operation_id = len(self.operations)
        self.operations.append({
            'id': operation_id,
            'domain': domain,
            'operation': operation,
            'kwargs': kwargs
        })

        if rollback_handler:
            self.rollback_handlers[operation_id] = rollback_handler

        return self

    def execute(self, stop_on_error: bool = True) -> MCPResponse:
        """
        Execute chain with error recovery.

        Args:
            stop_on_error: If True, stop execution on first error

        Returns:
            MCPResponse with chain execution results
        """
        started_at = datetime.utcnow().isoformat() + 'Z'
        results = []
        completed_operations = []

        for idx, op in enumerate(self.operations):
            # Execute operation
            try:
                result = op['domain'].execute(op['operation'], **op['kwargs'])

                # Store result
                results.append({
                    'step': idx,
                    'domain': op['domain'].__class__.__name__,
                    'operation': op['operation'],
                    'success': result.success,
                    'data': result.data,
                    'error': result.error
                })

                if result.success:
                    completed_operations.append((idx, result))
                else:
                    # Operation failed
                    if stop_on_error:
                        # Rollback completed operations
                        rollback_results = self._rollback(completed_operations)

                        completed_at = datetime.utcnow().isoformat() + 'Z'

                        return MCPResponse(
                            success=False,
                            error=f"Chain failed at step {idx + 1}/{len(self.operations)}: {result.error}",
                            context={
                                'chain': self.name,
                                'failed_step': idx,
                                'failed_operation': op['operation'],
                                'total_steps': len(self.operations),
                                'completed_steps': idx,
                                'rollback_performed': len(rollback_results) > 0
                            },
                            data={
                                'results': results,
                                'rollback_results': rollback_results,
                                'started_at': started_at,
                                'completed_at': completed_at
                            },
                            status=MCPStatus.ERROR,
                            trace=[
                                f"Chain '{self.name}' started with {len(self.operations)} operations",
                                f"Completed {idx} operations successfully",
                                f"Failed at operation {idx + 1}: {op['operation']}",
                                f"Rolled back {len(rollback_results)} operations"
                            ]
                        )
                    else:
                        # Continue with next operation
                        continue

            except Exception as e:
                # Unexpected exception
                if stop_on_error:
                    rollback_results = self._rollback(completed_operations)

                    completed_at = datetime.utcnow().isoformat() + 'Z'

                    return MCPResponse(
                        success=False,
                        error=f"Chain exception at step {idx + 1}/{len(self.operations)}: {str(e)}",
                        context={
                            'chain': self.name,
                            'failed_step': idx,
                            'exception_type': type(e).__name__,
                            'total_steps': len(self.operations),
                            'completed_steps': idx,
                            'rollback_performed': len(rollback_results) > 0
                        },
                        data={
                            'results': results,
                            'rollback_results': rollback_results,
                            'started_at': started_at,
                            'completed_at': completed_at
                        },
                        status=MCPStatus.ERROR,
                        trace=[
                            f"Chain '{self.name}' started with {len(self.operations)} operations",
                            f"Completed {idx} operations successfully",
                            f"Exception at operation {idx + 1}: {type(e).__name__}",
                            str(e),
                            f"Rolled back {len(rollback_results)} operations"
                        ]
                    )

        # All operations completed successfully
        completed_at = datetime.utcnow().isoformat() + 'Z'

        return MCPResponse(
            success=True,
            data={
                'results': results,
                'started_at': started_at,
                'completed_at': completed_at
            },
            context={
                'chain': self.name,
                'total_steps': len(self.operations),
                'completed_steps': len(results),
                'failed_steps': sum(1 for r in results if not r['success'])
            },
            status=MCPStatus.SUCCESS,
            trace=[
                f"Chain '{self.name}' started with {len(self.operations)} operations",
                f"All {len(results)} operations completed",
                f"Chain execution successful"
            ]
        )

    def _rollback(self, completed_operations: List[tuple]) -> List[Dict[str, Any]]:
        """
        Attempt to rollback completed operations.

        Args:
            completed_operations: List of (operation_id, result) tuples

        Returns:
            List of rollback results
        """
        rollback_results = []

        # Rollback in reverse order
        for op_id, result in reversed(completed_operations):
            if op_id in self.rollback_handlers:
                try:
                    rollback_handler = self.rollback_handlers[op_id]
                    rollback_result = rollback_handler(result)

                    rollback_results.append({
                        'operation_id': op_id,
                        'success': True,
                        'result': rollback_result
                    })
                except Exception as e:
                    rollback_results.append({
                        'operation_id': op_id,
                        'success': False,
                        'error': str(e)
                    })

        return rollback_results

    def __repr__(self) -> str:
        """String representation"""
        return f"OperationChain(name='{self.name}', operations={len(self.operations)})"
