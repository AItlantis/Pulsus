# Pulsus Dependency Guide

**Date**: November 17, 2025
**Version**: 0.1.0
**Status**: Production Ready

---

## Overview

This document describes all dependencies required for Pulsus MCP system, organized by phase and purpose according to the architecture plan.

---

## Core Dependencies (Phase 1)

These dependencies are required for basic Pulsus functionality:

```txt
# Data validation and type safety
pydantic>=2.0.0

# Environment configuration
python-dotenv
```

---

## LangChain Ecosystem (Phase 2, 9)

LangChain integration is core to Pulsus architecture:

```txt
# Core LangChain functionality
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.10

# LangGraph for StateGraph workflows (Phase 9)
langgraph>=0.0.20
```

### Import Guide

**Pulsus LangChain Integration** (our module):
```python
# Use langchain_integration for Pulsus-specific adapters
from langchain_integration import mcp_to_langchain_tool
from langchain_integration import discover_and_convert_mcp_domains
from langchain_integration.state import PulsusState, WorkflowState
```

**Official LangChain** (external library):
```python
# Use langchain_core for official LangChain components
from langchain_core.tools import StructuredTool
from langchain_core.messages import BaseMessage

# Use langchain for high-level components
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain
```

---

## LLM Providers (Phase 3)

Support for various LLM backends:

```txt
# OpenAI
openai>=1.0.0

# Anthropic (Claude)
anthropic

# Ollama (local models)
ollama>=0.1.0
```

---

## Process Management (Phase 5)

For external console execution and process monitoring:

```txt
# Cross-platform process utilities
psutil>=5.9.0
```

---

## Templating (Phase 4)

For customizable workflow templates:

```txt
# Jinja2 template engine
jinja2>=3.1.0
```

---

## Validation (Phase 4)

For custom workflow schema validation:

```txt
# JSON Schema validation
jsonschema>=4.17.0
```

---

## HTTP & API (Phase 8)

For REST API and external integrations:

```txt
# HTTP client
httpx>=0.24.0

# FastAPI framework
fastapi>=0.100.0

# ASGI server
uvicorn>=0.23.0
```

---

## Code Quality

For development and code formatting:

```txt
# Code formatting
black>=23.0.0

# Token counting
tiktoken
```

---

## Testing

Testing framework and utilities:

```txt
# Core testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Async testing (Phase 9)
pytest-asyncio>=0.21.0

# Performance testing
pytest-benchmark>=4.0.0
```

---

## Development Dependencies

Additional tools for development (in requirements-dev.txt):

```txt
# Type checking
mypy>=1.5.0
types-requests

# Linting
ruff>=0.1.0

# Security scanning
bandit>=1.7.5
```

---

## Optional Dependencies

Optional components that can be excluded:

```txt
# UI components (if needed)
# pyQt5
```

---

## Installation

### Basic Installation

Install core dependencies only:

```bash
pip install -r requirements.txt
```

### Development Installation

Install all dependencies including dev tools:

```bash
pip install -r requirements-dev.txt
```

### Specific Phase Installation

Install dependencies for specific phases:

```bash
# Phase 2-3: LangChain + LLM
pip install langchain langchain-core langgraph openai anthropic

# Phase 4: Customization
pip install jinja2 jsonschema

# Phase 5: Process Management
pip install psutil

# Phase 8: API
pip install fastapi uvicorn httpx
```

---

## Version Constraints

### Minimum Versions

- **Python**: 3.10+ (required for modern type hints)
- **Pydantic**: 2.0+ (V2 API)
- **LangChain**: 0.1.0+ (stable API)
- **pytest**: 7.0+ (modern pytest features)

### Known Compatibility

All packages tested with:
- Python 3.11.14
- LangChain 0.1.x
- Pydantic 2.12.x

---

## Import Structure

### Module Naming

To avoid conflicts with the official `langchain` package, Pulsus uses:

- **`langchain_integration/`** - Pulsus-specific LangChain adapters
- **`langchain`** - Official LangChain library (external)

### Correct Imports

✅ **Correct:**
```python
# Pulsus integration
from langchain_integration import mcp_to_langchain_tool

# Official LangChain
from langchain_core.tools import StructuredTool
from langchain.agents import AgentExecutor
```

❌ **Incorrect:**
```python
# Don't import Pulsus tools from 'langchain'
from langchain.tool_adapter import mcp_to_langchain_tool  # WRONG!

# Don't import LangChain from 'langchain_integration'
from langchain_integration.tools import StructuredTool  # WRONG!
```

---

## Dependency Map by Phase

| Phase | Dependencies | Status |
|-------|-------------|--------|
| **Phase 0** | Python 3.10+ | ✅ Complete |
| **Phase 1** | pydantic | ✅ Complete |
| **Phase 2** | langchain-core, langchain | ✅ Complete |
| **Phase 3** | openai, anthropic, ollama | ⚠️ Ready |
| **Phase 4** | jinja2, jsonschema | ⚠️ Ready |
| **Phase 5** | psutil | ⚠️ Ready |
| **Phase 6** | (built-in) | ⚠️ Ready |
| **Phase 7** | (built-in) | ⚠️ Ready |
| **Phase 8** | fastapi, uvicorn, httpx | ⚠️ Ready |
| **Phase 9** | langgraph | ⚠️ Ready |
| **Phase 10** | pytest, mypy, ruff, bandit | ✅ Complete |

---

## Security Considerations

### Pinning Versions

For production, consider pinning exact versions:

```txt
# Instead of:
langchain>=0.1.0

# Use:
langchain==0.1.52
```

### Vulnerability Scanning

Run regular security scans:

```bash
# Using bandit
bandit -r . -ll

# Using pip-audit (if available)
pip-audit
```

### Supply Chain Security

- All packages from PyPI official repository
- Regular updates to patch vulnerabilities
- Review of new dependencies before addition

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'langchain.tool_adapter'`

**Solution**: Use correct import path:
```python
from langchain_integration.tool_adapter import mcp_to_langchain_tool
```

### Version Conflicts

**Problem**: Pydantic V1/V2 conflicts

**Solution**: Ensure Pydantic >=2.0.0:
```bash
pip install --upgrade "pydantic>=2.0.0"
```

### Missing Dependencies

**Problem**: Import errors for optional dependencies

**Solution**: Install specific phase dependencies:
```bash
pip install fastapi  # For Phase 8
pip install jinja2   # For Phase 4
```

---

## Future Dependencies

Planned additions for future phases:

```txt
# Phase 11+: Advanced features
pandas>=2.0.0         # Data analysis
numpy>=1.24.0         # Numerical computing
matplotlib>=3.7.0     # Visualization
```

---

## Minimal Installation

For minimal installation (Phase 1-2 only):

```txt
pydantic>=2.0.0
langchain-core>=0.1.0
langchain>=0.1.0
```

This supports:
- ✅ MCPBase framework
- ✅ LangChain tool conversion
- ✅ Dynamic MCP discovery
- ❌ No LLM providers
- ❌ No API server
- ❌ No workflows

---

## References

- **requirements.txt**: Full production dependencies
- **requirements-dev.txt**: Development dependencies
- **ARCHITECTURE.md**: System architecture
- **TODO.md**: Phase-by-phase implementation plan

---

**Last Updated**: November 17, 2025
**Maintainer**: Pulsus Development Team
**Status**: Production Ready
