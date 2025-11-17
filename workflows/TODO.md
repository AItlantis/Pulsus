# Workflow Enhancement TODO

## Goal
Unify `@path` analysis to intelligently route between file and repository analysis, with automatic context loading from `.pulsus/` storage.

## Tasks

### 1. Smart Path Detection & Routing
- [x] Create path type detector (`workflows/utils/path_detector.py`)
  - Detect if path is file (.py) or directory
  - Return path type and normalized path
  - Handle edge cases (non-existent paths, symlinks)

### 2. Enhanced Repository Analysis Workflow
- [x] Update `workflows/repository_analysis.json`
  - Add context checking step (load from `.pulsus/` if available)
  - Add option to force re-analysis or use cached
  - Return repository context for downstream use

### 3. Context-Aware File Analysis
- [x] Update `workflows/file_analysis.json`
  - **Step 1**: Check if file belongs to analyzed repository
  - **Step 2**: Load repository analysis from `.pulsus/` if available
  - **Step 3**: Use repository context to enhance file analysis
  - Provide repository health, patterns, and issues as context

### 4. Context-Aware Function Commenting
- [x] Update `workflows/function_commenting.json`
  - **Step 1**: Detect repository from file path
  - **Step 2**: Load repository context from `.pulsus/`
  - **Step 3**: Use repository patterns for better comments
  - Follow existing naming conventions from repo analysis

### 5. Context-Aware Documentation Generation
- [ ] Update `workflows/generate_repo_report.json` (or create new)
  - Load repository analysis context
  - Use repository insights for better documentation
  - Reference high-priority issues and reusable functions

### 6. Unified `@path` Handler
- [x] Create `workflows/tools/analyze/unified_analyzer.py`
  - Entry point for all `@path` requests
  - Route to file or repository analyzer based on path type
  - Automatically load `.pulsus/` context when available
  - **Domain**: `analysis`
  - **Action**: `analyze_path`

### 7. Update Routing Logic
- [x] Modify `routing/mcp_router.py`
  - Add `@path` pattern detection
  - Route `@file.py` and `@directory` through unified analyzer
  - Ensure proper workflow selection

### 8. Context Retrieval Helper
- [x] Create `workflows/utils/context_loader.py`
  - Load repository analysis from `.pulsus/`
  - Detect repository from file path (walk up to find repo root)
  - Return structured context for downstream tools
  - Cache context during session

### 9. Workflow Composition
- [ ] Create composite workflows that chain:
  1. Repository analysis (if not cached)
  2. File analysis (with repo context)
  3. Function commenting (with repo patterns)
  4. Documentation generation (with repo insights)

### 10. Testing & Validation
- [x] Test unified `@path` with files
- [x] Test unified `@path` with directories
- [x] Test context loading from `.pulsus/`
- [ ] Test workflow composition
- [ ] Verify backward compatibility

## Implementation Priority

### Phase 1: Foundation (High Priority)
1. Path detector utility
2. Context loader utility
3. Unified analyzer tool

### Phase 2: Workflow Updates (High Priority)
4. Update file_analysis.json with context loading
5. Update function_commenting.json with repo patterns
6. Update repository_analysis.json with caching

### Phase 3: Integration (Medium Priority)
7. Update routing for `@path` detection
8. Create workflow compositions
9. Update documentation generation

### Phase 4: Polish (Low Priority)
10. Comprehensive testing
11. Performance optimization
12. User documentation

## Expected User Experience

**Before:**
```
[YOU] > @C:\path\to\file.py
  → Analyzes file in isolation (no context)

[YOU] > run repository analysis on framework
  → Analyzes repository, saves to .pulsus/
```

**After:**
```
[YOU] > @C:\path\to\repository
  → Detects directory
  → Runs repository analysis
  → Saves to .pulsus/

[YOU] > @C:\path\to\repository\file.py
  → Detects file
  → Loads repository analysis from .pulsus/
  → Analyzes file WITH repository context
  → Provides insights: "This file has 3 high-priority issues vs repo average of 1.2"
  → Suggests: "Consider extracting filter_by_date() (reusability score: 11/15)"

[YOU] > generate comments for @C:\path\to\file.py
  → Loads repository patterns from .pulsus/
  → Generates comments following repo conventions
  → Uses repo-specific terminology and patterns
```

## Success Criteria

- ✅ Single `@path` syntax works for both files and directories
- ✅ Repository context automatically loaded from `.pulsus/` when available
- ✅ File analysis enhanced with repository insights
- ✅ Function comments follow repository patterns
- ✅ No breaking changes to existing workflows
- ✅ All tests pass
