"""
Session initialization and pre-prompt loading for Pulsus.

This module handles:
- Loading the system pre-prompt from preprompt.md
- Initializing session context with run IDs
- Displaying greeting messages to users
- Managing session state and context
"""

from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from .greeting import (
    get_greeting,
    get_session_start_message,
    get_capabilities_summary,
)
from .llm_greeting import generate_introduction


@dataclass
class SessionContext:
    """
    Session context for a Pulsus interaction.

    Tracks the session ID, user info, start time, and configuration.
    """
    run_id: str
    started_at: datetime = field(default_factory=datetime.now)
    user_name: Optional[str] = None
    verbose: bool = True
    preprompt_loaded: bool = False
    preprompt_content: Optional[str] = None


def load_preprompt() -> str:
    """
    Load the Pulsus system pre-prompt from config/preprompt.md.

    Returns:
        Pre-prompt content as a string

    Raises:
        FileNotFoundError: If preprompt.md is not found
    """
    config_dir = Path(__file__).parent
    preprompt_path = config_dir / "preprompt.md"

    if not preprompt_path.exists():
        raise FileNotFoundError(
            f"Pre-prompt file not found at {preprompt_path}. "
            "Please ensure config/preprompt.md exists."
        )

    return preprompt_path.read_text(encoding="utf-8")


def generate_run_id() -> str:
    """
    Generate a unique run ID for the session.

    Format: run-{timestamp}-{short_uuid}
    Example: run-1730644496-abc123

    Returns:
        Run ID string
    """
    timestamp = int(datetime.now().timestamp())
    short_uuid = str(uuid.uuid4())[:6]
    return f"run-{timestamp}-{short_uuid}"


def initialize_session(
    user_name: Optional[str] = None,
    verbose: bool = True,
    load_preprompt_now: bool = True
) -> SessionContext:
    """
    Initialize a new Pulsus session.

    Args:
        user_name: Optional user name for personalization
        verbose: If True, display full greeting; if False, short greeting
        load_preprompt_now: If True, load preprompt immediately

    Returns:
        SessionContext with session metadata
    """
    run_id = generate_run_id()

    context = SessionContext(
        run_id=run_id,
        user_name=user_name,
        verbose=verbose,
    )

    if load_preprompt_now:
        try:
            context.preprompt_content = load_preprompt()
            context.preprompt_loaded = True
        except FileNotFoundError as e:
            # Log warning but continue - preprompt is optional for basic operation
            print(f"⚠️  Warning: {e}")
            context.preprompt_loaded = False

    return context


def display_session_start(context: SessionContext, use_llm: bool = True) -> None:
    """
    Display the session start message to the user.

    Shows greeting, run ID, and capabilities based on verbosity setting.

    Args:
        context: SessionContext with session information
        use_llm: If True, generate greeting with LLM; if False, use static greeting
    """
    if use_llm:
        # LLM-generated introduction (streams automatically)
        generate_introduction(
            user_name=context.user_name,
            session_id=context.run_id,
            verbose=context.verbose
        )

        if context.verbose:
            print(f"[*] Session ID: {context.run_id}")
            print(f"[*] Started: {context.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # Static greeting (original behavior)
        if context.verbose:
            # Full greeting with banner
            print(get_greeting(verbose=True))
            if context.run_id:
                print(f"\n[*] Session ID: {context.run_id}")
                print(f"[*] Started: {context.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Short greeting
            print(get_session_start_message(
                user_name=context.user_name,
                run_id=context.run_id
            ))


def get_system_prompt(context: SessionContext) -> str:
    """
    Get the system prompt for LLM interactions.

    Combines the pre-prompt with session-specific context.

    Args:
        context: SessionContext with session information

    Returns:
        Complete system prompt string
    """
    if not context.preprompt_loaded or not context.preprompt_content:
        # Fallback minimal prompt if preprompt not loaded
        return (
            "You are Pulsus, a deterministic routing agent that discovers, "
            "composes, or generates tools to satisfy user requests. "
            "Always explain your decisions and request approval."
        )

    # Prepend session context to the preprompt
    session_header = f"""
# Session Context

- **Run ID**: {context.run_id}
- **Started**: {context.started_at.isoformat()}
"""

    if context.user_name:
        session_header += f"- **User**: {context.user_name}\n"

    session_header += "\n---\n\n"

    return session_header + context.preprompt_content


def start_pulsus_session(
    user_name: Optional[str] = None,
    verbose: bool = True,
    show_greeting: bool = True,
    use_llm_greeting: bool = True
) -> SessionContext:
    """
    Complete session startup: initialize, load preprompt, display greeting.

    This is the main entry point for starting a Pulsus session.

    Args:
        user_name: Optional user name for personalization
        verbose: If True, show detailed greeting and info
        show_greeting: If True, display greeting message
        use_llm_greeting: If True, use LLM to generate dynamic greeting;
                         if False, use static pre-written greeting

    Returns:
        Initialized SessionContext
    """
    # Initialize session
    context = initialize_session(
        user_name=user_name,
        verbose=verbose,
        load_preprompt_now=True
    )

    # Display greeting if requested
    if show_greeting:
        display_session_start(context, use_llm=use_llm_greeting)

    return context


# Demo and testing
if __name__ == "__main__":
    print("=== TESTING SESSION INITIALIZATION ===\n")

    # Test 1: Verbose session
    print("--- Test 1: Verbose Session ---")
    ctx1 = start_pulsus_session(user_name="Alice", verbose=True)
    print(f"\nContext created: {ctx1.run_id}")
    print(f"Preprompt loaded: {ctx1.preprompt_loaded}")

    print("\n\n--- Test 2: Concise Session ---")
    ctx2 = start_pulsus_session(user_name="Bob", verbose=False)

    print("\n\n--- Test 3: System Prompt ---")
    ctx3 = start_pulsus_session(show_greeting=False)
    system_prompt = get_system_prompt(ctx3)
    print(f"System prompt length: {len(system_prompt)} characters")
    print(f"\nFirst 300 chars:\n{system_prompt[:300]}...")

    print("\n\n--- Test 4: Capabilities Summary ---")
    print(get_capabilities_summary())
