# Pulsus Architecture

**Version**: 0.1.0
**Status**: Phase 1 Complete, Phase 2 In Progress
**Last Updated**: November 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [System Architecture](#system-architecture)
4. [Three-Tier MCP Organization](#three-tier-mcp-organization)
5. [Component Architecture](#component-architecture)
6. [Data Flow](#data-flow)
7. [Safety & Security](#safety--security)
8. [Integration Points](#integration-points)
9. [Extension Points](#extension-points)
10. [Deployment Architecture](#deployment-architecture)

---

## Overview

Pulsus is a **Model Context Protocol (MCP) execution agent** that transforms natural language into executable actions through a sophisticated three-tier architecture. It combines deterministic routing with intelligent LLM-based decision making to provide safe, observable, and extensible MCP operations.

### Vision

Transform Pulsus from a routing layer into a **complete MCP orchestration platform** that:

- Routes natural language to MCP actions with intelligent tool discovery
- Orchestrates complex multi-step workflows with state management
- Integrates with external processes and software
- Adapts to user preferences while maintaining safety guarantees
- Provides full observability through comprehensive logging
- Exposes multiple interfaces (CLI, API, LangGraph)

### Key Capabilities

- **Smart Routing**: Intent parsing → Tool discovery → Execution
- **Three-Tier MCP**: Classic (simple), Workflow (complex), Customizable (user-defined)
- **Safety First**: Multi-level decorators, sandboxing, approval workflows
- **LangChain Native**: Built on LangChain Tools and LangGraph StateGraph
- **Observable**: Every action logged with SafeNet
- **Extensible**: Plugin architecture for custom MCP domains

---

## Core Principles

### 1. Modular Architecture
Clear separation of concerns across layers:
- **Core**: Base classes, safety, validation
- **MCP**: Domain implementations (Tier 1, 2, 3)
- **Routing**: Intent parsing and tool discovery
- **Execution**: Process management and sandboxing
- **Interface**: CLI, API, LangGraph adapters

### 2. Safety First
Multi-layered safety enforcement:
- **Decorators**: `@read_only`, `@write_safe`, `@restricted_write`
- **Policies**: ExecutionMode (PLAN, EXECUTE, UNSAFE)
- **Sandboxing**: Isolated execution environments
- **Approval**: User confirmation for destructive operations

### 3. LangChain Native
Built on industry-standard tools:
- All MCP domains are LangChain `StructuredTool` instances
- LangGraph `StateGraph` for workflow orchestration
- Compatible with any LangChain-based system

### 4. Deterministic + Adaptive
Predictable execution with intelligent fallback:
- **SELECT**: Direct tool execution for clear matches
- **COMPOSE**: Multi-tool composition for complex requests
- **GENERATE**: LLM-based routing for ambiguous queries

### 5. Observable
Complete execution transparency:
- Every MCP operation logged to SafeNet
- Metrics tracked (latency, success rate, usage)
- Dashboards for visualization
- Execution traces for debugging

### 6. Extensible
Easy to add new capabilities:
- Plugin architecture for MCP domains
- User-defined workflows via JSON/YAML
- Custom safety policies
- Flexible routing strategies

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
│           (Natural Language / CLI / API / LangGraph)            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ROUTING LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Intent       │→ │ Tool         │→ │ Routing Policy      │  │
│  │ Parser       │  │ Discovery    │  │ (SELECT/COMPOSE/GEN)│  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐       ┌─────────┐      ┌──────────┐
   │  TIER 1 │       │  TIER 2 │      │  TIER 3  │
   │ Classic │       │Workflow │      │Customized│
   │   MCP   │       │   MCP   │      │   MCP    │
   └────┬────┘       └────┬────┘      └────┬─────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP EXECUTION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Safety       │→ │ Execution    │→ │ Result              │  │
│  │ Enforcement  │  │ Environment  │  │ Aggregation         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ SafeNet      │  │ Metrics      │  │ Dashboard            │  │
│  │ Logger       │  │ Aggregator   │  │ Generator            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Three-Tier MCP Organization

Pulsus organizes MCP operations into three tiers based on complexity and customization needs:

### Tier 1: Classic MCP (Simple Operations)

**Location**: `mcp/simple/`
**Characteristics**: Atomic, deterministic operations with clear inputs/outputs

**Examples**:
- `ScriptOps`: Read/write/format Python files
- `RepositoryOps`: Git operations, file scanning
- `DataReader`: Load CSV, JSON, Parquet files
- `FileManager`: Create, delete, move files

**Architecture**:
```python
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe

class MyDomain(MCPBase):
    """Simple atomic operations"""

    @read_only
    def my_read_action(self, param: str) -> MCPResponse:
        """Safe read-only operation"""
        return MCPResponse.success(data=result)

    @write_safe
    def my_write_action(self, param: str) -> MCPResponse:
        """Write operation with safety checks"""
        return MCPResponse.success(data=result)
```

### Tier 2: Workflow MCP (Complex Operations)

**Location**: `workflows/`
**Characteristics**: Multi-step processes with state management and decision trees

**Examples**:
- `RepositoryAnalyzer`: Scan → Parse → Analyze → Report
- `CodeRefactorer`: Plan → Execute → Validate → Rollback
- `DependencyDocumenter`: Trace → Document → Export
- `UnifiedAnalyzer`: Composite analysis workflows

**Architecture**:
```python
from workflows.base import WorkflowBase, WorkflowStep, WorkflowState

class MyWorkflow(WorkflowBase):
    """Multi-step workflow with state"""

    def execute_workflow(self, config: Dict) -> MCPResponse:
        state = WorkflowState()

        steps = [
            WorkflowStep("scan", self._scan, required=True),
            WorkflowStep("analyze", self._analyze, required=True),
            WorkflowStep("report", self._report, required=False),
        ]

        for step in steps:
            result = step.execute(state)
            if not result.success and step.required:
                return MCPResponse.error(f"{step.name} failed")
            state.update(step.name, result.data)

        return MCPResponse.success(data=state.to_dict())
```

### Tier 3: Customizable MCP (User-Defined)

**Location**: `config/frameworks/`
**Characteristics**: JSON/YAML-configured workflows loaded dynamically

**Example Configuration**:
```json
{
  "name": "my_custom_analysis",
  "description": "Custom repository analysis",
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
      "config": {"depth": 2}
    },
    {
      "name": "generate_report",
      "tool": "ReportGenerator",
      "config": {
        "template": "custom_report.j2",
        "format": "markdown"
      }
    }
  ]
}
```

---

## Component Architecture

### Core Framework (`mcp/core/`)

#### MCPBase
Abstract base class for all MCP operations.

```python
class MCPBase(ABC):
    """Base class for all MCP operations"""

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return domain capabilities"""
        pass

    def execute(self, action: str, **params) -> MCPResponse:
        """Execute an action with parameters"""
        pass
```

#### MCPResponse
Standardized response structure.

```python
@dataclass
class MCPResponse:
    success: bool
    context: Dict[str, Any]
    data: Any
    error: Optional[str]
    trace: List[str]
    status: MCPStatus
    metadata: Dict[str, Any]
```

#### Safety Decorators
Multi-level safety enforcement.

```python
@read_only           # No modifications allowed
@write_safe          # User approval required
@restricted_write    # Limited file types/locations
@transactional       # Rollback on failure
@cached              # Cache results
```

#### SafetyPolicy
Execution mode enforcement.

```python
class ExecutionMode(Enum):
    PLAN = "plan"       # Dry run, no execution
    EXECUTE = "execute" # Normal execution
    UNSAFE = "unsafe"   # Bypass safety (admin only)
```

### Routing System (`routing/`)

#### Intent Parser
Extracts intent from natural language.

```python
class IntentParser:
    def parse(self, query: str) -> Intent:
        """Parse user query into structured intent"""
        return Intent(
            domain="script_ops",
            action="read_script",
            params={"path": "example.py"}
        )
```

#### Tool Discovery
Finds matching MCP domains.

```python
class ToolDiscovery:
    def discover(self, intent: Intent) -> List[MCPDomain]:
        """Find MCP domains matching intent"""
        candidates = self._find_candidates(intent)
        scored = self._score_candidates(candidates, intent)
        return sorted(scored, key=lambda x: x.score, reverse=True)
```

#### Routing Policy
Selects execution strategy.

```python
class RoutingPolicy:
    def select_policy(self, candidates: List[MCPDomain]) -> str:
        """Choose SELECT, COMPOSE, or GENERATE"""
        if len(candidates) == 1 and candidates[0].score > 0.9:
            return "SELECT"
        elif len(candidates) > 1:
            return "COMPOSE"
        else:
            return "GENERATE"
```

### LangChain Integration (`langchain/`)

#### Tool Adapter
Converts MCP domains to LangChain tools.

```python
def mcp_to_langchain_tool(mcp_class: Type[MCPBase]) -> StructuredTool:
    """Convert MCPBase to LangChain StructuredTool"""
    instance = mcp_class()
    capabilities = instance.get_capabilities()

    def execute_wrapper(**kwargs) -> Dict[str, Any]:
        response = instance.execute(
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

#### StateGraph Integration
LangGraph workflow execution.

```python
class PulsusState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "History"]
    parsed_intent: Dict[str, Any]
    selected_tools: List[StructuredTool]
    execution_results: List[MCPResponse]
    next_action: str

def create_pulsus_graph() -> StateGraph:
    workflow = StateGraph(PulsusState)
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("discover_tools", discover_tools_node)
    workflow.add_node("execute_tools", execute_tools_node)
    # ... edges and conditional routing
    return workflow.compile()
```

### External Execution (`mcp/execution/`)

#### ConsoleManager
Manages external processes.

```python
class ConsoleManager(MCPBase):
    """Launch and manage external processes"""

    @write_safe
    def launch_console(
        self,
        command: str,
        working_dir: Path,
        console_title: str,
        capture_output: bool = False
    ) -> MCPResponse:
        """Launch process in separate console"""
        # Platform-specific implementation
        # Windows: CREATE_NEW_CONSOLE
        # Unix: gnome-terminal / xterm
        pass
```

---

## Data Flow

### 1. Request Flow

```
User Query
    ↓
Intent Parser → Intent(domain, action, params)
    ↓
Tool Discovery → [MCPDomain1, MCPDomain2, ...]
    ↓
Routing Policy → SELECT / COMPOSE / GENERATE
    ↓
Execution Strategy
    ↓
    ├→ SELECT: Single tool execution
    ├→ COMPOSE: Multi-tool composition
    └→ GENERATE: LLM-based dynamic routing
    ↓
Safety Enforcement
    ↓
    ├→ Check decorator (@read_only, @write_safe)
    ├→ Check execution mode (PLAN, EXECUTE, UNSAFE)
    ├→ Request approval (if needed)
    └→ Apply sandboxing (if restricted)
    ↓
MCP Execution
    ↓
MCPResponse(success, data, context, trace)
    ↓
SafeNet Logging
    ↓
Result to User
```

### 2. Data Structures

#### Intent
```python
@dataclass
class Intent:
    domain: str           # Target MCP domain
    action: str           # Action to execute
    params: Dict[str, Any]  # Action parameters
    confidence: float     # Parsing confidence
    alternatives: List[Intent]  # Alternative interpretations
```

#### MCPResponse
```python
@dataclass
class MCPResponse:
    success: bool         # Operation succeeded
    context: Dict         # Execution context
    data: Any            # Result data
    error: Optional[str]  # Error message
    trace: List[str]     # Execution trace
    status: MCPStatus    # Detailed status
    metadata: Dict       # Timestamps, metrics
```

---

## Safety & Security

### 1. Decorator-Based Safety

```python
@read_only
def safe_read(self, path: str) -> MCPResponse:
    """Guaranteed read-only, no modifications"""
    pass

@write_safe
def controlled_write(self, path: str, content: str) -> MCPResponse:
    """Requires approval, limited scope"""
    pass

@restricted_write(file_types=[".py", ".json"], platform="linux")
def limited_write(self, path: str, content: str) -> MCPResponse:
    """Restricted to specific file types and platforms"""
    pass

@transactional(rollback_on_error=True)
def atomic_operation(self, params: Dict) -> MCPResponse:
    """Rolls back all changes if any step fails"""
    pass
```

### 2. Execution Modes

```python
class ExecutionMode(Enum):
    PLAN = "plan"       # Dry run - show what would happen
    EXECUTE = "execute" # Normal execution
    UNSAFE = "unsafe"   # Bypass safety (admin only)

# Usage
with execution_mode(ExecutionMode.PLAN):
    result = script_ops.write_script(...)  # Shows plan, doesn't execute
```

### 3. Sandboxing

```python
class SandboxRunner:
    """Execute operations in isolated environment"""

    def run_sandboxed(
        self,
        operation: Callable,
        allowed_paths: List[Path],
        allowed_network: bool = False
    ) -> MCPResponse:
        """Run with restricted access"""
        # Create isolated environment
        # Restrict file system access
        # Block network (optional)
        # Execute operation
        # Clean up
        pass
```

### 4. Approval Workflows

```python
class ApprovalManager:
    """Handle user approvals for sensitive operations"""

    def request_approval(
        self,
        operation: str,
        details: Dict,
        risk_level: str
    ) -> bool:
        """Request user approval for operation"""
        # Display operation details
        # Show risk assessment
        # Request confirmation
        # Log approval decision
        pass
```

---

## Integration Points

### 1. LangChain Tools

Any LangChain agent can use Pulsus MCP domains:

```python
from langchain.agents import AgentExecutor
from pulsus.langchain import mcp_to_langchain_tool
from pulsus.mcp.simple import ScriptOps

# Convert to LangChain tool
script_tool = mcp_to_langchain_tool(ScriptOps)

# Use in agent
agent = AgentExecutor(tools=[script_tool], ...)
result = agent.invoke("Read example.py and format it")
```

### 2. LangGraph StateGraph

Complex workflows with state management:

```python
from langgraph.graph import StateGraph
from pulsus.langchain import create_pulsus_graph

graph = create_pulsus_graph()
result = graph.invoke({
    "messages": [HumanMessage("Analyze this repository")],
    "parsed_intent": {},
    "selected_tools": [],
    "execution_results": [],
    "next_action": "start"
})
```

### 3. FastAPI Endpoints

HTTP API for remote execution:

```python
from fastapi import FastAPI
from pulsus.interface import create_api

app = create_api()

# POST /execute - Execute MCP action
# GET /domains - List available domains
# GET /health - Health check
# GET /metrics - SafeNet metrics
```

### 4. CLI Interface

Command-line execution:

```bash
# Execute MCP action
pulsus execute script_ops read_script --path example.py

# List domains
pulsus list-domains

# Configure preferences
pulsus config set auto_approve_read_only true
```

---

## Extension Points

### 1. Custom MCP Domains

Create new MCP operations:

```python
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only

class MyCustomDomain(MCPBase):
    """Custom MCP domain"""

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "domain": "my_domain",
            "description": "My custom operations",
            "actions": ["action1", "action2"]
        }

    @read_only
    def action1(self, param: str) -> MCPResponse:
        return MCPResponse.success(data=result)
```

### 2. Custom Workflows

Define workflows via JSON:

```json
{
  "name": "my_workflow",
  "steps": [
    {"name": "step1", "tool": "Tool1", "config": {}},
    {"name": "step2", "tool": "Tool2", "config": {}}
  ]
}
```

### 3. Custom Routing Strategies

Extend routing logic:

```python
class CustomRouter(RoutingPolicy):
    def select_policy(self, candidates: List[MCPDomain]) -> str:
        # Custom logic
        return "CUSTOM_STRATEGY"
```

### 4. Custom Safety Policies

Define safety rules:

```python
class CustomSafetyPolicy(SafetyPolicy):
    def enforce(self, operation: str, params: Dict) -> bool:
        # Custom safety checks
        return is_safe
```

---

## Deployment Architecture

### Development Environment

```
Local Machine
├── Pulsus CLI (console/)
├── MCP Domains (mcp/)
├── Workflows (workflows/)
├── Tests (tests/)
└── Configs (config/)
```

### Production Environment

```
┌─────────────────────────────────────────┐
│         Load Balancer                    │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼────┐     ┌───▼────┐
   │ API    │     │ API    │
   │ Server │     │ Server │
   │ (Fast  │     │ (Fast  │
   │  API)  │     │  API)  │
   └───┬────┘     └───┬────┘
       │               │
       └───────┬───────┘
               │
       ┌───────▼────────┐
       │  Pulsus Core   │
       │  (MCP Engine)  │
       └───────┬────────┘
               │
       ┌───────┴────────┐
       │  SafeNet       │
       │  Logger        │
       │  (Metrics DB)  │
       └────────────────┘
```

### Integration with Supervisors

```
┌─────────────────────────────────────────┐
│      LangGraph Supervisor               │
│  (Multi-agent orchestration)            │
└──────────────┬──────────────────────────┘
               │
       ┌───────▼───────┐
       │  Pulsus API   │
       │  (MCP Exec)   │
       └───────┬───────┘
               │
       ┌───────▼───────────┐
       │  External Tools   │
       │  - Aimsun         │
       │  - QGIS           │
       │  - Custom Software│
       └───────────────────┘
```

---

## Technology Stack

### Core Dependencies
- **Python**: 3.10+
- **Pydantic**: Data validation and type safety
- **LangChain**: Tool integration framework
- **LangGraph**: Workflow orchestration (planned)

### Development Tools
- **pytest**: Testing framework
- **mypy**: Static type checking
- **ruff**: Linting and formatting
- **bandit**: Security scanning

### Optional Dependencies
- **FastAPI**: HTTP API (Phase 8)
- **psutil**: Process monitoring (Phase 5)
- **Jinja2**: Template engine (Phase 4)
- **OpenAI/Anthropic**: LLM providers (Phase 3)

---

## Performance Considerations

### 1. Execution Performance
- **Target**: <250ms for simple operations
- **Target**: <5s for complex workflows
- **Optimization**: Caching, lazy loading, parallel execution

### 2. Memory Usage
- **Target**: <100MB base memory
- **Target**: <500MB under load
- **Optimization**: Streaming results, garbage collection

### 3. Scalability
- **Horizontal**: Multiple API servers behind load balancer
- **Vertical**: Thread/process pools for parallel execution
- **Caching**: Redis for result caching

---

## Future Enhancements

### Phase 2-10 Roadmap
1. **Phase 2**: Classic MCP Domains (Weeks 5-8)
2. **Phase 3**: Workflow MCP Domains (Weeks 9-12)
3. **Phase 4**: Customizable Framework (Weeks 13-14)
4. **Phase 5**: External Console Execution (Weeks 15-16)
5. **Phase 6**: Preferences & Context Memory (Week 17)
6. **Phase 7**: SafeNet Logging & Observability (Weeks 18-19)
7. **Phase 8**: Interface & API Adapters (Weeks 20-21)
8. **Phase 9**: LangGraph Integration (Weeks 22-24)
9. **Phase 10**: Testing, Validation & Performance (Weeks 25-26)

### Beyond V1.0
- Multi-agent orchestration
- Distributed execution
- Real-time collaboration
- ML-powered routing
- Visual workflow designer
- Plugin marketplace

---

## References

- **TODO.md**: High-level roadmap and progress tracking
- **PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md**: Complete implementation plan
- **ARCHITECTURE_AUDIT_REPORT.md**: Current state assessment
- **README.md**: Project overview and quick start

---

**Document Version**: 1.0
**Authors**: Jean-Claude Architect
**Last Updated**: November 2025
**Next Review**: End of Phase 2
