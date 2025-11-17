"""
LangGraph State Definitions

Defines state schemas for Pulsus LangGraph workflows.
These states track execution progress through multi-step MCP operations.
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from operator import add

from mcp.core.base import MCPResponse


class PulsusState(TypedDict):
    """
    State for Pulsus LangGraph execution.

    This state tracks the complete execution flow from user query
    through intent parsing, tool discovery, and execution.

    Attributes:
        messages: Conversation history (accumulated)
        query: Original user query
        parsed_intent: Structured intent from parser
        discovered_tools: Candidate MCP tools found
        selected_policy: Routing policy (SELECT/COMPOSE/GENERATE)
        selected_tools: Tools chosen for execution
        execution_results: Results from MCP execution
        final_response: Aggregated response to user
        next_action: Next node to visit in graph
        error: Error message if execution failed
        metadata: Additional execution metadata
    """
    # Conversation tracking
    messages: Annotated[Sequence[BaseMessage], add]

    # Input
    query: str

    # Intent parsing
    parsed_intent: Optional[Dict[str, Any]]

    # Tool discovery
    discovered_tools: List[Any]  # List of MCPDomain candidates

    # Routing
    selected_policy: Optional[str]  # "SELECT" | "COMPOSE" | "GENERATE"

    # Execution
    selected_tools: List[Any]  # Selected MCP tools
    execution_results: List[Dict[str, Any]]  # MCPResponse dicts

    # Output
    final_response: Optional[str]

    # Control flow
    next_action: str

    # Error handling
    error: Optional[str]

    # Metadata
    metadata: Dict[str, Any]


class WorkflowState(TypedDict):
    """
    State for multi-step workflow execution.

    Used for Tier 2 (Workflow MCP) operations that require
    state management across multiple steps.

    Attributes:
        workflow_name: Name of the workflow
        current_step: Current step being executed
        step_results: Results from each step
        workflow_context: Shared context across steps
        completed_steps: List of completed step names
        failed_steps: List of failed step names
        can_rollback: Whether rollback is possible
        next_step: Next step to execute
        final_result: Final workflow result
    """
    # Workflow identification
    workflow_name: str

    # Step tracking
    current_step: Optional[str]
    step_results: Dict[str, Dict[str, Any]]  # step_name -> result
    workflow_context: Dict[str, Any]  # Shared data

    # Progress tracking
    completed_steps: List[str]
    failed_steps: List[str]

    # Control flow
    can_rollback: bool
    next_step: Optional[str]

    # Output
    final_result: Optional[Dict[str, Any]]


class IntentParsingState(TypedDict):
    """
    State for intent parsing phase.

    Attributes:
        raw_query: Original user query
        normalized_query: Cleaned/normalized query
        extracted_domain: Identified MCP domain
        extracted_action: Identified action
        extracted_params: Identified parameters
        confidence: Parsing confidence (0-1)
        alternatives: Alternative interpretations
    """
    raw_query: str
    normalized_query: Optional[str]
    extracted_domain: Optional[str]
    extracted_action: Optional[str]
    extracted_params: Dict[str, Any]
    confidence: float
    alternatives: List[Dict[str, Any]]


class ToolDiscoveryState(TypedDict):
    """
    State for tool discovery phase.

    Attributes:
        intent: Parsed intent
        candidate_tools: Discovered MCP tools
        scored_tools: Tools with relevance scores
        top_match: Best matching tool
        policy_recommendation: Recommended routing policy
    """
    intent: Dict[str, Any]
    candidate_tools: List[Any]
    scored_tools: List[Dict[str, Any]]  # {tool, score, reason}
    top_match: Optional[Dict[str, Any]]
    policy_recommendation: Optional[str]


class ExecutionState(TypedDict):
    """
    State for MCP execution phase.

    Attributes:
        tools: Tools to execute
        execution_mode: PLAN | EXECUTE | UNSAFE
        approval_required: Whether user approval needed
        approval_granted: Whether approval was granted
        execution_results: Results from each tool
        aggregated_result: Combined result
        execution_trace: Detailed trace of execution
    """
    tools: List[Any]
    execution_mode: str
    approval_required: bool
    approval_granted: bool
    execution_results: List[Dict[str, Any]]
    aggregated_result: Optional[Dict[str, Any]]
    execution_trace: List[str]


# Helper functions for state manipulation

def create_initial_pulsus_state(query: str) -> PulsusState:
    """
    Create initial PulsusState from user query.

    Args:
        query: User's natural language query

    Returns:
        Initialized PulsusState ready for graph execution
    """
    return PulsusState(
        messages=[],
        query=query,
        parsed_intent=None,
        discovered_tools=[],
        selected_policy=None,
        selected_tools=[],
        execution_results=[],
        final_response=None,
        next_action="parse_intent",
        error=None,
        metadata={}
    )


def update_state_with_error(
    state: PulsusState,
    error: str,
    step: str
) -> PulsusState:
    """
    Update state with error information.

    Args:
        state: Current state
        error: Error message
        step: Step where error occurred

    Returns:
        Updated state with error
    """
    state['error'] = error
    state['next_action'] = "error_handler"
    state['metadata']['error_step'] = step
    return state


def merge_execution_results(
    results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge multiple MCP execution results.

    Args:
        results: List of MCPResponse dicts

    Returns:
        Aggregated result
    """
    # Simple merge - can be enhanced with custom logic
    all_successful = all(r.get('success', False) for r in results)
    combined_data = [r.get('data') for r in results if r.get('data')]
    combined_trace = []
    for r in results:
        combined_trace.extend(r.get('trace', []))

    return {
        'success': all_successful,
        'data': combined_data,
        'trace': combined_trace,
        'metadata': {
            'num_results': len(results),
            'all_successful': all_successful
        }
    }


# Export public API
__all__ = [
    'PulsusState',
    'WorkflowState',
    'IntentParsingState',
    'ToolDiscoveryState',
    'ExecutionState',
    'create_initial_pulsus_state',
    'update_state_with_error',
    'merge_execution_results',
]
