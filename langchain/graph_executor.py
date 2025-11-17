"""
LangGraph Integration

Provides LangGraph StateGraph integration for MCP workflows.
"""

from typing import TypedDict, Annotated, Sequence, Dict, Any, List, Optional


class PulsusState(TypedDict):
    """
    State for Pulsus LangGraph execution.

    This state flows through the graph nodes and contains:
    - messages: Conversation history
    - parsed_intent: User intent parsed from input
    - selected_tools: Tools selected for execution
    - execution_results: Results from tool execution
    - next_action: Next action to take
    """
    messages: Annotated[Sequence[Any], "Conversation history"]
    parsed_intent: Dict[str, Any]
    selected_tools: List[Any]
    execution_results: List[Dict[str, Any]]
    next_action: str


def create_pulsus_graph():
    """
    Create LangGraph StateGraph for Pulsus workflow.

    This function requires langgraph to be installed. If not available,
    it will return a placeholder dict with workflow information.

    Returns:
        Compiled StateGraph or workflow dict

    Example:
        >>> graph = create_pulsus_graph()
        >>> result = graph.invoke({
        ...     'messages': [{'role': 'user', 'content': 'Read script.py'}],
        ...     'parsed_intent': {},
        ...     'selected_tools': [],
        ...     'execution_results': [],
        ...     'next_action': 'parse'
        ... })
    """
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        # LangGraph not available, return placeholder
        return {
            'type': 'pulsus_graph',
            'error': 'langgraph not installed',
            'workflow': {
                'nodes': ['parse_intent', 'discover_tools', 'select_policy', 'execute_tools', 'compose_response'],
                'edges': [
                    ('parse_intent', 'discover_tools'),
                    ('discover_tools', 'select_policy'),
                    ('select_policy', 'execute_tools'),
                    ('execute_tools', 'compose_response')
                ]
            }
        }

    workflow = StateGraph(PulsusState)

    # Add nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("discover_tools", discover_tools_node)
    workflow.add_node("select_policy", select_policy_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("compose_response", compose_response_node)

    # Add edges
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "discover_tools")
    workflow.add_edge("discover_tools", "select_policy")

    # Conditional routing
    workflow.add_conditional_edges(
        "select_policy",
        route_execution_policy,
        {
            "execute": "execute_tools",
            "skip": "compose_response"
        }
    )

    workflow.add_edge("execute_tools", "compose_response")
    workflow.add_edge("compose_response", END)

    return workflow.compile()


def parse_intent_node(state: PulsusState) -> Dict[str, Any]:
    """
    Parse user intent from messages.

    Args:
        state: Current state

    Returns:
        Updated state with parsed intent
    """
    messages = state.get('messages', [])

    if not messages:
        return {
            'parsed_intent': {
                'error': 'No messages to parse'
            }
        }

    # Get last user message
    last_message = messages[-1] if messages else {}
    user_input = last_message.get('content', '')

    # Simple intent parsing (in production, use LLM or NLP)
    intent = {
        'raw_input': user_input,
        'domain': None,
        'operation': None,
        'params': {}
    }

    # Basic keyword matching
    keywords = {
        'read': ('ScriptOps', 'read_script'),
        'format': ('ScriptOps', 'format_script'),
        'comment': ('ScriptOps', 'add_comments'),
        'git status': ('GitOps', 'get_status'),
        'commit': ('GitOps', 'commit'),
    }

    for keyword, (domain, operation) in keywords.items():
        if keyword.lower() in user_input.lower():
            intent['domain'] = domain
            intent['operation'] = operation
            break

    return {
        'parsed_intent': intent
    }


def discover_tools_node(state: PulsusState) -> Dict[str, Any]:
    """
    Discover available tools based on intent.

    Args:
        state: Current state

    Returns:
        Updated state with selected tools
    """
    parsed_intent = state.get('parsed_intent', {})
    domain = parsed_intent.get('domain')
    operation = parsed_intent.get('operation')

    selected_tools = []

    if domain and operation:
        # In production, load actual tool from registry
        selected_tools.append({
            'domain': domain,
            'operation': operation,
            'available': True
        })

    return {
        'selected_tools': selected_tools
    }


def select_policy_node(state: PulsusState) -> Dict[str, Any]:
    """
    Select execution policy.

    Args:
        state: Current state

    Returns:
        Updated state with next action
    """
    selected_tools = state.get('selected_tools', [])

    if not selected_tools:
        return {'next_action': 'skip'}

    # Check if tools are available
    all_available = all(tool.get('available', False) for tool in selected_tools)

    if all_available:
        return {'next_action': 'execute'}
    else:
        return {'next_action': 'skip'}


def route_execution_policy(state: PulsusState) -> str:
    """
    Route based on execution policy.

    Args:
        state: Current state

    Returns:
        Next node name
    """
    next_action = state.get('next_action', 'skip')
    return next_action


def execute_tools_node(state: PulsusState) -> Dict[str, Any]:
    """
    Execute selected tools.

    Args:
        state: Current state

    Returns:
        Updated state with execution results
    """
    selected_tools = state.get('selected_tools', [])
    results = []

    for tool in selected_tools:
        # In production, actually execute the tool
        result = {
            'domain': tool['domain'],
            'operation': tool['operation'],
            'success': True,
            'data': {'message': f"Executed {tool['operation']}"},
            'error': None
        }
        results.append(result)

    return {
        'execution_results': results
    }


def compose_response_node(state: PulsusState) -> Dict[str, Any]:
    """
    Compose final response.

    Args:
        state: Current state

    Returns:
        Updated state with response message
    """
    results = state.get('execution_results', [])
    messages = state.get('messages', [])

    if not results:
        response_message = {
            'role': 'assistant',
            'content': 'No operations were executed.'
        }
    else:
        # Compose response from results
        success_count = sum(1 for r in results if r.get('success', False))
        response_message = {
            'role': 'assistant',
            'content': f"Executed {success_count}/{len(results)} operations successfully."
        }

    return {
        'messages': messages + [response_message]
    }


class PulsusGraphRunner:
    """
    Runner for Pulsus LangGraph workflows.

    Example:
        >>> runner = PulsusGraphRunner()
        >>> result = runner.run("Read the script at main.py")
    """

    def __init__(self):
        """Initialize graph runner"""
        self.graph = create_pulsus_graph()

    def run(self, user_input: str) -> Dict[str, Any]:
        """
        Run workflow with user input.

        Args:
            user_input: User input string

        Returns:
            Workflow result
        """
        if isinstance(self.graph, dict):
            # LangGraph not available
            return {
                'error': self.graph.get('error'),
                'input': user_input
            }

        # Create initial state
        initial_state = {
            'messages': [{'role': 'user', 'content': user_input}],
            'parsed_intent': {},
            'selected_tools': [],
            'execution_results': [],
            'next_action': ''
        }

        # Run graph
        result = self.graph.invoke(initial_state)

        return result

    def is_available(self) -> bool:
        """
        Check if LangGraph is available.

        Returns:
            True if LangGraph is installed
        """
        return not isinstance(self.graph, dict)
