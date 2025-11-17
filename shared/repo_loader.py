"""
Repository Context Loader

Provides functions to load and ensure repository context for framework awareness.
Automatically loads .pulse/ cached data or triggers re-analysis if needed.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import hashlib
import os
from datetime import datetime

from agents.shared.settings import get_framework_config


def get_pulse_folder(repo_path: Path) -> Path:
    """
    Get the .pulse folder path for a repository.

    Args:
        repo_path: Path to the repository

    Returns:
        Path to .pulse folder
    """
    pulse_folder = get_framework_config("pulse_folder") or ".pulse"
    return repo_path / pulse_folder


def pulse_folder_exists(repo_path: Path) -> bool:
    """
    Check if .pulse folder exists for a repository.

    Args:
        repo_path: Path to the repository

    Returns:
        True if .pulse folder exists
    """
    pulse_path = get_pulse_folder(repo_path)
    return pulse_path.exists() and pulse_path.is_dir()


def get_repo_index_path(repo_path: Path) -> Path:
    """
    Get the path to repo_index.json.

    Args:
        repo_path: Path to the repository

    Returns:
        Path to repo_index.json
    """
    return get_pulse_folder(repo_path) / "repo_index.json"


def load_repo_index(repo_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load repository index from .pulse/repo_index.json.

    Args:
        repo_path: Path to the repository

    Returns:
        Repository index data or None if not found
    """
    index_path = get_repo_index_path(repo_path)

    if not index_path.exists():
        return None

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[repo_loader] Error loading repo_index.json: {e}")
        return None


def save_repo_index(repo_path: Path, data: Dict[str, Any]) -> bool:
    """
    Save repository index to .pulse/repo_index.json.

    Args:
        repo_path: Path to the repository
        data: Repository analysis data to save

    Returns:
        True if saved successfully
    """
    pulse_folder = get_pulse_folder(repo_path)
    pulse_folder.mkdir(parents=True, exist_ok=True)

    index_path = get_repo_index_path(repo_path)

    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"[repo_loader] Error saving repo_index.json: {e}")
        return False


def calculate_repo_hash(repo_path: Path, ignore_patterns: Optional[list] = None) -> str:
    """
    Calculate a hash of all Python files in the repository for change detection.

    Args:
        repo_path: Path to the repository
        ignore_patterns: Patterns to ignore (e.g., ['test', '__pycache__'])

    Returns:
        Hash string representing the current state
    """
    if ignore_patterns is None:
        ignore_patterns = ['test', '__pycache__', '.venv', 'venv', '.git', '.pulse']

    hasher = hashlib.md5()

    # Sort files for consistent hashing
    py_files = sorted(repo_path.rglob("*.py"))

    for file_path in py_files:
        # Skip ignored patterns
        if any(pattern in str(file_path) for pattern in ignore_patterns):
            continue

        try:
            # Hash file path and modification time
            hasher.update(str(file_path.relative_to(repo_path)).encode())
            hasher.update(str(file_path.stat().st_mtime).encode())
        except Exception:
            continue

    return hasher.hexdigest()


def needs_reanalysis(repo_path: Path, ignore_patterns: Optional[list] = None) -> bool:
    """
    Check if repository needs re-analysis based on file changes.

    Args:
        repo_path: Path to the repository
        ignore_patterns: Patterns to ignore during comparison

    Returns:
        True if re-analysis is needed
    """
    # Load existing index
    index = load_repo_index(repo_path)

    if not index:
        return True  # No index, needs analysis

    # Check if hash has changed
    stored_hash = index.get('repo_hash')
    current_hash = calculate_repo_hash(repo_path, ignore_patterns)

    return stored_hash != current_hash


def load_repo_context(repo_path: str | Path) -> Optional[Dict[str, Any]]:
    """
    Load repository context from .pulse/repo_index.json.

    This is the main function to retrieve cached repository analysis.

    Args:
        repo_path: Path to the repository (string or Path)

    Returns:
        Repository context data or None if not available
    """
    repo_path = Path(repo_path)

    if not repo_path.exists():
        print(f"[repo_loader] Repository path does not exist: {repo_path}")
        return None

    # Check if .pulse folder exists
    if not pulse_folder_exists(repo_path):
        print(f"[repo_loader] No .pulse folder found at {repo_path}")
        return None

    # Load the index
    return load_repo_index(repo_path)


def ensure_repo_context(repo_path: str | Path,
                       force_reanalysis: bool = False,
                       ignore_patterns: Optional[list] = None) -> Dict[str, Any]:
    """
    Ensure repository context is available, analyzing if necessary.

    This function:
    1. Checks if .pulse/repo_index.json exists
    2. If not, or if force_reanalysis=True, triggers analysis
    3. If incremental_updates enabled, checks for file changes
    4. Returns the repository context

    Args:
        repo_path: Path to the repository
        force_reanalysis: Force re-analysis even if cache exists
        ignore_patterns: Patterns to ignore during analysis

    Returns:
        Repository context data

    Raises:
        Exception if analysis fails
    """
    repo_path = Path(repo_path)

    if not repo_path.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    # Check if analysis is needed
    incremental = get_framework_config("incremental_updates")

    if not force_reanalysis and get_framework_config("cache_enabled"):
        # Try to load existing context
        context = load_repo_context(repo_path)

        if context:
            # Check if re-analysis needed (if incremental updates enabled)
            if incremental and needs_reanalysis(repo_path, ignore_patterns):
                print(f"[repo_loader] Repository has changed, triggering re-analysis...")
            else:
                print(f"[repo_loader] Loaded cached repository context from .pulse/")
                return context

    # Trigger analysis
    print(f"[repo_loader] Analyzing repository: {repo_path}")
    from agents.shared.tools import mcp_analyze_repository

    # Call the MCP tool
    result_json = mcp_analyze_repository(str(repo_path), ignore_patterns)
    result = json.loads(result_json)

    if not result.get("success"):
        raise Exception(f"Repository analysis failed: {result.get('error')}")

    # Add repo hash for change detection
    result['repo_hash'] = calculate_repo_hash(repo_path, ignore_patterns)
    result['analyzed_at'] = datetime.now().isoformat()

    # Save to .pulse/repo_index.json
    save_repo_index(repo_path, result)

    # Generate enhanced .pulse/ outputs (dependency graph, function index, script cards)
    try:
        from agents.mcp.helpers.pulse_generator import PulseGenerator

        pulse_dir = get_pulse_folder(repo_path)
        gen_results = PulseGenerator.generate_all(result, pulse_dir)

        print(f"[repo_loader] Repository analysis complete and cached to .pulse/")
        print(f"[repo_loader] Generated: imports_graph={gen_results.get('imports_graph', False)}, "
              f"functions_index={gen_results.get('functions_index', False)}, "
              f"script_cards={gen_results.get('cards_generated', 0)} cards")

    except Exception as e:
        print(f"[repo_loader] Warning: Could not generate enhanced outputs: {e}")
        print(f"[repo_loader] Repository analysis complete and cached to .pulse/")

    return result


def get_framework_context(force_reanalysis: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get the framework context based on FRAMEWORK_PATH configuration.

    This is the main entry point for framework awareness initialization.

    Args:
        force_reanalysis: Force re-analysis even if cache exists

    Returns:
        Framework context data or None if no framework path configured
    """
    framework_path = get_framework_config("framework_path")

    if not framework_path:
        return None

    try:
        return ensure_repo_context(framework_path, force_reanalysis)
    except Exception as e:
        print(f"[repo_loader] Failed to get framework context: {e}")
        return None


def initialize_framework_awareness() -> bool:
    """
    Initialize framework awareness on Pulsus startup.

    This function is called during Pulsus initialization to:
    1. Check if FRAMEWORK_PATH is configured
    2. Check if auto_analyze_on_start is enabled
    3. Load or analyze the framework
    4. Store results in session history

    Returns:
        True if framework context was loaded/analyzed successfully
    """
    # Check if auto-analysis is enabled
    if not get_framework_config("auto_analyze_on_start"):
        return False

    framework_path = get_framework_config("framework_path")
    if not framework_path:
        return False

    try:
        # Import UI display functions
        from agents.pulsus.ui import display_manager as ui
    except ImportError:
        # Fallback to basic print if UI not available
        ui = None

    # Display header
    if ui:
        ui.framework_awareness_header()
        ui.repository_analysis_progress(f"Initializing: {framework_path}")
    else:
        print(f"\n[*] Initializing framework awareness for: {framework_path}")

    try:
        # Check if we have cached data
        from_cache = pulse_folder_exists(Path(framework_path))

        # Get or analyze framework
        context = get_framework_context(force_reanalysis=False)

        if not context:
            return False

        # Store in session history
        from agents.pulsus.console.session_history import get_session_history

        session = get_session_history()

        # Extract summary data
        stats = context.get('statistics', {})
        issues = context.get('issues_summary', {})
        reuse = context.get('reusability_summary', {})

        # For now, use a basic summary (will be enhanced with LLM later)
        health = _calculate_health_status(context)
        summary = _generate_basic_summary(context)

        # Store in session
        session.set_current_repository(
            path=Path(framework_path),
            llm_summary=summary,
            health_status=health,
            statistics=stats,
            issues_summary=issues,
            reusability_summary=reuse,
            raw_analysis=context
        )

        # Display status
        if ui:
            ui.framework_awareness_status(
                health=health,
                files=stats.get('total_files', 0),
                issues=issues.get('total_issues', 0),
                from_cache=from_cache
            )
        else:
            print(f"[✓] Framework context loaded and available for queries")
            print(f"[✓] Health: {health} | Files: {stats.get('total_files', 0)} | Issues: {issues.get('total_issues', 0)}")

        return True

    except Exception as e:
        if ui:
            ui.error(f"Framework initialization failed: {e}")
        else:
            print(f"[!] Framework initialization failed: {e}")
        return False


def _calculate_health_status(context: Dict[str, Any]) -> str:
    """Calculate basic health status from context."""
    stats = context.get('statistics', {})
    compliance = stats.get('compliance_rate', 0)

    if compliance >= 90:
        return "[EXCELLENT]"
    elif compliance >= 70:
        return "[GOOD]"
    elif compliance >= 50:
        return "[NEEDS IMPROVEMENT]"
    else:
        return "[CRITICAL]"


def _generate_basic_summary(context: Dict[str, Any]) -> str:
    """Generate basic summary from context (placeholder for LLM)."""
    stats = context.get('statistics', {})
    issues = context.get('issues_summary', {})

    summary = f"""Repository Analysis Summary:
- Total Files: {stats.get('total_files', 0)}
- Total Functions: {stats.get('total_functions', 0)}
- Total Classes: {stats.get('total_classes', 0)}
- Issues Found: {issues.get('total_issues', 0)}
- Compliance Rate: {stats.get('compliance_rate', 0):.1f}%

This analysis is cached and available for queries.
"""
    return summary
