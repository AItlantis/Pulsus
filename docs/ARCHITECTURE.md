# Pulsus MCP Architecture Documentation

**Version**: 4.0 (Phase 3 Complete)
**Date**: November 17, 2025
**Status**: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Deployment Architecture](#deployment-architecture)
6. [Integration Patterns](#integration-patterns)
7. [Security Architecture](#security-architecture)

---

## System Overview

Pulsus is a comprehensive Model Context Protocol (MCP) orchestration platform built on a multi-tier architecture that combines:

- **Core MCP Framework** (Phase 1)
- **Simple MCP Domains** (Phase 2)
- **Advanced MCP Domains** (Phase 3)
- **Workflow Composition** (Phase 3)
- **Monitoring & Observability** (Phase 3)
- **LangChain/LangGraph Integration** (Phase 3)

### Key Characteristics

- **Modular**: Clear separation of concerns across domains
- **Safe**: Multi-level safety decorators and execution modes
- **Observable**: Comprehensive logging and metrics
- **Extensible**: Plugin architecture for custom domains
- **LangChain Native**: Built on LangChain Tools and LangGraph StateGraph

---

## Architecture Diagrams

### 1. System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface]
        API[REST API]
        Dashboard[SafeNet Dashboard]
    end

    subgraph "Routing Layer"
        Router[MCP Router]
        IntentParser[Intent Parser]
        ToolDiscovery[Tool Discovery]
    end

    subgraph "Execution Layer"
        Safety[Safety Policy Engine]
        Executor[Operation Executor]
        Sandbox[Sandbox Runner]
    end

    subgraph "MCP Domain Layer"
        Simple[Simple Domains<br/>ScriptOps, FileManager, etc.]
        Advanced[Advanced Domains<br/>GitOps, WorkflowOps]
        Custom[Custom Domains<br/>User-defined]
    end

    subgraph "Composition Layer"
        Chain[OperationChain]
        Parallel[ParallelOperations]
        Conditional[ConditionalFlow]
    end

    subgraph "Monitoring Layer"
        Metrics[MCPMetrics]
        Alerts[AlertManager]
        Logger[SafeNet Logger]
    end

    subgraph "Integration Layer"
        LangChainAdapter[LangChain Tool Adapter]
        LangGraphExecutor[LangGraph Executor]
        ToolRegistry[MCP Tool Registry]
    end

    CLI --> Router
    API --> Router
    Dashboard --> Metrics
    Dashboard --> Alerts

    Router --> IntentParser
    IntentParser --> ToolDiscovery
    ToolDiscovery --> Safety

    Safety --> Executor
    Executor --> Sandbox
    Sandbox --> Simple
    Sandbox --> Advanced
    Sandbox --> Custom

    Simple --> Composition
    Advanced --> Composition
    Custom --> Composition

    Composition --> Chain
    Composition --> Parallel
    Composition --> Conditional

    Executor --> Logger
    Executor --> Metrics
    Metrics --> Alerts

    Simple --> LangChainAdapter
    Advanced --> LangChainAdapter
    LangChainAdapter --> ToolRegistry
    ToolRegistry --> LangGraphExecutor

    style Simple fill:#a8d5ba
    style Advanced fill:#f7b7a3
    style Custom fill:#ffd89b
    style Metrics fill:#b4a7d6
    style LangChainAdapter fill:#86c5da
```

### 2. MCP Domain Hierarchy

```mermaid
graph TD
    MCPBase[MCPBase<br/>Core Class]

    subgraph "Simple Domains (Phase 2)"
        ScriptOps[ScriptOps<br/>Python script operations]
        RepositoryOps[RepositoryOps<br/>Repository management]
        FileManager[FileManager<br/>File operations]
        DataReader[DataReader<br/>Data loading]
        TextProcessor[TextProcessor<br/>Text operations]
    end

    subgraph "Advanced Domains (Phase 3)"
        GitOps[GitOps<br/>Git operations]
        WorkflowOps[WorkflowOps<br/>Workflow orchestration]
    end

    subgraph "Platform Domains (Future)"
        AimsunOps[AimsunOps<br/>Traffic simulation]
        QGISOps[QGISOps<br/>GIS operations]
    end

    MCPBase --> ScriptOps
    MCPBase --> RepositoryOps
    MCPBase --> FileManager
    MCPBase --> DataReader
    MCPBase --> TextProcessor
    MCPBase --> GitOps
    MCPBase --> WorkflowOps
    MCPBase --> AimsunOps
    MCPBase --> QGISOps

    style MCPBase fill:#4a90e2
    style ScriptOps fill:#a8d5ba
    style RepositoryOps fill:#a8d5ba
    style GitOps fill:#f7b7a3
    style WorkflowOps fill:#f7b7a3
    style AimsunOps fill:#d3d3d3
    style QGISOps fill:#d3d3d3
```

### 3. Workflow Composition Architecture

```mermaid
graph LR
    subgraph "Composition Tools"
        Chain[OperationChain<br/>Sequential + Rollback]
        Parallel[ParallelOperations<br/>Concurrent Execution]
        Conditional[ConditionalFlow<br/>If/Then/Else]
    end

    subgraph "MCP Operations"
        Op1[Operation 1]
        Op2[Operation 2]
        Op3[Operation 3]
        Op4[Operation 4]
    end

    subgraph "Execution Strategies"
        Sequential[Sequential<br/>with Rollback]
        Concurrent[Parallel<br/>with ThreadPool]
        Branching[Conditional<br/>Branching]
    end

    Chain --> Sequential
    Parallel --> Concurrent
    Conditional --> Branching

    Sequential --> Op1
    Op1 --> Op2
    Op2 --> Op3

    Concurrent --> Op1
    Concurrent --> Op2
    Concurrent --> Op3

    Branching --> Op1
    Branching --> Op4

    style Chain fill:#86c5da
    style Parallel fill:#ffd89b
    style Conditional fill:#b4a7d6
```

### 4. Monitoring & Observability Architecture

```mermaid
graph TB
    subgraph "Data Collection"
        Operations[MCP Operations]
        Decorators[Safety Decorators]
        Execution[Execution Engine]
    end

    subgraph "Metrics Collection"
        Tracker[Metrics Tracker]
        Store[Metrics Store<br/>In-Memory + History]
    end

    subgraph "Analysis"
        Stats[Statistics Engine<br/>p50/p95/p99]
        Aggregator[Domain Aggregator]
        ErrorAnalyzer[Error Analyzer]
    end

    subgraph "Alerting"
        Conditions[Alert Conditions]
        Manager[Alert Manager]
        Actions[Alert Actions]
    end

    subgraph "Visualization"
        Dashboard[SafeNet Dashboard]
        API[REST API]
        Reports[Performance Reports]
    end

    Operations --> Decorators
    Decorators --> Execution
    Execution --> Tracker
    Tracker --> Store

    Store --> Stats
    Store --> Aggregator
    Store --> ErrorAnalyzer

    Stats --> Conditions
    Conditions --> Manager
    Manager --> Actions

    Store --> Dashboard
    Stats --> Dashboard
    Manager --> Dashboard
    Dashboard --> API
    Dashboard --> Reports

    style Tracker fill:#b4a7d6
    style Stats fill:#86c5da
    style Manager fill:#f7b7a3
    style Dashboard fill:#ffd89b
```

### 5. LangChain Integration Architecture

```mermaid
graph TB
    subgraph "MCP Layer"
        MCPDomain1[ScriptOps]
        MCPDomain2[GitOps]
        MCPDomain3[WorkflowOps]
    end

    subgraph "Adapter Layer"
        Adapter[MCP Tool Adapter]
        SchemaGen[Pydantic Schema Generator]
        Registry[MCP Tool Registry]
    end

    subgraph "LangChain Layer"
        StructuredTools[LangChain StructuredTools]
        Agent[LangChain Agent]
        Chain[LangChain Chain]
    end

    subgraph "LangGraph Layer"
        StateGraph[LangGraph StateGraph]
        Nodes[Graph Nodes]
        Edges[Conditional Edges]
    end

    subgraph "Orchestration"
        Supervisor[Supervisor Agent]
        Workers[Worker Agents]
    end

    MCPDomain1 --> Adapter
    MCPDomain2 --> Adapter
    MCPDomain3 --> Adapter

    Adapter --> SchemaGen
    SchemaGen --> StructuredTools
    StructuredTools --> Registry

    Registry --> Agent
    Registry --> Chain
    Registry --> StateGraph

    StateGraph --> Nodes
    Nodes --> Edges

    Agent --> Supervisor
    StateGraph --> Supervisor
    Supervisor --> Workers

    style Adapter fill:#86c5da
    style StructuredTools fill:#a8d5ba
    style StateGraph fill:#f7b7a3
    style Supervisor fill:#ffd89b
```

### 6. Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Router
    participant Safety
    participant Domain
    participant Metrics
    participant Logger

    User->>Router: Request Operation
    Router->>Router: Parse Intent
    Router->>Router: Discover Tools
    Router->>Safety: Validate Operation

    alt Read-Only Operation
        Safety->>Domain: Execute Directly
    else Write Operation
        Safety->>User: Request Confirmation
        User->>Safety: Confirm
        Safety->>Domain: Execute with Sandbox
    end

    Domain->>Domain: Perform Operation
    Domain->>Metrics: Track Performance
    Domain->>Logger: Log Action

    Domain->>Safety: Return MCPResponse
    Safety->>Router: Return Result
    Router->>User: Display Result

    Metrics->>Metrics: Update Statistics
    Logger->>Logger: Write to SafeNet Log
```

### 7. Safety Decorator Flow

```mermaid
graph TD
    Start[Operation Call]
    Decorator{Safety Decorator}
    ReadOnly[Read-Only]
    WriteSafe[Write-Safe]
    Restricted[Restricted-Write]

    ValidatePolicy[Validate Safety Policy]
    CheckMode{Execution Mode}

    Plan[PLAN Mode]
    Execute[EXECUTE Mode]

    RequestConfirm[Request User Confirmation]
    UserConfirm{User Confirms?}

    ExecuteOp[Execute Operation]
    ExecuteSandbox[Execute in Sandbox]

    LogSuccess[Log Success]
    LogFailure[Log Failure]

    ReturnResponse[Return MCPResponse]

    Start --> Decorator
    Decorator --> ReadOnly
    Decorator --> WriteSafe
    Decorator --> Restricted

    ReadOnly --> ValidatePolicy
    WriteSafe --> ValidatePolicy
    Restricted --> ValidatePolicy

    ValidatePolicy --> CheckMode

    CheckMode -->|PLAN| Plan
    CheckMode -->|EXECUTE| Execute

    Plan --> ReturnResponse
    Execute --> RequestConfirm

    RequestConfirm --> UserConfirm
    UserConfirm -->|Yes| ExecuteSandbox
    UserConfirm -->|No| LogFailure

    ExecuteSandbox --> ExecuteOp
    ExecuteOp -->|Success| LogSuccess
    ExecuteOp -->|Failure| LogFailure

    LogSuccess --> ReturnResponse
    LogFailure --> ReturnResponse

    style ReadOnly fill:#a8d5ba
    style WriteSafe fill:#ffd89b
    style Restricted fill:#f7b7a3
    style ExecuteSandbox fill:#b4a7d6
```

### 8. Workflow Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant WorkflowOps
    participant Validator
    participant Executor
    participant Domain1
    participant Domain2
    participant Metrics

    User->>WorkflowOps: Load Workflow JSON
    WorkflowOps->>Validator: Validate Workflow
    Validator->>Validator: Check Required Fields
    Validator->>Validator: Validate Steps
    Validator-->>WorkflowOps: Validation Result

    alt Workflow Valid
        WorkflowOps->>Executor: Execute Workflow

        loop For Each Step
            Executor->>Domain1: Execute Step 1
            Domain1->>Metrics: Track Metrics
            Domain1-->>Executor: Step 1 Result

            alt Step Success
                Executor->>Domain2: Execute Step 2
                Domain2->>Metrics: Track Metrics
                Domain2-->>Executor: Step 2 Result
            else Step Failure
                Executor->>Executor: Handle Error
                alt On Error: Abort
                    Executor->>Executor: Stop Execution
                else On Error: Continue
                    Executor->>Domain2: Execute Step 2
                end
            end
        end

        Executor-->>WorkflowOps: Workflow Result
        WorkflowOps-->>User: Success Response
    else Workflow Invalid
        Validator-->>User: Validation Errors
    end
```

### 9. Component Interaction Map

```mermaid
graph TB
    subgraph "Core Framework (Phase 1)"
        MCPBase[MCPBase]
        MCPResponse[MCPResponse]
        Decorators[Safety Decorators]
        Policy[Safety Policy]
        Logger[MCP Logger]
    end

    subgraph "Domain Layer (Phase 2 & 3)"
        SimpleDomains[Simple Domains]
        AdvancedDomains[Advanced Domains]
    end

    subgraph "Composition (Phase 3)"
        Composition[Composition Tools]
    end

    subgraph "Monitoring (Phase 3)"
        Monitoring[Metrics & Alerts]
    end

    subgraph "Integration (Phase 3)"
        LangChain[LangChain Integration]
    end

    MCPBase --> SimpleDomains
    MCPBase --> AdvancedDomains
    Decorators --> SimpleDomains
    Decorators --> AdvancedDomains
    Policy --> Decorators
    Logger --> SimpleDomains
    Logger --> AdvancedDomains

    SimpleDomains --> Composition
    AdvancedDomains --> Composition

    SimpleDomains --> Monitoring
    AdvancedDomains --> Monitoring
    Composition --> Monitoring

    SimpleDomains --> LangChain
    AdvancedDomains --> LangChain

    style MCPBase fill:#4a90e2
    style SimpleDomains fill:#a8d5ba
    style AdvancedDomains fill:#f7b7a3
    style Composition fill:#86c5da
    style Monitoring fill:#b4a7d6
    style LangChain fill:#ffd89b
```

---

## Component Details

### Core Components

#### MCPBase
- **Location**: `mcp/core/base.py`
- **Purpose**: Base class for all MCP domains
- **Key Features**:
  - Standardized MCPResponse format
  - Capability introspection
  - Operation logging
  - Context management

#### Safety Decorators
- **Location**: `mcp/core/decorators.py`
- **Types**:
  - `@read_only` - Safe read operations
  - `@write_safe` - Write operations with confirmation
  - `@restricted_write` - Platform-restricted writes
  - `@transactional` - Operations with rollback
  - `@cached` - Cached operations

#### Safety Policy
- **Location**: `mcp/core/policy.py`
- **Modes**:
  - `PLAN` - Planning mode (no execution)
  - `EXECUTE` - Full execution
  - `UNSAFE` - Unrestricted (developer mode)

### Simple Domains (Phase 2)

| Domain | Purpose | Operations | Safety Level |
|--------|---------|------------|--------------|
| ScriptOps | Python script operations | 5 | Read-only, Write-safe |
| RepositoryOps | Repository management | 4+ | Read-only, Write-safe |
| FileManager | File operations | 6 | Read-only, Write-safe |
| DataReader | Data loading | 4 | Read-only, Cached |
| TextProcessor | Text operations | 4+ | Read-only, Write-safe |

### Advanced Domains (Phase 3)

| Domain | Purpose | Operations | Safety Level |
|--------|---------|------------|--------------|
| GitOps | Git operations | 8 | Read-only, Write-safe |
| WorkflowOps | Workflow orchestration | 5 | Read-only, Write-safe |

### Composition Tools (Phase 3)

| Tool | Purpose | Key Features |
|------|---------|--------------|
| OperationChain | Sequential execution | Rollback support, error recovery |
| ParallelOperations | Concurrent execution | Thread pooling, result aggregation |
| ConditionalFlow | Conditional execution | If/then/else, switch-case |

### Monitoring Components (Phase 3)

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| MCPMetrics | Performance tracking | p50/p95/p99, error rates |
| AlertManager | Alert system | Severity levels, cooldown |
| SafeNet Dashboard | Web UI | REST API, real-time monitoring |

---

## Data Flow

### Operation Execution Flow

1. **Request Initiation**
   - User sends request via CLI/API
   - Request contains operation name and parameters

2. **Intent Parsing**
   - Router parses user intent
   - Identifies domain and operation
   - Extracts parameters

3. **Tool Discovery**
   - Search available domains
   - Score candidates
   - Select best match

4. **Safety Validation**
   - Check safety decorator
   - Validate execution mode
   - Request confirmation (if needed)

5. **Operation Execution**
   - Execute in sandbox (if restricted)
   - Perform operation
   - Track metrics

6. **Response Generation**
   - Create MCPResponse
   - Add trace information
   - Log to SafeNet

7. **Result Delivery**
   - Return to router
   - Format for user
   - Display result

### Metrics Collection Flow

1. **Operation Start**
   - Record timestamp
   - Capture context

2. **Execution**
   - Monitor duration
   - Track status

3. **Operation Complete**
   - Calculate duration
   - Create OperationMetric
   - Add to metrics store

4. **Aggregation**
   - Update domain statistics
   - Calculate percentiles
   - Update error rates

5. **Alerting**
   - Check alert conditions
   - Trigger alerts if needed
   - Execute alert actions

6. **Visualization**
   - Update dashboard
   - Provide API data
   - Generate reports

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────┐
│         Developer Machine           │
│  ┌──────────────────────────────┐   │
│  │       Pulsus CLI             │   │
│  │   (Direct Execution)         │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │    Local Git Repository      │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   SafeNet Dashboard          │   │
│  │   (localhost:5000)           │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Production Environment (Future)

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────▼────────┐         ┌────────▼────────┐
    │   API Server 1  │         │   API Server 2  │
    │   (FastAPI)     │         │   (FastAPI)     │
    └────────┬────────┘         └────────┬────────┘
             │                            │
    ┌────────▼────────────────────────────▼────────┐
    │          Message Queue (Redis)               │
    └────────┬─────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  Worker Pool    │
    │  (Celery)       │
    └────────┬────────┘
             │
    ┌────────▼─────────────────────────────────────┐
    │     Monitoring & Metrics (Prometheus)        │
    └──────────────────────────────────────────────┘
```

### Container Architecture (Future)

```
┌────────────────────────────────────────────────────────┐
│                  Docker Compose                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  API Service │  │ Worker Service│  │  Dashboard  │  │
│  │  (FastAPI)   │  │  (Celery)    │  │   (Flask)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                  │                  │         │
│  ┌──────▼──────────────────▼──────────────────▼──────┐ │
│  │            Shared Volume (Logs & Metrics)         │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │              Redis (Message Queue)                │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Pattern 1: Simple Domain Usage

```python
from mcp.simple import ScriptOps

script_ops = ScriptOps()
result = script_ops.read_script(path='main.py')

if result.success:
    print(f"Script structure: {result.data['structure']}")
```

### Pattern 2: Workflow Composition

```python
from mcp.composition import OperationChain
from mcp.simple import ScriptOps
from mcp.advanced import GitOps

chain = OperationChain("git_workflow")
chain.add(git_ops, 'get_status', repo_path='.')
chain.add(script_ops, 'format_script', path='main.py')
chain.add(git_ops, 'commit', repo_path='.', message='Format code')

result = chain.execute()
```

### Pattern 3: LangChain Integration

```python
from langchain.tool_adapter import mcp_to_langchain_tool
from mcp.simple import ScriptOps
from langchain.agents import AgentExecutor

tool = mcp_to_langchain_tool(ScriptOps)
agent = AgentExecutor(tools=[tool], ...)
```

### Pattern 4: Monitoring Setup

```python
from mcp.monitoring.metrics import get_metrics
from mcp.monitoring.alerts import get_alert_manager, AlertSeverity

metrics = get_metrics()
alerts = get_alert_manager()

alerts.register_alert(
    name='high_error_rate',
    condition=lambda: metrics.get_error_rate() > 0.1,
    severity=AlertSeverity.ERROR,
    message=lambda: "Error rate exceeded threshold"
)
```

---

## Security Architecture

### Defense in Depth

1. **Input Validation Layer**
   - Parameter type checking
   - Path sanitization
   - Command injection prevention

2. **Safety Policy Layer**
   - Operation-level permissions
   - Execution mode enforcement
   - User confirmation for writes

3. **Sandbox Execution Layer**
   - Restricted file system access
   - Resource limitations
   - Timeout enforcement

4. **Audit & Logging Layer**
   - All operations logged
   - File hash tracking
   - Change attribution

### Safety Levels

| Level | Description | Confirmation | Sandbox | Use Case |
|-------|-------------|--------------|---------|----------|
| READ_ONLY | No side effects | No | No | Data retrieval |
| WRITE_SAFE | Modifies files | Yes | Recommended | Code changes |
| RESTRICTED_WRITE | Platform-specific | Yes | Yes | Model updates |
| TRANSACTIONAL | With rollback | Yes | Yes | Bulk operations |

---

## Performance Characteristics

### Latency Targets

| Operation Type | Target (p95) | Target (p99) |
|----------------|--------------|--------------|
| Read operations | < 50ms | < 100ms |
| Write operations | < 100ms | < 200ms |
| Chain operations | < 500ms | < 1000ms |
| Workflow execution | < 2000ms | < 5000ms |

### Throughput

- **Single operations**: 100+ ops/sec
- **Parallel operations**: 400+ ops/sec (4 workers)
- **Dashboard API**: 1000+ req/sec

### Resource Usage

- **Memory**: < 100MB typical
- **CPU**: < 10% at rest, < 50% under load
- **Disk**: Log rotation at 100MB

---

## Future Enhancements

### Phase 4: Production & Scaling
- Multi-user support with authentication
- Distributed execution across nodes
- Cloud deployment (AWS/Azure/GCP)
- API Gateway with rate limiting
- Advanced monitoring (Prometheus/Grafana)

### Phase 5: AI Enhancement
- LLM-powered operation selection
- Automated workflow generation
- Intelligent error recovery
- Predictive alerting
- Auto-optimization based on metrics

---

**Document Version**: 1.0
**Last Updated**: November 17, 2025
**Status**: Complete ✅
**Next Review**: End of Phase 4
