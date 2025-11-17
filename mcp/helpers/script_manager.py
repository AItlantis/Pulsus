"""
ScriptManager - Class-Based MCP Helper for Script Operations

Provides MCP-compliant methods for:
- Reading and analyzing Python scripts
- Generating documentation
- Adding comments/docstrings
- Formatting scripts
- Scanning directory structures

This refactors the procedural script_ops.py into a class-based architecture
using the MCP Core Framework (Phase 1).
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import ast
import requests

# MCP Core Framework imports
from agents.mcp.core import (
    MCPBase,
    MCPResponse,
    read_only,
    write_safe,
    cached,
    get_mcp_logger
)

# Pulsus dependencies
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui


class ScriptManager(MCPBase):
    """
    Class-based MCP helper for Python script operations.

    Provides safe, structured methods for:
    - Script reading and AST analysis
    - Documentation generation
    - Function commenting
    - Code formatting
    - Structure scanning

    All methods return MCPResponse objects with standardized structure.
    """

    def __init__(self, logger=None, context=None):
        """
        Initialize ScriptManager.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        if logger is None:
            logger = get_mcp_logger()

        if context is None:
            context = {'caller': 'ScriptManager'}

        super().__init__(logger=logger, context=context)

        # Load settings
        self.settings = load_settings()

    # ===== Path Validation =====

    def _validate_path(self, path: str) -> MCPResponse:
        """
        Validate a file path for safety and existence.

        Args:
            path: File path to validate

        Returns:
            MCPResponse with path validation results
        """
        response = self._create_response()
        response.add_trace(f"Validating path: {path}")

        try:
            file_path = Path(path)

            # Check existence
            if not file_path.exists():
                response.set_error(f"File not found: {path}")
                return response

            # Check if it's a file
            if not file_path.is_file():
                response.set_error(f"Not a file: {path}")
                return response

            # Check if it's a Python file
            if file_path.suffix != '.py':
                response.set_error(f"Not a Python file: {path}")
                return response

            response.data = {'path': file_path, 'valid': True}
            response.add_trace("Path validation successful")
            return response

        except Exception as e:
            response.set_error(f"Path validation error: {str(e)}")
            return response

    # ===== Script Reading & Analysis =====

    @read_only
    @cached(ttl=60)
    def read_script(self, path: str) -> MCPResponse:
        """
        Read and analyze a Python script.

        Safe read-only operation that:
        - Reads file content
        - Performs AST analysis
        - Extracts metadata
        - Returns structured information

        Results are cached for 60 seconds for performance.

        Args:
            path: Path to the Python script

        Returns:
            MCPResponse with script content, AST analysis, and metadata
        """
        response = self._create_response()
        response.add_trace(f"Reading script: {path}")

        # Validate path
        validation = self._validate_path(path)
        if not validation.success:
            return validation

        file_path = validation.data['path']

        try:
            # Read content
            content = file_path.read_text(encoding='utf-8')
            response.add_trace(f"Read {len(content)} bytes")

            # Perform AST analysis
            ast_analysis = self._analyze_ast(file_path)
            response.add_trace(f"AST analysis: {len(ast_analysis.get('functions', []))} functions, {len(ast_analysis.get('classes', []))} classes")

            # Load metadata
            metadata = self._load_module_metadata(file_path)

            response.data = {
                'content': content,
                'ast_analysis': ast_analysis,
                'metadata': metadata,
                'file_path': str(file_path)
            }
            response.add_trace("Script reading completed successfully")

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

        This is a write operation that creates a .md file alongside the script.
        Requires user confirmation in interactive mode.

        Args:
            path: Path to the Python script
            content: Optional pre-generated Markdown content. If None, will auto-generate.

        Returns:
            MCPResponse with documentation path and status
        """
        response = self._create_response()
        response.add_trace(f"Generating documentation for: {path}")

        # Validate path
        validation = self._validate_path(path)
        if not validation.success:
            return validation

        file_path = validation.data['path']

        try:
            # Read script if content not provided
            if content is None:
                script_result = self.read_script(str(file_path))
                if not script_result.success:
                    return script_result

                # Generate documentation using LLM
                content = self._generate_documentation_content(
                    file_path,
                    script_result.data['content'],
                    script_result.data['ast_analysis'],
                    script_result.data['metadata']
                )
                response.add_trace("Documentation content generated")

            # Create .md file path
            doc_path = file_path.with_suffix('.md')

            # Save documentation
            doc_path.write_text(content, encoding='utf-8')
            response.add_trace(f"Documentation saved to: {doc_path.name}")

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

    @write_safe
    def add_comments(self, path: str, strategy: str = "docstring", show_progress: bool = True) -> MCPResponse:
        """
        Generate and add comments/docstrings to functions in a Python script.

        This is a write operation that modifies the file.
        Requires user confirmation in interactive mode.

        Args:
            path: Path to the Python script
            strategy: Comment strategy - 'docstring' (default) or 'inline'
            show_progress: Show progress messages during generation

        Returns:
            MCPResponse with comments generated and statistics
        """
        response = self._create_response()
        response.add_trace(f"Adding comments to: {path}")

        # Validate path
        validation = self._validate_path(path)
        if not validation.success:
            return validation

        file_path = validation.data['path']

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

                response.add_trace(f"Generated comment for {func['name']}()")

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

    # ===== Structure Scanning =====

    @read_only
    @cached(ttl=300)
    def scan_structure(self, base_dir: str, include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> MCPResponse:
        """
        Scan directory structure and create dependency map.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            base_dir: Base directory to scan
            include_patterns: Optional list of glob patterns to include (e.g., ['*.py'])
            exclude_patterns: Optional list of patterns to exclude (e.g., ['__pycache__', '*.pyc'])

        Returns:
            MCPResponse with structure, dependency map, and statistics
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

            # Analyze Python files for dependencies
            python_files = self._find_python_files(base_path, include_patterns, exclude_patterns)
            dependency_map = self._build_dependency_map(python_files, base_path)

            # Calculate statistics
            statistics = self._calculate_statistics(structure, dependency_map)

            response.add_trace(f"Found {statistics['total_files']} files in {statistics['total_directories']} directories")

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
        """Build hierarchical directory tree structure."""
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
        """Build dependency map for Python files."""
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
        """Calculate statistics from structure and dependency map."""
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
