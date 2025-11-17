# Classic MCP Domain Catalog

**Version:** 1.0
**Date:** November 17, 2025
**Status:** Phase 2 Complete

---

## Overview

This catalog documents all Classic MCP Domains (Tier 1) implemented in the Pulsus MCP framework. Classic domains provide simple, atomic operations with clear inputs and outputs, designed for direct integration with LangChain and other AI agent frameworks.

All classic domains:
- Extend `MCPBase` for standardized behavior
- Return `MCPResponse` for consistent LLM interaction
- Use safety decorators (`@read_only`, `@write_safe`, `@cached`)
- Include comprehensive error handling
- Are fully tested with 90%+ coverage
- Convert seamlessly to LangChain `StructuredTool`

---

## Table of Contents

1. [ScriptOps](#scriptops) - Python script operations
2. [RepositoryOps](#repositoryops) - Repository analysis
3. [FileManager](#filemanager) - File system operations
4. [DataReader](#datareader) - Data loading and analysis
5. [TextProcessor](#textprocessor) - Text manipulation
6. [Usage Examples](#usage-examples)
7. [LangChain Integration](#langchain-integration)

---

## Domain Details

### ScriptOps

**File:** `mcp/simple/script_ops.py`
**Purpose:** Python script operations including reading, analyzing, documenting, and formatting code.

#### Capabilities

| Operation | Decorator | Description |
|-----------|-----------|-------------|
| `read_script` | `@read_only` | Read and analyze Python script with AST parsing |
| `write_script` | `@write_safe` | Write or update Python script content |
| `format_script` | `@write_safe` | Format Python script with black, isort, autoflake |
| `comment_functions` | `@write_safe` | Add docstrings to functions using AI |
| `analyze_structure` | `@read_only` | Extract functions, classes, imports from script |
| `generate_documentation` | `@write_safe` | Generate documentation for Python module |

#### Example Usage

```python
from mcp.simple import ScriptOps

ops = ScriptOps()

# Read and analyze a script
response = ops.read_script(path="/path/to/script.py")
if response.success:
    print(f"Found {len(response.data['ast_analysis']['functions'])} functions")

# Format a script
response = ops.format_script(path="/path/to/script.py")
if response.success:
    print("Script formatted successfully")
```

---

### RepositoryOps

**File:** `mcp/simple/repository_ops.py`
**Purpose:** Repository analysis and management operations for understanding codebase structure and dependencies.

#### Capabilities

| Operation | Decorator | Description |
|-----------|-----------|-------------|
| `scan_repository` | `@read_only @cached` | Scan repository structure and file inventory |
| `analyze_dependencies` | `@read_only @cached` | Analyze Python dependencies and imports |
| `generate_report` | `@write_safe` | Generate markdown report of repository analysis |
| `find_files` | `@read_only` | Find files matching pattern in repository |
| `get_stats` | `@read_only @cached` | Get repository statistics (LOC, files, etc.) |

#### Example Usage

```python
from mcp.simple import RepositoryOps

ops = RepositoryOps()

# Scan repository
response = ops.scan_repository(path="/path/to/repo")
if response.success:
    print(f"Found {response.data['file_count']} files")

# Analyze dependencies
response = ops.analyze_dependencies(path="/path/to/repo")
if response.success:
    deps = response.data['dependencies']
    print(f"Found {len(deps)} dependencies")
```

---

### FileManager

**File:** `mcp/simple/file_manager.py`
**Purpose:** File system operations for creating, deleting, moving, and managing files.

**Status:** ✅ Phase 2 New
**Tests:** 14/14 passed
**Lines:** 445

#### Capabilities

| Operation | Decorator | Description |
|-----------|-----------|-------------|
| `create_file` | `@write_safe` | Create a new file with optional content |
| `delete_file` | `@write_safe` | Delete an existing file |
| `move_file` | `@write_safe` | Move file from source to destination |
| `copy_file` | `@write_safe` | Copy file from source to destination |
| `list_files` | `@read_only` | List files in directory with glob pattern |
| `get_file_info` | `@read_only` | Get detailed file information (size, dates, etc.) |

#### Example Usage

```python
from mcp.simple import FileManager

fm = FileManager()

# Create a file
response = fm.create_file(
    path="/tmp/test.txt",
    content="Hello World"
)

# List files with pattern
response = fm.list_files(
    directory="/tmp",
    pattern="*.txt",
    recursive=False
)
if response.success:
    print(f"Found {response.data['count']} files")

# Get file info
response = fm.get_file_info(path="/tmp/test.txt")
if response.success:
    print(f"File size: {response.data['size']} bytes")
```

#### Safety Features

- Path validation to prevent directory traversal
- Overwrite protection (requires explicit `overwrite=True`)
- Automatic parent directory creation
- Comprehensive error handling for permissions, missing files

---

### DataReader

**File:** `mcp/simple/data_reader.py`
**Purpose:** Data loading and analysis for multiple formats (CSV, JSON, Parquet, Excel).

**Status:** ✅ Phase 2 New
**Tests:** 11/11 passed
**Lines:** 467

#### Capabilities

| Operation | Decorator | Description |
|-----------|-----------|-------------|
| `read_csv` | `@read_only @cached` | Read CSV file into pandas DataFrame |
| `read_json` | `@read_only @cached` | Read JSON file (list or dict) |
| `read_parquet` | `@read_only @cached` | Read Parquet file into DataFrame |
| `read_excel` | `@read_only @cached` | Read Excel file (specific sheet) |
| `get_schema` | `@read_only @cached` | Get schema/metadata for data file |
| `query_dataframe` | `@read_only` | Query data using pandas query syntax |

#### Example Usage

```python
from mcp.simple import DataReader

dr = DataReader()

# Read CSV
response = dr.read_csv(
    path="/data/sales.csv",
    delimiter=",",
    max_rows=1000
)
if response.success:
    print(f"Loaded {response.data['rows']} rows")
    print(f"Columns: {response.data['columns']}")

# Query dataframe
data = [
    {'name': 'Alice', 'age': 30, 'city': 'NYC'},
    {'name': 'Bob', 'age': 25, 'city': 'LA'}
]
response = dr.query_dataframe(data, "age > 25")
if response.success:
    print(f"Found {response.data['row_count']} matching rows")

# Get schema
response = dr.get_schema(path="/data/sales.csv")
if response.success:
    print(f"Format: {response.data['format']}")
    print(f"Columns: {response.data['columns']}")
```

#### Supported Formats

- **CSV/TSV** - Customizable delimiter, encoding, header
- **JSON** - Lists, objects, nested structures
- **Parquet** - Columnar storage with schema
- **Excel** - Multiple sheets, custom headers

#### Performance Features

- **Caching** - Results cached for 5 minutes (TTL: 300s)
- **Lazy Loading** - Optional `max_rows` parameter
- **Schema-only** - `get_schema()` avoids full data load

---

### TextProcessor

**File:** `mcp/simple/text_processor.py`
**Purpose:** Text manipulation and analysis including search, replace, extract, and word counting.

**Status:** ✅ Phase 2 New
**Tests:** 17/17 passed
**Lines:** 400

#### Capabilities

| Operation | Decorator | Description |
|-----------|-----------|-------------|
| `search_text` | `@read_only` | Search for pattern in text (regex or literal) |
| `replace_text` | `@read_only` | Replace pattern with new string |
| `extract_patterns` | `@read_only` | Extract all matches of a regex pattern |
| `count_words` | `@read_only @cached` | Count word frequencies in text |
| `split_text` | `@read_only` | Split text by delimiter (literal or regex) |
| `analyze_text` | `@read_only` | Comprehensive text analysis (stats, metrics) |

#### Example Usage

```python
from mcp.simple import TextProcessor

tp = TextProcessor()

# Search with regex
response = tp.search_text(
    text="The quick brown fox jumps over the lazy dog",
    pattern=r"\b\w{5}\b",  # 5-letter words
    regex=True
)
if response.success:
    print(f"Found {response.data['count']} matches")

# Replace text
response = tp.replace_text(
    text="Hello World",
    old="World",
    new="Universe",
    ignore_case=False
)
if response.success:
    print(response.data['new_text'])  # "Hello Universe"

# Count words
response = tp.count_words(
    text="The quick brown fox. The lazy dog.",
    case_sensitive=False
)
if response.success:
    print(f"Total words: {response.data['total_words']}")
    print(f"Unique words: {response.data['unique_words']}")
    print(f"Top 10: {response.data['top_10']}")

# Analyze text
response = tp.analyze_text(text="Sample text here...")
if response.success:
    print(f"Length: {response.data['length']}")
    print(f"Words: {response.data['words']}")
    print(f"Sentences: {response.data['sentences']}")
    print(f"Avg word length: {response.data['avg_word_length']}")
```

#### Regex Features

- **Full regex support** - Python `re` module patterns
- **Case insensitive** - Optional `ignore_case` flag
- **Group extraction** - Extract specific regex groups
- **Match indices** - Get position of matches

---

## Usage Examples

### Chaining Operations

```python
from mcp.simple import FileManager, DataReader, TextProcessor

fm = FileManager()
dr = DataReader()
tp = TextProcessor()

# Create CSV file
fm.create_file(
    path="/tmp/data.csv",
    content="name,description\nAlice,Quick learner\nBob,Fast worker"
)

# Read CSV
response = dr.read_csv(path="/tmp/data.csv")
data = response.data['data']  # List of dicts

# Process text from CSV
descriptions = " ".join([row['description'] for row in data])
response = tp.count_words(text=descriptions)
print(f"Word count: {response.data['total_words']}")
```

### Error Handling

```python
from mcp.simple import FileManager

fm = FileManager()

response = fm.get_file_info(path="/nonexistent/file.txt")

if not response.success:
    print(f"Error: {response.error}")
    print(f"Trace: {response.trace}")
else:
    print(f"File info: {response.data}")
```

### Using Capabilities

```python
from mcp.simple import FileManager

fm = FileManager()

# Get all capabilities
capabilities = fm.get_capabilities()

for cap in capabilities:
    print(f"Operation: {cap['name']}")
    print(f"Description: {cap['description']}")
    print(f"Safety Level: {cap['safety_level']}")
```

---

## LangChain Integration

All classic MCP domains can be converted to LangChain `StructuredTool` for use in AI agents.

### Converting Domains to Tools

```python
from mcp.simple import FileManager, DataReader, TextProcessor
from langchain.tool_adapter import mcp_to_langchain_tool

# Convert entire domain to a tool
file_tool = mcp_to_langchain_tool(FileManager)
data_tool = mcp_to_langchain_tool(DataReader)
text_tool = mcp_to_langchain_tool(TextProcessor)

# Convert specific operation to a tool
list_tool = mcp_to_langchain_tool(FileManager, 'list_files')
```

### Using Tool Registry

```python
from mcp.simple import FileManager, DataReader, TextProcessor
from langchain.tool_adapter import MCPToolRegistry

# Create registry
registry = MCPToolRegistry()

# Register all classic domains
registry.register_domain(FileManager)
registry.register_domain(DataReader)
registry.register_domain(TextProcessor)

# Get all tools for agent
tools = registry.get_all_tools()

# Use in LangChain agent
from langchain.agents import AgentExecutor
agent = AgentExecutor(tools=tools, llm=my_llm, verbose=True)
```

### Auto-Discovery

```python
from langchain.tool_adapter import discover_and_convert_mcp_domains

# Automatically discover all MCP domains
tools = discover_and_convert_mcp_domains(
    search_paths=['mcp.simple'],
    verbose=True
)

print(f"Discovered {len(tools)} tools")
# Output: Discovered 5 tools (ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor)
```

---

## Domain Comparison Matrix

| Domain | Operations | Read-Only | Write-Safe | Cached | Use Case |
|--------|-----------|-----------|------------|--------|----------|
| ScriptOps | 6 | 2 | 4 | 0 | Python code manipulation |
| RepositoryOps | 5 | 4 | 1 | 3 | Codebase analysis |
| FileManager | 6 | 2 | 4 | 0 | File system operations |
| DataReader | 6 | 6 | 0 | 5 | Data loading and querying |
| TextProcessor | 6 | 6 | 0 | 1 | Text manipulation |

---

## Testing Summary

All classic domains have comprehensive test coverage:

| Domain | Test File | Tests | Status |
|--------|-----------|-------|--------|
| ScriptOps | `test_script_ops.py` | 15 | ✅ Passing |
| RepositoryOps | `test_repository_analyzer.py` | 12 | ✅ Passing |
| FileManager | `test_new_domains.py::TestFileManager` | 14 | ✅ Passing |
| DataReader | `test_new_domains.py::TestDataReader` | 11 | ✅ Passing |
| TextProcessor | `test_new_domains.py::TestTextProcessor` | 17 | ✅ Passing |
| **LangChain Integration** | `test_langchain_integration.py` | 22 | ✅ Passing |

**Total:** 91 tests, all passing ✅

---

## Best Practices

### 1. Always Check Response Success

```python
response = domain.operation(...)
if not response.success:
    # Handle error
    log.error(f"Operation failed: {response.error}")
    return
# Process response.data
```

### 2. Use Type Hints

```python
from mcp.simple import FileManager
from mcp.core.base import MCPResponse

fm: FileManager = FileManager()
response: MCPResponse = fm.create_file(path="/tmp/test.txt", content="Hello")
```

### 3. Leverage Caching

Operations marked with `@cached` store results for 5 minutes:
- `DataReader.read_csv()`, `read_json()`, `read_parquet()`, `read_excel()`, `get_schema()`
- `RepositoryOps.scan_repository()`, `analyze_dependencies()`, `get_stats()`
- `TextProcessor.count_words()`

### 4. Review Trace for Debugging

```python
response = domain.operation(...)
for trace_msg in response.trace:
    print(f"[TRACE] {trace_msg}")
```

### 5. Use Safety Decorators

When creating custom operations:
- `@read_only` - No side effects
- `@write_safe` - Requires confirmation
- `@cached(ttl=300)` - Cache for 5 minutes

---

## Next Steps

### Phase 3: Workflow MCP Domains (Tier 2)

Coming next:
- **RepositoryAnalyzer** - Multi-step analysis workflow
- **CodeRefactorer** - Plan → Execute → Validate
- **DocumentationGenerator** - Scan → Analyze → Generate

---

**Document Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** Phase 2 Complete
**Domains:** 5 Classic MCP Domains (ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor)
