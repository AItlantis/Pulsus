# TODO — Pulsus (Architecture + Routing v4)
_Last updated: 2025-10-31 11:08:05 _

Authoritative references:
- **Architecture:** `docs/pulsus_architecture.md` (commented edition)
- **Routing Spec:** `docs/pulsus_routing_system.md` (v4)

Priority tags: **P0 = must**, **P1 = should**, **P2 = nice‑to‑have**

---

## P0 — Must (v4 compliance)

### Core Types & Contracts
- [ ] **Unify shared types in `core/types.py`**: `ParsedIntent`, `ArgSpec`, `ToolSpec`, `RouteDecision`, `ValidationReport`, `RunContext`.  
      _Refs: Architecture §Folder Commentary → core/types; Routing v4 §2_
- [ ] Remove any duplicate dataclass definitions across routing/console.  
      _Ref: Routing v4 §2_

### Parser & Clarification
- [ ] Implement hybrid parser (heuristics + optional embeddings).  
      _Ref: Routing v4 §3_
- [ ] Enforce **clarification policy**: ask **one** targeted question if `confidence < 0.55` or missing domain/action.  
      _Ref: Routing v4 §3_
- [ ] Add parser property‑based tests for ambiguity handling.  
      _Ref: Routing v4 §18_

### Discovery & Ranking
- [ ] Implement discovery paths order: `domains/{domain}/{action}` then `shared_tools/{action}`.  
      _Ref: Routing v4 §4, §9_
- [ ] Implement rankers with default weights `name=0.40, doc=0.40, history=0.20` and threshold **τ=0.60**.  
      _Ref: Routing v4 §5_
- [ ] Implement tie‑breakers: domain > shared, higher history, shallower path, lexicographic.  
      _Ref: Routing v4 §5_

### Selector / Composition / Generator
- [ ] Implement **composition planner** and **Plan DSL**; choose compose when top‑2 ≥ (τ−0.05) and cover distinct sub‑intents.  
      _Ref: Routing v4 §6_
- [ ] Implement **generator guardrails**: template, allowlist imports, deterministic IO, rejection criteria.  
      _Ref: Routing v4 §7_

### Validation Pipeline & Sandbox
- [ ] Wire validation steps: **ruff → mypy → import smoke → sandbox dry‑run** with timeouts.  
      _Ref: Routing v4 §8_
- [ ] Enforce sandbox policy: path allowlist under `workflows/`, network=off, caps (1 CPU / 512MB / 30s).  
      _Ref: Routing v4 §8, §17_
- [ ] Emit `ValidationReport` with artifact paths in `logs/validation/YYYY‑MM‑DD/`.  
      _Ref: Routing v4 §8_

### Promotion & Metadata
- [ ] Move approved tool to `workflows/domains/{domain}/{action}/{tool_name}.py`.  
      _Ref: Routing v4 §10_
- [ ] Update per‑domain `CHANGELOG.md`; append JSONL record to per‑action `metadata.jsonl`.  
      _Ref: Routing v4 §10_
- [ ] Implement duplicate detection by **name + sha256(file)**; SemVer bump rules (MAJOR/MINOR/PATCH).  
      _Ref: Routing v4 §10_

### Precedence & Collisions
- [ ] Enforce **domain > shared** precedence and warn on shadowing.  
      _Ref: Routing v4 §9_

### Logging & CLI
- [ ] Write JSONL logs to `logs/app`, `logs/runs/<run_id>`, `logs/validation`, `logs/metrics`.  
      _Ref: Architecture §logs; Routing v4 §11_
- [ ] CLI summary line includes: domain, action, confidence, candidates, policy, validation status, `route_id`.  
      _Ref: Routing v4 §11_

---

## P1 — Should

### CLI Modes & Flags
- [ ] Implement flags: `--dry-run`, `--non-interactive`, `--explain`, `--plan`, `--cache/--no-cache`, `--rag/--no-rag`.  
      _Ref: Routing v4 §12_
- [ ] Behavior matrix adherence (auto‑approve policy for `--non-interactive`).  
      _Ref: Routing v4 §12_

### Observability
- [ ] Decision trace fields in logs: `run_id`, `route_id`, `phase`, `features`, `weights`, `top_score`, `policy`, `decision`, `artifacts`.  
      _Ref: Routing v4 §11_

### Tests & CI
- [ ] **Unit tests** for parser, discovery, rankers, validators, sandbox.  
- [ ] **Integration tests** for select/compose/generate flows (fixtures under `tests/fixtures/workflows/`).  
- [ ] **Golden transcripts** for CLI UX.  
- [ ] CI uploads `logs/validation/**/*` on failure; Python 3.11/3.12 matrix.  
      _Ref: Routing v4 §18_

### Docs & ADRs
- [ ] ADR: **Ranking Policy & Thresholds** (weights, τ, tie‑breakers).  
- [ ] ADR: **Validation Pipeline** (steps, timeouts, artifacts).  
- [ ] ADR: **Generator Guardrails** (allowlist, template, rejection).  
      _Ref: Architecture §docs; Routing v4 §§5–8_

---

## P2 — Nice‑to‑have

### Discovery Cache
- [ ] Warm discovery index + on‑disk cache; invalidate on file mtime/hash changes. Toggle with `--cache`.  
      _Ref: Routing v4 §13_

### RAG Augmentation
- [ ] Optional vector index over docstrings/ADRs/READMEs; hints only (no policy bypass).  
      _Ref: Routing v4 §14_

### Plugin / Manifest
- [ ] Optional `tool.yaml`/`tool.toml` manifest schema; use for discovery hints (intents, args).  
      _Ref: Routing v4 §15_

---

## Cross‑Cutting Acceptance Checks

- [ ] **No `_tmp_logs/`** references remain; only `logs/app`, `logs/runs`, `logs/validation`, `logs/metrics` used.
- [ ] All thresholds & policies configurable in `config/settings.py`.
- [ ] Console uses `ui/display_manager` for tables/panels; consistent `[PULSUS]` prompts.
- [ ] Sandbox denies writes outside `workflows_root`; never writes under `agents/` at runtime.
- [ ] Promotion path tests verify idempotency and SemVer rules.
- [ ] Telemetry logs include correlation IDs and surface artifact links in CLI summaries.

---

## Execution Order (suggested)

1) **Config & Core Types** → `config/settings.py`, `core/types.py`  
2) **Discovery & Rankers** → `routing/tool_discovery.py`, `core/rankers/*`  
3) **Parser & Clarification** → `routing/prompt_parser.py`  
4) **Selector/Compose/Generate** → `core/compose/*`, `routing/router.py`  
5) **Validators & Sandbox** → `core/validators/*`, `core/sandbox/*`  
6) **Promotion & Metadata** → `core/storage/*`  
7) **CLI & UI** → `console/interface.py`, `ui/*` + flags/modes  
8) **Observability & CI** → `core/telemetry/*`, GitHub Actions, golden tests  
9) **Optional** → Cache, RAG, Manifest

---

## Links
- `docs/pulsus_architecture.md`
- `docs/pulsus_routing_system.md` (v4)