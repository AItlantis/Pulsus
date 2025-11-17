"""
WorkflowOps - Workflow Orchestration MCP Domain

Provides workflow management and orchestration capabilities for complex multi-step operations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    domain: str
    operation: str
    params: Dict[str, Any]
    required: bool = True
    retry_count: int = 0
    max_retries: int = 3
    on_error: Optional[str] = None  # 'continue', 'abort', 'retry'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WorkflowResult:
    """Represents the result of a workflow execution"""
    workflow_name: str
    status: str  # 'success', 'partial', 'failed'
    started_at: str
    completed_at: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    step_results: List[Dict[str, Any]]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class WorkflowOps(MCPBase):
    """
    Workflow orchestration and management.

    Capabilities:
    - load_workflow: Load workflow from JSON definition
    - execute_workflow: Execute a workflow
    - validate_workflow: Validate workflow definition
    - list_workflows: List available workflow definitions
    - save_workflow: Save workflow definition
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """Initialize WorkflowOps domain"""
        super().__init__(logger, context)
        self.workflow_dir = Path("workflows")

    @read_only
    def load_workflow(self, workflow_path: str) -> MCPResponse:
        """
        Load a workflow definition from JSON file.

        Args:
            workflow_path: Path to workflow JSON file

        Returns:
            MCPResponse with workflow definition
        """
        response = self._create_response()
        response.add_trace("Loading workflow definition")

        path = Path(workflow_path)

        if not path.exists():
            response.set_error(f"Workflow file not found: {workflow_path}")
            return response

        try:
            with open(path, 'r') as f:
                workflow_data = json.load(f)

            # Validate basic structure
            required_fields = ['name', 'steps']
            for field in required_fields:
                if field not in workflow_data:
                    response.set_error(f"Missing required field: {field}")
                    return response

            response.data = {
                'path': str(path),
                'workflow': workflow_data,
                'step_count': len(workflow_data.get('steps', []))
            }

            response.add_trace(f"Loaded workflow with {len(workflow_data.get('steps', []))} steps")
            return response

        except json.JSONDecodeError as e:
            response.set_error(f"Invalid JSON in workflow file: {e}")
            return response
        except Exception as e:
            response.set_error(f"Failed to load workflow: {e}")
            return response

    @read_only
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> MCPResponse:
        """
        Validate a workflow definition.

        Args:
            workflow_data: Workflow definition dictionary

        Returns:
            MCPResponse with validation results
        """
        response = self._create_response()
        response.add_trace("Validating workflow")

        errors = []
        warnings = []

        # Check required fields
        required_fields = ['name', 'steps']
        for field in required_fields:
            if field not in workflow_data:
                errors.append(f"Missing required field: {field}")

        # Validate steps
        if 'steps' in workflow_data:
            steps = workflow_data['steps']
            if not isinstance(steps, list):
                errors.append("'steps' must be a list")
            else:
                for idx, step in enumerate(steps):
                    step_name = step.get('name', f'step_{idx}')

                    # Check required step fields
                    required_step_fields = ['domain', 'operation']
                    for field in required_step_fields:
                        if field not in step:
                            errors.append(f"Step '{step_name}': Missing required field '{field}'")

                    # Validate params
                    if 'params' in step and not isinstance(step['params'], dict):
                        errors.append(f"Step '{step_name}': 'params' must be a dictionary")

                    # Validate on_error
                    if 'on_error' in step:
                        valid_actions = ['continue', 'abort', 'retry']
                        if step['on_error'] not in valid_actions:
                            warnings.append(
                                f"Step '{step_name}': 'on_error' should be one of {valid_actions}"
                            )

        is_valid = len(errors) == 0

        response.data = {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }

        if is_valid:
            response.add_trace("Workflow is valid")
        else:
            response.add_trace(f"Workflow has {len(errors)} errors")

        return response

    @read_only
    def list_workflows(self, directory: Optional[str] = None) -> MCPResponse:
        """
        List available workflow definitions.

        Args:
            directory: Optional directory to search (defaults to workflows/)

        Returns:
            MCPResponse with list of workflows
        """
        response = self._create_response()
        response.add_trace("Listing workflows")

        workflow_dir = Path(directory) if directory else self.workflow_dir

        if not workflow_dir.exists():
            response.set_error(f"Workflow directory not found: {workflow_dir}")
            return response

        workflows = []
        for file in workflow_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)

                workflows.append({
                    'path': str(file),
                    'name': data.get('name', file.stem),
                    'description': data.get('description', ''),
                    'step_count': len(data.get('steps', []))
                })
            except Exception as e:
                # Skip invalid files
                continue

        response.data = {
            'directory': str(workflow_dir),
            'workflows': workflows,
            'count': len(workflows)
        }

        response.add_trace(f"Found {len(workflows)} workflows")
        return response

    @write_safe
    def save_workflow(
        self,
        workflow_data: Dict[str, Any],
        output_path: str,
        overwrite: bool = False
    ) -> MCPResponse:
        """
        Save a workflow definition to JSON file.

        Args:
            workflow_data: Workflow definition dictionary
            output_path: Path to save the workflow
            overwrite: If True, overwrite existing file

        Returns:
            MCPResponse with save result
        """
        response = self._create_response()
        response.add_trace("Saving workflow")

        path = Path(output_path)

        # Check if file exists
        if path.exists() and not overwrite:
            response.set_error(f"File already exists: {output_path}. Use overwrite=True to replace.")
            return response

        # Validate workflow first
        validation = self.validate_workflow(workflow_data)
        if not validation.data['valid']:
            response.set_error(
                f"Workflow is invalid: {', '.join(validation.data['errors'])}"
            )
            return response

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save workflow
            with open(path, 'w') as f:
                json.dump(workflow_data, f, indent=2)

            response.data = {
                'path': str(path),
                'name': workflow_data.get('name', 'unnamed'),
                'step_count': len(workflow_data.get('steps', []))
            }

            response.add_trace(f"Workflow saved to {path}")
            return response

        except Exception as e:
            response.set_error(f"Failed to save workflow: {e}")
            return response

    def execute_workflow(
        self,
        workflow_data: Dict[str, Any],
        domain_registry: Optional[Dict[str, MCPBase]] = None
    ) -> MCPResponse:
        """
        Execute a workflow.

        Note: This is a basic implementation. For production use, consider using
        the composition/chain.py module for more advanced features.

        Args:
            workflow_data: Workflow definition dictionary
            domain_registry: Optional registry of domain instances (domain_name -> MCPBase)

        Returns:
            MCPResponse with workflow execution results
        """
        response = self._create_response()
        response.add_trace("Executing workflow")

        # Validate workflow
        validation = self.validate_workflow(workflow_data)
        if not validation.data['valid']:
            response.set_error(
                f"Workflow is invalid: {', '.join(validation.data['errors'])}"
            )
            return response

        workflow_name = workflow_data.get('name', 'unnamed')
        steps = workflow_data.get('steps', [])

        started_at = datetime.utcnow().isoformat() + 'Z'
        step_results = []
        completed_steps = 0
        failed_steps = 0

        # Execute each step
        for idx, step_data in enumerate(steps):
            step_name = step_data.get('name', f'step_{idx}')
            domain_name = step_data.get('domain')
            operation = step_data.get('operation')
            params = step_data.get('params', {})
            required = step_data.get('required', True)
            on_error = step_data.get('on_error', 'abort')

            response.add_trace(f"Executing step: {step_name}")

            # Check if domain is available
            if domain_registry and domain_name in domain_registry:
                domain = domain_registry[domain_name]

                try:
                    # Execute operation
                    result = domain.execute(operation, **params)

                    step_result = {
                        'step_name': step_name,
                        'domain': domain_name,
                        'operation': operation,
                        'success': result.success,
                        'error': result.error,
                        'data': result.data
                    }

                    step_results.append(step_result)

                    if result.success:
                        completed_steps += 1
                        response.add_trace(f"Step '{step_name}' completed successfully")
                    else:
                        failed_steps += 1
                        response.add_trace(f"Step '{step_name}' failed: {result.error}")

                        # Handle error based on on_error strategy
                        if required and on_error == 'abort':
                            response.set_error(
                                f"Workflow aborted at step '{step_name}': {result.error}"
                            )
                            break
                        elif on_error == 'continue':
                            continue
                        # For 'retry', would need more complex logic

                except Exception as e:
                    failed_steps += 1
                    step_result = {
                        'step_name': step_name,
                        'domain': domain_name,
                        'operation': operation,
                        'success': False,
                        'error': str(e)
                    }
                    step_results.append(step_result)
                    response.add_trace(f"Step '{step_name}' exception: {e}")

                    if required and on_error == 'abort':
                        response.set_error(f"Workflow aborted at step '{step_name}': {e}")
                        break
            else:
                # Domain not available
                failed_steps += 1
                step_result = {
                    'step_name': step_name,
                    'domain': domain_name,
                    'operation': operation,
                    'success': False,
                    'error': f"Domain '{domain_name}' not available"
                }
                step_results.append(step_result)

                if required and on_error == 'abort':
                    response.set_error(
                        f"Workflow aborted: Domain '{domain_name}' not available"
                    )
                    break

        completed_at = datetime.utcnow().isoformat() + 'Z'

        # Determine overall status
        if failed_steps == 0:
            status = 'success'
        elif completed_steps > 0:
            status = 'partial'
        else:
            status = 'failed'

        workflow_result = WorkflowResult(
            workflow_name=workflow_name,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            total_steps=len(steps),
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            step_results=step_results,
            error=response.error
        )

        response.data = workflow_result.to_dict()

        if status == 'success':
            response.success = True
            response.add_trace(f"Workflow completed successfully: {completed_steps}/{len(steps)} steps")
        elif status == 'partial':
            response.success = False
            response.add_trace(
                f"Workflow partially completed: {completed_steps}/{len(steps)} steps, {failed_steps} failed"
            )
        else:
            response.success = False
            response.add_trace(f"Workflow failed: {failed_steps}/{len(steps)} steps failed")

        return response
