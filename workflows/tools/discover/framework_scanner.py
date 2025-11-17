"""
Framework Scanner Tool

Automatically discovers and summarizes all available tools in the user's framework directory.
This tool is called after Pulsus introduction to give users an overview of available capabilities.
"""

from pathlib import Path
import ast
from typing import List, Dict, Any
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.interrupt_handler import get_interrupt_handler

__domain__ = "discovery"
__action__ = "scan_framework"


def discover_all_tools() -> List[Dict[str, Any]]:
    """
    Scan the framework directory and discover all available tools (recursively).

    Returns:
        List of tool information dictionaries containing:
        - name: Tool module name
        - path: Full path to the tool
        - relative_path: Path relative to framework root
        - domain: Tool domain (if defined)
        - action: Tool action (if defined)
        - description: Tool documentation
    """
    settings = load_settings()
    framework_root = settings.framework_root

    if not framework_root.exists():
        return []

    interrupt_handler = get_interrupt_handler()
    tools = []
    # Use **/*.py to search recursively
    for file in framework_root.glob("**/*.py"):
        # Check for interrupt during scanning
        if interrupt_handler.is_interrupted():
            raise InterruptedError("Framework scanning interrupted by user (ESC)")

        if file.name == "__init__.py":
            continue

        # Get relative path from framework root
        try:
            relative_path = file.relative_to(framework_root)
        except ValueError:
            relative_path = file

        tool_info = {
            "name": file.stem,
            "path": str(file),
            "relative_path": str(relative_path),
            "domain": None,
            "action": None,
            "description": ""
        }

        # Try to extract metadata from source code without executing
        try:
            # Read file and extract docstring and metadata without executing
            content = file.read_text(encoding='utf-8')

            # Extract module docstring (first string literal at module level)
            try:
                tree = ast.parse(content)
                tool_info["description"] = ast.get_docstring(tree) or ""

                # Look for __domain__ and __action__ assignments
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "__domain__" and isinstance(node.value, ast.Constant):
                                    tool_info["domain"] = node.value.value
                                elif target.id == "__action__" and isinstance(node.value, ast.Constant):
                                    tool_info["action"] = node.value.value
            except:
                # Fallback to simple parsing
                pass

        except Exception as e:
            tool_info["description"] = f"[Error reading file: {str(e)[:50]}...]"

        tools.append(tool_info)

    return tools


def build_domains_summary(tools: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Build a summary of domains and their actions.

    Args:
        tools: List of tool information dictionaries

    Returns:
        Dictionary mapping domains to list of actions
    """
    domains = {}
    for tool in tools:
        domain = tool["domain"] or "general"
        action = tool["action"] or tool["name"]

        if domain not in domains:
            domains[domain] = []

        domains[domain].append(action)

    return domains


def _safe_print(text: str):
    """
    Print text safely, handling Windows console encoding issues.

    Args:
        text: Text to print
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove non-ASCII characters for Windows console
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)


def handle(text: str = "") -> Dict[str, Any]:
    """
    Main entry point for framework discovery tool.

    Args:
        text: User input text (not used for auto-discovery)

    Returns:
        Dictionary with discovery results and formatted summary
    """
    settings = load_settings()
    interrupt_handler = get_interrupt_handler()

    # Start listening for ESC key
    interrupt_handler.start_listening()

    try:
        # Show header
        ui.discovery_header(str(settings.framework_root))
        ui.info("Press ESC to skip discovery...\n")

        # Discover tools
        tools = discover_all_tools()

        if not tools:
            ui.warn("No tools found in framework directory")
            return {
                "status": "success",
                "tools_found": 0,
                "tools": [],
                "message": "No tools found"
            }

        # Build domain/action summary
        domains = build_domains_summary(tools)

        # Display summary
        ui.discovery_summary(len(tools), domains)

        return {
            "status": "success",
            "tools_found": len(tools),
            "tools": tools,
            "domains": domains,
            "message": f"Discovered {len(tools)} tools in framework"
        }
    except InterruptedError:
        ui.warn("\nFramework discovery interrupted by user (ESC)")
        return {
            "status": "interrupted",
            "tools_found": 0,
            "tools": [],
            "message": "Discovery interrupted"
        }
    finally:
        # Stop listening for ESC key
        interrupt_handler.stop_listening()


if __name__ == "__main__":
    # Test the scanner
    print("Testing Framework Scanner...")
    result = handle()
    print(f"\nResult: {result['message']}")
