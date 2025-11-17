"""
Parallel Execution

Provides tools for executing multiple MCP operations in parallel.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.core.base import MCPBase, MCPResponse, MCPStatus


class ParallelOperations:
    """
    Execute multiple operations in parallel.

    Example:
        >>> from mcp.simple import ScriptOps
        >>> script_ops = ScriptOps()
        >>> parallel = ParallelOperations(max_workers=4)
        >>> parallel.add(script_ops, 'read_script', path='file1.py')
        >>> parallel.add(script_ops, 'read_script', path='file2.py')
        >>> parallel.add(script_ops, 'read_script', path='file3.py')
        >>> result = parallel.execute()
    """

    def __init__(self, max_workers: int = 4, name: str = None):
        """
        Initialize parallel operations.

        Args:
            max_workers: Maximum number of concurrent workers
            name: Optional name for the parallel execution group
        """
        self.max_workers = max_workers
        self.name = name or "unnamed_parallel"
        self.operations = []

    def add(self, domain: MCPBase, operation: str, **kwargs) -> 'ParallelOperations':
        """
        Add operation to parallel batch.

        Args:
            domain: MCP domain instance
            operation: Operation name to execute
            **kwargs: Parameters to pass to the operation

        Returns:
            Self (for chaining)
        """
        self.operations.append({
            'id': len(self.operations),
            'domain': domain,
            'operation': operation,
            'kwargs': kwargs
        })
        return self

    def execute(self, timeout: Optional[float] = None) -> MCPResponse:
        """
        Execute all operations in parallel.

        Args:
            timeout: Optional timeout in seconds for each operation

        Returns:
            MCPResponse with parallel execution results
        """
        started_at = datetime.utcnow().isoformat() + 'Z'

        if not self.operations:
            return MCPResponse(
                success=True,
                data={'results': []},
                context={
                    'parallel_group': self.name,
                    'operation_count': 0
                },
                trace=["No operations to execute"]
            )

        results = []
        failed_count = 0
        success_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all operations
            future_to_op = {}
            for op in self.operations:
                future = executor.submit(
                    self._execute_operation,
                    op['domain'],
                    op['operation'],
                    op['kwargs']
                )
                future_to_op[future] = op

            # Collect results as they complete
            for future in as_completed(future_to_op, timeout=timeout):
                op = future_to_op[future]

                try:
                    result = future.result(timeout=timeout)

                    results.append({
                        'operation_id': op['id'],
                        'domain': op['domain'].__class__.__name__,
                        'operation': op['operation'],
                        'success': result.success,
                        'data': result.data,
                        'error': result.error
                    })

                    if result.success:
                        success_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    # Operation raised exception
                    results.append({
                        'operation_id': op['id'],
                        'domain': op['domain'].__class__.__name__,
                        'operation': op['operation'],
                        'success': False,
                        'error': f"Exception: {str(e)}",
                        'exception_type': type(e).__name__
                    })
                    failed_count += 1

        # Sort results by operation ID
        results.sort(key=lambda x: x['operation_id'])

        completed_at = datetime.utcnow().isoformat() + 'Z'

        # Determine overall success
        overall_success = failed_count == 0

        return MCPResponse(
            success=overall_success,
            data={
                'results': results,
                'started_at': started_at,
                'completed_at': completed_at
            },
            context={
                'parallel_group': self.name,
                'total_operations': len(self.operations),
                'successful_operations': success_count,
                'failed_operations': failed_count,
                'max_workers': self.max_workers
            },
            status=MCPStatus.SUCCESS if overall_success else MCPStatus.PARTIAL,
            trace=[
                f"Parallel group '{self.name}' started with {len(self.operations)} operations",
                f"Executed with max {self.max_workers} workers",
                f"Completed: {success_count} success, {failed_count} failed"
            ],
            error=f"{failed_count} operations failed" if failed_count > 0 else None
        )

    def _execute_operation(
        self,
        domain: MCPBase,
        operation: str,
        kwargs: Dict[str, Any]
    ) -> MCPResponse:
        """
        Execute a single operation.

        Args:
            domain: MCP domain instance
            operation: Operation name
            kwargs: Operation parameters

        Returns:
            MCPResponse from the operation
        """
        try:
            return domain.execute(operation, **kwargs)
        except Exception as e:
            return MCPResponse.error_response(
                error=f"Operation execution failed: {str(e)}",
                context={
                    'domain': domain.__class__.__name__,
                    'operation': operation,
                    'exception': type(e).__name__
                }
            )

    def __repr__(self) -> str:
        """String representation"""
        return f"ParallelOperations(name='{self.name}', operations={len(self.operations)}, workers={self.max_workers})"
