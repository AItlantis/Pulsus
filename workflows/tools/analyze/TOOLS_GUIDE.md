# Pulsus Analysis Tools - Quick Reference

This guide provides a quick reference for using the built-in analysis tools in Pulsus.

## Available Tools

### 1. File Analyzer
**Command**: `@path/to/file.py` or `analyze @path/to/file.py`

Analyzes Python files and provides comprehensive structure analysis.

**What it does:**
- Extracts functions, classes, and imports using AST
- Detects module metadata (__domain__, __action__)
- Generates LLM-powered understanding of script purpose
- Checks for existing documentation
- Saves analysis to session context

**Output:**
- Module description and metadata
- List of imports
- Classes with methods and docstrings
- Functions with signatures and docstrings
- File statistics (class count, function count)
- LLM-generated understanding

**Example:**
```
@C:\project\utils.py
```

---

### 2. Function Commenter
**Command**: `comment functions` or `comment functions @path/to/file.py`

Generates detailed Google-style docstrings for all functions in a Python file.

**What it does:**
- Parses all function definitions in the file
- Analyzes function signatures, parameters, and return types
- Uses LLM to generate comprehensive docstrings
- Formats comments with proper indentation
- Displays preview of each generated comment

**Output:**
- Formatted docstrings for each function
- Line numbers with clickable links
- Function count summary
- Copy-ready formatted comments

**Example:**
```
# After analyzing a file
comment functions

# Or specify directly
comment functions @C:\project\helpers.py
```

**Generated Docstring Format:**
```python
"""
Brief one-line description.

Detailed explanation of what the function does and why.

Args:
    param1 (type): Description of param1
    param2 (type): Description of param2

Returns:
    type: Description of return value

Raises:
    ExceptionType: When this exception is raised
"""
```

---

### 3. Dependency Documenter
**Command**: `analyze dependencies` or `document dependencies @path/to/file.py`

Identifies and documents local script dependencies with descriptions.

**What it does:**
- Extracts all import statements
- Distinguishes local files from external libraries
- Resolves dependency paths automatically
- Analyzes each dependency (functions, classes)
- Uses LLM to generate descriptions of dependencies
- Lists external dependencies separately

**Output:**
- List of local dependencies with descriptions
- Clickable links to dependency files
- Key functions and classes in each dependency
- Import statements for each dependency
- Separate list of external library dependencies

**Example:**
```
# After analyzing a file
analyze dependencies

# Or specify directly
document dependencies @C:\project\main.py
```

**Output Example:**
```
Module: agents.pulsus.ui.display_manager
File: display_manager.py
Import: from agents.pulsus.ui import display_manager as ui

This module provides UI display management functionality for the
pulsus agent system, including colored output, formatted sections,
and clickable file paths for terminal display.

Key Functions (15): info, error, warn, success, section, kv, ...
Key Classes (0):
```

---

### 4. Documentation Generator
**Command**: `generate docs`

Creates comprehensive Markdown documentation file (.md) for the analyzed script.

**What it does:**
- Uses session context from file analysis
- Generates structured Markdown documentation
- Creates or enhances existing .md file
- Includes overview, functions, classes, dependencies
- Uses LLM for comprehensive documentation

**Output:**
- Creates `filename.md` next to the Python file
- Markdown-formatted documentation
- Ready for version control and sharing

**Example:**
```
# After analyzing a file
generate docs
```

---

## Suggested Workflow

### Complete Documentation Workflow

1. **Analyze the file:**
   ```
   @C:\project\mymodule.py
   ```
   *Extracts structure and generates understanding*

2. **Generate function comments:**
   ```
   comment functions
   ```
   *Creates docstrings for all functions*

3. **Document dependencies:**
   ```
   analyze dependencies
   ```
   *Identifies and documents imports*

4. **Generate full documentation:**
   ```
   generate docs
   ```
   *Creates comprehensive .md file*

5. **Review and edit:**
   - Copy generated docstrings to source file
   - Review and adjust descriptions
   - Commit documentation to repository

---

## Tips and Best Practices

### Session Context
- After analyzing a file with `@path`, it becomes the "current file"
- Subsequent commands like `comment functions` use this context
- No need to repeat the file path

### Interrupting Operations
- Press **ESC** to interrupt long-running operations
- All tools support graceful interruption
- Partial results are preserved

### Clickable Links
- File paths and line numbers are clickable in most modern terminals
- Click to jump directly to the code in your editor
- Works in VS Code, Windows Terminal, iTerm2, etc.

### LLM Requirements
- Tools use the configured Ollama model
- Ensure Ollama is running: `ollama serve`
- Check model setting in `config/settings.py`
- Default model: `qwen3-coder:30b`

### File Paths
- Use `@path` syntax for explicit file specification
- Supports both Windows (`C:\path\file.py`) and Unix (`/path/file.py`) paths
- Paths with spaces are handled automatically

---

## Troubleshooting

### Tool Not Found
**Problem:** "No tool found for this action"

**Solutions:**
1. Check tool discovery: Tools should be in `workflows/tools/`
2. Verify `__domain__` and `__action__` metadata in tool file
3. Check spelling of command
4. Use exact phrases: `comment functions`, `analyze dependencies`

### LLM Not Responding
**Problem:** Tool hangs or times out

**Solutions:**
1. Check if Ollama is running: `ollama list`
2. Verify model is available: `ollama pull qwen3-coder:30b`
3. Check network/host configuration in settings
4. Press ESC to interrupt and try again

### Encoding Errors
**Problem:** Unicode character errors in console

**Solutions:**
1. Tools automatically handle encoding issues
2. Output should work in modern terminals
3. Use UTF-8 compatible terminal if possible

### No Local Dependencies Found
**Problem:** "No local script dependencies found"

**Solutions:**
1. File may only use external libraries (this is normal)
2. Check if imports use correct module paths
3. Verify files exist in the project structure

---

## Integration with Other Tools

### Chaining Commands
You can chain multiple operations in sequence:
```
@C:\project\utils.py
comment functions
analyze dependencies
generate docs
```

### Follow-up Questions
After any analysis, you can ask natural language questions:
```
what does the parse_input function do?
how are errors handled?
what libraries does this depend on?
```

### Custom Workflows
Create custom workflows by combining tools:
- Analyze → Comment → Document (complete documentation)
- Analyze → Dependencies → Refactor (understanding dependencies)
- Analyze → Questions → Implement (understanding before changes)

---

## Advanced Usage

### Custom Tool Creation
To create your own analysis tools, see the main [README.md](../../../README.md)

Key points:
- Place tools in `workflows/tools/{domain}/`
- Define `__domain__` and `__action__` metadata
- Implement `handle(text: str) -> Dict[str, Any]` function
- Use `ui.display_manager` for consistent output
- Add interrupt handling for long operations

### Extending Existing Tools
You can extend the built-in tools:
- Fork the tool file
- Add your custom logic
- Update the docstring for better discovery
- Test with the discovery system

---

## Getting Help

- Main documentation: [workflows/README.md](../../README.md)
- Architecture docs: Check `docs/` directory
- Issue reporting: Project issue tracker
- Example tools: Browse `workflows/tools/` directory

---

**Last Updated:** 2025-11-03
**Pulsus Version:** 1.0
**Tools:** file_analyzer, function_commenter, dependency_documenter, doc_generator
