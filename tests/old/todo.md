# 📝 TODO List — Pulsus Testing & Validation

## Test Coverage Status (Updated 2025-11-06)

### ✅ COMPLETED Tests (High Coverage)

**Core Routing Components:**
- ✅ `test_discovery_full.py` - **COMPLETE** (19 test classes, ~50 tests)
  - Tool discovery from framework directory
  - Scoring based on domain/action matching (0.0-1.0)
  - Module metadata introspection (__domain__, __action__, __doc__)
  - Docstring matching (domain/action in docstrings)
  - Error handling for malformed modules
  - Empty directory handling
  - Multiple tool scenarios
  - Case sensitivity checks

- ✅ `test_parser_full.py` - **COMPLETE** (13 test classes, ~80 tests)
  - Intent parsing and classification
  - Action guessing and normalization (American→British spelling)
  - Domain detection from hints
  - Confidence calculation (0.5 base, +0.2 action, +0.2 domain, +0.1 both, cap 0.95)
  - Real-world scenario testing
  - Edge cases and boundary conditions
  - Action map and domain hints validation

- ✅ `test_interrupt.py` - **COMPLETE** (2 test classes, 8 tests)
  - Interrupt handler initialization and reset
  - Singleton pattern verification
  - Start/stop listening functionality
  - Integration with long-running operations
  - ESC key interrupt simulation

**Basic Tests:**
- ✅ `test_config.py` - Settings and configuration (2 tests)
- ✅ `test_router.py` - Basic routing decision (1 test)
- ✅ `test_selector.py` - Policy selection (2 tests)
- ✅ `test_ollama_env.py` - Ollama environment validation

### ⚠️ PLACEHOLDER/INCOMPLETE Tests

- ⚠️ `test_compose.py` - Only 1 sanity test (needs expansion)
- ⚠️ `test_discovery.py` - Placeholder (superseded by test_discovery_full.py)
- ⚠️ `test_parse.py` - Placeholder (superseded by test_parser_full.py)
- ⚠️ `test_response_handling.py` - Needs expansion
- ⚠️ `test_environment_paths.py` - Needs expansion

### ❌ MISSING Critical Tests

**Priority 1 (Core Functionality):**
1. ❌ `test_generator_full.py` - LLM fallback generation when no tools match
2. ❌ `test_composer_full.py` - Multi-tool composition and chaining
3. ❌ `test_mcp_tools.py` - All 9 MCP tools (read_script, write_md, add_comments, format_script, scan_structure, search_aimsun_docs, search_qgis_docs, validate_python_code, execute_safe_python)
4. ❌ `test_builtin_analysis_tools.py` - file_analyzer, function_commenter, dependency_documenter, doc_generator, framework_scanner

**Priority 2 (Infrastructure):**
5. ❌ `test_tmp_module_lifecycle.py` - route_tmp/ management and cleanup
6. ❌ `test_validation_pipeline.py` - ruff/mypy/import/dry-run validation
7. ❌ `test_action_logger.py` - MCP action logging and rollback
8. ❌ `test_ui_display.py` - Display manager (info/success/warn/error/kv/section)

**Priority 3 (Integration):**
9. ❌ `test_routing_integration.py` - End-to-end routing scenarios (SELECT/COMPOSE/GENERATE)
10. ❌ `test_workflow_execution.py` - Actual tool invocation with real files
11. ❌ `test_session_context.py` - File context tracking across tools

### 📊 Updated Coverage Metrics
- **Current Coverage:** ~40% (comprehensive parser + discovery, basic routing/selector)
- **Missing Coverage:**
  - Generator: 0%
  - Composer: <5%
  - MCP Tools: 0%
  - Built-in Analysis Tools: 0%
  - Action Logger: 0%
  - Validation Pipeline: 0%
  - Integration: 0%

### 🎯 Recommended Test Implementation Order
1. `test_composer_full.py` - Complete the composition pipeline
2. `test_mcp_tools.py` - Validate all 9 MCP tools
3. `test_builtin_analysis_tools.py` - Validate 7 analysis tools
4. `test_generator_full.py` - Test LLM fallback generation
5. `test_routing_integration.py` - End-to-end scenarios
6. `test_action_logger.py` - MCP logging validation
7. `test_validation_pipeline.py` - Code validation checks
8. `test_tmp_module_lifecycle.py` - Temporary module cleanup

---

## Session 2: Routing & Workflow Tests
- [ ] Create new tests for the **routing system**:
  - selector resolution
  - generator output to `route_tmp/`
  - composer chaining and response checks
- [ ] Implement **workflow_root** and **framework_root** path tests.
- [ ] Simulate different `PULSUS_FRAMEWORK_ROOT` values and confirm discovery.
- [ ] Validate automatic cleanup of temporary modules in `route_tmp/`.

---

## Session 3: Agent Personality Setup
- [x] Create Pulsus **pre-prompt** file in  
      `agents/pulsus/config/preprompt.md`
- [x] Add a **first message** introducing Pulsus to the user session:
  > “👋 Hello, I’m Pulsus — your modular workflow agent...”
- [x] Integrate both into session startup logic.

---

## Session 4: Full Integration Run
- [ ] Execute feature tests via  
      `agents/pulsus/tests/pulsus_launch.bat`
- [ ] Confirm detection of framework_root and workflows_root.
- [ ] Validate logging to `runs/<run_id>/steps.log` and  
      `validation/YYYY-MM-DD/`.
- [ ] Check that temporary modules in `route_tmp/` auto-clean correctly.

---

## Session 5: Documentation & Review
- [ ] Update `pulsus_architecture.md` if directory paths or workflows change.
- [ ] Add notes to `framework/README.md` describing custom tool discovery.
- [ ] Archive validation results in `metrics/` or `validation/YYYY-MM-DD/`.

---

## ✅ Expected Outcome
- Clean separation between **user tools** (framework) and **agent workflows**.  
- Confirmed discovery and routing integrity after refactor.  
- A friendly, self-introducing Pulsus LLM.  
- Reliable launcher-based integration testing pipeline.

---

🧭 **Next step suggestion:**  
After downloading, place this file in your repo at  
`/tasks/todo.md`  
and commit it with message:  
> `docs: add Pulsus routing & framework TODO plan`
