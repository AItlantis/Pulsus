"""
Dependency Documentation Tool

Identifies and documents dependencies on other scripts in a Python file.
Analyzes imports to find local script dependencies and generates descriptions
of what each dependency does using LLM analysis.

Keywords: dependency, dependencies, import, imports, document, analyze, require
"""

from pathlib import Path
import ast
import re
import requests
from typing import Dict, Any, List, Set
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.interrupt_handler import get_interrupt_handler
from agents.pulsus.console.session_history import get_session_history
from colorama import Fore, Style

__domain__ = "analysis"
__action__ = "document_dependencies"


def extract_file_path(text: str) -> str:
    """
    Extract file path from user input containing @path syntax.

    Args:
        text: User input text (e.g., "@C:\\path\\to\\file.py" or "analyze @/path/to/file.py")

    Returns:
        Extracted file path or empty string if not found
    """
    pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return ""


def extract_imports(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse Python file and extract all import statements.

    Args:
        file_path: Path to Python file

    Returns:
        List of dictionaries containing import information
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "is_local": False,
                        "resolved_path": None
                    })

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "is_local": False,
                        "resolved_path": None
                    })

        return imports

    except Exception as e:
        ui.error(f"Error parsing imports: {e}")
        return []


def resolve_local_imports(file_path: Path, imports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify which imports are local project files and resolve their paths.

    Args:
        file_path: Path to the current Python file
        imports: List of import dictionaries

    Returns:
        Updated list with local imports identified and paths resolved
    """
    settings = load_settings()
    framework_root = Path(settings.framework_root) if hasattr(settings, 'framework_root') else file_path.parent
    current_dir = file_path.parent

    # Find the project root (directory containing 'agents' or 'testudo')
    project_root = file_path.parent
    while project_root.parent != project_root:
        if (project_root / 'agents').exists() or project_root.name == 'testudo':
            break
        project_root = project_root.parent

    local_imports = []

    for imp in imports:
        module_parts = imp['module'].split('.')

        # Try to resolve as relative to various roots
        potential_paths = []

        # Check relative to current file
        rel_path = current_dir / '/'.join(module_parts)
        potential_paths.append(rel_path.with_suffix('.py'))
        potential_paths.append(rel_path / '__init__.py')

        # Check relative to project root
        if project_root != current_dir:
            root_path = project_root / '/'.join(module_parts)
            potential_paths.append(root_path.with_suffix('.py'))
            potential_paths.append(root_path / '__init__.py')

        # Check relative to framework root
        if framework_root != current_dir and framework_root != project_root:
            fw_path = framework_root / '/'.join(module_parts)
            potential_paths.append(fw_path.with_suffix('.py'))
            potential_paths.append(fw_path / '__init__.py')

        # Check if it's a local import
        for potential_path in potential_paths:
            if potential_path.exists():
                imp['is_local'] = True
                imp['resolved_path'] = str(potential_path)
                local_imports.append(imp)
                break

    return local_imports


def analyze_dependency_file(dep_path: Path) -> Dict[str, Any]:
    """
    Analyze a dependency file to extract key information.

    Args:
        dep_path: Path to the dependency file

    Returns:
        Dictionary with dependency analysis
    """
    try:
        content = dep_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        # Get module docstring
        module_doc = ast.get_docstring(tree) or ""

        # Count functions and classes
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return {
            "path": str(dep_path),
            "module_doc": module_doc,
            "functions": functions[:10],  # Limit to first 10
            "classes": classes[:10],
            "total_functions": len(functions),
            "total_classes": len(classes)
        }

    except Exception as e:
        return {
            "path": str(dep_path),
            "error": str(e)
        }


def generate_dependency_description(dep_info: Dict[str, Any], usage_context: str) -> str:
    """
    Use LLM to generate a description of what a dependency does.

    Args:
        dep_info: Dictionary containing dependency information
        usage_context: Context about how it's used in the main script

    Returns:
        Generated description of the dependency
    """
    settings = load_settings()
    interrupt_handler = get_interrupt_handler()

    # Build summary of dependency
    dep_path = Path(dep_info['path'])
    summary = f"File: {dep_path.name}\n"

    if dep_info.get('module_doc'):
        summary += f"Module docstring: {dep_info['module_doc'][:300]}\n"

    if dep_info.get('total_classes'):
        summary += f"Classes ({dep_info['total_classes']}): {', '.join(dep_info.get('classes', []))}\n"

    if dep_info.get('total_functions'):
        summary += f"Functions ({dep_info['total_functions']}): {', '.join(dep_info.get('functions', []))}\n"

    prompt = f"""Describe the purpose of this Python module/dependency in 2-3 sentences.

{summary}

Usage context: {usage_context}

Provide a concise description of:
1. What this module/script does
2. What functionality it provides
3. Why it would be imported/used

Be specific and practical. Output only the description (no headers, no extra text)."""

    try:
        # Check for interrupt
        if interrupt_handler.is_interrupted():
            raise InterruptedError("Dependency analysis interrupted by user (ESC)")

        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200,
                }
            },
            timeout=settings.model.timeout
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return f"[Error: LLM request failed with status {response.status_code}]"

    except InterruptedError:
        raise
    except Exception as e:
        return f"[Error generating description: {str(e)[:100]}]"


def format_dependency_doc(deps_with_descriptions: List[Dict[str, Any]], source_file: Path) -> str:
    """
    Format dependency documentation as markdown.

    Args:
        deps_with_descriptions: List of dependencies with their descriptions
        source_file: Path to the source file

    Returns:
        Formatted markdown documentation
    """
    doc = f"# Dependencies for {source_file.name}\n\n"
    doc += f"This document describes the dependencies used in `{source_file.name}`.\n\n"
    doc += f"## Local Script Dependencies\n\n"

    for i, dep in enumerate(deps_with_descriptions, 1):
        dep_path = Path(dep['resolved_path'])
        clickable = ui.make_clickable_link(dep['resolved_path'], dep_path.name)

        doc += f"### {i}. {dep['module']}\n\n"
        doc += f"**File:** `{dep_path.name}` ([View]({dep['resolved_path']}))\n\n"
        doc += f"**Import:** `{dep['import_statement']}`\n\n"
        doc += f"**Description:**\n{dep['description']}\n\n"

        if dep.get('functions'):
            doc += f"**Key Functions:** {', '.join(dep['functions'][:5])}\n\n"

        if dep.get('classes'):
            doc += f"**Key Classes:** {', '.join(dep['classes'][:5])}\n\n"

        doc += "---\n\n"

    # Add external dependencies section
    doc += "## External Dependencies\n\n"
    doc += "Third-party libraries and standard library modules used:\n\n"

    return doc


def handle(text: str = "") -> Dict[str, Any]:
    """
    Main entry point for dependency documentation tool.

    Args:
        text: User input containing @path syntax

    Returns:
        Dictionary with status, message, and dependency documentation
    """
    # Try to get file path from input or session history
    file_path_str = extract_file_path(text)

    if not file_path_str:
        # Try to use current script from session history
        history = get_session_history()
        current_script = history.get_current_script()

        if current_script:
            file_path_str = str(current_script.get('path', ''))
            ui.info(f"Using current script from context: {Path(file_path_str).name}")
        else:
            error_msg = "No file path found. Use '@path' syntax or analyze a file first."
            ui.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

    file_path = Path(file_path_str)

    if not file_path.exists():
        error_msg = f"File not found: {file_path}"
        ui.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    if file_path.suffix != '.py':
        error_msg = f"Not a Python file: {file_path}"
        ui.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

    # Start listening for ESC key
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()
    ui.info("Press ESC to interrupt...")

    try:
        # Header
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}DEPENDENCY DOCUMENTER{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        clickable_path = ui.make_clickable_link(str(file_path), str(file_path))
        print(f"Analyzing: {clickable_path}\n")

        # Extract imports
        ui.info("Extracting imports...")
        all_imports = extract_imports(file_path)

        if not all_imports:
            ui.warn("No imports found in file")
            return {
                "status": "success",
                "message": "No dependencies to document",
                "dependencies": 0
            }

        print(f"{Fore.GREEN}[*] Found {len(all_imports)} total import(s){Style.RESET_ALL}")

        # Resolve local imports
        ui.info("Resolving local dependencies...")
        local_imports = resolve_local_imports(file_path, all_imports)

        if not local_imports:
            ui.warn("No local script dependencies found")
            print(f"\n{Fore.YELLOW}[!] All imports are external libraries or standard library modules{Style.RESET_ALL}\n")
            return {
                "status": "success",
                "message": "No local dependencies found",
                "dependencies": 0,
                "total_imports": len(all_imports)
            }

        print(f"{Fore.GREEN}[*] Found {len(local_imports)} local script dependency(ies){Style.RESET_ALL}\n")

        # Analyze and document each dependency
        deps_with_descriptions = []

        for i, imp in enumerate(local_imports, 1):
            if interrupt_handler.is_interrupted():
                raise InterruptedError("Dependency analysis interrupted by user (ESC)")

            dep_path = Path(imp['resolved_path'])
            clickable_link = ui.make_clickable_link(imp['resolved_path'], dep_path.name)

            # Format import statement
            if imp['type'] == 'import':
                import_stmt = f"import {imp['module']}"
                if imp['alias']:
                    import_stmt += f" as {imp['alias']}"
            else:
                import_stmt = f"from {imp['module']} import {imp['name']}"
                if imp['alias']:
                    import_stmt += f" as {imp['alias']}"

            print(f"\n{Fore.CYAN}[{i}/{len(local_imports)}]{Style.RESET_ALL} Analyzing: {Fore.YELLOW}{imp['module']}{Style.RESET_ALL}")
            print(f"    File: {clickable_link}")
            print(f"    Import: {Fore.GREEN}{import_stmt}{Style.RESET_ALL}")

            # Analyze the dependency file
            ui.llm_thinking()
            dep_info = analyze_dependency_file(dep_path)

            # Generate description
            usage_context = f"Imported in {file_path.name} as: {import_stmt}"
            description = generate_dependency_description(dep_info, usage_context)
            print()  # Clear thinking line

            # Combine information
            dep_doc = {
                **imp,
                **dep_info,
                "import_statement": import_stmt,
                "description": description
            }
            deps_with_descriptions.append(dep_doc)

            # Display preview
            preview = description.split('\n')[0][:80]
            print(f"    {Fore.GREEN}Description:{Style.RESET_ALL} {preview}...")

        # Summary
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Documented {len(deps_with_descriptions)} local dependency(ies){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Display full documentation
        print(f"\n{Fore.MAGENTA}[DEPENDENCY DOCUMENTATION]{Style.RESET_ALL}")
        print("="*70)

        for dep in deps_with_descriptions:
            dep_path = Path(dep['resolved_path'])
            clickable_link = ui.make_clickable_link(dep['resolved_path'], dep_path.name)

            print(f"\n{Fore.YELLOW}Module: {dep['module']}{Style.RESET_ALL}")
            print(f"File: {clickable_link}")
            print(f"Import: {Fore.GREEN}{dep['import_statement']}{Style.RESET_ALL}")
            print("-"*70)
            print(f"{dep['description']}")

            if dep.get('total_functions'):
                print(f"\nKey Functions ({dep['total_functions']}): {', '.join(dep.get('functions', [])[:5])}")

            if dep.get('total_classes'):
                print(f"Key Classes ({dep['total_classes']}): {', '.join(dep.get('classes', [])[:5])}")

            print()

        # External dependencies
        external_imports = [imp for imp in all_imports if not any(
            loc['module'] == imp['module'] for loc in local_imports
        )]

        if external_imports:
            print(f"\n{Fore.MAGENTA}[EXTERNAL DEPENDENCIES]{Style.RESET_ALL}")
            print("="*70)
            print("Third-party and standard library imports:\n")

            external_modules = sorted(set(imp['module'].split('.')[0] for imp in external_imports))
            for module in external_modules:
                print(f"  • {module}")

        # Next steps
        print(f"\n{Fore.CYAN}[NEXT STEPS]{Style.RESET_ALL}")
        print("  - Review dependency descriptions")
        print("  - Consider creating a dependency diagram")
        print(f"  - Type {Fore.GREEN}'comment functions'{Style.RESET_ALL} to add function documentation")
        print()

        return {
            "status": "success",
            "message": f"Documented {len(deps_with_descriptions)} local dependencies",
            "file": str(file_path),
            "local_dependencies": len(deps_with_descriptions),
            "external_dependencies": len(external_imports),
            "dependencies": deps_with_descriptions
        }

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {
            "status": "interrupted",
            "message": "Dependency analysis interrupted"
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
    # Test the documenter
    import sys
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
    else:
        test_text = "@c:\\Users\\jean-noel.diltoer\\software\\Atlantis\\testudo\\agents\\pulsus\\workflows\\tools\\analyze\\file_analyzer.py"

    print(f"Testing Dependency Documenter with: {test_text}")
    result = handle(test_text)
    print(f"\nResult: {result['message']}")
