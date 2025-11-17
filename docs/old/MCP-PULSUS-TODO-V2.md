
# ✅ MCP–PULSUS Simplified & Updated TODO (Post-Review)

**Version:** 2025-11-09  
**Purpose:** Practical, staged roadmap implementing the reviewed and optimized design.

---

## PHASE 1 — MCP CORE & SAFETY

**Goal:** Build stable deterministic MCP foundation.

**Tasks:**
- [x] Implement `MCPBase` and `MCPResponse`.
- [x] Add decorators (`@read_only`, `@write_safe`, `@restricted_write`).
- [ ] Implement rollback stack for file-based operations only.
- [ ] Add SafetyPolicy with per-domain profiles.

**Deliverables:**
- agents/mcp/core/base.py
- agents/mcp/core/decorators.py
- agents/mcp/core/policy.py

---

## PHASE 2 — DOMAIN MCP CLASSES

**Goal:** Modularize toolsets into safe MCP domains.

**Classes:**
- ScriptManager
- RepositoryManager
- ModelInspector
- DataAnalyzer

**Tasks:**
- [ ] Convert procedural utilities into MCP methods.
- [ ] Apply safety decorators per method.
- [ ] Register to MCPRegistry with metadata.

---

## PHASE 3 — PLAN & EXECUTOR (MINIMAL)

**Goal:** Enable multi-step deterministic execution with optional approval.

**Tasks:**
- [ ] Implement lightweight `Plan` model (id, steps, summary).
- [ ] Add `MCPExecutor.execute_plan(plan, approvals)`.
- [ ] No rollback for unreversible actions.
- [ ] Add SafeNet logging of start/stop events.

**Deliverables:**
- agents/pulsus/executor/mcp_executor.py

---

## PHASE 4 — APPROVAL UX (BASIC)

**Goal:** Let user review and approve steps safely.

**Tasks:**
- [ ] Qt/CLI Plan Preview panel.
- [ ] Display step safety, description, diff.
- [ ] Support “Approve all” and “Approve step” actions.
- [ ] Pass approvals to executor as flags.

---

## PHASE 5 — EXTERNAL PROCESS (SAFE MODE)

**Goal:** Controlled subprocess execution.

**Tasks:**
- [ ] Add `LocalProcessAdapter` with allowlist.
- [ ] Disable direct shell input.
- [ ] Add timeout and environment sanitization.

---

## PHASE 6 — REVIEW & VALIDATION (LIGHTWEIGHT)

**Goal:** Basic post-run integrity checks.

**Tasks:**
- [ ] Validate syntax and diffs only.
- [ ] Optional lint if available.
- [ ] Generate `MCPReviewResponse` summary.

---

## PHASE 7 — ADAPTIVE PREFERENCES

**Goal:** Simplified user approval memory.

**Tasks:**
- [ ] Track user approvals in local JSON.
- [ ] Recommend defaults for recurring actions.

---

## PHASE 8 — UI & SAFENET INTEGRATION

**Goal:** Unified interface for plan execution and logs.

**Tasks:**
- [ ] Live SafeNet panel (thread-safe signal events).
- [ ] Non-blocking MCPExecutor thread.
- [ ] Execution summary + review report panel.

---

## PHASE 9 — OPTIONAL EXTENSIONS

**Future Add-ons:**
- Planner autonomy with workflow blueprints.
- Multi-agent orchestration.
- Rich AutoReviewer plugins.
- Static registry caching and doc generation.

---

## PHASE 10 — TESTING & STAGING

**Goal:** Reliability and reproducibility.

**Tasks:**
- [ ] Unit tests for MCPBase, decorators, executor.
- [ ] Integration tests for plan execution.
- [ ] Performance test on startup and SafeNet logs.

---

**Final Target:** A stable, auditable, user-controlled MCP platform ready for modular autonomy upgrades.
