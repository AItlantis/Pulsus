# 🧭 Pulsus MCP Migration & Script Intelligence TODO

**Goal:**  
Transform current text-triggered LLM functions (read/write/comment) into formal **MCP tools**, then extend MCP to support **script organization, metadata management, documentation, and optimization**.

---

## 🔴 Phase 1 — MCP Migration ✅ COMPLETED

**Objective:** Convert the existing keyword-triggered functions into formal MCP tools.

### ✅ Existing functions
- `read_script()` → currently triggered by phrases like "read" or "open"
- `write_md()` → generates Markdown documentation
- `add_comments()` → inserts docstrings or inline comments

### 🔧 Actions
- [x] Create `agents/mcp/helpers/script_ops.py` for core functions:
  - `mcp_read_script(path: str)`
  - `mcp_write_md(path: str, content: str)`
  - `mcp_add_comments(path: str, strategy="docstring")`
- [x] Add input validation and SafeNet path checks
- [x] Bind these helpers as LangChain tools in `shared/tools.py`
- [x] Update Pulsus routing to call MCP tools instead of string triggers
- [x] Log all MCP actions (for reproducibility and rollback) ✅ COMPLETED
- [x] Fix routing logic to prevent blocking MCP file reads when script in context

### 📁 Created Files
- `agents/mcp/__init__.py` - MCP module initialization
- `agents/mcp/helpers/__init__.py` - MCP helpers module
- `agents/mcp/helpers/script_ops.py` - Core script operations with all MCP functions:
  - `read_script()` - Read and analyze scripts
  - `write_md()` - Generate documentation
  - `add_comments()` - Generate docstrings
  - `format_script()` - Auto-format code (black, isort, autoflake) ✨ NEW
  - `scan_structure()` - Directory scanning and dependency mapping ✨ NEW
- `agents/mcp/helpers/action_logger.py` - MCP action logging system for reproducibility and rollback
- `agents/mcp/test_script_ops.py` - Test suite for core MCP tools
- `agents/mcp/test_structure_tools.py` - Test suite for format_script and scan_structure ✨ NEW
- Updated `agents/shared/tools.py` - Added all MCP tool bindings including new structure tools
- Updated `agents/pulsus/console/interface.py` - Fixed routing logic to prevent blocking MCP calls

### ✅ Test Results
All MCP tools tested and working:
- `mcp_read_script()` - Successfully reads and analyzes Python scripts
- `mcp_write_md()` - Generates comprehensive Markdown documentation
- `mcp_add_comments()` - Creates docstrings for all functions

See: `agents/mcp/test_script_ops.py` for test examples

### 🔗 Routing Integration
Updated `agents/pulsus/console/interface.py` to route text triggers to MCP tools:

**Text Triggers → MCP Tools:**
- `@path` → `mcp_read_script()` (file analysis)
- `"generate docs"`, `"create docs"`, etc. → `mcp_write_md()`
- `"comment functions"`, `"add comments"`, etc. → `mcp_add_comments()`

**Routing Priority:**
1. File analysis (@path syntax) - highest priority
2. Generate docs text triggers
3. Comment functions text triggers
4. Follow-up questions (if script in context)
5. Normal Pulsus routing (fallback)

**Integration Test:** `agents/mcp/test_routing_integration.py` - All tests passing ✅

### 📊 MCP Action Logging System

**Location**: `agents/mcp/helpers/action_logger.py`

**Features:**
- ✅ Logs all MCP tool calls with parameters and results
- ✅ Tracks file state before/after operations (SHA-256 hashes)
- ✅ Records timestamps and unique action IDs
- ✅ Stores logs in multiple formats:
  - Daily logs: `logs/mcp/mcp_YYYY-MM-DD.jsonl`
  - Session logs: `logs/mcp/sessions/session_YYYYMMDD_HHMMSS.jsonl`
  - Individual action files: `logs/mcp/actions/{action_id}.json`
- ✅ Query capabilities:
  - Get all actions for a specific file
  - Get all actions from current session
  - Get recent actions (last N)
  - Retrieve specific action by ID
- ✅ File integrity verification (compare current hash vs. logged hash)
- ✅ Export session reports in Markdown format

**Integrated Tools:**
- `mcp_read_script()` - Logs read operations with file analysis summary
- `mcp_write_md()` - Logs documentation generation with file hashes
- `mcp_add_comments()` - Logs comment generation with function names

**Usage Example:**
```python
from agents.mcp.helpers.action_logger import get_mcp_logger

# Get logger instance
logger = get_mcp_logger()

# Get all actions for a file
actions = logger.get_actions_for_file("path/to/script.py")

# Verify file integrity
verification = logger.verify_file_integrity(action_id, "path/to/file.md")

# Export session report
report_path = logger.export_session_report()
```

### 🔧 Routing Fix

**Problem:** The routing logic in `interface.py` was treating ALL user inputs as follow-up questions when a script was in the session history, blocking MCP file reading and other operations.

**Solution:** Added intelligent `_is_followup_question()` function that distinguishes between:
- **Follow-up questions**: "What does this function do?", "How does it work?"
- **New actions**: "read file.py", "analyze script.py", "@path/to/file.py"

**Changes in** `agents/pulsus/console/interface.py`:
- Line 281-320: New `_is_followup_question()` helper function
- Line 402: Updated routing condition to check if input is actually a follow-up question
- Now allows MCP tools to be called even when script is in context

---

## 🟠 Phase 2 — Standardize Code Structure ✅ COMPLETED

**Objective:** Make all scripts easy for LLMs to understand and reuse.

### 🔧 New MCP functions
- [x] `mcp_format_script(path: str, check_only: bool = False)` ✅ COMPLETED
  → Auto-format and normalize indentation, imports, and naming conventions using black, isort, and autoflake.
- [x] `mcp_scan_structure(base_dir: str, include_patterns, exclude_patterns)` ✅ COMPLETED
  → Return a structural map of scripts and folders with dependency mapping.

### ✨ Implementation Details

#### `mcp_format_script()`
**Location**: `agents/mcp/helpers/script_ops.py:844-951`

**Features:**
- Three-stage formatting pipeline:
  1. **Autoflake** - Removes unused imports and variables
  2. **Isort** - Sorts imports (black-compatible profile)
  3. **Black** - Applies PEP 8 formatting
- `check_only` mode for previewing changes
- Detailed change tracking
- Full MCP action logging with file hashes

**Usage:**
```python
from agents.shared.tools import mcp_format_script

# Format a script
result = mcp_format_script.invoke({"path": "path/to/script.py"})

# Check formatting without changes
result = mcp_format_script.invoke({"path": "path/to/script.py", "check_only": True})
```

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

#### `mcp_scan_structure()`
**Location**: `agents/mcp/helpers/script_ops.py:1085-1394`

**Features:**
- Recursive directory tree scanning
- Import dependency analysis per file
- Configurable include/exclude patterns
- Comprehensive statistics:
  - Total files, directories, lines of code
  - Total imports across all files
  - Top 10 most imported modules
  - Files with parsing errors
- Full MCP action logging

**Usage:**
```python
from agents.shared.tools import mcp_scan_structure

# Scan a directory
result = mcp_scan_structure.invoke({"base_dir": "agents/pulsus"})

# Custom patterns
result = mcp_scan_structure.invoke({
    "base_dir": "agents",
    "include_patterns": ["*.py"],
    "exclude_patterns": ["tests", "__pycache__", ".git"]
})
```

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
      "path": "...",
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

### 📁 New Files
- `agents/mcp/test_structure_tools.py` - Test suite for format_script and scan_structure

### 📘 Implementation Notes
- Use AST parsing to enforce a consistent function/class layout.
- Store formatting rules in `/config/code_style.json`.

---

## 🎯 Initialization Features ✅ COMPLETED

**Objective:** Auto-display Pulsus capabilities and available tools during startup.

### ✨ Features Display System

**Location**: `agents/pulsus/config/features_display.py`

**Features:**
- Compact features overview displayed at startup
- Full categorized tool list (via `list tools` command)
- Quick start examples (via `examples` command)
- LLM-enhanced greeting with embedded capabilities

**New Components:**

1. **`display_features_compact()`** - Shows core capabilities:
   - DISCOVER - Scan and score existing tools
   - COMPOSE - Plan multi-step workflows
   - GENERATE - Create AI-powered solutions
   - VALIDATE - Lint, type-check, sandbox code
   - MCP TOOLS - Script operations and API search
   - LOGGING - Complete action history

2. **`display_tools_full()`** - Shows all MCP tools by category:
   - Script Analysis & Documentation (3 tools)
   - Code Formatting & Structure (2 tools)
   - API Documentation Search (2 tools)
   - Code Execution (2 tools)

3. **`display_quick_start_examples()`** - Shows example commands by category

**Built-in Commands:**
- `list tools` / `tools` / `features` - Display all available MCP tools
- `examples` / `quick start` - Show example commands

**Integration:**
- Auto-displayed after LLM greeting in `interface.py:48`
- LLM greeting enhanced with full feature list (`llm_greeting.py:145`)
- Commands accessible via interactive prompt

**Usage:**
```bash
# Start Pulsus (auto-displays features)
python -m agents.pulsus

# List all tools interactively
> list tools

# Show examples
> examples
```

### 🔧 Files Modified
- `agents/pulsus/config/llm_greeting.py` - Enhanced LLM prompt with features
- `agents/pulsus/console/interface.py` - Added features display and built-in commands
- New: `agents/pulsus/config/features_display.py` - Complete features display system

---

## 🟡 Phase 3 — Metadata System

**Objective:** Automatically generate and maintain metadata for each script.

### 🔧 New MCP functions
- [ ] `mcp_generate_metadata(path: str)`  
  → Extract function names, inputs, outputs, and docstrings.
- [ ] `mcp_update_metadata(path: str, metadata: dict)`  
  → Allow manual or LLM-assisted updates.
- [ ] `mcp_list_metadata(filter: str = None)`  
  → Query available scripts by tags or domains.

### 🗂️ Output
Each script should have a companion `.meta.json` file, for example:
```json
{
  "name": "import_traffic_data",
  "purpose": "Load and preprocess Aimsun traffic data",
  "inputs": ["file_path", "network_id"],
  "outputs": ["DataFrame"],
  "dependencies": ["qgis_utils", "aimsun_api"],
  "last_updated": "2025-11-01"
}
```

---

## 🟢 Phase 4 — Incremental Documentation

**Objective:** Let the LLM document scripts in small, validated batches.

### 🔧 New MCP functions
- [ ] `mcp_document_batch(paths: List[str])`  
  → Generates Markdown docs for a batch of scripts.
- [ ] `mcp_validate_docs(path: str)`  
  → Compares function docstrings with actual code behavior.
- [ ] `mcp_sync_docs()`  
  → Sync documentation with metadata and ensure consistency.

### 🧩 Integration
- Schedule periodic MCP calls for doc updates.
- Allow Shell agent to validate docs after Pulse generation.

---

## 🔵 Phase 5 — Search & Indexing Mechanism

**Objective:** Let the agent instantly find and reuse existing scripts with minimal token use.

### 🔧 New MCP functions
- [ ] `mcp_index_scripts(base_dir: str)`  
  → Build a vector or keyword index for all available functions.
- [ ] `mcp_search_scripts(query: str)`  
  → Return best matches with context and metadata.
- [ ] `mcp_fetch_dependencies(script_name: str)`  
  → Retrieve dependency graph.

### 🧠 Expected Output
Enable queries like:
> “Find all scripts that modify a selection layer”  
> → MCP returns `selection_tools.py`, `layer_editor.py`, etc.

---

## 🟣 Phase 6 — Iterative Improvement

**Objective:** Continuously refine performance, organization, and efficiency.

### 🔧 New MCP functions
- [ ] `mcp_analyze_efficiency(path: str)`  
  → Identify redundant imports, unused code, or complexity hotspots.
- [ ] `mcp_optimize_script(path: str)`  
  → Suggest or apply safe refactors.
- [ ] `mcp_review_usage(logs: str)`  
  → Learn which scripts are most used and suggest caching or optimization.

### 🧩 Continuous Feedback Loop
- Compass supervises which MCP calls succeed/fail.
- Pulse adapts to improved metadata.
- Shell validates documentation and optimization suggestions.

---

## 🧠 Outcome

By completing these steps, your system will:
- Move from **ad-hoc command triggers** → to **formal MCP-controlled actions**
- Gain **structured metadata and documentation** for all scripts
- Support **efficient LLM-driven discovery and optimization**
- Enable **safe, auditable, and incremental improvement** over time

---

## 📦 Directory Plan

```
agents/
├── mcp/
│   ├── helpers/
│   │   ├── script_ops.py         # read/write/comment helpers
│   │   ├── structure_ops.py      # format and scan structure
│   │   ├── metadata_ops.py       # metadata management
│   │   ├── doc_ops.py            # batch documentation tools
│   │   ├── index_ops.py          # indexing and search
│   │   └── optimize_ops.py       # performance and refactoring
│   └── command_router.py         # interprets MCP calls
├── shared/
│   ├── tools.py                  # binds all MCP tools
│   └── settings.py
└── pulse_agent.py
```
