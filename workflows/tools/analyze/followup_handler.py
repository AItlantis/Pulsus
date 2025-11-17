"""
Follow-up Question Handler

Handles follow-up questions about the currently analyzed script using session history.
"""

from typing import Dict, Any
import requests
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.session_history import get_session_history
from agents.pulsus.console.interrupt_handler import get_interrupt_handler
from colorama import Fore, Style

__domain__ = "analysis"
__action__ = "followup"


def handle(user_question: str) -> Dict[str, Any]:
    """
    Handle a follow-up question about the current script in context.

    Args:
        user_question: User's question

    Returns:
        Response dictionary
    """
    history = get_session_history()

    if not history.has_current_script():
        ui.warn("No script currently in context. Use @path to analyze a script first.")
        return {
            "status": "error",
            "message": "No script in context"
        }

    script_ctx = history.get_current_script()
    settings = load_settings()

    # Build context for the LLM
    functions_info = "\n".join([
        f"- {f['name']}({', '.join(f['args'])}): {f['docstring'][:100]}"
        for f in script_ctx.ast_analysis.get('functions', [])
    ])

    classes_info = "\n".join([
        f"- {c['name']}: {c['docstring'][:100]}"
        for c in script_ctx.ast_analysis.get('classes', [])
    ])

    # Include code sample if question seems code-specific
    code_sample = script_ctx.content[:3000] if script_ctx.content else ""

    prompt = f"""You are analyzing a Python script. Answer the user's question based on the following information:

File: {script_ctx.path.name}
Path: {script_ctx.path}

Previous Understanding:
{script_ctx.llm_understanding}

Functions:
{functions_info or "None"}

Classes:
{classes_info or "None"}

Code Sample:
```python
{code_sample}
```

User Question: {user_question}

Provide a clear, helpful answer based on the script's code and structure. Be specific and reference actual code elements when relevant."""

    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        ui.pulsus("Let me check the script...")
        ui.info("Press ESC to interrupt...")
        print()

        # Check for interrupt before starting
        if interrupt_handler.is_interrupted():
            raise InterruptedError("Follow-up question interrupted by user (ESC)")

        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 512,
                }
            },
            timeout=settings.model.timeout,
            stream=True
        )

        if response.status_code == 200:
            print(f"{Fore.MAGENTA}[PULSUS]{Style.RESET_ALL} ", end='', flush=True)

            full_text = ""
            for line in response.iter_lines():
                # Check for interrupt during streaming
                if interrupt_handler.is_interrupted():
                    print()
                    raise InterruptedError("Follow-up question interrupted by user (ESC)")

                if line:
                    import json
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            text = chunk["response"]
                            full_text += text
                            print(text, end='', flush=True)
                    except:
                        pass

            print("\n")

            # Add to conversation history
            history.add_conversation(user_question, full_text)

            return {
                "status": "success",
                "response": full_text.strip(),
                "message": "Follow-up answered"
            }
        else:
            ui.error("Failed to get response from LLM")
            return {
                "status": "error",
                "message": "LLM request failed"
            }

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {
            "status": "interrupted",
            "message": "Follow-up interrupted"
        }
    except Exception as e:
        ui.error(f"Follow-up question failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        interrupt_handler.stop_listening()


if __name__ == "__main__":
    print("Follow-up Handler - Test mode")
    print("Use in Pulsus session after analyzing a script")
