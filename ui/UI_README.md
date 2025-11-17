# Pulsus User Interface & Features

**Pulsus** is an intelligent workflow routing agent for the Atlantis framework (QGIS and Aimsun Next). This document provides a comprehensive overview of all features, capabilities, and available tools.

---

## 🎯 Core Capabilities

### 1. DISCOVER
**Scan and score existing tools in your framework**

- Automatically discovers workflow tools in the framework directory
- Scores tools by relevance to user requests
- Selects best match based on domain, action, and intent
- Reduces need for redundant code generation

**Example:**
```
> Summarize the data matrix
→ Discovers and runs existing summarize_matrix.py tool
```

### 2. COMPOSE
**Plan and chain multi-step workflows**

- Plans complex workflows requiring multiple tools
- Chains tools together with data flow between steps
- Validates composition logic before execution
- Optimizes execution order

**Example:**
```
> Load CSV and plot statistics
→ Composes: load_data.py + calculate_stats.py + create_plot.py
```

### 3. GENERATE
**Create AI-powered solutions when nothing else fits**

- Uses LLM to generate new code when no existing tools match
- Creates complete, executable Python modules
- Follows framework conventions and patterns
- Fallback when DISCOVER and COMPOSE don't apply

**Example:**
```
> Export selection to GeoJSON with custom attributes
→ Generates new script tailored to specific requirements
```

### 4. VALIDATE
**Ensure all code is safe and correct**

Every generated or composed workflow goes through:
- **Ruff** - Python linting and style checking
- **Mypy** - Type checking for type safety
- **Import smoke test** - Verify module can be imported
- **Dry run** - Sandbox execution to catch runtime errors

All validation happens automatically before user approval.

### 5. MCP TOOLS
**Script analysis, formatting, documentation, and API search**

Formal MCP (Model Context Protocol) tools for code operations:
- Read and analyze Python scripts
- Generate comprehensive documentation
- Auto-format code with black/isort/autoflake
- Scan directory structures and dependencies
- Search Aimsun and QGIS API documentation

See [MCP Tools](#mcp-tools-reference) section below.

### 6. LOGGING
**Complete action history for reproducibility**

- All MCP tool actions logged with timestamps
- File hashes tracked before/after operations
- Session-based logs for audit trails
- Query by file, session, or action ID
- Export session reports in Markdown

**Log locations:**
- `logs/mcp/mcp_YYYY-MM-DD.jsonl` - Daily logs
- `logs/mcp/sessions/session_YYYYMMDD_HHMMSS.jsonl` - Per session
- `logs/mcp/actions/{action_id}.json` - Individual actions

---

## 🛠️ MCP Tools Reference

### Script Analysis & Documentation

#### `mcp_read_script`
**Read and analyze Python scripts with AST parsing**

- Extracts functions, classes, imports, docstrings
- Analyzes module structure and metadata
- Provides line numbers for all definitions
- Clickable links in terminal output

**Usage:**
```
> @C:\path\to\script.py
> @path/to/script.py
```

**Returns:**
- File content
- AST analysis (functions, classes, imports)
- Module metadata (__domain__, __action__)
- Summary statistics

---

#### `mcp_write_md`
**Generate comprehensive Markdown documentation**

- Creates detailed .md file next to Python script
- Includes overview, features, API reference
- Shows usage examples and implementation details
- LLM-generated content with fallback

**Usage:**
```
> generate docs
> create docs
> make docs
```

**Generates:** `script.md` with full documentation

---

#### `mcp_add_comments`
**Generate docstrings for all functions**

- Google-style docstring format
- Includes Args, Returns, Raises sections
- Analyzes function signatures and code
- LLM-generated with context awareness

**Usage:**
```
> comment functions
> add comments
> add docstrings
```

**Returns:** Formatted docstrings ready to copy

---

### Code Formatting & Structure

#### `mcp_format_script`
**Auto-format with black, isort, and autoflake**

Three-stage formatting pipeline:
1. **Autoflake** - Remove unused imports and variables
2. **Isort** - Sort imports (black-compatible profile)
3. **Black** - Apply PEP 8 formatting

**Usage:**
```python
from agents.shared.tools import mcp_format_script

# Format a script
mcp_format_script.invoke({"path": "script.py"})

# Check only (dry run)
mcp_format_script.invoke({"path": "script.py", "check_only": True})
```

**Parameters:**
- `path` (str) - Path to Python script
- `check_only` (bool) - If True, preview changes without modifying

**Returns:**
```json
{
  "success": true,
  "formatted": true,
  "changes": [
    "Removed unused imports and variables",
    "Sorted imports",
    "Applied black formatting"
  ],
  "message": "Formatted: 3 changes"
}
```

---

#### `mcp_scan_structure`
**Scan directory and build dependency map**

- Recursive directory tree scanning
- Per-file import dependency analysis
- Configurable include/exclude patterns
- Comprehensive statistics

**Usage:**
```python
from agents.shared.tools import mcp_scan_structure

# Scan a directory
mcp_scan_structure.invoke({"base_dir": "agents/pulsus"})

# Custom patterns
mcp_scan_structure.invoke({
    "base_dir": "agents",
    "include_patterns": ["*.py"],
    "exclude_patterns": ["tests", "__pycache__", ".git"]
})
```

**Parameters:**
- `base_dir` (str) - Base directory to scan
- `include_patterns` (list) - Glob patterns to include (default: ['*.py'])
- `exclude_patterns` (list) - Patterns to exclude (default: ['__pycache__', '*.pyc', '.git', 'venv'])

**Returns:**
```json
{
  "success": true,
  "structure": {
    "name": "pulsus",
    "type": "directory",
    "children": [...]
  },
  "dependency_map": {
    "routing/router.py": {
      "imports": [...],
      "num_imports": 15,
      "lines": 84
    }
  },
  "statistics": {
    "total_files": 45,
    "total_directories": 12,
    "total_lines": 3521,
    "total_imports": 234,
    "top_imports": [
      {"module": "pathlib", "count": 28},
      {"module": "json", "count": 15}
    ]
  }
}
```

---

### API Documentation Search

#### `search_aimsun_docs`
**Search Aimsun Next API documentation**

- Search for classes, methods, or keywords
- Context and code examples included
- Ranked results by relevance

**Usage:**
```python
search_aimsun_docs.invoke({"query": "GKSection", "max_results": 5})
```

**Example queries:**
- "GKSection" - Find GKSection class
- "getSpeed" - Find speed-related methods
- "vehicle attributes" - Find vehicle APIs

---

#### `search_qgis_docs`
**Search QGIS (PyQGIS) API documentation**

- Search for QGIS classes and methods
- Usage examples and context
- Ranked results

**Usage:**
```python
search_qgis_docs.invoke({"query": "QgsVectorLayer", "max_results": 5})
```

**Example queries:**
- "QgsVectorLayer" - Find layer class
- "addFeature" - Find feature methods
- "export CSV" - Find export functions

---

### Code Execution

#### `validate_python_code`
**Validate code safety before execution**

- AST-based security validation
- Blocks dangerous modules (os, sys, subprocess)
- Blocks dangerous builtins (eval, exec, compile)
- Returns security issues found

**Usage:**
```python
validate_python_code.invoke({"code": "import requests\nprint('hello')"})
```

---

#### `execute_safe_python`
**Execute code in sandboxed environment**

- Runs in restricted environment
- Enforces timeout (max 30 seconds)
- Captures stdout/stderr
- Returns execution results

**Usage:**
```python
execute_safe_python.invoke({
    "code": "result = 2 + 2\nprint(result)",
    "timeout": 10
})
```

**Security:**
- Blocks dangerous modules
- Blocks dangerous builtins
- Enforces timeout
- AST validation before execution

---

## 💬 Built-in Interactive Commands

### `list tools`
Display all available MCP tools categorized by function.

**Aliases:** `show tools`, `tools`, `features`, `list features`

**Output:**
- Script Analysis & Documentation tools
- Code Formatting & Structure tools
- API Documentation Search tools
- Code Execution tools

---

### `examples`
Show quick start examples for common tasks.

**Aliases:** `show examples`, `quick start`

**Output:**
- Script analysis examples
- Code formatting examples
- API documentation examples
- Workflow execution examples

---

### `@path/to/script.py`
Analyze a Python script (shorthand for `mcp_read_script`).

**Features:**
- Full AST analysis
- Function and class extraction
- Import dependency listing
- Metadata extraction

---

### `generate docs`
Generate documentation for current script in context.

**Aliases:** `create docs`, `make docs`, `write docs`

**Requires:** Script must be analyzed first with `@path`

---

### `comment functions`
Generate docstrings for all functions in current script.

**Aliases:** `add comments`, `add docstrings`, `document functions`

**Requires:** Script must be analyzed first with `@path`

---

## 🚀 Quick Start Examples

### Script Analysis
```bash
# Analyze a Python script
> @C:\Users\name\project\script.py

# Generate documentation
> generate docs

# Add function comments
> comment functions
```

### Code Formatting
```bash
# Auto-format a script
> format script.py

# Check formatting without changes
> format script.py check_only
```

### Directory Structure
```bash
# Scan project structure
> scan structure agents/pulsus

# Custom scan with patterns
> scan agents/ include:*.py exclude:tests,__pycache__
```

### API Documentation
```bash
# Search Aimsun API
> search Aimsun docs for GKSection

# Search QGIS API
> search QGIS docs for QgsVectorLayer
```

### Workflow Execution
```bash
# Discover and run existing tools
> Summarize the data matrix

# Compose multi-step workflow
> Load CSV and plot statistics

# Generate new solution
> Export selection to GeoJSON with custom attributes
```

---

## 📊 Session Flow

### 1. Startup Sequence

```
┌─────────────────────────────────────┐
│  Pulsus Initialization              │
├─────────────────────────────────────┤
│  1. LLM Introduction                │
│     (warm greeting with             │
│      capabilities overview)         │
│                                     │
│  2. CAPABILITIES Display            │
│     - DISCOVER                      │
│     - COMPOSE                       │
│     - GENERATE                      │
│     - VALIDATE                      │
│     - MCP TOOLS                     │
│     - LOGGING                       │
│                                     │
│  3. Framework Tools Discovery       │
│     (scan workflow directory)       │
│                                     │
│  4. Ready for input                 │
└─────────────────────────────────────┘
```

### 2. Request Processing

```
User Input
    ↓
Built-in Command? → Yes → Execute command
    ↓ No
File Analysis (@path)? → Yes → mcp_read_script
    ↓ No
Generate Docs? → Yes → mcp_write_md
    ↓ No
Comment Functions? → Yes → mcp_add_comments
    ↓ No
Follow-up Question? → Yes → Handle with context
    ↓ No
Normal Routing
    ↓
┌─────────────────┐
│  Parse Intent   │
│  (domain,       │
│   action)       │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Discover Tools │
│  (score,        │
│   rank)         │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Choose Policy  │
│  - select       │
│  - compose      │
│  - generate     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Validate       │
│  - ruff         │
│  - mypy         │
│  - import       │
│  - dry run      │
└────────┬────────┘
         ↓
┌─────────────────┐
│  User Approval  │
└────────┬────────┘
         ↓
     Execute
```

---

## 🔧 Configuration

### Command-line Arguments

```bash
# Normal startup
python -m agents.pulsus

# Quiet mode (no greeting)
python -m agents.pulsus --quiet

# Static greeting (no LLM)
python -m agents.pulsus --static-greeting

# Single query mode
python -m agents.pulsus "Load CSV and plot statistics" --non-interactive

# Show routing details
python -m agents.pulsus --explain

# Dry run (no execution)
python -m agents.pulsus --dry-run
```

### Settings File

Located at: `agents/pulsus/config/settings.yaml`

**Key settings:**
- `model.host` - Ollama host URL
- `model.name` - Model name (e.g., qwen2.5-coder:7b)
- `model.timeout` - Request timeout
- `ranker.threshold` - Tool scoring threshold
- `workflows_root` - Framework directory path

---

## 📁 Directory Structure

```
agents/pulsus/
├── config/
│   ├── settings.yaml           # Configuration
│   ├── session.py              # Session management
│   ├── llm_greeting.py         # LLM-powered greeting
│   └── features_display.py     # Features & tools display
├── console/
│   ├── interface.py            # Main CLI interface
│   ├── session_manager.py      # Session state
│   └── interrupt_handler.py    # ESC key handling
├── routing/
│   ├── router.py               # Main routing logic
│   ├── prompt_parser.py        # Intent parsing
│   └── tool_discovery.py       # Tool scanning
├── core/
│   ├── compose/                # Workflow composition
│   ├── validators/             # Code validation
│   ├── sandbox/                # Safe execution
│   └── telemetry/              # Logging
├── ui/
│   ├── display_manager.py      # Terminal output
│   └── README.md              # This file
└── workflows/
    └── tools/                  # MCP tools implementation

agents/mcp/
├── helpers/
│   ├── script_ops.py           # Core MCP operations
│   └── action_logger.py        # MCP action logging
└── test_structure_tools.py     # Tests

agents/shared/
└── tools.py                    # MCP tool bindings

logs/mcp/
├── mcp_YYYY-MM-DD.jsonl        # Daily logs
├── sessions/                   # Per-session logs
└── actions/                    # Individual action logs
```

---

## 🔒 Security

### Validation Pipeline

All generated and composed code goes through:

1. **Ruff** - Linting and style checking
2. **Mypy** - Type checking
3. **Import Test** - Verify module loads
4. **Dry Run** - Sandbox execution

### Code Execution Safety

- Restricted builtins (no eval, exec, compile)
- Blocked modules (os, sys, subprocess)
- Timeout enforcement (max 30 seconds)
- AST validation before execution

### User Approval

- All actions require explicit approval
- Routing decisions shown with reasoning
- Validation results displayed
- Option to interrupt with ESC key

---

## 🆘 Troubleshooting

### LLM Not Available
If Ollama is down, Pulsus falls back to static greeting but remains fully functional.

### Tools Not Found
Run `list tools` to see all available tools. Ensure MCP helpers are properly installed.

### Formatting Fails
Ensure black, isort, and autoflake are installed:
```bash
pip install black isort autoflake
```

### Validation Errors
Check the validation output for specific issues:
- Ruff: Style/linting problems
- Mypy: Type errors
- Import: Missing dependencies
- Dry run: Runtime errors

---

## 📚 Additional Resources

- **MCP TODO**: See `workflows/Pulsus-MCP-TODO.md` for implementation details
- **Tests**: Run `agents/mcp/test_structure_tools.py` for MCP tool tests
- **Logs**: Check `logs/mcp/` for action history

---

## 📝 Version History

### Current Version
- ✅ Phase 1: MCP Migration (read, write, comment tools)
- ✅ MCP Action Logging System
- ✅ Routing Fix (no longer blocks MCP operations)
- ✅ Phase 2: Code Structure Tools (format, scan)
- ✅ Initialization Features Display
- 🟡 Phase 3: Metadata System (planned)
- 🟡 Phase 4: Incremental Documentation (planned)
- 🟡 Phase 5: Search & Indexing (planned)

---

**Pulsus** - Intelligent Workflow Routing for Atlantis Framework
