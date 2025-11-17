# Pulsus Configuration Module

This directory contains configuration, settings, and session management for the Pulsus agent.

## Files Overview

### `settings.py`
Core configuration classes and settings loader.

**Key Changes:**
- **max_tokens**: Increased from 1024 to **2048** for better code generation support
- Environment variable overrides supported for all settings
- Configuration classes: ModelConfig, RankerConfig, SandboxConfig, Settings

**Default Settings:**
```python
ModelConfig:
  - provider: "ollama"
  - host: "http://localhost:11434"
  - name: "falcon3:1b"
  - temperature: 0.2
  - max_tokens: 2048  # ← Increased
  - timeout: 60

RankerConfig:
  - threshold: 0.60
  - weights: {'name': 0.40, 'doc': 0.40, 'history': 0.20}

SandboxConfig:
  - max_seconds: 30
  - max_mem_mb: 512
  - network: 'off'
```

### `preprompt.md`
Comprehensive system prompt for LLM interactions with Pulsus.

**Contents:**
- Identity & Role definition
- Core capabilities (parsing, discovery, routing, validation)
- Three routing policies: SELECT, COMPOSE, GENERATE
- Safety principles and constraints
- Response format guidelines
- Configuration awareness
- Logging & observability details
- Interaction style guidelines
- Greeting message template

**Usage:**
```python
from agents.pulsus.config.session import load_preprompt
preprompt = load_preprompt()
```

### `greeting.py`
User-facing greeting messages and capability summaries.

**Exports:**
- `GREETING_MESSAGE`: Full welcome message with examples
- `WELCOME_BANNER`: ASCII art banner for session start
- `SHORT_GREETING`: Concise greeting for minimal output
- `get_greeting(verbose=True)`: Get greeting with optional verbosity
- `get_session_start_message(user_name, run_id)`: Personalized greeting
- `get_capabilities_summary()`: Detailed capability listing

**Example:**
```python
from agents.pulsus.config.greeting import get_greeting
print(get_greeting(verbose=True))
```

### `session.py`
Session initialization and lifecycle management.

**Key Components:**

1. **SessionContext** (dataclass):
   - `run_id`: Unique session identifier (format: `run-{timestamp}-{uuid}`)
   - `started_at`: Session start timestamp
   - `user_name`: Optional user personalization
   - `verbose`: Control greeting verbosity
   - `preprompt_loaded`: Flag for preprompt load status
   - `preprompt_content`: Loaded preprompt text

2. **Functions:**
   - `load_preprompt()`: Load system prompt from preprompt.md
   - `generate_run_id()`: Create unique session IDs
   - `initialize_session()`: Set up new session context
   - `display_session_start()`: Show greeting to user
   - `get_system_prompt()`: Build complete LLM prompt with context
   - `start_pulsus_session()`: **Main entry point** for session startup

**Usage Example:**
```python
from agents.pulsus.config.session import start_pulsus_session

# Start a new session with greeting
context = start_pulsus_session(
    user_name="Alice",
    verbose=True,
    show_greeting=True
)

# Use the context for LLM interactions
from agents.pulsus.config.session import get_system_prompt
system_prompt = get_system_prompt(context)
```

## Session Startup Flow

```
start_pulsus_session()
  ├─> generate_run_id()              # Create unique ID
  ├─> initialize_session()            # Set up context
  │   └─> load_preprompt()           # Load system prompt
  └─> display_session_start()        # Show greeting
      ├─> get_greeting() [verbose]
      └─> get_session_start_message() [concise]
```

## Environment Variables

All configuration can be overridden via environment variables:

```bash
# Model Configuration
export OLLAMA_HOST="http://localhost:11434"
export PULSUS_MODEL_NAME="falcon3:1b"
export PULSUS_TEMPERATURE="0.2"
export PULSUS_MAX_TOKENS="2048"
export PULSUS_TIMEOUT="60"

# Path Configuration
export PULSUS_WORKFLOWS_ROOT="agents/pulsus/workflows"
export PULSUS_FRAMEWORK_ROOT="/path/to/user/tools"
export PULSUS_LOG_DIR="logs"
```

## Testing

Run the session demo:
```bash
cd testudo
python -m agents.pulsus.config.session
```

Run individual module tests:
```bash
# Test greeting messages
python -m agents.pulsus.config.greeting

# Test session initialization
python -c "
from agents.pulsus.config.session import start_pulsus_session
ctx = start_pulsus_session(verbose=False)
print(f'Session ID: {ctx.run_id}')
"
```

## Integration Points

### CLI Integration
```python
from agents.pulsus.config.session import start_pulsus_session

def main():
    # Start session with greeting
    session = start_pulsus_session(
        user_name=None,  # Auto-detect or prompt
        verbose=True,
        show_greeting=True
    )

    # Use session.run_id for logging
    # Use get_system_prompt(session) for LLM calls
```

### Router Integration
```python
from agents.pulsus.config.session import get_system_prompt
from agents.pulsus.config.settings import load_settings

settings = load_settings()
session_context = ...  # From session manager

# Pass to LLM for generation/composition
system_prompt = get_system_prompt(session_context)
```

## Character Encoding Notes

All greeting messages and banners use ASCII-safe characters to ensure compatibility with Windows console (cp1252 encoding). Emojis and special Unicode characters have been replaced with ASCII equivalents:
- ✓ → [OK]
- 📋 → [*]
- 👋 → (removed)
- • → -
- → → ->

## Version History

**v4** (2025-11-03):
- Created comprehensive preprompt.md system prompt
- Increased max_tokens from 1024 to 2048
- Added greeting.py with multiple greeting formats
- Implemented session.py for lifecycle management
- Added run_id generation with timestamp-uuid format
- Ensured Windows console compatibility (ASCII-safe output)
