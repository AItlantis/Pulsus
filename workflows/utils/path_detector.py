"""
Path Detection Utility

Detects whether a user-provided path is a file or directory,
and normalizes paths for downstream processing.
"""

from pathlib import Path
from enum import Enum
from typing import Optional, Tuple
import re


class PathType(Enum):
    """Type of path detected."""
    FILE = "file"
    DIRECTORY = "directory"
    NON_EXISTENT = "non_existent"
    INVALID = "invalid"


def extract_path_from_input(text: str) -> Optional[str]:
    """
    Extract file or directory path from user input containing @path syntax.

    Args:
        text: User input text (e.g., "@C:\\path\\to\\file.py" or "@/path/to/dir")

    Returns:
        Extracted path or None if not found

    Example:
        >>> extract_path_from_input("analyze @C:\\repo\\file.py")
        "C:\\repo\\file.py"
        >>> extract_path_from_input("@/home/user/project")
        "/home/user/project"
    """
    # Pattern to match @path (handles both Windows and Unix paths)
    # Matches:
    # - Windows: @C:\path\to\file or @C:\path\to\dir
    # - Unix: @/path/to/file or @/path/to/dir
    # - Relative: @relative/path
    pattern = r'@([A-Za-z]:[\\\/][^\s]+|/[^\s]+|\.{0,2}[\\\/][^\s]+|[^\s]+\.py)'
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return None


def detect_path_type(path_str: str) -> Tuple[PathType, Optional[Path]]:
    """
    Detect if path is a file, directory, or non-existent.

    Args:
        path_str: Path string to analyze

    Returns:
        Tuple of (PathType, normalized_path)
        - PathType: Type of path detected
        - normalized_path: Normalized Path object or None if invalid

    Example:
        >>> detect_path_type("C:\\repo\\file.py")
        (PathType.FILE, Path("C:/repo/file.py"))
        >>> detect_path_type("C:\\repo")
        (PathType.DIRECTORY, Path("C:/repo"))
        >>> detect_path_type("C:\\nonexistent\\file.py")
        (PathType.NON_EXISTENT, Path("C:/nonexistent/file.py"))
    """
    try:
        path = Path(path_str).resolve()
    except (ValueError, OSError) as e:
        # Invalid path (e.g., invalid characters, too long, etc.)
        return (PathType.INVALID, None)

    # Check if path exists
    if path.exists():
        if path.is_file():
            return (PathType.FILE, path)
        elif path.is_dir():
            return (PathType.DIRECTORY, path)
        else:
            # Could be symlink, device, etc.
            # Treat as invalid for our purposes
            return (PathType.INVALID, path)
    else:
        # Path doesn't exist yet
        # Try to infer type from extension or trailing slash
        if path.suffix in ['.py', '.json', '.txt', '.md', '.yml', '.yaml']:
            return (PathType.NON_EXISTENT, path)
        else:
            # Assume directory if no file extension
            return (PathType.NON_EXISTENT, path)


def is_python_file(path: Path) -> bool:
    """
    Check if path is a Python file.

    Args:
        path: Path to check

    Returns:
        True if path is a .py file, False otherwise
    """
    return path.suffix == '.py'


def is_repository_root(path: Path) -> bool:
    """
    Check if path appears to be a repository root.

    A repository root typically contains:
    - .git directory
    - setup.py, pyproject.toml, or requirements.txt
    - README file

    Args:
        path: Path to check

    Returns:
        True if path appears to be a repository root
    """
    if not path.is_dir():
        return False

    # Check for common repository indicators
    indicators = [
        path / ".git",
        path / "setup.py",
        path / "pyproject.toml",
        path / "requirements.txt",
        path / "README.md",
        path / "README.rst",
    ]

    # At least one indicator should exist
    return any(indicator.exists() for indicator in indicators)


def normalize_path(path_str: str) -> Optional[Path]:
    """
    Normalize a path string to a Path object.

    Handles:
    - Expanding user home directory (~)
    - Resolving relative paths
    - Converting to absolute path

    Args:
        path_str: Path string to normalize

    Returns:
        Normalized Path object or None if invalid
    """
    try:
        path = Path(path_str).expanduser().resolve()
        return path
    except (ValueError, OSError):
        return None
