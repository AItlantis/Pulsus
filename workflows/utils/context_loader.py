"""
Context Loader Utility

Loads repository analysis context from .pulsus/ storage.
Provides caching and repository detection capabilities.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


# In-memory cache for repository context during session
_context_cache: Dict[str, Dict[str, Any]] = {}


def find_repository_root(start_path: Path) -> Optional[Path]:
    """
    Find repository root by walking up directory tree.

    Looks for indicators like .git, setup.py, pyproject.toml, etc.

    Args:
        start_path: Starting path (file or directory)

    Returns:
        Path to repository root, or None if not found

    Example:
        >>> find_repository_root(Path("C:/repo/src/module/file.py"))
        Path("C:/repo")
    """
    # Start from file's parent if it's a file
    if start_path.is_file():
        current = start_path.parent
    else:
        current = start_path

    # Walk up directory tree
    max_levels = 10  # Prevent infinite loop
    for _ in range(max_levels):
        # Check for repository indicators
        indicators = [
            current / ".git",
            current / "setup.py",
            current / "pyproject.toml",
            current / "requirements.txt",
            current / "README.md",
            current / "README.rst",
            current / ".pulsus",  # Our own marker
        ]

        if any(indicator.exists() for indicator in indicators):
            return current

        # Move up one level
        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    return None


def get_pulsus_storage_path(repo_root: Path) -> Path:
    """
    Get path to .pulsus/ storage directory for a repository.

    Args:
        repo_root: Path to repository root

    Returns:
        Path to .pulsus/ directory
    """
    return repo_root / ".pulsus"


def get_analysis_file_path(repo_root: Path) -> Path:
    """
    Get path to repository analysis JSON file.

    Args:
        repo_root: Path to repository root

    Returns:
        Path to analysis JSON file
    """
    pulsus_dir = get_pulsus_storage_path(repo_root)
    return pulsus_dir / "repository_analysis.json"


def load_repository_context(
    path: Path,
    use_cache: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Load repository analysis context from .pulsus/ storage.

    Handles:
    - Finding repository root from any file within repo
    - Loading cached analysis from .pulsus/repository_analysis.json
    - In-memory caching during session

    Args:
        path: Path to file or directory within repository
        use_cache: Whether to use in-memory cache (default: True)

    Returns:
        Dictionary with repository analysis or None if not available

    Example:
        >>> context = load_repository_context(Path("C:/repo/src/file.py"))
        >>> if context:
        ...     print(f"Repository has {context['statistics']['total_files']} files")
    """
    # Find repository root
    repo_root = find_repository_root(path)
    if not repo_root:
        return None

    # Check in-memory cache first
    cache_key = str(repo_root)
    if use_cache and cache_key in _context_cache:
        return _context_cache[cache_key]

    # Load from .pulsus/ storage
    analysis_file = get_analysis_file_path(repo_root)
    if not analysis_file.exists():
        return None

    try:
        with analysis_file.open('r', encoding='utf-8') as f:
            context = json.load(f)

        # Cache in memory
        if use_cache:
            _context_cache[cache_key] = context

        return context

    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load repository context from {analysis_file}: {e}")
        return None


def save_repository_context(
    repo_root: Path,
    context: Dict[str, Any]
) -> bool:
    """
    Save repository analysis context to .pulsus/ storage.

    Args:
        repo_root: Path to repository root
        context: Analysis context to save

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Create .pulsus/ directory if it doesn't exist
        pulsus_dir = get_pulsus_storage_path(repo_root)
        pulsus_dir.mkdir(exist_ok=True)

        # Add metadata
        context_with_meta = {
            **context,
            "metadata": {
                "saved_at": datetime.now().isoformat(),
                "pulsus_version": "1.0",
            }
        }

        # Save to file
        analysis_file = get_analysis_file_path(repo_root)
        with analysis_file.open('w', encoding='utf-8') as f:
            json.dump(context_with_meta, f, indent=2)

        # Update cache
        cache_key = str(repo_root)
        _context_cache[cache_key] = context_with_meta

        return True

    except (IOError, OSError) as e:
        print(f"Warning: Failed to save repository context: {e}")
        return False


def clear_context_cache():
    """
    Clear in-memory context cache.

    Useful when you want to force reload from disk.
    """
    global _context_cache
    _context_cache.clear()


def is_context_available(path: Path) -> bool:
    """
    Check if repository context is available for a given path.

    Args:
        path: Path to file or directory within repository

    Returns:
        True if context is available, False otherwise
    """
    repo_root = find_repository_root(path)
    if not repo_root:
        return False

    analysis_file = get_analysis_file_path(repo_root)
    return analysis_file.exists()


def get_context_age(path: Path) -> Optional[float]:
    """
    Get age of repository context in seconds.

    Args:
        path: Path to file or directory within repository

    Returns:
        Age in seconds, or None if context not available
    """
    repo_root = find_repository_root(path)
    if not repo_root:
        return None

    analysis_file = get_analysis_file_path(repo_root)
    if not analysis_file.exists():
        return None

    try:
        mtime = analysis_file.stat().st_mtime
        now = datetime.now().timestamp()
        return now - mtime
    except OSError:
        return None
