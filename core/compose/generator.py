"""
generator.py — Pulsus fallback LLM module generator.
If no tools or workflows match, this component queries Ollama for a response
and writes it into a temporary Python module.
"""

from pathlib import Path
import requests
import json
from agents.pulsus.config.settings import load_settings

# ---------------------------------------------------------------------------
# Load model settings (defined in your config/settings.py)
# ---------------------------------------------------------------------------
settings = load_settings()

# Default fallback template
_TEMPLATE = '''"""
Auto-generated temporary module (LLM fallback stub).
Allowed imports: stdlib only.
"""
def run(**kwargs):
    return {"ok": True, "message": "generated stub executed"}
'''


def generate_response(prompt: str) -> str:
    """
    Query the Ollama model for a text generation response.
    Returns a plain text answer or a safe fallback message.
    """
    try:
        r = requests.post(
            f"{settings.model.host}/api/generate",
            json={"model": settings.model.name, "prompt": prompt, "stream": False},
            timeout=settings.model.timeout
        )
        if r.status_code == 200:
            data = r.json()
            # With stream=False, Ollama returns a single JSON object with "response" field
            return data.get("response", "")
        return f"[Ollama Error {r.status_code}] {r.text}"
    except Exception as e:
        return f"[Generator Error] {str(e)}"

def generate_tmp_module(parsed, tmp_root: Path, route_id: str) -> Path:
    """
    Creates a temporary Python module embedding the Ollama LLM response.
    """
    tmp_root.mkdir(parents=True, exist_ok=True)

    # Build prompt and get LLM response
    prompt = f"You are a helpful assistant. Respond to the user's message in a natural, conversational way.\n\nUser message: {parsed.intent}"
    llm_response = generate_response(prompt)

    # Safely escape problematic characters for embedding into Python source
    safe_response = (
        llm_response
        .replace("\\", "\\\\")   # escape backslashes
        .replace('"', '\\"')     # escape quotes
        .replace("\n", "\\n")    # literal newlines
    )

    dynamic_code = f'''"""
Auto-generated temporary module (LLM fallback).
Generated from Pulsus router fallback → Ollama model.
"""
def run(**kwargs):
    return {{
        "ok": True,
        "message": "{safe_response}"
    }}
'''

    path = tmp_root / f"tmp_generated_{route_id}.py"

    try:
        path.write_text(dynamic_code, encoding="utf-8")
    except Exception:
        # fallback to safe template if write fails
        path.write_text(_TEMPLATE, encoding="utf-8")

    return path
