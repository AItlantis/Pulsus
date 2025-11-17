# BMAP: Building MCP Scripts for Pulsus

**BMAP** = **B**uilding **M**CP **A**ctions for **P**ulsus

**Version**: 1.0
**Last Updated**: November 2025
**Audience**: Developers building custom MCP domains

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [MCP Architecture Tiers](#mcp-architecture-tiers)
4. [Building Tier 1: Classic MCP](#building-tier-1-classic-mcp)
5. [Building Tier 2: Workflow MCP](#building-tier-2-workflow-mcp)
6. [Building Tier 3: Customizable MCP](#building-tier-3-customizable-mcp)
7. [Safety & Decorators](#safety--decorators)
8. [Testing Your MCP](#testing-your-mcp)
9. [LangChain Integration](#langchain-integration)
10. [Best Practices](#best-practices)
11. [Examples](#examples)

---

## Overview

This guide teaches you how to build custom MCP (Model Context Protocol) scripts for Pulsus. Pulsus uses a **three-tier architecture** that allows you to create operations ranging from simple atomic actions to complex multi-step workflows.

### What You'll Learn

- How to create MCPBase-compatible scripts
- When to use each tier (Classic, Workflow, Customizable)
- How to apply safety decorators
- How to integrate with LangChain
- How to test your MCP operations

### Prerequisites

- Python 3.10+
- Understanding of Python classes and decorators
- Basic knowledge of type hints
- Familiarity with Pydantic (helpful but not required)

---

## Quick Start

### 5-Minute MCP Creation

Create your first MCP domain in 5 minutes:

```python
# my_custom_mcp.py
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only

class MyCustomMCP(MCPBase):
    """My first custom MCP domain"""

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "domain": "my_custom",
            "description": "My custom operations",
            "actions": {
                "hello_world": {
                    "description": "Returns hello world",
                    "params": {}
                }
            }
        }

    @read_only
    def hello_world(self) -> MCPResponse:
        """Simple hello world operation"""
        return MCPResponse.success(
            data={"message": "Hello from my custom MCP!"}
        )
```

Save to `mcp/simple/my_custom_mcp.py`, and Pulsus will automatically discover it!

---

## MCP Architecture Tiers

Pulsus organizes MCP operations into three tiers based on complexity:

| Tier | Complexity | Use Case | Location |
|------|-----------|----------|----------|
| **Tier 1: Classic** | Simple, atomic | File operations, data loading | `mcp/simple/` |
| **Tier 2: Workflow** | Multi-step, stateful | Analysis workflows, refactoring | `workflows/` |
| **Tier 3: Customizable** | User-defined configs | Custom project workflows | `config/frameworks/` |

### Decision Tree: Which Tier?

```
Is it a single, atomic operation?
├─ YES → Tier 1 (Classic MCP)
└─ NO → Does it require multiple steps?
    ├─ YES → Are the steps fixed or user-configurable?
    │   ├─ Fixed → Tier 2 (Workflow MCP)
    │   └─ User-defined → Tier 3 (Customizable MCP)
    └─ NO → Tier 1 (Classic MCP)
```

---

## Building Tier 1: Classic MCP

Classic MCPs are **simple, atomic operations** with clear inputs and outputs.

### Step 1: Create MCP Class

```python
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe
from typing import Dict, Any
from pathlib import Path

class FileManager(MCPBase):
    """Manage file operations"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Define what this MCP can do"""
        return {
            "domain": "file_manager",
            "description": "File system operations",
            "actions": {
                "read_file": {
                    "description": "Read file contents",
                    "params": {
                        "path": {"type": "str", "description": "File path"}
                    }
                },
                "write_file": {
                    "description": "Write content to file",
                    "params": {
                        "path": {"type": "str", "description": "File path"},
                        "content": {"type": "str", "description": "File content"}
                    }
                }
            }
        }

    @read_only
    def read_file(self, path: str) -> MCPResponse:
        """
        Read file contents.

        Args:
            path: Path to file

        Returns:
            MCPResponse with file content
        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                return MCPResponse.error(f"File not found: {path}")

            content = file_path.read_text()

            return MCPResponse.success(
                data={"content": content, "path": str(file_path)},
                context={"file_size": file_path.stat().st_size}
            )

        except Exception as e:
            return MCPResponse.error(f"Failed to read file: {e}")

    @write_safe
    def write_file(self, path: str, content: str) -> MCPResponse:
        """
        Write content to file.

        Args:
            path: Path to file
            content: Content to write

        Returns:
            MCPResponse with write status
        """
        try:
            file_path = Path(path)

            # Safety check: don't overwrite without confirmation
            if file_path.exists():
                # @write_safe decorator will request approval
                pass

            file_path.write_text(content)

            return MCPResponse.success(
                data={"path": str(file_path), "bytes_written": len(content)}
            )

        except Exception as e:
            return MCPResponse.error(f"Failed to write file: {e}")
```

### Step 2: Save to Correct Location

```bash
# Save to mcp/simple/ for automatic discovery
mv file_manager.py mcp/simple/file_manager.py
```

### Step 3: Test Discovery

```python
from langchain_integration import discover_and_convert_mcp_domains

# Pulsus will automatically discover your MCP
tools = discover_and_convert_mcp_domains()
print([t.name for t in tools])  # Should include 'file_manager'
```

---

## Building Tier 2: Workflow MCP

Workflow MCPs handle **multi-step operations** with state management.

### Step 1: Create Workflow Class

```python
from workflows.base import WorkflowBase, WorkflowStep, WorkflowState
from mcp.core.base import MCPResponse
from typing import Dict, Any

class RepositoryAnalyzer(WorkflowBase):
    """Multi-step repository analysis"""

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "domain": "repository_analyzer",
            "description": "Analyze code repository structure",
            "actions": {
                "analyze_repository": {
                    "description": "Full repository analysis",
                    "params": {
                        "repo_path": {"type": "str", "description": "Path to repository"}
                    }
                }
            }
        }

    def analyze_repository(self, repo_path: str) -> MCPResponse:
        """
        Execute multi-step repository analysis.

        Steps:
        1. Scan files
        2. Parse imports
        3. Analyze dependencies
        4. Generate report

        Args:
            repo_path: Path to repository

        Returns:
            MCPResponse with analysis results
        """
        state = WorkflowState()
        state.context['repo_path'] = repo_path

        steps = [
            WorkflowStep("scan_files", self._scan_files, required=True),
            WorkflowStep("parse_imports", self._parse_imports, required=True),
            WorkflowStep("analyze_deps", self._analyze_dependencies, required=True),
            WorkflowStep("generate_report", self._generate_report, required=False)
        ]

        # Execute steps sequentially
        for step in steps:
            result = step.execute(state)

            if not result.success and step.required:
                return MCPResponse.error(
                    f"Step '{step.name}' failed: {result.error}"
                )

            state.update(step.name, result.data)

        return MCPResponse.success(
            data=state.to_dict(),
            trace=state.get_trace()
        )

    def _scan_files(self, state: WorkflowState) -> MCPResponse:
        """Step 1: Scan repository files"""
        repo_path = state.context['repo_path']
        # ... scan logic ...
        return MCPResponse.success(data={"files": files})

    def _parse_imports(self, state: WorkflowState) -> MCPResponse:
        """Step 2: Parse import statements"""
        files = state.results['scan_files']['files']
        # ... parse logic ...
        return MCPResponse.success(data={"imports": imports})

    # ... other step methods ...
```

### Step 2: Save to Workflows Directory

```bash
mv repository_analyzer.py workflows/tools/analyze/repository_analyzer.py
```

---

## Building Tier 3: Customizable MCP

Customizable MCPs are **user-defined via JSON/YAML** configuration.

### Step 1: Create Configuration File

```json
{
  "name": "custom_code_analysis",
  "description": "Custom code analysis workflow",
  "version": "1.0",
  "steps": [
    {
      "name": "scan_python_files",
      "tool": "FileScanner",
      "config": {
        "patterns": ["**/*.py"],
        "exclude": ["**/test_*.py", "**/__pycache__/**"]
      },
      "required": true
    },
    {
      "name": "analyze_complexity",
      "tool": "ComplexityAnalyzer",
      "config": {
        "threshold": 10,
        "metrics": ["cyclomatic", "cognitive"]
      },
      "required": true
    },
    {
      "name": "generate_report",
      "tool": "ReportGenerator",
      "config": {
        "template": "code_analysis_report.j2",
        "format": "markdown",
        "output_path": "reports/analysis.md"
      },
      "required": false
    }
  ],
  "on_error": "rollback",
  "timeout": 300
}
```

### Step 2: Save to Frameworks Directory

```bash
mkdir -p config/frameworks/custom_workflows/
mv custom_code_analysis.json config/frameworks/custom_workflows/
```

### Step 3: Execute Custom Workflow

```python
from workflows.custom_executor import execute_custom_workflow

result = execute_custom_workflow(
    config_path="config/frameworks/custom_workflows/custom_code_analysis.json",
    params={"repo_path": "/path/to/repo"}
)
```

---

## Safety & Decorators

Pulsus provides safety decorators to enforce security policies.

### Available Decorators

#### @read_only
```python
@read_only
def safe_read(self, path: str) -> MCPResponse:
    """Guaranteed read-only, no modifications allowed"""
    # Can read files, query data, analyze code
    # Cannot write files, execute commands, modify state
    pass
```

#### @write_safe
```python
@write_safe
def controlled_write(self, path: str, content: str) -> MCPResponse:
    """Write operation with user approval required"""
    # Will prompt user for approval before executing
    # User sees what will be modified
    pass
```

#### @restricted_write
```python
@restricted_write(file_types=[".py", ".json"], platform="linux")
def limited_write(self, path: str, content: str) -> MCPResponse:
    """Write restricted to specific file types and platforms"""
    # Only allows writing .py and .json files
    # Only works on Linux platform
    pass
```

#### @transactional
```python
@transactional(rollback_on_error=True)
def atomic_operation(self, params: Dict) -> MCPResponse:
    """All-or-nothing operation with automatic rollback"""
    # If any part fails, all changes are rolled back
    # Ensures data consistency
    pass
```

#### @cached
```python
@cached(ttl=3600)  # Cache for 1 hour
def expensive_operation(self, param: str) -> MCPResponse:
    """Expensive operation with caching"""
    # Result cached for 1 hour
    # Subsequent calls with same params return cached result
    pass
```

### Safety Best Practices

1. **Always use decorators**: Never create "naked" operations
2. **Start with @read_only**: Use most restrictive decorator by default
3. **Escalate only when needed**: Move to @write_safe only if modifications required
4. **Document safety**: Explain why specific decorator is used

```python
# ✅ GOOD: Starts restrictive, escalates with justification
@read_only
def analyze_code(self, path: str) -> MCPResponse:
    """Analysis is read-only, no modifications needed"""
    pass

@write_safe  # Needs to format code in-place
def format_code(self, path: str) -> MCPResponse:
    """Formatting requires file modification"""
    pass

# ❌ BAD: Too permissive for simple read operation
@write_safe
def analyze_code(self, path: str) -> MCPResponse:
    """Just reading, doesn't need write permission"""
    pass
```

---

## Testing Your MCP

### Unit Tests

```python
# tests/unit/test_my_mcp.py
import pytest
from mcp.simple.my_custom_mcp import MyCustomMCP

def test_hello_world():
    """Test hello_world action"""
    mcp = MyCustomMCP()
    result = mcp.hello_world()

    assert result.success
    assert result.data['message'] == "Hello from my custom MCP!"

def test_capabilities():
    """Test capability definition"""
    mcp = MyCustomMCP()
    caps = mcp.get_capabilities()

    assert caps['domain'] == "my_custom"
    assert 'hello_world' in caps['actions']
```

### Integration Tests

```python
# tests/integration/test_my_mcp_langchain.py
import pytest
from langchain_integration import mcp_to_langchain_tool
from mcp.simple.my_custom_mcp import MyCustomMCP

def test_langchain_conversion():
    """Test conversion to LangChain tool"""
    tool = mcp_to_langchain_tool(MyCustomMCP)

    assert tool.name == "my_custom"
    assert callable(tool.func)

def test_langchain_execution():
    """Test execution via LangChain"""
    tool = mcp_to_langchain_tool(MyCustomMCP)
    result = tool.func(action="hello_world", params={})

    assert result['success']
    assert result['data']['message'] == "Hello from my custom MCP!"
```

### Run Tests

```bash
# Run all tests
pytest tests/unit/test_my_mcp.py -v

# Run with coverage
pytest tests/unit/test_my_mcp.py --cov=mcp.simple.my_custom_mcp --cov-report=html
```

---

## LangChain Integration

### Automatic Conversion

Your MCP is automatically available as a LangChain tool:

```python
from langchain_integration import mcp_to_langchain_tool
from mcp.simple.my_custom_mcp import MyCustomMCP

# Convert to LangChain tool
tool = mcp_to_langchain_tool(MyCustomMCP)

# Use in LangChain agent
from langchain.agents import AgentExecutor

agent = AgentExecutor(tools=[tool], ...)
result = agent.invoke("Say hello")
```

### Dynamic Discovery

Pulsus discovers your MCP automatically:

```python
from langchain_integration import discover_and_convert_mcp_domains

# Discover all MCPs (including yours)
all_tools = discover_and_convert_mcp_domains()

# Your MCP is included automatically
my_tool = [t for t in all_tools if t.name == "my_custom"][0]
```

---

## Best Practices

### 1. Naming Conventions

```python
# ✅ GOOD: Clear, descriptive names
class FileManager(MCPBase):
    def read_file(self, path: str):
        pass

# ❌ BAD: Unclear abbreviations
class FM(MCPBase):
    def rf(self, p: str):
        pass
```

### 2. Error Handling

```python
# ✅ GOOD: Comprehensive error handling
@read_only
def read_file(self, path: str) -> MCPResponse:
    try:
        content = Path(path).read_text()
        return MCPResponse.success(data={"content": content})
    except FileNotFoundError:
        return MCPResponse.error(f"File not found: {path}")
    except PermissionError:
        return MCPResponse.error(f"Permission denied: {path}")
    except Exception as e:
        return MCPResponse.error(f"Unexpected error: {e}")

# ❌ BAD: Lets exceptions bubble up
@read_only
def read_file(self, path: str) -> MCPResponse:
    content = Path(path).read_text()  # Can crash
    return MCPResponse.success(data={"content": content})
```

### 3. Documentation

```python
# ✅ GOOD: Complete docstring
@read_only
def analyze_code(self, path: str, metrics: List[str]) -> MCPResponse:
    """
    Analyze code file using specified metrics.

    This operation reads the Python file, parses the AST, and
    calculates complexity metrics. No modifications are made.

    Args:
        path: Path to Python file to analyze
        metrics: List of metrics to calculate (e.g., ['cyclomatic', 'cognitive'])

    Returns:
        MCPResponse with analysis results:
        - success: bool indicating if analysis completed
        - data: Dict with metric results
        - trace: List of analysis steps performed

    Example:
        >>> mcp = CodeAnalyzer()
        >>> result = mcp.analyze_code("example.py", ["cyclomatic"])
        >>> print(result.data['metrics']['cyclomatic'])
        5
    """
    pass
```

### 4. Type Safety

```python
# ✅ GOOD: Full type hints
from typing import Dict, Any, List
from pathlib import Path

@read_only
def process_files(
    self,
    paths: List[Path],
    options: Dict[str, Any]
) -> MCPResponse:
    pass

# ❌ BAD: No type hints
@read_only
def process_files(self, paths, options):
    pass
```

### 5. Separation of Concerns

```python
# ✅ GOOD: Each action does one thing
class CodeAnalyzer(MCPBase):
    @read_only
    def analyze_complexity(self, path: str) -> MCPResponse:
        """Only analyzes complexity"""
        pass

    @read_only
    def analyze_style(self, path: str) -> MCPResponse:
        """Only checks style"""
        pass

# ❌ BAD: Single action does everything
class CodeAnalyzer(MCPBase):
    @read_only
    def analyze_everything(self, path: str) -> MCPResponse:
        """Analyzes complexity, style, security, tests..."""
        pass  # Too much in one function
```

---

## Examples

### Example 1: Simple Data Loader

```python
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only
import pandas as pd

class DataLoader(MCPBase):
    """Load data from various formats"""

    def get_capabilities(self):
        return {
            "domain": "data_loader",
            "description": "Load CSV, JSON, Parquet files",
            "actions": {
                "load_csv": {"params": {"path": "str"}},
                "load_json": {"params": {"path": "str"}},
                "load_parquet": {"params": {"path": "str"}}
            }
        }

    @read_only
    def load_csv(self, path: str) -> MCPResponse:
        try:
            df = pd.read_csv(path)
            return MCPResponse.success(data={
                "rows": len(df),
                "columns": list(df.columns),
                "preview": df.head().to_dict()
            })
        except Exception as e:
            return MCPResponse.error(str(e))
```

### Example 2: Git Operations

```python
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe
import subprocess

class GitOps(MCPBase):
    """Git repository operations"""

    def get_capabilities(self):
        return {
            "domain": "git_ops",
            "description": "Git operations",
            "actions": {
                "git_status": {},
                "git_commit": {"params": {"message": "str"}}
            }
        }

    @read_only
    def git_status(self) -> MCPResponse:
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True
            )
            return MCPResponse.success(data={"status": result.stdout})
        except Exception as e:
            return MCPResponse.error(str(e))

    @write_safe
    def git_commit(self, message: str) -> MCPResponse:
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
            return MCPResponse.success(data={"message": message})
        except Exception as e:
            return MCPResponse.error(str(e))
```

---

## Troubleshooting

### MCP Not Discovered

**Problem**: Your MCP doesn't appear in `discover_and_convert_mcp_domains()`

**Solutions**:
1. Check file location: Must be in `mcp/simple/` or `mcp/helpers/`
2. Check class inheritance: Must inherit from `MCPBase`
3. Check imports: Ensure `__init__.py` exists
4. Restart Python interpreter to clear import cache

### Decorator Not Working

**Problem**: Safety decorator not enforcing rules

**Solutions**:
1. Check decorator syntax: `@read_only` not `@read_only()`
2. Check decorator import: `from mcp.core.decorators import read_only`
3. Check decorator order: Safety decorators should be outermost

### LangChain Conversion Fails

**Problem**: `mcp_to_langchain_tool()` raises error

**Solutions**:
1. Check `get_capabilities()` returns correct structure
2. Ensure all actions return `MCPResponse`
3. Verify type hints are correct

---

## Next Steps

1. **Create your first MCP**: Start with Tier 1 (Classic MCP)
2. **Test thoroughly**: Write unit and integration tests
3. **Add to git**: Commit your MCP to the repository
4. **Share**: Submit PR to Pulsus for community use

## Resources

- **ARCHITECTURE.md**: System architecture overview
- **mcp/core/README.md**: Core framework documentation
- **tests/**: Example tests for reference
- **TODO.md**: Roadmap and upcoming features

---

**Happy Building!** 🚀

If you have questions or need help, check the documentation or ask in the community channels.
