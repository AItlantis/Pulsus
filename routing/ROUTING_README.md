# Pulsus Routing System

## Overview

The Pulsus routing system has been simplified and made more flexible by consolidating routing logic into a unified MCP-aware architecture.

## Architecture

### Core Components

1. **`mcp_router.py`** - Unified MCP-aware router
   - `MCPRouter` class: Main router with dynamic tool discovery
   - Semantic intent parsing instead of keyword matching
   - Integration with MCP tools registry
   - Workflow definition loading from JSON files

2. **`router.py`** - Main routing orchestration
   - Uses MCPRouter for parsing and discovery
   - Handles policy selection (compose/select/generate)
   > I need to refine the routing policy, when apply compose select or generate in script management only
   > for general operation and mcp, its another policy + gneeraiton
   - Manages validation and execution pipeline

3. **`__init__.py`** - Package exports
   - Provides clean API for routing functionality
   - Backward compatibility with old imports

### Deprecated (Backward Compatible)

- **`prompt_parser.py`** - Replaced by MCPRouter.parse_intent()
- **`tool_discovery.py`** - Replaced by MCPRouter.discover_tools()

Both files now serve as thin wrappers for backward compatibility.

## Key Features

### 1. Dynamic Tool Discovery

The MCPRouter discovers tools from two sources:

**Workflows** (JSON files):
```json
{
    "id": "file_analysis",
    "domain": "analysis",
    "action": "analyze_file",
    "description": "Analyze Python files provided with @path syntax",
    "steps": [
        {
            "tool": "agents/pulsus/workflows/tools/analyze/file_analyzer.py",
            "entry": "handle"
        }
    ]
}
```

**MCP Tools** (from `agents/shared/tools.py`):
- `mcp_read_script` - Read and analyze Python scripts
- `mcp_write_md` - Generate Markdown documentation
- `mcp_add_comments` - Generate docstrings
- `mcp_format_script` - Auto-format code
- `mcp_scan_structure` - Scan directory structure
- `search_aimsun_docs` - Search Aimsun API docs
- `search_qgis_docs` - Search QGIS API docs
- And more...

### 2. Semantic Intent Parsing

Instead of hardcoded keyword maps, the router uses semantic matching:

```python
router = MCPRouter(workflows_root)
a
# Parse user intent
parsed = router.parse_intent("analyze this Python file")
# Result: domain='script_ops', action='read_script', confidence=0.82

# Discover relevant tools
tools = router.discover_tools(parsed.domain, parsed.action, parsed.intent)
# Returns: [ToolSpec(path='mcp://mcp_read_script', score=0.95), ...]
```

### 3. Flexible and Extensible

**Add new tools** by:
1. Creating MCP tools in `agents/shared/tools.py` (preferred)
2. Adding workflow JSON definitions
3. Placing scripts in the framework directory

**No code changes required** - the router automatically discovers new tools.

## Usage

### Basic Routing

```python
from agents.pulsus.routing import route

# Route user input
decision = route("analyze my Python script", non_interactive=True)

print(f"Policy: {decision.policy}")
print(f"Selected tools: {decision.selected}")
print(f"Generated path: {decision.tmp_path}")
```

### Advanced Usage

```python
from agents.pulsus.routing import MCPRouter
from agents.pulsus.config.settings import load_settings

# Create router instance
settings = load_settings()
router = MCPRouter(settings.workflows_root)

# List available workflows
workflows = router.list_workflows()
for wf in workflows:
    print(f"{wf.id}: {wf.domain}/{wf.action}")

# List available MCP tools
tools = router.list_mcp_tools()
for name, tool in tools.items():
    print(f"{name}: {tool.description}")

# Parse and discover
parsed = router.parse_intent("format my code")
candidates = router.discover_tools(parsed.domain, parsed.action, parsed.intent)
```

## Migration Guide

### Old Code (Deprecated)
```python
from agents.pulsus.routing.prompt_parser import parse
from agents.pulsus.routing.tool_discovery import discover

parsed = parse(user_text)
candidates = discover(parsed.domain, parsed.action, parsed.intent)
```

### New Code (Recommended)
```python
from agents.pulsus.routing import MCPRouter
from agents.pulsus.config.settings import load_settings

settings = load_settings()
router = MCPRouter(settings.workflows_root)

parsed = router.parse_intent(user_text)
candidates = router.discover_tools(parsed.domain, parsed.action, parsed.intent)
```

Or use the convenience functions:
```python
from agents.pulsus.routing import parse, discover

parsed = parse(user_text)
candidates = discover(parsed.domain, parsed.action, parsed.intent)
```

## Testing

Run the test suite:
```bash
python testudo/agents/pulsus/routing/test_mcp_router.py
```

Expected output:
```
[SUCCESS] ALL TESTS PASSED (5/5)
```

## Benefits

1. **Simplified** - One router instead of fragmented logic
2. **Flexible** - Semantic matching instead of hardcoded keywords
3. **Extensible** - Add tools via MCP without code changes
4. **Maintainable** - Clear separation of concerns
5. **Testable** - Comprehensive test coverage

## Next Steps

See `agents/pulsus/workflows/Pulsus-MCP-TODO.md` for planned enhancements:
- Phase 3: Metadata system for scripts
- Phase 4: Incremental documentation
- Phase 5: Search & indexing
- Phase 6: Iterative improvement
