# MCP Natural Language Triggers

This document lists all natural language commands that trigger MCP tools in Pulsus.

## File Analysis (mcp_read_script)

**Syntax**: Use `@` followed by a file path

**Examples**:
- `@C:\path\to\script.py`
- `analyze @/path/to/script.py`
- `read @script.py`
- `@./relative/path/script.py`

**What it does**: Analyzes a Python script and displays:
- Imports
- Classes and methods
- Functions with signatures
- Module documentation
- Statistics

---

## Generate Documentation (mcp_write_md)

**Triggers** (case-insensitive):

### Exact Matches:
- `generate docs`
- `generate doc`
- `create docs`
- `create documentation`
- `make docs`
- `write docs`
- `gen docs`
- `document it`

### Pattern-Based (flexible):
- `generate the docs`
- `create doc for it`
- `make documentation`
- `build docs`
- `write markdown`

**What it does**: Generates comprehensive Markdown documentation (.md file) for the currently analyzed script.

**Requirements**: Must have a script in context (analyze one first with `@path`)

---

## Add Comments/Docstrings (mcp_add_comments)

**Triggers** (case-insensitive):

### Exact Matches:
- `comment functions`
- `add comments`
- `comment all`
- `generate comments`
- `add docstrings`
- `comment code`
- `document functions`
- `comment it`
- `comment this`
- `add comments to it`

### Pattern-Based (flexible):
- `comment the code`
- `add comments to this script`
- `document the functions`
- `generate docstrings`
- Any phrase containing "comment" + target word ("it", "this", "code", "functions", "file", "script")

**What it does**: Generates intelligent docstrings for all functions in the currently analyzed script.

**Requirements**: Must have a script in context (analyze one first with `@path`)

---

## Workflow Example

```
1. [YOU] > @C:\my_project\script.py
   [Pulsus analyzes the script via MCP]

2. [YOU] > comment it
   [Pulsus generates docstrings for all functions]

3. [YOU] > generate docs
   [Pulsus creates comprehensive .md documentation]
```

---

## Technical Details

### Logging
All MCP actions are logged with:
- Tool name and operation
- Target file path
- Parameters used
- Success/failure status
- Error messages (if any)
- File hashes (for write operations)

Logs are stored in: `logs/mcp/`

### Session History
Pulsus maintains context of the currently analyzed script, so you can:
- Ask follow-up questions about the script
- Run multiple MCP operations on the same file
- Use natural language commands like "comment it" or "document it"

---

## Troubleshooting

**"No script currently in context"**
- You need to analyze a script first using `@path` syntax
- Example: `@C:\path\to\script.py`

**Command not recognized**
- Make sure you're using one of the triggers listed above
- For commenting: use "comment it", "add comments", "comment functions", etc.
- For docs: use "generate docs", "create documentation", "document it", etc.

**Want to analyze a different file?**
- Simply use `@path` again with the new file
- The new file becomes the current context

---

## Advanced Features

### MCP Tools Available

All MCP tools can be called programmatically:

1. **mcp_read_script** - Analyze Python scripts
2. **mcp_write_md** - Generate documentation
3. **mcp_add_comments** - Add docstrings
4. **mcp_format_script** - Auto-format code (black, isort, autoflake)
5. **mcp_scan_structure** - Scan directory structure and dependencies

See `agents/shared/tools.py` for full tool definitions.
