# 🧩 PULSUS MCP — UNIFIED INTEGRATION PLAN

**Version:** 4.0 — UNIFIED EDITION
**Date:** November 2025
**Scope:** Complete transformation of Pulsus into a world-class AI MCP agent
**Architecture:** LangChain workflows + MCP domains + External execution + Claude Code agents

---

## 🎯 Executive Summary

This document unifies the MCP-PULSUS-TODO-V3 (Parts 1 & 2) into a comprehensive integration plan that transforms Pulsus into a world-class Model Context Protocol (MCP) execution agent with:

- **LangChain/LangGraph workflow architecture** - Professional multi-agent orchestration
- **Three-tier MCP feature organization** - Classic (simple), Complex (workflow-based), Customizable (config-driven)
- **External console execution** - Run software and processes in separate consoles
- **Jean-Claude agent integration** - Specialized Claude Code agents for each phase
- **Full observability** - SafeNet logging, metrics, and dashboards
- **Production-ready interfaces** - CLI and API for standalone and supervisor integration

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Three-Tier MCP Organization](#three-tier-mcp-organization)
3. [LangChain Workflow Structure](#langchain-workflow-structure)
4. [External Console Execution](#external-console-execution)
5. [Phase-by-Phase Implementation with Agent Assignments](#phase-by-phase-implementation)
6. [Jean-Claude Agents](#jean-claude-agents)
7. [Directory Structure](#directory-structure)
8. [Integration Timeline](#integration-timeline)
9. [Success Criteria](#success-criteria)

---

## 🏗️ Architecture Overview

### Vision

Pulsus evolves from a routing and execution layer into a **complete MCP orchestration platform** that:

1. **Routes natural language to MCP actions** - Intent parsing → Tool discovery → Execution
2. **Orchestrates complex workflows** - Multi-step analysis, code generation, validation
3. **Integrates with external processes** - Launch software in dedicated consoles
4. **Adapts to user preferences** - Configuration-driven behavior without compromising safety
5. **Provides full observability** - Every action logged, metrics tracked, dashboards generated
6. **Exposes multiple interfaces** - CLI for users, API for LangGraph supervisors

### Core Principles

- **Modular Architecture** - Clear separation: core, mcp (classic + workflow), config, interface
- **Safety First** - Multi-level safety decorators, sandboxing, approval workflows
- **LangChain Native** - Built on LangChain Tools and LangGraph StateGraph
- **Deterministic + Adaptive** - Predictable execution with intelligent fallback
- **Observable** - SafeNet logging tracks every decision and action
- **Extensible** - Plugin architecture for custom MCP domains and workflows

---

## 🎯 Three-Tier MCP Organization

### Tier 1: Classic MCP (Simple Operations)

**Location:** `pulsus/mcp/`
**Characteristics:** Simple, atomic operations with clear inputs/outputs
**Execution:** Direct function calls, minimal state

**Examples:**
- `ScriptOps` - Read/write/format Python files
- `FileManager` - Create, delete, move files
- `DataReader` - Load CSV, JSON, parquet
- `TextProcessor` - Search, replace, extract patterns

**Structure:**
```
pulsus/mcp/
├── core/
│   ├── base.py           # MCPBase, MCPResponse
│   ├── decorators.py     # @read_only, @write_safe, etc.
│   ├── policy.py         # SafetyPolicy, ExecutionMode
│   └── logger.py         # SafeNetLogger integration
├── simple/               # Tier 1: Classic MCP operations
│   ├── script_ops.py
│   ├── file_manager.py
│   ├── data_reader.py
│   └── text_processor.py
└── __init__.py
```

### Tier 2: Complex MCP (Workflow-Based)

**Location:** `pulsus/workflows/`
**Characteristics:** Multi-step processes, decision trees, state management
**Execution:** LangChain workflows, often with LLM assistance

**Examples:**
- `RepositoryAnalyzer` - Multi-step codebase analysis
- `CodeRefactorer` - Plan → Execute → Validate refactoring
- `DocumentationGenerator` - Scan → Analyze → Generate docs
- `DependencyDocumenter` - Trace → Document → Export dependencies

**Structure:**
```
pulsus/workflows/
├── tools/
│   ├── analyze/
│   │   ├── repository_analyzer_llm.py
│   │   ├── file_analyzer.py
│   │   ├── dependency_documenter.py
│   │   └── unified_analyzer.py
│   ├── discover/
│   │   └── framework_scanner.py
│   └── summarise/
│       └── summarize_matrix.py
├── definitions/
│   ├── repository_analysis.json
│   ├── dependency_documentation.json
│   └── unified_path_analysis.json
└── __init__.py
```

### Tier 3: Customizable MCP (Framework-Driven)

**Location:** `~/software/source/myproject/framework/`
**Characteristics:** User-defined, configuration-driven custom operations
**Execution:** Loaded dynamically from JSON/YAML configs

**Examples:**
- User defines custom analysis workflows
- Project-specific code generation templates
- Custom validation rules
- Domain-specific language patterns

**Structure:**
```
pulsus/config/frameworks/
├── domains/
│   ├── my_analysis.json
│   ├── my_codegen.yaml
│   └── my_validation.json
├── templates/
│   ├── python_class.j2
│   ├── test_file.j2
│   └── documentation.j2
└── schema/
    └── custom_workflow_schema.json
```

**Configuration Example:**
```json
{
  "name": "my_custom_analysis",
  "description": "Custom repository analysis workflow",
  "steps": [
    {
      "name": "scan_files",
      "tool": "FileScanner",
      "config": {
        "patterns": ["**/*.py"],
        "exclude": ["**/test_*.py"]
      }
    },
    {
      "name": "analyze_imports",
      "tool": "ImportAnalyzer",
      "config": {
        "depth": 2
      }
    },
    {
      "name": "generate_report",
      "tool": "ReportGenerator",
      "config": {
        "template": "custom_analysis_report.j2",
        "format": "markdown"
      }
    }
  ]
}
```

---

## 🔗 LangChain Workflow Structure

### Integration with Pulsus Routing

```
┌─────────────────────────────────────────────────────────────┐
│                   User Query / LLM Request                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Pulsus Router (routing/router.py)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Parse Intent → Identify Domain + Action          │   │
│  │ 2. Discover Tools → Score candidates                │   │
│  │ 3. Select Policy → select | compose | generate      │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
      SELECT       COMPOSE     GENERATE
          │            │            │
          ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Direct Tool │ │ Multi-Tool  │ │ LLM-Generated   │
│  Execution  │ │  Composer   │ │ Dynamic Route   │
└──────┬──────┘ └──────┬──────┘ └────────┬────────┘
       │               │                  │
       │               │                  │
       └───────────────┼──────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          LangChain Tool Execution Layer                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Tools converted to LangChain @tool format            │   │
│  │ MCPBase.execute() → LangChain StructuredTool         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Safety & Execution Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Apply Safety Decorators (@read_only, @write_safe)│   │
│  │ 2. Check ExecutionMode (PLAN | EXECUTE | UNSAFE)   │   │
│  │ 3. Request Approval (if needed)                     │   │
│  │ 4. Execute in Sandbox (if restricted)              │   │
│  │ 5. Log to SafeNet (all actions)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCPResponse + Logging                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Return: MCPResponse(success, data, context, trace)  │   │
│  │ Log: Domain, Action, Result, Latency, Hash          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### LangChain Tool Wrapper

**File:** `pulsus/langchain/tool_adapter.py`

```python
from langchain_core.tools import StructuredTool
from pulsus.mcp.core.base import MCPBase, MCPResponse
from typing import Type, Dict, Any

def mcp_to_langchain_tool(mcp_class: Type[MCPBase]) -> StructuredTool:
    """
    Convert an MCPBase class to a LangChain StructuredTool.

    Args:
        mcp_class: MCP domain class (e.g., ScriptOps, RepositoryAnalyzer)

    Returns:
        LangChain StructuredTool instance
    """
    instance = mcp_class()
    capabilities = instance.get_capabilities()

    def execute_wrapper(**kwargs) -> Dict[str, Any]:
        """Wrapper that calls MCPBase.execute() and converts MCPResponse."""
        response: MCPResponse = instance.execute(
            action=kwargs.get('action'),
            params=kwargs
        )
        return response.to_dict()

    return StructuredTool(
        name=capabilities['domain'],
        description=capabilities['description'],
        func=execute_wrapper,
        args_schema=_generate_args_schema(capabilities['actions'])
    )
```

### LangGraph StateGraph Integration

**File:** `pulsus/langchain/graph_executor.py`

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class PulsusState(TypedDict):
    """State for Pulsus LangGraph execution."""
    messages: Annotated[Sequence[BaseMessage], "Conversation history"]
    parsed_intent: Dict[str, Any]
    selected_tools: List[StructuredTool]
    execution_results: List[MCPResponse]
    next_action: str

def create_pulsus_graph() -> StateGraph:
    """Create LangGraph StateGraph for Pulsus workflow."""

    workflow = StateGraph(PulsusState)

    # Nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("discover_tools", discover_tools_node)
    workflow.add_node("select_policy", select_policy_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("compose_response", compose_response_node)

    # Edges
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "discover_tools")
    workflow.add_edge("discover_tools", "select_policy")

    # Conditional routing
    workflow.add_conditional_edges(
        "select_policy",
        route_execution_policy,
        {
            "select": "execute_tools",
            "compose": "execute_tools",
            "generate": "generate_dynamic_route"
        }
    )

    workflow.add_edge("execute_tools", "compose_response")
    workflow.add_edge("compose_response", END)

    return workflow.compile()
```

---

## 🖥️ External Console Execution

### Requirement

Pulsus must be able to launch and manage external software processes (e.g., simulations, data pipelines, GUI applications) in separate console windows.

### Implementation: ConsoleManager

**Location:** `pulsus/mcp/execution/console_manager.py`

```python
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import psutil

from pulsus.mcp.core.base import MCPBase, MCPResponse
from pulsus.mcp.core.decorators import write_safe, tracked

@dataclass
class ConsoleProcess:
    """Represents an external console process."""
    pid: int
    command: str
    working_dir: Path
    console_title: str
    started_at: str
    status: str  # 'running', 'completed', 'failed'

class ConsoleManager(MCPBase):
    """
    Manage external console processes for software execution.

    Capabilities:
    - launch_console: Start new process in separate console
    - list_consoles: Show all managed processes
    - get_console_status: Check process status
    - kill_console: Terminate process
    - get_console_output: Read stdout/stderr (if captured)
    """

    def __init__(self):
        super().__init__()
        self.processes: Dict[int, ConsoleProcess] = {}

    @write_safe
    @tracked
    def launch_console(
        self,
        command: str | List[str],
        working_dir: Path | str,
        console_title: str = "Pulsus Console",
        capture_output: bool = False,
        env_vars: Optional[Dict[str, str]] = None
    ) -> MCPResponse:
        """
        Launch external process in a new console window.

        Args:
            command: Command to execute (string or list)
            working_dir: Working directory for the process
            console_title: Title for the console window
            capture_output: Whether to capture stdout/stderr
            env_vars: Additional environment variables

        Returns:
            MCPResponse with process info (PID, console handle)

        Example:
            >>> manager = ConsoleManager()
            >>> response = manager.launch_console(
            ...     command=["python", "simulation.py"],
            ...     working_dir=Path("C:/Projects/MySimulation"),
            ...     console_title="Traffic Simulation Run #42",
            ...     capture_output=True
            ... )
            >>> print(response.data['pid'])
            12345
        """
        try:
            working_dir = Path(working_dir)
            if not working_dir.exists():
                return MCPResponse.error(
                    f"Working directory does not exist: {working_dir}"
                )

            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            # Platform-specific console creation
            if sys.platform == 'win32':
                process = self._launch_windows_console(
                    command, working_dir, console_title, capture_output, env
                )
            else:
                process = self._launch_unix_console(
                    command, working_dir, console_title, capture_output, env
                )

            # Track process
            console_proc = ConsoleProcess(
                pid=process.pid,
                command=str(command),
                working_dir=working_dir,
                console_title=console_title,
                started_at=datetime.now().isoformat(),
                status='running'
            )
            self.processes[process.pid] = console_proc

            return MCPResponse.success(
                data={
                    'pid': process.pid,
                    'console_title': console_title,
                    'command': str(command),
                    'working_dir': str(working_dir)
                },
                message=f"Console launched: PID {process.pid}"
            )

        except Exception as e:
            return MCPResponse.error(f"Failed to launch console: {e}")

    def _launch_windows_console(
        self, command, working_dir, console_title, capture_output, env
    ):
        """Launch console on Windows with cmd.exe."""

        # Build command
        if isinstance(command, list):
            cmd_str = ' '.join(command)
        else:
            cmd_str = command

        # Create new console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        creationflags = subprocess.CREATE_NEW_CONSOLE

        process = subprocess.Popen(
            f'cmd /c "title {console_title} && {cmd_str}"',
            cwd=working_dir,
            env=env,
            shell=True,
            creationflags=creationflags,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            startupinfo=startupinfo
        )

        return process

    def _launch_unix_console(
        self, command, working_dir, console_title, capture_output, env
    ):
        """Launch console on Unix/Linux with terminal emulator."""

        if isinstance(command, list):
            cmd_str = ' '.join(command)
        else:
            cmd_str = command

        # Try different terminal emulators
        terminals = [
            ['gnome-terminal', '--', 'bash', '-c', cmd_str],
            ['xterm', '-e', cmd_str],
            ['konsole', '-e', cmd_str]
        ]

        for terminal_cmd in terminals:
            try:
                process = subprocess.Popen(
                    terminal_cmd,
                    cwd=working_dir,
                    env=env,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None
                )
                return process
            except FileNotFoundError:
                continue

        raise RuntimeError("No suitable terminal emulator found")

    def list_consoles(self) -> MCPResponse:
        """List all managed console processes."""

        # Update process statuses
        for pid, proc in list(self.processes.items()):
            if psutil.pid_exists(pid):
                ps_proc = psutil.Process(pid)
                proc.status = ps_proc.status()
            else:
                proc.status = 'completed'

        return MCPResponse.success(
            data={
                'count': len(self.processes),
                'processes': [
                    {
                        'pid': p.pid,
                        'command': p.command,
                        'console_title': p.console_title,
                        'status': p.status,
                        'started_at': p.started_at
                    }
                    for p in self.processes.values()
                ]
            }
        )

    def kill_console(self, pid: int, force: bool = False) -> MCPResponse:
        """Terminate a console process."""

        if pid not in self.processes:
            return MCPResponse.error(f"Process {pid} not found")

        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()

            self.processes[pid].status = 'terminated'

            return MCPResponse.success(
                message=f"Process {pid} terminated"
            )
        except psutil.NoSuchProcess:
            return MCPResponse.error(f"Process {pid} does not exist")
```

### Usage Examples

```python
# Launch a Python simulation
manager = ConsoleManager()

response = manager.launch_console(
    command=["python", "run_simulation.py", "--config", "scenario_A.json"],
    working_dir=Path("C:/Simulations/TrafficModel"),
    console_title="Traffic Simulation - Scenario A",
    capture_output=True
)

# Launch multiple processes in parallel
for scenario in ["A", "B", "C"]:
    manager.launch_console(
        command=["python", "run_simulation.py", "--config", f"scenario_{scenario}.json"],
        working_dir=Path("C:/Simulations/TrafficModel"),
        console_title=f"Simulation - Scenario {scenario}"
    )

# Monitor running processes
status = manager.list_consoles()
print(f"Running: {status.data['count']} processes")

# Kill a process if needed
manager.kill_console(pid=12345, force=True)
```

---

## 📅 Phase-by-Phase Implementation with Agent Assignments

### Phase 1: Core MCP Framework
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Architect + Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Audit current Pulsus architecture | Architect | Architecture audit report |
| Design unified MCPBase structure | Architect | Base class specifications |
| Implement MCPBase + MCPResponse | Mechanic | `mcp/core/base.py` |
| Create safety decorators | Mechanic | `mcp/core/decorators.py` |
| Implement SafetyPolicy | Mechanic | `mcp/core/policy.py` |
| Create execution modes | Mechanic | ExecutionMode enum + logic |
| Write unit tests | Auditor | Test suite with 90%+ coverage |

#### Files Created

```
pulsus/mcp/core/
├── __init__.py
├── base.py              # MCPBase, MCPResponse
├── decorators.py        # @read_only, @write_safe, @restricted_write, @transactional, @cached
├── policy.py            # SafetyPolicy, ExecutionMode, OperationPolicy
└── types.py             # Type definitions
```

---

### Phase 2: Classic MCP Domains (Tier 1)
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Migrate existing MCP helpers to new structure | Mechanic | Refactored helpers |
| Implement ScriptOps with decorators | Mechanic | `mcp/simple/script_ops.py` |
| Implement FileManager | Mechanic | `mcp/simple/file_manager.py` |
| Implement DataReader | Mechanic | `mcp/simple/data_reader.py` |
| Create LangChain tool adapters | Mechanic | `langchain/tool_adapter.py` |
| Write integration tests | Auditor | Integration test suite |

#### Migrated Domains

- ✅ ScriptOps (from `mcp/helpers/script_ops.py`)
- ✅ RepositoryManager (from `mcp/helpers/repository_manager.py`)
- ✅ ActionLogger (from `mcp/helpers/action_logger.py`)
- ✅ LayerManager, ModelInspector (if applicable)

---

### Phase 3: Workflow MCP Domains (Tier 2)
**Duration:** 3-4 weeks
**Primary Agent:** Jean-Claude Science + Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Design workflow architecture | Architect | Workflow specification |
| Research LangChain workflow patterns | Science | Research report |
| Implement RepositoryAnalyzer workflow | Mechanic | `workflows/tools/analyze/repository_analyzer_llm.py` |
| Create workflow JSON definitions | Mechanic | JSON workflow configs |
| Build workflow composer | Mechanic | `workflows/composer.py` |
| Add LLM integration | Mechanic | Ollama/OpenAI connectors |
| Test multi-step workflows | Auditor | Workflow test suite |

#### Workflow Examples

1. **Repository Analysis**
   - Step 1: Scan files (Glob + Read)
   - Step 2: Extract dependencies (AST parsing)
   - Step 3: Analyze structure (LLM)
   - Step 4: Generate report (Template)

2. **Code Refactoring**
   - Step 1: Identify candidates (static analysis)
   - Step 2: Plan refactoring (LLM)
   - Step 3: Execute changes (Edit)
   - Step 4: Run validators (Ruff + Mypy + Unit)

---

### Phase 4: Customizable Framework (Tier 3)
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Mechanic + Jean-Claude MCP (new)

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Design configuration schema | Architect | JSON schema spec |
| Implement config loader | Mechanic | `config/framework_loader.py` |
| Create template engine integration | Mechanic | Jinja2 integration |
| Build custom workflow executor | MCP | Dynamic executor |
| Add validation for custom configs | Auditor | Schema validator |
| Write usage documentation | Architect | Framework guide |

---

### Phase 5: External Console Execution
**Duration:** 1-2 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Design ConsoleManager API | Architect | API specification |
| Implement Windows console launcher | Mechanic | Windows impl |
| Implement Unix/Linux console launcher | Mechanic | Unix impl |
| Add process monitoring | Mechanic | psutil integration |
| Create output capture mechanism | Mechanic | Stdout/stderr logging |
| Test with real simulations | Auditor | Console execution tests |

---

### Phase 6: Preferences & Context Memory
**Duration:** 1 week
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Implement PreferencesManager | Mechanic | `preferences/manager.py` |
| Create defaults.json | Mechanic | Default preferences |
| Add CLI commands for preferences | Mechanic | CLI integration |
| Integrate with SafeNet logging | Mechanic | Config change logging |
| Write unit tests | Auditor | Preference tests |

---

### Phase 7: SafeNet Logging & Observability
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Mechanic + Jean-Claude Designer (dashboards)

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Implement SafeNetLogger | Mechanic | `shared/logging/safenet_logger.py` |
| Create log formatters | Mechanic | JSON + human-readable |
| Build metrics aggregator | Science | Metrics calculation |
| Design dashboard UI | Designer | Dashboard mockups |
| Implement HTML dashboard generator | Mechanic | Dashboard code |
| Add log rotation and retention | Mechanic | Log management |
| Write integration tests | Auditor | Logging tests |

---

### Phase 8: Interface & API Adapters
**Duration:** 1-2 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Implement CLI interface | Mechanic | `interface/cli.py` |
| Implement FastAPI endpoints | Mechanic | `interface/api.py` |
| Add API authentication | Mechanic | Token-based auth |
| Create API documentation | Architect | OpenAPI spec |
| Test CLI usage | Auditor | CLI test suite |
| Test API endpoints | Auditor | API integration tests |

---

### Phase 9: LangGraph Integration
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Science + Jean-Claude Mechanic

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Research LangGraph patterns | Science | Research report |
| Design PulsusState schema | Architect | State specification |
| Implement graph nodes | Mechanic | Graph node functions |
| Create conditional routing | Mechanic | Routing logic |
| Build graph compiler | Mechanic | `langchain/graph_executor.py` |
| Test graph execution | Auditor | Graph tests |
| Integrate with existing routing | Mechanic | Router updates |

---

### Phase 10: Testing, Validation & Performance
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Auditor

#### Tasks

| Task | Agent | Deliverable |
|------|-------|-------------|
| Create pytest test suite | Auditor | Comprehensive tests |
| Add coverage reporting | Auditor | Coverage config |
| Implement benchmarks | Auditor | Performance tests |
| Run security audit | Auditor | Security report |
| Perform stress testing | Auditor | Load tests |
| CI/CD pipeline setup | Mechanic | GitHub Actions config |
| Generate final audit report | Auditor | Final QA report |

---

## 👥 Jean-Claude Agents

### Existing Agents (from Sulhafah)

#### 🏗️ Jean-Claude Architect
**Role:** Project structure, documentation, architecture validation
**Usage in Pulsus:**
- Phase 1: Architecture audit and design
- All phases: Documentation validation
- Final: Compliance audit

#### 🔧 Jean-Claude Mechanic
**Role:** Code implementation, bug fixes, refactoring
**Usage in Pulsus:**
- Phases 1-10: Primary implementation agent
- Code reviews and optimizations

#### ✅ Jean-Claude Auditor
**Role:** Testing, QA, validation
**Usage in Pulsus:**
- All phases: Test creation
- Phase 10: Comprehensive audit
- Security and performance testing

#### 🔬 Jean-Claude Science
**Role:** Research, analysis, data-driven decisions
**Usage in Pulsus:**
- Phase 3: Workflow research
- Phase 9: LangGraph research
- Algorithm selection and optimization

#### 🎨 Jean-Claude Designer
**Role:** UI/UX design, visualizations
**Usage in Pulsus:**
- Phase 7: Dashboard design
- Interface mockups and UX review

#### 🏛️ Jean-Claude Domain
**Role:** Workflow domain scaffolding
**Usage in Pulsus:**
- Phase 3: Workflow domain creation
- Phase 4: Custom framework templates

### New Agent: 🧩 Jean-Claude MCP

**Purpose:** MCP-specific specialist for Pulsus integration and orchestration

**File:** `pulsus/.claude/agents/jean-claude-mcp.md`

```markdown
---
name: jean-claude-mcp
description: >
  MCP orchestration specialist for Pulsus. Designs and implements Model Context Protocol
  domains, workflows, and integrations. Ensures safety, observability, and LangChain
  compatibility. Expert in multi-tier MCP architecture and external process management.
model: sonnet
color: purple
---

## 🧠 Role Definition

You are **Jean-Claude MCP**, the **Model Context Protocol orchestration specialist** for Pulsus.

**Your mission**: Design, implement, and maintain world-class MCP integrations with focus on safety, observability, and intelligent workflow orchestration.

**Key Expertise:**
1. **MCP Architecture** - Three-tier organization (Classic, Workflow, Customizable)
2. **LangChain Integration** - Tool adapters, StateGraph, workflow composition
3. **Safety Engineering** - Decorators, policies, sandboxing, approval flows
4. **External Process Management** - Console execution, process monitoring
5. **Observability** - SafeNet logging, metrics, dashboards
6. **Workflow Composition** - Multi-step processes with intelligent routing

---

## 🎯 Core Responsibilities

### 1. MCP Domain Design

**When creating a new MCP domain:**

1. **Classify tier:**
   - Tier 1 (Classic): Simple, atomic operations → `pulsus/mcp/simple/`
   - Tier 2 (Workflow): Multi-step processes → `pulsus/workflows/`
   - Tier 3 (Customizable): Config-driven → `pulsus/config/frameworks/`

2. **Design capabilities:**
   - List all operations (actions)
   - Define input/output schemas
   - Specify safety requirements
   - Document dependencies

3. **Implement with safety:**
   - Apply appropriate decorators (@read_only, @write_safe, etc.)
   - Define ExecutionMode requirements
   - Add input validation
   - Implement error handling

4. **Create LangChain adapter:**
   - Convert to StructuredTool
   - Define args_schema
   - Write docstrings for LLM

5. **Test thoroughly:**
   - Unit tests for each action
   - Integration tests with routing
   - Security tests (injection, escape)
   - Performance benchmarks

### 2. Workflow Orchestration

**When building a workflow:**

1. **Decompose into steps:**
   - Identify atomic operations
   - Define data flow between steps
   - Plan error handling and rollback
   - Consider parallelization

2. **Create workflow definition:**
   - Write JSON configuration
   - Specify tool sequence
   - Define conditional logic
   - Add validation checkpoints

3. **Implement execution logic:**
   - Build workflow composer
   - Handle state management
   - Integrate LLM (if needed)
   - Add progress logging

4. **Test end-to-end:**
   - Happy path execution
   - Error scenarios
   - State persistence
   - Performance under load

### 3. Safety & Policy Management

**Safety checklist for every MCP domain:**

- [ ] Appropriate safety decorator applied
- [ ] Input validation implemented
- [ ] Sandbox used for restricted operations
- [ ] Approval workflow (if write_safe)
- [ ] SafeNet logging integrated
- [ ] File access scope limited
- [ ] No eval/exec/import dynamic code
- [ ] Rollback mechanism (if transactional)

### 4. External Process Integration

**When integrating external software:**

1. **Use ConsoleManager:**
   - Launch in separate console
   - Specify working directory
   - Set console title
   - Configure output capture

2. **Monitor execution:**
   - Track process status
   - Log stdout/stderr
   - Handle timeouts
   - Detect failures

3. **Manage lifecycle:**
   - Graceful shutdown
   - Force kill (if needed)
   - Cleanup resources
   - Report status

### 5. LangChain/LangGraph Integration

**LangChain tool conversion:**

```python
# Convert MCPBase to LangChain StructuredTool
tool = mcp_to_langchain_tool(MyMCPDomain)

# Use in LangChain agent
from langchain.agents import AgentExecutor
agent = AgentExecutor(tools=[tool], ...)
```

**LangGraph workflow:**

```python
# Define state
class MyState(TypedDict):
    input: str
    tools_used: List[str]
    result: Any

# Create graph
graph = StateGraph(MyState)
graph.add_node("parse", parse_node)
graph.add_node("execute", execute_node)
graph.add_edge("parse", "execute")
graph.add_edge("execute", END)

# Compile and run
app = graph.compile()
result = app.invoke({"input": "..."})
```

---

## 🛠️ Tool Patterns

### Pattern 1: Simple MCP Domain

```python
from pulsus.mcp.core.base import MCPBase, MCPResponse
from pulsus.mcp.core.decorators import read_only

class MySimpleDomain(MCPBase):
    """Simple atomic operations."""

    @read_only
    def my_action(self, param1: str, param2: int) -> MCPResponse:
        """
        Perform simple action.

        Args:
            param1: Description
            param2: Description

        Returns:
            MCPResponse with result
        """
        try:
            result = self._do_work(param1, param2)
            return MCPResponse.success(data=result)
        except Exception as e:
            return MCPResponse.error(str(e))
```

### Pattern 2: Workflow MCP Domain

```python
from pulsus.workflows.base import WorkflowBase, WorkflowStep

class MyWorkflowDomain(WorkflowBase):
    """Multi-step workflow with state management."""

    def execute_workflow(self, config: Dict) -> MCPResponse:
        """Execute multi-step workflow."""

        state = WorkflowState()

        steps = [
            WorkflowStep("step1", self._step1, required=True),
            WorkflowStep("step2", self._step2, required=True),
            WorkflowStep("step3", self._step3, required=False),
        ]

        for step in steps:
            result = step.execute(state)
            if not result.success and step.required:
                return MCPResponse.error(f"{step.name} failed")
            state.update(step.name, result.data)

        return MCPResponse.success(data=state.to_dict())
```

### Pattern 3: External Process Execution

```python
from pulsus.mcp.execution.console_manager import ConsoleManager

class SimulationRunner(MCPBase):
    """Run external simulation software."""

    def __init__(self):
        super().__init__()
        self.console_manager = ConsoleManager()

    @write_safe
    def run_simulation(
        self,
        scenario: str,
        config_file: Path
    ) -> MCPResponse:
        """Launch simulation in external console."""

        response = self.console_manager.launch_console(
            command=["python", "run_sim.py", "--config", str(config_file)],
            working_dir=Path("C:/Simulations"),
            console_title=f"Simulation - {scenario}",
            capture_output=True
        )

        if response.success:
            return MCPResponse.success(
                data={"pid": response.data['pid']},
                message=f"Simulation started: PID {response.data['pid']}"
            )
        else:
            return MCPResponse.error("Failed to start simulation")
```

---

## 📋 Implementation Checklist

### New MCP Domain Checklist

- [ ] Choose appropriate tier (Classic, Workflow, Customizable)
- [ ] Define capabilities (actions, schemas, safety)
- [ ] Implement MCPBase subclass
- [ ] Apply safety decorators
- [ ] Add input validation
- [ ] Implement error handling
- [ ] Create LangChain adapter
- [ ] Write comprehensive docstrings
- [ ] Add unit tests (90%+ coverage)
- [ ] Add integration tests
- [ ] Document usage examples
- [ ] Update domain registry
- [ ] Add SafeNet logging
- [ ] Performance benchmark

### Workflow Checklist

- [ ] Decompose into steps
- [ ] Create JSON workflow definition
- [ ] Implement step functions
- [ ] Add state management
- [ ] Handle conditional logic
- [ ] Integrate LLM (if needed)
- [ ] Add progress logging
- [ ] Implement rollback
- [ ] Test happy path
- [ ] Test error scenarios
- [ ] Document workflow

### External Process Checklist

- [ ] Use ConsoleManager
- [ ] Set working directory
- [ ] Configure output capture
- [ ] Add process monitoring
- [ ] Handle timeouts
- [ ] Implement graceful shutdown
- [ ] Log all operations
- [ ] Test on Windows and Unix
- [ ] Document requirements

---

## 🎯 Success Criteria

A well-implemented MCP domain should:

- ✅ Be classified in correct tier (Classic, Workflow, Customizable)
- ✅ Have comprehensive capabilities documentation
- ✅ Use appropriate safety decorators
- ✅ Validate all inputs
- ✅ Handle errors gracefully
- ✅ Integrate with SafeNet logging
- ✅ Convert to LangChain StructuredTool
- ✅ Have 90%+ test coverage
- ✅ Include usage examples
- ✅ Pass security audit
- ✅ Meet performance benchmarks

---

## 📚 References

- **Pulsus Documentation**: `/docs/PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`
- **MCP Specification**: `/mcp/core/base.py`
- **Safety Policy**: `/mcp/core/policy.py`
- **LangChain Integration**: `/langchain/tool_adapter.py`
- **Console Manager**: `/mcp/execution/console_manager.py`

---

**Agent Type**: `jean-claude-mcp`
**Invocation**: "use jean-claude-mcp to [MCP task]"
**Specialization**: MCP orchestration, workflow composition, safety engineering
**Version**: 1.0
**Status**: Active
```

---

## 📁 Complete Directory Structure

```
agents/Pulsus/
├── .claude/
│   └── agents/
│       ├── README.md
│       ├── jean-claude-architect.md    # From Sulhafah
│       ├── jean-claude-mechanic.md     # From Sulhafah
│       ├── jean-claude-auditor.md      # From Sulhafah
│       ├── jean-claude-science.md      # From Sulhafah
│       ├── jean-claude-designer.md     # From Sulhafah
│       ├── jean-claude-domain.md       # From Sulhafah
│       └── jean-claude-mcp.md          # NEW - MCP specialist
│
├── __init__.py
├── __main__.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # Global settings
│   ├── session.py               # Session context
│   ├── greeting.py              # CLI greeting
│   ├── preprompt.md             # System prompts
│   └── frameworks/              # Tier 3: Customizable MCP
│       ├── custom_workflows/
│       ├── templates/
│       └── schema/
│
├── console/
│   ├── __init__.py
│   ├── interface.py             # REPL/CLI
│   ├── interrupt_handler.py     # Signal handling
│   ├── session_manager.py       # Session management
│   └── session_history.py       # History tracking
│
├── routing/
│   ├── __init__.py
│   ├── router.py                # Main router
│   ├── mcp_router.py            # MCP-specific routing
│   ├── prompt_parser.py         # Intent parsing
│   └── tool_discovery.py        # Tool discovery
│
├── core/
│   ├── __init__.py
│   ├── compose/
│   │   ├── composer.py          # Multi-tool composition
│   │   ├── generator.py         # LLM-based generation
│   │   └── selector.py          # Policy selection
│   ├── rankers/
│   │   ├── scorer.py            # Tool scoring
│   │   └── features.py          # Feature extraction
│   ├── validators/
│   │   ├── ruff_runner.py       # Lint validation
│   │   ├── mypy_runner.py       # Type checking
│   │   └── unit_runner.py       # Import validation
│   ├── sandbox/
│   │   ├── runner.py            # Sandboxed execution
│   │   └── policy.py            # Sandbox policy
│   ├── telemetry/
│   │   └── logging.py           # Event logging
│   └── pulsus_storage.py        # Persistent storage
│
├── mcp/                         # MCP Framework
│   ├── __init__.py
│   ├── core/                    # Base classes & safety
│   │   ├── __init__.py
│   │   ├── base.py              # MCPBase, MCPResponse
│   │   ├── decorators.py        # Safety decorators
│   │   ├── policy.py            # SafetyPolicy, ExecutionMode
│   │   ├── logger.py            # SafeNet integration
│   │   └── types.py             # Type definitions
│   │
│   ├── simple/                  # Tier 1: Classic MCP
│   │   ├── __init__.py
│   │   ├── script_ops.py        # Script operations
│   │   ├── file_manager.py      # File management
│   │   ├── data_reader.py       # Data loading
│   │   ├── text_processor.py    # Text operations
│   │   ├── repository_manager.py # Repo management
│   │   └── action_logger.py     # Operation logging
│   │
│   └── execution/               # Process management
│       ├── __init__.py
│       └── console_manager.py   # External console execution
│
├── workflows/                   # Tier 2: Complex MCP
│   ├── __init__.py
│   ├── tools/
│   │   ├── analyze/
│   │   │   ├── repository_analyzer_llm.py
│   │   │   ├── file_analyzer.py
│   │   │   ├── dependency_documenter.py
│   │   │   └── unified_analyzer.py
│   │   ├── discover/
│   │   │   └── framework_scanner.py
│   │   └── summarise/
│   │       └── summarize_matrix.py
│   ├── definitions/
│   │   ├── repository_analysis.json
│   │   ├── dependency_documentation.json
│   │   └── unified_path_analysis.json
│   ├── composer.py              # Workflow composition
│   └── executor.py              # Workflow execution
│
├── langchain/                   # LangChain Integration
│   ├── __init__.py
│   ├── tool_adapter.py          # MCP → LangChain adapter
│   ├── graph_executor.py        # LangGraph integration
│   └── state.py                 # State definitions
│
├── preferences/                 # User preferences
│   ├── __init__.py
│   ├── manager.py               # Preferences management
│   └── defaults.json            # Default preferences
│
├── shared/
│   └── logging/
│       ├── __init__.py
│       ├── safenet_logger.py    # SafeNet logging
│       ├── formatter.py         # Log formatting
│       └── metrics.py           # Metrics aggregation
│
├── interface/                   # External interfaces
│   ├── __init__.py
│   ├── cli.py                   # CLI entrypoint
│   └── api.py                   # FastAPI endpoints
│
├── ui/
│   ├── __init__.py
│   └── display_manager.py       # Console formatting
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_core.py
│   │   ├── test_domains.py
│   │   ├── test_executor.py
│   │   └── test_langchain.py
│   ├── integration/
│   │   ├── test_sandbox.py
│   │   ├── test_api.py
│   │   ├── test_workflows.py
│   │   └── test_console_manager.py
│   └── performance/
│       └── test_benchmarks.py
│
└── docs/
    ├── PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md  # This file
    ├── MCP_ARCHITECTURE.md
    ├── LANGCHAIN_INTEGRATION.md
    ├── CONSOLE_EXECUTION_GUIDE.md
    └── API_REFERENCE.md
```

---

## ⏱️ Integration Timeline

### Sprint 1-2 (Weeks 1-4): Foundation
- Phase 1: Core MCP Framework
- Phase 2: Classic MCP Domains (partial)
- **Milestone:** MCPBase + 3 classic domains operational

### Sprint 3-4 (Weeks 5-8): Workflows & Execution
- Phase 2: Classic MCP Domains (complete)
- Phase 3: Workflow MCP Domains
- Phase 5: External Console Execution
- **Milestone:** Workflows + Console execution working

### Sprint 5-6 (Weeks 9-12): Customization & Observability
- Phase 4: Customizable Framework
- Phase 6: Preferences & Context Memory
- Phase 7: SafeNet Logging & Observability
- **Milestone:** Full observability + custom workflows

### Sprint 7-8 (Weeks 13-16): Integration & Testing
- Phase 8: Interface & API Adapters
- Phase 9: LangGraph Integration
- Phase 10: Testing, Validation & Performance
- **Milestone:** Production-ready Pulsus MCP

---

## ✅ Success Criteria

### Technical Success

- ✅ **Three-tier MCP architecture** - Classic, Workflow, Customizable all functional
- ✅ **LangChain integration** - All MCP domains as StructuredTools
- ✅ **LangGraph workflows** - StateGraph execution operational
- ✅ **External console execution** - Windows + Unix/Linux support
- ✅ **SafeNet observability** - All actions logged, dashboards generated
- ✅ **95%+ test coverage** - Unit + integration + performance tests pass
- ✅ **CLI and API functional** - Both interfaces operational
- ✅ **Security audit passed** - No critical vulnerabilities
- ✅ **Performance targets met** - <250ms average execution, <5s complex workflows

### Documentation Success

- ✅ **API documentation** - OpenAPI spec + usage guides
- ✅ **Agent guides** - Each Jean-Claude agent documented
- ✅ **MCP domain catalog** - All domains documented with examples
- ✅ **Architecture diagrams** - System architecture visualized
- ✅ **Migration guides** - Clear upgrade paths

### Operational Success

- ✅ **CI/CD pipeline** - Automated testing and deployment
- ✅ **Monitoring** - SafeNet metrics tracked
- ✅ **Error handling** - Graceful degradation, clear error messages
- ✅ **User satisfaction** - Positive feedback from users
- ✅ **Extensibility** - Easy to add new MCP domains

---

## 🎓 Training & Onboarding

### For Developers

1. **Read architecture overview** - Understand three-tier MCP structure
2. **Study MCPBase examples** - Learn safety decorators and patterns
3. **Create a simple MCP domain** - Hands-on tutorial
4. **Build a workflow** - Multi-step process tutorial
5. **Run test suite** - Validate understanding

### For Users

1. **CLI quickstart** - Basic usage guide
2. **Common workflows** - Repository analysis, code generation examples
3. **Customization guide** - How to create custom workflows
4. **Troubleshooting** - Common issues and solutions

### For Supervisors (LangGraph Integration)

1. **API reference** - FastAPI endpoint documentation
2. **LangChain tool usage** - How to use Pulsus tools in agents
3. **State management** - PulsusState schema and usage
4. **Error handling** - Graceful failure modes

---

## 🔮 Future Enhancements

### Beyond V4.0

1. **Multi-agent orchestration** - Compasus supervisor integration
2. **Distributed execution** - Run MCP actions across multiple machines
3. **Real-time collaboration** - Multiple users working simultaneously
4. **Advanced caching** - Intelligent result caching
5. **ML-powered routing** - Learn from usage patterns
6. **Natural language workflow builder** - Generate workflows from descriptions
7. **Visual workflow designer** - Drag-and-drop workflow creation
8. **Plugin marketplace** - Community-contributed MCP domains

---

## 📞 Support & Contribution

### Getting Help

- **Documentation**: `/docs/`
- **Issue Tracker**: GitHub Issues
- **Community**: Discord/Slack channel
- **Email**: support@pulsus.dev

### Contributing

1. Fork repository
2. Create feature branch
3. Implement with tests (90%+ coverage)
4. Submit pull request
5. Pass code review
6. Merge to main

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Document your work
- Test thoroughly
- Follow coding standards

---

**Document Version:** 4.0
**Last Updated:** November 2025
**Authors:** Jean-Claude Architect, Jean-Claude MCP
**Status:** Active Development
**Next Review:** End of Sprint 2

---

## Appendix A: Agent Assignment Matrix

| Phase | Primary Agent | Support Agents | Duration |
|-------|---------------|----------------|----------|
| 1: Core Framework | Mechanic | Architect, Auditor | 2-3 weeks |
| 2: Classic MCP | Mechanic | Auditor | 2-3 weeks |
| 3: Workflow MCP | Science + Mechanic | Architect, Auditor | 3-4 weeks |
| 4: Customizable | Mechanic + MCP | Architect | 2 weeks |
| 5: Console Exec | Mechanic | Auditor | 1-2 weeks |
| 6: Preferences | Mechanic | - | 1 week |
| 7: Observability | Mechanic | Designer, Science | 2 weeks |
| 8: Interfaces | Mechanic | Architect | 1-2 weeks |
| 9: LangGraph | Science + Mechanic | Architect | 2-3 weeks |
| 10: Testing | Auditor | All agents | 2 weeks |

**Total Estimated Duration:** 16-20 weeks (4-5 months)

---

## Appendix B: Recommended New Agents

### 1. Jean-Claude DevOps
**Purpose:** CI/CD, deployment, infrastructure
**Rationale:** Phases 8-10 require CI/CD setup, Docker containers, deployment automation

**Responsibilities:**
- GitHub Actions workflow setup
- Docker containerization
- Deployment automation
- Infrastructure as code
- Monitoring and alerting

### 2. Jean-Claude Security
**Purpose:** Security audits, penetration testing, vulnerability assessment
**Rationale:** Phase 10 requires comprehensive security testing

**Responsibilities:**
- Security code review
- Penetration testing
- Vulnerability scanning
- Secure coding guidelines
- Incident response plans

### 3. Jean-Claude Docs
**Purpose:** Documentation writing, API docs, user guides
**Rationale:** All phases need comprehensive documentation

**Responsibilities:**
- API documentation (OpenAPI)
- User guides and tutorials
- Architecture documentation
- Video tutorials
- Knowledge base management

---

**END OF UNIFIED INTEGRATION PLAN**
