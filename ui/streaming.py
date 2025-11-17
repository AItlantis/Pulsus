"""
Streaming response utilities for Pulsus workflows.

Provides live LLM response streaming capabilities that can be used
across all workflow tools to give users real-time feedback.
"""

import requests
from typing import Optional, Callable, Dict, Any
from colorama import Fore, Style
from agents.pulsus.config.settings import load_settings
from agents.pulsus.console.interrupt_handler import get_interrupt_handler


def stream_llm_response(
    prompt: str,
    prefix: str = "",
    color: str = Fore.WHITE,
    on_token: Optional[Callable[[str], None]] = None,
    temperature: float = 0.3,
    num_predict: int = 400
) -> str:
    """
    Stream LLM response token-by-token to the console.

    Args:
        prompt: The prompt to send to the LLM
        prefix: Optional prefix to display before streaming (e.g., "Comment: ")
        color: Colorama color to use for streamed text
        on_token: Optional callback function called with each token
        temperature: LLM temperature parameter
        num_predict: Maximum number of tokens to generate

    Returns:
        Complete response text

    Raises:
        InterruptedError: If user presses ESC during streaming
        Exception: For other errors during generation
    """
    settings = load_settings()
    interrupt_handler = get_interrupt_handler()

    # Print prefix if provided
    if prefix:
        print(f"{color}{prefix}{Style.RESET_ALL}", end='', flush=True)

    full_response = []

    try:
        # Check for interrupt before starting
        if interrupt_handler.is_interrupted():
            raise InterruptedError("Response generation interrupted by user (ESC)")

        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                }
            },
            stream=True,
            timeout=settings.model.timeout
        )

        if response.status_code != 200:
            raise Exception(f"LLM request failed with status {response.status_code}")

        # Stream the response
        for line in response.iter_lines():
            # Check for interrupt during streaming
            if interrupt_handler.is_interrupted():
                print()  # New line before error
                raise InterruptedError("Response generation interrupted by user (ESC)")

            if line:
                import json
                chunk = json.loads(line)

                if "response" in chunk:
                    token = chunk["response"]

                    # Display token
                    print(f"{color}{token}{Style.RESET_ALL}", end='', flush=True)

                    # Collect for full response
                    full_response.append(token)

                    # Call token callback if provided
                    if on_token:
                        on_token(token)

                # Check if done
                if chunk.get("done", False):
                    break

        print()  # New line after streaming
        return "".join(full_response).strip()

    except InterruptedError:
        raise
    except Exception as e:
        print(f"\n{Fore.RED}[Error streaming response: {str(e)[:100]}]{Style.RESET_ALL}")
        raise


def stream_llm_json_response(
    prompt: str,
    prefix: str = "",
    temperature: float = 0.3,
    num_predict: int = 500
) -> Dict[str, Any]:
    """
    Stream LLM response and parse as JSON.

    Args:
        prompt: The prompt to send to the LLM
        prefix: Optional prefix to display before streaming
        temperature: LLM temperature parameter
        num_predict: Maximum number of tokens to generate

    Returns:
        Parsed JSON response as dictionary

    Raises:
        InterruptedError: If user presses ESC during streaming
        ValueError: If response cannot be parsed as JSON
        Exception: For other errors during generation
    """
    import json

    # Stream the response
    response_text = stream_llm_response(
        prompt=prompt,
        prefix=prefix,
        color=Fore.CYAN,
        temperature=temperature,
        num_predict=num_predict
    )

    # Try to extract JSON from response (handle markdown code blocks)
    try:
        # Remove markdown code fences if present
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")


def non_streaming_llm_response(
    prompt: str,
    temperature: float = 0.3,
    num_predict: int = 400
) -> str:
    """
    Get LLM response without streaming (original behavior).

    Args:
        prompt: The prompt to send to the LLM
        temperature: LLM temperature parameter
        num_predict: Maximum number of tokens to generate

    Returns:
        Complete response text

    Raises:
        InterruptedError: If user presses ESC before response
        Exception: For errors during generation
    """
    settings = load_settings()
    interrupt_handler = get_interrupt_handler()

    # Check for interrupt before starting
    if interrupt_handler.is_interrupted():
        raise InterruptedError("Response generation interrupted by user (ESC)")

    response = requests.post(
        f"{settings.model.host}/api/generate",
        json={
            "model": settings.model.name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            }
        },
        timeout=settings.model.timeout
    )

    if response.status_code == 200:
        result = response.json()
        return result.get("response", "").strip()
    else:
        raise Exception(f"LLM request failed with status {response.status_code}")
