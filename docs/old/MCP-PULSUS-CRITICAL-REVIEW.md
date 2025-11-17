
# ⚠️ MCP–PULSUS Critical Technical Review

**Date:** 2025-11-09  
**Purpose:** Identify weaknesses, unrealistic assumptions, and optimization gaps in the MCP–PULSUS Advanced TODO before implementation.

---

## 1. Architectural Complexity
The proposed system attempts to merge a full orchestration engine with an LLM, MCP, and UI in one runtime. This creates excessive coupling and runtime complexity.

**Risks:**
- Too many interdependent modules.
- Async execution, rollback, and logging complicate error recovery.

**Fix:**
Split into two modes:
1. Deterministic MCP (direct tool calls).
2. Autonomous Planning (optional workflow composition).

---

## 2. Overengineered State Machine
The 6-state Plan lifecycle is excessive for a single-agent environment.

**Fix:** Reduce to 3 runtime states: `PLAN → EXECUTION → REVIEW`.

---

## 3. Unrealistic Planner Autonomy
Expecting the LLM to autonomously produce optimal Plans is infeasible.

**Fix:** Use **blueprint workflows (YAML/JSON)** for known task mappings. The LLM adapts parameters, not structure.

---

## 4. Rollback Unrealism
Automatic rollback for complex domain actions (QGIS, repo updates) is unsafe.

**Fix:** Restrict rollback to reversible file operations or metadata backups only.

---

## 5. ExternalProcessManager Risks
Subprocess control with timeouts and sandboxing is fragile and OS-dependent.

**Fix:** Define adapter interfaces: `LocalProcessAdapter`, `MockAdapter`, and `RemoteAdapter`. Never execute arbitrary shell commands.

---

## 6. AutoReviewer Unrealism
Validation (lint, tests, CI-level checks) needs fixed environments.

**Fix:** Restrict to syntax check, diff/hash validation, and optional lint. Defer CI-level testing to external pipelines.

---

## 7. Safety Policy Too Generic
Global safety levels ignore context differences between domains.

**Fix:** Use **Policy Profiles per domain** with explicit constraints.

---

## 8. Heavy Registry Introspection
Dynamic MCP discovery on startup is slow and brittle.

**Fix:** Generate a **static cache** and lazily introspect only modified modules.

---

## 9. Dependency Overload
LangChain, SafeNet, Qt, subprocess, and validation in one runtime adds fragility.

**Fix:** Separate layers; communicate via JSON messages, not shared runtime state.

---

## 10. Unrealistic Learning
Adaptive feedback implies model retraining; not viable in local mode.

**Fix:** Rename to **Adaptive Preferences** (simple approval heuristics).

---

## 11. LLM Role Confusion
LLM both plans and validates; no independence.

**Fix:** Separate roles: Planner (LLM), Executor (deterministic), Reviewer (rule-based).

---

## 12. Redundant LangChain Integration
Duplicating MCP and LangChain tool wrappers wastes tokens.

**Fix:** Use LangChain tools only for discovery, MCP for execution.

---

## 13. Missing Technical Details
Missing concurrency, versioning, permission, and resource control.

**Fix:** Add explicit resource manager and per-step context fields.

---

## 14. Performance Bottlenecks
Registry introspection and plan analysis increase startup latency.

**Fix:** Lazy-load MCP classes and defer doc generation.

---

## 15. UI Integration Risks
Qt concurrency must use signals/slots; synchronous calls will freeze UI.

**Fix:** Run MCPExecutor in a worker thread and emit SafeNet events asynchronously.

---

## ✅ Strengths
- Strong modularity vision.  
- Clear safety and approval design.  
- Excellent logging and documentation approach.

---

## 🧩 Summary Recommendations
- Start small: deterministic MCP, static workflows.  
- Postpone planner autonomy, rollback, and AutoReviewer.  
- Add safety, policy, and rollback per domain only.  
- Focus on safe, incremental deployment.  
