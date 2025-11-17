# MCP Test Failure Fixing TODO

**Generated**: 2025-11-11 08:53:41
**Report Based On**: test_results/mcp_test_report_20251111_085341.txt
**Overall Status**: 3 out of 4 test suites failing due to import path inconsistencies
**Success Rate**: 25.0% → Target: 100.0%

---

## Executive Summary

**Root Cause**: Mixed import patterns using `agents.` prefix that doesn't exist in the package structure
**Impact**: Critical - blocks Phase 2 MCP testing and integration
**Estimated Fix Time**: 30 minutes
**Confidence Level**: Very High (95%+)

---

## Priority 1 - Critical (Blocking Tests)

### 1.1 Fix script_ops.py Relative Imports

| Field | Value |
|-------|-------|
| **Priority** | P0 - Critical |
| **Status** | 🔴 Not Started |
| **Document** | `mcp/simple/script_ops.py` |
| **Agent** | jean-claude-mechanic |
| **Lines** | 22-23 |
| **Objective** | Fix relative imports beyond package boundary |
| **Current Code** | `from ...config.settings import load_settings`<br>`from ...ui import display_manager as ui` |
| **Corrected Code** | `from config.settings import load_settings`<br>`from ui import display_manager as ui` |
| **Expected Output** | Phase 2: Simple Domains tests pass |
| **Test Command** | `pytest mcp/tests/test_simple_domains.py -v` |
| **Error Message** | `ImportError: attempted relative import beyond top-level package` |

---

### 1.2 Fix test_script_ops.py Import

| Field | Value |
|-------|-------|
| **Priority** | P0 - Critical |
| **Status** | 🔴 Not Started |
| **Document** | `mcp/tests/test_script_ops.py` |
| **Agent** | jean-claude-mechanic |
| **Line** | 15 |
| **Objective** | Remove incorrect 'agents.' prefix from import |
| **Current Code** | `from agents.shared.tools import mcp_read_script, mcp_write_md, mcp_add_comments` |
| **Corrected Code** | `from shared.tools import mcp_read_script, mcp_write_md, mcp_add_comments` |
| **Expected Output** | Script Operations tests can be collected |
| **Test Command** | `pytest mcp/tests/test_script_ops.py -v` |
| **Error Message** | `ModuleNotFoundError: No module named 'agents'` |

---

### 1.3 Fix test_core_framework.py Import

| Field | Value |
|-------|-------|
| **Priority** | P0 - Critical |
| **Status** | 🔴 Not Started |
| **Document** | `mcp/tests/test_core_framework.py` |
| **Agent** | jean-claude-mechanic |
| **Line** | 16 |
| **Objective** | Remove incorrect 'agents.' prefix from import |
| **Current Code** | `from agents.mcp.core import (MCPBase, MCPResponse, ...)` |
| **Corrected Code** | `from mcp.core import (MCPBase, MCPResponse, ...)` |
| **Expected Output** | Core Framework tests can be collected |
| **Test Command** | `pytest mcp/tests/test_core_framework.py -v` |
| **Error Message** | `ModuleNotFoundError: No module named 'agents'` |

---

## Priority 2 - High (Fix Soon)

### 2.1 Fix repository_ops.py Relative Imports

| Field | Value |
|-------|-------|
| **Priority** | P1 - High |
| **Status** | 🟡 Not Started |
| **Document** | `mcp/simple/repository_ops.py` |
| **Agent** | jean-claude-mechanic |
| **Line** | 23 |
| **Objective** | Fix relative imports beyond package boundary |
| **Current Code** | `from ...mcp.helpers.repository_analyzer import (...)` |
| **Corrected Code** | `from mcp.helpers.repository_analyzer import (...)` |
| **Expected Output** | RepositoryOps can be imported without errors |
| **Test Command** | `python -c "from mcp.simple import RepositoryOps; print('✓')"` |
| **Error Message** | Will fail with `ImportError` when tested |

---

### 2.2 Fix shared/tools.py Import

| Field | Value |
|-------|-------|
| **Priority** | P1 - High |
| **Status** | 🟡 Not Started |
| **Document** | `shared/tools.py` |
| **Agent** | jean-claude-mechanic |
| **Line** | 29 |
| **Objective** | Remove incorrect 'agents.' prefix from import |
| **Current Code** | `from agents.mcp.helpers.script_ops import ScriptOps` |
| **Corrected Code** | `from mcp.helpers.script_ops import ScriptOps` |
| **Expected Output** | Central tool registry works correctly |
| **Test Command** | `python -c "from shared.tools import mcp_read_script; print('✓')"` |
| **Error Message** | `ModuleNotFoundError: No module named 'agents'` |

---

### 2.3 Global Search & Replace for 'agents.' Imports

| Field | Value |
|-------|-------|
| **Priority** | P1 - High |
| **Status** | 🟡 Not Started |
| **Document** | All `*.py` files |
| **Agent** | jean-claude-mechanic |
| **Objective** | Find and fix all remaining 'agents.' import prefixes |
| **Search Pattern** | `from agents\.` |
| **Replace Patterns** | `from agents.mcp.` → `from mcp.`<br>`from agents.shared.` → `from shared.`<br>`from agents.config.` → `from config.` |
| **Expected Output** | Zero occurrences of 'from agents.' in codebase |
| **Verification** | `grep -r "from agents\." --include="*.py"` returns nothing |
| **Estimated Files** | ~60+ files based on initial grep |

---

## Priority 3 - Medium (Code Cleanup)

### 3.1 Remove Path Manipulation from Tests

| Field | Value |
|-------|-------|
| **Priority** | P2 - Medium |
| **Status** | 🟢 Not Started |
| **Document** | Test files with `sys.path.insert()` |
| **Agent** | jean-claude-mechanic |
| **Objective** | Remove unnecessary path manipulation |
| **Current Pattern** | `testudo_root = Path(__file__).parents[3]`<br>`sys.path.insert(0, str(testudo_root))` |
| **Action** | Remove these lines from test files |
| **Expected Output** | Tests run cleanly with proper package structure |
| **Files Affected** | `mcp/tests/test_script_ops.py` (lines 12-13) and similar |

---

### 3.2 Add Package Root __init__.py

| Field | Value |
|-------|-------|
| **Priority** | P2 - Medium |
| **Status** | 🟢 Not Started |
| **Document** | `Pulsus/__init__.py` (root level) |
| **Agent** | jean-claude-architect |
| **Objective** | Clearly define package root and exports |
| **Content** | Package docstring, version, main exports |
| **Expected Output** | Clear package structure documentation |

---

### 3.3 Update Documentation for Import Conventions

| Field | Value |
|-------|-------|
| **Priority** | P2 - Medium |
| **Status** | 🟢 Not Started |
| **Document** | `docs/IMPORT_CONVENTIONS.md` (new) |
| **Agent** | jean-claude-architect |
| **Objective** | Document proper import patterns |
| **Content** | - Use absolute imports for cross-package<br>- Use relative imports within sub-packages<br>- Never use 'agents.' prefix<br>- Package structure diagram |
| **Expected Output** | Clear guidelines for future development |

---

## Verification Strategy

### Step 1: Import Tests

```bash
# Test core imports work
python -c "from mcp.simple import ScriptOps; print('✓ ScriptOps')"
python -c "from mcp.core import MCPBase; print('✓ MCPBase')"
python -c "from shared.tools import mcp_read_script; print('✓ tools')"
```

**Status**: 🔴 Not Started
**Expected Output**: All print checkmarks

---

### Step 2: Individual Test Suites

```bash
pytest mcp/tests/test_simple_domains.py -v
pytest mcp/tests/test_script_ops.py -v
pytest mcp/tests/test_core_framework.py -v
```

**Status**: 🔴 Not Started
**Expected Output**: All tests collected and pass

---

### Step 3: Full Test Suite

```bash
python run_mcp_tests_with_prompts.py
```

**Status**: 🔴 Not Started
**Expected Output**: 4/4 test suites pass (100% success rate)

---

## Quick Fix Script

For rapid execution of Priority 1 fixes:

```bash
# From Pulsus root directory
cd C:\Users\jean-noel.diltoer\software\Atlantis\Testudo\agents\Pulsus

# Fix 1: script_ops.py
# Edit lines 22-23 manually (see section 1.1)

# Fix 2: test_script_ops.py
# Edit line 15 manually (see section 1.2)

# Fix 3: test_core_framework.py
# Edit line 16 manually (see section 1.3)

# Verify
pytest mcp/tests/ -v
```

---

## Success Criteria

- ✅ All 4 test suites pass (currently 1/4)
- ✅ No `ModuleNotFoundError` or `ImportError`
- ✅ Zero uses of `from agents.` pattern
- ✅ All relative imports stay within package boundaries
- ✅ Tests run without sys.path manipulation

**Current Status**: 25% → **Target**: 100%

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking working code | Low | Medium | Only change imports, not logic |
| Missing some import errors | Medium | Low | Use grep to find all occurrences |
| Test failures after fix | Low | Low | Incremental testing strategy |
| Regression in production | Very Low | N/A | This is dev/test code only |

---

## Execution Log

| Timestamp | Task | Status | Agent | Notes |
|-----------|------|--------|-------|-------|
| 2025-11-11 08:53 | Initial Analysis | ✅ Complete | jean-claude-auditor | Comprehensive audit report generated |
| - | Fix 1.1 | 🔴 Pending | jean-claude-mechanic | script_ops.py imports |
| - | Fix 1.2 | 🔴 Pending | jean-claude-mechanic | test_script_ops.py imports |
| - | Fix 1.3 | 🔴 Pending | jean-claude-mechanic | test_core_framework.py imports |
| - | Verify Step 1 | 🔴 Pending | - | Import tests |
| - | Verify Step 2 | 🔴 Pending | - | Individual test suites |
| - | Verify Step 3 | 🔴 Pending | - | Full test suite |

---

## Agent Assignment Summary

- **jean-claude-auditor**: ✅ Analysis complete
- **jean-claude-mechanic**: Import fixes (Priority 1 & 2)
- **jean-claude-architect**: Documentation (Priority 3)

---

## Next Actions

1. **Immediate** (Today): Execute Priority 1 fixes (Tasks 1.1-1.3)
2. **Follow-up** (This week): Execute Priority 2 fixes (Tasks 2.1-2.3)
3. **Enhancement** (Next sprint): Execute Priority 3 improvements (Tasks 3.1-3.3)

**Estimated Total Time**: 30 minutes for Priority 1, 1 hour for all priorities

---

**End of Fixing TODO**
**Document Generated**: 2025-11-11
**Last Updated**: 2025-11-11
**Report Version**: 1.0
