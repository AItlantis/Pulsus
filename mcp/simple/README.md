# MCP Simple Domains

Classic MCP domains migrated to the MCPBase framework.

## Overview

This directory contains "simple" MCP domains - standalone operation classes that provide common functionality for interacting with code, files, and data. All domains in this directory:

- Extend `MCPBase` for standardized operation interface
- Return `MCPResponse` for consistent LLM interaction
- Use safety decorators (`@read_only`, `@write_safe`, etc.)
- Support capability introspection via `get_capabilities()`
- Include automatic operation logging via MCPLogger
- Provide trace messages for debugging

## Available Domains

### ScriptOps

**Purpose**: Python script manipulation and analysis

**Operations**:
- `read_script(path)` - Read and analyze Python scripts (AST parsing)
- `write_md(path, content)` - Generate/write Markdown documentation
- `add_comments(path, strategy)` - Generate docstrings for functions
- `format_script(path, check_only)` - Auto-format code (black, isort, autoflake)
- `scan_structure(base_dir, include_patterns, exclude_patterns)` - Scan directory structure and build dependency map

**Safety Levels**:
- Read-only: `read_script`, `add_comments`, `scan_structure`
- Write-safe: `write_md`, `format_script`

**Example Usage**:
```python
from mcp.simple import ScriptOps

# Create instance with logging and context
ops = ScriptOps(logger=logger, context={'caller': 'Pulse'})

# Read and analyze a script
result = ops.read_script('path/to/script.py')

if result.success:
    functions = result.data['ast_analysis']['functions']
    print(f"Found {len(functions)} functions")

    # Generate comments
    comments_result = ops.add_comments('path/to/script.py')
    for comment in comments_result.data['comments']:
        print(f"{comment['function']}: {comment['comment']}")
```

---

### RepositoryOps

**Purpose**: Python repository analysis and management

**Operations**:
- `analyze_repository(repo_path, ignore_patterns)` - Comprehensive repository analysis
- `validate_file(file_path)` - Validate single Python file
- `generate_excel_report(analysis_result, output_path)` - Generate Excel report
- `analyze_dependencies(repo_path, ignore_patterns)` - Analyze dependencies
- `analyze_reusability(repo_path, ignore_patterns, min_score)` - Function reusability scoring
- `get_issues_summary(repo_path, ignore_patterns, priority)` - Get issues summary
- `get_statistics(repo_path, ignore_patterns)` - Get repository statistics
- `scan_repository(repo_path, include_stats)` - Quick repository scan

**Safety Levels**:
- Read-only: `analyze_repository`, `validate_file`, `analyze_dependencies`, `analyze_reusability`, `get_issues_summary`, `get_statistics`, `scan_repository`
- Write-safe: `generate_excel_report`

**Caching**:
- `analyze_repository`: 10 minutes
- `analyze_dependencies`: 5 minutes
- `analyze_reusability`: 5 minutes
- `get_statistics`: 5 minutes
- `scan_repository`: 10 minutes

**Example Usage**:
```python
from mcp.simple import RepositoryOps

# Create instance
ops = RepositoryOps(context={'caller': 'Pulse'})

# Analyze a repository
result = ops.analyze_repository('path/to/repo')

if result.success:
    stats = result.data['statistics']
    print(f"Files: {stats['total_files']}")
    print(f"Functions: {stats['total_functions']}")
    print(f"Lines: {stats['total_lines']}")

    # Get reusability analysis
    reusability = ops.analyze_reusability('path/to/repo', min_score=5)
    if reusability.success:
        for func in reusability.data['highly_reusable_functions']:
            print(f"{func['function']}: score {func['score']}")

    # Generate Excel report
    report = ops.generate_excel_report(result.data, 'report.xlsx')
    if report.success:
        print(f"Report saved: {report.data['output_path']}")
```

---

## Migration from Old Format

Domains in this directory were migrated from `mcp/helpers/` to use the new MCPBase framework.

### Key Changes

1. **Class inheritance**:
   ```python
   # Old
   class ScriptOps:
       def __init__(self):
           self.settings = load_settings()

   # New
   class ScriptOps(MCPBase):
       def __init__(self, logger=None, context=None):
           super().__init__(logger=logger, context=context)
           self.settings = load_settings()
   ```

2. **Return types**:
   ```python
   # Old
   def read_script(self, path: str) -> Dict[str, Any]:
       return {
           'success': True,
           'content': content,
           'ast_analysis': analysis,
           'error': None
       }

   # New
   @read_only
   def read_script(self, path: str) -> MCPResponse:
       response = self._create_response()
       response.add_trace("Reading script...")
       # ... operation logic
       response.data = {'content': content, 'ast_analysis': analysis}
       return response
   ```

3. **Logging**:
   ```python
   # Old
   log_mcp_action(
       tool_name="mcp_read_script",
       operation="read",
       target_path=path,
       parameters={"path": path},
       result=result,
       success=True
   )

   # New
   # Automatic via MCPBase._log_operation() - no manual logging needed
   ```

4. **Safety decorators**:
   ```python
   # Old
   def read_script(self, path: str):
       # No safety enforcement

   # New
   @read_only  # Enforces safety policy
   def read_script(self, path: str) -> MCPResponse:
       # Safety automatically enforced by decorator
   ```

## Benefits of MCPBase Framework

1. **Standardized Interface**
   - All domains return `MCPResponse` with consistent structure
   - LLMs can reliably parse responses
   - Easier error handling and debugging

2. **Safety Enforcement**
   - `@read_only` decorator for safe read operations
   - `@write_safe` decorator with user confirmation for writes
   - `@cached` decorator for performance optimization
   - Policy validation before execution

3. **Automatic Logging**
   - All operations automatically logged to SafeNet
   - Caller tracking (Pulse, Shell, Compass)
   - Operation parameters and results recorded
   - Performance metrics captured

4. **Introspection**
   - `get_capabilities()` lists all operations
   - Safety levels visible to LLM
   - Parameters and return types documented
   - Enables dynamic tool discovery

5. **Trace Messages**
   - Execution steps recorded in `response.trace`
   - Useful for debugging and explaining actions
   - LLM can see what happened during operation

## Testing

All domains have comprehensive test coverage in `mcp/tests/test_simple_domains.py`.

Run tests:
```bash
python -m pytest mcp/tests/test_simple_domains.py -v
```

Or run integration test:
```bash
python test_integration.py
```

## Creating New Simple Domains

To add a new simple domain:

1. **Create the domain class**:
   ```python
   from mcp.core.base import MCPBase, MCPResponse
   from mcp.core.decorators import read_only, write_safe

   class MyDomain(MCPBase):
       """Description of your domain"""

       def __init__(self, logger=None, context=None):
           super().__init__(logger=logger, context=context)

       @read_only
       def my_read_operation(self, param: str) -> MCPResponse:
           response = self._create_response()
           response.add_trace("Starting operation")
           # ... do work
           response.data = {'result': 'value'}
           return response

       @write_safe
       def my_write_operation(self, target: str) -> MCPResponse:
           response = self._create_response()
           # ... do work
           return response
   ```

2. **Add to `__init__.py`**:
   ```python
   from .my_domain import MyDomain

   __all__ = ['ScriptOps', 'MyDomain']
   ```

3. **Write tests** in `mcp/tests/test_simple_domains.py`

4. **Document** operations and safety levels in this README

## Safety Decorator Reference

- `@read_only` - Safe read operations, no side effects
- `@write_safe` - Write operations requiring confirmation
- `@restricted_write(allowed_types=[...])` - Type-validated writes
- `@transactional(rollback_handler=...)` - Operations with rollback
- `@cached(ttl=300)` - Cached operations (5 min default TTL)

## Integration with Routing

Simple domains are automatically discovered by the MCP router when registered:

```python
from mcp.simple import ScriptOps
from routing.mcp_router import MCPRouter

router = MCPRouter()
router.register_domain(ScriptOps)

# Router can now route to ScriptOps operations
result = router.route("read script at path/to/file.py")
```

## Migration Status

- ✅ **ScriptOps** - Migrated (Day 1-2, Week 1)
- ⏳ **RepositoryOps** - Planned (Day 3-4, Week 1)
- ⏳ **FileManager** - Planned (Day 5, Week 1)
- ⏳ **DataReader** - Planned (Week 2)
- ⏳ **TextProcessor** - Planned (Week 2)

See `docs/PHASE2_PLAN.md` for full migration timeline.
