
# MCP–PULSUS Integration — Advanced TODO
**Version:** 2025-11-09  
**Purpose:** A deep, production-ready roadmap and specification to transform Pulsus into a modular, autonomous agent platform where **every action** is formalized through MCP (Model Context Protocol). This document is intended to be used as both a developer guide and a specification for implementation, testing, and compliance.

---

## Overview & Principles

**Core principles**
- **Single contract**: every action returns an `MCPResponse` and is decorated with safety metadata.
- **Plan-driven autonomy**: agents create, propose, and execute Plans; users approve write operations.
- **Observability & traceability**: SafeNet logging, diffs, hashes, and full plan history stored in `MCPRegistry`.
- **Reversibility**: transactional operations must supply rollback hooks.
- **Composability**: workflows combine MCP actions, external processes, and custom scripts seamlessly.
- **Learning loop**: store feedback and adapt approval defaults and recommendations over time.

---

## Contents
1. Core contracts and models
2. System components and responsibilities
3. Control flow (detailed state machine)
4. Safety model & decorators
5. Execution engine & external process management
6. Plan proposal, approval UX, and UI payloads
7. Review, validation, and confidence scoring
8. Rollback, transactions, and constraints
9. Introspection, docs, and registry
10. Testing strategy & migration checklist
11. Sample API stubs and JSON examples
12. Implementation timeline & milestones

---

# 1. Core Contracts & Data Models

All types below are canonical. Use `pydantic` or `attrs` in production.

```python
from enum import Enum
from typing import Any, Dict, List, Optional

class SafetyLevel(str, Enum):
    READ_ONLY = "read_only"
    WRITE_SAFE = "write_safe"
    RESTRICTED_WRITE = "restricted_write"

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class MCPResponse(BaseModel):
    success: bool
    context: Dict[str, Any] = {}
    data: Any = None
    error: Optional[str] = None
    trace: List[str] = []

class MCPActionSpec(BaseModel):
    name: str                    # "ScriptManager.read_script"
    mcp_class: str               # "ScriptManager"
    mcp_method: str              # "read_script"
    params: Dict[str, Any] = {}
    safety: SafetyLevel
    description: Optional[str] = None
    transactional: bool = False  # whether rollback hooks exist
```

`Plan` model:

```python
class Plan(BaseModel):
    id: str
    title: str
    author: str
    steps: List[MCPActionSpec]
    summary: str
    created_at: datetime
    dry_run: bool = True
    metadata: Dict[str, Any] = {}
```

---

# 2. System Components & Responsibilities

- **MCPBase (core)**: base class with `execute()` helper, rollback stack, register_rollback, and helper utils to produce `MCPResponse`.
- **MCPRegistry**: dynamic registry of MCP classes/methods; stores method metadata, versioning, and historical plan artifacts.
- **MCPRouter / Planner**: intent parsing, candidate discovery, plan generation (single or multi-step), and alternative proposals.
- **MCPExecutor**: executes plans with approval checks, transactional rollback management, and SafeNet logging.
- **ExternalProcessManager**: validated, sandboxed process runner with streaming, timeouts, resource limits, and artifact manifests.
- **AutoReviewer**: post-execution checks (lint, typecheck, smoke tests, schema validation) and confidence scoring.
- **UI Approval Manager**: produces plan preview payloads, diffs, and collects mapped per-step approvals.
- **SafeNet Logger**: structured logging (JSONL or SQLite) for plan lifecycle, step events, diffs and hashes.
- **Learning & Policy Engine**: aggregates user approvals/feedback to suggest default approvals and detect unsafe patterns.

---

# 3. Control Flow & State Machine (detailed)

Plan lifecycle states:
```
DRAFT -> PROPOSED -> APPROVED -> EXECUTING -> REVIEWING -> COMPLETED | FAILED | ROLLBACK_COMPLETED
```

Transitions:
- `DRAFT -> PROPOSED`: Planner finalizes a plan and computes impact analysis (diffs, artifacts, affected files).
- `PROPOSED -> APPROVED`: User accepts plan (whole or stepwise). Approval metadata persists in `MCPRegistry`.
- `APPROVED -> EXECUTING`: Executor runs steps sequentially; each step recorded; approval passed into MCP calls.
- `EXECUTING -> REVIEWING`: After execution, AutoReviewer runs validations.
- `REVIEWING -> COMPLETED`: If confidence >= threshold and no critical failures.
- `REVIEWING -> FAILED`: If tests/lint/validations fail and rollback not performed.
- `FAILED -> ROLLBACK_COMPLETED`: If rollback succeeds. All outcomes logged.

Key invariants:
- No WRITE_SAFE or RESTRICTED_WRITE step executes without explicit approval recorded.
- Executor aborts on first critical failure unless plan marked `continue_on_failure` with allowed side effects.
- Rollbacks run in reverse order of successful transactional steps.

---

# 4. Safety Model & Decorators

Decorators live in `agents/mcp/core/decorators.py` and include:
- `@read_only`
- `@write_safe` (interacts with UI approval checkpoint)
- `@restricted_write` (additional type/target validation required)
- `@transactional` (registers rollback intent)
- `@cached(ttl=...)`

`@require_approval` wrapper behavior:
- at runtime, Executor calls MCP methods with `__approval__=True` for steps the user approved. Without approval decorator returns an `MCPResponse(success=False, error="Approval required")`.

Type validation and command allowlists are enforced by `SafetyPolicy` with pluggable rules per domain.

---

# 5. Execution Engine & External Process Management

**MCPExecutor features**
- Sequential step execution with per-step timeouts
- Support synchronous and async MCP methods
- Map exceptions to `MCPResponse` with `trace` filled
- Register rollbacks when a transactional step starts successfully
- Support `continue_on_failure` granular flag per plan/step
- Emit SafeNet events for UI streaming

**ExternalProcessManager** minimal API
```python
class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    artifacts: List[{"path":str,"hash":str,"size":int}]
    allowed: bool  # true if command passed allowlist
```

Security measures:
- Validate commands against domain allowlist and denylist
- Sanitize environment variables, disallow secret passthrough
- Use resource limits (ulimit) and timeouts
- Prefer container/chroot for heavy tasks

---

# 6. Plan Proposal, Approval UX, & UI Payloads

**Proposal payload (sent to UI):**
```json
{
  "plan_id": "plan-abc",
  "title": "Generate docs and update README",
  "summary": "Analyze scripts, generate docstrings, update README.md",
  "steps":[
    {"idx":0, "action":"ScriptManager.read_script", "safety":"read_only", "summary":"Analyze script.py", "diff_preview": null},
    {"idx":1, "action":"ScriptManager.write_docstring", "safety":"write_safe", "summary":"Add docstrings", "diff_preview":"--- before\n+++ after\n@@ ... "}
  ],
  "estimated_side_effects":[ "README.md modified", "files created: docs/script.md" ],
  "approve_options": ["approve_all","approve_per_step","dry_run_only"]
}
```

UI should support:
- Per-step diffs (unified diff or summary)
- Approve step / Approve all / Reject
- Toggle for allowing external processes and resource limits
- Option to store approval as preference for future plans (configurable)

---

# 7. Review, Validation & Confidence Scoring

AutoReviewer runs checks and produces `MCPReviewResponse`:
- Lint (ruff) status
- Typecheck (mypy) status
- Import smoke test (module importability)
- Unit/smoke tests results (if provided)
- Artifact integrity (hashes, sizes)
- Behavior validation (schema, ranges)
- Score aggregation: weighted metric -> confidence in [0.0,1.0]

If confidence < threshold, agent must either propose corrective Plan or ask user to rollback.

---

# 8. Rollback, Transactions, & Constraints

Rollback rules:
- Transactional steps must register rollback functions: file backups, restore DB snapshots, remove artifacts.
- Rollbacks executed in LIFO for steps that succeeded and registered hooks.
- If rollback fails, mark plan as `ROLLBACK_FAILED` and surface manual remediation steps in UI.

Constraints (defaults, tunable in config):
- `max_steps_per_plan = 20`
- `default_timeout_per_step = 30s`
- `max_artifact_size = 200MB`
- `denylist_commands = ["rm -rf /", "docker", "ssh"]`
- `blocked_modules = ["subprocess", "os.system", "eval", "exec"]` for code executed by the sandboxed runners

---

# 9. Introspection, Docs & Registry

**MCPRegistry responsibilities:**
- Auto-discover MCP classes & methods at startup
- Maintain metadata: safety, description, parameters, version
- Record plan history & approvals
- Provide introspection API for LLM and UI:
  - `list_domains()`, `list_methods(domain)`, `get_method_info(cls, method)`

**Docs generator:**
- Extract docstrings + decorator metadata to produce `MCP_<Class>.md` with examples and safety tags.
- Place docs into `agents/mcp/docs/` and index in startup capabilities display.

---

# 10. Testing Strategy & Migration Checklist

**Unit tests**
- Decorator behavior & approval enforcement
- MCPExecutor step lifecycle, rollback stack
- ExternalProcessManager allowlist/denylist behavior

**Integration tests**
- Full Plan lifecycle: propose → approve → execute → review → complete
- Failure scenarios: mid-plan failure + rollback
- External process heavy task + artifact verification

**E2E tests**
- Simulated user with default preferences and with strict approval policy
- Multi-agent cross-validation (Pulse + Shell)

**Migration checklist (minimal):**
- Implement rollback hooks in MCPBase
- Provide `MCPExecutor.execute_plan` and tests
- Integrate ExternalProcessManager and safety policy
- Update `MCPRouter` to emit Plan objects, not raw tool calls
- Update UI to accept Plan payloads and send approvals
- Auto-generate docs for all MCP classes
- Add telemetry & SafeNet logging

---

# 11. Minimal API Stubs & Examples

## MCPExecutor.execute_plan (conceptual)
```python
def execute_plan(plan: Plan, approvals: Dict[int,bool], continue_on_failure=False):
    for idx, step in enumerate(plan.steps):
        if step.safety != SafetyLevel.READ_ONLY and not approvals.get(idx):
            raise PermissionError("Approval missing for step {}".format(idx))
        # run step (MCP call or external process)
        resp = invoke_step(step, approval=approvals.get(idx, False))
        if not resp.success and not continue_on_failure:
            run_rollbacks()
            return {"status":"failed", "step": idx, "response": resp}
    # after all steps
    review = autoview_and_review(plan)
    return {"status":"completed", "review": review}
```

## Workflow JSON binding to MCP class/method
```json
{
  "id":"analyze_screenlines",
  "domain":"analysis",
  "action":"get_screenlines",
  "mcp_class":"ModelInspector",
  "mcp_method":"get_screenlines",
  "steps":[
    {"tool":"ModelInspector.get_screenlines","params":{"group_name":"${input.group}"}}
  ]
}
```

---

# 12. Implementation Timeline & Milestones (suggested)

**Sprint 0 (1 week)**: Core contracts, MCPBase, decorators, registry skeleton.  
**Sprint 1 (2 weeks)**: Implement ScriptManager, RepositoryManager, unit tests.  
**Sprint 2 (2 weeks)**: MCPExecutor, Planner refactor, Plan model.  
**Sprint 3 (2 weeks)**: ExternalProcessManager, AutoReviewer.  
**Sprint 4 (2 weeks)**: UI integration (Plan preview + approvals), SafeNet panel.  
**Sprint 5 (2 weeks)**: Docs generation, registry introspection, migration.  
**Sprint 6 (ongoing)**: Learning engine and multi-agent support, hardening, performance.

---

# Appendix A — Quick Reference: Filenames & Endpoints

```
agents/mcp/core/
  base.py
  decorators.py
  logger.py
  policy.py
  registry.py

agents/mcp/helpers/
  script_manager.py
  model_inspector.py
  layer_manager.py
  data_analyzer.py
  repository_manager.py

agents/pulsus/
  routing/mcp_router.py
  workflows/definitions/
  ui/display_manager.py
  ui/safenet_panel.py
  executor/mcp_executor.py
  external/external_process_manager.py
```

---

# Appendix B — Governance & Auditing Notes

- Every plan is immutable once `APPROVED`. Amendments must create a new Plan.  
- Keep plan snapshots and diffs for at least 90 days (configurable).  
- Provide exportable SafeNet reports for compliance (Markdown/JSON).

---

# Contact & Next Steps

If you want, I can:
- Generate the **actual Python skeleton files** in the project (stubs + tests) and save them to `/mnt/data/pulsus_mcp_skeleton.zip`.  
- Produce a Qt-based **Plan Preview UI** payload and a minimal CLI client example.  
- Create E2E test cases (pytest) for the Plan lifecycle.

Which do you want exported next?
