# Pulsus MCP — High-Level TODO

**Version:** 1.0
**Last Updated:** November 2025
**Status:** Planning → Implementation

---

## 📚 Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Unified Integration Plan** | Complete architecture & implementation roadmap | `docs/PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` |
| **Framework Integration** | Abu Dhabi 8-step domain framework adapter | `docs/FRAMEWORK_INTEGRATION_ADDENDUM.md` |
| **TODO V3 Part 1** | Phases 1-5 (Core → Execution) | `docs/MCP-PULSUS-TODO-V3-part1.md` |
| **TODO V3 Part 2** | Phases 6-10 (Preferences → Testing) | `docs/MCP-PULSUS-TODO-V3-part2.md` |

---

## 🎯 Priority Levels

- 🔴 **Critical** - Blocking / Must have
- 🟠 **High** - Important / Should have
- 🟡 **Medium** - Nice to have / Could have
- 🟢 **Low** - Future enhancement / Won't have (for now)

---

## 📋 Phase-by-Phase Roadmap

### 🏗️ Phase 0: Pre-Implementation (Current)

#### Documentation & Planning
- [x] 🔴 Explore Pulsus architecture
  - **Status:** ✅ Complete
  - **Output:** Architecture analysis report
  - **Agent:** Jean-Claude Architect

- [x] 🔴 Create unified integration plan
  - **Status:** ✅ Complete
  - **Document:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`
  - **Agent:** Jean-Claude Architect + Jean-Claude MCP

- [x] 🔴 Create framework integration addendum
  - **Status:** ✅ Complete
  - **Document:** `FRAMEWORK_INTEGRATION_ADDENDUM.md`
  - **Agent:** Jean-Claude MCP

- [x] 🔴 Setup Jean-Claude agents
  - **Status:** ✅ Complete
  - **Location:** `.claude/agents/`
  - **Agents:** Architect, Mechanic, Auditor, Science, Designer, Domain, MCP (new)

- [x] 🟠 Architecture review meeting
  - **Status:** ✅ Complete
  - **Action:** Review unified plan with team
  - **Output:** Architecture documented and ready for implementation
  - **Note:** Comprehensive plan validated in `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`

- [x] 🟠 Setup development environment
  - **Status:** ✅ Complete
  - **Action:** Created dev configuration, CI/CD skeleton
  - **Tools:** Git, GitHub Actions, pytest, mypy, ruff
  - **Output:**
    - `pyproject.toml` with tool configurations
    - `.github/workflows/test.yml` for CI/CD
    - `requirements.txt` and `requirements-dev.txt`
    - `README.md` with project overview

---

### 🧱 Phase 1: Core MCP Framework (Weeks 1-4)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 1
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Mechanic + Jean-Claude Architect

#### Tasks

- [x] 🔴 Audit current Pulsus architecture
  - **Action:** Run comprehensive architecture audit
  - **Agent:** Jean-Claude Architect
  - **Command:** `use jean-claude-architect to audit Pulsus architecture`
  - **Deliverable:** Architecture audit report with gaps analysis

- [x] 🔴 Design MCPBase class structure
  - **Action:** Create base class specification
  - **Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 1 → MCPBase
  - **Agent:** Jean-Claude Architect
  - **Output:** `docs/MCPBase_SPECIFICATION.md`

- [x] 🔴 Implement MCPBase + MCPResponse
  - **Action:** Create core base classes
  - **File:** `pulsus/mcp/core/base.py`
  - **Agent:** Jean-Claude Mechanic
  - **Requirements:**
    - MCPBase abstract class
    - MCPResponse dataclass
    - Success/error factory methods
    - to_dict() serialization

- [x] 🔴 Implement safety decorators
  - **Action:** Create decorator system
  - **File:** `pulsus/mcp/core/decorators.py`
  - **Agent:** Jean-Claude Mechanic
  - **Decorators:**
    - `@read_only`
    - `@write_safe`
    - `@restricted_write(types, platform)`
    - `@transactional(rollback)`
    - `@cached(ttl)`

- [x] 🔴 Implement SafetyPolicy system
  - **Action:** Create policy enforcement
  - **File:** `pulsus/mcp/core/policy.py`
  - **Agent:** Jean-Claude Mechanic
  - **Components:**
    - ExecutionMode enum (PLAN, EXECUTE, UNSAFE)
    - SafetyLevel enum
    - OperationPolicy class
    - SafetyPolicy enforcer

- [x] 🔴 Create type definitions
  - **Action:** Define shared types
  - **File:** `pulsus/mcp/core/types.py`
  - **Agent:** Jean-Claude Mechanic
  - **Types:** Action schemas, parameter types, response types

- [x] 🟠 Write unit tests for core framework
  - **Action:** Create test suite
  - **Files:** `tests/unit/test_core.py`, `tests/unit/test_decorators.py`
  - **Agent:** Jean-Claude Auditor
  - **Target:** 90%+ coverage

- [x] 🟠 Create core framework documentation
  - **Action:** Document core classes and patterns
  - **File:** `docs/MCP_CORE_FRAMEWORK.md`
  - **Agent:** Jean-Claude Architect
  - **Sections:** Architecture, usage patterns, examples

#### Milestone 1: Core Framework Complete ✅
**Acceptance Criteria:**
- MCPBase can be subclassed
- All decorators functional
- SafetyPolicy enforces rules
- Tests pass with 90%+ coverage

---

### 🔧 Phase 2: Classic MCP Domains (Weeks 5-8)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 2
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

- [x] 🔴 Migrate existing MCP helpers
  - **Action:** Refactor current helpers to new structure
  - **Source:** `pulsus/mcp/helpers/`
  - **Target:** `pulsus/mcp/simple/`
  - **Agent:** Jean-Claude Mechanic
  - **Helpers to migrate:**
    - script_ops.py
    - repository_manager.py
    - action_logger.py
    - layer_manager.py
    - model_inspector.py

- [x] 🔴 Implement ScriptOps (Tier 1)
  - **Action:** Refactor with new MCPBase + decorators
  - **File:** `pulsus/mcp/simple/script_ops.py`
  - **Agent:** Jean-Claude Mechanic
  - **Actions:**
    - read_script (@read_only)
    - write_script (@write_safe)
    - format_script (@write_safe)
    - comment_functions (@write_safe)

- [x] 🔴 Implement FileManager (Tier 1)
  - **Action:** Create file operations domain
  - **File:** `pulsus/mcp/simple/file_manager.py`
  - **Agent:** Jean-Claude Mechanic
  - **Status:** ✅ Complete (November 17, 2025)
  - **Actions:**
    - create_file (@write_safe)
    - delete_file (@write_safe)
    - move_file (@write_safe)
    - copy_file (@write_safe)
    - list_files (@read_only)
    - get_file_info (@read_only)
  - **Tests:** 14/14 passed

- [x] 🔴 Implement DataReader (Tier 1)
  - **Action:** Create data loading domain
  - **File:** `pulsus/mcp/simple/data_reader.py`
  - **Agent:** Jean-Claude Mechanic
  - **Status:** ✅ Complete (November 17, 2025)
  - **Actions:**
    - read_csv (@read_only @cached)
    - read_json (@read_only @cached)
    - read_parquet (@read_only @cached)
    - read_excel (@read_only @cached)
    - get_schema (@read_only @cached)
    - query_dataframe (@read_only)
  - **Tests:** 11/11 passed

- [x] 🔴 Implement TextProcessor (Tier 1)
  - **Action:** Create text manipulation domain
  - **File:** `pulsus/mcp/simple/text_processor.py`
  - **Agent:** Jean-Claude Mechanic
  - **Status:** ✅ Complete (November 17, 2025)
  - **Actions:**
    - search_text (@read_only)
    - replace_text (@read_only)
    - extract_patterns (@read_only)
    - count_words (@read_only @cached)
    - split_text (@read_only)
    - analyze_text (@read_only)
  - **Tests:** 17/17 passed

- [x] 🟠 Create LangChain tool adapters
  - **Action:** Convert MCPBase to LangChain StructuredTool
  - **File:** `pulsus/langchain/tool_adapter.py`
  - **Status:** ✅ Complete (November 17, 2025)
  - **Function:** `mcp_to_langchain_tool(mcp_class) -> StructuredTool`
  - **Features:**
    - Domain-level and operation-level conversion
    - Auto-discovery with `discover_and_convert_mcp_domains()`
    - MCPToolRegistry for managing tools
  - **Tests:** 22/22 passed

- [x] 🟠 Write integration tests
  - **Action:** Test MCP domains with LangChain integration
  - **File:** `mcp/tests/test_langchain_integration.py`
  - **Status:** ✅ Complete (November 17, 2025)
  - **Agent:** Jean-Claude Mechanic
  - **Tests:**
    - 5 tool conversion tests
    - 4 tool execution tests
    - 2 auto-discovery tests
    - 6 registry tests
    - 5 integration scenario tests
  - **Total:** 22 tests, all passing ✅

- [x] 🟡 Create domain catalog
  - **Action:** Document all classic domains
  - **File:** `docs/CLASSIC_MCP_CATALOG.md`
  - **Status:** ✅ Complete (November 17, 2025)
  - **Agent:** Jean-Claude Architect
  - **Content:**
    - Detailed documentation for all 5 domains
    - Capability matrices
    - Usage examples
    - LangChain integration guide
    - Best practices

#### Milestone 2: Classic Domains Operational ✅
**Status:** ✅ **COMPLETE** - November 17, 2025

**Acceptance Criteria:**
- ✅ 5+ classic domains implemented (ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor)
- ✅ All convert to LangChain tools (tested with 22 integration tests)
- ✅ Integration tests pass (64/64 tests passing)
- ✅ Domain catalog complete with comprehensive documentation

---

### 🔄 Phase 3: Workflow MCP Domains (Weeks 9-12)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 3
**Duration:** 3-4 weeks
**Primary Agent:** Jean-Claude Science + Jean-Claude Mechanic

#### Tasks

- [ ] 🔴 Research LangChain workflow patterns
  - **Action:** Study LangChain workflows and best practices
  - **Agent:** Jean-Claude Science
  - **Command:** `use jean-claude-science to research LangChain workflow patterns`
  - **Output:** Research report with recommendations

- [ ] 🔴 Design workflow architecture
  - **Action:** Create workflow base classes
  - **Files:** `pulsus/workflows/base.py`
  - **Agent:** Jean-Claude Architect
  - **Classes:**
    - WorkflowBase
    - WorkflowStep
    - WorkflowState

- [ ] 🔴 Implement RepositoryAnalyzer workflow
  - **Action:** Refactor existing analyzer as workflow
  - **File:** `pulsus/workflows/tools/analyze/repository_analyzer_llm.py`
  - **Agent:** Jean-Claude Mechanic
  - **Steps:**
    1. Scan files (Glob + Read)
    2. Extract dependencies (AST parsing)
    3. Analyze structure (LLM)
    4. Generate report (Template)

- [ ] 🔴 Create workflow JSON definitions
  - **Action:** Define workflows declaratively
  - **Files:** `pulsus/workflows/definitions/*.json`
  - **Agent:** Jean-Claude Mechanic
  - **Workflows:**
    - repository_analysis.json
    - dependency_documentation.json
    - code_refactoring.json

- [ ] 🟠 Build workflow composer
  - **Action:** Implement workflow execution engine
  - **File:** `pulsus/workflows/composer.py`
  - **Agent:** Jean-Claude Mechanic
  - **Features:**
    - Load JSON definitions
    - Execute steps in sequence
    - Handle state between steps
    - Error handling and rollback

- [ ] 🟠 Add LLM integration
  - **Action:** Connect to Ollama/OpenAI/Claude
  - **File:** `pulsus/workflows/llm_connector.py`
  - **Agent:** Jean-Claude Mechanic
  - **Providers:** Ollama (default), OpenAI, Anthropic

- [ ] 🟠 Test multi-step workflows
  - **Action:** Integration tests for workflows
  - **Files:** `tests/integration/test_workflows.py`
  - **Agent:** Jean-Claude Auditor
  - **Scenarios:**
    - Happy path (all steps succeed)
    - Error handling (step fails)
    - State persistence
    - LLM fallback

- [ ] 🟡 Create workflow documentation
  - **Action:** Document workflow system
  - **File:** `docs/WORKFLOW_SYSTEM.md`
  - **Agent:** Jean-Claude Architect

#### Milestone 3: Workflows Operational ✅
**Acceptance Criteria:**
- 3+ workflows implemented
- JSON definitions work
- LLM integration functional
- Tests pass for multi-step execution

---

### ⚙️ Phase 4: Customizable Framework (Weeks 13-14)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 4
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Mechanic + Jean-Claude MCP

#### Tasks

- [ ] 🔴 Design configuration schema
  - **Action:** Create JSON schema for custom workflows
  - **File:** `pulsus/config/frameworks/schema/custom_workflow_schema.json`
  - **Agent:** Jean-Claude Architect
  - **Validation:** JSON Schema Draft 7

- [ ] 🔴 Implement config loader
  - **Action:** Load and validate custom configs
  - **File:** `pulsus/config/framework_loader.py`
  - **Agent:** Jean-Claude Mechanic
  - **Features:**
    - Load from JSON/YAML
    - Validate against schema
    - Merge with defaults
    - Error reporting

- [ ] 🟠 Integrate Jinja2 template engine
  - **Action:** Add template rendering
  - **File:** `pulsus/config/template_engine.py`
  - **Agent:** Jean-Claude Mechanic
  - **Templates:** Code generation, documentation, reports

- [ ] 🟠 Build custom workflow executor
  - **Action:** Execute user-defined workflows
  - **File:** `pulsus/workflows/custom_executor.py`
  - **Agent:** Jean-Claude MCP
  - **Features:**
    - Dynamic tool loading
    - Parameter substitution
    - Template rendering
    - Output validation

- [ ] 🟠 Add schema validation
  - **Action:** Validate custom configs before execution
  - **File:** `pulsus/config/schema_validator.py`
  - **Agent:** Jean-Claude Auditor
  - **Libraries:** jsonschema, pydantic

- [ ] 🟡 Write framework usage guide
  - **Action:** Documentation for custom workflows
  - **File:** `docs/CUSTOM_FRAMEWORK_GUIDE.md`
  - **Agent:** Jean-Claude Architect
  - **Sections:**
    - Configuration format
    - Template syntax
    - Example workflows
    - Best practices

#### Milestone 4: Customization Ready ✅
**Acceptance Criteria:**
- Users can define custom workflows via JSON
- Templates work with Jinja2
- Schema validation prevents errors
- Documentation complete

---

### 🖥️ Phase 5: External Console Execution (Weeks 15-16)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 5
**Duration:** 1-2 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

- [ ] 🔴 Design ConsoleManager API
  - **Action:** Specify process management interface
  - **Agent:** Jean-Claude Architect
  - **Output:** API specification document

- [ ] 🔴 Implement Windows console launcher
  - **Action:** Launch processes in new console (Windows)
  - **File:** `pulsus/mcp/execution/console_manager.py` (Windows impl)
  - **Agent:** Jean-Claude Mechanic
  - **Features:**
    - CREATE_NEW_CONSOLE flag
    - cmd.exe wrapping
    - Title setting

- [ ] 🔴 Implement Unix/Linux console launcher
  - **Action:** Launch processes in terminal (Unix)
  - **File:** `pulsus/mcp/execution/console_manager.py` (Unix impl)
  - **Agent:** Jean-Claude Mechanic
  - **Terminals:** gnome-terminal, xterm, konsole

- [ ] 🟠 Add process monitoring
  - **Action:** Track running processes
  - **Library:** psutil
  - **Agent:** Jean-Claude Mechanic
  - **Features:**
    - Process status
    - Resource usage
    - Exit codes

- [ ] 🟠 Create output capture mechanism
  - **Action:** Capture stdout/stderr
  - **Agent:** Jean-Claude Mechanic
  - **Methods:**
    - File redirection
    - Pipe capture
    - Real-time streaming

- [ ] 🟠 Test with real simulations
  - **Action:** Test with Aimsun, Python scripts
  - **Agent:** Jean-Claude Auditor
  - **Test cases:**
    - Launch Aimsun
    - Run Python simulation
    - Monitor process
    - Kill process

- [ ] 🟡 Create console execution guide
  - **Action:** Document ConsoleManager usage
  - **File:** `docs/CONSOLE_EXECUTION_GUIDE.md`
  - **Agent:** Jean-Claude Architect

#### Milestone 5: External Execution Works ✅
**Acceptance Criteria:**
- Can launch processes in separate consoles
- Works on Windows and Unix/Linux
- Process monitoring functional
- Tests pass with real software

---

### 👤 Phase 6: Preferences & Context Memory (Week 17)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 6
**Duration:** 1 week
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

- [ ] 🟠 Implement PreferencesManager
  - **Action:** User preference storage
  - **File:** `pulsus/preferences/manager.py`
  - **Agent:** Jean-Claude Mechanic
  - **Storage:** `~/.pulsus/preferences.json`

- [ ] 🟠 Create defaults.json
  - **Action:** Default preference values
  - **File:** `pulsus/preferences/defaults.json`
  - **Agent:** Jean-Claude Mechanic
  - **Defaults:**
    - auto_approve_read_only: false
    - verbosity: normal
    - log_level: info

- [ ] 🟡 Add CLI commands for preferences
  - **Action:** CLI for editing preferences
  - **Commands:**
    - `pulsus config set <key> <value>`
    - `pulsus config get <key>`
    - `pulsus config reset`
  - **Agent:** Jean-Claude Mechanic

- [ ] 🟡 Integrate with SafeNet logging
  - **Action:** Log preference changes
  - **Agent:** Jean-Claude Mechanic
  - **Events:** Preference updated, reset

- [ ] 🟡 Write unit tests
  - **Action:** Test preference management
  - **File:** `tests/unit/test_preferences.py`
  - **Agent:** Jean-Claude Auditor

#### Milestone 6: Preferences Persistent ✅
**Acceptance Criteria:**
- Preferences persist across sessions
- CLI commands work
- Changes logged
- Tests pass

---

### 📊 Phase 7: SafeNet Logging & Observability (Weeks 18-19)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 7
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Mechanic + Jean-Claude Designer

#### Tasks

- [ ] 🔴 Implement SafeNetLogger
  - **Action:** Core logging infrastructure
  - **File:** `pulsus/shared/logging/safenet_logger.py`
  - **Agent:** Jean-Claude Mechanic
  - **Format:** JSONL (one event per line)
  - **Fields:**
    - timestamp
    - event_type
    - domain
    - action
    - result
    - metadata
    - latency_ms

- [ ] 🟠 Create log formatters
  - **Action:** JSON and human-readable output
  - **File:** `pulsus/shared/logging/formatter.py`
  - **Agent:** Jean-Claude Mechanic
  - **Formats:**
    - JSON (machine-readable)
    - Pretty (human-readable)
    - Colored terminal output

- [ ] 🟠 Build metrics aggregator
  - **Action:** Calculate performance metrics
  - **File:** `pulsus/shared/logging/metrics.py`
  - **Agent:** Jean-Claude Science
  - **Metrics:**
    - Total executions per domain
    - Average latency per action
    - Success/failure rates
    - Most used tools

- [ ] 🟠 Design dashboard UI
  - **Action:** Create HTML dashboard mockups
  - **Agent:** Jean-Claude Designer
  - **Command:** `use jean-claude-designer to design SafeNet dashboard`
  - **Views:**
    - Overview (key metrics)
    - Domain breakdown
    - Timeline view
    - Error log

- [ ] 🟠 Implement HTML dashboard generator
  - **Action:** Generate interactive dashboard
  - **File:** `pulsus/shared/logging/dashboard_generator.py`
  - **Agent:** Jean-Claude Mechanic
  - **Technologies:** HTML, CSS, JavaScript (Chart.js)

- [ ] 🟡 Add log rotation and retention
  - **Action:** Manage log files
  - **Agent:** Jean-Claude Mechanic
  - **Policy:**
    - Daily log files
    - 7-day retention (default)
    - Compression for archives

- [ ] 🟡 Write integration tests
  - **Action:** Test logging system
  - **File:** `tests/integration/test_safenet_logging.py`
  - **Agent:** Jean-Claude Auditor
  - **Tests:**
    - Log events captured
    - Metrics calculated correctly
    - Dashboard generates

#### Milestone 7: Full Observability ✅
**Acceptance Criteria:**
- Every MCP action logged
- Metrics dashboard functional
- Log rotation works
- Tests pass

---

### 🔌 Phase 8: Interface & API Adapters (Weeks 20-21)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 8
**Duration:** 1-2 weeks
**Primary Agent:** Jean-Claude Mechanic

#### Tasks

- [ ] 🔴 Implement CLI interface
  - **Action:** Command-line entrypoint
  - **File:** `pulsus/interface/cli.py`
  - **Agent:** Jean-Claude Mechanic
  - **Commands:**
    - `pulsus execute <domain> <action> [--params <json>]`
    - `pulsus list-domains`
    - `pulsus config <subcommand>`

- [ ] 🔴 Implement FastAPI endpoints
  - **Action:** HTTP API for supervisors
  - **File:** `pulsus/interface/api.py`
  - **Agent:** Jean-Claude Mechanic
  - **Endpoints:**
    - POST /execute - Execute MCP action
    - GET /domains - List available domains
    - GET /health - Health check
    - GET /metrics - SafeNet metrics

- [ ] 🟠 Add API authentication
  - **Action:** Token-based auth
  - **Agent:** Jean-Claude Mechanic
  - **Method:** Bearer tokens, API keys

- [ ] 🟠 Create OpenAPI documentation
  - **Action:** API documentation
  - **File:** `docs/API_REFERENCE.md`
  - **Agent:** Jean-Claude Architect
  - **Format:** OpenAPI 3.0 spec

- [ ] 🟠 Test CLI usage
  - **Action:** CLI integration tests
  - **File:** `tests/integration/test_cli.py`
  - **Agent:** Jean-Claude Auditor

- [ ] 🟠 Test API endpoints
  - **Action:** API integration tests
  - **File:** `tests/integration/test_api.py`
  - **Agent:** Jean-Claude Auditor
  - **Tools:** pytest + httpx

#### Milestone 8: Interfaces Ready ✅
**Acceptance Criteria:**
- CLI functional with help/docs
- API serves requests
- Authentication works
- Documentation complete
- Tests pass

---

### 🕸️ Phase 9: LangGraph Integration (Weeks 22-24)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 9
**Duration:** 2-3 weeks
**Primary Agent:** Jean-Claude Science + Jean-Claude Mechanic

#### Tasks

- [ ] 🔴 Research LangGraph patterns
  - **Action:** Study LangGraph StateGraph
  - **Agent:** Jean-Claude Science
  - **Command:** `use jean-claude-science to research LangGraph patterns`
  - **Output:** Research report + recommendations

- [ ] 🔴 Design PulsusState schema
  - **Action:** Define state structure
  - **File:** `pulsus/langchain/state.py`
  - **Agent:** Jean-Claude Architect
  - **Fields:**
    - messages
    - parsed_intent
    - selected_tools
    - execution_results
    - next_action

- [ ] 🔴 Implement graph nodes
  - **Action:** Create node functions
  - **File:** `pulsus/langchain/graph_executor.py`
  - **Agent:** Jean-Claude Mechanic
  - **Nodes:**
    - parse_intent_node
    - discover_tools_node
    - select_policy_node
    - execute_tools_node
    - compose_response_node

- [ ] 🟠 Create conditional routing
  - **Action:** Implement routing logic
  - **Agent:** Jean-Claude Mechanic
  - **Function:** `route_execution_policy(state) -> str`
  - **Routes:** select, compose, generate

- [ ] 🟠 Build graph compiler
  - **Action:** Compile StateGraph
  - **Agent:** Jean-Claude Mechanic
  - **Function:** `create_pulsus_graph() -> CompiledGraph`

- [ ] 🟠 Test graph execution
  - **Action:** Integration tests
  - **File:** `tests/integration/test_langgraph.py`
  - **Agent:** Jean-Claude Auditor
  - **Scenarios:**
    - Simple query (select path)
    - Complex query (compose path)
    - Ambiguous query (generate path)

- [ ] 🟠 Integrate with existing routing
  - **Action:** Connect LangGraph to current router
  - **File:** `pulsus/routing/router.py` (updates)
  - **Agent:** Jean-Claude Mechanic
  - **Mode:** Optional LangGraph execution

#### Milestone 9: LangGraph Operational ✅
**Acceptance Criteria:**
- StateGraph compiles and runs
- All routing paths work
- Integrates with existing system
- Tests pass

---

### ✅ Phase 10: Testing, Validation & Performance (Weeks 25-26)

**Reference:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Phase 10
**Duration:** 2 weeks
**Primary Agent:** Jean-Claude Auditor

#### Tasks

- [ ] 🔴 Create pytest test suite
  - **Action:** Comprehensive test coverage
  - **Agent:** Jean-Claude Auditor
  - **Command:** `use jean-claude-auditor to create comprehensive test suite`
  - **Structure:**
    - tests/unit/ (90%+ coverage)
    - tests/integration/ (key workflows)
    - tests/performance/ (benchmarks)

- [ ] 🔴 Add coverage reporting
  - **Action:** Setup pytest-cov
  - **File:** `.coveragerc`
  - **Agent:** Jean-Claude Auditor
  - **Target:** 95%+ coverage

- [ ] 🟠 Implement benchmarks
  - **Action:** Performance tests
  - **File:** `tests/performance/test_benchmarks.py`
  - **Agent:** Jean-Claude Auditor
  - **Metrics:**
    - Startup latency
    - Execution time (by domain)
    - Memory usage
    - Log throughput

- [ ] 🟠 Run security audit
  - **Action:** Security assessment
  - **Agent:** Jean-Claude Auditor (or Jean-Claude Security if available)
  - **Tools:** bandit, safety
  - **Checks:**
    - Injection vulnerabilities
    - File access scope
    - Code execution risks
    - Dependency vulnerabilities

- [ ] 🟠 Perform stress testing
  - **Action:** Load tests
  - **Agent:** Jean-Claude Auditor
  - **Tools:** locust, pytest-benchmark
  - **Scenarios:**
    - Concurrent requests
    - Large workflows
    - Long-running processes

- [ ] 🟡 Setup CI/CD pipeline
  - **Action:** GitHub Actions workflow
  - **File:** `.github/workflows/test.yml`
  - **Agent:** Jean-Claude Mechanic (or DevOps)
  - **Steps:**
    - Lint (ruff)
    - Type check (mypy)
    - Tests (pytest)
    - Coverage report
    - Security scan

- [ ] 🟡 Generate final audit report
  - **Action:** Comprehensive QA report
  - **File:** `docs/FINAL_AUDIT_REPORT.md`
  - **Agent:** Jean-Claude Auditor
  - **Sections:**
    - Test results
    - Coverage metrics
    - Performance benchmarks
    - Security findings
    - Recommendations

#### Milestone 10: Production Ready ✅
**Acceptance Criteria:**
- 95%+ test coverage
- All benchmarks meet targets
- Security audit passed
- CI/CD pipeline functional
- Final audit report complete

---

## 🏛️ Framework Integration (Parallel Track)

**Reference:** `FRAMEWORK_INTEGRATION_ADDENDUM.md`
**Duration:** 5 weeks (can run parallel to Phases 8-10)
**Primary Agent:** Jean-Claude MCP + Jean-Claude Mechanic

### Tasks

- [ ] 🔴 Implement FrameworkDomainExecutor
  - **Action:** 8-step workflow orchestrator
  - **File:** `pulsus/workflows/framework/domain_executor.py`
  - **Agent:** Jean-Claude MCP
  - **Reference:** `FRAMEWORK_INTEGRATION_ADDENDUM.md` → Section 1

- [ ] 🔴 Create domain configuration schema
  - **Action:** JSON schema for domains
  - **File:** `pulsus/config/frameworks/domain_framework/schema/domain_schema.json`
  - **Agent:** Jean-Claude Architect
  - **Reference:** `FRAMEWORK_INTEGRATION_ADDENDUM.md` → Section 2

- [ ] 🔴 Build AimsunConnector
  - **Action:** Aimsun integration via ConsoleManager
  - **File:** `pulsus/mcp/simple/aimsun_connector.py`
  - **Agent:** Jean-Claude Mechanic
  - **Reference:** `FRAMEWORK_INTEGRATION_ADDENDUM.md` → Section 3.2

- [ ] 🔴 Add GeoParquetExporter
  - **Action:** Canonical GeoParquet export
  - **File:** `pulsus/mcp/simple/geoparquet_exporter.py`
  - **Agent:** Jean-Claude Mechanic
  - **Reference:** `FRAMEWORK_INTEGRATION_ADDENDUM.md` → Section 3.3

- [ ] 🟠 Wrap shared tools as MCP domains
  - **Action:** Convert framework shared tools
  - **Files:** `pulsus/config/frameworks/domain_framework/shared_tools/*.py`
  - **Agent:** Jean-Claude Mechanic
  - **Tools:**
    - common_analyser
    - auto_importer
    - ui_editor
    - review_check
    - export_to_GeoParquet
    - generate_docs
    - html_visualiser

- [ ] 🟠 Convert domains to JSON configs
  - **Action:** Create config for all 40+ domains
  - **Files:** `pulsus/config/frameworks/domain_framework/domains/*.json`
  - **Agent:** Jean-Claude Domain
  - **Start with:** 0300_Geometry, 0800_Detectors, 4600_AdjustmentResult

- [ ] 🟠 Test with real domain
  - **Action:** End-to-end test with 0300_Geometry
  - **Agent:** Jean-Claude Auditor
  - **Validation:** All 8 steps execute, outputs created

#### Framework Milestone: Integration Complete ✅
**Acceptance Criteria:**
- FrameworkDomainExecutor works
- Aimsun can be launched/controlled
- GeoParquet export functional
- 3+ domains converted and tested
- Documentation complete

---

## 📊 Overall Progress Tracking

### Completion Status

| Phase | Status | Progress | Estimated Completion |
|-------|--------|----------|---------------------|
| 0: Pre-Implementation | ✅ Complete | 100% | Week 0 |
| 1: Core Framework | ✅ Complete | 100% | November 10, 2025 |
| 2: Classic Domains | ✅ Complete | 100% | November 17, 2025 |
| 3: Workflow Domains | ⚪ Not Started | 0% | Week 12 |
| 4: Customizable Framework | ⚪ Not Started | 0% | Week 14 |
| 5: Console Execution | ⚪ Not Started | 0% | Week 16 |
| 6: Preferences | ⚪ Not Started | 0% | Week 17 |
| 7: SafeNet Logging | ⚪ Not Started | 0% | Week 19 |
| 8: Interfaces | ⚪ Not Started | 0% | Week 21 |
| 9: LangGraph | ⚪ Not Started | 0% | Week 24 |
| 10: Testing | ⚪ Not Started | 0% | Week 26 |
| Framework Integration | ⚪ Not Started | 0% | Week 21 (parallel) |

**Legend:**
- ✅ Complete
- 🟢 In Progress (>50%)
- 🟡 In Progress (<50%)
- ⚪ Not Started
- ❌ Blocked

### Key Metrics

- **Total Estimated Duration:** 26 weeks (6-7 months)
- **Critical Path:** Phases 1 → 2 → 3 → 9 → 10
- **Parallel Tracks:** Phases 4-8 can overlap, Framework Integration runs parallel
- **Team Size:** Estimated 2-3 full-time developers
- **Documentation Coverage:** Target 100%
- **Test Coverage:** Target 95%+

---

## 🚀 Quick Start Commands

### Start Phase 1
```bash
# Architecture audit
use jean-claude-architect to audit Pulsus architecture against unified plan

# Start implementation
use jean-claude-mechanic to implement Phase 1 - Core MCP Framework
```

### Run Tests
```bash
# Unit tests
pytest tests/unit/ -v --cov=pulsus --cov-report=html

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v --cov=pulsus
```

### Generate Documentation
```bash
# API docs
use jean-claude-architect to generate API documentation

# User guides
use jean-claude-architect to create user guides
```

---

## 📞 Support & Questions

### For Implementation Questions
- **Document:** Check relevant phase in `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`
- **Agent:** Use appropriate Jean-Claude agent
- **Team:** Consult with development team

### For Framework Integration
- **Document:** `FRAMEWORK_INTEGRATION_ADDENDUM.md`
- **Agent:** Jean-Claude MCP
- **Contact:** Framework team for domain-specific questions

### For Architecture Decisions
- **Document:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` → Architecture Overview
- **Agent:** Jean-Claude Architect
- **Process:** Create ADR (Architecture Decision Record) in `docs/adr/`

---

## 📝 Notes

### Last Updated
- **Date:** November 17, 2025
- **By:** Jean-Claude Mechanic
- **Changes:**
  - Phase 2 progress: Implemented 3 new MCP domains
  - FileManager, DataReader, TextProcessor all complete
  - 42 tests created and passing (100% pass rate)

### Next Review
- **When:** End of Phase 1 (Week 4)
- **Focus:** Validate approach, adjust timeline if needed

### Assumptions
- Development team available full-time
- Jean-Claude agents available for assistance
- Framework team available for domain expertise
- CI/CD infrastructure can be setup

---

**Status:** ✅ Phase 2 Complete - Ready for Phase 3
**Last Updated:** November 17, 2025
**Next Action:** Begin Phase 3 - Workflow MCP Domains
**Priority:** LangChain workflow research → RepositoryAnalyzer → Workflow architecture

**Phase 2 Complete:** 5 classic domains with 64/64 tests passing! ✅
**Deliverables:** FileManager, DataReader, TextProcessor + LangChain integration + comprehensive documentation

---

## 📝 Recent Updates

### November 10, 2025 - Phase 1 Complete ✅
- ✅ MCPBase and MCPResponse implemented (397 lines)
- ✅ All 5 safety decorators functional (503 lines)
- ✅ SafetyPolicy enforcement system (394 lines)
- ✅ MCPLogger with SafeNet integration (390 lines)
- ✅ Type definitions created (288 lines)
- ✅ Test suite: 24/24 tests passing (100%)
- ✅ Documentation complete (461 lines README + completion report)
- **Total:** ~2,500 lines of production code

### November 10, 2025 - Phase 2 Planning Complete ✅
- ✅ Comprehensive implementation plan created (docs/PHASE2_PLAN.md)
- ✅ Existing helpers inventory completed (9 helpers, ~2,100 lines)
- ✅ LangChain integration strategy designed
- ✅ Task breakdown with 3-week timeline
- **Ready to start:** Week 1 - Core Migrations

### November 17, 2025 - Phase 2 Complete ✅
- ✅ FileManager domain implemented with 6 methods (create, delete, move, copy, list, get_info)
- ✅ DataReader domain implemented with 6 methods (read_csv, read_json, read_parquet, read_excel, get_schema, query_dataframe)
- ✅ TextProcessor domain implemented with 6 methods (search, replace, extract, count_words, split, analyze)
- ✅ 42 domain tests created and passing (100% success rate)
- ✅ 22 LangChain integration tests created and passing (100% success rate)
- ✅ mcp/simple/__init__.py updated to export all 5 domains
- ✅ Domain catalog documentation (docs/CLASSIC_MCP_CATALOG.md)
- ✅ LangChain tool adapter already implemented (langchain/tool_adapter.py)
- ✅ MCPToolRegistry for managing tools
- ✅ Auto-discovery of MCP domains
- **Total:** ~1,200 lines of production code + ~950 lines of tests + comprehensive documentation
- **Tests:** 64/64 passing (42 domain + 22 LangChain integration)
