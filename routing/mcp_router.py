"""
MCP-aware router for Pulsus agent.

This module consolidates routing logic by:
1. Loading workflow definitions from JSON files
2. Leveraging MCP tools from the shared tools registry
3. Using semantic matching instead of hardcoded keywords
4. Providing flexible, extensible routing

Replaces the fragmented prompt_parser + tool_discovery approach.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from dataclasses import dataclass

from ..core.types import ParsedIntent, ToolSpec


@dataclass
class Workflow:
    """Workflow definition from JSON files."""
    id: str
    domain: str
    action: str
    description: str
    steps: List[Dict[str, Any]]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Workflow":
        """Create Workflow from JSON data."""
        return cls(
            id=data["id"],
            domain=data["domain"],
            action=data["action"],
            description=data["description"],
            steps=data.get("steps", [])
        )


class MCPRouter:
    """
    MCP-aware router that dynamically matches user intents to workflows and MCP tools.

    Key features:
    - Loads workflow definitions from JSON
    - Uses MCP tool registry for tool discovery
    - Semantic matching instead of keyword maps
    - Extensible through MCP tools
    """

    def __init__(self, workflows_root: Path):
        """
        Initialize the MCP router.

        Args:
            workflows_root: Path to workflows directory containing JSON definitions
        """
        self.workflows_root = workflows_root
        self.workflows: List[Workflow] = []
        self.mcp_tools: Dict[str, Any] = {}
        self._load_workflows()
        self._load_mcp_tools()

    def _load_workflows(self):
        """Load all workflow definitions from JSON files."""
        if not self.workflows_root.exists():
            print(f"Warning: Workflows root does not exist: {self.workflows_root}")
            return

        workflow_files = list(self.workflows_root.glob("*.json"))

        for wf_file in workflow_files:
            try:
                data = json.loads(wf_file.read_text())
                workflow = Workflow.from_json(data)
                self.workflows.append(workflow)
            except Exception as e:
                # Log but don't fail on individual workflow load errors
                print(f"Warning: Failed to load workflow {wf_file}: {e}")
                import traceback
                traceback.print_exc()

    def _load_mcp_tools(self):
        """Load MCP tools from the shared tools registry."""
        try:
            from agents.shared.tools import BASE_TOOLS

            # Index tools by name for quick lookup
            for tool in BASE_TOOLS:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                self.mcp_tools[tool_name] = tool

        except ImportError:
            print("Warning: Could not import MCP tools from agents.shared.tools")

    def parse_intent(self, text: str) -> ParsedIntent:
        """
        Parse user input to extract domain, action, and intent.

        Uses semantic matching against workflow descriptions and MCP tool metadata
        instead of hardcoded keyword maps.

        Args:
            text: User input text

        Returns:
            ParsedIntent with domain, action, intent, and confidence
        """
        text_lower = text.lower()

        # Check for @path pattern (highest priority)
        # Pattern matches @C:\path\to\file.py or @/path/to/dir
        import re
        from pathlib import Path

        path_pattern = r'@([A-Za-z]:[\\\/][^\s]+|/[^\s]+|\.{0,2}[\\\/][^\s]+|[^\s]+\.py)'
        if re.search(path_pattern, text):
            # This is a path analysis request - route to unified analyzer
            return ParsedIntent(
                domain="analysis",
                action="analyze_path",
                intent=text,
                confidence=0.95
            )

        # Check for implicit path analysis patterns (secondary priority)
        # Patterns like: "analyze framework", "analyse mydir", "analyze repository myproject"
        # Support both British (analyse) and American (analyze) spelling
        implicit_patterns = [
            r'(?:analys[ez])\s+(?:repository\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
            r'(?:check|inspect|review)\s+(?:repository\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
            r'(?:run\s+)?(?:repository\s+)?(?:analys[ei]s)\s+(?:on\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
        ]

        for pattern in implicit_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_path = match.group(1)

                # Check if it's a valid path (directory or file)
                # Try as absolute path first
                path_obj = Path(potential_path)
                if not path_obj.is_absolute():
                    # Try as relative to current directory
                    path_obj = Path.cwd() / potential_path

                # Check if path exists
                if path_obj.exists():
                    # Valid path found - route to analyze_path
                    return ParsedIntent(
                        domain="analysis",
                        action="analyze_path",
                        intent=f"@{path_obj}",  # Convert to @path syntax
                        confidence=0.90
                    )
                else:
                    # Path doesn't exist, but pattern matched
                    # Still route with medium confidence (user clearly wants analysis)
                    # The analyzer will handle non-existent paths
                    return ParsedIntent(
                        domain="analysis",
                        action="analyze_repository",
                        intent=text,
                        confidence=0.75
                    )

        # Try to match against workflows
        best_workflow = None
        best_score = 0.0

        for workflow in self.workflows:
            score = self._match_workflow(text_lower, workflow)
            if score > best_score:
                best_score = score
                best_workflow = workflow

        # Try to match against MCP tools
        best_mcp_tool = None
        best_mcp_score = 0.0

        for tool_name, tool in self.mcp_tools.items():
            score = self._match_mcp_tool(text_lower, tool)
            if score > best_mcp_score:
                best_mcp_score = score
                best_mcp_tool = tool_name

        # Use the best match overall
        if best_score >= best_mcp_score and best_workflow:
            domain = best_workflow.domain
            action = best_workflow.action
            confidence = min(0.5 + best_score * 0.4, 0.95)
        elif best_mcp_tool:
            domain = self._extract_domain_from_tool(best_mcp_tool)
            action = self._extract_action_from_tool(best_mcp_tool)
            confidence = min(0.5 + best_mcp_score * 0.4, 0.95)
        else:
            # No good match - return low confidence
            domain = None
            action = None
            confidence = 0.3

        return ParsedIntent(
            domain=domain,
            action=action,
            intent=text,
            confidence=confidence
        )

    def _match_workflow(self, text: str, workflow: Workflow) -> float:
        """
        Calculate match score between user text and workflow.

        Args:
            text: Lowercase user input
            workflow: Workflow to match against

        Returns:
            Match score between 0.0 and 1.0
        """
        score = 0.0

        # Check domain match (handle word variations)
        if workflow.domain:
            domain_lower = workflow.domain.lower()
            # Check exact match or word parts (e.g., "analysis" -> "analys")
            if domain_lower in text or any(part in text for part in domain_lower.split('_')):
                score += 0.3

        # Check action match (handle underscores as spaces)
        if workflow.action:
            action_lower = workflow.action.lower().replace('_', ' ')
            # Check if action words appear in text
            action_words = action_lower.split()
            matches = sum(1 for word in action_words if word in text)
            if matches == len(action_words):  # All action words present
                score += 0.4
            elif matches > 0:  # Some action words present
                score += 0.2

        # Check description match (more flexible)
        if workflow.description:
            desc_words = workflow.description.lower().split()
            matches = sum(1 for word in desc_words if len(word) > 3 and word in text)
            if matches > 0:
                score += min(matches * 0.1, 0.4)

        return min(score, 1.0)

    def _match_mcp_tool(self, text: str, tool: Any) -> float:
        """
        Calculate match score between user text and MCP tool.

        Args:
            text: Lowercase user input
            tool: MCP tool to match against

        Returns:
            Match score between 0.0 and 1.0
        """
        score = 0.0

        # Check tool name
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        if tool_name.lower() in text or any(part in text for part in tool_name.split('_')):
            score += 0.3

        # Check tool description
        if hasattr(tool, 'description') and tool.description:
            desc = tool.description.lower()
            desc_words = desc.split()
            matches = sum(1 for word in desc_words if len(word) > 3 and word in text)
            if matches > 0:
                score += min(matches * 0.1, 0.5)

        return min(score, 1.0)

    def _extract_domain_from_tool(self, tool_name: str) -> Optional[str]:
        """Extract domain from MCP tool name."""
        # MCP tools use prefixes like 'mcp_read_script', 'search_aimsun_docs'
        if 'read' in tool_name or 'write' in tool_name or 'format' in tool_name or 'scan' in tool_name:
            return 'script_ops'
        elif 'search' in tool_name or 'docs' in tool_name:
            return 'documentation'
        elif 'execute' in tool_name or 'validate' in tool_name:
            return 'execution'
        return 'general'

    def _extract_action_from_tool(self, tool_name: str) -> Optional[str]:
        """Extract action from MCP tool name."""
        # Remove common prefixes
        action = tool_name.replace('mcp_', '').replace('search_', '').replace('get_', '')
        return action

    def discover_tools(self, domain: str, action: str, intent: str) -> List[ToolSpec]:
        """
        Discover relevant tools based on domain, action, and user intent.

        This replaces the filesystem-scanning approach with MCP tool registry lookup.

        Args:
            domain: Parsed domain
            action: Parsed action
            intent: Full user intent text

        Returns:
            List of ToolSpec objects with scored matches
        """
        results = []

        # First, check workflows using semantic matching
        for workflow in self.workflows:
            # Use semantic matching for more flexible scoring
            score = self._match_workflow(intent.lower(), workflow)

            # Boost workflow scores to prefer them over raw MCP tools
            # when providing enhanced functionality (LLM insights, composition, etc.)
            # 1.5x boost to prioritize workflows that add value beyond raw tool execution
            score = min(score * 1.5, 1.0)

            if score > 0.3:  # Only include workflows with reasonable match
                # Extract tool path from workflow steps
                for step in workflow.steps:
                    tool_path = step.get('tool')
                    if tool_path:
                        tool_path_obj = Path(tool_path)

                        results.append(ToolSpec(
                            path=tool_path_obj,
                            entry=step.get('entry', 'handle'),
                            args=[],
                            doc=workflow.description,
                            score=score
                        ))

        # Second, check MCP tools
        # But skip MCP tools that have enhanced workflow wrappers
        # This prevents raw MCP tools from competing with enhanced versions
        enhanced_mcp_tools = {
            'mcp_analyze_repository',  # Enhanced by repository_analyzer_llm.py
            'mcp_generate_repository_report',  # Enhanced by workflows
        }

        for tool_name, tool in self.mcp_tools.items():
            # Skip raw MCP tools that have enhanced workflow versions
            if tool_name in enhanced_mcp_tools:
                continue

            tool_domain = self._extract_domain_from_tool(tool_name)
            tool_action = self._extract_action_from_tool(tool_name)

            score = 0.0
            if tool_domain == domain:
                score += 0.4
            if tool_action == action:
                score += 0.4

            # Also check if tool description matches intent
            if hasattr(tool, 'description') and tool.description:
                desc = tool.description.lower()
                intent_words = intent.lower().split()
                matches = sum(1 for word in intent_words if len(word) > 3 and word in desc)
                if matches > 0:
                    score += min(matches * 0.05, 0.2)

            if score > 0.3:  # Only include tools with reasonable match
                # For MCP tools, we don't have a file path, so use a virtual path
                virtual_path = Path(f"mcp://{tool_name}")
                doc = tool.description if hasattr(tool, 'description') else ""

                results.append(ToolSpec(
                    path=virtual_path,
                    entry=tool_name,
                    args=[],
                    doc=doc,
                    score=score
                ))

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    def get_workflow(self, domain: str, action: str) -> Optional[Workflow]:
        """
        Get a specific workflow by domain and action.

        Args:
            domain: Workflow domain
            action: Workflow action

        Returns:
            Workflow if found, None otherwise
        """
        for workflow in self.workflows:
            if workflow.domain == domain and workflow.action == action:
                return workflow
        return None

    def list_workflows(self) -> List[Workflow]:
        """List all available workflows."""
        return self.workflows.copy()

    def list_mcp_tools(self) -> Dict[str, Any]:
        """List all available MCP tools."""
        return self.mcp_tools.copy()


# Convenience functions for backward compatibility

def parse(text: str, workflows_root: Path = None) -> ParsedIntent:
    """
    Parse user input to extract intent (backward compatible).

    Args:
        text: User input
        workflows_root: Optional workflows root (uses default if not provided)

    Returns:
        ParsedIntent
    """
    if workflows_root is None:
        from ..config.settings import load_settings
        settings = load_settings()
        workflows_root = settings.workflows_root

    router = MCPRouter(workflows_root)
    return router.parse_intent(text)


def discover(domain: str, action: str, intent: str, workflows_root: Path = None) -> List[ToolSpec]:
    """
    Discover tools based on domain and action (backward compatible).

    Args:
        domain: Parsed domain
        action: Parsed action
        intent: Full user intent
        workflows_root: Optional workflows root

    Returns:
        List of ToolSpec objects
    """
    if workflows_root is None:
        from ..config.settings import load_settings
        settings = load_settings()
        workflows_root = settings.workflows_root

    router = MCPRouter(workflows_root)
    return router.discover_tools(domain, action, intent)