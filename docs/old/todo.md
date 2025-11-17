# Pulsus TODO

**Focus**: Repository intelligence, MCP integration, and unified analysis/documentation workflow  
**Framework Context**: Analysis triggered automatically on configured framework path

---

## 🔴 Critical Tasks

### 1. Framework Path Integration
**Location**: `agents/shared/settings.py` and `agents/shared/repo_loader.py`

- [x] Add `FRAMEWORK_PATH` variable in `settings.py` (points to main repository)
- [x] Allow user to define or override in configuration file
- [ ] Automatically trigger repository analysis on Pulsus startup using `FRAMEWORK_PATH`
- [ ] Detect if `.pulse/` already exists and load existing data
- [ ] Perform full `analyze_repository()` only if:
  - `.pulse/repo_index.json` is missing, or  
  - Framework files have changed (detected via hashes or timestamps)
- [ ] Add console/Qt notification when repository scan completes
- [ ] Add fallback prompt if `FRAMEWORK_PATH` is invalid or missing

> ⚙️ *Purpose:* Pulsus always initializes with full awareness of the framework’s structure, functions, and dependencies.

---

### 2. MCP Repository Analysis
**Location**: `mcp/helpers/repo_tools.py`

- [x] Create `analyze_repository()` to parse functions, classes, and imports
- [x] Save analysis results to `.pulse/repo_index.json`
- [x] Auto-create `.pulse/` folder at repo root
- [ ] Integrate existing MCP commenting and documentation tools
- [ ] Add `mode` parameter: `comment | document | analyze`
- [ ] Support “framework mode” for automatic background analysis
- [ ] Handle unreadable or excluded files gracefully
- [ ] Add quick-scan mode for startup initialization

> 🧩 *Goal:* Merge analysis, commenting, and documentation into one consistent system.
> When Pulsus boots, it analyzes the configured framework automatically, caching structure in `.pulse/`.

---

### 3. Persistent Repository Context
**Location**: `agents/shared/repo_loader.py`

- [x] Implement `load_repo_context()` to load `.pulse/repo_index.json`
- [x] Implement `ensure_repo_context()` for auto re-analysis if missing
- [ ] Add incremental updates (check for modified or new files)
- [ ] Add configuration flag: `auto_analyze_on_start=True`
- [ ] Maintain `.pulse/version.txt` for change detection
- [ ] Log load/analyze events to console for transparency

---

### 4. MCP Tool Integration
**Location**: `agents/shared/tools.py`

- [x] Bind `mcp_analyze_repository` for full scans
- [x] Bind `mcp_load_or_analyze_repo` for lazy loading
- [ ] Bind `mcp_comment_repository` for quick LLM-only feedback
- [ ] Bind `mcp_document_repository` for persistent documentation
- [ ] Add `mode` parameter to all repository tools
- [ ] Standardize JSON schema for framework-level results
- [ ] Add schema validation to ensure MCP consistency

---

### 5. Function Commenting Integration
**Location**: `mcp/helpers/comment_tools.py`

- [x] Reuse short MCP for function-level comments
- [ ] Integrate into repository analysis when mode=`comment`
- [ ] Provide optional comment summaries in `.pulse/functions_index.json`
- [ ] Add “comment-only” startup mode (no writes)
- [ ] Cache ephemeral results in memory for LLM context

> ⚡ *Purpose:* Let Pulsus rapidly comment or inspect the framework without modifying files — ideal for initialization or review.

---

### 6. Documentation Integration
**Location**: `mcp/helpers/doc_tools.py`

- [x] Use existing documentation MCP to generate `.md` outputs
- [ ] Integrate with repository analysis when mode=`document`
- [ ] Auto-create `.pulse/docs/` for each analyzed script
- [ ] Log documentation progress to `.pulse/doc_history.json`
- [ ] Allow user to trigger “document framework” manually or automatically
- [ ] Include coverage stats and missing doc warnings

> 🧠 *Purpose:* When the framework is analyzed, all documented scripts sync automatically with persistent .md files.

---

### 7. Dependency Graph
**Location**: `.pulse/imports_graph.json`

- [ ] Build import relationships between scripts
- [ ] Detect circular dependencies
- [ ] Add file-level dependency scores (fan-in/out)
- [ ] Store graph for future visualization and optimization

---

### 8. Function Signature Index
**Location**: `.pulse/functions_index.json`

- [ ] Extract function names, args, returns, and docstrings
- [ ] Merge comment/documentation data from MCP tools
- [ ] Add file references, line numbers, and status flags
- [ ] Support incremental updates and change detection
- [ ] Link functions to their corresponding `.pulse/cards/`

---

### 9. Script Cards
**Location**: `.pulse/cards/<path>.md`

- [ ] Auto-generate script summaries after framework analysis
- [ ] Include:
  - Script overview
  - Function list with summaries
  - Dependencies and imports
  - Documentation status
  - Optimization notes
- [ ] Sync when `.pulse/repo_index.json` or functions change
- [ ] Maintain consistent Markdown structure for LLM parsing

---

## 🟡 Medium Priority

### 10. Incremental Analysis Engine
**Location**: `agents/shared/repo_loader.py`

- [ ] Compare file hashes with stored `.pulse/repo_index.json`
- [ ] Re-analyze only changed or new scripts
- [ ] Merge updated comments/docs
- [ ] Record each update in `.pulse/history/`
- [ ] Notify user when framework cache refreshes

---

**Next Action:**  
Integrate framework auto-analysis into Pulsus startup sequence using `FRAMEWORK_PATH`.  
Unify MCP commenting and documentation logic under a shared mode system.  
Once Script Cards and persistent context are stable, Pulsus will maintain full awareness of the user’s framework automatically.
