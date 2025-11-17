# Pulsus Workflows - Creating Tools and Features

This guide explains how to create and integrate new tools and features into the Pulsus agent.

## Table of Contents

1. [Overview](#overview)
2. [Tool Structure](#tool-structure)
3. [Creating a New Tool](#creating-a-new-tool)
4. [Tool Discovery System](#tool-discovery-system)
5. [Best Practices](#best-practices)
6. [Built-in MCP Tools](#built-in-mcp-tools)
   - [MCP Script Operations](#mcp-script-operations)
   - [MCP API Documentation Search](#mcp-api-documentation-search)
   - [MCP Code Execution](#mcp-code-execution)
   - [MCP Action Logging](#mcp-action-logging)
   - [MCP Workflow Example](#mcp-workflow-example)
7. [Built-in Analysis Tools](#built-in-analysis-tools)
8. [Examples](#examples)
9. [Testing](#testing)

---

## Overview

Pulsus uses a **discoverable tool system** where tools are Python modules that follow specific conventions. The agent automatically discovers and routes user requests to appropriate tools based on metadata and documentation.

### Key Concepts

- **Domain**: Broad category of functionality (e.g., "analysis", "discovery", "ingestion")
- **Action**: Specific operation within a domain (e.g., "analyze_file", "scan_framework")
- **Tool Discovery**: Automatic scanning and scoring of tools based on user intent
- **Handle Function**: Standard entry point that all tools must implement

---

## Tool Structure

Every Pulsus tool follows this basic structure:

```python
"""
Tool Name

Brief description of what this tool does.
More detailed explanation can go here.
"""

from typing import Dict, Any
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.interrupt_handler import get_interrupt_handler

# Required metadata for tool discovery
__domain__ = "your_domain"      # e.g., "analysis", "discovery", "chat"
__action__ = "your_action"      # e.g., "analyze_file", "greet", "scan"


def handle(text: str = "") -> Dict[str, Any]:
    """
    Main entry point for the tool.

    Args:
        text: User input text or query

    Returns:
        Dictionary with status, results, and message:
        {
            "status": "success" | "error" | "interrupted",
            "message": "Description of result",
            # ... additional result data
        }
    """
    # Optional: Add interrupt support for long operations
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        ui.info(f"Running {__action__}...")

        # Your tool logic here
        result = do_work(text)

        return {
            "status": "success",
            "message": f"Completed {__action__}",
            "result": result
        }

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {
            "status": "interrupted",
            "message": "Operation interrupted by user"
        }
    except Exception as e:
        ui.error(f"Error in {__action__}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        interrupt_handler.stop_listening()


def do_work(text: str):
    """Helper function for your tool's core logic."""
    # Implementation here
    pass


if __name__ == "__main__":
    # Optional: Test code for standalone execution
    print(f"Testing {__action__}...")
    result = handle("test input")
    print(f"Result: {result}")
```

---

## Creating a New Tool

### Step 1: Choose Location

Place your tool in the appropriate subdirectory under `workflows/tools/`:

```
workflows/
├── tools/
│   ├── analyze/          # Analysis tools
│   ├── discover/         # Discovery tools
│   ├── ingestion/        # Data ingestion tools
│   ├── chat/             # Conversational tools
│   └── your_domain/      # Create new domain if needed
```

### Step 2: Define Metadata

Choose appropriate domain and action identifiers:

```python
__domain__ = "analysis"          # Broad category
__action__ = "validate_schema"   # Specific action
```

**Common Domains:**
- `analysis` - Code/data analysis tools
- `discovery` - Finding and scanning tools
- `ingestion` - Data loading and parsing
- `chat` - Conversational/greeting tools
- `visualization` - Plotting and display tools

### Step 3: Write Module Docstring

The docstring is crucial for tool discovery:

```python
"""
Schema Validator Tool

Validates data against a JSON schema and reports errors.
Supports nested schemas, custom formats, and validation rules.

Keywords: validate, schema, json, check, verify
"""
```

**Tips:**
- First line: Clear, concise tool name
- Second paragraph: Detailed description
- Include relevant keywords for better discovery
- Mention supported formats, inputs, or use cases

### Step 4: Implement handle() Function

The `handle()` function is the required entry point:

```python
def handle(text: str = "") -> Dict[str, Any]:
    """
    Entry point called by Pulsus router.

    Args:
        text: User's input query or command

    Returns:
        Dictionary with at minimum:
        - status: "success", "error", or "interrupted"
        - message: Human-readable result description
    """
    # Parse user input
    params = parse_input(text)

    # Execute tool logic
    result = execute_validation(params)

    # Return standardized response
    return {
        "status": "success",
        "message": "Schema validation complete",
        "errors": result.errors,
        "valid": result.is_valid
    }
```

### Step 5: Add Interrupt Support (Optional but Recommended)

For long-running operations:

```python
from agents.pulsus.console.interrupt_handler import get_interrupt_handler

def handle(text: str = "") -> Dict[str, Any]:
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        ui.info("Press ESC to interrupt...")

        for item in large_dataset:
            # Check periodically
            if interrupt_handler.is_interrupted():
                raise InterruptedError("Validation interrupted by user (ESC)")

            validate_item(item)

        return {"status": "success", "message": "Validation complete"}

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {"status": "interrupted", "message": str(e)}
    finally:
        interrupt_handler.stop_listening()
```

### Step 6: Use UI Display Manager

Use consistent UI messaging:

```python
from agents.pulsus.ui import display_manager as ui

# Info messages
ui.info("Starting validation...")

# Success messages
ui.success("Validation passed!")

# Warnings
ui.warn("Found 3 warnings")

# Errors
ui.error("Validation failed")

# Key-value display
ui.kv("Schema", "user_profile.json")
ui.kv("Valid", "True")

# Sections
ui.section("Validation Results")
```

---

## Tool Discovery System

### How Discovery Works

1. **User Input Parsing**: User query is parsed for domain and action hints
   ```
   "analyze the CSV file" → domain: analysis, action: analyze
   ```

2. **Tool Scanning**: Pulsus scans `workflows/tools/` for matching tools
   - Checks `__domain__` and `__action__` metadata
   - Searches module docstrings for keywords
   - Calculates relevance scores

3. **Scoring System**:
   - Exact domain match: +0.5
   - Exact action match: +0.5
   - Domain in docstring: +0.5
   - Action in docstring: +0.5
   - Maximum score: 1.0

4. **Policy Selection**:
   - **SELECT**: Single best tool (score ≥ threshold)
   - **COMPOSE**: Multiple tools chained together
   - **GENERATE**: No match, LLM generates solution

### Improving Discoverability

**1. Use Clear Metadata:**
```python
__domain__ = "analysis"       # Matches "analyze", "analysis"
__action__ = "parse_csv"      # Matches "parse", "csv"
```

**2. Rich Docstrings:**
```python
"""
CSV Parser and Analyzer

Parses CSV files and performs statistical analysis.
Handles various delimiters, encodings, and malformed data.

Use cases:
- Load CSV for data analysis
- Parse tabular data
- Import spreadsheet files
- Analyze comma-separated values

Keywords: csv, parse, load, import, spreadsheet, tabular, delimited
"""
```

**3. Semantic Variations:**

Include synonyms and variations in your docstring:
- "parse" → parsing, parser, load, import, read
- "analyze" → analysis, examine, inspect, review
- "validate" → validation, check, verify, test

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def handle(text: str = "") -> Dict[str, Any]:
    try:
        result = risky_operation(text)
        return {"status": "success", "result": result}
    except FileNotFoundError as e:
        ui.error(f"File not found: {e}")
        return {"status": "error", "message": f"File not found: {e}"}
    except Exception as e:
        ui.error(f"Unexpected error: {e}")
        return {"status": "error", "message": str(e)}
```

### 2. Input Validation

Validate user input early:

```python
def handle(text: str = "") -> Dict[str, Any]:
    if not text or not text.strip():
        ui.warn("No input provided")
        return {"status": "error", "message": "Input required"}

    # Parse and validate
    params = parse_input(text)
    if not params.is_valid:
        return {"status": "error", "message": params.error}
```

### 3. Progress Feedback

For long operations, provide feedback:

```python
def handle(text: str = "") -> Dict[str, Any]:
    items = load_items()
    total = len(items)

    for i, item in enumerate(items, 1):
        ui.info(f"Processing {i}/{total}...")
        process_item(item)
```

### 4. Return Structured Data

Return consistent, structured results:

```python
return {
    "status": "success",           # Required
    "message": "Processed 100 items",  # Required
    "items_processed": 100,        # Additional data
    "errors": [],                  # Additional data
    "output_file": "/path/to/result.csv"  # Additional data
}
```

### 5. Logging and Telemetry

Use the logger for debugging:

```python
from agents.pulsus.core.telemetry.logging import get_logger

def handle(text: str = "") -> Dict[str, Any]:
    logger = get_logger("my_tool")
    logger.event("tool_start", {"input_length": len(text)})

    result = do_work(text)

    logger.event("tool_complete", {"result_size": len(result)})
    return {"status": "success", "result": result}
```

### 6. Settings and Configuration

Use the settings system:

```python
from agents.pulsus.config.settings import load_settings

def handle(text: str = "") -> Dict[str, Any]:
    settings = load_settings()

    # Access framework root
    framework_root = settings.framework_root

    # Access model settings
    model_name = settings.model.name
    model_host = settings.model.host
```

---

## Built-in MCP Tools

Pulsus includes a complete set of **MCP (Model Context Protocol) tools** for script operations, code formatting, and API documentation search. These are formal, logged tools with full action history tracking.

### MCP vs. Standard Tools

**MCP Tools:**
- Formal tool protocol with standardized interfaces
- All actions logged for reproducibility and rollback
- File hash tracking for write operations
- JSON-based responses
- Available through `agents.shared.tools`
- Used via LangChain tool invocation

**Standard Workflow Tools:**
- Discoverable Python modules
- Domain/action metadata
- Handle function interface
- Located in `workflows/tools/`

---

### MCP Script Operations

#### mcp_read_script
**Read and analyze Python scripts with AST parsing**

```python
from agents.shared.tools import mcp_read_script

result = mcp_read_script.invoke({"path": "path/to/script.py"})
```

**Features:**
- Full AST analysis (functions, classes, imports)
- Module metadata extraction
- Line numbers for all definitions
- Integration with session context

**Usage in Pulsus:**
```
> @C:\path\to\script.py
> @path/to/script.py
```

**Returns:**
```json
{
  "success": true,
  "file_path": "path/to/script.py",
  "ast_analysis": {
    "functions": [...],
    "classes": [...],
    "imports": [...],
    "module_docstring": "..."
  },
  "metadata": {
    "domain": "analysis",
    "action": "analyze_file"
  }
}
```

**Logged:** All read operations logged with file analysis summary

---

#### mcp_write_md
**Generate comprehensive Markdown documentation**

```python
from agents.shared.tools import mcp_write_md

result = mcp_write_md.invoke({"path": "path/to/script.py"})
```

**Features:**
- LLM-generated comprehensive documentation
- Overview, features, API reference sections
- Usage examples and implementation details
- Fallback to AST-based docs if LLM unavailable

**Usage in Pulsus:**
```
> generate docs
> create docs
> make docs
```

**Returns:**
```json
{
  "success": true,
  "doc_path": "path/to/script.md",
  "message": "Documentation created: script.md"
}
```

**Logged:** Document generation with file hashes before/after

---

#### mcp_add_comments
**Generate docstrings for all functions**

```python
from agents.shared.tools import mcp_add_comments

result = mcp_add_comments.invoke({
    "path": "path/to/script.py",
    "strategy": "docstring"
})
```

**Features:**
- Google-style docstring format
- Args, Returns, Raises sections
- Context-aware LLM generation
- Per-function analysis

**Usage in Pulsus:**
```
> comment functions
> add comments
> add docstrings
```

**Returns:**
```json
{
  "success": true,
  "functions_commented": 5,
  "comments": [
    {
      "function": "parse_data",
      "line": 42,
      "comment": "...",
      "formatted": "\"\"\"...\"\"\""
    }
  ]
}
```

**Logged:** Comment generation with function names tracked

---

#### mcp_format_script
**Auto-format with black, isort, and autoflake**

```python
from agents.shared.tools import mcp_format_script

# Format a script
result = mcp_format_script.invoke({"path": "script.py"})

# Check only (dry run)
result = mcp_format_script.invoke({
    "path": "script.py",
    "check_only": True
})
```

**Features:**
- Three-stage formatting pipeline:
  1. **Autoflake** - Remove unused imports/variables
  2. **Isort** - Sort imports (black-compatible)
  3. **Black** - Apply PEP 8 formatting
- Check-only mode for previewing changes
- Detailed change tracking

**Usage in Pulsus:**
```
> format script.py
> format script.py check_only
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

**Logged:** Formatting operations with file hashes

**Requirements:**
```bash
pip install black isort autoflake
```

---

#### mcp_scan_structure
**Scan directory and build dependency map**

```python
from agents.shared.tools import mcp_scan_structure

# Scan a directory
result = mcp_scan_structure.invoke({"base_dir": "agents/pulsus"})

# Custom patterns
result = mcp_scan_structure.invoke({
    "base_dir": "agents",
    "include_patterns": ["*.py"],
    "exclude_patterns": ["tests", "__pycache__"]
})
```

**Features:**
- Recursive directory tree scanning
- Per-file import dependency analysis
- Configurable include/exclude patterns
- Comprehensive statistics:
  - Total files, directories, lines
  - Total imports across codebase
  - Top 10 most imported modules
  - Files with parsing errors

**Usage in Pulsus:**
```
> scan structure agents/pulsus
> scan agents/ include:*.py exclude:tests
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
      {"module": "pathlib", "count": 28}
    ]
  }
}
```

**Logged:** Structure scan with summary statistics

---

### MCP API Documentation Search

#### search_aimsun_docs
**Search Aimsun Next API documentation**

```python
from agents.shared.tools import search_aimsun_docs

result = search_aimsun_docs.invoke({
    "query": "GKSection",
    "max_results": 5
})
```

**Features:**
- Search classes, methods, keywords
- Context and code examples
- Ranked results by relevance

**Example queries:**
- "GKSection" - Find GKSection class
- "getSpeed" - Find speed methods
- "vehicle attributes" - Find vehicle APIs

---

#### search_qgis_docs
**Search QGIS (PyQGIS) API documentation**

```python
from agents.shared.tools import search_qgis_docs

result = search_qgis_docs.invoke({
    "query": "QgsVectorLayer",
    "max_results": 5
})
```

**Features:**
- Search QGIS classes and methods
- Usage examples and context
- Ranked results

**Example queries:**
- "QgsVectorLayer" - Find layer class
- "addFeature" - Find feature methods
- "export CSV" - Find export functions

---

### MCP Code Execution

#### validate_python_code
**Validate code safety before execution**

```python
from agents.shared.tools import validate_python_code

result = validate_python_code.invoke({
    "code": "import requests\nprint('hello')"
})
```

**Security checks:**
- AST-based validation
- Blocks dangerous modules
- Blocks dangerous builtins
- Returns security issues

---

#### execute_safe_python
**Execute code in sandboxed environment**

```python
from agents.shared.tools import execute_safe_python

result = execute_safe_python.invoke({
    "code": "result = 2 + 2\nprint(result)",
    "timeout": 10
})
```

**Security:**
- Restricted environment
- Timeout enforcement (max 30s)
- Stdout/stderr capture
- AST validation first

---

### MCP Action Logging

All MCP tool operations are automatically logged for reproducibility and rollback.

**Location:** `agents/mcp/helpers/action_logger.py`

**Features:**
- Timestamps and unique action IDs
- File hashes before/after operations
- Complete parameter and result tracking
- Query by file, session, or action ID

**Log files:**
```
logs/mcp/
├── mcp_YYYY-MM-DD.jsonl           # Daily logs
├── sessions/
│   └── session_YYYYMMDD_HHMMSS.jsonl  # Per session
└── actions/
    └── {action_id}.json            # Individual actions
```

**Query logs:**
```python
from agents.mcp.helpers.action_logger import get_mcp_logger

logger = get_mcp_logger()

# Get all actions for a file
actions = logger.get_actions_for_file("script.py")

# Get session actions
actions = logger.get_session_actions()

# Get recent actions
actions = logger.get_recent_actions(limit=20)

# Verify file integrity
result = logger.verify_file_integrity(action_id, "file.py")

# Export session report
report = logger.export_session_report()
```

---

### MCP Workflow Example

Complete workflow using MCP tools:

```python
from agents.shared.tools import (
    mcp_read_script,
    mcp_format_script,
    mcp_add_comments,
    mcp_write_md,
    mcp_scan_structure
)

# 1. Scan project structure
structure = mcp_scan_structure.invoke({"base_dir": "agents/pulsus"})
print(f"Found {structure['statistics']['total_files']} files")

# 2. Format a script
format_result = mcp_format_script.invoke({
    "path": "agents/pulsus/routing/router.py",
    "check_only": False
})
print(f"Formatting: {format_result['changes']}")

# 3. Analyze script
analysis = mcp_read_script.invoke({
    "path": "agents/pulsus/routing/router.py"
})
print(f"Found {len(analysis['ast_analysis']['functions'])} functions")

# 4. Add comments
comments = mcp_add_comments.invoke({
    "path": "agents/pulsus/routing/router.py"
})
print(f"Generated {comments['functions_commented']} docstrings")

# 5. Generate docs
docs = mcp_write_md.invoke({
    "path": "agents/pulsus/routing/router.py"
})
print(f"Created: {docs['doc_path']}")

# 6. Check action history
from agents.mcp.helpers.action_logger import get_mcp_logger
logger = get_mcp_logger()
recent = logger.get_recent_actions(limit=5)
for action in recent:
    print(f"{action.tool_name}: {action.operation} on {action.target_path}")
```

---

## Built-in Analysis Tools

Pulsus also comes with several built-in analysis tools that work alongside MCP tools. These tools are discoverable through the standard routing system.

### Function Commenter

**Domain:** `analysis` | **Action:** `comment_functions`

Generates detailed Google-style docstrings for each function in a Python script using LLM analysis.

**Usage:**
```
comment functions @path/to/file.py
```

**Features:**
- Analyzes function signatures, parameters, and return types
- Generates comprehensive docstrings with Args, Returns, and Raises sections
- Works with session context (no need to specify file if already analyzed)
- Displays formatted comments with clickable file paths
- Supports ESC key to interrupt long operations

**Example:**
```
# After analyzing a file
comment functions

# Or specify a file directly
comment functions @C:\project\utils.py
```

**Output:**
- Formatted docstrings for each function
- Line numbers with clickable links
- Preview of generated comments
- Suggestions for next steps

### Dependency Documenter

**Domain:** `analysis` | **Action:** `document_dependencies`

Identifies and documents local script dependencies with LLM-generated descriptions.

**Usage:**
```
analyze dependencies @path/to/file.py
document dependencies
```

**Features:**
- Extracts all import statements from Python files
- Distinguishes local project files from external libraries
- Resolves dependency paths automatically
- Generates descriptions of what each dependency does
- Analyzes dependency structure (functions, classes)
- Lists external dependencies separately

**Example:**
```
# After analyzing a file
analyze dependencies

# Or specify a file directly
document dependencies @C:\project\main.py
```

**Output:**
- List of local script dependencies with descriptions
- Clickable links to dependency files
- Key functions and classes in each dependency
- Separate list of external library dependencies

### File Analyzer

**Domain:** `analysis` | **Action:** `analyze_file`

Analyzes Python files and provides comprehensive structure analysis with LLM-powered understanding.

**Usage:**
```
analyze @path/to/file.py
@path/to/file.py
```

**Features:**
- AST-based code structure analysis
- Extracts functions, classes, imports
- Module metadata detection
- LLM-generated understanding of script purpose
- Integration with existing documentation
- Clickable file paths and line numbers

**Suggested Workflow:**

1. **Analyze a file:**
   ```
   @C:\project\mymodule.py
   ```

2. **Generate function comments:**
   ```
   comment functions
   ```

3. **Document dependencies:**
   ```
   analyze dependencies
   ```

4. **Generate full documentation:**
   ```
   generate docs
   ```

---

## Examples

### Example 1: Simple Data Processor

```python
"""
Data Deduplicator

Removes duplicate entries from datasets.
Supports CSV, JSON, and Python lists.
"""

from typing import Dict, Any, List
from agents.pulsus.ui import display_manager as ui

__domain__ = "analysis"
__action__ = "deduplicate"


def handle(text: str = "") -> Dict[str, Any]:
    """Remove duplicates from data."""
    ui.info("Starting deduplication...")

    # Parse input (simplified)
    data = parse_data_source(text)

    # Remove duplicates
    unique_data = list(set(data))
    removed = len(data) - len(unique_data)

    ui.success(f"Removed {removed} duplicates")

    return {
        "status": "success",
        "message": f"Deduplication complete: {removed} duplicates removed",
        "original_count": len(data),
        "unique_count": len(unique_data),
        "duplicates_removed": removed
    }


def parse_data_source(text: str) -> List:
    """Parse data from input."""
    # Implementation
    return []
```

### Example 2: LLM-Powered Tool

```python
"""
Code Explainer

Explains code snippets in natural language using LLM.
"""

from typing import Dict, Any
import requests
from agents.pulsus.config.settings import load_settings
from agents.pulsus.ui import display_manager as ui
from agents.pulsus.console.interrupt_handler import get_interrupt_handler

__domain__ = "analysis"
__action__ = "explain_code"


def handle(text: str = "") -> Dict[str, Any]:
    """Explain code using LLM."""
    settings = load_settings()
    interrupt_handler = get_interrupt_handler()
    interrupt_handler.start_listening()

    try:
        ui.info("Analyzing code...")
        ui.info("Press ESC to interrupt...")

        code = extract_code(text)
        prompt = f"Explain this code:\n\n```\n{code}\n```"

        response = requests.post(
            f"{settings.model.host}/api/generate",
            json={
                "model": settings.model.name,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )

        explanation = ""
        for line in response.iter_lines():
            if interrupt_handler.is_interrupted():
                raise InterruptedError("Explanation interrupted by user")

            # Process streaming response
            chunk = parse_chunk(line)
            explanation += chunk
            print(chunk, end='', flush=True)

        return {
            "status": "success",
            "message": "Explanation complete",
            "explanation": explanation
        }

    except InterruptedError as e:
        ui.warn(f"\n{e}")
        return {"status": "interrupted", "message": str(e)}
    finally:
        interrupt_handler.stop_listening()


def extract_code(text: str) -> str:
    """Extract code from user input."""
    # Implementation
    return ""

def parse_chunk(line: bytes) -> str:
    """Parse streaming chunk."""
    # Implementation
    return ""
```

### Example 3: File-Based Tool

```python
"""
Configuration Validator

Validates YAML/JSON configuration files against schemas.
"""

from typing import Dict, Any
from pathlib import Path
import json
import yaml
from agents.pulsus.ui import display_manager as ui

__domain__ = "analysis"
__action__ = "validate_config"


def handle(text: str = "") -> Dict[str, Any]:
    """Validate configuration file."""
    # Extract file path from input
    file_path = extract_path(text)

    if not file_path:
        return {
            "status": "error",
            "message": "No file path provided. Use: validate config @path/to/file"
        }

    path = Path(file_path)

    if not path.exists():
        ui.error(f"File not found: {path}")
        return {"status": "error", "message": "File not found"}

    # Validate based on extension
    if path.suffix == '.json':
        errors = validate_json(path)
    elif path.suffix in ['.yml', '.yaml']:
        errors = validate_yaml(path)
    else:
        return {"status": "error", "message": "Unsupported file type"}

    if not errors:
        ui.success("Configuration is valid!")
        return {"status": "success", "message": "Valid", "errors": []}
    else:
        ui.error(f"Found {len(errors)} validation errors")
        for error in errors:
            ui.warn(f"  - {error}")
        return {
            "status": "success",
            "message": f"Validation complete with {len(errors)} errors",
            "valid": False,
            "errors": errors
        }


def extract_path(text: str) -> str:
    """Extract file path from @path syntax."""
    import re
    match = re.search(r'@([^\s]+)', text)
    return match.group(1) if match else ""


def validate_json(path: Path) -> list:
    """Validate JSON file."""
    try:
        with open(path) as f:
            json.load(f)
        return []
    except json.JSONDecodeError as e:
        return [str(e)]


def validate_yaml(path: Path) -> list:
    """Validate YAML file."""
    try:
        with open(path) as f:
            yaml.safe_load(f)
        return []
    except yaml.YAMLError as e:
        return [str(e)]
```

---

## Testing

### Unit Tests

Create tests in `agents/pulsus/tests/`:

```python
"""
tests/test_my_tool.py
"""

import pytest
from agents.pulsus.workflows.tools.your_domain.your_tool import handle


class TestYourTool:
    """Test suite for your tool."""

    def test_basic_functionality(self):
        """Test basic tool operation."""
        result = handle("test input")
        assert result["status"] == "success"
        assert "message" in result

    def test_empty_input(self):
        """Test handling of empty input."""
        result = handle("")
        assert result["status"] == "error"

    def test_invalid_input(self):
        """Test error handling."""
        result = handle("invalid@@#$%")
        assert result["status"] == "error"
        assert "message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Manual Testing

Test standalone:

```bash
cd testudo
python -m agents.pulsus.workflows.tools.your_domain.your_tool
```

Test in Pulsus:

```bash
python -m agents.pulsus
# Then type commands that should trigger your tool
```

### Integration Testing

Verify discovery:

```python
from agents.pulsus.routing.tool_discovery import discover

# Test if your tool is discovered
results = discover("your_domain", "your_action", "test query")
print(f"Found {len(results)} tools")
for tool in results:
    print(f"  - {tool.path.name}: score={tool.score}")
```

---

## Troubleshooting

### Tool Not Discovered

**Problem:** Your tool isn't found by Pulsus

**Solutions:**
1. Check `__domain__` and `__action__` are defined
2. Verify file is in `workflows/tools/` subdirectory
3. Ensure module has a `handle()` function
4. Add more keywords to module docstring
5. Check for syntax errors: `python -m py_compile your_tool.py`

### Low Discovery Score

**Problem:** Tool found but not selected

**Solutions:**
1. Make domain/action names more specific
2. Add relevant keywords to docstring
3. Match common user vocabulary
4. Check competing tools with similar metadata

### Import Errors

**Problem:** Module fails to load

**Solutions:**
1. Ensure all dependencies are installed
2. Use relative imports for Pulsus modules
3. Add error handling in imports
4. Check Python path and virtual environment

---

## Additional Resources

### Core System
- **Router Implementation**: `agents/pulsus/routing/router.py`
- **Discovery Logic**: `agents/pulsus/routing/tool_discovery.py`
- **Existing Tools**: `agents/pulsus/workflows/tools/`
- **Types**: `agents/pulsus/core/types.py`
- **UI Manager**: `agents/pulsus/ui/display_manager.py`
- **Settings**: `agents/pulsus/config/settings.py`

### MCP Tools
- **MCP Script Operations**: `agents/mcp/helpers/script_ops.py`
- **MCP Action Logger**: `agents/mcp/helpers/action_logger.py`
- **MCP Tool Bindings**: `agents/shared/tools.py`
- **MCP Tests**: `agents/mcp/test_structure_tools.py`
- **MCP TODO/Roadmap**: `agents/pulsus/workflows/Pulsus-MCP-TODO.md`
- **MCP Logs**: `logs/mcp/`

### Documentation
- **UI Features Guide**: `agents/pulsus/ui/README.md`
- **Features Display**: `agents/pulsus/config/features_display.py`
- **This Guide**: `agents/pulsus/workflows/README.md`

---

## Quick Checklist

When creating a new tool, ensure:

- [ ] Tool is in `workflows/tools/{domain}/` directory
- [ ] `__domain__` and `__action__` metadata defined
- [ ] Module docstring is descriptive with keywords
- [ ] `handle(text: str = "") -> Dict[str, Any]` function exists
- [ ] Returns dict with `status` and `message` keys
- [ ] Error handling for common failure cases
- [ ] Interrupt support for long operations (optional)
- [ ] UI messages for user feedback
- [ ] Unit tests created
- [ ] Tested standalone and in Pulsus

---

**Happy tool building! 🛠️**

For questions or issues, check existing tools in `workflows/tools/` for reference implementations.
