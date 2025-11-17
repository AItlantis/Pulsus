"""
Pulse Generator - Enhanced Repository Analysis Outputs

Generates .pulse/ folder contents including:
- imports_graph.json: Dependency graph with circular dependency detection
- functions_index.json: Function signature index with cross-references
- cards/*.md: Script cards with comprehensive summaries
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime


class DependencyGraph:
    """Build and analyze import dependency graph."""

    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # file -> imported files
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # file -> files that import it

    def add_dependency(self, from_file: str, to_file: str):
        """Add a dependency edge."""
        self.graph[from_file].add(to_file)
        self.reverse_graph[to_file].add(from_file)

    def get_dependencies(self, file: str) -> Set[str]:
        """Get all files that this file imports."""
        return self.graph.get(file, set())

    def get_dependents(self, file: str) -> Set[str]:
        """Get all files that import this file."""
        return self.reverse_graph.get(file, set())

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependency cycles using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in self.graph.keys():
            if node not in visited:
                dfs(node, [])

        return cycles

    def calculate_fan_metrics(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate fan-in and fan-out metrics for each file.

        Returns:
            Dict mapping file paths to {fan_in, fan_out, instability}
        """
        metrics = {}

        all_files = set(self.graph.keys()) | set(self.reverse_graph.keys())

        for file in all_files:
            fan_out = len(self.graph.get(file, set()))  # Dependencies
            fan_in = len(self.reverse_graph.get(file, set()))  # Dependents

            # Instability metric: I = fan_out / (fan_in + fan_out)
            # I = 0: maximally stable (many dependents, few dependencies)
            # I = 1: maximally unstable (many dependencies, few dependents)
            total = fan_in + fan_out
            instability = fan_out / total if total > 0 else 0

            metrics[file] = {
                "fan_in": fan_in,
                "fan_out": fan_out,
                "instability": round(instability, 3)
            }

        return metrics

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to JSON-serializable dict."""
        return {
            "dependencies": {k: list(v) for k, v in self.graph.items()},
            "dependents": {k: list(v) for k, v in self.reverse_graph.items()},
            "circular_dependencies": self.find_circular_dependencies(),
            "metrics": self.calculate_fan_metrics()
        }


class FunctionIndex:
    """Index of all functions with signatures and cross-references."""

    def __init__(self):
        self.functions: Dict[str, Dict[str, Any]] = {}

    def add_function(self, file_path: str, func_info: Dict[str, Any],
                    used_in_files: Set[str] = None):
        """
        Add a function to the index.

        Args:
            file_path: Relative path to file containing function
            func_info: Function metadata (name, args, docstring, etc.)
            used_in_files: Set of files where this function is called
        """
        func_id = f"{file_path}::{func_info['name']}"

        self.functions[func_id] = {
            "name": func_info["name"],
            "file": file_path,
            "line": func_info.get("lineno", 0),
            "end_line": func_info.get("end_lineno", 0),
            "class_name": func_info.get("class_name"),
            "qualname": func_info.get("qualname", func_info["name"]),
            "args": func_info.get("args", []),
            "returns": func_info.get("returns"),
            "docstring": func_info.get("docstring"),
            "complexity": func_info.get("complexity"),
            "reusability_score": func_info.get("reusability_score"),
            "used_in": list(used_in_files) if used_in_files else [],
            "usage_count": len(used_in_files) if used_in_files else 0,
            "is_generic": func_info.get("is_generic_name", False),
            "has_hardcoded_paths": func_info.get("has_hardcoded_paths", False)
        }

    def get_function(self, func_id: str) -> Optional[Dict[str, Any]]:
        """Get function by ID (file::name)."""
        return self.functions.get(func_id)

    def search_functions(self, query: str) -> List[Dict[str, Any]]:
        """Search functions by name (partial match)."""
        query_lower = query.lower()
        return [
            func for func_id, func in self.functions.items()
            if query_lower in func["name"].lower()
        ]

    def get_top_reusable(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N most reusable functions."""
        sorted_funcs = sorted(
            self.functions.values(),
            key=lambda f: (f.get("reusability_score", 0), f.get("usage_count", 0)),
            reverse=True
        )
        return sorted_funcs[:limit]

    def get_most_used(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N most used functions."""
        sorted_funcs = sorted(
            self.functions.values(),
            key=lambda f: f.get("usage_count", 0),
            reverse=True
        )
        return sorted_funcs[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Convert index to JSON-serializable dict."""
        return {
            "total_functions": len(self.functions),
            "top_reusable": self.get_top_reusable(10),
            "most_used": self.get_most_used(10),
            "functions": self.functions
        }


class ScriptCardGenerator:
    """Generate Markdown script cards for .pulse/cards/."""

    @staticmethod
    def generate_card(file_info: Dict[str, Any], dep_graph: DependencyGraph,
                     func_index: FunctionIndex) -> str:
        """
        Generate a script card for a single file.

        Args:
            file_info: File analysis data
            dep_graph: Dependency graph
            func_index: Function index

        Returns:
            Markdown content for the script card
        """
        file_path = file_info.get("file_rel", "unknown")
        file_name = Path(file_path).name

        # Build card
        card = f"# {file_name}\n\n"

        # Overview
        card += "## Overview\n\n"
        card += f"**Path**: `{file_path}`  \n"
        card += f"**Size**: {file_info.get('size_kb', 0):.1f} KB  \n"
        card += f"**Lines**: {file_info.get('lines', 0)}  \n"
        card += f"**Modified**: {file_info.get('mtime', 'unknown')}  \n"
        card += "\n"

        # Metadata
        metadata = file_info.get("metadata", {})
        if metadata.get("owner") or metadata.get("atype"):
            card += "## Metadata\n\n"
            if metadata.get("owner"):
                card += f"**Owner**: {metadata['owner']}  \n"
            if metadata.get("atype"):
                card += f"**Type**: {metadata['atype']}  \n"
            if metadata.get("category_name"):
                card += f"**Category**: {metadata['category_name']}  \n"
            card += "\n"

        # Module docstring
        docstring = file_info.get("docstring")
        if docstring:
            card += "## Description\n\n"
            card += f"{docstring}\n\n"

        # Dependencies
        dependencies = dep_graph.get_dependencies(file_path)
        dependents = dep_graph.get_dependents(file_path)

        if dependencies or dependents:
            card += "## Dependencies\n\n"

            if dependencies:
                card += f"**Imports** ({len(dependencies)} files):  \n"
                for dep in sorted(dependencies)[:10]:
                    card += f"- `{dep}`\n"
                if len(dependencies) > 10:
                    card += f"- _{len(dependencies) - 10} more..._\n"
                card += "\n"

            if dependents:
                card += f"**Imported by** ({len(dependents)} files):  \n"
                for dep in sorted(dependents)[:10]:
                    card += f"- `{dep}`\n"
                if len(dependents) > 10:
                    card += f"- _{len(dependents) - 10} more..._\n"
                card += "\n"

        # Functions
        functions = file_info.get("functions", [])
        if functions:
            card += f"## Functions ({len(functions)})\n\n"

            for func in functions[:20]:  # Limit to first 20
                func_name = func.get("name", "unknown")
                args = func.get("args", [])
                args_str = ", ".join(args) if args else ""

                card += f"### `{func_name}({args_str})`\n\n"

                if func.get("docstring"):
                    card += f"{func['docstring'][:200]}...\n\n" if len(func.get("docstring", "")) > 200 else f"{func['docstring']}\n\n"

                card += f"**Line**: {func.get('lineno', 0)}  \n"

                if func.get("complexity"):
                    card += f"**Complexity**: {func['complexity']}  \n"

                if func.get("reusability_score"):
                    card += f"**Reusability**: {func['reusability_score']}/15  \n"

                used_in = func.get("used_in_files", set())
                if used_in:
                    card += f"**Used in**: {len(used_in)} files  \n"

                card += "\n"

            if len(functions) > 20:
                card += f"_... and {len(functions) - 20} more functions_\n\n"

        # Classes
        classes = file_info.get("classes", [])
        if classes:
            card += f"## Classes ({len(classes)})\n\n"

            for cls in classes[:10]:
                cls_name = cls.get("name", "unknown")
                card += f"### `{cls_name}`\n\n"

                if cls.get("docstring"):
                    card += f"{cls['docstring'][:200]}...\n\n" if len(cls.get("docstring", "")) > 200 else f"{cls['docstring']}\n\n"

                methods = cls.get("methods", [])
                if methods:
                    card += f"**Methods**: {len(methods)}  \n"
                    for method in methods[:5]:
                        card += f"- `{method.get('name', 'unknown')}`\n"
                    if len(methods) > 5:
                        card += f"- _{len(methods) - 5} more..._\n"

                card += "\n"

        # Issues
        issues = file_info.get("issues", [])
        if issues:
            card += f"## Issues ({len(issues)})\n\n"
            for issue in issues[:10]:
                card += f"- ⚠️ {issue}\n"
            if len(issues) > 10:
                card += f"- _{len(issues) - 10} more issues..._\n"
            card += "\n"

        # Footer
        card += "---\n"
        card += f"*Generated by Pulsus Repository Analyzer*  \n"
        card += f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return card


class PulseGenerator:
    """Main class for generating all .pulse/ outputs."""

    @staticmethod
    def generate_imports_graph(analysis_data: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate imports_graph.json from repository analysis.

        Args:
            analysis_data: Repository analysis results
            output_path: Path to save imports_graph.json

        Returns:
            True if generated successfully
        """
        try:
            dep_graph = DependencyGraph()

            files = analysis_data.get("files", [])
            repo_root = Path(analysis_data.get("repository", "."))

            # Build dependency graph
            for file_info in files:
                file_rel = file_info.get("file_rel", "")

                # Add local imports as dependencies
                for local_import in file_info.get("imports_local", []):
                    # Try to resolve import to actual file
                    dep_graph.add_dependency(file_rel, local_import)

            # Save to JSON
            output_path.parent.mkdir(parents=True, exist_ok=True)

            graph_data = dep_graph.to_dict()
            graph_data["generated_at"] = datetime.now().isoformat()
            graph_data["repository"] = str(repo_root)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2)

            return True

        except Exception as e:
            print(f"[pulse_generator] Error generating imports graph: {e}")
            return False

    @staticmethod
    def generate_functions_index(analysis_data: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate functions_index.json from repository analysis.

        Args:
            analysis_data: Repository analysis results
            output_path: Path to save functions_index.json

        Returns:
            True if generated successfully
        """
        try:
            func_index = FunctionIndex()

            files = analysis_data.get("files", [])

            # Build function index
            for file_info in files:
                file_rel = file_info.get("file_rel", "")

                for func in file_info.get("functions", []):
                    used_in_files = set(func.get("used_in_files", []))
                    func_index.add_function(file_rel, func, used_in_files)

            # Save to JSON
            output_path.parent.mkdir(parents=True, exist_ok=True)

            index_data = func_index.to_dict()
            index_data["generated_at"] = datetime.now().isoformat()
            index_data["repository"] = analysis_data.get("repository", ".")

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)

            return True

        except Exception as e:
            print(f"[pulse_generator] Error generating functions index: {e}")
            return False

    @staticmethod
    def generate_script_cards(analysis_data: Dict[str, Any], output_dir: Path) -> int:
        """
        Generate script cards for all files.

        Args:
            analysis_data: Repository analysis results
            output_dir: Directory to save script cards (.pulse/cards/)

        Returns:
            Number of cards generated
        """
        try:
            # Build dependency graph and function index
            dep_graph = DependencyGraph()
            func_index = FunctionIndex()

            files = analysis_data.get("files", [])

            # Build structures
            for file_info in files:
                file_rel = file_info.get("file_rel", "")

                # Add dependencies
                for local_import in file_info.get("imports_local", []):
                    dep_graph.add_dependency(file_rel, local_import)

                # Add functions
                for func in file_info.get("functions", []):
                    used_in_files = set(func.get("used_in_files", []))
                    func_index.add_function(file_rel, func, used_in_files)

            # Generate cards
            output_dir.mkdir(parents=True, exist_ok=True)
            cards_generated = 0

            for file_info in files:
                file_rel = file_info.get("file_rel", "")

                # Create card path maintaining directory structure
                rel_path = Path(file_rel)
                card_path = output_dir / rel_path.with_suffix('.md')

                # Ensure parent directory exists
                card_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate card content
                card_content = ScriptCardGenerator.generate_card(
                    file_info, dep_graph, func_index
                )

                # Write card
                with open(card_path, 'w', encoding='utf-8') as f:
                    f.write(card_content)

                cards_generated += 1

            return cards_generated

        except Exception as e:
            print(f"[pulse_generator] Error generating script cards: {e}")
            return 0

    @staticmethod
    def generate_all(analysis_data: Dict[str, Any], pulse_dir: Path) -> Dict[str, bool]:
        """
        Generate all .pulse/ outputs from analysis data.

        Args:
            analysis_data: Repository analysis results
            pulse_dir: Path to .pulse/ directory

        Returns:
            Dict with generation status for each output type
        """
        results = {}

        # Generate imports graph
        imports_graph_path = pulse_dir / "imports_graph.json"
        results["imports_graph"] = PulseGenerator.generate_imports_graph(
            analysis_data, imports_graph_path
        )

        # Generate functions index
        functions_index_path = pulse_dir / "functions_index.json"
        results["functions_index"] = PulseGenerator.generate_functions_index(
            analysis_data, functions_index_path
        )

        # Generate script cards
        cards_dir = pulse_dir / "cards"
        cards_count = PulseGenerator.generate_script_cards(analysis_data, cards_dir)
        results["script_cards"] = cards_count > 0
        results["cards_generated"] = cards_count

        return results
