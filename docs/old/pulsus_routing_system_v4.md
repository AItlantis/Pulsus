# Pulsus Routing System — v4
_Approved enhancements integrated • Last updated: 2025-10-31 11:05:21 _

This document defines the **authoritative routing specification** for Pulsus. It supersedes v3 and aligns with the updated architecture (commented edition).

---

## 0) Goals & Non‑Goals

### Goals
- **Deterministic, explainable routing** with visible scores, thresholds, and decision traces.
- **Files‑first & human‑in‑the‑loop**: discover/compose tools from the repo; promote only after approval.
- **Safe by default**: sandboxed validation with path allowlists, network=off, and bounded resources.
- **LLM‑agnostic orchestration**: use LLMs only for composition/codegen fallback when discovery cannot satisfy intent.

### Non‑Goals
- Building a generic task runner or workflow engine outside the `workflows/` conventions.
- Executing unbounded network/file operations during validation.

---

## 1) End‑to‑End Flow

```mermaid
flowchart TD
  U[User Prompt] --> P[Prompt Parser]
  P -->|ParsedIntent (domain, action, confidence)| D[Tool Discovery]
  D --> K{{One or more candidates?}}
  K -->|≥1| S[Selector / Planner]
  K -->|0| G[Generator (LLM fallback)]
  S --> V[Validation Pipeline]
  G --> V
  V --> A{{Approve?}}
  A -->|Yes| PR[Promote to workflows/domains/...]
  A -->|No| E[Edit / Relocate / Discard]
  PR --> M[Metadata JSONL + CHANGELOG.md]
  E --> S
```
All steps emit structured logs under `logs/` (see §11).

---

## 2) Data Contracts (single source of truth)

> **All shared types live in `agents/pulsus/core/types.py`.** Routing/console import from here.

```python
@dataclass
class ParsedIntent:
    domain: str | None
    action: str | None
    intent: str
    confidence: float          # 0..1

@dataclass
class ArgSpec:
    name: str
    type_hint: str | None
    required: bool
    default: str | None

@dataclass
class ToolSpec:
    path: Path                 # absolute path to tool module
    entry: str                 # 'run' or 'main'
    args: list[ArgSpec]
    doc: str
    score: float               # 0..1 after ranking

@dataclass
class RouteDecision:
    route_id: str
    policy: Literal["select","compose","generate"]
    selected: list[ToolSpec]   # empty if generate
    plan: dict | None          # composition plan DSL (see §6)
    reason: str                # human-readable summary

@dataclass
class ValidationReport:
    ok: bool
    steps: list[str]
    duration_ms: int
    artifacts: list[Path]      # paths under logs/validation/
    summary: str
```
No duplicate dataclass definitions are allowed in other modules.

---

## 3) Parser & Clarification Policy

**Module:** `agents/pulsus/routing/prompt_parser.py`

- **Hybrid approach:** keyword heuristics + optional embeddings (cosine similarity) over domain/action phrases.
- **Thresholds:**
  - If `confidence ≥ 0.55` and both `domain` and `action` are present → proceed.
  - Else → **ask exactly one targeted clarification** (e.g., “Did you mean domain=analysis or ingest?”).
  - If still unresolved → proceed with best guess and set `confidence` accordingly (to preserve momentum).
- **Outputs:** `ParsedIntent` populated with `domain`, `action`, `intent` (raw user text), and `confidence`.

---

## 4) Discovery & Candidate Construction

**Module:** `agents/pulsus/routing/tool_discovery.py`

- **Search order (paths):**
  1. `workflows/domains/{domain}/{action}/`
  2. `workflows/shared_tools/{action}/` (fallback)
- **Candidate criteria:**
  - Python module exporting `run()` or `main(**kwargs)`.
  - Docstring present (used for ranking & CLI hints).
- **Arg extraction:** via `inspect.signature` with type hints when present; docstring parsed for descriptions.
- **ToolSpec scoring features (normalized 0..1):**
  - `name_similarity` (token/Levenshtein)
  - `doc_keywords` (tf-idf style overlap with intent)
  - `history_success` (prior acceptance/low-error rate from metadata)
  - optional `embedding_similarity`
- **History boost inputs:** promotion metadata and last-success timestamps (see §10).

---

## 5) Ranking Policy & Thresholds

**Module:** `agents/pulsus/core/rankers/`

- Default weights: `name=0.40`, `doc=0.40`, `history=0.20`. Embeddings contribute into `doc` bucket if enabled.
- Selection threshold `τ = 0.60` (configurable in `settings.py`).
- **Tie-breakers:**
  1. Prefer **domain tool** over shared tool.
  2. Higher `history_success` (recent accepted promotions).
  3. Shallower path depth (simpler placement).
  4. Lexicographic by filename.

All features, weights, and `τ` are configurable and must be printed in `--explain` output.

---

## 6) Composition Planner (deterministic)

**Module:** `agents/pulsus/core/compose/`

When a single tool does not satisfy the intent but two or more partials do, **compose** a plan. The planner is deterministic and produces a small **Plan DSL**.

**Plan DSL (YAML/JSON):**
```yaml
plan:
  description: "Summarize a matrix then plot it"
  steps:
    - id: s1
      tool: summarize_matrix.py::run
      inputs: { df: "{{input.df}}" }
      outputs: { summary: "summary" }
    - id: s2
      tool: plot_matrix.py::run
      inputs: { summary: "{{steps.s1.outputs.summary}}" }
      outputs: { figure_path: "figure_path" }
io:
  params: ["df"]
  returns: ["figure_path"]
```

- **Policy:** choose composition when top-2 candidates both exceed `τ-0.05` and cover distinct sub-intents inferred from the prompt (e.g., _summarize_, _plot_).
- The planner must be able to render a **tmp module** implementing the plan, or defer to the generator if code is required beyond orchestration glue.

---

## 7) Generator Guardrails (LLM fallback)

**Module:** `agents/pulsus/core/compose/generator.py`

Used only when discovery/composition cannot satisfy the intent.
- **Template contract:**
  - File-level docstring with summary, params, returns, and side‑effects.
  - Export `run()` (or `main(**kwargs)`) with explicit args and return value.
  - Deterministic IO: no network, no filesystem writes unless explicitly allowed by policy.
- **Allowed imports (default):** `typing`, `dataclasses`, `pathlib`, `json`, `csv`, `math`, `statistics`, `re`, `datetime`, `collections`, `itertools`, `functools`, `random` (seeded), plus **provider‑optional** libs enabled in config.
- **Rejection criteria:** if generated code imports modules outside allowlist, writes outside allowed paths, lacks docstring, or fails validation → reject and surface reasons.

Generated modules are saved to `workflows/_tmp/` and identified by `route_id` for traceability.

---

## 8) Validation Pipeline (contract)

**Module:** `agents/pulsus/core/validators/` + `agents/pulsus/core/sandbox/`

**Steps and defaults (configurable):**
1. **ruff** (lint) — timeout 5s
2. **mypy** (type check) — timeout 20s
3. **import smoke** (load module, inspect callable) — timeout 3s/module
4. **dry‑run** in sandbox — timeout 30s, **network=off**, **CPU/mem caps** (1 core / 512MB default)

**Outputs:**
- Each step appends to a `ValidationReport` and writes artifacts under `logs/validation/YYYY‑MM‑DD/*.log`.
- Failure semantics:
  - If any step fails → `ok=False`, show concise summary with artifact links; keep tmp module for N days.

**Sandbox policy (defaults):**
- Allowed paths under `workflows/` (deny writes to `agents/` and repo roots).
- Network egress OFF unless allowlisted in `settings.py`.
- Resource caps enforced by the sandbox runner.

---

## 9) Shared‑Tools Precedence & Collisions

- Resolution order during selection: **domain tool > shared tool**.
- If a shared tool is shadowed by a domain tool with the same action/name, log a **warning** with both paths and chosen precedence.
- Composition may mix domain and shared tools; precedence only affects single‑selection.

---

## 10) Promotion & Metadata Semantics

On approval:

- Move tmp or composed module to:
  `workflows/domains/{domain}/{action}/{tool_name}.py`
- Update per‑domain: `workflows/domains/{domain}/CHANGELOG.md`
- Append to per‑action JSONL:
  `workflows/domains/{domain}/{action}/metadata.jsonl`

**JSONL record (canonical fields):**
```json
{{
  "id": "rev-20251031-001",
  "run_id": "run-20251031-1200-abc",
  "route_id": "route-001",
  "name": "generate_visual_summary.py",
  "domain": "analysis",
  "action": "visualise",
  "description": "Generates summary stats and a visual matrix plot",
  "status": "stable",
  "created_by": "pulsus_v4.0",
  "created_at": "2025-10-31T12:00:00+04:00",
  "version": "1.0.0",
  "tool_hash": "sha256:...",
  "tokens_estimate": 1340,
  "model": {{ "provider": "openai", "name": "gpt-4o-mini", "temperature": 0.3 }},
  "rag": {{ "enabled": true, "index": "docs_v1" }}
}}
```

**Duplicate detection policy:**
- Compute `tool_hash` (sha256) of promoted file content.
- If same `name + tool_hash` exists → **idempotent** (no new record).
- If same `name` but different hash → bump **patch** version by default.

**SemVer guidance:**
- **MAJOR**: breaking signature change (args removed/renamed) or relocation between domains/actions.
- **MINOR**: new optional args, enhanced behavior, or non‑breaking composition changes.
- **PATCH**: fixes, docstrings, or internal refactors that preserve behavior.

---

## 11) Decision Trace & Observability

**Module:** `agents/pulsus/core/telemetry/logging.py`

- Write JSONL events to:
  - `logs/app/YYYY‑MM‑DD/*.log` (app lifecycle)
  - `logs/runs/<run_id>/steps.log` (per‑run trace)
  - `logs/validation/YYYY‑MM‑DD/*.log` (validation outputs)
  - `logs/metrics/*.jsonl` (optional counters/timers)

**Required fields (minimum):**
```json
{{
  "ts": "2025-10-31T12:00:00+04:00",
  "run_id": "run-20251031-1200-abc",
  "route_id": "route-001",
  "phase": "discover",
  "candidates": 3,
  "features": ["name","doc","history"],
  "weights": {{"name":0.4,"doc":0.4,"history":0.2}},
  "top_score": 0.72,
  "policy": "compose",
  "decision": "compose s1->s2",
  "artifacts": ["logs/validation/2025-10-31/step-mypy.log"]
}}
```

**CLI summary example:**
```
[PULSUS] domain=analysis action=visualise (confidence=0.71)
[PULSUS] candidates: summarize_matrix(0.66), plot_matrix(0.63)
[PULSUS] policy=compose plan=2 steps  validation=OK  route_id=route-001
```

---

## 12) CLI Modes & Flags

- `--dry-run` — execute full routing + validation, **stop before promotion**.
- `--non-interactive` — auto‑approve **only** when:
  - `confidence ≥ 0.55` and
  - selected tool(s) all have `score ≥ τ` and
  - validation `ok=True`. Otherwise exit non‑zero.
- `--explain` — print ranking features, weights, scores, and tie‑breakers.
- `--plan` — print composition plan DSL (no execution).
- `--cache/--no-cache` — enable/disable discovery cache (see §13).
- `--rag/--no-rag` — toggle RAG augmentation (see §14).

Behavior matrix (excerpt):
```
Flag combo                 | Parse | Discover | Validate | Promote | Output
-------------------------- | ----- | -------- | -------- | ------- | -----------------------------
--dry-run                  | Yes   | Yes      | Yes      | No      | Validation report + plan
--non-interactive          | Yes   | Yes      | Yes      | Auto    | Summary or non-zero exit
--explain                  | Yes   | Yes      | (if run) | (n/a)   | Feature/weight/score details
--plan                     | Yes   | Yes      | No       | No      | Plan DSL only
```

---

## 13) Warm Discovery Index & Caching (optional)

- Maintain an in‑memory + on‑disk cache of discovery results keyed by path mtimes and file hashes.
- **Invalidation triggers:** file create/delete/modify in `workflows/` paths, or settings that affect ranking.
- Expose `--cache/--no-cache` flags to toggle; default **on**.

---

## 14) RAG Augmentation over Tool Docs (optional)

- If enabled, build a small vector index over:
  - tool docstrings
  - `docs/` and `ADRs/`
  - `workflows/domains/**/README.md` (if present)
- Use retrieval results only as **hints** to parser & composition planner; do not bypass thresholds or safety policies.
- Privacy note: index remains local to the repo; no external calls unless explicitly configured.

---

## 15) Plugin / Manifest Interface (optional)

Allow tools to ship a manifest (no import needed) to improve discovery ranking.

**Manifest (`tool.yaml` or `tool.toml`) schema (minimal):**
```yaml
name: "summarize_matrix"
intents: ["summarize", "statistics", "matrix"]
args:
  - name: df
    type: "DataFrame"
    required: true
returns: ["summary"]
hints:
  domain: "analysis"
  action: "summarise"
  anti_intents: ["plot", "visualise"]
```

**Discovery order:**
1. Python introspection (source of truth for runtime).
2. Manifest (ranking hints only).

---

## 16) Error Handling & Retention

- On validation failure: keep tmp module in `workflows/_tmp/` and logs in `logs/validation/DATE/`.
- On user rejection: retain tmp for `retention_days` (default 7); offer regenerate/debug next run.
- All retention controlled by `settings.log.retention_days` and `settings.tmp.retention_days`.

---

## 17) Security & Sandboxing Defaults

- Operate strictly under `workflows_root` allowlist.
- Network egress OFF by default; enable per‑run or per‑tool allowlist if required.
- Sandbox resource caps: 1 CPU, 512MB RAM, 30s per dry‑run (defaults).
- Never write into `agents/` during runtime.

---

## 18) Testing Strategy

- **Unit:** parser, discovery, rankers, validators, sandbox policy.
- **Integration:** end‑to‑end routing (select, compose, generate) against fixtures.
- **Golden:** CLI transcripts for typical flows and error cases.
- **CI:** upload `logs/validation/**/*` artifacts on failure; run on Python 3.11/3.12.

---

## 19) Examples

### 19.1 Single‑selection (happy path)
```
[PULSUS] domain=analysis action=summarise (0.78)
[PULSUS] select summarize_matrix.py::run score=0.74  τ=0.60
[PULSUS] validation OK (ruff,mypy,import,dry‑run=2.1s)
[PULSUS] promote → workflows/domains/analysis/summarise/summarize_matrix.py
[PULSUS] revision=rev-20251031-007 route_id=route-002
```

### 19.2 Composition (two‑step)
```
[PULSUS] domain=analysis action=visualise (0.71)
[PULSUS] candidates: summarize_matrix(0.66), plot_matrix(0.63)
[PULSUS] compose plan=2 steps  validation OK
[PULSUS] promote → workflows/domains/analysis/visualise/generate_visual_summary.py
```

### 19.3 Generator fallback (guardrails enforced)
```
[PULSUS] No candidates above threshold; falling back to generator (allowlist: stdlib)
[PULSUS] validation FAILED: mypy errors; see logs/validation/2025-10-31/gen-001-mypy.log
```

---

## 20) Configuration (selected keys)

```python
class Settings(BaseSettings):
    workflows_root: Path = Path("workflows")
    log_dir: Path = Path("logs")
    tmp_dirname: str = "_tmp"
    retention_days: int = 7

    model: ModelConfig = ModelConfig(provider="openai", name="gpt-4o-mini", temperature=0.3)
    embeddings_enabled: bool = False

    ranker: RankerConfig = RankerConfig(threshold=0.60, weights={"name":0.4,"doc":0.4,"history":0.2})
    sandbox: SandboxConfig = SandboxConfig(max_seconds=30, max_mem_mb=512, network="off")
    cache_enabled: bool = True
    rag_enabled: bool = False
```
All thresholds and policies are overridable in `config/settings.py`.

---

## 21) Compliance Checklist (quick audit)

- [ ] Uses `core/types.py` only for shared types.
- [ ] Uses `logs/app`, `logs/runs`, `logs/validation`, `logs/metrics` only (no `_tmp_logs/`).
- [ ] Enforces precedence: **domain > shared** (warn on shadow).
- [ ] Documents `τ`, weights, and tie‑breakers.
- [ ] Enforces one‑question clarification policy.
- [ ] Generator respects allowlist & template; rejects on violations.
- [ ] Validation pipeline (ruff → mypy → import → dry‑run) with timeouts & sandbox.
- [ ] Promotion writes JSONL + CHANGELOG; duplicate detection by `name+hash`.
- [ ] CLI flags `--dry-run --non-interactive --explain --plan --cache --rag` implemented.
- [ ] Caching, RAG, and Manifest interfaces are optional and clearly toggled.

---

**This v4 spec is implementation‑ready.** It aligns with the commented architecture and provides concrete thresholds, policies, and contracts to guide engineering and reviews.