# Pulsus Architecture

## Overview

Pulsus is a **console‑first routing agent** that interprets natural‑language requests, discovers or composes domain/action‑scoped tools, validates them, and (with approval) **promotes** them into a stable, versioned toolbox. The design is *files‑first*, *LLM‑agnostic*, and *human‑in‑the‑loop* with safe defaults.

This document maps the implementation to the requested code structure and enumerates responsibilities, interfaces, and chosen technologies.

## Design Principles
- **Deterministic & explainable:** visible ranking scores, thresholds, and logs.
- **Files‑first:** code, prompts, and metadata live in the repo for auditability.
- **Human‑in‑the‑loop:** explicit approvals before promotion.
- **Safe by default:** path allowlists, no network by default, time/memory caps.
- **Composable:** select best tool or compose multiple; generate only as a last resort.
---

## Technology Choices

- **Language**: Python 3.11+
- **CLI**: [Typer] for the entry command, with [Rich] for colorized console output.
- **Config & Schema**: [Pydantic] (v2) and `pydantic-settings` for typed settings; JSON Schema for metadata.
- **Prompting**: Optional [LangChain] wrappers around the configured LLM; prompts live in repo for auditability.
- **Discovery**: `importlib`, `inspect`, and `ast` to locate functions, read signatures/docstrings, and rank candidates.
- **Embeddings (optional)**: `sentence-transformers` (local) or provider embeddings for semantic domain/action detection.
- **Validation**: Static checks (ruff/flake8, mypy), plus dry-run hooks; **SafeNet** sandbox (future) for execution isolation.
- **Observability**: `structlog` for JSON logs; optional OpenTelemetry exporter.
- **Testing**: pytest; golden transcripts for console I/O.
- **Packaging**: uv/poetry; pinned lockfile for reproducibility.

> Swap libraries freely; the architecture keeps seams and interfaces stable.

---

## Directory Structure (Authoritative)

```
agents/                               # All importable Python packages
  pulsus/                             # Pulsus package (stable API surface)
    __init__.py
    console/                          # CLI & REPL UX (Typer + Rich)
      __init__.py
      interface.py                    # CLI entry; prompts, confirmations, output blocks
      session_manager.py              # Tracks session context, last decisions, run ids
    config/                           # Typed settings + metadata schemas
      __init__.py
      settings.py                     # Model/provider, paths, thresholds, retention
      metadata_schema.py              # Pydantic/JSON Schema for promotions
    routing/                          # Text → (domain, action) → candidates → decision
      __init__.py
      router.py                       # Orchestration: parse→discover→(select|compose|generate)→validate→approve→promote
      prompt_parser.py                # Heuristics + optional embeddings → ParsedIntent
      tool_discovery.py               # Find & score callable tools (run/main)
    ui/                               # Console visualization helpers
      __init__.py
      display_manager.py              # Tables/panels/diffs (Rich)
      progress_bar.py                 # Spinners/progress for long steps
    core/                             # Cross‑cutting engine (pure logic; no CLI)
      __init__.py
      types.py                        # ParsedIntent, ToolSpec, ArgSpec, ValidationReport, RouteDecision, RunContext
      rankers/                        # Feature extraction & scoring
        __init__.py
        features.py                   # Name/docstring/embedding features
        scorer.py                     # Weighted score; configurable thresholds
      compose/                        # Selection, composition planning, codegen fallback
        __init__.py
        selector.py                   # Top‑1 if score≥τ; otherwise consider compose
        composer.py                   # Chain tools to satisfy intent
        generator.py                  # LLM synthesis when discovery fails
      validators/                     # Static & runtime validation
        __init__.py
        ruff_runner.py                # Lint step
        mypy_runner.py                # Type‑check step
        unit_runner.py                # Smoke imports / optional unit hooks
      sandbox/                        # Execution safety boundaries
        __init__.py
        policy.py                     # Path allowlist, no‑network default, resource caps
        runner.py                     # Timed dry‑run executor
      telemetry/                      # Logs/traces/metrics
        __init__.py
        logging.py                    # structlog JSON; correlation IDs
        otel_exporter.py              # Optional OpenTelemetry exporter
      storage/                        # Filesystem & metadata helpers
        __init__.py
        fs.py                         # Safe FS ops; tmp retention
        metadata_store.py             # JSONL append/read for promotions
        changelog.py                  # Per‑domain CHANGELOG helpers
    tests/                                # Test suite (pytest)
      unit/                               # Parser, discovery, ranker, validator unit tests
      integration/                        # End‑to‑end routing flows
      golden/                             # Console transcripts for UX regression
        transcripts/
      fixtures/                           # Sample workflows tree & data

    docs/                                 # Project documentation
      README.md
      pulsus_architecture.md              # (this file)
      pulsus_routing_system_v3.md         # Implementation‑ready routing spec
      ADRs/                               # Architecture Decision Records

    logs/                                 # Runtime and validation logs (JSON lines)
      app/YYYY-MM-DD/*.log                # Application logs
      runs/<run_id>/steps.log             # Per‑run trace; route→tmp→promotion
      validation/YYYY-MM-DD/*.log         # ruff/mypy/import outputs; dry‑run logs
      metrics/*.jsonl                     # Optional metrics/telemetry
workflows/                            # DEPRECATED: Old location - now inside agents/pulsus/

agents/pulsus/workflows/              # Pulsus agent workflows & temporary modules
  domains/                            # Domain‑scoped workflow definitions
    <domain>/
      <action>/
        *.json                        # Workflow definitions
  shared_tools/                       # Agent-specific shared utilities & MCP tools
  route_tmp/                          # Ephemeral generated modules (auto‑cleaned)
    tmp_generated_*.py                # LLM fallback modules

framework/                            # USER-DEFINED TOOLS (configured in settings)
  *.py                                # User's custom tools exposing __domain__, __action__
                                      # These are discovered by tool_discovery.py
                                      # Separate from agent's internal workflows

```

### Directory Organization Philosophy

**`framework/`** (user space):
- User-defined tools and functions
- Discovered by `tool_discovery.py`
- Configured via `PULSUS_FRAMEWORK_ROOT` environment variable
- User maintains their own tools here

**`agents/pulsus/workflows/`** (agent space):
- Agent's internal workflow definitions
- MCP integrations for agent operations
- Temporary generated modules in `route_tmp/`
- Managed by Pulsus itself

This separation ensures clean boundaries between:
1. User's custom tools (framework)
2. Agent's internal operations (workflows)
3. Temporary generated code (workflows/route_tmp)

```

---

## Module-by-Module Responsibilities & Interfaces

### `console/`
**`interface.py`**
- Exposes `run_console()` entrypoint (Typer).
- Standardizes the `[PULSUS]` prompt and confirmation dialogs.
- Contracts:
  - `def ask_confirmation(msg: str) -> bool`
  - `def ask_text(prompt: str, default: str | None = None) -> str`
  - `def print_block(title: str, body: str) -> None`

**`session_manager.py`**
- Tracks transient state (current domain/action, tmp paths, last suggestions).
- Persists a session log; exposes checkpoint/rewind stubs for future LLM session recovery.

### `config/`
**`settings.py`**
- Typed settings with env/file merging.
- Key fields (suggested):
  - `workflows_root: Path = Path('workflows')`
  - `domains_dir: str = 'domains'`
  - `shared_tools_dir: str = 'shared_tools'`
  - `tmp_dirname: str = '_tmp'`
  - `log_dir: Path = Path('logs')`
  - `retention_days: int = 7`
  - `model: ModelConfig` (provider, name, temperature, max_tokens)
  - `rag: RagConfig` (enabled, index_path, provider)

**`metadata_schema.py`**
- JSON Schema + Pydantic model for promoted tool records:
  - `name`, `domain`, `action`, `description`, `status`
  - provenance: `created_by`, `created_at`, `version`, `revision_id`
  - LLM params and `tokens_estimate`
  - `rag` settings if used

### `routing/`
**`prompt_parser.py`**
- Hybrid parsing: keyword heuristics + optional embedding classifier.
- API:
  - `def parse(text: str) -> ParsedIntent`
  - `ParsedIntent(domain: str | None, action: str | None, intent: str, confidence: float)`

**`tool_discovery.py`**
- Traverses `workflows/domains/<domain>/<action>/` and `workflows/shared_tools/<action>/`.
- Extracts **callable candidates**:
  - Python function `main(**kwargs)` or module-level `run()` convention.
  - Reads docstring for description and expected args.
- API:
  - `def discover(domain: str, action: str) -> list[ToolSpec]`
  - `ToolSpec(path: Path, entry: str, args: list[ArgSpec], doc: str, score: float)`

**`router.py`**
- Orchestrates: `parse → discover → rank → (compose|generate) → validate → approve → promote`.
- Rankers consider: name similarity, docstring keywords, past success (metadata), and parser confidence.
- Promotion writes metadata and updates `CHANGELOG.md` per domain.
- API:
  - `def route(request: str) -> RouteDecision`
  - `def promote(tmp_path: Path, target_name: str, meta: dict) -> Path`

### `ui/`
**`display_manager.py`**
- Uniform blocks: suggestions, diffs, logs; wraps Rich for tables and panels.

**`progress_bar.py`**
- Optional spinner/progress for discovery, validation, and execution.

### `core/`
**`types.py`**
- Central dataclasses and type aliases shared across routing and console:
  - `ParsedIntent`, `ToolSpec`, `ArgSpec`, `RouteDecision`, `ValidationReport`, `RunContext`.

**`rankers/`**
- Feature extraction and weighted scoring rules; thresholds configurable from `settings.py`.
- Expose `score_tool(intent, tools) -> list[ToolSpec]`.

**`compose/`**
- Selection policy (`top-1 if score≥τ`) and composition planner when multiple partials match intent.
- LLM `generator.py` emits tmp modules only when discovery fails.

**`validators/`**
- `ruff_runner`/`mypy_runner`/`unit_runner` with consistent result objects and timeouts.

**`sandbox/`**
- Enforces path allowlist (`workflows/`), network off by default, CPU/mem caps, and max runtime during validation.

**`telemetry/`**
- `logging.py` initializes structlog with JSON lines, correlation IDs, and writes to `logs/`.
- `otel_exporter.py` ships traces/metrics when enabled.

**`storage/`**
- File-safe ops, JSONL metadata append/read, and domain `CHANGELOG.md` helpers.

---

## Data Contracts (selected)

```python
# core/types.py
@dataclass
class ParsedIntent:
    domain: str | None
    action: str | None
    intent: str
    confidence: float

@dataclass
class ArgSpec:
    name: str
    type_hint: str | None
    required: bool
    default: str | None

@dataclass
class ToolSpec:
    path: Path
    entry: str
    args: list[ArgSpec]
    doc: str
    score: float

@dataclass
class ValidationReport:
    ok: bool
    steps: list[str]
    duration_ms: int
    artifacts: list[Path]  # log files written under logs/validation/
```

---

## Execution Flow (Happy Path)
1. **User prompt** → `console.interface` captures text.
2. **Parse** → `routing.prompt_parser.parse()` returns `(domain, action, confidence)`.
3. **Discover** → `routing.tool_discovery.discover()` returns ranked `ToolSpec`s.
4. **Select/Compose** → choose best tool(s) or compose a tmp module (LLM optional).
5. **Validate** → static checks + sandboxed dry run. All logs land under `logs/validation/YYYY-MM-DD/`.
6. **User Approval** → console prompts for rename/relocate.
7. **Promote** → `router.promote()` writes file, metadata JSONL, and domain changelog.

---

## Logging & Retention
- All app logs are **JSON lines** in `logs/app/YYYY-MM-DD/`.
- Per-run traces live in `logs/runs/<run_id>/steps.log` and are correlated to metadata via `revision_id` and `route_id`.
- Validation output goes to `logs/validation/YYYY-MM-DD/`.
- Retention controlled by `settings.log.retention_days` (default: 7). A cleanup job purges old logs and tmp artifacts.

---

## Testing Strategy
- **Unit**: focused tests for parser, discovery, rankers, validators (mocks for filesystem/LLM).
- **Integration**: end-to-end against `tests/fixtures/workflows/` tree.
- **Golden**: console transcripts captured under `tests/golden/transcripts/` with review diffs.
- **CI**: pre-commit (ruff/mypy/black), GitHub Actions for unit+integration on 3.11/3.12.

---

## Documentation
- `docs/` houses architecture, the routing v3 spec, ADRs, and contributor docs.
- Keep prompts, thresholds, and ranker weights documented for auditability.

---

## Future Work
- UI polish (candidate selection TUI), learning-to-rank, RAG over tool docs, VSCode integration.