"""
Function Commenter Tool

Generates detailed comments for each function in Python files using LLM.
Supports recursive directory processing, streaming responses, and automatic
docstring insertion.

Keywords: comment, document, function, docstring, annotation, explain
"""

from pathlib import Path
import ast
import re
import json
from typing import Dict, Any, List, Optional
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.ui.streaming import stream_llm_response
from agents.pulsus.console.interrupt_handler import get_interrupt_handler
from agents.pulsus.console.session_history import get_session_history
from colorama import Fore, Style

__domain__ = "analysis"
__action__ = "comment_functions"

# Global workflow config loaded from JSON
_workflow_config = None


def load_workflow_config() -> Dict[str, Any]:
    """
    Load workflow configuration from JSON file.

    Returns:
        Dictionary containing workflow configuration including preprompt
    """
    global _workflow_config
    if _workflow_config is None:
        workflow_file = Path(__file__).parent.parent.parent / "function_commenting.json"
        with open(workflow_file, 'r', encoding='utf-8') as f:
            _workflow_config = json.load(f)
    return _workflow_config


def extract_path(text: str) -> str:
    """
    Extract file or directory path from user input containing @path syntax.

    Args:
        text (str): User input text (e.g., "@C:\\path\\to\\file.py" or "@/path/to/dir")

    Returns:
        str: Extracted path or empty string if not found
    """
    pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+)'
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return ""


def find_python_files(path: Path, recursive: bool = True, skip_patterns: List[str] = None) -> List[Path]:
    """
    Find all Python files in a directory.

    Args:
        path (Path): Directory or file path to search
        recursive (bool, optional): Search subdirectories recursively. Defaults to True.
        skip_patterns (List[str], optional): Directory/file patterns to skip. Defaults to None.

    Returns:
        List[Path]: List of Python file paths found
    """
    if skip_patterns is None:
        skip_patterns = ["__pycache__", ".git", ".venv", "venv", "env", ".tox"]

    if path.is_file():
        return [path] if path.suffix == '.py' else []

    python_files = []

    if recursive:
        for py_file in path.rglob("*.py"):
            # Skip files in excluded directories
            if any(pattern in str(py_file) for pattern in skip_patterns):
                continue
            python_files.append(py_file)
    else:
        for py_file in path.glob("*.py"):
            python_files.append(py_file)

    return sorted(python_files)


def extract_function_source(file_path: Path, func_node: ast.FunctionDef) -> str:
    """
    Extract the source code for a specific function from the file.

    Args:
        file_path (Path): Path to the Python file
        func_node (ast.FunctionDef): AST FunctionDef node

    Returns:
        str: Source code of the function as string
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Get function lines (from start to end)
        start_line = func_node.lineno - 1
        end_line = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start_line + 10

        func_lines = lines[start_line:end_line]
        return '\n'.join(func_lines)
    except Exception as e:
        return f"# Error extracting source: {str(e)}"


def analyze_functions(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse Python file and extract all function definitions.

    Args:
        file_path (Path): Path to Python file

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing function information
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
                source = extract_function_source(file_path, node)

                # Get existing docstring
                existing_docstring = ast.get_docstring(node) or ""

                func_info = {
                    "name": node.name,
                    "args": args_list,
                    "returns": returns,
                    "line": node.lineno,
                    "end_line": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "existing_docstring": existing_docstring,
                    "source": source,
                    "node": node  # Keep reference for insertion
                }
                functions.append(func_info)

        return functions

    except Exception as e:
        ui.error(f"Error parsing file: {e}")
        return []


def build_prompt_from_config(func_info: Dict[str, Any], file_context: str, config: Dict[str, Any]) -> str:
    """
    Build LLM prompt using configuration from workflow JSON.

    Args:
        func_info (Dict[str, Any]): Dictionary containing function information
        file_context (str): Brief context about the file/module
        config (Dict[str, Any]): Workflow configuration containing preprompt

    Returns:
        str: Formatted prompt for LLM
    """
    preprompt = config.get("preprompt", {})

    # System context
    system = preprompt.get("system", "You are a Python documentation expert.")

    # Instructions
    instructions = preprompt.get("instructions", [])
    instructions_text = "\n".join(f"- {inst}" for inst in instructions)

    # Format information
    format_info = preprompt.get("format", {})
    structure = format_info.get("structure", [])
    structure_text = "\n".join(f"{i+1}. {item}" for i, item in enumerate(structure))
    example = format_info.get("example", "")

    # Guidelines
    guidelines = preprompt.get("guidelines", [])
    guidelines_text = "\n".join(f"- {guide}" for guide in guidelines)

    # Build the full prompt
    prompt = f"""{system}

**Your Task:**
Generate a comprehensive Python docstring for the function below.

**Instructions:**
{instructions_text}

**File Context:** {file_context}

**Function to Document:**
```python
{func_info['source']}
```

**Docstring Structure:**
{structure_text}

**Format Example:**
{example}

**Guidelines:**
{guidelines_text}

**Existing Docstring (if any):**
{func_info['existing_docstring'] if func_info['existing_docstring'] else "(None - create new docstring)"}

**Important:** Output ONLY the docstring text content (without the triple quotes). Do not include code fences, explanatory text, or any other commentary. Start directly with the summary line."""

    return prompt


def generate_function_comment_streaming(
    func_info: Dict[str, Any],
    file_context: str,
    config: Dict[str, Any]
) -> str:
    """
    Use LLM to generate a detailed comment for a function with streaming output.

    Args:
        func_info (Dict[str, Any]): Dictionary containing function information
        file_context (str): Brief context about the file/module
        config (Dict[str, Any]): Workflow configuration

    Returns:
        str: Generated docstring comment

    Raises:
        InterruptedError: If user interrupts during generation
    """
    prompt = build_prompt_from_config(func_info, file_context, config)

    try:
        # Stream the response with visual feedback
        print(f"    {Fore.WHITE + Style.DIM}Docstring: {Style.RESET_ALL}", end='', flush=True)

        comment = stream_llm_response(
            prompt=prompt,
            prefix="",
            color=Fore.GREEN,
            temperature=0.3,
            num_predict=500
        )

        return comment

    except InterruptedError:
        raise
    except Exception as e:
        return f"[Error generating comment: {str(e)[:100]}]"


def format_docstring(comment: str, indent_level: int = 1) -> str:
    """
    Format comment as a proper Python docstring with correct indentation.

    Args:
        comment (str): The comment text
        indent_level (int, optional): Number of indentation levels. Defaults to 1.

    Returns:
        str: Formatted docstring with triple quotes and proper indentation
    """
    indent = "    " * indent_level
    lines = comment.split('\n')

    # Format as triple-quoted docstring
    formatted = f'{indent}"""\n'
    for line in lines:
        formatted += f'{indent}{line}\n'
    formatted += f'{indent}"""\n'

    return formatted


def insert_docstring_in_file(file_path: Path, func_info: Dict[str, Any], docstring: str) -> bool:
    """
    Insert or update docstring in the source file.

    Args:
        file_path (Path): Path to the Python file
        func_info (Dict[str, Any]): Function information including line numbers
        docstring (str): The formatted docstring to insert

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Determine insertion point
        func_start_line = func_info['line'] - 1  # Convert to 0-indexed

        # Find the line after function definition (after the def line and colon)
        insertion_line = func_start_line + 1

        # If there's an existing docstring, find its end and remove it
        if func_info['existing_docstring']:
            # Find and remove existing docstring lines
            in_docstring = False
            docstring_start = -1
            docstring_end = -1

            for i in range(insertion_line, min(insertion_line + 50, len(lines))):
                line_stripped = lines[i].strip()

                if not in_docstring and ('"""' in line_stripped or "'''" in line_stripped):
                    in_docstring = True
                    docstring_start = i
                    # Check if single-line docstring
                    if line_stripped.count('"""') == 2 or line_stripped.count("'''") == 2:
                        docstring_end = i
                        break
                elif in_docstring and ('"""' in line_stripped or "'''" in line_stripped):
                    docstring_end = i
                    break

            if docstring_start >= 0 and docstring_end >= 0:
                # Remove old docstring
                del lines[docstring_start:docstring_end + 1]
                insertion_line = docstring_start

        # Insert new docstring
        docstring_lines = docstring.split('\n')
        # Remove empty last line if present
        if docstring_lines and not docstring_lines[-1].strip():
            docstring_lines = docstring_lines[:-1]

        for i, doc_line in enumerate(docstring_lines):
            lines.insert(insertion_line + i, doc_line)

        # Write back to file
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True

    except Exception as e:
        ui.error(f"Failed to insert docstring: {e}")
        return False


def process_file(
    file_path: Path,
    config: Dict[str, Any],
    file_num: int,
    total_files: int
) -> Dict[str, Any]:
    """
    Process a single Python file and generate comments for all functions.

    Args:
        file_path (Path): Path to the Python file
        config (Dict[str, Any]): Workflow configuration
        file_num (int): Current file number (for progress display)
        total_files (int): Total number of files to process

    Returns:
        Dict[str, Any]: Processing results including success status and statistics

    Raises:
        InterruptedError: If user interrupts during processing
    """
    interrupt_handler = get_interrupt_handler()

    # Check for interrupt
    if interrupt_handler.is_interrupted():
        raise InterruptedError("Processing interrupted by user (ESC)")

    # File header
    print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
    clickable_path = ui.make_clickable_link(str(file_path), str(file_path.name))
    print(f"{Fore.CYAN}[File {file_num}/{total_files}]{Style.RESET_ALL} {clickable_path}")
    print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")

    # Parse functions
    ui.info("Parsing functions...")
    functions = analyze_functions(file_path)

    if not functions:
        ui.warn("No functions found")
        return {
            "status": "success",
            "file": str(file_path),
            "functions_processed": 0,
            "comments": []
        }

    print(f"{Fore.GREEN}[*] Found {len(functions)} function(s){Style.RESET_ALL}\n")

    # Get file context
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        file_context = ast.get_docstring(tree) or f"Python module: {file_path.name}"
    except:
        file_context = f"Python module: {file_path.name}"

    # Process each function
    comments = []
    auto_insert = config.get("options", {}).get("auto_insert", False)

    for i, func in enumerate(functions, 1):
        if interrupt_handler.is_interrupted():
            raise InterruptedError("Processing interrupted by user (ESC)")

        clickable_line = ui.make_clickable_path(str(file_path), func['line'])
        print(f"\n{Fore.CYAN}[{i}/{len(functions)}]{Style.RESET_ALL} Function: {Fore.YELLOW}{func['name']}(){Style.RESET_ALL} ({clickable_line})")

        # Generate comment with streaming
        comment = generate_function_comment_streaming(func, file_context, config)

        # Format the docstring
        formatted_comment = format_docstring(comment)

        comments.append({
            "function": func['name'],
            "line": func['line'],
            "comment": comment,
            "formatted": formatted_comment
        })

        # Auto-insert if enabled
        if auto_insert and not comment.startswith("[Error"):
            success = insert_docstring_in_file(file_path, func, formatted_comment)
            if success:
                print(f"    {Fore.GREEN}✓ Docstring inserted{Style.RESET_ALL}")
            else:
                print(f"    {Fore.YELLOW}⚠ Failed to insert (shown below){Style.RESET_ALL}")

    # File summary
    print(f"\n{Fore.GREEN}[✓] Processed {len(comments)} function(s) in {file_path.name}{Style.RESET_ALL}")

    return {
        "status": "success",
        "file": str(file_path),
        "functions_processed": len(comments),
        "comments": comments
    }


def handle(text: str = "") -> Dict[str, Any]:
    """
    Main entry point for function commenting tool.

    Processes Python files or directories, generating detailed docstrings
    for all functions found. Supports recursive directory processing,
    streaming LLM responses, and automatic docstring insertion.

    Args:
        text (str, optional): User input containing @path syntax. Defaults to "".

    Returns:
        Dict[str, Any]: Dictionary with status, message, and processing statistics

    Raises:
        InterruptedError: If user interrupts with ESC key
    """
    # Load workflow configuration
    config = load_workflow_config()

    # Try to get path from input or session history
    path_str = extract_path(text)

    if not path_str:
        # Try to use current script from session history
        history = get_session_history()
        current_script = history.get_current_script()

        if current_script:
            path_str = str(current_script.get('path', ''))
            ui.info(f"Using current script from context: {Path(path_str).name}")
        else:
            error_msg = "No path found. Use '@path' syntax to specify file or directory."
            ui.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

    target_path = Path(path_str)

    if not target_path.exists():
        error_msg = f"Path not found: {target_path}"
        ui.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    # Start listening for ESC key
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        # Header
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}FUNCTION COMMENTER{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        ui.info("Press ESC to interrupt...")

        # Find Python files
        options = config.get("options", {})
        recursive = options.get("recursive", True)
        skip_patterns = options.get("skip_patterns", [])

        python_files = find_python_files(target_path, recursive, skip_patterns)

        if not python_files:
            ui.warn("No Python files found")
            return {
                "status": "success",
                "message": "No Python files to process",
                "files_processed": 0
            }

        print(f"\n{Fore.GREEN}[*] Found {len(python_files)} Python file(s){Style.RESET_ALL}")

        if options.get("auto_insert", False):
            print(f"{Fore.YELLOW}[*] Auto-insert mode: ENABLED{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[*] Auto-insert mode: DISABLED (display only){Style.RESET_ALL}")

        # Process each file
        all_results = []
        total_functions = 0

        for i, py_file in enumerate(python_files, 1):
            result = process_file(py_file, config, i, len(python_files))
            all_results.append(result)
            total_functions += result.get("functions_processed", 0)

        # Final summary
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] COMPLETE{Style.RESET_ALL}")
        print(f"    Files processed: {len(python_files)}")
        print(f"    Functions documented: {total_functions}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")

        # Next steps
        if not options.get("auto_insert", False):
            print(f"{Fore.CYAN}[NEXT STEPS]{Style.RESET_ALL}")
            print("  - Review generated docstrings above")
            print("  - Manually copy to your source files, or")
            print("  - Enable 'auto_insert' in workflow config for automatic insertion")
            print()

        return {
            "status": "success",
            "message": f"Processed {len(python_files)} files, documented {total_functions} functions",
            "files_processed": len(python_files),
            "functions_documented": total_functions,
            "results": all_results
        }

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {
            "status": "interrupted",
            "message": "Processing interrupted by user"
        }
    except Exception as e:
        ui.error(f"Error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        interrupt_handler.stop_listening()


if __name__ == "__main__":
    # Test the commenter
    import sys
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
    else:
        test_text = "@testudo/agents/pulsus/workflows/tools/analyze"

    print(f"Testing Function Commenter with: {test_text}")
    result = handle(test_text)
    print(f"\nResult: {result['message']}")
