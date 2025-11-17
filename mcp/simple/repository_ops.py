"""
Repository Operations MCP Domain

Provides MCPBase-compliant operations for Python repository analysis:
- Repository scanning and analysis
- File validation and metadata extraction
- Reusability scoring
- Dependency mapping
- Report generation (Excel, JSON)

Merged from repository_manager.py and repository_analyzer.py.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import Counter

from ..core.base import MCPBase, MCPResponse, MCPStatus
from ..core.decorators import read_only, write_safe, cached

# Import the underlying analyzer
try:
    from mcp.helpers.repository_analyzer import (
        RepositoryAnalyzer,
        FileInfo,
        FunctionInfo,
        ClassInfo
    )
    _HAS_ANALYZER = True
except ImportError:
    _HAS_ANALYZER = False
    RepositoryAnalyzer = None


class RepositoryOps(MCPBase):
    """
    Repository operations domain for MCP.

    Provides comprehensive Python repository analysis:
    - Scanning and analyzing entire repositories
    - File-level validation and metadata extraction
    - Reusability scoring for functions
    - Dependency analysis and mapping
    - Excel/JSON report generation
    - Statistics and issue tracking

    All methods return MCPResponse for standardized LLM interaction.
    Safety decorators applied: @read_only for analysis, @write_safe for reports.
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize the repository operations domain.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        super().__init__(logger=logger, context=context)

        # Initialize the underlying analyzer
        if not _HAS_ANALYZER or RepositoryAnalyzer is None:
            raise ImportError(
                "RepositoryAnalyzer not available - check that mcp.helpers.repository_analyzer is installed"
            )

        self.analyzer = RepositoryAnalyzer()

    # ===== Repository Analysis =====

    @read_only
    @cached(ttl=600)
    def analyze_repository(self, repo_path: str, ignore_patterns: Optional[List[str]] = None) -> MCPResponse:
        """
        Analyze a Python repository comprehensively.

        Safe read-only operation that:
        - Scans all Python files
        - Analyzes dependencies
        - Validates metadata
        - Calculates reusability scores
        - Generates statistics

        Results are cached for 10 minutes for performance.

        Args:
            repo_path: Path to repository root
            ignore_patterns: Optional list of patterns to ignore (e.g., ['test', '__pycache__'])

        Returns:
            MCPResponse with complete analysis results including:
            - repository: Repository path
            - files_analyzed: Number of files analyzed
            - statistics: Summary statistics
            - files: List of file information
            - issues_summary: Summary of issues found
            - reusability_summary: Reusability scores
        """
        response = self._create_response()
        response.add_trace(f"Analyzing repository: {repo_path}")

        try:
            root = Path(repo_path).resolve()

            if not root.is_dir():
                response.set_error(f"Path is not a directory: {repo_path}")
                return response

            response.add_trace(f"Repository root: {root}")

            # Set default ignore patterns
            if ignore_patterns is None:
                ignore_patterns = [
                    "__pycache__", ".venv", "venv", ".git", "build", "dist",
                    "node_modules", "test", "tests", ".pytest_cache"
                ]

            response.add_trace(f"Ignore patterns: {', '.join(ignore_patterns)}")

            # Perform analysis using underlying analyzer
            analysis = self.analyzer.analyze_repository(str(root), ignore_patterns)

            if not analysis.get("success"):
                response.set_error(analysis.get("error", "Analysis failed"))
                return response

            # Enrich response with trace information
            stats = analysis.get("statistics", {})
            response.add_trace(f"Analyzed {analysis.get('files_analyzed', 0)} files")
            response.add_trace(f"Found {stats.get('total_functions', 0)} functions")
            response.add_trace(f"Found {stats.get('total_classes', 0)} classes")
            response.add_trace(f"Total lines: {stats.get('total_lines', 0)}")

            # Set response data
            response.data = {
                'repository': str(root),
                'files_analyzed': analysis.get('files_analyzed', 0),
                'statistics': stats,
                'files': analysis.get('files', []),
                'issues_summary': analysis.get('issues_summary', {}),
                'reusability_summary': analysis.get('reusability_summary', {})
            }

            return response

        except Exception as e:
            response.set_error(f"Error analyzing repository: {str(e)}")
            return response

    # ===== File Validation =====

    @read_only
    def validate_file(self, file_path: str) -> MCPResponse:
        """
        Validate a single Python file.

        Safe read-only operation that checks:
        - File existence and type
        - Naming conventions
        - Metadata (owner, docstrings)
        - Code structure

        Args:
            file_path: Path to Python file

        Returns:
            MCPResponse with validation results including:
            - file: File path
            - issues: List of issues found
            - naming_valid: Whether naming is valid
            - metadata: File metadata (owner, atype, etc.)
            - statistics: File statistics
        """
        response = self._create_response()
        response.add_trace(f"Validating file: {file_path}")

        try:
            path = Path(file_path)

            if not path.exists():
                response.set_error(f"File not found: {file_path}")
                return response

            if not path.is_file():
                response.set_error(f"Not a file: {file_path}")
                return response

            if path.suffix != ".py":
                response.set_error(f"Not a Python file: {file_path}")
                return response

            response.add_trace("File type validated")

            # Perform validation using underlying analyzer
            validation = self.analyzer.validate_file(str(path))

            if not validation.get("success"):
                response.set_error(validation.get("error", "Validation failed"))
                return response

            # Enrich response
            issues = validation.get("issues", [])
            response.add_trace(f"Found {len(issues)} issue(s)")

            metadata = validation.get("metadata", {})
            if metadata.get("owner"):
                response.add_trace(f"Owner: {metadata['owner']}")

            response.data = {
                'file': str(path),
                'issues': issues,
                'naming_valid': validation.get('naming_valid', False),
                'metadata': metadata,
                'statistics': validation.get('statistics', {})
            }

            return response

        except Exception as e:
            response.set_error(f"Error validating file: {str(e)}")
            return response

    # ===== Report Generation =====

    @write_safe
    def generate_excel_report(self, analysis_result: Dict[str, Any], output_path: str) -> MCPResponse:
        """
        Generate comprehensive Excel report from analysis results.

        This is a write operation that creates an Excel file.
        Requires user confirmation in interactive mode.

        Args:
            analysis_result: Result from analyze_repository() (MCPResponse.data)
            output_path: Path for output Excel file

        Returns:
            MCPResponse with report details including:
            - output_path: Path to generated report
            - sheets: List of sheet names generated
            - message: Success message
        """
        response = self._create_response()
        response.add_trace(f"Generating Excel report: {output_path}")

        try:
            # Validate input
            if not isinstance(analysis_result, dict):
                response.set_error("analysis_result must be a dictionary")
                return response

            # Ensure openpyxl is available
            try:
                import openpyxl
                response.add_trace("Excel library available")
            except ImportError:
                response.set_error("openpyxl not installed - cannot generate Excel reports")
                return response

            # Prepare data for export
            export_data = {
                'success': True,
                'files': analysis_result.get('files', []),
                'statistics': analysis_result.get('statistics', {}),
                'repository': analysis_result.get('repository', '')
            }

            # Generate report using underlying analyzer
            result = self.analyzer.generate_excel_report(export_data, output_path)

            if not result.get("success"):
                response.set_error(result.get("error", "Report generation failed"))
                return response

            response.add_trace(f"Report generated: {output_path}")

            response.data = {
                'output_path': result.get('output_path', output_path),
                'sheets': result.get('sheets', []),
                'message': f"Excel report generated: {Path(output_path).name}"
            }

            return response

        except Exception as e:
            response.set_error(f"Error generating Excel report: {str(e)}")
            return response

    # ===== Dependency Analysis =====

    @read_only
    @cached(ttl=300)
    def analyze_dependencies(self, repo_path: str, ignore_patterns: Optional[List[str]] = None) -> MCPResponse:
        """
        Analyze dependencies in a repository.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            repo_path: Path to repository root
            ignore_patterns: Optional list of patterns to ignore

        Returns:
            MCPResponse with dependency analysis including:
            - dependency_graph: Graph structure of dependencies
            - metrics: Dependency metrics
            - top_imported: Most imported modules
            - circular_dependencies: Detected circular dependencies
        """
        response = self._create_response()
        response.add_trace(f"Analyzing dependencies: {repo_path}")

        try:
            # First perform full repository analysis
            analysis_result = self.analyze_repository(repo_path, ignore_patterns)

            if not analysis_result.success:
                return analysis_result

            # Extract dependency information
            files = analysis_result.data.get('files', [])

            # Build dependency graph
            dependency_graph = self._build_dependency_graph(files)

            # Calculate dependency metrics
            metrics = self._calculate_dependency_metrics(dependency_graph)

            response.add_trace(f"Analyzed dependencies for {len(files)} files")
            response.add_trace(f"Found {metrics['total_dependencies']} dependencies")

            response.data = {
                'dependency_graph': dependency_graph,
                'metrics': metrics,
                'top_imported': metrics.get('top_imported', []),
                'circular_dependencies': metrics.get('circular_dependencies', [])
            }

            return response

        except Exception as e:
            response.set_error(f"Error analyzing dependencies: {str(e)}")
            return response

    def _build_dependency_graph(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build dependency graph from file list.

        Args:
            files: List of file dictionaries

        Returns:
            Dependency graph structure
        """
        graph = {}

        for file_data in files:
            file_rel = file_data.get('file_rel', '')
            imports_third = file_data.get('imports_third', [])
            imports_local = file_data.get('imports_local', [])

            graph[file_rel] = {
                'third_party': imports_third,
                'local': imports_local,
                'total': len(imports_third) + len(imports_local)
            }

        return graph

    def _calculate_dependency_metrics(self, dependency_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate metrics from dependency graph.

        Args:
            dependency_graph: Dependency graph structure

        Returns:
            Dictionary with metrics
        """
        total_deps = sum(data['total'] for data in dependency_graph.values())

        # Count most imported modules
        module_counts = Counter()
        for file_data in dependency_graph.values():
            module_counts.update(file_data['third_party'])
            module_counts.update(file_data['local'])

        return {
            'total_dependencies': total_deps,
            'average_dependencies': total_deps / len(dependency_graph) if dependency_graph else 0,
            'top_imported': [
                {'module': mod, 'count': count}
                for mod, count in module_counts.most_common(10)
            ],
            'circular_dependencies': []  # Placeholder for circular dependency detection
        }

    # ===== Reusability Analysis =====

    @read_only
    @cached(ttl=300)
    def analyze_reusability(self, repo_path: str, ignore_patterns: Optional[List[str]] = None,
                           min_score: int = 5) -> MCPResponse:
        """
        Analyze function reusability in a repository.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            repo_path: Path to repository root
            ignore_patterns: Optional list of patterns to ignore
            min_score: Minimum reusability score to include in results

        Returns:
            MCPResponse with reusability analysis including:
            - total_functions: Number of functions analyzed
            - average_score: Average reusability score
            - max_score: Maximum score found
            - highly_reusable_functions: Functions with score >= min_score
            - threshold: Minimum score threshold used
        """
        response = self._create_response()
        response.add_trace(f"Analyzing reusability: {repo_path}")

        try:
            # Perform full repository analysis
            analysis_result = self.analyze_repository(repo_path, ignore_patterns)

            if not analysis_result.success:
                return analysis_result

            # Extract reusability summary
            reusability = analysis_result.data.get('reusability_summary', {})

            # Filter functions by minimum score
            top_functions = reusability.get('top_reusable_functions', [])
            filtered_functions = [
                func for func in top_functions
                if func.get('score', 0) >= min_score
            ]

            response.add_trace(f"Found {len(filtered_functions)} functions with score >= {min_score}")
            response.add_trace(f"Average score: {reusability.get('average_score', 0)}")

            response.data = {
                'total_functions': reusability.get('total_functions', 0),
                'average_score': reusability.get('average_score', 0),
                'max_score': reusability.get('max_score', 0),
                'highly_reusable_functions': filtered_functions,
                'threshold': min_score
            }

            return response

        except Exception as e:
            response.set_error(f"Error analyzing reusability: {str(e)}")
            return response

    # ===== Issues Summary =====

    @read_only
    def get_issues_summary(self, repo_path: str, ignore_patterns: Optional[List[str]] = None,
                          priority: Optional[str] = None) -> MCPResponse:
        """
        Get summary of issues found in repository.

        Safe read-only operation.

        Args:
            repo_path: Path to repository root
            ignore_patterns: Optional list of patterns to ignore
            priority: Optional priority filter ('HIGH', 'MEDIUM', 'LOW')

        Returns:
            MCPResponse with issues summary including:
            - total_issues: Total number of issues
            - by_priority: Issues grouped by priority
            - issues: List of issues (filtered if priority specified)
            - filter_applied: Priority filter used (if any)
        """
        response = self._create_response()
        response.add_trace(f"Getting issues summary: {repo_path}")

        try:
            # Perform full repository analysis
            analysis_result = self.analyze_repository(repo_path, ignore_patterns)

            if not analysis_result.success:
                return analysis_result

            # Extract issues summary
            issues = analysis_result.data.get('issues_summary', {})

            # Filter by priority if specified
            top_issues = issues.get('top_issues', [])
            if priority:
                top_issues = [
                    issue for issue in top_issues
                    if issue.get('priority', '').upper() == priority.upper()
                ]

            response.add_trace(f"Total issues: {issues.get('total_issues', 0)}")
            if priority:
                response.add_trace(f"Filtered by priority: {priority}")

            response.data = {
                'total_issues': issues.get('total_issues', 0),
                'by_priority': issues.get('by_priority', {}),
                'issues': top_issues,
                'filter_applied': priority
            }

            return response

        except Exception as e:
            response.set_error(f"Error getting issues summary: {str(e)}")
            return response

    # ===== Statistics =====

    @read_only
    @cached(ttl=300)
    def get_statistics(self, repo_path: str, ignore_patterns: Optional[List[str]] = None) -> MCPResponse:
        """
        Get repository statistics.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            repo_path: Path to repository root
            ignore_patterns: Optional list of patterns to ignore

        Returns:
            MCPResponse with statistics including:
            - total_files: Number of files
            - total_functions: Number of functions
            - total_classes: Number of classes
            - total_lines: Total lines of code
            - files_with_issues: Number of files with issues
            - compliance_rate: Percentage of compliant files
            - third_party_imports: Number of unique third-party imports
            - top_imports: Most frequently used imports
            - owners: File ownership distribution
        """
        response = self._create_response()
        response.add_trace(f"Getting statistics: {repo_path}")

        try:
            # Perform full repository analysis
            analysis_result = self.analyze_repository(repo_path, ignore_patterns)

            if not analysis_result.success:
                return analysis_result

            # Extract statistics
            stats = analysis_result.data.get('statistics', {})

            response.add_trace(f"Total files: {stats.get('total_files', 0)}")
            response.add_trace(f"Total functions: {stats.get('total_functions', 0)}")
            response.add_trace(f"Total lines: {stats.get('total_lines', 0)}")

            response.data = stats

            return response

        except Exception as e:
            response.set_error(f"Error getting statistics: {str(e)}")
            return response

    # ===== Quick Operations =====

    @read_only
    @cached(ttl=600)
    def scan_repository(self, repo_path: str, include_stats: bool = True) -> MCPResponse:
        """
        Quick scan of repository (lightweight alternative to full analysis).

        Safe read-only operation. Results cached for 10 minutes.

        Args:
            repo_path: Path to repository root
            include_stats: Whether to include statistics

        Returns:
            MCPResponse with scan results
        """
        response = self._create_response()
        response.add_trace(f"Scanning repository: {repo_path}")

        try:
            root = Path(repo_path).resolve()

            if not root.is_dir():
                response.set_error(f"Path is not a directory: {repo_path}")
                return response

            # Quick scan: just count Python files
            py_files = list(root.rglob("*.py"))
            py_files = [f for f in py_files if '__pycache__' not in str(f)]

            response.add_trace(f"Found {len(py_files)} Python files")

            response.data = {
                'repository': str(root),
                'files_found': len(py_files),
                'files': [str(f.relative_to(root)) for f in py_files[:100]]  # First 100
            }

            # Optionally include stats
            if include_stats:
                total_lines = 0
                for py_file in py_files:
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        total_lines += content.count('\n')
                    except:
                        pass

                response.data['total_lines_approx'] = total_lines
                response.add_trace(f"Approximate total lines: {total_lines}")

            return response

        except Exception as e:
            response.set_error(f"Error scanning repository: {str(e)}")
            return response
