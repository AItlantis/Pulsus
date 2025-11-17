# Phase 3: Advanced MCP Domains & Agent Integration

**Version:** 1.0
**Date:** November 10, 2025
**Status:** Planning (Dependent on Phase 2 Completion)
**Duration:** 3-4 weeks
**Primary Agent:** Jean-Claude Mechanic
**Support Agents:** Jean-Claude Domain (platform integration), Jean-Claude Auditor (testing)

---

## Executive Summary

Phase 3 builds on the completed Phase 1 (Core Framework) and Phase 2 (Classic Domains) to create advanced, platform-specific MCP domains and integrate them into the Pulsus agent ecosystem. This phase involves:

1. **Platform-Specific Domains** (Aimsun, QGIS, specialized tools)
2. **Agent Integration** (Pulse, Shell, Compass)
3. **Advanced Features** (workflows, composition, error recovery)
4. **Production Deployment** (monitoring, logging, SafeNet)

**Key Goal:** Transform Pulsus from a code assistant into a comprehensive, production-ready MCP-powered development environment.

---

## Prerequisites

### Phase 1 Complete ✅
- MCPBase and MCPResponse implemented
- Safety decorators functional
- SafetyPolicy enforcement working
- MCPLogger with SafeNet integration

### Phase 2 Complete ⏳
- 5+ Classic MCP domains operational (ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor)
- All domains extend MCPBase
- LangChain integration complete
- Comprehensive test coverage
- Documentation complete

### Required Knowledge
- Platform APIs (Aimsun GetKernel, QGIS PyQGIS)
- Agent architecture (Pulse, Shell, Compass)
- Workflow orchestration patterns
- Production deployment practices

---

## Phase 3 Objectives

### Primary Objectives

1. **Advanced Domain Development**
   - Create 3-5 platform-specific MCP domains
   - Implement complex operations with rollback support
   - Add specialized validation and safety checks

2. **Agent Integration**
   - Integrate MCP domains into Pulse (main agent)
   - Enable Shell for MCP operations
   - Configure Compass for domain discovery

3. **Production Features**
   - Add comprehensive error recovery
   - Implement workflow composition
   - Build monitoring and alerting
   - Create SafeNet dashboard

4. **User Experience**
   - Natural language interface for all domains
   - Interactive confirmation flows
   - Real-time progress reporting
   - Comprehensive help system

---

## Phase 3 Deliverables

### New Directory Structure

```
agents/Pulsus/
├── mcp/
│   ├── core/                      ✅ Phase 1
│   ├── simple/                    ✅ Phase 2
│   │
│   ├── advanced/                  ⭐ Phase 3 NEW
│   │   ├── __init__.py           (exports all advanced domains)
│   │   ├── aimsun_ops.py         (Aimsun model operations)
│   │   ├── qgis_ops.py           (QGIS layer operations)
│   │   ├── git_ops.py            (Advanced Git operations)
│   │   ├── workflow_ops.py       (Workflow orchestration)
│   │   └── README.md
│   │
│   ├── composition/               ⭐ Phase 3 NEW
│   │   ├── __init__.py
│   │   ├── chain.py              (Operation chaining)
│   │   ├── parallel.py           (Parallel execution)
│   │   ├── conditional.py        (Conditional flows)
│   │   └── README.md
│   │
│   ├── monitoring/                ⭐ Phase 3 NEW
│   │   ├── __init__.py
│   │   ├── metrics.py            (Performance metrics)
│   │   ├── alerts.py             (Alert system)
│   │   ├── dashboard.py          (SafeNet dashboard)
│   │   └── README.md
│   │
│   └── tests/
│       ├── test_advanced_domains.py
│       ├── test_composition.py
│       └── test_integration_full.py
│
├── agents/                         ⭐ Phase 3 UPDATE
│   ├── pulse/
│   │   ├── mcp_integration.py    (MCP → Pulse bridge)
│   │   └── domain_router.py      (Route prompts to domains)
│   ├── shell/
│   │   └── mcp_commands.py       (Shell commands for MCP)
│   └── compass/
│       └── domain_discovery.py   (Domain introspection)
│
├── workflows/                      ⭐ Phase 3 UPDATE
│   ├── mcp/                      (MCP-based workflows)
│   │   ├── analyze_repo.json
│   │   ├── refactor_code.json
│   │   └── generate_docs.json
│   └── README.md
│
└── safenet/                        ⭐ Phase 3 NEW
    ├── dashboard.py              (Web dashboard)
    ├── templates/
    │   └── dashboard.html
    └── README.md
```

---

## Implementation Timeline

### Week 1: Advanced Domains (Platform-Specific)

#### Task 1.1: AimsunOps Domain
**Duration:** 3 days
**Priority:** 🔴 Critical (if Aimsun is primary platform)

**Operations**:
```python
class AimsunOps(MCPBase):
    @read_only
    def get_network_stats(self, model: GKModel) -> MCPResponse:
        """Get network statistics"""

    @read_only
    @cached(ttl=300)
    def list_sections(self, model: GKModel, criteria: dict) -> MCPResponse:
        """List sections matching criteria"""

    @restricted_write(platform='aimsun')
    def update_section(self, section: GKSection, **attributes) -> MCPResponse:
        """Update section attributes"""

    @transactional(rollback_handler=_rollback_batch_update)
    def batch_update_sections(self, sections: List, updates: dict) -> MCPResponse:
        """Update multiple sections (with rollback)"""

    @write_safe
    def create_detector(self, section: GKSection, position: float) -> MCPResponse:
        """Create detector on section"""

    @read_only
    def analyze_simulation(self, replication: GKReplication) -> MCPResponse:
        """Analyze simulation results"""
```

**Safety Features**:
- Type validation for GK* objects
- Rollback support for batch operations
- Confirmation for destructive operations
- Comprehensive error messages

**Test Requirements**:
- Mock Aimsun kernel for testing
- Test type validation
- Test rollback functionality
- Integration tests with real models (optional)

#### Task 1.2: GitOps Domain
**Duration:** 2 days
**Priority:** 🟠 High

**Operations**:
```python
class GitOps(MCPBase):
    @read_only
    def get_status(self, repo_path: str) -> MCPResponse:
        """Get git status"""

    @read_only
    def get_diff(self, repo_path: str, file: str = None) -> MCPResponse:
        """Get git diff"""

    @read_only
    def get_history(self, repo_path: str, limit: int = 10) -> MCPResponse:
        """Get commit history"""

    @write_safe
    def commit(self, repo_path: str, message: str, files: List[str] = None) -> MCPResponse:
        """Create git commit"""

    @write_safe
    def create_branch(self, repo_path: str, branch_name: str) -> MCPResponse:
        """Create new branch"""

    @write_safe
    def merge_branch(self, repo_path: str, branch: str, strategy: str = 'merge') -> MCPResponse:
        """Merge branch"""

    @transactional
    def rebase(self, repo_path: str, target: str) -> MCPResponse:
        """Rebase current branch (with rollback)"""
```

**Safety Features**:
- Prevent force operations without explicit confirmation
- Rollback support for rebase
- Validate repository state before operations
- Detect uncommitted changes

---

### Week 2: Workflow Composition & Error Recovery

#### Task 2.1: Operation Chaining
**Duration:** 2 days
**Priority:** 🔴 Critical

**Implementation**:
```python
# mcp/composition/chain.py
from mcp.core import MCPBase, MCPResponse

class OperationChain:
    """Chain multiple MCP operations together"""

    def __init__(self, name: str = None):
        self.name = name or "unnamed_chain"
        self.operations = []

    def add(self, domain: MCPBase, operation: str, **kwargs):
        """Add operation to chain"""
        self.operations.append({
            'domain': domain,
            'operation': operation,
            'kwargs': kwargs
        })
        return self

    def execute(self) -> MCPResponse:
        """Execute chain with error recovery"""
        results = []
        for idx, op in enumerate(self.operations):
            result = op['domain'].execute(op['operation'], **op['kwargs'])

            if not result.success:
                # Chain failed - rollback if possible
                self._rollback(results)
                return MCPResponse.error_response(
                    error=f"Chain failed at step {idx+1}: {result.error}",
                    context={'failed_operation': op, 'previous_results': results}
                )

            results.append(result)

        return MCPResponse.success_response(
            data={'results': results},
            context={'chain': self.name, 'steps': len(results)}
        )

    def _rollback(self, completed_operations):
        """Attempt to rollback completed operations"""
        for result in reversed(completed_operations):
            # Check if operation supports rollback
            # Execute rollback if available
            pass


# Usage Example:
chain = OperationChain("analyze_and_document")
chain.add(script_ops, 'read_script', path='main.py')
chain.add(script_ops, 'add_comments', path='main.py')
chain.add(script_ops, 'write_md', path='main.py')
result = chain.execute()
```

**Features**:
- Sequential operation execution
- Automatic error recovery
- Rollback support
- Progress tracking
- Partial result preservation

#### Task 2.2: Parallel Execution
**Duration:** 1 day
**Priority:** 🟡 Medium

**Implementation**:
```python
# mcp/composition/parallel.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelOperations:
    """Execute multiple operations in parallel"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.operations = []

    def add(self, domain: MCPBase, operation: str, **kwargs):
        """Add operation to parallel batch"""
        self.operations.append((domain, operation, kwargs))
        return self

    def execute(self) -> MCPResponse:
        """Execute all operations in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(domain.execute, operation, **kwargs)
                for domain, operation, kwargs in self.operations
            ]

            results = [future.result() for future in futures]

            # Check if any failed
            failed = [r for r in results if not r.success]

            if failed:
                return MCPResponse.error_response(
                    error=f"{len(failed)} operations failed",
                    context={'failed': failed, 'succeeded': len(results) - len(failed)}
                )

            return MCPResponse.success_response(
                data={'results': results},
                context={'operations': len(results)}
            )


# Usage Example:
parallel = ParallelOperations(max_workers=4)
parallel.add(script_ops, 'read_script', path='file1.py')
parallel.add(script_ops, 'read_script', path='file2.py')
parallel.add(script_ops, 'read_script', path='file3.py')
result = parallel.execute()
```

#### Task 2.3: Conditional Flows
**Duration:** 1 day
**Priority:** 🟡 Medium

**Implementation**:
```python
# mcp/composition/conditional.py
class ConditionalFlow:
    """Conditional operation execution"""

    def if_then_else(
        self,
        condition_fn: callable,
        then_domain: MCPBase,
        then_operation: str,
        else_domain: MCPBase = None,
        else_operation: str = None,
        **kwargs
    ) -> MCPResponse:
        """Execute operation based on condition"""

        if condition_fn(**kwargs):
            return then_domain.execute(then_operation, **kwargs)
        elif else_domain and else_operation:
            return else_domain.execute(else_operation, **kwargs)
        else:
            return MCPResponse.success_response(
                data={'skipped': True},
                context={'condition': False}
            )


# Usage Example:
def check_file_size(path):
    return Path(path).stat().st_size > 1000

flow = ConditionalFlow()
result = flow.if_then_else(
    condition_fn=check_file_size,
    then_domain=script_ops,
    then_operation='format_script',
    else_domain=script_ops,
    else_operation='read_script',
    path='main.py'
)
```

---

### Week 3: Agent Integration

#### Task 3.1: Pulse Integration
**Duration:** 2 days
**Priority:** 🔴 Critical

**Implementation**:
```python
# agents/pulse/mcp_integration.py
from mcp.core import MCPBase
from mcp.simple import ScriptOps, RepositoryOps, FileManager
from mcp.advanced import AimsunOps, GitOps
from routing.mcp_router import MCPRouter

class PulseMCPIntegration:
    """Integrate MCP domains into Pulse agent"""

    def __init__(self, pulse_instance):
        self.pulse = pulse_instance
        self.router = MCPRouter()

        # Register all domains
        self.register_domains()

        # Set up natural language routing
        self.setup_routing()

    def register_domains(self):
        """Register all available MCP domains"""
        # Simple domains
        self.router.register_domain(ScriptOps)
        self.router.register_domain(RepositoryOps)
        self.router.register_domain(FileManager)

        # Advanced domains (if available)
        try:
            self.router.register_domain(AimsunOps)
            self.router.register_domain(GitOps)
        except ImportError:
            pass

    def setup_routing(self):
        """Set up natural language routing rules"""
        # This connects Pulse's prompt parser to MCP router
        pass

    def handle_prompt(self, prompt: str) -> MCPResponse:
        """Route user prompt to appropriate MCP domain"""
        return self.router.route(prompt)


# In Pulse main loop:
mcp = PulseMCPIntegration(pulse_instance)

# Natural language commands now route to MCP:
result = mcp.handle_prompt("read the script at src/main.py")
# Routes to: ScriptOps.read_script(path='src/main.py')
```

**Features**:
- Auto-discovery of available domains
- Natural language routing
- Context preservation across operations
- Error handling and recovery

#### Task 3.2: Shell Commands
**Duration:** 1 day
**Priority:** 🟠 High

**Implementation**:
```python
# agents/shell/mcp_commands.py

# Add new shell commands:
# - mcp list                     # List all domains
# - mcp caps <domain>           # Show domain capabilities
# - mcp exec <domain> <op>      # Execute operation
# - mcp help <domain>           # Show domain help
# - mcp history                 # Show operation history

class MCPShellCommands:
    """Shell commands for MCP operations"""

    def cmd_mcp_list(self):
        """List all registered MCP domains"""
        # Implementation

    def cmd_mcp_caps(self, domain_name: str):
        """Show capabilities of a domain"""
        # Implementation

    def cmd_mcp_exec(self, domain: str, operation: str, **kwargs):
        """Execute MCP operation"""
        # Implementation
```

#### Task 3.3: Compass Discovery
**Duration:** 1 day
**Priority:** 🟡 Medium

**Implementation**:
```python
# agents/compass/domain_discovery.py

class CompassMCPDiscovery:
    """Compass agent discovers MCP domains dynamically"""

    def discover_domains(self) -> List[Dict]:
        """Discover all available MCP domains"""
        # Scan mcp/simple/ and mcp/advanced/
        # Return domain metadata

    def get_domain_capabilities(self, domain_name: str) -> List[Dict]:
        """Get capabilities of a domain"""
        # Use get_capabilities()

    def suggest_operations(self, user_intent: str) -> List[Dict]:
        """Suggest operations based on user intent"""
        # Use LLM to match intent to operations
```

---

### Week 4: Monitoring, SafeNet Dashboard & Production

#### Task 4.1: Performance Monitoring
**Duration:** 2 days
**Priority:** 🟠 High

**Implementation**:
```python
# mcp/monitoring/metrics.py

class MCPMetrics:
    """Collect and analyze MCP performance metrics"""

    def track_operation(
        self,
        domain: str,
        operation: str,
        duration_ms: float,
        success: bool,
        error: str = None
    ):
        """Track operation execution"""

    def get_statistics(
        self,
        domain: str = None,
        operation: str = None,
        timeframe: str = 'last_hour'
    ) -> Dict:
        """Get performance statistics"""

    def get_slow_operations(self, threshold_ms: float = 1000) -> List:
        """Get operations slower than threshold"""

    def get_error_rate(self, domain: str = None) -> float:
        """Get error rate for domain/all domains"""
```

**Metrics Collected**:
- Operation execution time (p50, p95, p99)
- Success/failure rates
- Error types and frequencies
- Cache hit rates
- Memory usage
- Concurrent operations

#### Task 4.2: SafeNet Dashboard
**Duration:** 2 days
**Priority:** 🟠 High

**Implementation**:
```python
# safenet/dashboard.py
from flask import Flask, render_template
from mcp.core.logger import get_mcp_logger
from mcp.monitoring.metrics import MCPMetrics

app = Flask(__name__)
logger = get_mcp_logger()
metrics = MCPMetrics()

@app.route('/')
def dashboard():
    """Main SafeNet dashboard"""
    return render_template('dashboard.html',
        recent_operations=logger.get_history(limit=50),
        statistics=metrics.get_statistics(),
        error_rate=metrics.get_error_rate()
    )

@app.route('/domain/<domain_name>')
def domain_detail(domain_name):
    """Domain-specific view"""
    # Implementation

@app.route('/api/metrics')
def api_metrics():
    """API for metrics (for external tools)"""
    # Implementation

# Run with: python -m safenet.dashboard
```

**Dashboard Features**:
- Real-time operation log
- Performance charts
- Error rate graphs
- Domain usage statistics
- Safety level distribution
- Operation success trends

#### Task 4.3: Alerting System
**Duration:** 1 day
**Priority:** 🟡 Medium

**Implementation**:
```python
# mcp/monitoring/alerts.py

class AlertManager:
    """Alert system for MCP operations"""

    def register_alert(
        self,
        name: str,
        condition: callable,
        severity: str,  # 'info', 'warning', 'error', 'critical'
        action: callable
    ):
        """Register alert condition and action"""

    def check_alerts(self):
        """Check all registered alerts"""

    def send_alert(self, alert, context):
        """Send alert notification"""


# Example alerts:
alerts = AlertManager()

# High error rate
alerts.register_alert(
    name='high_error_rate',
    condition=lambda: metrics.get_error_rate() > 0.1,
    severity='error',
    action=lambda: print("ERROR: High error rate detected!")
)

# Slow operations
alerts.register_alert(
    name='slow_operations',
    condition=lambda: len(metrics.get_slow_operations(threshold_ms=5000)) > 0,
    severity='warning',
    action=lambda: print("WARNING: Slow operations detected")
)
```

---

## Success Criteria

### Functional Requirements ✅

- [ ] **3+ Advanced Domains Operational**
  - AimsunOps (if Aimsun used)
  - GitOps
  - WorkflowOps

- [ ] **Composition System Working**
  - Operation chaining
  - Parallel execution
  - Conditional flows
  - Error recovery

- [ ] **Agent Integration Complete**
  - Pulse integration
  - Shell commands
  - Compass discovery

- [ ] **Monitoring & SafeNet**
  - Performance metrics
  - SafeNet dashboard
  - Alerting system

### Quality Requirements ✅

- [ ] **Test Coverage ≥ 90%**
  - Advanced domain tests
  - Composition tests
  - Integration tests
  - End-to-end tests

- [ ] **Documentation Complete**
  - Advanced domain docs
  - Composition guide
  - Agent integration guide
  - SafeNet dashboard guide

- [ ] **Production Ready**
  - Error handling robust
  - Logging comprehensive
  - Monitoring in place
  - Performance acceptable

### Performance Requirements ✅

- [ ] **Execution Times**
  - Simple operations: <100ms
  - Complex operations: <1000ms
  - Chain operations: <5000ms

- [ ] **Reliability**
  - Uptime: >99%
  - Error rate: <1%
  - Recovery rate: >95%

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Platform API changes | High | Medium | Version pinning, abstraction layers |
| Complex rollback logic | High | Medium | Thorough testing, state snapshots |
| Agent integration conflicts | Medium | Low | Careful isolation, testing |
| Performance degradation | Medium | Low | Profiling, optimization |
| Dashboard security | High | Medium | Authentication, input validation |

---

## Dependencies

### External Libraries

```toml
# Add to pyproject.toml
[project]
dependencies = [
    # Phase 1 & 2 dependencies
    "langchain-core>=0.1.0",
    "pydantic>=2.0",
    "pandas>=2.0",

    # Phase 3 additions
    "flask>=3.0",              # for SafeNet dashboard
    "plotly>=5.0",             # for metrics visualization
    "gitpython>=3.1",          # for git operations
    "psutil>=5.9",             # for resource monitoring
]
```

### Internal Dependencies

- Phase 1: Core MCP Framework ✅
- Phase 2: Classic Domains ⏳
- Pulsus routing system (existing)
- Agent infrastructure (Pulse, Shell, Compass)

---

## Migration Path from Phase 2

### What Changes
1. **New domains** in `mcp/advanced/`
2. **Composition system** in `mcp/composition/`
3. **Monitoring** in `mcp/monitoring/`
4. **Agent updates** in respective agent directories

### What Stays the Same
- MCPBase framework (no changes)
- Phase 2 domains (fully compatible)
- Safety decorators (no changes)
- MCPResponse format (no changes)

### Backward Compatibility
- All Phase 2 domains continue to work
- No breaking API changes
- New features are additive only

---

## Timeline Summary

| Week | Focus | Deliverables |
|------|-------|-------------|
| 1 | Advanced Domains | AimsunOps, GitOps, tests |
| 2 | Composition | Chaining, parallel, conditional flows |
| 3 | Agent Integration | Pulse, Shell, Compass integration |
| 4 | Monitoring | Metrics, dashboard, alerts |

**Total Duration**: 4 weeks
**Expected Completion**: ~4 weeks after Phase 2 completion

---

## Next Steps After Phase 3

### Phase 4 (Future): Production & Scaling
- Multi-user support
- Authentication & authorization
- Distributed execution
- Cloud deployment
- API Gateway
- Advanced monitoring

### Phase 5 (Future): AI Enhancement
- LLM-powered operation selection
- Automated workflow generation
- Intelligent error recovery
- Predictive alerts
- Auto-optimization

---

## Appendix: Example End-to-End Workflow

```python
# Example: Complete code refactoring workflow using Phase 3 features

from mcp.simple import ScriptOps, GitOps
from mcp.composition import OperationChain
from agents.pulse import PulseMCPIntegration

# Initialize
pulse = PulseMCPIntegration(pulse_instance)
script_ops = ScriptOps(context={'caller': 'Pulse'})
git_ops = GitOps(context={'caller': 'Pulse'})

# Create workflow chain
workflow = OperationChain("refactor_codebase")

# 1. Get current git status
workflow.add(git_ops, 'get_status', repo_path='.')

# 2. Create feature branch
workflow.add(git_ops, 'create_branch', repo_path='.', branch_name='refactor/formatting')

# 3. Format all Python files
workflow.add(script_ops, 'scan_structure', base_dir='src')
workflow.add(script_ops, 'format_script', path='src/main.py')
workflow.add(script_ops, 'format_script', path='src/utils.py')

# 4. Add comments to functions
workflow.add(script_ops, 'add_comments', path='src/main.py')
workflow.add(script_ops, 'add_comments', path='src/utils.py')

# 5. Generate documentation
workflow.add(script_ops, 'write_md', path='src/main.py')
workflow.add(script_ops, 'write_md', path='src/utils.py')

# 6. Commit changes
workflow.add(git_ops, 'commit',
    repo_path='.',
    message='Refactor: Format code and add documentation',
    files=['src/main.py', 'src/utils.py']
)

# Execute workflow with automatic rollback on failure
result = workflow.execute()

if result.success:
    print("✓ Refactoring complete!")
    print(f"✓ Completed {len(result.data['results'])} operations")
else:
    print(f"✗ Workflow failed: {result.error}")
    print("✓ Changes rolled back automatically")
```

---

**Generated**: 2025-11-10
**Author**: Jean-Claude Architect (via Claude Code)
**Status**: Planning - Ready for Phase 2 Completion
