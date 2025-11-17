"""
Pulsus Features and Tools Display

This module provides formatted display of Pulsus capabilities,
available MCP tools, and system features during initialization.
"""

from typing import List, Dict, Any
from colorama import Fore, Style
from agents.shared.tools import BASE_TOOLS


def get_mcp_tools_summary() -> Dict[str, List[Dict[str, str]]]:
    """
    Get categorized summary of available MCP tools.

    Returns:
        Dictionary with categorized tool descriptions
    """
    return {
        "Script Analysis & Documentation": [
            {
                "name": "mcp_read_script",
                "description": "Read and analyze Python scripts with AST parsing",
                "usage": "@path/to/script.py"
            },
            {
                "name": "mcp_write_md",
                "description": "Generate comprehensive Markdown documentation",
                "usage": "generate docs"
            },
            {
                "name": "mcp_add_comments",
                "description": "Generate docstrings for all functions",
                "usage": "comment functions"
            }
        ],
        "Repository Analysis": [
            {
                "name": "mcp_analyze_repository",
                "description": "Comprehensive repository analysis with quality metrics",
                "usage": "analyze repository at path/to/repo"
            },
            {
                "name": "mcp_comment_repository",
                "description": "Generate comments for all functions in repository",
                "usage": "comment repository path/to/repo"
            },
            {
                "name": "mcp_document_repository",
                "description": "Generate docs for all scripts in repository",
                "usage": "document repository path/to/repo"
            },
            {
                "name": "mcp_validate_python_file",
                "description": "Validate Python file for quality and compliance",
                "usage": "validate file.py"
            },
            {
                "name": "mcp_generate_repository_report",
                "description": "Generate Excel report with repository analysis",
                "usage": "generate report for repository"
            }
        ],
        "Code Formatting & Structure": [
            {
                "name": "mcp_format_script",
                "description": "Auto-format with black, isort, and autoflake",
                "usage": "format script.py"
            },
            {
                "name": "mcp_scan_structure",
                "description": "Scan directory and build dependency map",
                "usage": "scan structure agents/"
            }
        ],
        "API Documentation Search": [
            {
                "name": "search_aimsun_docs",
                "description": "Search Aimsun Next API documentation",
                "usage": "search API for GKSection"
            },
            {
                "name": "search_qgis_docs",
                "description": "Search QGIS (PyQGIS) API documentation",
                "usage": "search API for QgsVectorLayer"
            }
        ],
        "Code Execution": [
            {
                "name": "validate_python_code",
                "description": "Validate code safety before execution",
                "usage": "validate code"
            },
            {
                "name": "execute_safe_python",
                "description": "Execute code in sandboxed environment",
                "usage": "run code safely"
            }
        ]
    }


def get_core_features() -> List[Dict[str, str]]:
    """
    Get list of Pulsus core features.

    Returns:
        List of feature dictionaries with name and description
    """
    return [
        {
            "name": "DISCOVER",
            "icon": "🔍",
            "description": "Scan framework for existing tools, score by relevance, select best match"
        },
        {
            "name": "COMPOSE",
            "icon": "🔗",
            "description": "Plan multi-step workflows by chaining tools together"
        },
        {
            "name": "GENERATE",
            "icon": "✨",
            "description": "Create AI-powered solutions when nothing else fits"
        },
        {
            "name": "VALIDATE",
            "icon": "✅",
            "description": "Lint, type-check, and sandbox all code before execution"
        },
        {
            "name": "MCP TOOLS",
            "icon": "🛠️",
            "description": "Script analysis, formatting, documentation, and API search"
        },
        {
            "name": "LOGGING",
            "icon": "📊",
            "description": "Complete action history for reproducibility and rollback"
        }
    ]


def display_features_compact() -> None:
    """Display compact feature list."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN + Style.BRIGHT}  PULSUS CAPABILITIES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    features = get_core_features()

    for feature in features:
        # Remove emoji from display
        print(f"{Fore.GREEN + Style.BRIGHT}{feature['name']:12s}{Style.RESET_ALL} | {feature['description']}")

    print(f"\n{Fore.YELLOW}Type 'list tools' to see all available MCP tools{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def display_tools_full() -> None:
    """Display full categorized tool list."""
    print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA + Style.BRIGHT}  AVAILABLE MCP TOOLS{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")

    tools_by_category = get_mcp_tools_summary()

    for category, tools in tools_by_category.items():
        print(f"{Fore.CYAN + Style.BRIGHT}{category}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-' * len(category)}{Style.RESET_ALL}")

        for tool in tools:
            print(f"\n  {Fore.GREEN}{tool['name']}{Style.RESET_ALL}")
            print(f"    {tool['description']}")
            print(f"    {Fore.YELLOW}Usage:{Style.RESET_ALL} {tool['usage']}")

        print()

    # Add total count
    total_tools = sum(len(tools) for tools in tools_by_category.values())
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Total: {total_tools} MCP tools available{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")


def display_quick_start_examples() -> None:
    """Display quick start examples."""
    examples = [
        {
            "category": "Script Analysis",
            "commands": [
                "@path/to/script.py - Analyze Python script",
                "generate docs - Create documentation for current script",
                "comment functions - Add docstrings to all functions"
            ]
        },
        {
            "category": "Code Formatting",
            "commands": [
                "format script.py - Auto-format with black/isort/autoflake",
                "scan structure agents/ - Build dependency map"
            ]
        },
        {
            "category": "API Documentation",
            "commands": [
                "search Aimsun docs for GKSection",
                "search QGIS docs for QgsVectorLayer"
            ]
        },
        {
            "category": "Workflow Execution",
            "commands": [
                "Load CSV and plot statistics",
                "Summarize the data matrix",
                "Analyze traffic data from Aimsun"
            ]
        }
    ]

    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN + Style.BRIGHT}  QUICK START EXAMPLES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    for example in examples:
        print(f"{Fore.GREEN + Style.BRIGHT}{example['category']}{Style.RESET_ALL}")
        for cmd in example['commands']:
            print(f"  {Fore.YELLOW}>{Style.RESET_ALL} {cmd}")
        print()

    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def display_session_info(session_id: str, started_at: str) -> None:
    """Display session information."""
    print(f"\n{Fore.CYAN}[SESSION INFO]{Style.RESET_ALL}")
    print(f"  ID: {session_id}")
    print(f"  Started: {started_at}")
    print()


def get_features_text() -> str:
    """
    Get features as plain text for LLM greeting enhancement.

    Returns:
        Formatted text listing all features and tools
    """
    text = "\n**MY CAPABILITIES:**\n\n"

    features = get_core_features()
    for feature in features:
        text += f"- {feature['name']}: {feature['description']}\n"

    text += "\n**AVAILABLE MCP TOOLS:**\n\n"

    tools_by_category = get_mcp_tools_summary()
    total_tools = 0

    for category, tools in tools_by_category.items():
        text += f"{category}:\n"
        for tool in tools:
            text += f"  - {tool['name']}: {tool['description']}\n"
            total_tools += 1
        text += "\n"

    text += f"Total: {total_tools} MCP tools available\n"

    return text


# Integration function for use in interface.py
def show_startup_banner(session_id: str = None, started_at: str = None,
                       show_tools: bool = False, show_examples: bool = False) -> None:
    """
    Display complete startup banner with features and optional sections.

    Args:
        session_id: Optional session ID to display
        started_at: Optional start time to display
        show_tools: If True, show full tool list
        show_examples: If True, show quick start examples
    """
    # Always show compact features
    display_features_compact()

    # Optional session info
    if session_id and started_at:
        display_session_info(session_id, started_at)

    # Optional full tools list
    if show_tools:
        display_tools_full()

    # Optional examples
    if show_examples:
        display_quick_start_examples()


if __name__ == "__main__":
    """Test the display functions."""
    print("\n=== TEST: Compact Features ===")
    display_features_compact()

    print("\n=== TEST: Full Tools List ===")
    display_tools_full()

    print("\n=== TEST: Quick Start Examples ===")
    display_quick_start_examples()

    print("\n=== TEST: Complete Startup Banner ===")
    show_startup_banner(
        session_id="run-1234567890-abc123",
        started_at="2025-01-15 10:30:00",
        show_tools=False,
        show_examples=True
    )

    print("\n=== TEST: Features Text for LLM ===")
    print(get_features_text())
