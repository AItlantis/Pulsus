"""
Unified Path Analyzer

Entry point for all @path analysis requests.
Routes to file or repository analyzer based on path type.
Automatically loads .pulsus/ context when available.

__domain__ = "analysis"
__action__ = "analyze_path"
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add paths for imports
from pathlib import Path as PathLib
testudo_root = PathLib(__file__).parents[5]
if str(testudo_root) not in sys.path:
    sys.path.insert(0, str(testudo_root))

from agents.pulsus.workflows.utils.path_detector import (
    extract_path_from_input,
    detect_path_type,
    PathType
)
from agents.pulsus.workflows.utils.context_loader import (
    load_repository_context,
    is_context_available,
    find_repository_root
)


__domain__ = "analysis"
__action__ = "analyze_path"


def handle(input_text: str = None, path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Unified handler for @path analysis.

    Automatically detects if path is file or directory and routes accordingly.
    Loads repository context from .pulsus/ when available.

    Args:
        input_text: Full user input (for extracting @path)
        path: Direct path string (alternative to input_text)
        **kwargs: Additional arguments passed to underlying analyzers

    Returns:
        Analysis results dictionary

    Example:
        >>> handle(input_text="analyze @C:\\repo\\file.py")
        {...}  # File analysis with repo context
        >>> handle(path="C:\\repo")
        {...}  # Repository analysis
    """
    # Extract path from input
    if path:
        path_str = path
    elif input_text:
        path_str = extract_path_from_input(input_text)
        if not path_str:
            return {
                "success": False,
                "error": "No @path found in input. Use @path syntax (e.g., @C:\\repo\\file.py)"
            }
    else:
        return {
            "success": False,
            "error": "No input provided. Provide either input_text or path parameter."
        }

    # Detect path type
    path_type, normalized_path = detect_path_type(path_str)

    if path_type == PathType.INVALID:
        return {
            "success": False,
            "error": f"Invalid path: {path_str}"
        }

    if path_type == PathType.NON_EXISTENT:
        return {
            "success": False,
            "error": f"Path does not exist: {path_str}"
        }

    # Route based on path type
    if path_type == PathType.DIRECTORY:
        return _analyze_directory(normalized_path, **kwargs)
    elif path_type == PathType.FILE:
        return _analyze_file(normalized_path, **kwargs)
    else:
        return {
            "success": False,
            "error": f"Unsupported path type: {path_type}"
        }


def _analyze_directory(path: Path, **kwargs) -> Dict[str, Any]:
    """
    Analyze a directory (repository).

    Args:
        path: Path to directory
        **kwargs: Additional arguments

    Returns:
        Repository analysis results
    """
    from agents.pulsus.workflows.tools.analyze.repository_analyzer_llm import handle as repo_handle

    print(f"\n[*] Detected directory: {path}")
    print(f"[*] Running repository analysis...")

    # Check if context already exists
    if is_context_available(path):
        print(f"[*] Note: Previous analysis found in .pulsus/")
        print(f"[*] Will update with fresh analysis...")

    # Run repository analysis
    result = repo_handle(
        repo_path=str(path),
        generate_report=kwargs.get('generate_report', False),
        output_path=kwargs.get('output_path', None)
    )

    return result


def _analyze_file(path: Path, **kwargs) -> Dict[str, Any]:
    """
    Analyze a file with repository context if available.

    Args:
        path: Path to file
        **kwargs: Additional arguments

    Returns:
        File analysis results with repository context
    """
    from agents.pulsus.workflows.tools.analyze.file_analyzer import handle as file_handle

    print(f"\n[*] Detected file: {path}")

    # Try to load repository context
    repo_context = None
    repo_root = find_repository_root(path)

    if repo_root and is_context_available(path):
        print(f"[*] Loading repository context from: {repo_root}")
        repo_context = load_repository_context(path)

        if repo_context:
            print(f"[*] Repository context loaded successfully")
            print(f"    - Repository: {repo_root.name}")

            stats = repo_context.get("statistics", {})
            if stats:
                print(f"    - Total files: {stats.get('total_files', 'N/A')}")
                print(f"    - Compliance: {stats.get('compliance_rate', 'N/A')}")
        else:
            print(f"[*] Warning: Could not load repository context")
    else:
        if repo_root:
            print(f"[*] Note: No repository analysis found in .pulsus/")
            print(f"[*] Consider running: @{repo_root}")
            print(f"[*] Analyzing file in isolation...")
        else:
            print(f"[*] Note: File not part of a recognized repository")
            print(f"[*] Analyzing file in isolation...")

    # Run file analysis
    print(f"\n[*] Analyzing file...")
    result = file_handle(
        input_text=f"@{path}",
        repo_context=repo_context,
        **kwargs
    )

    # Enhance result with context comparison if available
    if repo_context and result.get("success"):
        result = _enhance_with_context(result, repo_context)

    return result


def _enhance_with_context(
    file_analysis: Dict[str, Any],
    repo_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhance file analysis with repository context comparison.

    Args:
        file_analysis: File analysis results
        repo_context: Repository analysis context

    Returns:
        Enhanced file analysis with context insights
    """
    # Extract repository statistics
    repo_stats = repo_context.get("statistics", {})

    # Add context comparison section
    context_insights = []

    # Compare issues
    if "issues_count" in file_analysis:
        file_issues = file_analysis["issues_count"]
        avg_issues = repo_stats.get("avg_issues_per_file", 0)

        if file_issues > avg_issues * 1.5:
            context_insights.append(
                f"⚠️  This file has {file_issues} issues vs repo average of {avg_issues:.1f}"
            )
        elif file_issues < avg_issues * 0.5:
            context_insights.append(
                f"✓ This file has fewer issues than repo average ({file_issues} vs {avg_issues:.1f})"
            )

    # Compare complexity
    if "complexity" in file_analysis:
        file_complexity = file_analysis["complexity"]
        # Add complexity comparison if repo has this metric
        pass

    # Add reusability suggestions from repo context
    reusable_functions = repo_context.get("reusability_summary", {}).get("top_reusable", [])
    if reusable_functions:
        context_insights.append(
            f"\n💡 Top reusable functions in repository:"
        )
        for func in reusable_functions[:3]:
            context_insights.append(
                f"   - {func.get('function', 'N/A')} (score: {func.get('reusability_score', 0)}/15)"
            )

    # Add context insights to result
    if context_insights:
        file_analysis["repository_context_insights"] = "\n".join(context_insights)

    return file_analysis
