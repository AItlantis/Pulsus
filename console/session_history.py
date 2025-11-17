"""
Session History Module

Tracks the context of the current Pulsus session, including:
- Last analyzed script path
- Conversation history for follow-up questions
- Script analysis cache
"""

from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ScriptContext:
    """Context information for an analyzed script."""
    path: Path
    ast_analysis: Dict[str, Any]
    metadata: Dict[str, Any]
    llm_understanding: str
    analyzed_at: datetime = field(default_factory=datetime.now)
    content: str = ""


@dataclass
class RepositoryContext:
    """Context information for an analyzed repository."""
    path: Path
    llm_summary: str
    health_status: str
    statistics: Dict[str, Any]
    issues_summary: Dict[str, Any]
    reusability_summary: Dict[str, Any]
    analyzed_at: datetime = field(default_factory=datetime.now)
    raw_analysis: Dict[str, Any] = field(default_factory=dict)


class SessionHistory:
    """
    Manages session history and context for Pulsus conversations.
    """

    def __init__(self):
        self.current_script: Optional[ScriptContext] = None
        self.current_repository: Optional[RepositoryContext] = None
        self.conversation_history = []

    def set_current_script(self, path: Path, ast_analysis: Dict, metadata: Dict,
                          llm_understanding: str, content: str = ""):
        """
        Set the currently analyzed script.

        Args:
            path: Path to the script
            ast_analysis: AST analysis results
            metadata: Module metadata
            llm_understanding: LLM-generated understanding
            content: Full script content
        """
        self.current_script = ScriptContext(
            path=path,
            ast_analysis=ast_analysis,
            metadata=metadata,
            llm_understanding=llm_understanding,
            content=content
        )

    def has_current_script(self) -> bool:
        """Check if there's a current script in context."""
        return self.current_script is not None

    def get_current_script(self) -> Optional[ScriptContext]:
        """Get the current script context."""
        return self.current_script

    def clear_current_script(self):
        """Clear the current script context."""
        self.current_script = None

    def set_current_repository(self, path: Path, llm_summary: str, health_status: str,
                               statistics: Dict, issues_summary: Dict, reusability_summary: Dict,
                               raw_analysis: Dict = None):
        """
        Set the currently analyzed repository.

        Args:
            path: Path to the repository
            llm_summary: Natural language summary with insights
            health_status: Health assessment (e.g., '[EXCELLENT]', '[GOOD]', '[CRITICAL]')
            statistics: Repository statistics
            issues_summary: Issues found in the repository
            reusability_summary: Reusability metrics
            raw_analysis: Raw analysis data
        """
        self.current_repository = RepositoryContext(
            path=path,
            llm_summary=llm_summary,
            health_status=health_status,
            statistics=statistics,
            issues_summary=issues_summary,
            reusability_summary=reusability_summary,
            raw_analysis=raw_analysis or {}
        )

    def has_current_repository(self) -> bool:
        """Check if there's a current repository in context."""
        return self.current_repository is not None

    def get_current_repository(self) -> Optional[RepositoryContext]:
        """Get the current repository context."""
        return self.current_repository

    def clear_current_repository(self):
        """Clear the current repository context."""
        self.current_repository = None

    def add_conversation(self, user_input: str, response: str):
        """
        Add a conversation exchange to history.

        Args:
            user_input: User's input
            response: Pulsus response
        """
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "user": user_input,
            "pulsus": response,
            "script": str(self.current_script.path) if self.current_script else None
        })

    def get_context_summary(self) -> str:
        """
        Get a summary of the current context for LLM prompts.

        Returns:
            Formatted context summary
        """
        parts = []

        # Add repository context if available
        if self.current_repository:
            repo = self.current_repository
            parts.append(f"""Current Repository Context:
- Repository: {repo.path.name}
- Path: {repo.path}
- Health Status: {repo.health_status}
- Files Analyzed: {repo.statistics.get('total_files', 0)}
- Total Functions: {repo.statistics.get('total_functions', 0)}
- Total Classes: {repo.statistics.get('total_classes', 0)}
- Issues Found: {repo.issues_summary.get('total_issues', 0)}
- Average Reusability Score: {repo.reusability_summary.get('average_score', 0):.2f}/15
- Analyzed: {repo.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}

Repository Insights:
{repo.llm_summary}
""")

        # Add script context if available
        if self.current_script:
            parts.append(f"""Current Script Context:
- File: {self.current_script.path.name}
- Path: {self.current_script.path}
- Functions: {len(self.current_script.ast_analysis.get('functions', []))}
- Classes: {len(self.current_script.ast_analysis.get('classes', []))}

Previous Understanding:
{self.current_script.llm_understanding}
""")

        if not parts:
            return "No script or repository currently in context."

        return "\n".join(parts)


# Global session history instance
_session_history = SessionHistory()


def get_session_history() -> SessionHistory:
    """Get the global session history instance."""
    return _session_history
