"""
LangChain Tool Adapter

Converts Pulsus MCPBase domains to LangChain StructuredTool instances,
enabling MCP operations to be used in any LangChain-based system.
"""

from typing import Type, Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field, create_model
from langchain_core.tools import StructuredTool

from mcp.core.base import MCPBase, MCPResponse


def _generate_args_schema(
    actions: Dict[str, Dict[str, Any]]
) -> Type[BaseModel]:
    """
    Generate Pydantic model for tool arguments from action schemas.

    Args:
        actions: Dictionary mapping action names to their parameter schemas

    Returns:
        Pydantic BaseModel class for argument validation

    Example:
        >>> actions = {
        ...     "read_script": {
        ...         "params": {
        ...             "path": {"type": "str", "description": "File path"}
        ...         }
        ...     }
        ... }
        >>> schema = _generate_args_schema(actions)
    """
    # For now, create a flexible schema that accepts action and params
    # In Phase 2, we'll make this more specific per-action

    class MCPToolArgs(BaseModel):
        """Arguments for MCP tool execution"""
        action: str = Field(
            description="The MCP action to execute"
        )
        params: Dict[str, Any] = Field(
            default_factory=dict,
            description="Parameters for the action"
        )

    return MCPToolArgs


def mcp_to_langchain_tool(
    mcp_class: Type[MCPBase],
    verbose: bool = False
) -> StructuredTool:
    """
    Convert an MCPBase class to a LangChain StructuredTool.

    This adapter enables Pulsus MCP domains to be used as standard
    LangChain tools in agents, chains, and workflows.

    Args:
        mcp_class: MCP domain class (must inherit from MCPBase)
        verbose: Enable verbose logging

    Returns:
        LangChain StructuredTool instance

    Example:
        >>> from pulsus.mcp.simple import ScriptOps
        >>> from pulsus.langchain import mcp_to_langchain_tool
        >>>
        >>> # Convert to LangChain tool
        >>> script_tool = mcp_to_langchain_tool(ScriptOps)
        >>>
        >>> # Use in LangChain agent
        >>> from langchain.agents import AgentExecutor
        >>> agent = AgentExecutor(tools=[script_tool], ...)
        >>> result = agent.invoke("Read example.py")

    Integration with LangGraph:
        >>> from langgraph.graph import StateGraph
        >>> from pulsus.langchain import create_pulsus_graph
        >>>
        >>> graph = create_pulsus_graph()
        >>> result = graph.invoke({
        ...     "messages": [HumanMessage("Format my scripts")],
        ...     "tools": [script_tool]
        ... })
    """
    # Validate that class inherits from MCPBase
    if not issubclass(mcp_class, MCPBase):
        raise TypeError(
            f"{mcp_class.__name__} must inherit from MCPBase"
        )

    # Create instance to get capabilities
    instance = mcp_class()
    capabilities = instance.get_capabilities()

    # Extract metadata
    domain_name = capabilities.get('domain', mcp_class.__name__)
    description = capabilities.get('description', 'MCP domain operations')
    actions = capabilities.get('actions', {})

    # Create wrapper function for LangChain
    def execute_wrapper(**kwargs) -> Dict[str, Any]:
        """
        Wrapper that calls MCPBase.execute() and converts MCPResponse.

        Args:
            **kwargs: Tool arguments (action, params)

        Returns:
            Dictionary representation of MCPResponse
        """
        action = kwargs.get('action')
        params = kwargs.get('params', {})

        if verbose:
            print(f"[LangChain→Pulsus] Executing {domain_name}.{action}")
            print(f"[LangChain→Pulsus] Params: {params}")

        # Execute MCP operation
        response: MCPResponse = instance.execute(
            action=action,
            params=params
        )

        if verbose:
            print(f"[Pulsus→LangChain] Success: {response.success}")
            if not response.success:
                print(f"[Pulsus→LangChain] Error: {response.error}")

        # Convert to dict for LangChain
        return response.to_dict()

    # Generate argument schema
    args_schema = _generate_args_schema(actions)

    # Create LangChain StructuredTool
    tool = StructuredTool(
        name=domain_name,
        description=description,
        func=execute_wrapper,
        args_schema=args_schema,
        return_direct=False  # Allow agent to process result
    )

    return tool


def create_mcp_tool_collection(
    mcp_classes: List[Type[MCPBase]],
    verbose: bool = False
) -> List[StructuredTool]:
    """
    Convert multiple MCP domains to LangChain tools.

    Args:
        mcp_classes: List of MCP domain classes
        verbose: Enable verbose logging

    Returns:
        List of LangChain StructuredTool instances

    Example:
        >>> from pulsus.mcp.simple import ScriptOps, RepositoryOps
        >>> from pulsus.langchain import create_mcp_tool_collection
        >>>
        >>> tools = create_mcp_tool_collection([ScriptOps, RepositoryOps])
        >>>
        >>> # Use in agent
        >>> agent = AgentExecutor(tools=tools, ...)
    """
    tools = []
    for mcp_class in mcp_classes:
        try:
            tool = mcp_to_langchain_tool(mcp_class, verbose=verbose)
            tools.append(tool)
        except Exception as e:
            print(f"Warning: Failed to convert {mcp_class.__name__}: {e}")

    return tools


def discover_and_convert_mcp_domains(
    search_paths: Optional[List[str]] = None,
    verbose: bool = False
) -> List[StructuredTool]:
    """
    Dynamically discover MCP domains and convert to LangChain tools.

    This implements the "explorer on fly" pattern - instead of hardcoding
    available MCPs, it discovers them dynamically from the codebase.

    Args:
        search_paths: Directories to search (default: ['mcp/simple/', 'mcp/'])
        verbose: Enable verbose logging

    Returns:
        List of discovered LangChain tools

    Example:
        >>> from pulsus.langchain import discover_and_convert_mcp_domains
        >>>
        >>> # Discover all available MCP tools
        >>> tools = discover_and_convert_mcp_domains()
        >>> print(f"Found {len(tools)} MCP tools")
        >>>
        >>> # Use in agent
        >>> agent = AgentExecutor(tools=tools, ...)

    Note:
        This is the foundation for the "flexible architecture based on latest
        Claude MCP" requirement - Pulsus doesn't maintain a hardcoded list,
        but discovers available MCPs dynamically.
    """
    import importlib
    import inspect
    from pathlib import Path

    if search_paths is None:
        search_paths = ['mcp.simple', 'mcp.helpers']

    discovered_classes = []

    for module_path in search_paths:
        try:
            # Import module
            module = importlib.import_module(module_path)

            # Find all MCPBase subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, MCPBase) and
                    obj != MCPBase):
                    discovered_classes.append(obj)
                    if verbose:
                        print(f"[Discovery] Found MCP: {obj.__name__}")

        except ImportError as e:
            if verbose:
                print(f"[Discovery] Could not import {module_path}: {e}")
            continue

    # Convert to LangChain tools
    tools = create_mcp_tool_collection(discovered_classes, verbose=verbose)

    return tools


# Export public API
__all__ = [
    'mcp_to_langchain_tool',
    'create_mcp_tool_collection',
    'discover_and_convert_mcp_domains',
]
