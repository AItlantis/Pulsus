# MCP Core Framework

**Status**: Phase 1 Complete ✅

The MCP Core Framework provides the foundational classes, decorators, and utilities for building class-based MCP (Model Context Protocol) helpers.

---

## Components

### 1. MCPResponse & MCPBase (`base.py`)

**MCPResponse**: Standardized response structure for all MCP operations.

```python
from agents.mcp.core import MCPResponse

# Success response
response = MCPResponse.success_response(
    data={'result': 'value'},
    context={'caller': 'Pulse'},
    trace=['Step 1', 'Step 2']
)

# Error response
response = MCPResponse.error_response(
    error='Operation failed',
    context={'operation': 'test'}
)

# Response attributes
response.success      # bool
response.data         # any type
response.error        # str or None
response.context      # dict
response.trace        # list of strings
response.status       # MCPStatus enum
response.metadata     # dict (includes timestamp)
```

**MCPBase**: Base class for all MCP helpers.

```python
from agents.mcp.core import MCPBase, read_only, MCPResponse

class MyHelper(MCPBase):
    @read_only
    def get_info(self, obj_id: str) -> MCPResponse:
        """Get object information"""
        return MCPResponse.success_response(
            data={'id': obj_id, 'info': 'details'}
        )

# Use the helper
helper = MyHelper(logger=logger, context={'caller': 'Pulse'})
result = helper.get_info('obj-123')

# Execute by name
result = helper.execute('get_info', obj_id='obj-123')

# Introspect capabilities
caps = helper.get_capabilities()
# [{'name': 'get_info', 'safety_level': 'read_only', ...}]
```

---

### 2. Decorators (`decorators.py`)

**@read_only**: Safe operations with no side effects.

```python
@read_only
def query_data(self, filter: str) -> MCPResponse:
    """Query data (read-only, safe in all modes)"""
    return MCPResponse.success_response(data=results)
```

**@write_safe**: Operations that modify data (requires confirmation).

```python
@write_safe
def update_file(self, path: str, content: str) -> MCPResponse:
    """Update file (requires user confirmation)"""
    Path(path).write_text(content)
    return MCPResponse.success_response()
```

**@restricted_write**: Write operations with type validation.

```python
@restricted_write(platform='aimsun')
def modify_section(self, section) -> MCPResponse:
    """Modify Aimsun section (validates type)"""
    section.setSpeed(50)
    return MCPResponse.success_response()
```

**@transactional**: Operations that support rollback.

```python
def rollback_handler(self, *args, **kwargs):
    """Custom rollback logic"""
    # Restore previous state
    pass

@transactional(rollback_handler=rollback_handler)
def batch_update(self, items: list) -> MCPResponse:
    """Batch update with rollback support"""
    for item in items:
        item.update()
    return MCPResponse.success_response()
```

**@cached**: Cache results for performance.

```python
@read_only
@cached(ttl=300)  # 5 minutes
def expensive_query(self, params: dict) -> MCPResponse:
    """Expensive operation with caching"""
    results = slow_database_query(params)
    return MCPResponse.success_response(data=results)
```

---

### 3. Safety Policy (`policy.py`)

**ExecutionMode**: Control operation execution.

```python
from agents.mcp.core import ExecutionMode, get_safety_policy

policy = get_safety_policy()

# Set execution mode
policy.set_mode(ExecutionMode.PLAN)      # Read-only mode
policy.set_mode(ExecutionMode.EXECUTE)   # Full execution
policy.set_mode(ExecutionMode.UNSAFE)    # Unrestricted (testing only)
```

**SafetyPolicy**: Manage operation policies.

```python
from agents.mcp.core import SafetyPolicy, SafetyLevel

policy = SafetyPolicy()

# Register operation
policy.register_operation(
    'update_model',
    SafetyLevel.WRITE_SAFE,
    requires_confirmation=True
)

# Validate operation
is_allowed, reason = policy.validate_operation(
    'update_model',
    mode=ExecutionMode.PLAN
)

# Check type safety
from pathlib import Path
is_safe, error = policy.check_type_safety(
    Path('.'),
    platform='python'
)

# Register custom platform
policy.register_platform('custom', ['MyType', 'OtherType'])

# List operations
read_ops = policy.list_operations(safety_level=SafetyLevel.READ_ONLY)

# Get summary
summary = policy.get_summary()
# {
#   'total_operations': 10,
#   'current_mode': 'execute',
#   'by_safety_level': {...},
#   'platforms': ['aimsun', 'qgis', 'python']
# }
```

**SafetyLevel**: Operation safety levels.

- `READ_ONLY`: No side effects, safe in all modes
- `WRITE_SAFE`: Modifies data, requires confirmation
- `RESTRICTED_WRITE`: Additional type validation
- `TRANSACTIONAL`: Supports rollback
- `CACHED`: Results cached for performance

---

### 4. Logger (`logger.py`)

**MCPLogger**: Enhanced logging with SafeNet integration.

```python
from agents.mcp.core import MCPLogger, get_mcp_logger

# Get global logger
logger = get_mcp_logger()

# Log a call
call_id = logger.log_call(
    caller='Pulse',
    mcp_class='ScriptManager',
    operation='read_script',
    params={'path': 'script.py'},
    result={'success': True, 'data': {...}},
    success=True,
    context={'mode': 'execute'}
)

# Get call history
history = logger.get_history(caller='Pulse', limit=10)

# Filter history
pulse_calls = logger.get_calls_by_caller('Pulse')
script_calls = logger.get_calls_by_class('ScriptManager')

# Export SafeNet report
report_path = logger.export_safenet_report(
    caller='Pulse',
    timeframe='last_hour'
)

# Get summary
summary = logger.get_summary()
# {
#   'total_calls': 50,
#   'successful': 48,
#   'failed': 2,
#   'success_rate': 96.0,
#   'by_caller': {'Pulse': 30, 'Shell': 20},
#   'by_class': {...},
#   'by_operation': {...}
# }
```

---

## Complete Example

```python
from agents.mcp.core import (
    MCPBase,
    MCPResponse,
    read_only,
    write_safe,
    cached,
    get_mcp_logger
)

class DataManager(MCPBase):
    """Manages data operations with safety policies"""

    def __init__(self):
        logger = get_mcp_logger()
        super().__init__(logger=logger, context={'caller': 'Pulse'})

    @read_only
    @cached(ttl=60)
    def get_records(self, filter: str) -> MCPResponse:
        """
        Get records matching filter.

        Cached for 60 seconds for performance.
        """
        response = MCPResponse.success_response()
        response.add_trace("Querying database")

        # Query logic
        records = self._query_db(filter)

        response.data = records
        response.add_trace(f"Found {len(records)} records")

        return response

    @write_safe
    def update_record(self, record_id: str, data: dict) -> MCPResponse:
        """
        Update a record.

        Requires user confirmation in interactive mode.
        """
        response = MCPResponse.success_response()
        response.add_trace(f"Updating record {record_id}")

        try:
            # Update logic
            self._update_db(record_id, data)
            response.data = {'updated': True, 'record_id': record_id}
            response.add_trace("Update successful")
        except Exception as e:
            response.set_error(f"Update failed: {str(e)}")

        return response

    def _query_db(self, filter: str) -> list:
        """Database query implementation"""
        return []

    def _update_db(self, record_id: str, data: dict):
        """Database update implementation"""
        pass


# Use the manager
manager = DataManager()

# Read operation (cached, no confirmation)
result = manager.get_records("status=active")
print(f"Success: {result.success}")
print(f"Records: {result.data}")
print(f"Cached: {result.context.get('cached', False)}")

# Write operation (requires confirmation)
result = manager.update_record("rec-123", {"status": "completed"})
print(f"Success: {result.success}")
print(f"Safety level: {result.context.get('safety_level')}")

# Introspect capabilities
capabilities = manager.get_capabilities()
for cap in capabilities:
    print(f"- {cap['name']}: {cap['safety_level']}")

# Export SafeNet report
logger = get_mcp_logger()
report = logger.export_safenet_report()
print(f"Report saved to: {report}")
```

---

## Platform Types

The safety policy knows about these platform types:

**Aimsun**:
- GKSection, GKNode, GKCentroid, GKTurning
- GKDetector, GKReplication, GKExperiment
- GKModel, GKCatalog, GKLayer, GKFolder

**QGIS**:
- QgsVectorLayer, QgsRasterLayer, QgsFeature
- QgsGeometry, QgsProject, QgsLayerTreeLayer
- QgsMapCanvas, QgsPoint, QgsRectangle

**Python**:
- Path, str, int, float, dict, list
- set, tuple, bool, None

Register custom platforms:
```python
policy = get_safety_policy()
policy.register_platform('myplatform', ['MyType', 'OtherType'])
```

---

## Testing

Run the test suite:

```bash
cd testudo
python -m pytest agents/mcp/tests/test_core_framework.py -v
```

Test coverage includes:
- MCPResponse creation and manipulation
- MCPBase capabilities and execution
- All decorators (read_only, write_safe, etc.)
- SafetyPolicy validation and type checking
- MCPLogger call tracking and reporting
- Integration tests

---

## Next Steps: Phase 2

With the core framework complete, Phase 2 will:

1. **Create class-based MCP helpers**:
   - ScriptManager (refactor script_ops.py)
   - ModelInspector (new - Aimsun/QGIS)
   - LayerManager (new - QGIS focus)
   - DataAnalyzer (new - data operations)
   - RepositoryManager (refactor repository_analyzer.py)

2. **Expose as LangChain tools**:
   - Update `agents/shared/tools.py`
   - Generate tool wrappers automatically
   - Maintain backward compatibility

3. **Integration with Pulsus**:
   - Update routing for class discovery
   - Enhance workflow JSON definitions
   - Add startup discovery

---

## API Reference

### MCPResponse

- `success: bool` - Operation success status
- `data: Any` - Result data
- `error: Optional[str]` - Error message
- `context: Dict[str, Any]` - Contextual information
- `trace: List[str]` - Execution trace
- `status: MCPStatus` - Status enum
- `metadata: Dict[str, Any]` - Additional metadata

Methods:
- `add_trace(message: str)` - Add trace message
- `set_error(error_msg: str)` - Set error state
- `to_dict() -> Dict` - Convert to dictionary
- `success_response(...)` - Create success response (classmethod)
- `error_response(...)` - Create error response (classmethod)

### MCPBase

Methods:
- `execute(operation: str, **kwargs) -> MCPResponse` - Execute operation by name
- `get_capabilities() -> List[Dict]` - Get list of capabilities
- `_create_response(...) -> MCPResponse` - Create response with context
- `_log_operation(...)` - Log operation to logger
- `_validate_inputs(**kwargs) -> tuple` - Validate inputs

### SafetyPolicy

Methods:
- `set_mode(mode: ExecutionMode)` - Set execution mode
- `register_operation(...)` - Register operation policy
- `get_policy(operation: str) -> OperationPolicy` - Get operation policy
- `validate_operation(...) -> tuple` - Validate if operation allowed
- `check_type_safety(...) -> tuple` - Check object type safety
- `requires_confirmation(operation: str) -> bool` - Check confirmation requirement
- `list_operations(...) -> List[str]` - List operations
- `get_summary() -> Dict` - Get policy summary

### MCPLogger

Methods:
- `log_call(...)` - Log MCP call
- `get_history(...) -> List` - Get call history
- `get_calls_by_caller(caller: str) -> List` - Filter by caller
- `get_calls_by_class(mcp_class: str) -> List` - Filter by class
- `export_safenet_report(...) -> str` - Export SafeNet report
- `get_summary() -> Dict` - Get logging summary
- `clear_history()` - Clear in-memory history

---

**MCP Core Framework** - Foundation for Class-Based MCP Architecture
