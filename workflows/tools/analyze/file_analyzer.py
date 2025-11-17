"""
File Analyzer Tool

Analyzes Python files when user provides @path syntax.
Provides code structure analysis, function signatures, and documentation.
Enhanced with LLM-powered understanding of script purpose and usage.
"""

from pathlib import Path
import ast
import importlib.util
from typing import Dict, Any, List
import re
import requests
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.session_history import get_session_history
from agents.pulsus.console.interrupt_handler import get_interrupt_handler
from agents.pulsus.workflows.tools.analyze.doc_scanner import (
    has_documentation, load_existing_documentation, scan_related_documentation
)
from colorama import Fore, Style

__domain__ = "analysis"
__action__ = "analyze_file"


def extract_file_path(text: str) -> str:
    """
    Extract file path from user input containing @path syntax.

    Args:
        text: User input text (e.g., "@C:\\path\\to\\file.py" or "analyze @/path/to/file.py")

    Returns:
        Extracted file path or empty string if not found
    """
    # Pattern to match @path (handles both Windows and Unix paths)
    pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return ""


def analyze_ast(file_path: Path) -> Dict[str, Any]:
    """
    Parse Python file using AST and extract structure information.

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary containing:
        - functions: List of function definitions
        - classes: List of class definitions
        - imports: List of imports
        - module_docstring: Module-level docstring
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


def load_module_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Load module and extract metadata attributes like __domain__, __action__.

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with metadata
    """
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


def generate_llm_understanding(file_path: Path, content: str, ast_analysis: Dict) -> str:
    """
    Use LLM to generate an intelligent understanding of the script with streaming.
    Uses existing documentation and related docs for better context.

    Args:
        file_path: Path to the script
        content: Full source code content
        ast_analysis: AST analysis results

    Returns:
        LLM-generated understanding or empty string if LLM unavailable
    """
    settings = load_settings()

    # Check for existing documentation
    existing_doc = load_existing_documentation(file_path)
    related_docs = scan_related_documentation(file_path)

    # Build a concise summary of the script for the LLM
    num_functions = len(ast_analysis.get("functions", []))
    num_classes = len(ast_analysis.get("classes", []))
    imports = ", ".join(ast_analysis.get("imports", [])[:10])

    # Truncate content if too long (keep first 3000 chars)
    code_sample = content[:3000] if len(content) > 3000 else content

    # Build context from existing documentation
    doc_context = ""
    if existing_doc:
        doc_context += f"\n\nExisting Documentation (use this as primary reference):\n{existing_doc[:2000]}"

    if related_docs:
        doc_context += "\n\nRelated Documentation:\n"
        for doc in related_docs[:2]:  # Limit to 2 related docs
            doc_context += f"\n--- {doc['name']} ---\n{doc['content'][:1000]}\n"

    prompt = f"""Analyze this Python script and provide a concise understanding.
{doc_context if doc_context else ""}

Analyze this Python script and provide a concise understanding:

File: {file_path.name}
Stats: {num_classes} classes, {num_functions} functions
Key imports: {imports}

Code:
```python
{code_sample}
```

Provide a brief analysis (3-4 sentences) covering:
1. What is the main purpose of this script?
2. What are the key capabilities/features?
3. How would someone typically use it?
4. Any notable dependencies or requirements?

Keep it concise and practical."""

    try:
        # Show thinking message
        ui.llm_thinking()

        # Check for interrupt before starting
        interrupt_handler = get_interrupt_handler()
        if interrupt_handler.is_interrupted():
            raise InterruptedError("LLM analysis interrupted by user (ESC)")

        # Stream response
        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": True,  # Enable streaming
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300,
                }
            },
            timeout=settings.model.timeout,
            stream=True
        )

        if response.status_code == 200:
            print()  # New line after thinking message
            ui.llm_understanding_header()

            full_text = ""
            for line in response.iter_lines():
                # Check for interrupt during streaming
                if interrupt_handler.is_interrupted():
                    raise InterruptedError("LLM analysis interrupted by user (ESC)")

                if line:
                    import json
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            text = chunk["response"]
                            full_text += text
                            # Stream output
                            print(text, end='', flush=True)
                    except:
                        pass

            print()  # Final newline
            return full_text.strip()
        else:
            print()  # Clear thinking line
            return ""

    except InterruptedError:
        print()  # Clear thinking line
        raise  # Re-raise to be caught by handle()
    except Exception as e:
        print()  # Clear thinking line
        return f"[LLM analysis unavailable: {str(e)[:50]}]"


def format_analysis(file_path: Path, ast_analysis: Dict, metadata: Dict, llm_understanding: str = "") -> str:
    """
    Format analysis results into readable output.

    Args:
        file_path: Path to analyzed file
        ast_analysis: AST analysis results
        metadata: Module metadata

    Returns:
        Formatted analysis string
    """
    output = "\n" + "="*70 + "\n"
    output += f"  FILE ANALYSIS: {file_path.name}\n"
    output += "="*70 + "\n"

    # Make the path clickable
    clickable_path = ui.make_clickable_link(str(file_path), str(file_path))
    output += f"Path: {clickable_path}\n"

    # Metadata section
    if metadata.get("domain") or metadata.get("action"):
        output += "\n[METADATA]\n"
        output += "-" * 70 + "\n"
        if metadata.get("domain"):
            output += f"  Domain: {metadata['domain']}\n"
        if metadata.get("action"):
            output += f"  Action: {metadata['action']}\n"

    # Module docstring
    if ast_analysis.get("module_docstring"):
        output += "\n[MODULE DESCRIPTION]\n"
        output += "-" * 70 + "\n"
        output += f"{ast_analysis['module_docstring']}\n"

    # Imports
    if ast_analysis.get("imports"):
        output += "\n[IMPORTS]\n"
        output += "-" * 70 + "\n"
        for imp in ast_analysis["imports"][:10]:  # Limit to first 10
            output += f"  • {imp}\n"
        if len(ast_analysis["imports"]) > 10:
            output += f"  ... and {len(ast_analysis['imports']) - 10} more\n"

    # Classes
    if ast_analysis.get("classes"):
        output += "\n[CLASSES]\n"
        output += "-" * 70 + "\n"
        for cls in ast_analysis["classes"]:
            # Make class line clickable
            clickable_line = ui.make_clickable_path(str(file_path), cls['line'])
            output += f"  • {cls['name']} ({clickable_line})\n"
            if cls['methods']:
                output += f"    Methods: {', '.join(cls['methods'])}\n"
            if cls['docstring']:
                doc_preview = cls['docstring'].split('\n')[0][:60]
                output += f"    {doc_preview}\n"

    # Functions
    if ast_analysis.get("functions"):
        output += "\n[FUNCTIONS]\n"
        output += "-" * 70 + "\n"
        for func in ast_analysis["functions"]:
            args_str = ', '.join(func['args']) if func['args'] else ''
            # Make function line clickable
            clickable_line = ui.make_clickable_path(str(file_path), func['line'])
            output += f"  • {func['name']}({args_str}) - {clickable_line}\n"
            if func['docstring']:
                doc_preview = func['docstring'].split('\n')[0][:60]
                output += f"    {doc_preview}\n"

    output += "\n" + "="*70 + "\n"

    # Statistics
    num_functions = len(ast_analysis.get("functions", []))
    num_classes = len(ast_analysis.get("classes", []))
    output += f"[SUMMARY] {num_classes} classes, {num_functions} functions\n"
    output += "="*70 + "\n"

    # LLM Understanding section (if available)
    if llm_understanding:
        output += "\n[PULSUS UNDERSTANDING]\n"
        output += "-" * 70 + "\n"
        output += f"{llm_understanding}\n"

    return output


def handle(text: str = None, input_text: str = None, repo_context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for file analysis tool.

    Args:
        text: User input containing @path syntax (deprecated, use input_text)
        input_text: User input containing @path syntax
        repo_context: Optional repository analysis context from .pulsus/
        **kwargs: Additional arguments

    Returns:
        Dictionary with analysis results
    """
    # Support both text and input_text parameters for backward compatibility
    if input_text is None:
        input_text = text

    if input_text is None:
        error_msg = "[Error] No input provided"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    # Extract file path from @path syntax
    file_path_str = extract_file_path(input_text)

    if not file_path_str:
        error_msg = "[Error] No file path found. Use '@path' syntax (e.g., @C:\\path\\to\\file.py)"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    file_path = Path(file_path_str)

    if not file_path.exists():
        error_msg = f"[Error] File not found: {file_path}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    if not file_path.suffix == '.py':
        error_msg = f"[Error] Not a Python file: {file_path}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    # Start listening for ESC key
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()
    ui.info("Press ESC to interrupt...")

    try:
        # Show header
        ui.analysis_header(file_path.name)

        # Display repository context if available
        if repo_context:
            print(f"{Fore.CYAN}[*] Repository context loaded{Style.RESET_ALL}")
            stats = repo_context.get("statistics", {})
            if stats:
                print(f"    - Compliance: {stats.get('compliance_rate', 'N/A')}")
                print(f"    - Total files: {stats.get('total_files', 'N/A')}")
                print(f"    - Avg issues/file: {stats.get('avg_issues_per_file', 'N/A')}")
            print()

        # Check if documentation exists
        if has_documentation(file_path):
            md_path = file_path.with_suffix('.md')
            clickable_md = ui.make_clickable_link(str(md_path), md_path.name)
            print(f"{Fore.GREEN}[*] Found existing documentation: {clickable_md}{Style.RESET_ALL}\n")

        # Read file content for LLM analysis
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            content = ""

        # Perform analysis
        ast_analysis = analyze_ast(file_path)
        metadata = load_module_metadata(file_path)

        # Format and display static analysis results
        output = format_analysis(file_path, ast_analysis, metadata, "")  # Don't include LLM in output (already streamed)
        print(output)

        # Generate LLM understanding (streams automatically)
        llm_understanding = generate_llm_understanding(file_path, content, ast_analysis)

        # Save to session history
        history = get_session_history()
        history.set_current_script(file_path, ast_analysis, metadata, llm_understanding, content)

        # Show available actions
        clickable_current = ui.make_clickable_link(str(file_path), file_path.name)
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[PULSUS]{Style.RESET_ALL} Available actions for {clickable_current}:")
        print(f"  - Ask follow-up questions about this script")
        print(f"  - Type {Fore.GREEN}'comment functions'{Style.RESET_ALL} to generate docstrings for all functions")
        print(f"  - Type {Fore.GREEN}'analyze dependencies'{Style.RESET_ALL} to document script dependencies")
        print(f"  - Type {Fore.GREEN}'generate docs'{Style.RESET_ALL} to create documentation (.md file)")
        print(f"  - Use {Fore.CYAN}@path{Style.RESET_ALL} to analyze a different script")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        return {
            "status": "success",
            "file": str(file_path),
            "analysis": ast_analysis,
            "metadata": metadata,
            "llm_understanding": llm_understanding,
            "message": f"Analysis complete for {file_path.name}"
        }
    except InterruptedError:
        ui.warn("\nFile analysis interrupted by user (ESC)")
        return {
            "status": "interrupted",
            "message": "Analysis interrupted"
        }
    finally:
        # Stop listening for ESC key
        interrupt_handler.stop_listening()


if __name__ == "__main__":
    # Test the analyzer
    import sys
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
    else:
        test_text = "@c:\\Users\\jean-noel.diltoer\\software\\Atlantis\\testudo\\agents\\pulsus\\routing\\tool_discovery.py"

    print(f"Testing File Analyzer with: {test_text}")
    result = handle(test_text)
    print(f"\nResult: {result['message']}")
