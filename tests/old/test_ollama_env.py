"""
test_ollama_env.py — Ensures Ollama is installed, running, and lists available models.
"""

import subprocess
import time
import json
import requests
import pytest

OLLAMA_HOST = "http://localhost:11434"


# ----------------------------- #
# 🔧 Utility Functions
# ----------------------------- #
def is_ollama_installed() -> bool:
    """Return True if 'ollama' CLI is installed."""
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def start_ollama_if_possible():
    """Try to start Ollama in the background if it's installed but not running."""
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
    except Exception:
        pass


def is_ollama_running() -> bool:
    """Check if Ollama responds on localhost:11434."""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def list_ollama_models() -> list:
    """
    Return a list of models available in Ollama.
    Uses REST API if available, otherwise falls back to CLI.
    """
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if r.status_code == 200:
            data = r.json()
            models = [m["name"] for m in data.get("models", [])]
            return models
    except Exception:
        pass

    # fallback to CLI
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        lines = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        if len(lines) > 1:
            # Skip header line like "NAME  SIZE  MODIFIED"
            return [line.split()[0] for line in lines[1:]]
    except Exception:
        pass
    return []


# ----------------------------- #
# 🧪 The Test
# ----------------------------- #
@pytest.mark.environment
def test_ollama_presence_and_health():
    """
    Verify Ollama is installed and serving locally.
    If installed but not running, attempt to start it.
    Finally, print the list of available models.
    """
    print("\n[INFO] Checking Ollama installation and runtime environment...")

    installed = is_ollama_installed()
    if not installed:
        pytest.skip("Ollama not installed. Please install from https://ollama.ai")

    running = is_ollama_running()
    if not running:
        print("[WARN] Ollama is installed but not running — attempting to start...")
        start_ollama_if_possible()
        time.sleep(2)
        running = is_ollama_running()

    if not running:
        pytest.fail("Ollama is installed but not responding on localhost:11434.\n"
                    "Try running 'ollama serve' manually.")
    else:
        print("[OK] Ollama service is running and responding.")

    # Fetch and display available models
    models = list_ollama_models()
    if models:
        print("\n[INFO] ✅ Available Ollama models:")
        for m in models:
            print(f"   - {m}")
    else:
        print("\n[WARN] No Ollama models found locally. Use 'ollama pull llama3' to add one.")

    assert running, "Ollama must be responsive for Pulsus to function."
