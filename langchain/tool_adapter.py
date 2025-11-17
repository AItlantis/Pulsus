"""
LangChain Tool Adapter

Converts MCP domains to LangChain StructuredTools for use in LangChain agents.
"""

from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field, create_model
import inspect

from mcp.core.base import MCPBase, MCPResponse


def mcp_to_langchain_tool(mcp_class: Type[MCPBase], operation: Optional[str] = None):
    """
    Convert an MCPBase class or specific operation to a LangChain StructuredTool.

    This function requires langchain-core to be installed. If not available,
    it will return a placeholder dict with capability information.

    Args:
        mcp_class: MCP domain class (e.g., ScriptOps, RepositoryOps)
        operation: Optional specific operation to convert (if None, creates tool for domain)

    Returns:
        LangChain StructuredTool instance or capability dict

    Example:
        >>> from mcp.simple import ScriptOps
        >>> from langchain.agents import AgentExecutor
        >>>
        >>> # Convert entire domain
        >>> tool = mcp_to_langchain_tool(ScriptOps)
        >>>
        >>> # Or convert specific operation
        >>> read_tool = mcp_to_langchain_tool(ScriptOps, 'read_script')
        >>>
        >>> # Use in agent
        >>> agent = AgentExecutor(tools=[tool], ...)
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        # LangChain not available, return capability dict
        instance = mcp_class()
        capabilities = instance.get_capabilities()
        return {
            'domain': mcp_class.__name__,
            'type': 'mcp_domain',
            'capabilities': capabilities,
            'error': 'langchain-core not installed'
        }

    instance = mcp_class()
    capabilities = instance.get_capabilities()

    if operation:
        # Create tool for specific operation
        return _create_operation_tool(instance, operation, capabilities)
    else:
        # Create tool for entire domain
        return _create_domain_tool(instance, capabilities)


def _create_operation_tool(instance: MCPBase, operation: str, capabilities: List[Dict]):
    """
    Create LangChain tool for a specific operation.

    Args:
        instance: MCP domain instance
        operation: Operation name
        capabilities: List of capabilities

    Returns:
        StructuredTool
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        return None

    # Find operation in capabilities
    op_info = next((cap for cap in capabilities if cap['name'] == operation), None)

    if not op_info:
        raise ValueError(f"Operation '{operation}' not found in {instance.__class__.__name__}")

    # Get the actual method
    method = getattr(instance, operation)

    # Extract parameters
    sig = inspect.signature(method)
    params = {}
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        # Determine type
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str

        # Create field
        params[param_name] = (param_type, Field(description=f"Parameter: {param_name}"))

    # Create Pydantic model for parameters
    ArgsSchema = create_model(
        f"{instance.__class__.__name__}_{operation}_Args",
        **params
    )

    # Create wrapper function
    def execute_wrapper(**kwargs) -> Dict[str, Any]:
        """Wrapper that calls MCP operation and converts MCPResponse."""
        result: MCPResponse = instance.execute(operation, **kwargs)
        return result.to_dict()

    # Create StructuredTool
    tool = StructuredTool(
        name=f"{instance.__class__.__name__}_{operation}",
        description=op_info['description'] or f"Execute {operation} on {instance.__class__.__name__}",
        func=execute_wrapper,
        args_schema=ArgsSchema
    )

    return tool


def _create_domain_tool(instance: MCPBase, capabilities: List[Dict]):
    """
    Create LangChain tool for entire domain (generic execute).

    Args:
        instance: MCP domain instance
        capabilities: List of capabilities

    Returns:
        StructuredTool
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        return None

    # Create args schema for generic execute
    ArgsSchema = create_model(
        f"{instance.__class__.__name__}_Args",
        operation=(str, Field(description="Operation name to execute")),
        params=(Dict[str, Any], Field(default={}, description="Operation parameters"))
    )

    # Create wrapper function
    def execute_wrapper(operation: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wrapper that calls MCP execute and converts MCPResponse."""
        params = params or {}
        result: MCPResponse = instance.execute(operation, **params)
        return result.to_dict()

    # Build description
    op_list = ', '.join([cap['name'] for cap in capabilities[:5]])
    description = (
        f"Execute operations on {instance.__class__.__name__}. "
        f"Available operations: {op_list}, ..."
    )

    # Create StructuredTool
    tool = StructuredTool(
        name=instance.__class__.__name__,
        description=description,
        func=execute_wrapper,
        args_schema=ArgsSchema
    )

    return tool


def discover_and_convert_mcp_domains(
    search_paths: Optional[List[str]] = None,
    verbose: bool = False
) -> List[Any]:
    """
    Discover all MCP domain classes and convert them to LangChain tools.

    Args:
        search_paths: Optional list of module paths to search (e.g., ['mcp.simple'])
                     If None, searches common MCP locations
        verbose: Whether to print discovery progress

    Returns:
        List of LangChain tools

    Example:
        >>> tools = discover_and_convert_mcp_domains()
        >>> tools = discover_and_convert_mcp_domains(search_paths=['mcp.simple'])
    """
    import importlib
    import pkgutil

    if search_paths is None:
        search_paths = ['mcp.simple', 'mcp']

    discovered_tools = []

    for search_path in search_paths:
        try:
            # Import the module
            module = importlib.import_module(search_path)

            # Get all classes in the module
            if hasattr(module, '__path__'):
                # It's a package, iterate through submodules
                for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
                    try:
                        submodule = importlib.import_module(f"{search_path}.{modname}")
                        # Find MCPBase subclasses
                        for name in dir(submodule):
                            obj = getattr(submodule, name)
                            if (isinstance(obj, type) and
                                issubclass(obj, MCPBase) and
                                obj is not MCPBase):
                                if verbose:
                                    print(f"Discovered: {obj.__name__}")
                                tool = mcp_to_langchain_tool(obj)
                                if tool:
                                    discovered_tools.append(tool)
                    except Exception as e:
                        if verbose:
                            print(f"Error loading {search_path}.{modname}: {e}")
            else:
                # It's a single module
                for name in dir(module):
                    obj = getattr(module, name)
                    if (isinstance(obj, type) and
                        issubclass(obj, MCPBase) and
                        obj is not MCPBase):
                        if verbose:
                            print(f"Discovered: {obj.__name__}")
                        tool = mcp_to_langchain_tool(obj)
                        if tool:
                            discovered_tools.append(tool)
        except Exception as e:
            if verbose:
                print(f"Error searching {search_path}: {e}")

    return discovered_tools


class MCPToolRegistry:
    """
    Registry for managing MCP tools in LangChain applications.

    Example:
        >>> from mcp.simple import ScriptOps, RepositoryOps
        >>> registry = MCPToolRegistry()
        >>> registry.register_domain(ScriptOps)
        >>> registry.register_domain(RepositoryOps)
        >>> tools = registry.get_all_tools()
        >>> agent = AgentExecutor(tools=tools, ...)
    """

    def __init__(self):
        """Initialize tool registry"""
        self.domains: Dict[str, Type[MCPBase]] = {}
        self.tools: Dict[str, Any] = {}

    def register_domain(self, mcp_class: Type[MCPBase]) -> None:
        """
        Register an MCP domain.

        Args:
            mcp_class: MCP domain class
        """
        domain_name = mcp_class.__name__
        self.domains[domain_name] = mcp_class

        # Create LangChain tool
        tool = mcp_to_langchain_tool(mcp_class)
        if tool:
            self.tools[domain_name] = tool

    def register_operation(
        self,
        mcp_class: Type[MCPBase],
        operation: str
    ) -> None:
        """
        Register a specific operation as a tool.

        Args:
            mcp_class: MCP domain class
            operation: Operation name
        """
        tool_name = f"{mcp_class.__name__}_{operation}"
        tool = mcp_to_langchain_tool(mcp_class, operation)
        if tool:
            self.tools[tool_name] = tool

    def get_tool(self, name: str) -> Optional[Any]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool or None if not found
        """
        return self.tools.get(name)

    def get_all_tools(self) -> List[Any]:
        """
        Get all registered tools.

        Returns:
            List of tools
        """
        return list(self.tools.values())

    def get_domain_capabilities(self, domain_name: str) -> List[Dict[str, Any]]:
        """
        Get capabilities for a domain.

        Args:
            domain_name: Domain name

        Returns:
            List of capabilities
        """
        if domain_name in self.domains:
            instance = self.domains[domain_name]()
            return instance.get_capabilities()
        return []

    def list_domains(self) -> List[str]:
        """
        List all registered domains.

        Returns:
            List of domain names
        """
        return list(self.domains.keys())

    def list_tools(self) -> List[str]:
        """
        List all registered tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())
