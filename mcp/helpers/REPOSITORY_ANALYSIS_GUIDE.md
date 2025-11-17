# Repository Analysis Guide

## Overview

The Repository Analysis feature provides comprehensive Python codebase analysis integrated into the Pulsus MCP framework. It combines file validation, reusability scoring, dependency tracking, and detailed reporting.

Based on the enhanced `read_python_structure.py` script, it provides enterprise-grade repository auditing capabilities.

## Features

### 1. Comprehensive File Analysis
- **AST Parsing**: Extract functions, classes, methods, and calls
- **Complexity Metrics**: Calculate cyclomatic complexity (requires `radon`)
- **Metadata Extraction**: Parse file headers, docstrings, and naming conventions
- **Import Tracking**: Categorize imports (standard library, third-party, local)

### 2. Validation & Compliance
- **Naming Conventions**: Validate file naming patterns
- **Metadata Presence**: Check for owner, type, and description
- **Docstring Completeness**: Verify documentation coverage
- **Issue Detection**: Identify missing or incomplete elements

### 3. Reusability Scoring
Functions are scored on a 0-15 scale based on:
- **Documentation** (+2 points): Has comprehensive docstring
- **Generic Naming** (+2 points): Uses standard prefixes (get_, load_, process_, etc.)
- **Multi-file Usage** (+6 points max): Used in multiple files
- **Low Complexity** (+1 point): Cyclomatic complexity ≤ 10
- **Clean Code** (+1 point): Length < 50 lines
- **No Hardcoded Paths** (-3 points penalty): Avoids hardcoded file paths

### 4. Dependency Analysis
- Track import relationships
- Identify local vs third-party dependencies
- Detect unused functions
- Map function call graphs

### 5. Report Generation
- **Excel Reports**: Multi-sheet workbooks with pivot-ready data
- **JSON Output**: Structured data for programmatic access
- **HTML Visualizations**: Interactive D3.js graphs (future enhancement)

## Installation

### Required Dependencies
```bash
cd testudo
pip install openpyxl  # For Excel report generation
```

### Optional Dependencies
```bash
pip install radon  # For complexity metrics (recommended)
pip install graphviz  # For graph visualizations (future)
```

## Usage

### 1. Analyze a Repository (JSON Output)

**Via MCP Tool:**
```python
from agents.shared.tools import mcp_analyze_repository
import json

# Analyze a repository
result_json = mcp_analyze_repository.invoke({
    "repo_path": "C:/path/to/repository",
    "ignore_patterns": ["test", "__pycache__", ".venv"]
})

result = json.loads(result_json)
print(f"Files analyzed: {result['files_analyzed']}")
print(f"Issues found: {result['issues_summary']['total_issues']}")
print(f"Average reusability score: {result['reusability_summary']['average_score']}")
```

**Via Pulsus Routing:**
```bash
python -m agents.pulsus
> analyze repository at C:/path/to/repository
```

### 2. Generate Excel Report

**Via MCP Tool:**
```python
from agents.shared.tools import mcp_generate_repository_report
import json

result_json = mcp_generate_repository_report.invoke({
    "repo_path": "C:/Users/jean-noel.diltoer/software/sources/aimsun-python-scripts/FW_Abu_Dhabi/workflow",
    "output_path": "workflow_analysis.xlsx"
})

result = json.loads(result_json)
if result['success']:
    print(f"Report generated: {result['output_path']}")
    print(f"Sheets included: {', '.join(result['sheets'])}")
```

**Via Pulsus Routing:**
```bash
> generate report for repository C:/path/to/repo output to analysis.xlsx
```

### 3. Validate Single File

**Via MCP Tool:**
```python
from agents.shared.tools import mcp_validate_python_file
import json

result_json = mcp_validate_python_file.invoke({
    "file_path": "agents/pulsus/routing/mcp_router.py"
})

result = json.loads(result_json)
print(f"Issues found: {len(result['issues'])}")
for issue in result['issues']:
    print(f"  - {issue}")
print(f"Functions: {result['statistics']['functions']}")
print(f"Lines: {result['statistics']['lines']}")
```

**Via Pulsus Routing:**
```bash
> validate file agents/pulsus/routing/mcp_router.py
```

## Output Examples

### 1. Repository Analysis (JSON)

```json
{
  "success": true,
  "repository": "C:\\path\\to\\repo",
  "files_analyzed": 45,
  "statistics": {
    "total_files": 45,
    "total_functions": 234,
    "total_classes": 28,
    "total_lines": 8923,
    "files_with_issues": 12,
    "compliance_rate": "73.3%",
    "third_party_imports": 18,
    "top_imports": {
      "numpy": 15,
      "pandas": 12,
      "pathlib": 28
    }
  },
  "issues_summary": {
    "total_issues": 35,
    "by_priority": {
      "HIGH": 8,
      "MEDIUM": 27
    },
    "top_issues": [
      {
        "file": "workflow/analysis/network_stats.py",
        "issue": "Missing owner metadata (#owner=...)",
        "priority": "HIGH"
      }
    ]
  },
  "reusability_summary": {
    "total_functions": 234,
    "average_score": 4.2,
    "max_score": 12,
    "top_reusable_functions": [
      {
        "function": "load_network_data",
        "file": "utils/data_loader.py",
        "score": 12,
        "used_in": 8
      }
    ]
  }
}
```

### 2. Excel Report Structure

The generated Excel workbook contains:

**Sheet 1: Summary & Actions**
- Repository health dashboard
- Compliance metrics
- Ownership distribution
- Priority action items

**Sheet 2: Issues & Warnings**
- Prioritized issue list (HIGH/MEDIUM/LOW)
- Color-coded by severity
- Quick links to affected files
- Recommended actions

**Sheet 3: Files Overview**
- All analyzed files
- Status indicators (OK / Issues)
- Metadata (Owner, Type, Category)
- Function count, line count
- Issue summaries

**Sheet 4: Reusability Analysis**
- Function-level scoring (0-15)
- Usage tracking (which files use this function)
- Recommendations (Extract to utils / Refactor / Remove)
- Complexity and documentation metrics

**Sheet 5: Functions & Complexity**
- All functions with qualnames
- Cyclomatic complexity
- Line numbers and lengths
- Unused function detection

**Sheet 6: Function Calls**
- Call graph data
- Caller -> Callee relationships
- Links to function definitions

**Sheet 7: Dashboard**
- Visual charts
- Import distribution
- Category breakdown
- Top dependencies

## Integration with Aimsun Workflows

The analyzer is specifically enhanced for Aimsun Python scripts:

### Aimsun-Specific Features

1. **Header Metadata Parsing**
   ```python
   #atype=analysis
   #owner=john.doe
   ```

2. **Naming Convention Validation**
   - Expected format: `_XX_YY_descriptive_name.py`
   - XX: Category code
   - YY: Script sequence

3. **Structured Docstrings**
   ```python
   """
   ## Description
   This script analyzes network topology.

   ## Inputs
   - network_file: Path to Aimsun network
   - parameters: Analysis configuration

   ## Outputs
   - report.xlsx: Statistical summary
   """
   ```

### Example: Analyze Aimsun Framework

```python
from agents.shared.tools import mcp_generate_repository_report
import json

result_json = mcp_generate_repository_report.invoke({
    "repo_path": r"C:\Users\jean-noel.diltoer\software\sources\aimsun-python-scripts\FW_Abu_Dhabi\workflow",
    "output_path": "FW_Abu_Dhabi_audit.xlsx",
    "ignore_patterns": ["project", "old", "test", "__pycache__"]
})

result = json.loads(result_json)
print(f"Analysis complete: {result['success']}")
print(f"Report: {result['output_path']}")
```

## Advanced Usage

### Programmatic Access

```python
from agents.mcp.helpers.repository_analyzer import RepositoryAnalyzer

# Create analyzer instance
analyzer = RepositoryAnalyzer()

# Perform analysis
result = analyzer.analyze_repository(
    repo_path="C:/path/to/repo",
    ignore_patterns=["test", "__pycache__"]
)

# Access detailed results
for file_data in result["files"]:
    if file_data["issues"]:
        print(f"\n{file_data['file_rel']}:")
        for issue in file_data["issues"]:
            print(f"  - {issue}")

# Generate custom report
analyzer.generate_excel_report(result, "custom_report.xlsx")
```

### Filtering and Querying

```python
import json

result_json = mcp_analyze_repository.invoke({"repo_path": "agents/pulsus"})
result = json.loads(result_json)

# Find high-priority issues
high_priority = [
    issue for issue in result["issues_summary"]["top_issues"]
    if issue["priority"] == "HIGH"
]

# Find highly reusable functions
highly_reusable = [
    fn for fn in result["reusability_summary"]["top_reusable_functions"]
    if fn["score"] >= 10
]

# Find files without owners
unowned_files = [
    f for f in result["files"]
    if "Missing owner metadata" in str(f.get("issues", []))
]
```

## Workflow Integration

### Create Custom Workflows

You can create custom workflows combining analysis with other tools:

**Example: Analyze + Format + Document**
```json
{
    "id": "comprehensive_audit",
    "domain": "quality",
    "action": "full_audit",
    "description": "Analyze repository, format code, and generate documentation",
    "steps": [
        {
            "tool": "mcp_analyze_repository",
            "params": {"repo_path": "${input.repo_path}"}
        },
        {
            "tool": "mcp_format_script",
            "params": {"path": "${input.repo_path}/**/*.py"}
        },
        {
            "tool": "mcp_generate_repository_report",
            "params": {
                "repo_path": "${input.repo_path}",
                "output_path": "${input.output_path}"
            }
        }
    ]
}
```

## Troubleshooting

### Common Issues

**1. "openpyxl not installed"**
```bash
pip install openpyxl
```

**2. "RepositoryAnalyzer not available"**
- Ensure `agents/mcp/helpers/repository_analyzer.py` exists
- Check import paths in `agents/shared/tools.py`

**3. "No Python files found"**
- Verify repository path is correct
- Check `ignore_patterns` - might be excluding too much
- Ensure path contains `.py` files

**4. Missing complexity metrics**
```bash
pip install radon
```

### Performance Tips

- Use `ignore_patterns` to exclude large directories (node_modules, venv)
- For very large repositories (>1000 files), consider analyzing subdirectories
- Excel generation can be slow for large reports - use JSON output for quick checks

## Best Practices

1. **Regular Audits**: Run monthly repository analyses
2. **Pre-Commit Validation**: Use `mcp_validate_python_file` in hooks
3. **Team Dashboards**: Share Excel reports with team for visibility
4. **Track Progress**: Compare reports over time to measure improvement
5. **Focus on High-Value**: Prioritize HIGH severity issues
6. **Reusability First**: Extract functions with score >= 8 to shared utilities

## Future Enhancements

Planned features (see `Pulsus-MCP-TODO.md`):
- HTML visualizations with D3.js dependency graphs
- Automated refactoring suggestions
- Integration with LLM for intelligent code improvements
- Version tracking and diff analysis
- Integration with git history for change impact analysis

## Support

For issues or questions:
- Check `agents/pulsus/routing/README.md` for routing details
- See `agents/pulsus/workflows/Pulsus-MCP-TODO.md` for roadmap
- Review test examples in `agents/mcp/test_script_ops.py`
