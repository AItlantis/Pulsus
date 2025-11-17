"""
LLM-powered greeting generator for Pulsus.

This module uses Ollama to generate dynamic, personalized introductions
instead of static pre-written greetings.
"""

import requests
import re
import json
from typing import Optional
from agents.pulsus.config.settings import load_settings
from agents.pulsus.console.interrupt_handler import get_interrupt_handler
from colorama import Fore, Style


def _strip_emojis(text: str) -> str:
    """
    Remove emojis and other Unicode symbols that cause Windows console issues.

    Args:
        text: Input text possibly containing emojis

    Returns:
        Text with emojis removed
    """
    # Pattern to match emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def generate_introduction(
    user_name: Optional[str] = None,
    session_id: Optional[str] = None,
    verbose: bool = True
) -> str:
    """
    Generate a dynamic introduction using the LLM (Ollama).

    Args:
        user_name: Optional user name for personalization
        session_id: Optional session ID to mention
        verbose: If True, request detailed introduction; if False, brief

    Returns:
        LLM-generated introduction text
    """
    settings = load_settings()

    # Build the prompt for the LLM
    if verbose:
        prompt = _build_verbose_prompt(user_name, session_id)
    else:
        prompt = _build_concise_prompt(user_name, session_id)

    # Call Ollama to generate the introduction with streaming
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        # Show header for streaming
        print(f"\n{Fore.MAGENTA + Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA + Style.BRIGHT}  PULSUS INTRODUCTION{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA + Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}Press ESC to skip introduction...{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}[PULSUS]{Style.RESET_ALL} ", end='', flush=True)

        # Check for interrupt before starting
        if interrupt_handler.is_interrupted():
            print()
            print(f"{Fore.YELLOW}[Skipped by user]{Style.RESET_ALL}\n")
            return _fallback_greeting(user_name, session_id, verbose)

        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": True,  # Enable streaming
                "options": {
                    "temperature": 0.7,  # Slightly more creative for greetings
                    "num_predict": 300,  # Slightly longer for greeting
                }
            },
            timeout=settings.model.timeout,
            stream=True
        )

        if response.status_code == 200:
            full_text = ""
            for line in response.iter_lines():
                # Check for interrupt during streaming
                if interrupt_handler.is_interrupted():
                    print()
                    print(f"\n{Fore.YELLOW}[Introduction interrupted by user]{Style.RESET_ALL}\n")
                    return _fallback_greeting(user_name, session_id, verbose)

                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            text = chunk["response"]
                            # Strip emojis on each chunk
                            clean_text = _strip_emojis(text)
                            full_text += clean_text
                            # Stream output
                            print(clean_text, end='', flush=True)
                    except:
                        pass

            print("\n")  # Final newline
            return full_text.strip()
        else:
            print()  # Clear line
            # Fallback on error
            return _fallback_greeting(user_name, session_id, verbose)

    except Exception as e:
        print()  # Clear line
        # Fallback if LLM is unavailable
        print(f"{Fore.YELLOW}[Warning] LLM unavailable for greeting: {e}{Style.RESET_ALL}")
        return _fallback_greeting(user_name, session_id, verbose)
    finally:
        interrupt_handler.stop_listening()


def _build_verbose_prompt(user_name: Optional[str], session_id: Optional[str]) -> str:
    """Build a detailed prompt for verbose greeting."""
    from agents.pulsus.config.features_display import get_features_text

    user_greeting = f"Hello, {user_name}" if user_name else "Hello"
    session_mention = f"\n\nYour session ID is: {session_id}" if session_id else ""

    # Get detailed features and tools list
    features_text = get_features_text()

    base_prompt = f"""You are Pulsus, an intelligent workflow routing agent for the Atlantis framework (QGIS and Aimsun Next).

Write a warm, natural introduction (2-3 paragraphs, under 250 words) that flows conversationally. Include:

- {user_greeting}! Introduce yourself as Pulsus, a modular workflow agent
- Briefly explain your core capabilities:
  * DISCOVER: Finding and scoring existing tools
  * COMPOSE: Planning multi-step workflows
  * GENERATE: Creating AI-powered solutions
  * MCP TOOLS: Script analysis, formatting, documentation, API search
  * LOGGING: Complete action history for reproducibility
- Mention validation (linting, type-checking, sandboxing) and user approval
- Give 2-3 quick examples: "@path/to/script.py", "format script.py", "search API for GKSection"
- Ask what they'd like help with today{session_mention}

{features_text}

Write as if you're talking to a colleague - friendly, professional, enthusiastic but not over-the-top. Use natural paragraphs. Keep it under 250 words.

Introduction:"""

    return base_prompt


def _build_concise_prompt(user_name: Optional[str], session_id: Optional[str]) -> str:
    """Build a brief prompt for concise greeting."""
    base_prompt = """You are Pulsus, a workflow routing agent in the Atlantis framework.

Write a BRIEF introduction (under 80 words) that:
1. Greets the user"""

    if user_name:
        base_prompt += f" by name ({user_name})"

    base_prompt += """
2. States you help by discovering existing tools, composing workflows, or generating new code
3. Mentions all actions require approval and are logged"""

    if session_id:
        base_prompt += f"""
4. Include session ID: {session_id}"""

    base_prompt += """
5. Ask what they need help with

Be warm but concise.

Introduction:"""

    return base_prompt


def _fallback_greeting(
    user_name: Optional[str],
    session_id: Optional[str],
    verbose: bool
) -> str:
    """
    Fallback static greeting when LLM is unavailable.

    This ensures Pulsus always greets the user even if Ollama is down.
    """
    if verbose:
        greeting = """
================================================================

   PULSUS v4 - Deterministic Routing Agent
   Part of the Atlantis Framework

================================================================

Hello"""
        if user_name:
            greeting += f", {user_name}"
        greeting += """! I'm Pulsus, your modular workflow agent.

I help you execute tasks through three main capabilities:

1. **DISCOVER** - I scan your framework directory for existing tools that match
   your request, scoring them by relevance and selecting the best fit.

2. **COMPOSE** - When multiple tools are needed, I plan and chain them together
   into multi-step workflows with data flowing between steps.

3. **GENERATE** - If no existing tools match, I use AI to synthesize new
   solutions, which are validated and require your approval.

Every decision I make is transparent. All code goes through a validation
pipeline (linting, type-checking, sandboxed execution) and I always request
your approval before making changes permanent.

**Try asking me to:**
  - "Summarize the data matrix"
  - "Load CSV and plot statistics"
  - "Analyze traffic data from Aimsun"
"""

        if session_id:
            greeting += f"\n[*] Session ID: {session_id}\n"

        greeting += "\n**What would you like me to help with?**"

    else:
        # Concise fallback
        greeting = "Hello"
        if user_name:
            greeting += f", {user_name}"
        greeting += """! I'm Pulsus, your workflow agent.

I help by discovering existing tools, composing multi-step workflows, or
generating new solutions. All actions require your approval and are fully logged.
"""
        if session_id:
            greeting += f"\nSession ID: {session_id}\n"

        greeting += "\n**What would you like to do?**"

    return greeting


def test_llm_greeting():
    """Test function to see LLM-generated greeting."""
    print("=== Testing LLM-Generated Greeting ===\n")

    print("--- Verbose Greeting ---")
    verbose_intro = generate_introduction(
        user_name="Alice",
        session_id="run-1234567890-abc123",
        verbose=True
    )
    print(verbose_intro)

    print("\n\n--- Concise Greeting ---")
    concise_intro = generate_introduction(
        user_name="Bob",
        session_id="run-9876543210-xyz789",
        verbose=False
    )
    print(concise_intro)


if __name__ == "__main__":
    test_llm_greeting()
