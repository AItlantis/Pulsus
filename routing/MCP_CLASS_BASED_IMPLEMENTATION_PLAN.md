# MCP Class-Based Architecture - Implementation Plan

## Overview

This document outlines the implementation plan for transitioning to a class-based MCP architecture, integrating with existing Pulsus features and workflows.

## Current Architecture Analysis

### Two-Level MCP Structure

1. **Basic MCP Layer** (`testudo/agents/mcp/`)
   - Core MCP operations (script_ops.py, action_logger.py)
   - Low-level helpers for file operations
   - Repository analyzer
   - Direct function-based tools

2. **Complex Workflow Layer** (`testudo/agents/pulsus/workflows/`)
   - High-level, LLM-enhanced tools
   - JSON workflow definitions
   - Tools with `__domain__` and `__action__` metadata
   - Context-aware operations (repository awareness, session history)

### Existing Features to Preserve and Enhance

#### UI & Display Features (agents/pulsus/ui/)
- **display_manager.py**: Rich terminal output with clickable links, colored sections
- **streaming.py**: LLM streaming response handling
- **Features**:
  - Clickable file paths with line numbers
  - Progress indicators
  - Framework awareness status
  - Repository analysis progress
  - Section headers and key-value displays

#### Action Logging (agents/mcp/helpers/action_logger.py)
- **Existing capabilities**:
  - Records all MCP actions with timestamps
  - File hash tracking (before/after)
  - Session-based logs
  - Query by file, session, or action ID
  - Markdown report export

#### Routing System (agents/pulsus/routing/)
- **mcp_router.py**: Workflow-based routing with semantic matching
- **tool_discovery.py**: Deprecated, functionality moved to mcp_router
- **router.py**: Main routing logic (DISCOVER, COMPOSE, GENERATE)
- **Features**:
  - @path pattern detection
  - Workflow JSON loading
  - MCP tool registry integration
  - Score-based tool selection

#### Workflow Tools (agents/pulsus/workflows/tools/)
- **Structure**: `tools/{domain}/{tool_name}.py`
- **Metadata**: `__domain__` and `__action__` for discovery
- **handle() function**: Standard entry point
- **Features**:
  - LLM integration for intelligent analysis
  - Streaming responses
  - Interrupt handling (ESC key)
  - Repository context loading
  - Session history integration

---

## Implementation Plan

### Phase 1 — MCP Core Framework ✨

**Objective**: Establish standardized base classes, decorators, and logging for all MCP operations

#### 1.1 MCPBase Class (`agents/mcp/core/base.py`)
```python
class MCPResponse:
    """Standardized MCP response structure"""
    success: bool
    context: Dict[str, Any]  # Caller, object info, environment
    data: Any                # Operation result
    error: Optional[str]     # Error message if failed
    trace: List[str]         # Execution trace for debugging

class MCPBase:
    """Base class for all MCP helpers"""
    - __init__(self, logger: MCPLogger)
    - execute(self, operation: str, **kwargs) -> MCPResponse
    - _validate_inputs(self, **kwargs) -> bool
    - _log_operation(self, operation, params, result)
    - get_capabilities(self) -> List[str]
```

#### 1.2 Decorator System (`agents/mcp/core/decorators.py`)
```python
@read_only         # Safe in plan mode, no writes
@write        
@restricted_write  # Additional validation required
@transactional     # Supports rollback
@cached           # Cache results for performance
```

**Integration with existing features**:
- Use `agents.pulsus.ui.display_manager` for decorator output
- Integrate with `agents.mcp.helpers.action_logger` for logging

#### 1.3 Enhanced Logging (`agents/mcp/core/logger.py`)
```python
class MCPLogger:
    """Enhanced logging with SafeNet integration"""
    - log_call(caller, function, params, timestamp)
    - log_result(success, data, error, trace)
    - get_history(filters) -> List[MCPAction]
```

**Extends existing**:
- Builds on `agents.mcp.helpers.action_logger.MCPActionLogger`
- Adds caller tracking (Pulse, Shell, Compass)
- Integrates with UI display for live SafeNet panel

#### 1.4 Safety Policy (`agents/mcp/core/policy.py`)
```python
class ExecutionMode(Enum):
    PLAN = "plan"          # Read-only operations
    EXECUTE = "execute"    # Requires confirmations

class SafetyPolicy:
    """Safety policy enforcement"""
    - validate_operation(mode, operation, target) -> bool
    - check_type_safety(obj, expected_types) -> bool
    - require_confirmation(operation, target) -> bool
```

**Deliverables**:
- ✅ `agents/mcp/core/__init__.py`
- ✅ `agents/mcp/core/base.py` (MCPBase, MCPResponse)
- ✅ `agents/mcp/core/decorators.py` (decorators)
- ✅ `agents/mcp/core/logger.py` (MCPLogger)
- ✅ `agents/mcp/core/policy.py` (SafetyPolicy)
- ✅ Unit tests for core framework

---

### Phase 2 — Class-Based MCP Helpers 🏗️

**Objective**: Group MCP functions into domain-specific classes

#### 2.1 ScriptManager (`agents/mcp/helpers/script_manager.py`)
```python
class ScriptManager(MCPBase):
    """Manages Python script operations"""

    @read_only
    def read_script(self, path: str) -> MCPResponse:
        """Read and analyze script with AST"""

    @write
    def write_docstring(self, path: str, function: str,
                       docstring: str) -> MCPResponse:
        """Add docstring to function"""

    @write
    def format_script(self, path: str) -> MCPResponse:
        """Format with black/isort/autoflake"""

    @read_only
    def get_dependencies(self, path: str) -> MCPResponse:
        """Extract import dependencies"""
```

**Refactor from**:
- `agents.mcp.helpers.script_ops.ScriptOps`
- Keep existing functionality, add class structure

#### 2.2 ModelInspector (`agents/mcp/helpers/model_inspector.py`)
```python
class ModelInspector(MCPBase):
    """Inspects Aimsun/QGIS model objects"""

    @read_only
    def get_object_info(self, obj_id: Any) -> MCPResponse:
        """Get object properties and metadata"""

    @read_only
    def query_catalog(self, type_filter: str) -> MCPResponse:
        """Query model catalog for objects"""

    @read_only
    def get_screenlines(self, group_name: str) -> MCPResponse:
        """Get screenlines from group"""
```

**New capability** for Aimsun/QGIS integration

#### 2.3 LayerManager (`agents/mcp/helpers/layer_manager.py`)
```python
class LayerManager(MCPBase):
    """Manages map layers (QGIS focus)"""

    @read_only
    def list_layers(self) -> MCPResponse:
        """List all layers in project"""

    @read_only
    def read_layer_objects(self, layer_name: str) -> MCPResponse:
        """Read objects from layer"""

    @write_safe
    def create_layer(self, name: str, type: str) -> MCPResponse:
        """Create new layer"""
```

**New capability** for QGIS integration

#### 2.4 DataAnalyzer (`agents/mcp/helpers/data_analyzer.py`)
```python
class DataAnalyzer(MCPBase):
    """Analyzes model data and results"""

    @read_only
    def aggregate_results(self, query: dict) -> MCPResponse:
        """Aggregate simulation results"""

    @read_only
    def filter_objects(self, criteria: dict) -> MCPResponse:
        """Filter objects by criteria"""

    @read_only
    def analyze_layer_data(self, layer: str,
                           metric: str) -> MCPResponse:
        """Analyze layer data"""
```

**New capability** for data analysis

#### 2.5 RepositoryManager (`agents/mcp/helpers/repository_manager.py`)
```python
class RepositoryManager(MCPBase):
    """Manages repository analysis and context"""

    @read_only
    @cached
    def analyze_repository(self, path: str) -> MCPResponse:
        """Comprehensive repository analysis"""

    @read_only
    def load_context(self, path: str) -> MCPResponse:
        """Load .pulsus/ context if available"""

    @write_safe
    def save_context(self, path: str, context: dict) -> MCPResponse:
        """Save analysis to .pulsus/"""
```

**Refactor from**:
- `agents.mcp.helpers.repository_analyzer.py`
- `agents.pulsus.workflows.utils.context_loader.py`

**Deliverables**:
- ✅ `agents/mcp/helpers/script_manager.py`
- ✅ `agents/mcp/helpers/model_inspector.py`
- ✅ `agents/mcp/helpers/layer_manager.py`
- ✅ `agents/mcp/helpers/data_analyzer.py`
- ✅ `agents/mcp/helpers/repository_manager.py`
- ✅ Update `agents/shared/tools.py` to expose as LangChain tools
- ✅ Maintain backward compatibility with existing functions

---

### Phase 3 — Workflow & Tool Integration 🔗

**Objective**: Integrate MCP classes with Pulsus workflows and routing

#### 3.1 Tool Discovery Enhancement (`agents/pulsus/routing/mcp_router.py`)

**Current capabilities**:
- Loads workflow JSON files
- Matches user intent to workflows
- Semantic matching for domain/action

**Enhancements**:
```python
class MCPRouter:
    def _load_mcp_class_tools(self):
        """
        Discover MCP class methods and register as tools
        - Scan agents/mcp/helpers/ for MCPBase subclasses
        - Extract method metadata (read_only, write_safe, etc.)
        - Generate tool descriptions from docstrings
        - Register with MCP tools registry
        """

    def discover_tools(self, domain, action, intent):
        """
        Enhanced discovery:
        1. Check workflow JSON files (high priority)
        2. Check MCP class methods (medium priority)
        3. Check legacy MCP functions (low priority)
        4. Boost scores for workflow-wrapped tools
        """
```

#### 3.2 Workflow JSON Enhancement

**Add MCP class binding** to workflow definitions:
```json
{
  "id": "analyze_screenlines",
  "domain": "analysis",
  "action": "get_screenlines",
  "description": "Analyze screenlines from Aimsun model",
  "mcp_class": "ModelInspector",
  "mcp_method": "get_screenlines",
  "preprompt": {
    "system": "You are analyzing Aimsun screenline data...",
    "instructions": [...]
  },
  "steps": [
    {
      "tool": "agents.mcp.helpers.model_inspector.ModelInspector",
      "entry": "get_screenlines",
      "params": {
        "group_name": "${input.group_name}"
      }
    }
  ]
}
```

#### 3.3 Startup Discovery (`agents/pulsus/config/features_display.py`)

**Current**: Displays MCP tools at startup
**Enhancement**: Automatic workflow and MCP class discovery

```python
def discover_and_display_mcp_features():
    """
    Discover all MCP features at startup:
    1. Scan workflow JSON files
    2. Discover MCP class helpers
    3. Display organized by domain
    4. Show capabilities summary
    """
```

**Display format**:
```
════════════════════════════════════════════════════════════
  PULSUS MCP CAPABILITIES
════════════════════════════════════════════════════════════

📋 SCRIPT OPERATIONS (ScriptManager)
   • read_script         [read-only]    - Analyze Python scripts
   • write_docstring     [write]        - Add function docstrings
   • format_script       [write]        - Auto-format code
   • get_dependencies    [read-only]    - Extract imports

🔍 MODEL INSPECTOR (ModelInspector)
   • get_object_info     [read-only]    - Query object properties
   • query_catalog       [read-only]    - Search model catalog
   • get_screenlines     [read-only]    - Extract screenline data

🗺️  LAYER MANAGER (LayerManager)
   • list_layers         [read-only]    - List map layers
   • read_layer_objects  [read-only]    - Read layer features
   • create_layer        [write]        - Create new layer

📊 DATA ANALYZER (DataAnalyzer)
   • aggregate_results   [read-only]    - Aggregate simulation data
   • filter_objects      [read-only]    - Filter by criteria
   • analyze_layer_data  [read-only]    - Analyze layer metrics

📦 REPOSITORY MANAGER (RepositoryManager)
   • analyze_repository  [read-only]    - Comprehensive repo analysis
   • load_context        [read-only]    - Load .pulsus/ context
   • save_context        [write]        - Save analysis results

════════════════════════════════════════════════════════════
  Available: 15 MCP tools across 5 domains
════════════════════════════════════════════════════════════
```

**Deliverables**:
- ✅ Update `agents/pulsus/routing/mcp_router.py` for class discovery
- ✅ Create workflow JSON templates for common MCP operations
- ✅ Enhance `agents/pulsus/config/features_display.py`
- ✅ Add `agents/pulsus/config/mcp_registry.py` for dynamic registration
- ✅ Documentation in `agents/pulsus/workflows/README.md`

---

### Phase 4 — Safety & Policy Enforcement 🔒

**Objective**: Ensure safe operation with validation and confirmation

#### 4.1 Decorator Implementation

**Safety levels**:
- `@read_only`: Always safe, no confirmation needed
- `@write_safe`: Requires user confirmation in interactive mode
- `@restricted_write`: Additional validation (e.g., check object type)
- `@transactional`: Supports rollback if operation fails

**Integration with UI**:
```python
from agents.pulsus.ui import display_manager as ui

@write_safe
def write_docstring(self, path: str, docstring: str):
    # Display confirmation prompt
    ui.warn(f"About to modify file: {path}")
    ui.kv("Operation", "Add docstring")
    ui.kv("Safety Level", "write-safe")

    # Get user confirmation (handled by decorator)
    # ... perform operation

    # Log with SafeNet
    self.logger.log_call("write_docstring", locals())
```

#### 4.2 Type Validation

```python
class SafetyPolicy:
    KNOWN_TYPES = {
        'aimsun': ['GKSection', 'GKNode', 'GKCentroid', ...],
        'qgis': ['QgsVectorLayer', 'QgsFeature', ...],
    }

    def validate_object_type(self, obj, platform: str) -> bool:
        """Validate object is known safe type"""
```

#### 4.3 Error Handling

**All MCP methods** return `MCPResponse` instead of raising exceptions:
```python
try:
    result = perform_operation()
    return MCPResponse(success=True, data=result)
except Exception as e:
    return MCPResponse(
        success=False,
        error=str(e),
        trace=[...]
    )
```

**Deliverables**:
- ✅ Implement decorator behavior in `agents/mcp/core/decorators.py`
- ✅ Add type validation in `agents/mcp/core/policy.py`
- ✅ Update all MCP helpers to use decorators
- ✅ Add confirmation UI flows
- ✅ Test safety policies with unit and integration tests

---

### Phase 5 — Logging & Traceability 📝

**Objective**: Complete audit trail with SafeNet integration

#### 5.1 Enhanced Action Logger

**Extend existing** `agents.mcp.helpers.action_logger.py`:
```python
class EnhancedMCPLogger(MCPActionLogger):
    """Adds caller tracking and SafeNet integration"""

    def log_action(self, caller: str, tool_name: str,
                   operation: str, ...):
        """
        Extended logging with:
        - Caller identification (Pulse, Shell, Compass)
        - Object context (ID, type, properties)
        - Execution trace for debugging
        """
```

#### 5.2 SafeNet Panel Display

**Add live monitoring** (optional Qt UI integration):
```python
class SafeNetPanel:
    """Real-time MCP event display"""

    def show_event(self, event: MCPAction):
        """Display MCP event in SafeNet panel"""

    def show_history(self, limit: int = 20):
        """Show recent MCP actions"""
```

#### 5.3 Query and Review

```python
# Query MCP history
logger = get_mcp_logger()
history = logger.get_history(
    caller="Pulse",
    operation="write",
    timeframe="last_hour"
)

# Export SafeNet report
report_path = logger.export_safenet_report(
    format="markdown",
    include_traces=True
)
```

**Deliverables**:
- ✅ Extend `MCPActionLogger` with caller tracking
- ✅ Add SafeNet report templates
- ✅ Create query API for MCP history
- ✅ Optional: Qt SafeNet panel prototype
- ✅ Documentation for MCP logging

---

### Phase 6 — Documentation & Registry 📚

**Objective**: Auto-generated docs and dynamic tool registry

#### 6.1 Method Documentation

**Extract from MCP classes**:
```python
def generate_mcp_docs(class_name: str):
    """
    Auto-generate documentation from MCP class:
    - Class docstring
    - Method signatures
    - Parameter descriptions (from docstrings)
    - Safety level indicators
    - Usage examples
    """
```

**Output**: `MCP_ModelInspector.md`, `MCP_ScriptManager.md`, etc.

#### 6.2 Dynamic Registry

```python
class MCPRegistry:
    """Central registry of all MCP capabilities"""

    def register_class(self, cls: Type[MCPBase]):
        """Register MCP class and methods"""

    def get_methods(self, domain: str = None) -> List[dict]:
        """Get available methods by domain"""

    def introspect(self, class_name: str, method_name: str):
        """Get detailed method info"""
```

**Used by**:
- Routing system for tool discovery
- LLM for capability awareness
- Documentation generation

**Deliverables**:
- ✅ `agents/mcp/core/registry.py`
- ✅ Auto-generate docs in `agents/mcp/docs/`
- ✅ Update `agents/pulsus/workflows/README.md`
- ✅ Add introspection API for LLM queries

---

### Phase 7 — Advanced Features 🚀

**Objective**: Performance and multi-agent support

#### 7.1 Caching

```python
@read_only
@cached(ttl=300)  # Cache for 5 minutes
def query_catalog(self, type_filter: str) -> MCPResponse:
    """Cached catalog queries"""
```

#### 7.2 Cross-Agent Validation

```python
# Pulse generates MCP call
pulse_result = model_inspector.get_screenlines("Group1")

# Shell validates the call
shell_validation = validate_mcp_call(
    caller="Pulse",
    action_id=pulse_result.action_id
)
```

#### 7.3 Versioning

```python
class ScriptManagerV1(MCPBase):
    """Version 1 implementation"""

class ScriptManagerV2(MCPBase):
    """Version 2 with breaking changes"""

# Route to appropriate version
router.get_class_version("ScriptManager", version="v2")
```

**Deliverables**:
- ✅ Add caching decorator
- ✅ Async method support (optional)
- ✅ Cross-agent validation utilities
- ✅ Versioning strategy documentation

---

## Integration Points

### With Existing Workflows
- **Preserve** all existing workflow JSON files
- **Enhance** with MCP class bindings
- **Maintain** backward compatibility with function-based tools

### With Routing System
- **Extend** `MCPRouter` for class-based discovery
- **Keep** existing workflow priority boosting
- **Add** MCP class method scoring

### With UI System
- **Use** `display_manager` for all output
- **Add** SafeNet panel notifications
- **Maintain** clickable links and progress indicators

### With Logging System
- **Build on** existing `MCPActionLogger`
- **Add** caller tracking and object context
- **Preserve** all existing log formats and queries

---

## Testing Strategy

### Unit Tests
- Core classes (MCPBase, MCPResponse)
- Decorators (read_only, write_safe, etc.)
- Safety policies
- Each MCP helper class

### Integration Tests
- Routing with MCP classes
- Workflow execution with MCP bindings
- Logging and audit trail
- UI display and confirmations

### End-to-End Tests
- Complete workflow: discover → execute → log
- Multi-agent scenarios (Pulse + Shell)
- Error handling and rollback
- Performance with caching

---

## Migration Path

### Phase 1: Non-Breaking Foundation (Week 1)
- Implement core framework
- Add decorator system
- Enhance logging
- **No changes to existing tools**

### Phase 2: Parallel Implementation (Week 2-3)
- Create class-based helpers
- Keep existing function-based tools working
- Add backward compatibility wrappers

### Phase 3: Integration (Week 4)
- Update routing for class discovery
- Enhance workflow JSON files
- Add startup discovery

### Phase 4: Validation & Testing (Week 5)
- Comprehensive testing
- Documentation
- User validation

### Phase 5: Deprecation (Week 6+)
- Mark old functions as deprecated
- Migrate all workflows to class-based
- Remove legacy code

---

## Success Metrics

✅ **Functionality**
- All existing MCP operations work with class-based system
- New capabilities (ModelInspector, LayerManager) operational
- No regression in routing or tool discovery

✅ **Safety**
- All operations properly decorated
- SafeNet logging captures all actions
- User confirmations work correctly

✅ **Performance**
- Caching reduces repeated queries
- Startup discovery < 2 seconds
- No performance degradation vs. function-based

✅ **Usability**
- Clear documentation for all MCP classes
- LLM can discover and use new capabilities
- Developers can easily add new MCP classes

---

## Next Steps

1. **Review and approve** this implementation plan
2. **Create GitHub issues** for each phase
3. **Set up development branch** for MCP refactoring
4. **Begin Phase 1** implementation
5. **Weekly reviews** to track progress and adjust plan

---

## References

- **Original TODO**: `testudo/agents/pulsus/routing/MCP-PULSUS-TODO.md`
- **UI Features**: `testudo/agents/pulsus/ui/README.md`
- **Workflow Guide**: `testudo/agents/pulsus/workflows/README.md`
- **Existing MCP**: `testudo/agents/mcp/helpers/`
- **Routing System**: `testudo/agents/pulsus/routing/`
