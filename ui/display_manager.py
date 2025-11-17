"""
display_manager.py — Unified Pulsus console output formatting.
Provides consistent, colorized, and structured display utilities.
"""

import sys
import shutil
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────
def _timestamp():
    return datetime.now().strftime("%H:%M:%S")


def _separator(char="═"):
    width = shutil.get_terminal_size((80, 20)).columns
    return char * min(width, 80)


def make_clickable_link(path: str, text: str = None, line: int = None) -> str:
    """
    Create a clickable hyperlink for terminal that supports OSC 8.

    Most modern terminals (VS Code, Windows Terminal, iTerm2, etc.) support this.

    Args:
        path: File path
        text: Display text (defaults to path)
        line: Optional line number

    Returns:
        Formatted hyperlink string
    """
    if text is None:
        text = path

    # Convert to absolute path
    abs_path = Path(path).resolve()

    # Create file:// URI
    # Windows paths need special handling
    if sys.platform == 'win32':
        # Convert Windows path to file URI: file:///C:/path/to/file.py
        uri = abs_path.as_uri()
    else:
        uri = f"file://{abs_path}"

    # Add line number if provided (VSCode and many editors support this)
    if line is not None:
        uri += f":{line}"
        if text == path:
            text = f"{text}:{line}"

    # OSC 8 hyperlink format: \033]8;;URI\033\\TEXT\033]8;;\033\\
    return f"\033]8;;{uri}\033\\{text}\033]8;;\033\\"


def make_clickable_path(path: str, line: int = None) -> str:
    """
    Create a clickable path with nice formatting.

    Args:
        path: File path
        line: Optional line number

    Returns:
        Formatted clickable path
    """
    path_obj = Path(path)

    if line is not None:
        display = f"{path_obj.name}:{line}"
    else:
        display = path_obj.name

    link = make_clickable_link(str(path), display, line)
    return f"{Fore.CYAN}{link}{Style.RESET_ALL}"


# ──────────────────────────────────────────────
# Headings & Sections
# ──────────────────────────────────────────────
def banner(title: str, sub: str = None):
    """Prints a large session banner."""
    line = _separator("═")
    print(Fore.CYAN + Style.BRIGHT + f"\n{line}")
    print(f"{title.center(len(line))}")
    if sub:
        print(Style.DIM + sub.center(len(line)))
    print(line + Style.RESET_ALL)


def section(title: str):
    """Prints a smaller section header."""
    print(Fore.MAGENTA + Style.BRIGHT + f"\n▌ {title}")
    print(Fore.MAGENTA + "‾" * (len(title) + 4) + Style.RESET_ALL)


def kv(key: str, value: str):
    """Prints a key-value pair in aligned form."""
    print(f"  {Fore.CYAN}{key:<14}{Style.RESET_ALL}: {value}")


# ──────────────────────────────────────────────
# Message Levels
# ──────────────────────────────────────────────
def info(msg: str):
    print(f"[{_timestamp()}] {Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")


def success(msg: str):
    print(f"[{_timestamp()}] {Fore.GREEN}[ OK ]{Style.RESET_ALL} {msg}")


def warn(msg: str):
    print(f"[{_timestamp()}] {Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")


def error(msg: str):
    print(f"[{_timestamp()}] {Fore.RED}[ERR ]{Style.RESET_ALL} {msg}", file=sys.stderr)


def debug(msg: str):
    print(f"[{_timestamp()}] {Fore.WHITE}{Style.DIM}[DBG ]{Style.RESET_ALL} {msg}")


# ──────────────────────────────────────────────
# Chat Labels
# ──────────────────────────────────────────────
def pulsus(msg: str):
    """Print message with [PULSUS] label in pink/magenta."""
    print(f"\n{Fore.MAGENTA}[PULSUS]{Style.RESET_ALL} {msg}")


def user(msg: str):
    """Print message with [YOU] label."""
    print(f"\n{Fore.CYAN}[YOU]{Style.RESET_ALL} {msg}")


def pulsus_streaming(text: str):
    """Print streaming text without newline (for LLM streaming)."""
    print(text, end='', flush=True)


# ──────────────────────────────────────────────
# Discovery & Analysis Display
# ──────────────────────────────────────────────
def discovery_header(framework_path: str):
    """Print framework discovery header."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN + Style.BRIGHT}  FRAMEWORK DISCOVERY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.WHITE + Style.DIM}  Scanning: {framework_path}{Style.RESET_ALL}\n")


def discovery_summary(total_tools: int, domains: dict):
    """Print discovery summary with domains and actions."""
    print(f"\n{Fore.GREEN + Style.BRIGHT}[+] Discovered {total_tools} tools{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}\n")

    for domain, actions in sorted(domains.items()):
        domain_name = domain.upper() if domain else "GENERAL"
        action_list = ", ".join(sorted(set(actions)))[:60]
        print(f"  {Fore.YELLOW}>{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{domain_name}{Style.RESET_ALL}")
        if action_list:
            print(f"    Actions: {Fore.WHITE + Style.DIM}{action_list}{Style.RESET_ALL}")
        else:
            print(f"    {Fore.WHITE + Style.DIM}(no specific actions defined){Style.RESET_ALL}")
        print()

    print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[*] Tip:{Style.RESET_ALL} Use {Fore.CYAN}@path{Style.RESET_ALL} to analyze any tool file")
    print(f"   Example: {Fore.WHITE + Style.DIM}@C:\\path\\to\\tool.py{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def analysis_header(filename: str):
    """Print file analysis header."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN + Style.BRIGHT}  FILE ANALYSIS: {filename}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def llm_thinking():
    """Print LLM thinking/processing message."""
    print(f"{Fore.MAGENTA}[PULSUS]{Style.RESET_ALL} {Fore.WHITE + Style.DIM}Analyzing script...{Style.RESET_ALL}", end='', flush=True)


def llm_understanding_header():
    """Print header for LLM understanding section."""
    print(f"\n\n{Fore.MAGENTA + Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA + Style.BRIGHT}  PULSUS UNDERSTANDING{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA + Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")


# ──────────────────────────────────────────────
# Framework Awareness Display
# ──────────────────────────────────────────────
def framework_awareness_header():
    """Print framework awareness initialization header."""
    print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN + Style.BRIGHT}  FRAMEWORK AWARENESS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")


def framework_awareness_status(health: str, files: int, issues: int, from_cache: bool = False):
    """
    Print framework awareness status summary.

    Args:
        health: Health status (e.g., '[EXCELLENT]', '[GOOD]', '[CRITICAL]')
        files: Number of files analyzed
        issues: Number of issues found
        from_cache: Whether loaded from cache or freshly analyzed
    """
    cache_status = "cached" if from_cache else "fresh"
    health_color = Fore.GREEN if "EXCELLENT" in health or "GOOD" in health else Fore.YELLOW if "NEEDS" in health else Fore.RED

    print(f"  {Fore.WHITE}Status:{Style.RESET_ALL} {health_color}{health}{Style.RESET_ALL} ({cache_status})")
    print(f"  {Fore.WHITE}Files:{Style.RESET_ALL}  {Fore.CYAN}{files}{Style.RESET_ALL} | {Fore.WHITE}Issues:{Style.RESET_ALL} {Fore.YELLOW}{issues}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}\n")


def repository_analysis_progress(message: str):
    """Print repository analysis progress message."""
    print(f"  {Fore.WHITE + Style.DIM}[*] {message}{Style.RESET_ALL}")


def repository_analysis_complete(repo_name: str, stats: dict):
    """
    Print repository analysis completion summary.

    Args:
        repo_name: Name of the repository
        stats: Statistics dictionary with metrics
    """
    print(f"\n{Fore.GREEN + Style.BRIGHT}[✓] Repository analysis complete:{Style.RESET_ALL} {repo_name}")
    print(f"    Files: {stats.get('total_files', 0)} | "
          f"Functions: {stats.get('total_functions', 0)} | "
          f"Issues: {stats.get('total_issues', 0)}")


# ──────────────────────────────────────────────
# Optional Utilities
# ──────────────────────────────────────────────
def line(char="─"):
    """Print a single decorative line."""
    print(_separator(char))
