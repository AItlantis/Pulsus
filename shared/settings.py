# UTF-8, Pylance-friendly
"""
Agent Settings - Synced with Shared Configuration

This module provides agent-specific settings that are synchronized with
the global configuration system. Model selections from L'Oasis are
automatically reflected here.
"""
from typing import Final
import os
import sys

# Import shared config
try:
    from shared_config import config as shared_config
except ImportError:
    # Add parent directories to path - go up to Atlantis root (3 levels: shared -> agents -> testudo -> Atlantis)
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from shared_config import config as shared_config

# Point LangChain at your local Ollama
OLLAMA_BASE_URL: Final[str] = "http://localhost:11434"

# Map your role->model names (pull them with `ollama pull ...`)
# These are now loaded from shared config, with fallback defaults
def get_model_pulse() -> str:
    """Get Pulse agent model from shared config"""
    return shared_config.get("pulse_model", "llama3.2:3b")

def get_model_shell() -> str:
    """Get Shell agent model from shared config"""
    return shared_config.get("shell_model", "mistral:7b")

def get_model_compass() -> str:
    """Get Compass agent model from shared config"""
    return shared_config.get("compass_model", "llama3.1:8b")

# Backwards compatibility - use functions but provide constants
MODEL_PULSE: str = get_model_pulse()      # light & quick
MODEL_SHELL: str = get_model_shell()      # larger doc/model
MODEL_COMPASS: str = get_model_compass()  # supervisor

# Tunables
DEFAULT_TEMP: Final[float] = 0.3
MAX_TOKENS: Final[int] = 768  # keep responses tight for tool loops

# Documentation Configuration
DOCS_CONFIG = {
    "aimsun_url": "http://localhost:9230/index.html",
    "qgis_url": "https://api.qgis.org/api/",
    "cache_ttl": 3600,  # 1 hour cache
    "max_results": 5,
    "local_docs_path": "docs/",
    "enable_remote": True,  # Enable remote doc fetching
    "enable_cache": True    # Enable caching
}

# External Domains Configuration
EXTERNAL_DOMAINS_CONFIG = {
    "enabled": False,  # Enable external domain scanning
    "domains_path": "",  # Path to external workflow domains folder (e.g., workflow/domains)
    "auto_scan_on_startup": False,  # Automatically scan domains on startup
    "merge_with_builtin": True,  # Merge discovered domains with built-in domains
    "cache_domains": True,  # Cache discovered domains to avoid re-scanning
    "cache_file": "agents/config/external_domains_cache.json"
}

# Framework Path Configuration
FRAMEWORK_CONFIG = {
    "framework_path": "",  # Path to main framework/repository to analyze
    "auto_analyze_on_start": True,  # Automatically analyze framework on Pulsus startup
    "pulse_folder": ".pulse",  # Folder name for storing analysis results
    "incremental_updates": True,  # Only re-analyze changed files
    "cache_enabled": True,  # Enable caching of analysis results
}

# Reload models from config
def reload_models():
    """Reload model settings from shared config"""
    global MODEL_PULSE, MODEL_SHELL, MODEL_COMPASS
    shared_config.load()
    MODEL_PULSE = get_model_pulse()
    MODEL_SHELL = get_model_shell()
    MODEL_COMPASS = get_model_compass()
    return MODEL_PULSE, MODEL_SHELL, MODEL_COMPASS

def get_docs_config(key: str = None):
    """
    Get documentation configuration

    Args:
        key: Specific config key to retrieve, or None for entire config

    Returns:
        Config value or entire config dict
    """
    if key:
        return DOCS_CONFIG.get(key)
    return DOCS_CONFIG.copy()

def update_docs_config(**kwargs):
    """
    Update documentation configuration

    Args:
        **kwargs: Configuration keys and values to update
    """
    DOCS_CONFIG.update(kwargs)

def get_external_domains_config(key: str = None):
    """
    Get external domains configuration

    Args:
        key: Specific config key to retrieve, or None for entire config

    Returns:
        Config value or entire config dict
    """
    if key:
        return EXTERNAL_DOMAINS_CONFIG.get(key)
    return EXTERNAL_DOMAINS_CONFIG.copy()

def update_external_domains_config(**kwargs):
    """
    Update external domains configuration

    Args:
        **kwargs: Configuration keys and values to update
    """
    EXTERNAL_DOMAINS_CONFIG.update(kwargs)

def set_external_domains_path(path: str):
    """
    Set the external domains path and enable scanning

    Args:
        path: Path to external workflow domains folder
    """
    EXTERNAL_DOMAINS_CONFIG["domains_path"] = path
    EXTERNAL_DOMAINS_CONFIG["enabled"] = bool(path)

def get_framework_config(key: str = None):
    """
    Get framework configuration

    Args:
        key: Specific config key to retrieve, or None for entire config

    Returns:
        Config value or entire config dict
    """
    if key:
        return FRAMEWORK_CONFIG.get(key)
    return FRAMEWORK_CONFIG.copy()

def update_framework_config(**kwargs):
    """
    Update framework configuration

    Args:
        **kwargs: Configuration keys and values to update
    """
    FRAMEWORK_CONFIG.update(kwargs)

def set_framework_path(path: str):
    """
    Set the framework path for automatic analysis

    Args:
        path: Path to main framework/repository
    """
    FRAMEWORK_CONFIG["framework_path"] = path
