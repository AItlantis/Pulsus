# Phase 2: Classic MCP Domains - Implementation Plan

**Version:** 1.0
**Date:** November 10, 2025
**Status:** Planning → Ready for Implementation
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Mechanic
**Support Agents:** Jean-Claude Auditor (testing), Jean-Claude Architect (review)

---

## Executive Summary

Phase 2 builds on the completed Phase 1 Core Framework to create production-ready MCP domains (Tier 1: Classic). This phase involves:

1. **Migrating existing helpers** to the new MCPBase structure
2. **Creating new MCP domains** for common operations
3. **Building LangChain integration** for tool discovery
4. **Comprehensive testing** of all domains

**Key Goal:** Transform standalone helpers into a cohesive, safe, and discoverable MCP domain ecosystem.

---

## Prerequisites

### Phase 1 Complete ✅
- MCPBase and MCPResponse implemented
- All 5 safety decorators functional
- SafetyPolicy enforcement working
- MCPLogger with SafeNet integration
- Test suite with 100% pass rate
- Complete documentation

### Required Knowledge
- Understanding of MCPBase architecture
- Familiarity with safety decorators
- Knowledge of existing helper functions
- LangChain StructuredTool basics

---

## Existing Helpers Inventory

### Current Status (mcp/helpers/)

| Helper | Lines | Status | Migration Priority |
|--------|-------|--------|-------------------|
| script_ops.py | ~400 | Functional | 🔴 High |
| repository_manager.py | ~300 | Functional | 🔴 High |
| action_logger.py | ~200 | Functional | 🟠 Medium |
| script_manager.py | ~250 | Functional | 🟡 Low (duplicate?) |
| repository_analyzer.py | ~350 | Functional | 🟠 Medium |
| data_analyzer.py | ~200 | Functional | 🟠 Medium |
| model_inspector.py | ~150 | Functional | 🟡 Low |
| layer_manager.py | ~150 | Functional | 🟡 Low |
| pulse_generator.py | ~100 | Utility | 🟢 Very Low |

**Total:** 9 helpers, ~2,100 lines of code

### Analysis

**Immediate Migration (High Priority):**
1. **script_ops.py** - Core functionality, frequently used
2. **repository_manager.py** - Key for workflow operations

**Second Wave (Medium Priority):**
3. **action_logger.py** - Integrate with MCPLogger
4. **repository_analyzer.py** - Merge with repository_manager?
5. **data_analyzer.py** - Useful for data operations

**Later/Optional (Low Priority):**
6. **script_manager.py** - Check if duplicate of script_ops
7. **model_inspector.py** - Platform-specific (Aimsun/QGIS)
8. **layer_manager.py** - Platform-specific (QGIS)
9. **pulse_generator.py** - Utility, may not need migration

---

## Phase 2 Deliverables

### New Directory Structure

```
agents/Pulsus/
├── mcp/
│   ├── core/                      ✅ Phase 1 Complete
│   │   ├── base.py
│   │   ├── decorators.py
│   │   ├── policy.py
│   │   ├── logger.py
│   │   ├── types.py
│   │   └── README.md
│   │
│   ├── simple/                    ⭐ Phase 2 NEW
│   │   ├── __init__.py           (exports all domains)
│   │   ├── script_ops.py         (migrated + enhanced)
│   │   ├── repository_ops.py     (migrated + merged)
│   │   ├── file_manager.py       (NEW - file operations)
│   │   ├── data_reader.py        (NEW - data loading)
│   │   ├── text_processor.py     (NEW - text operations)
│   │   └── README.md             (domain catalog)
│   │
│   ├── helpers/                   📦 Phase 2 Archive
│   │   └── [moved to simple/]    (keep for backup)
│   │
│   └── tests/
│       ├── test_core_framework.py          ✅ Phase 1
│       ├── test_simple_domains.py          ⭐ Phase 2 NEW
│       └── test_langchain_integration.py   ⭐ Phase 2 NEW
│
├── langchain/                     ⭐ Phase 2 NEW
│   ├── __init__.py
│   ├── tool_adapter.py           (MCP → LangChain converter)
│   ├── tool_registry.py          (auto-discovery)
│   └── README.md                 (integration guide)
│
├── run_phase2_tests.py            ⭐ Phase 2 NEW
└── docs/
    ├── PHASE1_COMPLETE.md         ✅ Complete
    ├── PHASE2_PLAN.md            (this file)
    └── PHASE2_COMPLETE.md        (deliverable)
```

---

## Task Breakdown

### Week 1: Core Migrations

#### Task 1.1: Migrate script_ops.py to MCPBase
**Duration:** 2 days
**Agent:** Jean-Claude Mechanic
**Priority:** 🔴 Critical

**Actions:**
1. Create `mcp/simple/script_ops.py` extending MCPBase
2. Migrate all methods from `mcp/helpers/script_ops.py`
3. Add appropriate safety decorators:
   - `read_script()` → `@read_only`
   - `write_script()` → `@write_safe`
   - `format_script()` → `@write_safe`
   - `comment_functions()` → `@write_safe`
4. Update method signatures to return `MCPResponse`
5. Add trace messages for debugging
6. Remove old path validation (use MCPBase validation)
7. Test all methods

**Acceptance Criteria:**
- All methods return MCPResponse
- Safety decorators applied correctly
- Trace messages added
- No breaking changes to API
- Tests pass

#### Task 1.2: Migrate repository_manager.py to MCPBase
**Duration:** 2 days
**Agent:** Jean-Claude Mechanic
**Priority:** 🔴 Critical

**Actions:**
1. Create `mcp/simple/repository_ops.py` extending MCPBase
2. Merge functionality from `repository_manager.py` + `repository_analyzer.py`
3. Add safety decorators:
   - `scan_repository()` → `@read_only`
   - `analyze_dependencies()` → `@read_only`
   - `generate_report()` → `@write_safe`
4. Update to use MCPResponse
5. Add caching for expensive operations (`@cached`)
6. Test integration

**Acceptance Criteria:**
- Combines best of both repository helpers
- All methods decorated
- Caching implemented for scan operations
- Tests pass

#### Task 1.3: Create file_manager.py (NEW)
**Duration:** 1 day
**Agent:** Jean-Claude Mechanic
**Priority:** 🟠 High

**Actions:**
1. Create `mcp/simple/file_manager.py` extending MCPBase
2. Implement methods:
   - `create_file(path, content)` → `@write_safe`
   - `delete_file(path)` → `@write_safe`
   - `move_file(source, dest)` → `@write_safe`
   - `copy_file(source, dest)` → `@write_safe`
   - `list_files(directory, pattern)` → `@read_only`
   - `get_file_info(path)` → `@read_only`
3. Add input validation
4. Implement error handling
5. Write unit tests

**Acceptance Criteria:**
- All CRUD operations for files
- Safe path validation
- Error handling for permissions, missing files
- Tests pass

---

### Week 2: New Domains & LangChain Integration

#### Task 2.1: Create data_reader.py (NEW)
**Duration:** 2 days
**Agent:** Jean-Claude Mechanic
**Priority:** 🟠 High

**Actions:**
1. Create `mcp/simple/data_reader.py` extending MCPBase
2. Implement methods:
   - `read_csv(path, **kwargs)` → `@read_only @cached`
   - `read_json(path)` → `@read_only @cached`
   - `read_parquet(path)` → `@read_only @cached`
   - `read_excel(path, sheet)` → `@read_only @cached`
   - `query_dataframe(df, query)` → `@read_only`
   - `get_schema(path)` → `@read_only @cached`
3. Use pandas for data operations
4. Add caching (TTL: 5 minutes)
5. Write tests with sample data files

**Acceptance Criteria:**
- Supports CSV, JSON, Parquet, Excel
- Caching works correctly
- Schema introspection available
- Tests with real files

#### Task 2.2: Create text_processor.py (NEW)
**Duration:** 1 day
**Agent:** Jean-Claude Mechanic
**Priority:** 🟡 Medium

**Actions:**
1. Create `mcp/simple/text_processor.py` extending MCPBase
2. Implement methods:
   - `search_text(text, pattern, regex)` → `@read_only`
   - `replace_text(text, old, new)` → `@read_only`
   - `extract_patterns(text, pattern)` → `@read_only`
   - `count_words(text)` → `@read_only @cached`
   - `split_text(text, delimiter)` → `@read_only`
3. Support regex patterns
4. Add input validation
5. Write tests

**Acceptance Criteria:**
- Text search/replace working
- Regex support
- Tests with various patterns

#### Task 2.3: Build LangChain Tool Adapter
**Duration:** 2 days
**Agent:** Jean-Claude Mechanic
**Priority:** 🔴 Critical

**Actions:**
1. Create `langchain/tool_adapter.py`
2. Implement `mcp_to_langchain_tool(mcp_class)`:
   ```python
   from langchain_core.tools import StructuredTool
   from mcp.core import MCPBase
   from pydantic import BaseModel, Field, create_model

   def mcp_to_langchain_tool(mcp_class: type[MCPBase]) -> StructuredTool:
       """Convert MCPBase to LangChain StructuredTool"""
       instance = mcp_class()
       capabilities = instance.get_capabilities()

       # Generate Pydantic model for args
       args_schema = _generate_args_schema(capabilities)

       def execute_wrapper(**kwargs):
           action = kwargs.pop('action', None)
           response = instance.execute(action, **kwargs)
           return response.to_dict()

       return StructuredTool(
           name=mcp_class.__name__,
           description=instance.__doc__ or f"MCP domain: {mcp_class.__name__}",
           func=execute_wrapper,
           args_schema=args_schema
       )
   ```
3. Implement `_generate_args_schema()` using Pydantic
4. Create `tool_registry.py` for auto-discovery
5. Write tests for conversion

**Acceptance Criteria:**
- All MCP domains convert to LangChain tools
- Args schema generated correctly
- Tests verify LangChain compatibility

---

### Week 3: Testing, Documentation & Integration

#### Task 3.1: Integration Testing
**Duration:** 2 days
**Agent:** Jean-Claude Auditor
**Priority:** 🔴 Critical

**Actions:**
1. Create `mcp/tests/test_simple_domains.py`:
   - Test each domain's methods
   - Test safety decorator enforcement
   - Test error handling
   - Test MCPResponse format
2. Create `mcp/tests/test_langchain_integration.py`:
   - Test tool conversion
   - Test LangChain invocation
   - Test args schema validation
3. Run full test suite
4. Achieve 90%+ coverage for new code

**Test Matrix:**

| Domain | Read Methods | Write Methods | Coverage Target |
|--------|-------------|---------------|-----------------|
| ScriptOps | 3 | 4 | 95% |
| RepositoryOps | 5 | 2 | 90% |
| FileManager | 2 | 4 | 95% |
| DataReader | 6 | 0 | 90% |
| TextProcessor | 5 | 0 | 85% |

**Acceptance Criteria:**
- 90%+ test coverage
- All edge cases covered
- LangChain integration tested
- Performance benchmarks met

#### Task 3.2: Create Domain Catalog Documentation
**Duration:** 1 day
**Agent:** Jean-Claude Architect
**Priority:** 🟠 High

**Actions:**
1. Create `mcp/simple/README.md`:
   - Overview of all domains
   - Capability matrix
   - Usage examples
   - Safety level reference
2. Create `langchain/README.md`:
   - Integration guide
   - Conversion examples
   - Registry usage
3. Update main README.md

**Acceptance Criteria:**
- Complete domain catalog
- LangChain guide with examples
- Clear usage documentation

#### Task 3.3: Backward Compatibility & Migration
**Duration:** 1 day
**Agent:** Jean-Claude Mechanic
**Priority:** 🟠 High

**Actions:**
1. Create compatibility shims in `mcp/helpers/`:
   ```python
   # mcp/helpers/script_ops.py (compatibility shim)
   from mcp.simple.script_ops import ScriptOps as _ScriptOps
   import warnings

   class ScriptOps(_ScriptOps):
       def __init__(self, *args, **kwargs):
           warnings.warn(
               "mcp.helpers.ScriptOps is deprecated, "
               "use mcp.simple.ScriptOps instead",
               DeprecationWarning
           )
           super().__init__(*args, **kwargs)
   ```
2. Update imports in existing code
3. Add deprecation notices
4. Create migration guide

**Acceptance Criteria:**
- Old imports still work with warnings
- Migration guide available
- No breaking changes

#### Task 3.4: Update Routing Integration
**Duration:** 1 day
**Agent:** Jean-Claude Mechanic
**Priority:** 🟠 High

**Actions:**
1. Update `routing/tool_discovery.py`:
   - Auto-discover MCP domains from `mcp.simple`
   - Register capabilities
   - Integrate with existing routing
2. Update `routing/router.py`:
   - Support MCPBase execution
   - Handle MCPResponse format
3. Test routing with new domains

**Acceptance Criteria:**
- Router discovers new domains automatically
- Routing works with MCPBase
- Existing workflows unaffected

---

## Success Criteria

### Functional Requirements ✅

- [ ] **5+ Classic MCP Domains Operational**
  - ScriptOps ✅
  - RepositoryOps ✅
  - FileManager ✅
  - DataReader ✅
  - TextProcessor ✅

- [ ] **All Domains Use MCPBase**
  - Extend MCPBase
  - Return MCPResponse
  - Use safety decorators
  - Implement get_capabilities()

- [ ] **LangChain Integration Complete**
  - All domains convert to StructuredTool
  - Args schema generation works
  - Tool registry auto-discovers

- [ ] **Safety Enforcement**
  - All write operations require confirmation
  - Type validation working
  - Execution modes respected

### Quality Requirements ✅

- [ ] **Test Coverage ≥ 90%**
  - Unit tests for all methods
  - Integration tests for LangChain
  - Edge case coverage

- [ ] **Documentation Complete**
  - Domain catalog (README.md)
  - LangChain integration guide
  - Migration guide
  - API reference

- [ ] **Backward Compatibility**
  - Old imports work with warnings
  - No breaking changes
  - Migration path documented

### Performance Requirements ✅

- [ ] **Execution Times**
  - Read operations: <100ms average
  - Write operations: <250ms average
  - Cached reads: <10ms

- [ ] **Resource Usage**
  - Memory: <100MB for typical usage
  - Caching: Configurable TTL

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing workflows | High | Medium | Compatibility shims, thorough testing |
| LangChain API changes | Medium | Low | Pin version, abstract integration |
| Performance regression | Medium | Low | Benchmarks, caching |
| Incomplete migration | High | Low | Prioritize helpers, phase rollout |
| Test coverage gaps | Medium | Medium | Code review, coverage reports |

---

## Dependencies

### External Libraries

```toml
# Add to pyproject.toml
[project]
dependencies = [
    "langchain-core>=0.1.0",
    "pydantic>=2.0",
    "pandas>=2.0",          # for data_reader
    "pyarrow>=10.0",        # for parquet support
    "openpyxl>=3.0",        # for Excel support
]
```

### Internal Dependencies

- Phase 1: Core MCP Framework (COMPLETE ✅)
- Pulsus routing system (existing)
- UI display manager (existing)

---

## Rollout Strategy

### Phase 2A: Core Migrations (Week 1)
1. Migrate ScriptOps
2. Migrate RepositoryOps
3. Create FileManager
4. **Checkpoint:** Test migrations, verify backward compatibility

### Phase 2B: New Domains (Week 2)
1. Create DataReader
2. Create TextProcessor
3. Build LangChain adapter
4. **Checkpoint:** Test LangChain integration

### Phase 2C: Integration & Testing (Week 3)
1. Integration tests
2. Documentation
3. Routing updates
4. **Final Review:** Complete system test

### Rollback Plan

If issues arise:
1. Keep `mcp/helpers/` as fallback
2. Use compatibility shims to redirect
3. Fix issues incrementally
4. Don't delete old code until Phase 2 validated

---

## Monitoring & Validation

### Test Metrics

```bash
# Run all Phase 2 tests
python run_phase2_tests.py

# Coverage report
pytest mcp/tests/test_simple_domains.py --cov=mcp.simple --cov-report=html

# LangChain integration
pytest mcp/tests/test_langchain_integration.py -v
```

### Success Indicators

- ✅ All tests pass (24+ tests from Phase 1, 30+ new tests)
- ✅ Coverage ≥ 90% for new code
- ✅ LangChain tools discoverable
- ✅ No performance regressions
- ✅ Documentation complete

---

## Next Phase Preview

### Phase 3: Workflow MCP Domains (Tier 2)

**Focus:** Multi-step processes with LLM integration

**Key Deliverables:**
- RepositoryAnalyzer workflow (multi-step analysis)
- CodeRefactorer workflow (plan → execute → validate)
- DocumentationGenerator workflow (scan → analyze → generate)
- Workflow JSON definitions
- LLM connector (Ollama/OpenAI/Claude)

**Build On:**
- Classic domains from Phase 2
- Composer pattern from routing
- LangChain StructuredTool format

---

## Appendix

### A. Command Reference

```bash
# Development
cd agents/Pulsus

# Run tests
python run_phase2_tests.py

# Test specific domain
pytest mcp/tests/test_simple_domains.py::TestScriptOps -v

# Test LangChain integration
pytest mcp/tests/test_langchain_integration.py -v

# Coverage report
pytest --cov=mcp.simple --cov-report=term-missing

# Type check
mypy mcp/simple/ --strict

# Lint
ruff check mcp/simple/
```

### B. File Templates

**Template: New MCP Domain**

```python
"""
[Domain Name] MCP Helper

Provides [description] operations.
"""

from mcp.core import MCPBase, MCPResponse, read_only, write_safe
from pathlib import Path
from typing import Any, Dict

class [DomainName](MCPBase):
    """
    [Domain description]

    Capabilities:
    - [capability 1]
    - [capability 2]
    """

    def __init__(self):
        super().__init__()

    @read_only
    def [read_method](self, param: str) -> MCPResponse:
        """
        [Method description]

        Args:
            param: [parameter description]

        Returns:
            MCPResponse with [data description]
        """
        response = MCPResponse.success_response()
        response.add_trace('Starting operation')

        try:
            # Implementation
            result = self._do_work(param)
            response.data = result
            response.add_trace('Operation complete')
            return response
        except Exception as e:
            response.set_error(str(e))
            return response

    @write_safe
    def [write_method](self, param: str) -> MCPResponse:
        """Write operation with confirmation"""
        # Implementation
        pass
```

---

**Document Version:** 1.0
**Last Updated:** November 10, 2025
**Author:** Jean-Claude Architect + Jean-Claude Mechanic
**Status:** Ready for Implementation

**Next Action:** Begin Task 1.1 - Migrate script_ops.py

---

**Phase 2: Classic MCP Domains - Let's Build! 🚀**
