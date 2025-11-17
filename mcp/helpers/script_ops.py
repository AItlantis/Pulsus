"""
Script Operations MCP Helper

Core MCP functions for reading, writing, and commenting Python scripts.
Migrated from agents/pulsus/workflows/tools/analyze/
"""

from pathlib import Path
import ast
import re
import requests
from typing import Dict, Any, List, Optional
from config.settings import load_settings
from ui import display_manager as ui
from console.interrupt_handler import get_interrupt_handler
from colorama import Fore, Style

# Import MCP action logger
try:
    from mcp.helpers.action_logger import log_mcp_action
except ImportError:
    # Fallback if logger not available
    def log_mcp_action(*args, **kwargs):
        pass


class ScriptOps:
    """
    Script operations helper for MCP.

    Provides core functionality for:
    - Reading and analyzing Python scripts
    - Generating documentation
    - Adding comments/docstrings to functions
    """

    def __init__(self):
        """Initialize the script operations helper."""
        self.settings = load_settings()

    # ===== Path Validation =====

    def validate_path(self, path: str) -> Dict[str, Any]:
        """
        Validate a file path for safety and existence.

        Args:
            path: File path to validate

        Returns:
            Dict with 'valid' (bool), 'path' (Path), 'error' (str)
        """
        try:
            file_path = Path(path)

            # Check existence
            if not file_path.exists():
                return {
                    'valid': False,
                    'path': None,
                    'error': f"File not found: {path}"
                }

            # Check if it's a file
            if not file_path.is_file():
                return {
                    'valid': False,
                    'path': None,
                    'error': f"Not a file: {path}"
                }

            # Check if it's a Python file
            if file_path.suffix != '.py':
                return {
                    'valid': False,
                    'path': None,
                    'error': f"Not a Python file: {path}"
                }

            return {
                'valid': True,
                'path': file_path,
                'error': None
            }

        except Exception as e:
            return {
                'valid': False,
                'path': None,
                'error': f"Path validation error: {str(e)}"
            }

    # ===== Script Reading & Analysis =====

    def read_script(self, path: str) -> Dict[str, Any]:
        """
        Read and analyze a Python script.

        Args:
            path: Path to the Python script

        Returns:
            Dict with 'success' (bool), 'content' (str), 'ast_analysis' (dict),
            'metadata' (dict), 'error' (str)
        """
        # Validate path
        validation = self.validate_path(path)
        if not validation['valid']:
            result = {
                'success': False,
                'content': None,
                'ast_analysis': None,
                'metadata': None,
                'error': validation['error']
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_read_script",
                operation="read",
                target_path=path,
                parameters={"path": path},
                result=result,
                success=False,
                error=validation['error']
            )

            return result

        file_path = validation['path']

        try:
            # Read content
            content = file_path.read_text(encoding='utf-8')

            # Perform AST analysis
            ast_analysis = self._analyze_ast(file_path)

            # Load metadata
            metadata = self._load_module_metadata(file_path)

            result = {
                'success': True,
                'content': content,
                'ast_analysis': ast_analysis,
                'metadata': metadata,
                'error': None,
                'file_path': str(file_path)
            }

            # Log successful action (without full content to save space)
            log_mcp_action(
                tool_name="mcp_read_script",
                operation="read",
                target_path=str(file_path),
                parameters={"path": path},
                result={
                    'success': True,
                    'file_path': str(file_path),
                    'num_functions': len(ast_analysis.get('functions', [])),
                    'num_classes': len(ast_analysis.get('classes', [])),
                    'content_length': len(content)
                },
                success=True
            )

            return result

        except Exception as e:
            result = {
                'success': False,
                'content': None,
                'ast_analysis': None,
                'metadata': None,
                'error': f"Error reading script: {str(e)}"
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_read_script",
                operation="read",
                target_path=str(file_path),
                parameters={"path": path},
                result=result,
                success=False,
                error=str(e)
            )

            return result

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

    def write_md(self, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate or write Markdown documentation for a Python script.

        Args:
            path: Path to the Python script
            content: Optional pre-generated Markdown content. If None, will auto-generate.

        Returns:
            Dict with 'success' (bool), 'doc_path' (str), 'error' (str)
        """
        # Validate path
        validation = self.validate_path(path)
        if not validation['valid']:
            result = {
                'success': False,
                'doc_path': None,
                'error': validation['error']
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_write_md",
                operation="write_md",
                target_path=path,
                parameters={"path": path, "content_provided": content is not None},
                result=result,
                success=False,
                error=validation['error']
            )

            return result

        file_path = validation['path']

        try:
            # Read script if content not provided
            if content is None:
                script_data = self.read_script(str(file_path))
                if not script_data['success']:
                    result = {
                        'success': False,
                        'doc_path': None,
                        'error': script_data['error']
                    }

                    # Log failed action
                    log_mcp_action(
                        tool_name="mcp_write_md",
                        operation="write_md",
                        target_path=str(file_path),
                        parameters={"path": path, "content_provided": False},
                        result=result,
                        success=False,
                        error=script_data['error']
                    )

                    return result

                # Generate documentation using LLM
                content = self._generate_documentation_content(
                    file_path,
                    script_data['content'],
                    script_data['ast_analysis'],
                    script_data['metadata']
                )

            # Create .md file path
            doc_path = file_path.with_suffix('.md')

            # Save documentation
            doc_path.write_text(content, encoding='utf-8')

            result = {
                'success': True,
                'doc_path': str(doc_path),
                'error': None,
                'message': f"Documentation created: {doc_path.name}"
            }

            # Log successful action
            log_mcp_action(
                tool_name="mcp_write_md",
                operation="write_md",
                target_path=str(doc_path),
                parameters={"path": path, "content_provided": content is not None},
                result=result,
                success=True
            )

            return result

        except Exception as e:
            result = {
                'success': False,
                'doc_path': None,
                'error': f"Error writing documentation: {str(e)}"
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_write_md",
                operation="write_md",
                target_path=str(file_path),
                parameters={"path": path, "content_provided": content is not None},
                result=result,
                success=False,
                error=str(e)
            )

            return result

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

    def add_comments(self, path: str, strategy: str = "docstring", show_progress: bool = True) -> Dict[str, Any]:
        """
        Generate and add comments/docstrings to functions in a Python script.

        Args:
            path: Path to the Python script
            strategy: Comment strategy - 'docstring' (default) or 'inline'

        Returns:
            Dict with 'success' (bool), 'functions_commented' (int),
            'comments' (list), 'error' (str)
        """
        # Validate path
        validation = self.validate_path(path)
        if not validation['valid']:
            result = {
                'success': False,
                'functions_commented': 0,
                'comments': [],
                'error': validation['error']
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_add_comments",
                operation="add_comments",
                target_path=path,
                parameters={"path": path, "strategy": strategy},
                result=result,
                success=False,
                error=validation['error']
            )

            return result

        file_path = validation['path']

        try:
            # Analyze functions
            functions = self._analyze_functions(file_path)

            if not functions:
                result = {
                    'success': True,
                    'functions_commented': 0,
                    'comments': [],
                    'error': None,
                    'message': 'No functions found to comment'
                }

                # Log action (no functions found)
                log_mcp_action(
                    tool_name="mcp_add_comments",
                    operation="add_comments",
                    target_path=str(file_path),
                    parameters={"path": path, "strategy": strategy},
                    result=result,
                    success=True
                )

                return result

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

            result = {
                'success': True,
                'functions_commented': len(comments),
                'comments': comments,
                'error': None,
                'message': f"Generated comments for {len(comments)} functions"
            }

            # Log successful action
            log_mcp_action(
                tool_name="mcp_add_comments",
                operation="add_comments",
                target_path=str(file_path),
                parameters={"path": path, "strategy": strategy},
                result={
                    'success': True,
                    'functions_commented': len(comments),
                    'function_names': [c['function'] for c in comments]
                },
                success=True
            )

            return result

        except Exception as e:
            result = {
                'success': False,
                'functions_commented': 0,
                'comments': [],
                'error': f"Error adding comments: {str(e)}"
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_add_comments",
                operation="add_comments",
                target_path=str(file_path),
                parameters={"path": path, "strategy": strategy},
                result=result,
                success=False,
                error=str(e)
            )

            return result

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

    def format_script(self, path: str, check_only: bool = False) -> Dict[str, Any]:
        """
        Auto-format and normalize a Python script.

        Uses black for formatting, isort for import sorting, and autoflake for cleanup.

        Args:
            path: Path to the Python script
            check_only: If True, only check formatting without making changes

        Returns:
            Dict with 'success' (bool), 'formatted' (bool), 'changes' (list), 'error' (str)
        """
        # Validate path
        validation = self.validate_path(path)
        if not validation['valid']:
            result = {
                'success': False,
                'formatted': False,
                'changes': [],
                'error': validation['error']
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_format_script",
                operation="format",
                target_path=path,
                parameters={"path": path, "check_only": check_only},
                result=result,
                success=False,
                error=validation['error']
            )

            return result

        file_path = validation['path']

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

            # Step 2: Sort imports with isort
            formatted_content, isort_changes = self._apply_isort(formatted_content)
            if isort_changes:
                changes.append("Sorted imports")

            # Step 3: Format with black
            formatted_content, black_changes = self._apply_black(formatted_content)
            if black_changes:
                changes.append("Applied black formatting")

            # Check if any changes were made
            was_formatted = formatted_content != original_content

            if not check_only and was_formatted:
                # Write formatted content back
                file_path.write_text(formatted_content, encoding='utf-8')

            result = {
                'success': True,
                'formatted': was_formatted,
                'changes': changes,
                'error': None,
                'message': f"{'Would format' if check_only else 'Formatted'}: {len(changes)} changes" if was_formatted else "No formatting needed"
            }

            # Log action
            log_mcp_action(
                tool_name="mcp_format_script",
                operation="format",
                target_path=str(file_path),
                parameters={"path": path, "check_only": check_only},
                result=result,
                success=True
            )

            return result

        except Exception as e:
            result = {
                'success': False,
                'formatted': False,
                'changes': [],
                'error': f"Error formatting script: {str(e)}"
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_format_script",
                operation="format",
                target_path=str(file_path),
                parameters={"path": path, "check_only": check_only},
                result=result,
                success=False,
                error=str(e)
            )

            return result

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

    def scan_structure(self, base_dir: str, include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan directory structure and create dependency map.

        Args:
            base_dir: Base directory to scan
            include_patterns: Optional list of glob patterns to include (e.g., ['*.py'])
            exclude_patterns: Optional list of patterns to exclude (e.g., ['__pycache__', '*.pyc'])

        Returns:
            Dict with 'success' (bool), 'structure' (dict), 'statistics' (dict), 'error' (str)
        """
        try:
            base_path = Path(base_dir)

            if not base_path.exists():
                result = {
                    'success': False,
                    'structure': {},
                    'statistics': {},
                    'error': f"Directory not found: {base_dir}"
                }

                # Log failed action
                log_mcp_action(
                    tool_name="mcp_scan_structure",
                    operation="scan",
                    target_path=base_dir,
                    parameters={
                        "base_dir": base_dir,
                        "include_patterns": include_patterns,
                        "exclude_patterns": exclude_patterns
                    },
                    result=result,
                    success=False,
                    error=result['error']
                )

                return result

            if not base_path.is_dir():
                result = {
                    'success': False,
                    'structure': {},
                    'statistics': {},
                    'error': f"Not a directory: {base_dir}"
                }

                # Log failed action
                log_mcp_action(
                    tool_name="mcp_scan_structure",
                    operation="scan",
                    target_path=base_dir,
                    parameters={
                        "base_dir": base_dir,
                        "include_patterns": include_patterns,
                        "exclude_patterns": exclude_patterns
                    },
                    result=result,
                    success=False,
                    error=result['error']
                )

                return result

            # Default patterns
            if include_patterns is None:
                include_patterns = ['*.py']
            if exclude_patterns is None:
                exclude_patterns = ['__pycache__', '*.pyc', '*.pyo', '.git', '.venv', 'venv']

            # Scan directory structure
            structure = self._build_directory_tree(base_path, include_patterns, exclude_patterns)

            # Analyze Python files for dependencies
            python_files = self._find_python_files(base_path, include_patterns, exclude_patterns)
            dependency_map = self._build_dependency_map(python_files, base_path)

            # Calculate statistics
            statistics = self._calculate_statistics(structure, dependency_map)

            result = {
                'success': True,
                'structure': structure,
                'dependency_map': dependency_map,
                'statistics': statistics,
                'error': None
            }

            # Log successful action
            log_mcp_action(
                tool_name="mcp_scan_structure",
                operation="scan",
                target_path=str(base_path),
                parameters={
                    "base_dir": base_dir,
                    "include_patterns": include_patterns,
                    "exclude_patterns": exclude_patterns
                },
                result={
                    'success': True,
                    'num_files': statistics.get('total_files', 0),
                    'num_directories': statistics.get('total_directories', 0),
                    'total_lines': statistics.get('total_lines', 0)
                },
                success=True
            )

            return result

        except Exception as e:
            result = {
                'success': False,
                'structure': {},
                'statistics': {},
                'error': f"Error scanning structure: {str(e)}"
            }

            # Log failed action
            log_mcp_action(
                tool_name="mcp_scan_structure",
                operation="scan",
                target_path=base_dir,
                parameters={
                    "base_dir": base_dir,
                    "include_patterns": include_patterns,
                    "exclude_patterns": exclude_patterns
                },
                result=result,
                success=False,
                error=str(e)
            )

            return result

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
