# Pulsus Routing System

## Overview
The **Pulsus Routing System** defines how the `Pulse.ai` agent, powered by **LangChain**, interacts with domain-specific tools and workflows. This routing system ensures that user prompts are dynamically matched with the most relevant functions and scripts across available modules.

---

## Flow Diagram (Mermaid)
```mermaid
flowchart TD
  U[User prompt via console] --> C[Prompt Parser]
  C --> D{Domain detection}
  D -->|Known domain| T[Tool Retriever]
  D -->|Unclear| Q[Ask user clarification]
  T --> S[Code Synthesizer]
  S --> V[Validation (Shell or Pulsus Console)]
  V --> A{User approval}
  A -->|Approve| P[Promote to official tool]
  A -->|Reject| E[Edit / Relocate / Discard]
  P --> M[Metadata update & Versioning]
  E --> S
```

---

## 1. User Input Flow

When a user submits a **prompt via the console interface**, the following sequence occurs:

1. **Prompt reception**
   Pulsus receives the natural language query from the user through the console (e.g., *"Analyse the current network performance").*

2. **Configuration lookup**
   Pulsus reads from a configuration file to locate the root folder for available workflows and tools:

```
workflows/
├── domains/
│   ├── traffic_demand/
│   ├── analysis/
│   ├── simulation/
│   └── visualisation/
└── shared_tools/
```

> Note: UK English is used throughout (`analyse`, `visualise`, etc.) and the `workflows/` prefix is standardised.

3. **Domain & action detection**
   The Prompt Parser attempts to detect domain and action (e.g. `analysis` + `visualise`). If uncertain, Pulsus asks a brief clarifying question in the console.

4. **Action search & tool discovery**
   Pulsus navigates subdirectories representing actions:

```
acquire/
analyse/
edit/
review/
import/
export/
visualise/
```

It lists available scripts, inspects their function signatures and docstrings, and builds a ranked list of candidate tools.

5. **Tool selection & code synthesis**
   Candidate tools may be:
   - Imported and run as-is,
   - Composed into a new script,
   - Or replaced by freshly generated code following existing conventions.

---

## 2. Shared Tools

If the user request is general (e.g., *"Count records"*, *"Show recent imports"*), Pulsus defaults to the `workflows/shared_tools/` directory which contains reusable utilities:

```
workflows/shared_tools/
├── acquire/
│   └── get_data_from_api.py
├── analyse/
│   └── calculate_statistics.py
└── visualise/
    └── generate_plot.py
```

---

## 3. Code Composition & Validation (Merged)

After assembling or generating a script, Pulsus:

1. Writes the code to a **temporary script** inside the target domain/action folder (e.g. `workflows/domains/analysis/visualise/tmp_script_name.py`).
2. Runs optional static validation (via the Shell agent) and/or sandboxed tests in a forthcoming Pulsus Console (SafeNet) environment — see *Future enhancement* below.
3. Interacts with the user via consistent console prompts to approve, relocate or edit the script before promotion.

---

## 4. Console Interaction (Consistent Format)

All console interactions use a standard `[PULSUS]` prompt and fenced code blocks in docs. Example session:

```bash
[PULSUS] Suggested save path: workflows/domains/analysis/visualise/tmp_script_name.py
[PULSUS] Approve this location and filename? (y/n)
> n

[PULSUS] Enter new domain (default: analysis):
> network_management

[PULSUS] Enter new action (default: visualise):
> analyse

[PULSUS] Enter new filename (no spaces, .py added if missing):
> analyse_network_tmp

[PULSUS] Saved as: workflows/domains/network_management/analyse/analyse_network_tmp.py

[PULSUS] Execute analyse_network_tmp.py now? (y/n)
> y

[PULSUS] Execution complete. Was the output correct? Approve for integration? (y/n)
> y

[PULSUS] Approved. Promoting to official tool: analyse_network_summary.py
```

---

## 5. Example Scenarios (Expanded)

### a) Analysis + Visualise (existing example)
User: "Analyse the imported OD matrix and generate a visual summary."
- Pulsus finds `summarize_matrix.py` and `plot_matrix.py`, composes `tmp_script_name.py`, asks for approval, tests, and promotes to `generate_visual_summary.py` upon user approval.

### b) Import action (new example)
User: "Import CSV into the network database and normalise IDs."
- Domain: `data_import` / action: `import`.
- Candidate: `import_csv.py` in `workflows/domains/data_import/import/`.
- Pulsus generates wrapper that validates columns, executes import in tmp file, and requests user approval.

### c) Review action (new example)
User: "Review last 50 edits on the network and create a changelog."
- Domain: `analysis` / action: `review`.
- Pulsus looks for `list_changes.py`, `generate_changelog.py`, composes a script for review and prepares a changelog preview for user validation.

---

## 6. Metadata Update (JSON Example)

When a temporary script is approved for promotion, Pulsus updates the domain metadata. Example record:

```json
{
  "name": "generate_visual_summary.py",
  "domain": "analysis",
  "action": "visualise",
  "description": "Generates summary stats and visual summary for OD matrices",
  "status": "stable",
  "created_by": "pulse_ai_v1.1",
  "created_at": "2025-10-31T12:00:00+04:00",
  "version": "1.0.0",
  "revision_id": "rev-20251031-001",
  "tokens_estimate": 1340,
  "model": {
    "type": "openai/gpt-like",
    "name": "llama3.2:3b",
    "params": {"temperature": 0.3, "max_tokens": 1024}
  },
  "RAG": {
    "enabled": true,
    "vector_index": "docs_v1"
  }
}
```

> Note: Metadata fields include token estimates, model configuration, RAG settings and a revision identifier to support traceability.

---

## 7. Error Handling & Edge Cases

- **User cancels during naming/relocation:** Pulsus discards the temporary file and logs the attempt. The user can re-run the request.
- **Invalid path / permissions error:** Pulsus reports the error and prompts for a new location or suggests running with elevated permissions.
- **Script execution fails during test:** Pulsus saves the stderr/stdout logs in `workflows/tmp_logs/` and offers options: regenerate code, debug (open logs), edit filename, or discard.
- **User rejects promotion after test:** Pulsus keeps the tmp file for a configurable retention period (default: 7 days) and offers to re-run or delete it.

---

## 8. Versioning & Revision History

Promoted scripts are versioned. Minimal versioning metadata:
- `version` (semver style)
- `revision_id` (unique id)
- `created_at` and `created_by`

Promotions append a changelog entry in `workflows/domains/<domain>/CHANGELOG.md`.

---

## 9. Pulsus Console (SafeNet) — Future Enhancement

A sandboxed **Pulsus Console** (SafeNet) will be introduced as a future enhancement for secure execution and testing of temporary scripts. Its responsibilities will include:
- Isolated runtime for executing tmp scripts
- Resource limits (CPU, memory, timeouts)
- Network access control
- Automatic log capture and sanitisation

This is planned as a future feature and will be integrated with the existing validation layer.

---

## 10. Console Command Reference (Summary Table)

| Command / Prompt | Purpose |
|------------------|---------|
| Approve (y/n) | Accept suggested filename & location |
| Relocate | Move tmp script to different domain/action |
| Rename | Change filename before promotion |
| Execute (y/n) | Run tmp script for testing |
| Approve promotion (y/n) | Promote tmp script to official tool |
| Discard | Delete tmp script |

---

## 11. Formatting & Conventions

- Use UK English spelling (`analyse`, `visualise`) consistently.
- Use `workflows/` as the canonical root for tool discovery.
- Console prompts always use `[PULSUS]` for clarity.

---

## 12. Summary

This version (v1.1) integrates visual routing, expanded examples, improved metadata, error handling, a versioning approach, and a future-safe Pulsus Console plan. It is intended to be practical for developers implementing or extending Pulse.ai in a LangChain-driven system.

> "Structure first, synthesis next — validation always — that’s the Pulsus way."