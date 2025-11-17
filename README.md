# Pulsus MCP

**Version:** 0.1.0
**Status:** Phase 0 Complete - Ready for Phase 1 Implementation

A world-class Model Context Protocol (MCP) execution agent with LangChain workflows, external console execution, and Claude Code integration.

## Overview

Pulsus transforms natural language into executable actions through:

- **LangChain/LangGraph workflow architecture** - Professional multi-agent orchestration
- **Three-tier MCP organization** - Classic (simple), Complex (workflow-based), Customizable (config-driven)
- **External console execution** - Run software and processes in separate consoles
- **Jean-Claude agent integration** - Specialized Claude Code agents for development
- **Full observability** - SafeNet logging, metrics, and dashboards
- **Production-ready interfaces** - CLI and API for standalone and supervisor integration

## Project Structure

```
pulsus/
├── mcp/                      # MCP domain implementations
│   ├── core/                 # MCPBase, decorators, policy
│   ├── helpers/              # Repository management, script operations
│   └── tests/                # MCP-specific tests
├── routing/                  # Intent parsing and tool routing
├── workflows/                # LangChain workflow definitions
│   ├── tools/                # Workflow-based analysis tools
│   └── tests/                # Workflow integration tests
├── config/                   # Configuration and settings
├── console/                  # Console interface and session management
├── core/                     # Core utilities (compose, rankers, validators)
├── shared/                   # Shared utilities and tools
├── ui/                       # Display management
└── docs/                     # Comprehensive documentation
```

## Documentation

| Document | Purpose |
|----------|---------|
| [TODO.md](TODO.md) | High-level roadmap and progress tracking |
| [Unified Integration Plan](docs/PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md) | Complete architecture & implementation plan |
| [Framework Integration](docs/FRAMEWORK_INTEGRATION_ADDENDUM.md) | Domain framework adapter (Abu Dhabi 8-step) |

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Pulsus

# Install dependencies
pip install -e ".[dev]"
```

### Development Setup

```bash
# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy pulsus

# Run security scan
bandit -r pulsus
```

### Running Pulsus

```bash
# Start Pulsus console
python -m pulsus

# Run specific workflow
python -m pulsus execute <workflow-name>
```

## Development Roadmap

### Phase 0: Pre-Implementation ✅ COMPLETE

- [x] Architecture exploration
- [x] Unified integration plan
- [x] Framework integration addendum
- [x] Jean-Claude agents setup
- [x] Development environment setup
- [x] CI/CD skeleton

### Phase 1: Core MCP Framework (Weeks 1-4) - NEXT

- [ ] Audit current architecture
- [ ] Design and implement MCPBase class
- [ ] Implement safety decorators
- [ ] Implement SafetyPolicy system
- [ ] Create type definitions
- [ ] Write unit tests (90%+ coverage)

See [TODO.md](TODO.md) for complete roadmap (Phases 1-10 + Framework Integration).

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=pulsus --cov-report=html

# Run specific test file
pytest tests/unit/test_core.py

# Run integration tests
pytest tests/integration/
```

## Code Quality

- **Test Coverage Target:** 95%+
- **Python Version:** 3.10+
- **Linting:** Ruff
- **Type Checking:** MyPy
- **Security:** Bandit

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure all tests pass and coverage is maintained
4. Submit a pull request

## Architecture

Pulsus uses a modular architecture with clear separation of concerns:

- **Core Framework:** MCPBase, decorators, policy enforcement
- **Classic MCP Domains:** Simple, atomic operations (Tier 1)
- **Workflow MCP Domains:** Multi-step processes with LLM assistance (Tier 2)
- **Customizable Framework:** JSON-defined workflows (Tier 3)
- **External Execution:** Console manager for process control
- **Routing System:** Intent parsing and tool discovery
- **Observability:** SafeNet logging and metrics

## License

MIT

## Contact

For questions or support, see [TODO.md](TODO.md) support section.

---

**Ready to begin Phase 1 implementation!** 🚀
