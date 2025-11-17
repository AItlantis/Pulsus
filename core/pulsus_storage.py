"""
Pulsus Storage Module

Manages persistent storage of analysis results in the .pulsus/ directory.

Directory Structure:
    .pulsus/
        repositories/
            <repo_hash>/
                latest.json          # Most recent analysis
                history/
                    <timestamp>.json # Historical analyses
                reports/
                    <timestamp>.xlsx # Generated Excel reports
        cache/
            mcp_responses/           # Cached MCP tool responses
        sessions/
            <session_id>.json        # Session history

Usage:
    from agents.pulsus.core.pulsus_storage import save_repository_analysis

    save_repository_analysis(repo_path, analysis_data)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil


class PulsusStorage:
    """Manages .pulsus/ directory structure and data persistence."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize storage manager.

        Args:
            base_path: Base directory for .pulsus/ (defaults to current working directory)
        """
        if base_path is None:
            base_path = Path.cwd()

        self.base_path = Path(base_path)
        self.pulsus_dir = self.base_path / ".pulsus"

        # Create directory structure
        self._init_directory_structure()

    def _init_directory_structure(self):
        """Initialize .pulsus/ directory structure."""
        directories = [
            self.pulsus_dir / "repositories",
            self.pulsus_dir / "cache" / "mcp_responses",
            self.pulsus_dir / "sessions",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _get_repo_hash(self, repo_path: str) -> str:
        """
        Generate a unique hash for a repository path.

        Args:
            repo_path: Path to repository

        Returns:
            8-character hash of the repository path
        """
        repo_path_normalized = str(Path(repo_path).resolve())
        return hashlib.sha256(repo_path_normalized.encode()).hexdigest()[:8]

    def save_repository_analysis(
        self,
        repo_path: str,
        analysis_data: Dict[str, Any],
        save_to_history: bool = True
    ) -> Dict[str, str]:
        """
        Save repository analysis to .pulsus/ directory.

        Args:
            repo_path: Path to analyzed repository
            analysis_data: Analysis results dictionary
            save_to_history: Whether to save to history (default: True)

        Returns:
            Dictionary with paths to saved files
        """
        repo_hash = self._get_repo_hash(repo_path)
        repo_dir = self.pulsus_dir / "repositories" / repo_hash

        # Create repository-specific directories
        (repo_dir / "history").mkdir(parents=True, exist_ok=True)
        (repo_dir / "reports").mkdir(parents=True, exist_ok=True)

        # Add metadata
        timestamp = datetime.now().isoformat()
        analysis_with_meta = {
            "repository_path": str(Path(repo_path).resolve()),
            "repository_name": Path(repo_path).name,
            "timestamp": timestamp,
            "analysis": analysis_data
        }

        # Save as latest
        latest_path = repo_dir / "latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_with_meta, f, indent=2)

        saved_paths = {
            "latest": str(latest_path)
        }

        # Save to history if requested
        if save_to_history:
            # Include microseconds to avoid filename collisions
            history_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
            history_path = repo_dir / "history" / history_filename
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_with_meta, f, indent=2)
            saved_paths["history"] = str(history_path)

        # Save repository info file
        info_path = repo_dir / "info.json"
        info_data = {
            "repository_path": str(Path(repo_path).resolve()),
            "repository_name": Path(repo_path).name,
            "repository_hash": repo_hash,
            "first_analyzed": timestamp if not info_path.exists() else self._get_first_analyzed(info_path),
            "last_analyzed": timestamp,
            "analysis_count": self._get_analysis_count(repo_dir) + 1
        }
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, indent=2)

        return saved_paths

    def _get_first_analyzed(self, info_path: Path) -> str:
        """Get the first_analyzed timestamp from existing info file."""
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                return info.get("first_analyzed", datetime.now().isoformat())
        except:
            return datetime.now().isoformat()

    def _get_analysis_count(self, repo_dir: Path) -> int:
        """Count existing analyses in history."""
        history_dir = repo_dir / "history"
        if not history_dir.exists():
            return 0
        return len(list(history_dir.glob("*.json")))

    def get_latest_analysis(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest analysis for a repository.

        Args:
            repo_path: Path to repository

        Returns:
            Latest analysis data or None if not found
        """
        repo_hash = self._get_repo_hash(repo_path)
        latest_path = self.pulsus_dir / "repositories" / repo_hash / "latest.json"

        if not latest_path.exists():
            return None

        with open(latest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_analysis_history(self, repo_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve analysis history for a repository.

        Args:
            repo_path: Path to repository
            limit: Maximum number of historical analyses to return

        Returns:
            List of historical analyses (newest first)
        """
        repo_hash = self._get_repo_hash(repo_path)
        history_dir = self.pulsus_dir / "repositories" / repo_hash / "history"

        if not history_dir.exists():
            return []

        # Get all history files sorted by modification time (newest first)
        history_files = sorted(
            history_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]

        history = []
        for file_path in history_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                history.append(json.load(f))

        return history

    def save_report(self, repo_path: str, report_path: str) -> str:
        """
        Copy a generated report to the .pulsus/ directory.

        Args:
            repo_path: Path to repository
            report_path: Path to the generated report file

        Returns:
            Path to the saved report in .pulsus/
        """
        repo_hash = self._get_repo_hash(repo_path)
        reports_dir = self.pulsus_dir / "repositories" / repo_hash / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped filename
        report_ext = Path(report_path).suffix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_filename = f"report_{timestamp}{report_ext}"
        dest_path = reports_dir / dest_filename

        # Copy the report
        shutil.copy2(report_path, dest_path)

        return str(dest_path)

    def list_analyzed_repositories(self) -> List[Dict[str, Any]]:
        """
        List all repositories that have been analyzed.

        Returns:
            List of repository info dictionaries
        """
        repos_dir = self.pulsus_dir / "repositories"

        if not repos_dir.exists():
            return []

        repositories = []
        for repo_dir in repos_dir.iterdir():
            if repo_dir.is_dir():
                info_path = repo_dir / "info.json"
                if info_path.exists():
                    with open(info_path, 'r', encoding='utf-8') as f:
                        repositories.append(json.load(f))

        # Sort by last analyzed (newest first)
        repositories.sort(key=lambda r: r.get("last_analyzed", ""), reverse=True)

        return repositories

    def clear_cache(self):
        """Clear the MCP response cache."""
        cache_dir = self.pulsus_dir / "cache" / "mcp_responses"
        if cache_dir.exists():
            for file_path in cache_dir.glob("*.json"):
                file_path.unlink()

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about .pulsus/ storage.

        Returns:
            Dictionary with storage statistics
        """
        repos_count = len(self.list_analyzed_repositories())

        # Calculate total size
        total_size = 0
        for file_path in self.pulsus_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return {
            "total_repositories": repos_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "pulsus_directory": str(self.pulsus_dir)
        }


# Global storage instance
_storage: Optional[PulsusStorage] = None


def get_storage(base_path: Optional[Path] = None) -> PulsusStorage:
    """
    Get or create the global storage instance.

    Args:
        base_path: Base directory for .pulsus/ (defaults to current working directory)

    Returns:
        PulsusStorage instance
    """
    global _storage
    if _storage is None or (base_path and base_path != _storage.base_path):
        _storage = PulsusStorage(base_path)
    return _storage


# Convenience functions
def save_repository_analysis(repo_path: str, analysis_data: Dict[str, Any], **kwargs) -> Dict[str, str]:
    """Save repository analysis to .pulsus/ directory."""
    return get_storage().save_repository_analysis(repo_path, analysis_data, **kwargs)


def get_latest_analysis(repo_path: str) -> Optional[Dict[str, Any]]:
    """Get the latest analysis for a repository."""
    return get_storage().get_latest_analysis(repo_path)


def get_analysis_history(repo_path: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get analysis history for a repository."""
    return get_storage().get_analysis_history(repo_path, limit)


def save_report(repo_path: str, report_path: str) -> str:
    """Save a generated report to .pulsus/ directory."""
    return get_storage().save_report(repo_path, report_path)


def list_analyzed_repositories() -> List[Dict[str, Any]]:
    """List all analyzed repositories."""
    return get_storage().list_analyzed_repositories()


def get_storage_stats() -> Dict[str, Any]:
    """Get .pulsus/ storage statistics."""
    return get_storage().get_storage_stats()
