from typing import List, Optional
from langchain_core.tools import tool
from pathlib import Path
import json

# Import all MCP helpers
try:
    from mcp.helpers.docs_helper import DocsHelper
    from mcp.helpers.aimsun_helper import AimsunHelper
    from mcp.helpers.qgis_helper import QGISHelper
    from mcp.helpers.executor import ScriptExecutor
except ImportError:
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from mcp.helpers.docs_helper import DocsHelper
        from mcp.helpers.aimsun_helper import AimsunHelper
        from mcp.helpers.qgis_helper import QGISHelper
        from mcp.helpers.executor import ScriptExecutor
    except ImportError:
        DocsHelper = None
        AimsunHelper = None
        QGISHelper = None
        ScriptExecutor = None

# Import ScriptOps separately
try:
    from mcp.helpers.script_ops import ScriptOps
except ImportError:
    ScriptOps = None

# Initialize global helper instances (will be populated from Qt context)
_docs_helper = DocsHelper() if DocsHelper else None
_aimsun_helper = None  # Set via make_aimsun_tools()
_qgis_helper = None    # Set via make_qgis_tools()
_executor = ScriptExecutor() if ScriptExecutor else None
_script_ops = ScriptOps() if ScriptOps else None

# ----- Simple local doc fetcher (replace with vector search later) -----
DOC_EXTS = {".md", ".txt", ".rst", ".py"}

@tool
def read_local_doc(path: str) -> str:
    """Read a small UTF-8 text file from the docs folder."""
    if _docs_helper:
        result = _docs_helper.read_doc(path)
        if result['success']:
            return result['content']
        else:
            return f"[read_local_doc] {result.get('error', 'Unknown error')}"

    # Fallback to direct file reading
    p = Path("docs") / path
    if not p.exists() or not p.is_file():
        return f"[read_local_doc] Not found: {p}"
    if p.suffix.lower() not in DOC_EXTS:
        return f"[read_local_doc] Unsupported extension: {p.suffix}"
    return p.read_text(encoding="utf-8")

@tool
def list_docs(sub: Optional[str] = None) -> List[str]:
    """List candidate doc files under docs/ (optionally within a subfolder)."""
    if _docs_helper:
        return _docs_helper.list_docs(subfolder=sub)

    # Fallback to direct file listing
    base = Path("docs")
    if sub:
        base = base / sub
    if not base.exists():
        return []
    return sorted(str(p.relative_to(Path("docs"))) for p in base.rglob("*") if p.suffix.lower() in DOC_EXTS)

# ----- Qt bridge placeholders (you will bind real callables from Qt) -----
# In your Qt app, pass functions with these signatures into compass.run()
def make_get_ui_context(func):
    """Wrap a Qt-side callable like: func() -> dict"""
    @tool
    def get_ui_context() -> dict:
        """Ask the Qt app for current context (selection, active file, etc.)."""
        try:
            return func() or {}
        except Exception as e:
            return {"error": str(e)}
    return get_ui_context

def make_run_in_qt(func):
    """Wrap a Qt-side callable like: func(code: str) -> str"""
    @tool
    def run_in_qt(code: str) -> str:
        """Request the Qt app to execute a small code block/snippet."""
        try:
            return str(func(code))
        except Exception as e:
            return f"[run_in_qt error] {e}"
    return run_in_qt

# ----- Documentation Search Tools -----

@tool
def search_aimsun_docs(query: str, max_results: int = 5) -> str:
    """
    Search Aimsun Next API documentation for classes, methods, or keywords.

    Args:
        query: Search query (e.g., 'GKSection', 'getSpeed', 'vehicle attributes')
        max_results: Maximum number of results to return (default 5)

    Returns:
        JSON string with search results including context and code examples

    Examples:
        - search_aimsun_docs("GKSection") - Find GKSection class documentation
        - search_aimsun_docs("getSpeed") - Find methods related to speed
        - search_aimsun_docs("vehicle") - Find vehicle-related APIs
    """
    if not _docs_helper:
        return json.dumps({
            "success": False,
            "error": "DocsHelper not available",
            "results": []
        })

    try:
        result = _docs_helper.search_aimsun_docs(query, max_results=max_results)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "results": []
        })

@tool
def search_qgis_docs(query: str, max_results: int = 5) -> str:
    """
    Search QGIS (PyQGIS) API documentation for classes, methods, or keywords.

    Args:
        query: Search query (e.g., 'QgsVectorLayer', 'addFeature', 'geometry')
        max_results: Maximum number of results to return (default 5)

    Returns:
        JSON string with search results including context and usage examples

    Examples:
        - search_qgis_docs("QgsVectorLayer") - Find QgsVectorLayer class
        - search_qgis_docs("addFeature") - Find feature creation methods
        - search_qgis_docs("export CSV") - Find CSV export functions
    """
    if not _docs_helper:
        return json.dumps({
            "success": False,
            "error": "DocsHelper not available",
            "results": []
        })

    try:
        result = _docs_helper.search_qgis_docs(query, max_results=max_results)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "results": []
        })

@tool
def search_api_docs(query: str, platform: str = "auto", max_results: int = 5) -> str:
    """
    Search API documentation for Aimsun or QGIS based on context.

    Args:
        query: Search query (class name, method, or keyword)
        platform: Target platform - 'aimsun', 'qgis', or 'auto' (default auto-detect)
        max_results: Maximum number of results (default 5)

    Returns:
        JSON string with search results from appropriate documentation

    The platform is auto-detected from keywords if set to 'auto':
    - Aimsun keywords: GK*, Aimsun, section, node, centroid, replication
    - QGIS keywords: Qgs*, PyQGIS, layer, feature, geometry, processing
    """
    if not _docs_helper:
        return json.dumps({
            "success": False,
            "error": "DocsHelper not available",
            "results": []
        })

    # Auto-detect platform from query
    if platform.lower() == "auto":
        aimsun_keywords = ['gk', 'aimsun', 'section', 'node', 'centroid', 'replication', 'turn']
        qgis_keywords = ['qgs', 'pyqgis', 'layer', 'feature', 'geometry', 'processing', 'vector']

        query_lower = query.lower()
        has_aimsun = any(kw in query_lower for kw in aimsun_keywords)
        has_qgis = any(kw in query_lower for kw in qgis_keywords)

        if has_aimsun and not has_qgis:
            platform = "aimsun"
        elif has_qgis and not has_aimsun:
            platform = "qgis"
        else:
            # Default to aimsun if ambiguous
            platform = "aimsun"

    try:
        if platform.lower() == "aimsun":
            result = _docs_helper.search_aimsun_docs(query, max_results=max_results)
        elif platform.lower() == "qgis":
            result = _docs_helper.search_qgis_docs(query, max_results=max_results)
        else:
            result = {
                "success": False,
                "error": f"Unknown platform: {platform}. Use 'aimsun', 'qgis', or 'auto'",
                "results": []
            }

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "results": []
        })


# ----- Aimsun Helper Tools -----

def make_aimsun_tools(amodel):
    """
    Create Aimsun helper tools bound to a specific model instance.
    Call this from Qt/UI to inject the real Aimsun model.

    Args:
        amodel: Aimsun model object (real or mock)

    Returns:
        List of LangChain tools
    """
    global _aimsun_helper
    if AimsunHelper:
        _aimsun_helper = AimsunHelper(amodel)

    @tool
    def get_aimsun_selection(max_items: int = 25) -> str:
        """
        Get detailed information about current Aimsun selection.

        Args:
            max_items: Maximum number of objects to return (default 25)

        Returns:
            JSON string with selection details including object IDs, names, types, and properties
        """
        if not _aimsun_helper:
            return json.dumps({"error": "Aimsun helper not available", "selection_count": 0})

        try:
            result = _aimsun_helper.get_selection_details(max_items=max_items)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "selection_count": 0})

    @tool
    def get_aimsun_network_stats() -> str:
        """
        Get network statistics for current Aimsun selection.

        Returns:
            JSON string with object counts by type and overall statistics
        """
        if not _aimsun_helper:
            return json.dumps({"error": "Aimsun helper not available"})

        try:
            result = _aimsun_helper.get_network_stats()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def validate_aimsun_selection() -> str:
        """
        Validate current Aimsun selection for common issues.

        Returns:
            JSON string with validation results and any issues found
        """
        if not _aimsun_helper:
            return json.dumps({"valid": False, "issues": ["Aimsun helper not available"]})

        try:
            result = _aimsun_helper.validate_selection()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"valid": False, "issues": [str(e)]})

    @tool
    def get_aimsun_object_properties(obj_id: int) -> str:
        """
        Get detailed properties for a specific Aimsun object.

        Args:
            obj_id: Object ID to query

        Returns:
            JSON string with object properties
        """
        if not _aimsun_helper:
            return json.dumps({"error": "Aimsun helper not available"})

        try:
            result = _aimsun_helper.get_object_properties(obj_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return [get_aimsun_selection, get_aimsun_network_stats,
            validate_aimsun_selection, get_aimsun_object_properties]


# ----- QGIS Helper Tools -----

def make_qgis_tools(iface):
    """
    Create QGIS helper tools bound to a specific interface instance.
    Call this from Qt/UI to inject the real QGIS interface.

    Args:
        iface: QGIS interface object (real or mock)

    Returns:
        List of LangChain tools
    """
    global _qgis_helper
    if QGISHelper:
        _qgis_helper = QGISHelper(iface)

    @tool
    def get_qgis_layer_info() -> str:
        """
        Get information about the active QGIS layer.

        Returns:
            JSON string with layer name, feature count, geometry type, and CRS
        """
        if not _qgis_helper:
            return json.dumps({"error": "QGIS helper not available", "has_layer": False})

        try:
            result = _qgis_helper.get_layer_info()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "has_layer": False})

    @tool
    def get_qgis_selected_features(max_features: int = 25) -> str:
        """
        Get detailed information about selected features in active QGIS layer.

        Args:
            max_features: Maximum number of features to return (default 25)

        Returns:
            JSON string with feature details including attributes and geometry
        """
        if not _qgis_helper:
            return json.dumps({"error": "QGIS helper not available", "selection_count": 0})

        try:
            result = _qgis_helper.get_selected_features(max_features=max_features)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "selection_count": 0})

    @tool
    def get_qgis_layer_extent() -> str:
        """
        Get spatial extent of the active QGIS layer.

        Returns:
            JSON string with xmin, ymin, xmax, ymax, and CRS
        """
        if not _qgis_helper:
            return json.dumps({"error": "QGIS helper not available"})

        try:
            result = _qgis_helper.get_layer_extent()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def get_qgis_layer_fields() -> str:
        """
        Get field schema for the active QGIS layer.

        Returns:
            JSON string with field names, types, and properties
        """
        if not _qgis_helper:
            return json.dumps({"error": "QGIS helper not available", "fields": []})

        try:
            result = _qgis_helper.get_layer_fields()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "fields": []})

    @tool
    def validate_qgis_selection() -> str:
        """
        Validate current QGIS selection for common issues.

        Returns:
            JSON string with validation results and any issues found
        """
        if not _qgis_helper:
            return json.dumps({"valid": False, "issues": ["QGIS helper not available"]})

        try:
            result = _qgis_helper.validate_selection()
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"valid": False, "issues": [str(e)]})

    return [get_qgis_layer_info, get_qgis_selected_features, get_qgis_layer_extent,
            get_qgis_layer_fields, validate_qgis_selection]


# ----- Code Execution Tools -----

@tool
def validate_python_code(code: str) -> str:
    """
    Validate Python code for safety before execution.

    Args:
        code: Python code to validate

    Returns:
        JSON string with validation results and any security issues
    """
    if not _executor:
        return json.dumps({
            "valid": False,
            "error": "ScriptExecutor not available",
            "issues": []
        })

    try:
        result = _executor.validate(code)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "valid": False,
            "error": str(e),
            "issues": []
        })

@tool
def execute_safe_python(code: str, timeout: int = 30) -> str:
    """
    Execute Python code in a safe sandboxed environment.

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds (default 30, max 30)

    Returns:
        JSON string with execution results, stdout, or error messages

    Security:
        - Blocks dangerous modules (os, sys, subprocess, etc.)
        - Blocks dangerous builtins (eval, exec, compile, __import__)
        - Enforces timeout
        - Validates code via AST before execution
    """
    if not _executor:
        return json.dumps({
            "success": False,
            "error": "ScriptExecutor not available",
            "output": "",
            "execution_time": 0
        })

    try:
        result = _executor.execute_safe(code, timeout=min(timeout, 30))
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "output": "",
            "execution_time": 0
        })


# ----- Script Operations MCP Tools -----

@tool
def mcp_read_script(path: str) -> str:
    """
    Read and analyze a Python script using MCP.

    Args:
        path: Path to the Python script

    Returns:
        JSON string with script content, AST analysis, and metadata

    This is the formal MCP replacement for the text-triggered "read" function.
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        result = _script_ops.read_script(path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_write_md(path: str, content: str = None) -> str:
    """
    Generate or write Markdown documentation for a Python script using MCP.

    Args:
        path: Path to the Python script
        content: Optional pre-generated Markdown content. If None, will auto-generate.

    Returns:
        JSON string with doc_path and status

    This is the formal MCP replacement for the text-triggered "write_md" function.
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        result = _script_ops.write_md(path, content)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_add_comments(path: str, strategy: str = "docstring") -> str:
    """
    Generate and add comments/docstrings to functions in a Python script using MCP.

    Args:
        path: Path to the Python script
        strategy: Comment strategy - 'docstring' (default) or 'inline'

    Returns:
        JSON string with generated comments for all functions

    This is the formal MCP replacement for the text-triggered "add_comments" function.
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        result = _script_ops.add_comments(path, strategy)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_format_script(path: str, check_only: bool = False) -> str:
    """
    Auto-format and normalize a Python script using black, isort, and autoflake.

    Args:
        path: Path to the Python script
        check_only: If True, only check formatting without making changes (default False)

    Returns:
        JSON string with formatting results including changes made

    Formatting steps:
    1. Remove unused imports and variables (autoflake)
    2. Sort imports (isort with black profile)
    3. Apply black formatting

    Example:
        mcp_format_script("path/to/script.py")
        mcp_format_script("path/to/script.py", check_only=True)
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        result = _script_ops.format_script(path, check_only)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_scan_structure(base_dir: str, include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> str:
    """
    Scan directory structure and create dependency map for Python scripts.

    Args:
        base_dir: Base directory to scan
        include_patterns: Optional list of glob patterns to include (default: ['*.py'])
        exclude_patterns: Optional list of patterns to exclude (default: ['__pycache__', '*.pyc', '.git', 'venv'])

    Returns:
        JSON string with directory structure, dependency map, and statistics

    Returns:
    - structure: Hierarchical directory tree
    - dependency_map: File-by-file import analysis
    - statistics: Total files, lines, imports, and top imported modules

    Example:
        mcp_scan_structure("agents/pulsus")
        mcp_scan_structure("agents", include_patterns=['*.py'], exclude_patterns=['tests', '__pycache__'])
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        result = _script_ops.scan_structure(base_dir, include_patterns, exclude_patterns)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# ----- Repository Analysis Tools -----

# Import repository analyzer
try:
    from mcp.helpers.repository_analyzer import RepositoryAnalyzer
    _repo_analyzer = RepositoryAnalyzer()
except ImportError:
    _repo_analyzer = None


@tool
def mcp_analyze_repository(repo_path: str, ignore_patterns: Optional[List[str]] = None,
                           mode: str = "analyze") -> str:
    """
    Analyze a Python repository comprehensively.

    Provides:
    - File metadata validation (ownership, naming conventions, docstrings)
    - Function reusability scoring
    - Dependency analysis (imports, local vs third-party)
    - Code complexity metrics
    - Issue detection and reporting

    Args:
        repo_path: Path to repository root directory
        ignore_patterns: Optional list of patterns to ignore (default: ['test', '__pycache__', '.venv'])
        mode: Operation mode - 'analyze' (default), 'comment', or 'document'

    Returns:
        JSON string with comprehensive analysis results including:
        - statistics: Overall repository metrics
        - files: List of analyzed files with metadata
        - issues_summary: Prioritized list of issues
        - reusability_summary: Top reusable functions

    Example:
        mcp_analyze_repository("path/to/repository")
        mcp_analyze_repository("agents/pulsus", ignore_patterns=["tests", "__pycache__"])
        mcp_analyze_repository("agents/pulsus", mode="comment")
    """
    if not _repo_analyzer:
        return json.dumps({
            "success": False,
            "error": "RepositoryAnalyzer not available"
        })

    try:
        result = _repo_analyzer.analyze_repository(repo_path, ignore_patterns)

        # Add mode to result for downstream processing
        result['mode'] = mode

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_generate_repository_report(repo_path: str, output_path: str,
                                   ignore_patterns: Optional[List[str]] = None) -> str:
    """
    Generate comprehensive Excel report for a Python repository.

    Analyzes the repository and generates an Excel file with multiple sheets:
    - Summary & Actions: Dashboard with key metrics and action items
    - Issues & Warnings: Prioritized list of code quality issues
    - Files Overview: All files with status, owner, and metadata
    - Reusability Analysis: Functions scored by reusability potential
    - Functions & Complexity: All functions with complexity metrics
    - Function Calls: Call graph and usage tracking

    Args:
        repo_path: Path to repository root directory
        output_path: Path for output Excel file (e.g., "report.xlsx")
        ignore_patterns: Optional patterns to ignore during analysis

    Returns:
        JSON string with generation results and output file path

    Example:
        mcp_generate_repository_report("agents/pulsus", "pulsus_analysis.xlsx")
    """
    if not _repo_analyzer:
        return json.dumps({
            "success": False,
            "error": "RepositoryAnalyzer not available"
        })

    try:
        # First analyze the repository
        analysis = _repo_analyzer.analyze_repository(repo_path, ignore_patterns)

        if not analysis.get("success"):
            return json.dumps(analysis)

        # Then generate the Excel report
        result = _repo_analyzer.generate_excel_report(analysis, output_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_validate_python_file(file_path: str) -> str:
    """
    Validate a single Python file for quality and compliance.

    Checks:
    - File naming conventions
    - Metadata presence (owner, type, description)
    - Code structure and complexity
    - Import organization
    - Docstring completeness

    Args:
        file_path: Path to Python file to validate

    Returns:
        JSON string with validation results:
        - issues: List of validation issues found
        - metadata: Extracted file metadata
        - statistics: Lines, functions, classes, imports

    Example:
        mcp_validate_python_file("agents/pulsus/routing/mcp_router.py")
    """
    if not _repo_analyzer:
        return json.dumps({
            "success": False,
            "error": "RepositoryAnalyzer not available"
        })

    try:
        result = _repo_analyzer.validate_file(file_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_comment_repository(repo_path: str, ignore_patterns: Optional[List[str]] = None,
                           strategy: str = "docstring") -> str:
    """
    Generate comments/docstrings for all functions in a repository.

    This tool analyzes the repository and generates comments for functions
    without modifying files. Results are returned in memory for LLM context.

    Args:
        repo_path: Path to repository root directory
        ignore_patterns: Optional list of patterns to ignore
        strategy: Comment strategy - 'docstring' (default) or 'inline'

    Returns:
        JSON string with generated comments for each file:
        - files_processed: Number of files processed
        - total_functions: Total functions found
        - comments: Dict mapping file paths to function comments

    Example:
        mcp_comment_repository("agents/pulsus")
        mcp_comment_repository("agents/pulsus", strategy="inline")
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        from pathlib import Path

        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            return json.dumps({
                "success": False,
                "error": f"Repository path does not exist: {repo_path}"
            })

        # Get all Python files
        if ignore_patterns is None:
            ignore_patterns = ['test', '__pycache__', '.venv', 'venv', '.git']

        py_files = []
        for file_path in repo_path_obj.rglob("*.py"):
            # Skip ignored patterns
            if any(pattern in str(file_path) for pattern in ignore_patterns):
                continue
            py_files.append(file_path)

        # Generate comments for each file
        all_comments = {}
        total_functions = 0

        for file_path in py_files:
            result = _script_ops.add_comments(str(file_path), strategy, show_progress=False)

            if result.get("success"):
                comments = result.get("comments", {})
                all_comments[str(file_path.relative_to(repo_path_obj))] = comments
                total_functions += len(comments)

        return json.dumps({
            "success": True,
            "files_processed": len(py_files),
            "total_functions": total_functions,
            "comments": all_comments,
            "strategy": strategy
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_document_repository(repo_path: str, ignore_patterns: Optional[List[str]] = None,
                            output_dir: Optional[str] = None) -> str:
    """
    Generate documentation for all scripts in a repository.

    Creates Markdown documentation files for each Python script.
    If output_dir is not specified, creates .pulse/docs/ folder.

    Args:
        repo_path: Path to repository root directory
        ignore_patterns: Optional list of patterns to ignore
        output_dir: Optional output directory (default: {repo}/.pulse/docs/)

    Returns:
        JSON string with documentation generation results:
        - files_processed: Number of files documented
        - output_directory: Where docs were saved
        - files: List of generated documentation files

    Example:
        mcp_document_repository("agents/pulsus")
        mcp_document_repository("agents/pulsus", output_dir="docs/api")
    """
    if not _script_ops:
        return json.dumps({
            "success": False,
            "error": "ScriptOps helper not available"
        })

    try:
        from pathlib import Path

        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            return json.dumps({
                "success": False,
                "error": f"Repository path does not exist: {repo_path}"
            })

        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            from shared.settings import get_framework_config
            pulse_folder = get_framework_config("pulse_folder") or ".pulse"
            output_path = repo_path_obj / pulse_folder / "docs"

        output_path.mkdir(parents=True, exist_ok=True)

        # Get all Python files
        if ignore_patterns is None:
            ignore_patterns = ['test', '__pycache__', '.venv', 'venv', '.git', '.pulse']

        py_files = []
        for file_path in repo_path_obj.rglob("*.py"):
            # Skip ignored patterns
            if any(pattern in str(file_path) for pattern in ignore_patterns):
                continue
            py_files.append(file_path)

        # Generate documentation for each file
        generated_docs = []

        for file_path in py_files:
            # Create output path maintaining directory structure
            rel_path = file_path.relative_to(repo_path_obj)
            doc_path = output_path / rel_path.with_suffix('.md')

            # Ensure parent directory exists
            doc_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate documentation
            result = _script_ops.write_md(str(file_path))

            if result.get("success"):
                # Move generated doc to output path if needed
                source_doc = Path(result.get("doc_path", ""))
                if source_doc.exists() and source_doc != doc_path:
                    import shutil
                    shutil.move(str(source_doc), str(doc_path))

                generated_docs.append(str(doc_path.relative_to(repo_path_obj)))

        return json.dumps({
            "success": True,
            "files_processed": len(py_files),
            "docs_generated": len(generated_docs),
            "output_directory": str(output_path),
            "files": generated_docs
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# ----- Tool Collections -----

# Base documentation tools (always available)
BASE_TOOLS = [
    read_local_doc,
    list_docs,
    search_aimsun_docs,
    search_qgis_docs,
    search_api_docs,
    validate_python_code,
    execute_safe_python,
    mcp_read_script,
    mcp_write_md,
    mcp_add_comments,
    mcp_format_script,
    mcp_scan_structure,
    mcp_analyze_repository,
    mcp_generate_repository_report,
    mcp_validate_python_file,
    mcp_comment_repository,
    mcp_document_repository
]
