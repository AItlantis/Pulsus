import argparse
import json
import sys
import time
import importlib.util
from agents.pulsus.routing.router import route
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.session_manager import ping_agent
from agents.pulsus.config.session import start_pulsus_session
from agents.pulsus.console.interrupt_handler import get_interrupt_handler


def main():
    """
    Pulsus Agent console main entrypoint.
    Supports both interactive and CLI (non-interactive) modes.
    """
    ap = argparse.ArgumentParser(description="Pulsus console (enhanced)")
    ap.add_argument("text", nargs="*", help="user prompt")
    ap.add_argument("--dry-run", action="store_true", help="Parse and show routing without executing.")
    ap.add_argument("--non-interactive", action="store_true", help="Single-shot mode; exit after one route.")
    ap.add_argument("--explain", action="store_true", help="Show detailed routing reasoning.")
    ap.add_argument("--plan", action="store_true", help="Display execution plan if available.")
    ap.add_argument("--ping", action="store_true", help="Ping the Pulsus agent.")
    ap.add_argument("--quiet", action="store_true", help="Skip greeting message.")
    ap.add_argument("--static-greeting", action="store_true", help="Use static greeting instead of LLM-generated.")
    args = ap.parse_args()

    # 🩺 Health check mode
    if args.ping:
        ping_agent()
        return

    # 👋 Automatic introduction - Pulsus introduces himself (using LLM by default)
    if not args.quiet:
        # Determine verbosity: use concise greeting for non-interactive single-shot
        verbose = not (args.non_interactive and args.text)
        use_llm = not args.static_greeting  # Use LLM unless --static-greeting flag
        session_ctx = start_pulsus_session(
            user_name=None,
            verbose=verbose,
            show_greeting=True,
            use_llm_greeting=use_llm
        )
        print()  # Add spacing after greeting

        # 🎯 Display Pulsus features and available tools
        _display_features_and_tools()

        # 🔍 Auto-discover framework tools after greeting
        _auto_discover_framework()

        # 🧠 Initialize framework awareness (auto-analyze if configured)
        _initialize_framework_awareness()
    else:
        # Quiet mode: initialize session without greeting
        from agents.pulsus.config.session import initialize_session
        session_ctx = initialize_session(verbose=False, load_preprompt_now=True)

        # 🧠 Initialize framework awareness even in quiet mode
        _initialize_framework_awareness()

    # If user provided a prompt via CLI args → single run
    if args.text:
        text = " ".join(args.text)
        _process_input(text, args, session_ctx)
        if args.non_interactive:
            return
    else:
        # 🧠 Interactive REPL mode (greeting already shown above)
        while True:
            try:
                text = input("\n[YOU] > ").strip()
                if text.lower() in {"exit", "quit"}:
                    ui.info("Session ended by user.")
                    break
                if not text:
                    continue
                _process_input(text, args, session_ctx)
            except KeyboardInterrupt:
                ui.info("\nSession interrupted (Ctrl+C). Exiting.")
                break
            except Exception as e:
                ui.error(f"Unexpected error: {e}")
                time.sleep(0.5)

    ui.info("Goodbye!")
    sys.exit(0)


def _auto_discover_framework():
    """
    Automatically discover and display all framework tools after greeting.
    """
    try:
        from agents.pulsus.workflows.tools.discover.framework_scanner import handle
        handle()
    except Exception as e:
        ui.error(f"Auto-discovery failed: {e}")


def _initialize_framework_awareness():
    """
    Initialize framework awareness by loading or analyzing the configured framework path.
    This runs on Pulsus startup if auto_analyze_on_start is enabled.
    """
    try:
        from agents.shared.repo_loader import initialize_framework_awareness
        initialize_framework_awareness()
    except Exception as e:
        # Silently fail if framework awareness initialization fails
        # (e.g., no FRAMEWORK_PATH configured)
        pass


def _display_features_and_tools():
    """
    Display Pulsus features and available MCP tools.
    """
    try:
        from agents.pulsus.config.features_display import display_features_compact
        display_features_compact()
    except Exception as e:
        ui.error(f"Failed to display features: {e}")


def _is_file_analysis_request(text: str) -> bool:
    """
    Check if user input contains @path syntax for file analysis.

    Args:
        text: User input text

    Returns:
        True if @path syntax detected, False otherwise
    """
    import re
    pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
    return bool(re.search(pattern, text))


def _handle_file_analysis(text: str):
    """
    Handle file analysis request with @path syntax using MCP.

    Supports smart routing when user adds additional text:
    - "@path comment it" -> analyze file, then generate comments
    - "@path generate docs" -> analyze file, then generate documentation
    - "@path what does X do?" -> analyze file, then answer question

    Args:
        text: User input containing @path
    """
    try:
        import re
        from agents.shared.tools import mcp_read_script
        from agents.pulsus.console.session_history import get_session_history
        from agents.mcp.helpers.action_logger import log_mcp_action
        from pathlib import Path
        from colorama import Fore, Style
        import json

        # Extract file path and any additional text
        pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
        match = re.search(pattern, text)

        if not match:
            ui.error("No file path found. Use '@path' syntax (e.g., @C:\\path\\to\\file.py)")
            return

        file_path_str = match.group(1)
        file_path = Path(file_path_str)

        # Extract additional text after the @path
        additional_text = text[match.end():].strip()

        ui.analysis_header(file_path.name)

        # Check if documentation exists
        from agents.pulsus.workflows.tools.analyze.doc_scanner import has_documentation
        if has_documentation(file_path):
            md_path = file_path.with_suffix('.md')
            clickable_md = ui.make_clickable_link(str(md_path), md_path.name)
            print(f"{Fore.GREEN}[*] Found existing documentation: {clickable_md}{Style.RESET_ALL}\n")

        ui.pulsus("Analyzing script via MCP...")
        ui.info("Press ESC to interrupt...")
        ui.info("📊 Parsing Python AST and extracting metadata...")

        # Use MCP tool to read and analyze
        result = mcp_read_script.invoke({"path": file_path_str})
        data = json.loads(result)

        ui.success("✓ Analysis complete!")

        # Log MCP action at routing level
        log_mcp_action(
            tool_name="mcp_read_script",
            operation="read",
            target_path=file_path_str,
            parameters={"path": file_path_str, "triggered_by": "pulsus_routing"},
            result=data,
            success=data.get('success', False),
            error=data.get('error') if not data.get('success') else None
        )

        if not data.get('success'):
            ui.error(f"File analysis failed: {data.get('error')}")
            return

        # Display analysis results
        ast_analysis = data.get('ast_analysis', {})
        metadata = data.get('metadata', {})

        # Format output
        output = "\n" + "="*70 + "\n"
        output += f"  FILE ANALYSIS: {file_path.name}\n"
        output += "="*70 + "\n"

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
            for imp in ast_analysis["imports"][:10]:
                output += f"  • {imp}\n"
            if len(ast_analysis["imports"]) > 10:
                output += f"  ... and {len(ast_analysis['imports']) - 10} more\n"

        # Classes
        if ast_analysis.get("classes"):
            output += "\n[CLASSES]\n"
            output += "-" * 70 + "\n"
            for cls in ast_analysis["classes"]:
                clickable_line = ui.make_clickable_path(str(file_path), cls['line'])
                output += f"  • {cls['name']} ({clickable_line})\n"
                if cls.get('methods'):
                    output += f"    Methods: {', '.join(cls['methods'])}\n"
                if cls.get('docstring'):
                    doc_preview = cls['docstring'].split('\n')[0][:60]
                    output += f"    {doc_preview}\n"

        # Functions
        if ast_analysis.get("functions"):
            output += "\n[FUNCTIONS]\n"
            output += "-" * 70 + "\n"
            for func in ast_analysis["functions"]:
                args_str = ', '.join(func.get('args', [])) if func.get('args') else ''
                clickable_line = ui.make_clickable_path(str(file_path), func['line'])
                output += f"  • {func['name']}({args_str}) - {clickable_line}\n"
                if func.get('docstring'):
                    doc_preview = func['docstring'].split('\n')[0][:60]
                    output += f"    {doc_preview}\n"

        output += "\n" + "="*70 + "\n"

        # Statistics
        num_functions = len(ast_analysis.get("functions", []))
        num_classes = len(ast_analysis.get("classes", []))
        output += f"[SUMMARY] {num_classes} classes, {num_functions} functions\n"
        output += "="*70 + "\n"

        print(output)

        # Save to session history
        history = get_session_history()
        history.set_current_script(
            file_path,
            ast_analysis,
            metadata,
            "",  # llm_understanding (not needed for MCP version)
            data.get('content', '')
        )

        # Smart routing: Check if user added additional text after @path
        if additional_text:
            ui.info(f"\nDetected follow-up action: '{additional_text}'")

            # Check if it's a comment request
            if _is_comment_functions_request(additional_text):
                ui.info("Auto-routing to comment generation...")
                _handle_comment_functions()
                return

            # Check if it's a docs request
            elif _is_generate_docs_request(additional_text):
                ui.info("Auto-routing to documentation generation...")
                _handle_generate_docs()
                return

            # Otherwise treat as a follow-up question
            else:
                ui.info("Processing as follow-up question...")
                _handle_followup_question(additional_text)
                return

        # Show available actions (only if no additional text)
        clickable_current = ui.make_clickable_link(str(file_path), file_path.name)
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[PULSUS MCP]{Style.RESET_ALL} Available actions for {clickable_current}:")
        print(f"  - Ask follow-up questions about this script")
        print(f"  - Type {Fore.GREEN}'comment it'{Style.RESET_ALL} to generate docstrings for all functions")
        print(f"  - Type {Fore.GREEN}'generate docs'{Style.RESET_ALL} to create documentation (.md file)")
        print(f"  - Use {Fore.CYAN}@path comment it{Style.RESET_ALL} to analyze and comment in one command")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    except Exception as e:
        ui.error(f"File analysis failed: {e}")
        import traceback
        traceback.print_exc()


def _is_generate_docs_request(text: str) -> bool:
    """
    Check if user wants to generate documentation.

    Args:
        text: User input

    Returns:
        True if requesting documentation generation
    """
    text_lower = text.lower().strip()

    # Exact matches
    exact_matches = ['generate docs', 'generate doc', 'create docs', 'create documentation',
                     'make docs', 'write docs', 'gen docs', 'document it']

    if text_lower in exact_matches:
        return True

    # Pattern matching for variations like "generate the docs", "create documentation for it"
    doc_keywords = ['generate', 'create', 'make', 'write', 'build', 'gen']
    doc_targets = ['doc', 'docs', 'documentation', 'markdown', 'md']

    words = text_lower.split()
    has_doc_keyword = any(kw in words for kw in doc_keywords)
    has_doc_target = any(tgt in text_lower for tgt in doc_targets)

    return has_doc_keyword and has_doc_target


def _is_comment_functions_request(text: str) -> bool:
    """
    Check if user wants to add comments/docstrings to functions.

    Args:
        text: User input

    Returns:
        True if requesting function commenting
    """
    text_lower = text.lower().strip()

    # Exact matches
    exact_matches = ['comment functions', 'add comments', 'comment all', 'generate comments',
                     'add docstrings', 'comment code', 'document functions', 'comment it',
                     'add comments to it', 'comment this']

    if text_lower in exact_matches:
        return True

    # Pattern matching for variations like "add comments to this", "comment the code"
    comment_keywords = ['comment', 'add comments', 'generate comments', 'document']
    comment_targets = ['functions', 'function', 'code', 'it', 'this', 'script', 'file']

    # Check if it's a comment request with natural language
    # Examples: "comment it", "add comments to this", "document the functions"
    has_comment_keyword = any(kw in text_lower for kw in comment_keywords)
    has_target = any(tgt in text_lower.split() for tgt in comment_targets)

    # Also check for "docstring" keyword
    if 'docstring' in text_lower:
        return True

    return has_comment_keyword and has_target


def _is_followup_question(text: str) -> bool:
    """
    Determine if user input is a follow-up question about the current script,
    or a new request that should go through normal routing.

    Args:
        text: User input

    Returns:
        True if this is a follow-up question, False if it should be routed normally
    """
    text_lower = text.lower().strip()

    # Keywords that indicate a NEW action (not a follow-up)
    new_action_keywords = [
        'read', 'write', 'create', 'generate', 'analyze', 'scan',
        'execute', 'run', 'validate', 'search', 'find', 'discover',
        'export', 'import', 'list', 'show all', 'get all'
    ]

    # If it starts with @ it's definitely a new file analysis request
    if text.strip().startswith('@'):
        return False

    # If it contains action keywords at the start, it's likely a new request
    for keyword in new_action_keywords:
        if text_lower.startswith(keyword):
            return False

    # Question words indicate follow-up questions
    question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'tell me']
    if any(text_lower.startswith(qw) for qw in question_words):
        return True

    # Short phrases are likely follow-up questions
    if len(text.split()) <= 5:
        return True

    # Default to follow-up for ambiguous cases (preserves existing behavior)
    return True


def _handle_generate_docs():
    """Handle documentation generation request using MCP."""
    from agents.pulsus.console.session_history import get_session_history
    from agents.mcp.helpers.action_logger import log_mcp_action

    history = get_session_history()

    if not history.has_current_script():
        ui.warn("No script currently in context. Analyze a script with @path first.")
        return

    script_ctx = history.get_current_script()

    try:
        # Use MCP tool instead of old workflow
        from agents.shared.tools import mcp_write_md
        import json

        ui.pulsus("Generating comprehensive documentation via MCP...")
        ui.info("⏳ This may take 30-60 seconds depending on file size...")
        result = mcp_write_md.invoke({"path": str(script_ctx.path)})

        # Parse JSON result
        data = json.loads(result)

        # Log MCP action at routing level
        log_mcp_action(
            tool_name="mcp_write_md",
            operation="write_md",
            target_path=str(script_ctx.path),
            parameters={"path": str(script_ctx.path), "triggered_by": "pulsus_routing"},
            result=data,
            success=data.get('success', False),
            error=data.get('error') if not data.get('success') else None
        )

        if data.get('success'):
            ui.success(data.get('message', 'Documentation generated'))
            clickable_doc = ui.make_clickable_link(data['doc_path'], data['doc_path'])
            print(f"\nDocumentation created: {clickable_doc}")
        else:
            ui.error(f"Documentation generation failed: {data.get('error')}")
    except Exception as e:
        ui.error(f"Documentation generation failed: {e}")


def _handle_comment_functions():
    """Handle function commenting request using MCP."""
    from agents.pulsus.console.session_history import get_session_history
    from agents.mcp.helpers.action_logger import log_mcp_action

    history = get_session_history()

    if not history.has_current_script():
        ui.warn("No script currently in context. Analyze a script with @path first.")
        return

    script_ctx = history.get_current_script()

    try:
        # Use MCP tool instead of old workflow
        from agents.shared.tools import mcp_add_comments
        import json
        from colorama import Fore, Style

        ui.pulsus("Generating function comments via MCP...")
        ui.info("⏳ Processing each function (progress will be shown)...")
        params = {
            "path": str(script_ctx.path),
            "strategy": "docstring"
        }
        result = mcp_add_comments.invoke(params)

        # Parse JSON result
        data = json.loads(result)

        # Log MCP action at routing level
        log_mcp_action(
            tool_name="mcp_add_comments",
            operation="add_comments",
            target_path=str(script_ctx.path),
            parameters={**params, "triggered_by": "pulsus_routing"},
            result=data,
            success=data.get('success', False),
            error=data.get('error') if not data.get('success') else None
        )

        if data.get('success'):
            comments = data.get('comments', [])
            ui.success(f"Generated comments for {len(comments)} functions")

            # Display generated comments
            if comments:
                print(f"\n{Fore.MAGENTA}[GENERATED COMMENTS]{Style.RESET_ALL}")
                print("="*70)
                for comment in comments:
                    clickable_line = ui.make_clickable_path(str(script_ctx.path), comment['line'])
                    print(f"\n{Fore.YELLOW}Function: {comment['function']}(){Style.RESET_ALL} ({clickable_line})")
                    print("-"*70)
                    print(comment['formatted'])

                print(f"\n{Fore.CYAN}[NEXT STEPS]{Style.RESET_ALL}")
                print("  - Review and edit comments as needed")
                print("  - Copy comments to your source file")
                print()
        else:
            ui.error(f"Comment generation failed: {data.get('error')}")
    except Exception as e:
        ui.error(f"Comment generation failed: {e}")


def _handle_followup_question(text: str):
    """Handle follow-up question about current script."""
    try:
        from agents.pulsus.workflows.tools.analyze.followup_handler import handle
        handle(text)
    except Exception as e:
        ui.error(f"Follow-up question failed: {e}")


def _process_input(text, args, session_ctx):
    """
    Shared routine for processing a query and printing routing results.

    Args:
        text: User input text
        args: Command-line arguments
        session_ctx: Session context with run_id and preprompt
    """
    # Check for built-in commands
    text_lower = text.lower().strip()

    # "list tools" command
    if text_lower in ['list tools', 'show tools', 'tools', 'list features', 'features']:
        from agents.pulsus.config.features_display import display_tools_full
        display_tools_full()
        return

    # "examples" command
    if text_lower in ['examples', 'show examples', 'quick start']:
        from agents.pulsus.config.features_display import display_quick_start_examples
        display_quick_start_examples()
        return

    # Check if this is a file analysis request (@path syntax)
    if _is_file_analysis_request(text):
        _handle_file_analysis(text)
        return

    # Check if this is a documentation generation request
    if _is_generate_docs_request(text):
        _handle_generate_docs()
        return

    # Check if this is a function commenting request
    if _is_comment_functions_request(text):
        _handle_comment_functions()
        return

    # Check if this might be a follow-up question
    from agents.pulsus.console.session_history import get_session_history
    history = get_session_history()

    if history.has_current_script() and _is_followup_question(text):
        # User has a script in context AND asking a followup question
        _handle_followup_question(text)
        return

    # Otherwise, proceed with normal routing
    start = time.strftime("%H:%M:%S")
    ui.info(f"[{start}] Routing query (Session: {session_ctx.run_id})...")
    ui.info("Press ESC to interrupt...")

    # Start listening for ESC key
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        decision = route(text, non_interactive=args.non_interactive, explain=args.explain)
        end = time.strftime("%H:%M:%S")

        ui.success(f"[{end}] Routing complete.")
        ui.kv("Policy", decision.policy)
        ui.kv("Route ID", decision.route_id)

        if decision.selected:
            ui.kv("Selected", ", ".join([s.path.name for s in decision.selected]))
        ui.kv("Reason", decision.reason)

        if args.plan and decision.plan:
            ui.section("Execution Plan")
            print(json.dumps(decision.plan, indent=2, ensure_ascii=False))

        # Auto-execute based on policy
        if decision.policy == "select" and decision.tmp_path:
            # Execute the selected tool directly
            _execute_selected_tool(str(decision.tmp_path), decision.selected[0] if decision.selected else None)
        elif decision.policy == "compose" and decision.tmp_path:
            # Execute the composed workflow
            _execute_generated(str(decision.tmp_path))
        elif decision.policy == "generate" and decision.tmp_path:
            # Execute generated module if fallback used
            _execute_generated(str(decision.tmp_path))
    except InterruptedError as e:
        ui.warn(f"\n{e}")
        ui.info("Returning to prompt...")
    finally:
        # Stop listening for ESC key
        interrupt_handler.stop_listening()


def _execute_selected_tool(path: str, tool_spec=None):
    """
    Execute the selected tool directly.

    Args:
        path: Path to the tool file
        tool_spec: ToolSpec object with tool metadata
    """
    if not path:
        return

    try:
        from pathlib import Path
        tool_path = Path(path)

        # Check if it's an MCP virtual path
        if str(tool_path).startswith("mcp:"):
            ui.warn("MCP tool execution not yet implemented")
            return

        if not tool_path.exists():
            ui.error(f"Tool not found: {path}")
            return

        ui.info(f"Executing tool: {tool_path.name}")

        # Import and execute the tool
        spec = importlib.util.spec_from_file_location("selected_tool", str(tool_path))
        tool_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_mod)

        # Call the handle function with appropriate parameters
        if hasattr(tool_mod, 'handle'):
            # For repository analyzer, it expects repo_path
            # Try to infer from framework settings
            from agents.pulsus.config.settings import load_settings
            settings = load_settings()

            # Use framework root if available, otherwise current directory
            repo_path = str(settings.framework_root) if settings.framework_root and settings.framework_root.exists() else None

            result = tool_mod.handle(repo_path=repo_path)

            if result and isinstance(result, dict):
                if result.get('success'):
                    ui.success("Tool execution completed successfully")
                else:
                    ui.error(f"Tool execution failed: {result.get('error', 'Unknown error')}")
        else:
            ui.error(f"Tool does not have a 'handle' function: {tool_path.name}")

    except Exception as e:
        ui.error(f"Tool execution error: {e}")
        import traceback
        traceback.print_exc()


def _execute_generated(path: str):
    """
    Dynamically loads and runs a generated module (LLM fallback).
    """
    if not path:
        return

    ui.info(f"Executing generated module: {path}")
    try:
        spec = importlib.util.spec_from_file_location("tmp_mod", path)
        tmp_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tmp_mod)
        result = tmp_mod.run()
        ui.success(f"Generated Output: {result.get('message', 'OK')}")
    except Exception as e:
        ui.error(f"Execution error: {e}")

if __name__ == "__main__":
    main()
