# 🧩 MCP-PULSUS-TODO-V3 — PART 2 (Phases 6–10)

**Version:** 3.0 — November 2025
**Scope:** Pulsus Execution Agent — Advanced Capabilities, Observability, and Testing
**Goal:** Extend the foundational architecture from Part 1 with user adaptability, observability (SafeNet), interface integrations, optional extensions, and robust testing.

---

## 🧩 Phase 6 — Adaptive Preferences & Context Memory

### 🎯 Objective

Enable Pulsus to adapt to developer preferences without affecting safety. These preferences should be lightweight, human-readable, and easily reset.

### 🧠 Context

Preferences store non-critical user configurations such as default safety levels, auto-approval for read-only actions, and display verbosity.

### ⚙️ File Structure

```
agents/pulsus/preferences/
 ├── manager.py
 ├── defaults.json
 └── __init__.py
```

### 🧩 Technical Specification

#### manager.py

```python
import json, os
from pathlib import Path

class PreferencesManager:
    def __init__(self):
        self.pref_path = Path.home() / '.pulsus/preferences.json'
        self.data = self.load_preferences()

    def load_preferences(self):
        if not self.pref_path.exists():
            return {"auto_approve_read_only": False, "verbosity": "normal"}
        with open(self.pref_path, 'r') as f:
            return json.load(f)

    def save_preferences(self):
        os.makedirs(self.pref_path.parent, exist_ok=True)
        with open(self.pref_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def update(self, key, value):
        self.data[key] = value
        self.save_preferences()
```

### 🪜 Development Steps

1. Define `PreferencesManager` with load/save/update.
2. Load defaults from `defaults.json`.
3. Add CLI command to edit or reset preferences.
4. Write unit tests simulating preference changes.

### ✅ Acceptance Criteria

* Preferences persist across sessions.
* Auto-approval flags never override safety checks.
* Config changes logged to SafeNet.

### 🔗 Dependencies

Phases 1–5 (for logging integration).

---

## 🧩 Phase 7 — SafeNet Logging & Observability

### 🎯 Objective

Introduce a structured observability layer to track all MCP actions, execution details, and review metadata.

### ⚙️ File Structure

```
agents/shared/logging/
 ├── safenet_logger.py
 ├── formatter.py
 ├── metrics.py
 └── __init__.py
```

### 🧩 Technical Specification

#### safenet_logger.py

```python
import json, time, os
from datetime import datetime

class SafeNetLogger:
    def __init__(self, log_dir='logs/mcp'):
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.jsonl"

    def log_event(self, event_type, domain, action, result, metadata=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "domain": domain,
            "action": action,
            "result": result,
            "metadata": metadata or {},
            "latency_ms": round(time.time() * 1000)
        }
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
```

#### formatter.py

Provide JSON and human-readable output.

#### metrics.py

Aggregate performance stats:

* Total executions per domain
* Average latency per action

### 🪜 Development Steps

1. Implement SafeNetLogger and connect to all MCPExecutions.
2. Create metrics aggregator for dashboards.
3. Add rotating logs and retention policy (7 days default).
4. Write integration tests ensuring logs capture all MCP events.

### ✅ Acceptance Criteria

* Every MCP call produces a SafeNet log entry.
* Log entries include domain, action, safety level, result, and hash.
* Retention and formatting validated.

### 🔗 Dependencies

Phases 1–5.

---

## 🧩 Phase 8 — Interface & API Adapters

### 🎯 Objective

Expose Pulsus via multiple interfaces: CLI for users and JSON API for LangGraph or Compasus supervisor.

### ⚙️ File Structure

```
agents/pulsus/interface/
 ├── cli.py
 ├── api.py
 └── __init__.py
```

### 🧩 Technical Specification

#### cli.py

```python
import argparse
from agents.pulsus.executor.mcp_executor import MCPExecutor

def main():
    parser = argparse.ArgumentParser(description="Pulsus CLI - Execute MCP actions")
    parser.add_argument('domain', help='MCP domain (e.g. ScriptManager)')
    parser.add_argument('method', help='MCP method to invoke')
    parser.add_argument('--params', type=str, default='{}', help='JSON parameters')
    args = parser.parse_args()

    executor = MCPExecutor.load_registry()
    result = executor.execute_action(args.domain, args.method, eval(args.params))
    print(result)
```

#### api.py

Expose HTTP API for LangGraph integration.

```python
from fastapi import FastAPI
from agents.pulsus.executor.mcp_executor import MCPExecutor

app = FastAPI()
executor = MCPExecutor.load_registry()

@app.post('/execute')
def execute_action(payload: dict):
    domain = payload['domain']
    method = payload['method']
    params = payload.get('params', {})
    return executor.execute_action(domain, method, params).__dict__
```

### 🪜 Development Steps

1. Implement CLI entrypoint with argparse.
2. Implement FastAPI endpoint.
3. Add test cases (CLI command, API call, invalid domain).
4. Ensure SafeNet logs API-triggered actions.

### ✅ Acceptance Criteria

* CLI and API both functional and return MCPResponse JSON.
* CLI tool includes `--help` and verbose modes.
* Compatible with LangGraph nodes via HTTP or local ToolNode.

### 🔗 Dependencies

Phases 1–7.

---

## 🧩 Phase 9 — Optional Extensions (Future-Proofing)

### 🎯 Objective

Design extension points for future planning, multi-agent orchestration, and blueprint workflows.

### 🧠 Context

These extensions will integrate Pulsus into the larger multi-agent ecosystem once Compasus and LangGraph orchestration are online.

### ⚙️ File Structure

```
agents/pulsus/extensions/
 ├── blueprint_runner.py
 ├── registry_cache.py
 ├── autoreviewer.py
 └── __init__.py
```

### 🧩 Technical Specification

#### blueprint_runner.py

* Execute declarative YAML/JSON blueprints defining sequences of MCP actions.

```yaml
plan:
  - domain: ScriptManager
    method: format_script
    params: {path: "main.py"}
  - domain: DataAnalyzer
    method: summarize_csv
    params: {path: "data.csv"}
```

#### registry_cache.py

* Preload and cache available MCP domains for faster startup.

#### autoreviewer.py

* Optional plugin to run post-execution checks (lint, typecheck, test discovery).

### 🪜 Development Steps

1. Scaffold each extension with clear entrypoints.
2. Implement dynamic import under feature flags.
3. Write test stubs for blueprint parsing.

### ✅ Acceptance Criteria

* Extensions load only when explicitly enabled.
* Core Pulsus remains unaffected by optional modules.

### 🔗 Dependencies

Phases 1–8.

---

## 🧩 Phase 10 — Testing, Validation, and Performance

### 🎯 Objective

Guarantee Pulsus’ reliability, safety, and scalability through extensive automated testing and benchmarking.

### ⚙️ File Structure

```
tests/
 ├── unit/
 │   ├── test_core.py
 │   ├── test_domains.py
 │   └── test_executor.py
 ├── integration/
 │   ├── test_sandbox.py
 │   ├── test_api.py
 │   └── test_preferences.py
 └── performance/
     └── test_benchmarks.py
```

### 🧩 Testing Matrix

| Category    | Coverage                                        |
| ----------- | ----------------------------------------------- |
| Unit        | Core, Decorators, Executor                      |
| Integration | Sandbox, API, Logging                           |
| Performance | Startup latency, Execution time, Log throughput |
| Security    | Injection prevention, File access scope         |

### 🪜 Development Steps

1. Create pytest-based suite with coverage reports.
2. Add sandbox stress tests.
3. Benchmark using timeit and async profiling.
4. Run tests in CI container with limited permissions.

### ✅ Acceptance Criteria

* 95%+ test coverage.
* Execution latency < 250ms average for light tasks.
* Sandbox rejects all unsafe imports.
* CI passes on Linux & macOS.

### 🔗 Dependencies

All previous phases.

---

## 🧭 Final Outcome

By the end of Phase 10:

* Pulsus is a **fully modular, deterministic execution engine**, built atop MCP.
* Integrates seamlessly with **LangChain Tools** and **LangGraph supervisors**.
* Provides **structured observability** via SafeNet logs.
* Supports **CLI and API** interfaces for users and multi-agent systems.

**Next Steps:**
Transition Pulsus into LangGraph’s execution layer (Compasus supervisor integration) for autonomous multi-agent orchestration.

---

**End of MCP-PULSUS-TODO-V3 — Part 2**
