"""
Pulsus greeting and introduction messages.

This module provides the first message shown to users when starting a Pulsus session,
introducing the agent's capabilities and interaction model.
"""

GREETING_MESSAGE = """
** Hello, I'm Pulsus ** - your modular workflow agent.

I help you execute tasks by discovering existing tools, composing multi-step workflows,
or generating new solutions when needed. Every decision is transparent, validated, and
requires your approval before becoming permanent.

**What can I help you with today?**

Examples:
  - "Summarize the data matrix"
  - "Load CSV and plot statistics"
  - "Import JSON schema for validation"
  - "Analyze traffic data from Aimsun"
  - "Generate QGIS layer from coordinates"

---

**How I work:**
  1. **Parse** your request -> extract domain & action
  2. **Discover** existing tools or compose a workflow
  3. **Validate** all code (lint, type-check, sandbox)
  4. **Request approval** before making changes permanent
  5. **Log everything** for transparency and debugging

Type your request or use `/help` for more information.
"""

WELCOME_BANNER = """
================================================================

   PULSUS v4 - Deterministic Routing Agent
   Part of the Atlantis Framework

   [Discover]  |  [Compose]  |  [Generate]
   [OK] Safe by default  |  [*] Transparent decisions

================================================================
"""

SHORT_GREETING = """
Welcome to Pulsus! What would you like me to help you with?
"""


def get_greeting(verbose: bool = True) -> str:
    """
    Get the appropriate greeting message.

    Args:
        verbose: If True, return full greeting with examples and banner.
                If False, return short greeting only.

    Returns:
        Greeting message string
    """
    if verbose:
        return WELCOME_BANNER + "\n" + GREETING_MESSAGE
    else:
        return SHORT_GREETING


def get_session_start_message(user_name: str | None = None, run_id: str | None = None) -> str:
    """
    Get session start message with optional personalization.

    Args:
        user_name: Optional user name for personalization
        run_id: Optional run ID for tracking

    Returns:
        Personalized session start message
    """
    greeting = "Hello"
    if user_name:
        greeting += f", {user_name}"
    greeting += "! I'm Pulsus - your workflow agent.\n\n"

    if run_id:
        greeting += f"Session ID: {run_id}\n\n"

    greeting += (
        "I can help you by:\n"
        "  - Discovering existing tools from your framework\n"
        "  - Composing multi-step workflows\n"
        "  - Generating new solutions when needed\n\n"
        "All actions require your approval and are fully logged.\n\n"
        "**What would you like to do?**"
    )

    return greeting


def get_capabilities_summary() -> str:
    """
    Get a concise summary of Pulsus capabilities.

    Returns:
        Capabilities summary string
    """
    return """
**Pulsus Capabilities:**

[*] **Discovery**
   - Scan framework directory for existing tools
   - Score candidates by name, docs, and history
   - Select best match (threshold: 0.60)

[*] **Composition**
   - Chain multiple tools into workflows
   - Plan deterministic multi-step execution
   - Data flow between steps

[*] **Generation**
   - LLM-powered code synthesis as fallback
   - Safe, validated Python modules
   - Temporary storage for review

[*] **Validation Pipeline**
   - Ruff: Linting & style
   - Mypy: Type checking
   - Import: Smoke test
   - Dry-run: Sandboxed execution (30s, 512MB, no network)

[*] **Transparency**
   - All decisions scored and explained
   - Structured JSON logs (runs, validation, aggregated)
   - Human-in-the-loop approval required

[*] **Safety**
   - Path allowlists prevent unsafe access
   - Network disabled by default
   - Resource limits prevent runaway execution
   - AST validation ensures code integrity
"""


if __name__ == "__main__":
    # Demo the greeting messages
    print("=== VERBOSE GREETING ===")
    print(get_greeting(verbose=True))

    print("\n\n=== SHORT GREETING ===")
    print(get_greeting(verbose=False))

    print("\n\n=== SESSION START (Personalized) ===")
    print(get_session_start_message(user_name="Alice", run_id="run-1234-abcd"))

    print("\n\n=== CAPABILITIES SUMMARY ===")
    print(get_capabilities_summary())
