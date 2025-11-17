"""
MCP Tool Wrappers for LangChain Integration

Provides lightweight tool wrappers that expose MCP class methods as callable
LangChain tools for Pulse and other agents.

This implements Phase 2 & Phase 3 of the MCP class-based integration plan.
"""

from typing import Dict, Any, List, Optional, Callable
from functools import wraps

# MCP Helpers
from agents.mcp.helpers import (
    ScriptManager,
    RepositoryManager,
    ModelInspector,
    LayerManager,
    DataAnalyzer
)

# MCP Core
from agents.mcp.core import MCPResponse, get_mcp_logger


# ===== Tool Wrapper Factory =====

def create_mcp_tool(mcp_instance, method_name: str, tool_name: Optional[str] = None) -> Callable:
    """
    Create a LangChain tool wrapper for an MCP method.

    Args:
        mcp_instance: MCP helper instance (ScriptManager, etc.)
        method_name: Name of the method to wrap
        tool_name: Optional custom tool name (defaults to mcp_{method_name})

    Returns:
        Wrapped function suitable for LangChain StructuredTool
    """
    if tool_name is None:
        tool_name = f"mcp_{method_name}"

    # Get the method
    method = getattr(mcp_instance, method_name)

    # Get method metadata
    capabilities = mcp_instance.get_capabilities()
    method_info = next((cap for cap in capabilities if cap['name'] == method_name), {})

    @wraps(method)
    def tool_wrapper(**kwargs) -> Dict[str, Any]:
        """
        Tool wrapper that calls MCP method and returns standardized dict.

        Returns:
            Dictionary with success, data, error, and metadata
        """
        # Call the MCP method
        result: MCPResponse = method(**kwargs)

        # Convert MCPResponse to dict for LangChain
        return result.to_dict()

    # Enhance wrapper with metadata
    tool_wrapper.__name__ = tool_name
    tool_wrapper.__doc__ = method.__doc__ or f"MCP tool: {method_name}"

    # Add metadata attributes
    tool_wrapper.mcp_method = method_name
    tool_wrapper.safety_level = method_info.get('safety_level', 'unknown')
    tool_wrapper.requires_confirmation = method_info.get('requires_confirmation', False)

    return tool_wrapper


def create_all_tools(mcp_instance) -> Dict[str, Callable]:
    """
    Create tool wrappers for all capabilities of an MCP instance.

    Args:
        mcp_instance: MCP helper instance

    Returns:
        Dictionary of {tool_name: tool_function}
    """
    tools = {}

    capabilities = mcp_instance.get_capabilities()

    for cap in capabilities:
        method_name = cap['name']
        tool_name = f"mcp_{type(mcp_instance).__name__.lower()}_{method_name}"
        tool = create_mcp_tool(mcp_instance, method_name, tool_name)
        tools[tool_name] = tool

    return tools


# ===== Pre-configured Tool Sets =====

class MCPToolRegistry:
    """
    Registry for all MCP tools.

    Provides organized access to MCP helper tools by category.
    """

    def __init__(self, logger=None, context=None):
        """
        Initialize MCP tool registry.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        self.logger = logger or get_mcp_logger()
        self.context = context or {'caller': 'MCPToolRegistry'}

        # Initialize MCP helpers
        self.script_manager = ScriptManager(logger=self.logger, context=self.context)
        self.repository_manager = RepositoryManager(logger=self.logger, context=self.context)
        self.data_analyzer = DataAnalyzer(logger=self.logger, context=self.context)

        # Model/layer helpers (optional - may not be available in all environments)
        try:
            self.model_inspector = ModelInspector(platform='aimsun', logger=self.logger, context=self.context)
        except:
            self.model_inspector = None

        try:
            self.layer_manager = LayerManager(logger=self.logger, context=self.context)
        except:
            self.layer_manager = None

        # Build tool registry
        self._tools = self._build_registry()

    def _build_registry(self) -> Dict[str, Callable]:
        """
        Build the complete tool registry.

        Returns:
            Dictionary of all tools
        """
        tools = {}

        # Script Manager tools
        tools.update(create_all_tools(self.script_manager))

        # Repository Manager tools
        tools.update(create_all_tools(self.repository_manager))

        # Data Analyzer tools
        tools.update(create_all_tools(self.data_analyzer))

        # Model Inspector tools (if available)
        if self.model_inspector:
            tools.update(create_all_tools(self.model_inspector))

        # Layer Manager tools (if available)
        if self.layer_manager:
            tools.update(create_all_tools(self.layer_manager))

        return tools

    def get_all_tools(self) -> Dict[str, Callable]:
        """
        Get all registered tools.

        Returns:
            Dictionary of {tool_name: tool_function}
        """
        return self._tools.copy()

    def get_tools_by_category(self, category: str) -> Dict[str, Callable]:
        """
        Get tools by category.

        Args:
            category: Category name ('script', 'repository', 'model', 'layer', 'data')

        Returns:
            Dictionary of tools in that category
        """
        category_prefix = f"mcp_{category}"
        return {
            name: tool
            for name, tool in self._tools.items()
            if name.startswith(category_prefix)
        }

    def get_tools_by_safety_level(self, safety_level: str) -> Dict[str, Callable]:
        """
        Get tools by safety level.

        Args:
            safety_level: Safety level ('read_only', 'write_safe', etc.)

        Returns:
            Dictionary of tools at that safety level
        """
        return {
            name: tool
            for name, tool in self._tools.items()
            if hasattr(tool, 'safety_level') and tool.safety_level == safety_level
        }

    def get_read_only_tools(self) -> Dict[str, Callable]:
        """Get all read-only tools (safe for plan mode)."""
        return self.get_tools_by_safety_level('read_only')

    def get_write_tools(self) -> Dict[str, Callable]:
        """Get all write tools (require confirmation)."""
        write_levels = ['write_safe', 'restricted_write']
        return {
            name: tool
            for name, tool in self._tools.items()
            if hasattr(tool, 'safety_level') and tool.safety_level in write_levels
        }

    def get_tool_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all tools.

        Returns:
            List of tool metadata dictionaries
        """
        metadata = []

        for name, tool in self._tools.items():
            meta = {
                'name': name,
                'description': tool.__doc__ or '',
                'safety_level': getattr(tool, 'safety_level', 'unknown'),
                'requires_confirmation': getattr(tool, 'requires_confirmation', False),
                'mcp_method': getattr(tool, 'mcp_method', '')
            }
            metadata.append(meta)

        return metadata


# ===== Convenience Functions =====

def get_script_tools(logger=None, context=None) -> Dict[str, Callable]:
    """
    Get all script management tools.

    Args:
        logger: Optional MCPLogger instance
        context: Optional context dict

    Returns:
        Dictionary of script tools
    """
    registry = MCPToolRegistry(logger=logger, context=context)
    return registry.get_tools_by_category('scriptmanager')


def get_repository_tools(logger=None, context=None) -> Dict[str, Callable]:
    """
    Get all repository analysis tools.

    Args:
        logger: Optional MCPLogger instance
        context: Optional context dict

    Returns:
        Dictionary of repository tools
    """
    registry = MCPToolRegistry(logger=logger, context=context)
    return registry.get_tools_by_category('repositorymanager')


def get_data_tools(logger=None, context=None) -> Dict[str, Callable]:
    """
    Get all data analysis tools.

    Args:
        logger: Optional MCPLogger instance
        context: Optional context dict

    Returns:
        Dictionary of data tools
    """
    registry = MCPToolRegistry(logger=logger, context=context)
    return registry.get_tools_by_category('dataanalyzer')


def get_all_mcp_tools(logger=None, context=None) -> Dict[str, Callable]:
    """
    Get all MCP tools.

    Args:
        logger: Optional MCPLogger instance
        context: Optional context dict

    Returns:
        Dictionary of all MCP tools
    """
    registry = MCPToolRegistry(logger=logger, context=context)
    return registry.get_all_tools()


# ===== LangChain Integration Helpers =====

def create_langchain_structured_tools(tool_dict: Dict[str, Callable]) -> List:
    """
    Convert MCP tool dictionary to LangChain StructuredTool objects.

    Args:
        tool_dict: Dictionary of {tool_name: tool_function}

    Returns:
        List of LangChain StructuredTool objects
    """
    try:
        from langchain.tools import StructuredTool
    except ImportError:
        raise ImportError("langchain not installed - cannot create StructuredTool objects")

    structured_tools = []

    for name, func in tool_dict.items():
        # Create StructuredTool
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=func.__doc__ or f"MCP tool: {name}"
        )

        # Add metadata
        if hasattr(func, 'safety_level'):
            tool.metadata = {
                'safety_level': func.safety_level,
                'requires_confirmation': getattr(func, 'requires_confirmation', False),
                'mcp_method': getattr(func, 'mcp_method', '')
            }

        structured_tools.append(tool)

    return structured_tools


def bind_tools_to_agent(agent, tool_dict: Dict[str, Callable]):
    """
    Bind MCP tools to a LangChain agent.

    Args:
        agent: LangChain agent instance
        tool_dict: Dictionary of tools to bind
    """
    try:
        from langchain.tools import StructuredTool
    except ImportError:
        raise ImportError("langchain not installed")

    # Convert to StructuredTool objects
    structured_tools = create_langchain_structured_tools(tool_dict)

    # Bind to agent
    if hasattr(agent, 'tools'):
        agent.tools.extend(structured_tools)
    elif hasattr(agent, 'bind_tools'):
        agent.bind_tools(structured_tools)
    else:
        raise ValueError("Agent does not support tool binding")

    return agent


# ===== Export =====

__all__ = [
    'create_mcp_tool',
    'create_all_tools',
    'MCPToolRegistry',
    'get_script_tools',
    'get_repository_tools',
    'get_data_tools',
    'get_all_mcp_tools',
    'create_langchain_structured_tools',
    'bind_tools_to_agent'
]
