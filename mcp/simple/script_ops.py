"""
Script Operations MCP Domain

Provides MCPBase-compliant operations for Python script manipulation:
- Reading and analyzing scripts
- Generating documentation
- Adding comments/docstrings
- Code formatting
- Structure scanning

Migrated from mcp/helpers/script_ops.py to use MCPBase framework.
"""

from pathlib import Path
import ast
import re
import requests
from typing import Dict, Any, List, Optional

from ..core.base import MCPBase, MCPResponse, MCPStatus
from ..core.decorators import read_only, write_safe, cached
from config.settings import load_settings
from ui import display_manager as ui


class ScriptOps(MCPBase):
    """
    Script operations domain for MCP.

    Provides core functionality for:
    - Reading and analyzing Python scripts (AST parsing)
    - Generating documentation (AI-powered or fallback)
    - Adding comments/docstrings to functions (AI-powered)
    - Code formatting (black, isort, autoflake)
    - Structure scanning and dependency mapping

    All methods return MCPResponse for standardized LLM interaction.
    Safety decorators applied: @read_only for reads, @write_safe for writes.
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize the script operations domain.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        super().__init__(logger=logger, context=context)
        self.settings = load_settings()

    # ===== Path Validation =====

    def _validate_path(self, path: str) -> tuple[bool, Optional[Path], Optional[str]]:
        """
        Validate a file path for safety and existence.

        Args:
            path: File path to validate

        Returns:
            Tuple of (is_valid, Path object, error_message)
        """
        try:
            file_path = Path(path)

            # Check existence
            if not file_path.exists():
                return False, None, f"File not found: {path}"

            # Check if it's a file
            if not file_path.is_file():
                return False, None, f"Not a file: {path}"

            # Check if it's a Python file
            if file_path.suffix != '.py':
                return False, None, f"Not a Python file: {path}"

            return True, file_path, None

        except Exception as e:
            return False, None, f"Path validation error: {str(e)}"

    # ===== Script Reading & Analysis =====

    @read_only
    def read_script(self, path: str) -> MCPResponse:
        """
        Read and analyze a Python script.

        Args:
            path: Path to the Python script

        Returns:
            MCPResponse with data containing:
            - content: Script source code
            - ast_analysis: AST analysis (functions, classes, imports)
            - metadata: Module metadata (__domain__, __action__, etc.)
            - file_path: Resolved file path
        """
        response = self._create_response()
        response.add_trace(f"Reading script: {path}")

        # Validate path
        is_valid, file_path, error = self._validate_path(path)
        if not is_valid:
            response.set_error(error)
            return response

        try:
            # Read content
            content = file_path.read_text(encoding='utf-8')
            response.add_trace(f"Read {len(content)} characters")

            # Perform AST analysis
            ast_analysis = self._analyze_ast(file_path)
            response.add_trace(
                f"AST analysis: {len(ast_analysis.get('functions', []))} functions, "
                f"{len(ast_analysis.get('classes', []))} classes"
            )

            # Load metadata
            metadata = self._load_module_metadata(file_path)

            # Set response data
            response.data = {
                'content': content,
                'ast_analysis': ast_analysis,
                'metadata': metadata,
                'file_path': str(file_path)
            }

            response.add_trace("Script read successfully")
            return response

        except Exception as e:
            response.set_error(f"Error reading script: {str(e)}")
            return response

    def _analyze_ast(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse Python file using AST and extract structure information.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary containing functions, classes, imports, and module docstring
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "module_docstring": ast.get_docstring(tree) or ""
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                        "line": node.lineno
                    }
                    analysis["functions"].append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node) or "",
                        "line": node.lineno
                    }
                    analysis["classes"].append(class_info)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")

            return analysis

        except Exception as e:
            return {"error": str(e)}

    def _load_module_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Load module and extract metadata attributes like __domain__, __action__.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with metadata
        """
        import importlib.util

        metadata = {
            "domain": None,
            "action": None,
            "doc": None
        }

        try:
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            metadata["domain"] = getattr(module, "__domain__", None)
            metadata["action"] = getattr(module, "__action__", None)
            metadata["doc"] = getattr(module, "__doc__", None)

        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    # ===== Documentation Generation =====

    @write_safe
    def write_md(self, path: str, content: Optional[str] = None) -> MCPResponse:
        """
        Generate or write Markdown documentation for a Python script.

        Args:
            path: Path to the Python script
            content: Optional pre-generated Markdown content. If None, will auto-generate.

        Returns:
            MCPResponse with data containing:
            - doc_path: Path to generated documentation file
            - message: Success message
        """
        response = self._create_response()
        response.add_trace(f"Writing documentation for: {path}")

        # Validate path
        is_valid, file_path, error = self._validate_path(path)
        if not is_valid:
            response.set_error(error)
            return response

        try:
            # Read script if content not provided
            if content is None:
                script_response = self.read_script(str(file_path))
                if not script_response.success:
                    response.set_error(script_response.error)
                    return response

                # Generate documentation using LLM
                content = self._generate_documentation_content(
                    file_path,
                    script_response.data['content'],
                    script_response.data['ast_analysis'],
                    script_response.data['metadata']
                )
                response.add_trace("Documentation generated via LLM")

            # Create .md file path
            doc_path = file_path.with_suffix('.md')

            # Save documentation
            doc_path.write_text(content, encoding='utf-8')
            response.add_trace(f"Documentation written to: {doc_path}")

            # Set response data
            response.data = {
                'doc_path': str(doc_path),
                'message': f"Documentation created: {doc_path.name}"
            }

            return response

        except Exception as e:
            response.set_error(f"Error writing documentation: {str(e)}")
            return response

    def _generate_documentation_content(self, file_path: Path, content: str,
                                       ast_analysis: Dict, metadata: Dict) -> str:
        """
        Generate comprehensive documentation content using LLM.

        Args:
            file_path: Path to the script
            content: Script content
            ast_analysis: AST analysis
            metadata: Module metadata

        Returns:
            Markdown documentation content
        """
        # Build structured prompt for comprehensive documentation
        functions_list = "\n".join([
            f"- {f['name']}({', '.join(f['args'])}): {f['docstring'][:100]}"
            for f in ast_analysis.get('functions', [])
        ])

        classes_list = "\n".join([
            f"- {c['name']}: {c['docstring'][:100]}"
            for c in ast_analysis.get('classes', [])
        ])

        prompt = f"""Create comprehensive documentation in Markdown format for this Python script.

File: {file_path.name}
Path: {file_path}

Functions:
{functions_list or "None"}

Classes:
{classes_list or "None"}

Code Sample (first 5000 chars):
```python
{content[:5000]}
```

Create detailed documentation following this structure:

# {file_path.name}

## Overview
[2-3 paragraphs explaining purpose, main functionality, and use cases]

## Features
- [Key feature 1]
- [Key feature 2]
- [etc.]

## Installation & Dependencies
[List required packages and installation instructions]

## Usage

### Basic Usage
[Simple example of how to use the script]

### Advanced Usage
[More complex examples if applicable]

## API Reference

### Functions
[For each main function: signature, parameters, return value, description]

### Classes
[For each class: purpose, main methods, usage examples]

## Implementation Details
[Technical notes about the implementation approach]

## Examples
[Practical code examples showing real usage]

## Notes
[Important considerations, limitations, or gotchas]

---
*Auto-generated by Pulsus MCP on {file_path.as_posix()}*

Write in clear, professional technical documentation style. Be comprehensive but concise."""

        try:
            ui.info("Generating comprehensive documentation with LLM (this may take 30-60 seconds)...")
            ui.info("📝 Analyzing code structure and relationships...")

            response = requests.post(
                f"{self.settings.model.host}/api/generate",
                json={
                    "model": self.settings.model.name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 2048,
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                ui.success("✓ Documentation generated successfully!")
                return result.get("response", "").strip()
            else:
                ui.warn(f"LLM request failed (status {response.status_code}). Using fallback documentation.")
                return self._generate_fallback_documentation(file_path, ast_analysis, metadata)

        except requests.exceptions.ConnectionError:
            ui.warn(f"Cannot connect to Ollama at {self.settings.model.host}. Using fallback documentation.")
            ui.info("Tip: Start Ollama with 'ollama serve' for AI-generated documentation.")
            return self._generate_fallback_documentation(file_path, ast_analysis, metadata)
        except Exception as e:
            ui.warn(f"Error generating documentation: {str(e)[:100]}")
            return self._generate_fallback_documentation(file_path, ast_analysis, metadata)

    def _generate_fallback_documentation(self, file_path: Path, ast_analysis: Dict,
                                        metadata: Dict) -> str:
        """
        Generate basic documentation when LLM is unavailable.

        Args:
            file_path: Path to the script
            ast_analysis: AST analysis
            metadata: Module metadata

        Returns:
            Basic markdown documentation
        """
        doc = f"# {file_path.name}\n\n"
        doc += "## Overview\n\n"
        doc += f"{ast_analysis.get('module_docstring', 'No description available.')}\n\n"

        # Metadata
        if metadata.get('domain') or metadata.get('action'):
            doc += "## Metadata\n\n"
            if metadata.get('domain'):
                doc += f"- **Domain**: {metadata['domain']}\n"
            if metadata.get('action'):
                doc += f"- **Action**: {metadata['action']}\n"
            doc += "\n"

        # Functions
        if ast_analysis.get('functions'):
            doc += "## Functions\n\n"
            for func in ast_analysis['functions']:
                args = ', '.join(func['args'])
                doc += f"### `{func['name']}({args})`\n\n"
                if func['docstring']:
                    doc += f"{func['docstring']}\n\n"
                doc += f"**Line**: {func['line']}\n\n"

        # Classes
        if ast_analysis.get('classes'):
            doc += "## Classes\n\n"
            for cls in ast_analysis['classes']:
                doc += f"### `{cls['name']}`\n\n"
                if cls['docstring']:
                    doc += f"{cls['docstring']}\n\n"
                if cls['methods']:
                    doc += f"**Methods**: {', '.join(cls['methods'])}\n\n"
                doc += f"**Line**: {cls['line']}\n\n"

        # Imports
        if ast_analysis.get('imports'):
            doc += "## Dependencies\n\n"
            for imp in ast_analysis['imports'][:20]:
                doc += f"- `{imp}`\n"
            doc += "\n"

        doc += "---\n"
        doc += f"*Auto-generated documentation by Pulsus MCP*\n"

        return doc

    # ===== Function Commenting =====

    @read_only
    def add_comments(self, path: str, strategy: str = "docstring", show_progress: bool = True) -> MCPResponse:
        """
        Generate and return comments/docstrings for functions in a Python script.

        Note: This method ONLY generates comments, it does not modify the file.
        Use the returned comments to apply them to the file as needed.

        Args:
            path: Path to the Python script
            strategy: Comment strategy - 'docstring' (default) or 'inline'
            show_progress: Whether to show progress messages

        Returns:
            MCPResponse with data containing:
            - functions_commented: Number of functions processed
            - comments: List of comment dictionaries with:
              - function: Function name
              - line: Line number
              - comment: Generated comment text
              - formatted: Formatted docstring
        """
        response = self._create_response()
        response.add_trace(f"Generating comments for: {path}")

        # Validate path
        is_valid, file_path, error = self._validate_path(path)
        if not is_valid:
            response.set_error(error)
            return response

        try:
            # Analyze functions
            functions = self._analyze_functions(file_path)
            response.add_trace(f"Found {len(functions)} functions")

            if not functions:
                response.data = {
                    'functions_commented': 0,
                    'comments': [],
                    'message': 'No functions found to comment'
                }
                return response

            # Get file context
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
                file_context = ast.get_docstring(tree) or f"Python module: {file_path.name}"
            except:
                file_context = f"Python module: {file_path.name}"

            # Generate comments for each function
            comments = []
            total_funcs = len(functions)

            for idx, func in enumerate(functions, 1):
                # Show progress to user
                if show_progress:
                    ui.info(f"Generating docstring for {func['name']}() [{idx}/{total_funcs}]...")

                comment = self._generate_function_comment(func, file_context)
                formatted_comment = self._format_docstring(comment)

                comments.append({
                    "function": func['name'],
                    "line": func['line'],
                    "comment": comment,
                    "formatted": formatted_comment
                })

            response.add_trace(f"Generated {len(comments)} comments")

            response.data = {
                'functions_commented': len(comments),
                'comments': comments,
                'message': f"Generated comments for {len(comments)} functions"
            }

            return response

        except Exception as e:
            response.set_error(f"Error adding comments: {str(e)}")
            return response

    def _analyze_functions(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse Python file and extract all function definitions.

        Args:
            file_path: Path to Python file

        Returns:
            List of dictionaries containing function information
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function signature
                    args_list = []
                    for arg in node.args.args:
                        arg_str = arg.arg
                        if arg.annotation:
                            arg_str += f": {ast.unparse(arg.annotation)}"
                        args_list.append(arg_str)

                    # Get return annotation
                    returns = ""
                    if node.returns:
                        returns = ast.unparse(node.returns)

                    # Extract source code
                    source = self._extract_function_source(file_path, node)

                    func_info = {
                        "name": node.name,
                        "args": args_list,
                        "returns": returns,
                        "line": node.lineno,
                        "existing_docstring": ast.get_docstring(node) or "",
                        "source": source
                    }
                    functions.append(func_info)

            return functions

        except Exception as e:
            return []

    def _extract_function_source(self, file_path: Path, func_node: ast.FunctionDef) -> str:
        """
        Extract the source code for a specific function from the file.

        Args:
            file_path: Path to the Python file
            func_node: AST FunctionDef node

        Returns:
            Source code of the function as string
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            start_line = func_node.lineno - 1
            end_line = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start_line + 10

            func_lines = lines[start_line:end_line]
            return '\n'.join(func_lines)
        except Exception as e:
            return f"# Error extracting source: {str(e)}"

    def _generate_function_comment(self, func_info: Dict[str, Any], file_context: str) -> str:
        """
        Use LLM to generate a detailed comment for a function.

        Args:
            func_info: Dictionary containing function information
            file_context: Brief context about the file/module

        Returns:
            Generated docstring comment
        """
        args_display = ", ".join(func_info['args']) if func_info['args'] else ""
        returns_display = f" -> {func_info['returns']}" if func_info['returns'] else ""

        prompt = f"""Generate a detailed Python docstring for this function.

File Context: {file_context}

Function:
```python
{func_info['source']}
```

Generate a comprehensive docstring following this format:
- Brief one-line description
- Detailed explanation (if needed)
- Args section with parameter descriptions
- Returns section with return value description
- Raises section (if applicable)

Use Google-style docstring format. Be concise but thorough.
{f"Existing docstring (improve/expand if inadequate): {func_info['existing_docstring']}" if func_info['existing_docstring'] else ""}

Output ONLY the docstring text (no code fences, no extra commentary)."""

        try:
            response = requests.post(
                f"{self.settings.model.host}/api/generate",
                json={
                    "model": self.settings.model.name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 400,
                    }
                },
                timeout=self.settings.model.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            elif response.status_code == 404:
                return f"""[Error: Ollama not available]

Please start Ollama:
1. Open a new terminal
2. Run: ollama serve
3. Try again

Alternative: Use environment variable to configure a different LLM endpoint.
"""
            else:
                return f"[Error: LLM request failed with status {response.status_code}]"

        except requests.exceptions.ConnectionError:
            return f"""[Error: Cannot connect to Ollama at {self.settings.model.host}]

Please start Ollama:
1. Open a new terminal
2. Run: ollama serve
3. Try again

Or set OLLAMA_HOST environment variable to a different endpoint.
"""
        except Exception as e:
            return f"[Error generating comment: {str(e)[:100]}]"

    def _format_docstring(self, comment: str, indent_level: int = 1) -> str:
        """
        Format comment as a proper Python docstring with correct indentation.

        Args:
            comment: The comment text
            indent_level: Number of indentation levels (default 1)

        Returns:
            Formatted docstring with triple quotes and proper indentation
        """
        indent = "    " * indent_level
        lines = comment.split('\n')

        formatted = f'{indent}"""\n'
        for line in lines:
            formatted += f'{indent}{line}\n'
        formatted += f'{indent}"""\n'

        return formatted

    # ===== Script Formatting =====

    @write_safe
    def format_script(self, path: str, check_only: bool = False) -> MCPResponse:
        """
        Auto-format and normalize a Python script.

        Uses black for formatting, isort for import sorting, and autoflake for cleanup.

        Args:
            path: Path to the Python script
            check_only: If True, only check formatting without making changes

        Returns:
            MCPResponse with data containing:
            - formatted: Whether formatting was applied
            - changes: List of formatting changes made
            - message: Summary message
        """
        response = self._create_response()
        response.add_trace(f"Formatting script: {path} (check_only={check_only})")

        # Validate path
        is_valid, file_path, error = self._validate_path(path)
        if not is_valid:
            response.set_error(error)
            return response

        try:
            # Read original content
            original_content = file_path.read_text(encoding='utf-8')
            changes = []

            # Apply formatting steps
            formatted_content = original_content

            # Step 1: Remove unused imports and variables with autoflake
            formatted_content, autoflake_changes = self._apply_autoflake(formatted_content)
            if autoflake_changes:
                changes.extend(autoflake_changes)
                response.add_trace(f"Autoflake: {', '.join(autoflake_changes)}")

            # Step 2: Sort imports with isort
            formatted_content, isort_changes = self._apply_isort(formatted_content)
            if isort_changes:
                changes.append("Sorted imports")
                response.add_trace("isort: Sorted imports")

            # Step 3: Format with black
            formatted_content, black_changes = self._apply_black(formatted_content)
            if black_changes:
                changes.append("Applied black formatting")
                response.add_trace("black: Applied formatting")

            # Check if any changes were made
            was_formatted = formatted_content != original_content

            if not check_only and was_formatted:
                # Write formatted content back
                file_path.write_text(formatted_content, encoding='utf-8')
                response.add_trace("Formatted content written to file")

            response.data = {
                'formatted': was_formatted,
                'changes': changes,
                'message': f"{'Would format' if check_only else 'Formatted'}: {len(changes)} changes" if was_formatted else "No formatting needed"
            }

            return response

        except Exception as e:
            response.set_error(f"Error formatting script: {str(e)}")
            return response

    def _apply_autoflake(self, content: str) -> tuple[str, List[str]]:
        """
        Remove unused imports and variables using autoflake.

        Args:
            content: Python source code

        Returns:
            Tuple of (formatted_content, list of changes)
        """
        try:
            import subprocess
            import tempfile

            changes = []

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name

            try:
                # Run autoflake
                result = subprocess.run(
                    ['python', '-m', 'autoflake', '--remove-all-unused-imports', '--remove-unused-variables', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    formatted = result.stdout
                    if formatted != content:
                        changes.append("Removed unused imports and variables")
                    return formatted, changes
                else:
                    return content, []

            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception:
            # If autoflake not available or fails, return original
            return content, []

    def _apply_isort(self, content: str) -> tuple[str, bool]:
        """
        Sort imports using isort.

        Args:
            content: Python source code

        Returns:
            Tuple of (formatted_content, was_changed)
        """
        try:
            import subprocess
            import tempfile

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name

            try:
                # Run isort
                result = subprocess.run(
                    ['python', '-m', 'isort', '--profile', 'black', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Read result
                formatted = Path(temp_path).read_text(encoding='utf-8')
                was_changed = formatted != content

                return formatted, was_changed

            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception:
            # If isort not available or fails, return original
            return content, False

    def _apply_black(self, content: str) -> tuple[str, bool]:
        """
        Format code using black.

        Args:
            content: Python source code

        Returns:
            Tuple of (formatted_content, was_changed)
        """
        try:
            import subprocess
            import tempfile

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name

            try:
                # Run black
                result = subprocess.run(
                    ['python', '-m', 'black', '--quiet', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Read result
                formatted = Path(temp_path).read_text(encoding='utf-8')
                was_changed = formatted != content

                return formatted, was_changed

            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception:
            # If black not available or fails, return original
            return content, False

    # ===== Structure Scanning =====

    @read_only
    @cached(ttl=300)  # Cache for 5 minutes
    def scan_structure(self, base_dir: str, include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> MCPResponse:
        """
        Scan directory structure and create dependency map.

        Args:
            base_dir: Base directory to scan
            include_patterns: Optional list of glob patterns to include (e.g., ['*.py'])
            exclude_patterns: Optional list of patterns to exclude (e.g., ['__pycache__', '*.pyc'])

        Returns:
            MCPResponse with data containing:
            - structure: Hierarchical directory tree
            - dependency_map: File dependency information
            - statistics: Analysis statistics
        """
        response = self._create_response()
        response.add_trace(f"Scanning structure: {base_dir}")

        try:
            base_path = Path(base_dir)

            if not base_path.exists():
                response.set_error(f"Directory not found: {base_dir}")
                return response

            if not base_path.is_dir():
                response.set_error(f"Not a directory: {base_dir}")
                return response

            # Default patterns
            if include_patterns is None:
                include_patterns = ['*.py']
            if exclude_patterns is None:
                exclude_patterns = ['__pycache__', '*.pyc', '*.pyo', '.git', '.venv', 'venv']

            response.add_trace(f"Include patterns: {include_patterns}")
            response.add_trace(f"Exclude patterns: {exclude_patterns}")

            # Scan directory structure
            structure = self._build_directory_tree(base_path, include_patterns, exclude_patterns)
            response.add_trace("Built directory tree")

            # Analyze Python files for dependencies
            python_files = self._find_python_files(base_path, include_patterns, exclude_patterns)
            response.add_trace(f"Found {len(python_files)} Python files")

            dependency_map = self._build_dependency_map(python_files, base_path)
            response.add_trace("Built dependency map")

            # Calculate statistics
            statistics = self._calculate_statistics(structure, dependency_map)
            response.add_trace(f"Statistics: {statistics['total_files']} files, {statistics['total_lines']} lines")

            response.data = {
                'structure': structure,
                'dependency_map': dependency_map,
                'statistics': statistics
            }

            return response

        except Exception as e:
            response.set_error(f"Error scanning structure: {str(e)}")
            return response

    def _build_directory_tree(self, base_path: Path, include_patterns: List[str],
                             exclude_patterns: List[str]) -> Dict[str, Any]:
        """
        Build hierarchical directory tree structure.

        Args:
            base_path: Base directory path
            include_patterns: Patterns to include
            exclude_patterns: Patterns to exclude

        Returns:
            Dictionary representing directory tree
        """
        tree = {
            'name': base_path.name,
            'path': str(base_path),
            'type': 'directory',
            'children': []
        }

        try:
            for item in sorted(base_path.iterdir()):
                # Check if excluded
                if self._should_exclude(item, exclude_patterns):
                    continue

                if item.is_dir():
                    # Recursively build subdirectory tree
                    subtree = self._build_directory_tree(item, include_patterns, exclude_patterns)
                    tree['children'].append(subtree)
                elif item.is_file():
                    # Check if file matches include patterns
                    if self._should_include(item, include_patterns):
                        tree['children'].append({
                            'name': item.name,
                            'path': str(item),
                            'type': 'file',
                            'size': item.stat().st_size
                        })

        except PermissionError:
            pass

        return tree

    def _should_exclude(self, path: Path, exclude_patterns: List[str]) -> bool:
        """Check if path should be excluded."""
        for pattern in exclude_patterns:
            if pattern in str(path):
                return True
            if path.match(pattern):
                return True
        return False

    def _should_include(self, path: Path, include_patterns: List[str]) -> bool:
        """Check if path should be included."""
        for pattern in include_patterns:
            if path.match(pattern):
                return True
        return False

    def _find_python_files(self, base_path: Path, include_patterns: List[str],
                          exclude_patterns: List[str]) -> List[Path]:
        """Find all Python files in directory."""
        python_files = []

        for pattern in include_patterns:
            for file_path in base_path.rglob(pattern):
                if file_path.is_file() and not self._should_exclude(file_path, exclude_patterns):
                    python_files.append(file_path)

        return python_files

    def _build_dependency_map(self, python_files: List[Path], base_path: Path) -> Dict[str, Any]:
        """
        Build dependency map for Python files.

        Args:
            python_files: List of Python file paths
            base_path: Base directory path

        Returns:
            Dictionary mapping file paths to their dependencies
        """
        dependency_map = {}

        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)

                # Extract imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                'type': 'import',
                                'module': alias.name,
                                'alias': alias.asname
                            })
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append({
                                'type': 'from_import',
                                'module': module,
                                'name': alias.name,
                                'alias': alias.asname
                            })

                # Get file info
                relative_path = file_path.relative_to(base_path)

                dependency_map[str(relative_path)] = {
                    'path': str(file_path),
                    'relative_path': str(relative_path),
                    'imports': imports,
                    'num_imports': len(imports),
                    'lines': len(content.splitlines())
                }

            except Exception as e:
                dependency_map[str(file_path.relative_to(base_path))] = {
                    'path': str(file_path),
                    'error': str(e)
                }

        return dependency_map

    def _calculate_statistics(self, structure: Dict[str, Any],
                             dependency_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics from structure and dependency map.

        Args:
            structure: Directory tree structure
            dependency_map: File dependency map

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_files': len(dependency_map),
            'total_directories': self._count_directories(structure),
            'total_lines': sum(info.get('lines', 0) for info in dependency_map.values() if 'lines' in info),
            'total_imports': sum(info.get('num_imports', 0) for info in dependency_map.values() if 'num_imports' in info),
            'files_with_errors': sum(1 for info in dependency_map.values() if 'error' in info)
        }

        # Most imported modules
        module_counts = {}
        for info in dependency_map.values():
            if 'imports' in info:
                for imp in info['imports']:
                    module = imp.get('module', '')
                    if module:
                        module_counts[module] = module_counts.get(module, 0) + 1

        # Top 10 most imported modules
        stats['top_imports'] = sorted(
            [{'module': k, 'count': v} for k, v in module_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        return stats

    def _count_directories(self, tree: Dict[str, Any]) -> int:
        """Recursively count directories in tree."""
        count = 1 if tree.get('type') == 'directory' else 0
        for child in tree.get('children', []):
            count += self._count_directories(child)
        return count
