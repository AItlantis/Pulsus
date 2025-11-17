# Pulsus Architecture - Quick Reference

**Version**: 4.0 (Phase 3 Complete)
**Last Updated**: November 17, 2025

---

## System Layers (Top to Bottom)

```
┌─────────────────────────────────────────────┐
│  User Interface (CLI, API, Dashboard)      │
├─────────────────────────────────────────────┤
│  Routing (Intent Parser, Tool Discovery)   │
├─────────────────────────────────────────────┤
│  Safety (Policy Engine, Decorators)        │
├─────────────────────────────────────────────┤
│  Execution (Sandbox, Operation Executor)   │
├─────────────────────────────────────────────┤
│  MCP Domains (Simple, Advanced, Custom)    │
├─────────────────────────────────────────────┤
│  Composition (Chain, Parallel, Conditional)│
├─────────────────────────────────────────────┤
│  Monitoring (Metrics, Alerts, Logging)     │
├─────────────────────────────────────────────┤
│  Integration (LangChain, LangGraph)        │
└─────────────────────────────────────────────┘
```

---

## Core Concepts

### MCPBase
- **What**: Base class for all MCP domains
- **Where**: `mcp/core/base.py`
- **Key Methods**: `execute()`, `get_capabilities()`
- **Returns**: `MCPResponse` (success, data, error, trace, context)

### Safety Decorators
| Decorator | Purpose | Confirmation | Sandbox |
|-----------|---------|--------------|---------|
| `@read_only` | Safe reads | No | No |
| `@write_safe` | Write ops | Yes | Recommended |
| `@restricted_write` | Platform writes | Yes | Yes |
| `@transactional` | With rollback | Yes | Yes |
| `@cached` | Cached reads | No | No |

### Execution Modes
- **PLAN**: Planning only (no execution)
- **EXECUTE**: Full execution with safety checks
- **UNSAFE**: Unrestricted (developer mode)

---

## Domain Overview

### Simple Domains (Phase 2)
```python
from mcp.simple import (
    ScriptOps,       # Python script operations
    RepositoryOps,   # Repository management
    FileManager,     # File operations
    DataReader,      # Data loading
    TextProcessor    # Text operations
)
```

### Advanced Domains (Phase 3)
```python
from mcp.advanced import (
    GitOps,         # Git operations (8 ops)
    WorkflowOps     # Workflow orchestration (5 ops)
)
```

---

## Composition Tools (Phase 3)

### OperationChain - Sequential Execution
```python
from mcp.composition import OperationChain

chain = OperationChain("my_workflow")
chain.add(domain, 'operation1', param1='value1')
chain.add(domain, 'operation2', param2='value2')
result = chain.execute()  # Executes with rollback on error
```

### ParallelOperations - Concurrent Execution
```python
from mcp.composition import ParallelOperations

parallel = ParallelOperations(max_workers=4)
parallel.add(domain, 'operation1', param1='value1')
parallel.add(domain, 'operation2', param2='value2')
result = parallel.execute()  # Executes all in parallel
```

### ConditionalFlow - Conditional Execution
```python
from mcp.composition import ConditionalFlow

flow = ConditionalFlow()
result = flow.if_then_else(
    condition_fn=lambda: check_condition(),
    then_domain=domain, then_operation='op1',
    else_domain=domain, else_operation='op2'
)
```

---

## Monitoring (Phase 3)

### MCPMetrics - Performance Tracking
```python
from mcp.monitoring.metrics import get_metrics

metrics = get_metrics()

# Track operation
metrics.track_operation(
    domain='ScriptOps',
    operation='read_script',
    duration_ms=45.2,
    success=True
)

# Get statistics
stats = metrics.get_statistics(domain='ScriptOps')
# Returns: count, success_rate, duration_ms (min/max/mean/p50/p95/p99)
```

### AlertManager - Alerting System
```python
from mcp.monitoring.alerts import get_alert_manager, AlertSeverity

alerts = get_alert_manager()

alerts.register_alert(
    name='high_error_rate',
    condition=lambda: metrics.get_error_rate() > 0.1,
    severity=AlertSeverity.ERROR,
    message=lambda: "Error rate exceeded 10%"
)

triggered = alerts.check_all()
```

### SafeNet Dashboard - Web UI
```python
from safenet.dashboard import run_dashboard

run_dashboard(host='0.0.0.0', port=5000, debug=True)
# Access at http://localhost:5000
```

---

## LangChain Integration (Phase 3)

### Convert MCP to LangChain Tool
```python
from langchain.tool_adapter import mcp_to_langchain_tool
from mcp.simple import ScriptOps

# Convert entire domain
tool = mcp_to_langchain_tool(ScriptOps)

# Or convert specific operation
read_tool = mcp_to_langchain_tool(ScriptOps, 'read_script')

# Use in agent
from langchain.agents import AgentExecutor
agent = AgentExecutor(tools=[tool], ...)
```

### Tool Registry
```python
from langchain.tool_adapter import MCPToolRegistry

registry = MCPToolRegistry()
registry.register_domain(ScriptOps)
registry.register_domain(GitOps)

tools = registry.get_all_tools()
```

### LangGraph Integration
```python
from langchain.graph_executor import PulsusGraphRunner

runner = PulsusGraphRunner()
result = runner.run("Read the script at main.py")
```

---

## File Structure

```
Pulsus/
├── mcp/
│   ├── core/              # MCPBase, decorators, policy
│   ├── simple/            # Simple domains (Phase 2)
│   ├── advanced/          # Advanced domains (Phase 3)
│   ├── composition/       # Composition tools (Phase 3)
│   └── monitoring/        # Metrics & alerts (Phase 3)
├── langchain/             # LangChain integration (Phase 3)
├── safenet/               # Dashboard (Phase 3)
├── routing/               # Router, intent parser
├── core/                  # Compose, rankers, validators
├── tests/                 # Test suites
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

---

## Common Patterns

### Pattern 1: Simple Operation
```python
from mcp.simple import ScriptOps

ops = ScriptOps()
result = ops.read_script(path='main.py')

if result.success:
    print(result.data)
else:
    print(result.error)
```

### Pattern 2: Workflow Chain
```python
from mcp.composition import OperationChain
from mcp.simple import ScriptOps
from mcp.advanced import GitOps

chain = OperationChain("refactor")
chain.add(git_ops, 'get_status', repo_path='.')
chain.add(script_ops, 'format_script', path='main.py')
chain.add(git_ops, 'commit', repo_path='.', message='Format')
result = chain.execute()
```

### Pattern 3: Parallel Execution
```python
from mcp.composition import ParallelOperations

parallel = ParallelOperations(max_workers=4)
for file in files:
    parallel.add(script_ops, 'read_script', path=file)
result = parallel.execute()
```

### Pattern 4: Monitoring Setup
```python
from mcp.monitoring.metrics import get_metrics
from mcp.monitoring.alerts import get_alert_manager, AlertSeverity

metrics = get_metrics()
alerts = get_alert_manager()

# Register alerts
alerts.register_alert(
    name='slow_operations',
    condition=lambda: len(metrics.get_slow_operations()) > 0,
    severity=AlertSeverity.WARNING,
    message=lambda: "Slow operations detected"
)

# Check periodically
import time
while True:
    triggered = alerts.check_all()
    time.sleep(60)
```

---

## Key APIs

### MCPResponse Structure
```python
{
    'success': bool,
    'data': Any,
    'error': Optional[str],
    'context': Dict[str, Any],
    'trace': List[str],
    'status': MCPStatus,
    'metadata': Dict[str, Any]
}
```

### Operation Execution
```python
# Direct call
result = domain.operation_name(param1='value1')

# Generic execute
result = domain.execute('operation_name', param1='value1')
```

### Metrics API
```python
# Track
metrics.track_operation(domain, operation, duration_ms, success)

# Statistics
stats = metrics.get_statistics(domain=None, timeframe='all')

# Slow ops
slow = metrics.get_slow_operations(threshold_ms=1000)

# Error rate
rate = metrics.get_error_rate(domain=None, timeframe='last_hour')

# Domain summary
summary = metrics.get_domain_summary()
```

### Dashboard API Endpoints
```
GET  /                          Main dashboard
GET  /api/metrics               Metrics statistics
GET  /api/metrics/recent        Recent operations
GET  /api/metrics/domains       Domain summary
GET  /api/metrics/slow          Slow operations
GET  /api/alerts                Alert history
GET  /api/alerts/counts         Alert counts
GET  /health                    Health check
```

---

## Performance Targets

| Operation Type | p95 Target | p99 Target |
|----------------|------------|------------|
| Read operations | < 50ms | < 100ms |
| Write operations | < 100ms | < 200ms |
| Chain operations | < 500ms | < 1000ms |
| Workflow execution | < 2000ms | < 5000ms |

---

## Testing

### Run Tests
```bash
# All tests
pytest tests/ -v

# Phase 3 tests
pytest tests/test_phase3.py -v

# Specific test
pytest tests/test_phase3.py::test_gitops_capabilities -v

# With coverage
pytest tests/ --cov=mcp --cov-report=html
```

---

## Common Commands

### Start Dashboard
```bash
python -m safenet.dashboard
# Or with options
python -m safenet.dashboard --host 0.0.0.0 --port 5000 --debug
```

### Render Diagrams
```bash
# PNG (default)
python scripts/render_diagrams.py

# SVG
python scripts/render_diagrams.py --format svg

# Custom output
python scripts/render_diagrams.py --output docs/diagrams/
```

### Run Tests
```bash
pytest tests/test_phase3.py -v
```

---

## Troubleshooting

### Import Errors
```python
# If langchain-core not installed
pip install langchain-core

# If langgraph not installed
pip install langgraph

# If flask not installed
pip install flask
```

### Diagram Rendering
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Then run
python scripts/render_diagrams.py
```

### Dashboard Not Starting
```bash
# Install Flask
pip install flask

# Then run
python -m safenet.dashboard
```

---

## Quick Links

- **Full Architecture**: `docs/ARCHITECTURE.md`
- **Phase 3 Documentation**: `docs/PHASE3_COMPLETE.md`
- **Unified Plan**: `docs/PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`
- **Test Suite**: `tests/test_phase3.py`
- **Dashboard**: `safenet/dashboard.py`

---

**Document Version**: 1.0
**Status**: Complete ✅
**Last Updated**: November 17, 2025
