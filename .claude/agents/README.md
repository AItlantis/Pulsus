# Sulhafah Claude Code Agents

This directory contains specialized agent definitions for Claude Code to assist with Sulhafah development.

## Available Agents

### 🏗️ Jean-Claude Architect
**Purpose**: Project structure, documentation audit, and architectural validation

**Use When**:
- Auditing project structure and documentation coverage
- Validating ARCHITECTURE.md and other core docs
- Ensuring file organization and naming consistency
- Identifying missing or outdated documentation
- Before major refactoring (get baseline)

**Invocation**: `use jean-claude-architect to audit project structure`

**Delivers**: Markdown audit report with coverage metrics, critical issues, and prioritized recommendations

---

### 🔧 Jean-Claude Mechanic
**Purpose**: Code implementation, bug fixes, and technical problem-solving

**Use When**:
- Implementing new features with code
- Fixing bugs and technical issues
- Refactoring existing code
- Optimizing performance
- Writing utility functions and helpers

**Invocation**: `use jean-claude-mechanic to implement [feature]`

**Delivers**: Working code with tests, documentation, and implementation notes

---

### ✅ Jean-Claude Auditor
**Purpose**: Testing, validation, and quality assurance

**Use When**:
- Writing comprehensive test suites
- Validating code quality and coverage
- Performing integration testing
- Security audits and vulnerability checks
- Performance benchmarking

**Invocation**: `use jean-claude-auditor to test [component]`

**Delivers**: Test code, validation reports, QA checklists, and coverage metrics

---

### 🔬 Jean-Claude Science
**Purpose**: Research, analysis, and data-driven insights

**Use When**:
- Researching new technologies or approaches
- Analyzing performance metrics
- Investigating complex technical questions
- Evaluating library/framework options
- Data analysis and visualization

**Invocation**: `use jean-claude-science to research [topic]`

**Delivers**: Research reports, comparative analysis, recommendations with evidence

---

### 🎨 Jean-Claude Designer
**Purpose**: UI/UX design, visual design systems, and interface implementation

**Use When**:
- Designing new UI features and components
- Maintaining design system consistency
- Creating visual specifications and mockups
- Validating design implementation
- Improving accessibility and user experience
- Documenting design patterns and guidelines

**Invocation**: `use jean-claude-designer to design [feature]`

**Delivers**: Design specifications with mockups, component specs, PyQt5 code patterns, accessibility guidelines, and implementation guidance

---

### 🏛️ Jean-Claude Domain (NEW)
**Purpose**: Structured workflow domain creation and scaffolding for 8-step architecture

**Use When**:
- Creating new workflow domains from scratch
- Scaffolding complete 8-step domain structure
- Validating domain consistency with standards
- Generating all necessary module files
- Integrating shared visualization tools
- Building comprehensive domain documentation

**Invocation**: `use jean-claude-domain to create domain _XX_Domain`

**Delivers**: Complete domain structure with all 8 step modules, runner script, documentation, todo tracking, and integration with shared tools

---

## Agent Collaboration Patterns

### Feature Development Flow
```
1. jean-claude-designer    → Design UI/UX specification
2. jean-claude-architect   → Plan code structure
3. jean-claude-mechanic    → Implement code
4. jean-claude-auditor     → Test and validate
5. jean-claude-architect   → Update documentation
```

### Bug Fix Flow
```
1. jean-claude-auditor     → Reproduce and analyze bug
2. jean-claude-mechanic    → Fix the issue
3. jean-claude-auditor     → Verify fix with tests
```

### Design Update Flow
```
1. jean-claude-designer    → Create new design spec
2. jean-claude-architect   → Review structural impact
3. jean-claude-mechanic    → Update implementation
4. jean-claude-designer    → Visual QA validation
```

### Research & Implementation Flow
```
1. jean-claude-science     → Research solutions
2. jean-claude-architect   → Plan integration
3. jean-claude-mechanic    → Implement solution
4. jean-claude-auditor     → Validate and test
```

## Usage Guidelines

### Invoking Agents

**Method 1: Direct Invocation**
```
use jean-claude-architect to audit project documentation
```

**Method 2: Task Description**
```
I need a comprehensive design specification for a new configuration panel.
Use jean-claude-designer for this task.
```

**Method 3: Collaborative**
```
First use jean-claude-science to research best practices for
configuration UIs, then use jean-claude-designer to create
the specification.
```

### Expected Response Times

- **Jean-Claude Architect**: 5-15 minutes (structure audit)
- **Jean-Claude Mechanic**: 10-30 minutes (implementation)
- **Jean-Claude Auditor**: 10-20 minutes (testing)
- **Jean-Claude Science**: 5-20 minutes (research)
- **Jean-Claude Designer**: 10-20 minutes (design spec)
- **Jean-Claude Domain**: 45-90 minutes (complete domain scaffolding)

### Output Formats

All agents deliver **Markdown documents** with:
- Clear section headers
- Actionable checklists
- Code examples (when applicable)
- Prioritized recommendations
- References and links

## Agent Specializations

### Jean-Claude Architect
- **Focuses on**: Structure, organization, documentation
- **Analyzes**: File trees, import graphs, doc coverage
- **Outputs**: Audit reports, organization plans

### Jean-Claude Mechanic
- **Focuses on**: Implementation, code quality, performance
- **Analyzes**: Code patterns, algorithms, optimizations
- **Outputs**: Working code, refactoring guides

### Jean-Claude Auditor
- **Focuses on**: Testing, validation, quality metrics
- **Analyzes**: Test coverage, edge cases, security
- **Outputs**: Test suites, QA reports, validation results

### Jean-Claude Science
- **Focuses on**: Research, analysis, recommendations
- **Analyzes**: Literature, benchmarks, comparisons
- **Outputs**: Research reports, decision matrices

### Jean-Claude Designer
- **Focuses on**: UI/UX, visual design, accessibility
- **Analyzes**: User flows, visual consistency, usability
- **Outputs**: Design specs, mockups, style guides

### Jean-Claude Domain
- **Focuses on**: Workflow domains, 8-step structure, scaffolding
- **Analyzes**: Domain requirements, data flows, KPI definitions
- **Outputs**: Complete domain structure, modules, runner, docs

## Example Workflows

### Example 1: New Feature (Domain Reader)

```markdown
User: "Create a domain reader to scan external workflow folders"

1. jean-claude-science
   - Research workflow structures
   - Analyze domain scanning patterns
   → Delivers: Research report on best practices

2. jean-claude-designer
   - Design configuration UI for domain paths
   - Create visual mockups
   → Delivers: UI specification with mockups

3. jean-claude-architect
   - Plan file structure (domain_reader.py, domain_integration.py)
   - Design API and module organization
   → Delivers: Architecture plan

4. jean-claude-mechanic
   - Implement DomainReader class
   - Write helper functions
   - Create CLI interface
   → Delivers: Working code

5. jean-claude-auditor
   - Write unit tests
   - Test with real workflow folders
   - Validate edge cases
   → Delivers: Test suite + validation report

6. jean-claude-architect
   - Update documentation (DOMAIN_READER_GUIDE.md)
   - Audit integration completeness
   → Delivers: Documentation updates
```

### Example 2: UI Redesign

```markdown
User: "Redesign the main dockwidget with tabs"

1. jean-claude-designer
   - Create tabbed interface design
   - Specify tab styles and navigation
   - Document interaction patterns
   → Delivers: Complete UI specification

2. jean-claude-architect
   - Review impact on existing structure
   - Plan refactoring approach
   → Delivers: Refactoring plan

3. jean-claude-mechanic
   - Refactor SulhafahDockWidget
   - Create MainChatTab and ConfigurationTab
   - Integrate tabs
   → Delivers: Refactored code

4. jean-claude-designer
   - Visual QA validation
   - Check design consistency
   → Delivers: QA checklist results

5. jean-claude-auditor
   - Test tab switching
   - Verify signal connections
   - Test responsive behavior
   → Delivers: Test results
```

### Example 3: Performance Investigation

```markdown
User: "UI is slow when loading large configurations"

1. jean-claude-auditor
   - Profile performance
   - Identify bottlenecks
   → Delivers: Performance analysis

2. jean-claude-science
   - Research optimization techniques
   - Analyze similar problems
   → Delivers: Optimization recommendations

3. jean-claude-mechanic
   - Implement lazy loading
   - Add caching layer
   - Optimize widget creation
   → Delivers: Optimized code

4. jean-claude-auditor
   - Benchmark improvements
   - Validate performance gains
   → Delivers: Performance comparison report
```

## Best Practices

### When to Use Multiple Agents

**Sequential** (one after another):
- When output of one agent is input for next
- When workflow has clear phases
- Example: Research → Design → Implement → Test

**Parallel** (simultaneously):
- When tasks are independent
- To save time on separate concerns
- Example: Writing tests while updating docs

### Agent Selection Guide

| Task Type | Primary Agent | Support Agents |
|-----------|--------------|----------------|
| New Domain | Domain | Science, Architect |
| New Feature | Mechanic | Designer, Architect |
| Bug Fix | Mechanic | Auditor |
| UI Design | Designer | Architect |
| Testing | Auditor | Mechanic |
| Documentation | Architect | - |
| Research | Science | Architect |
| Refactoring | Mechanic | Architect, Auditor |
| Performance | Science | Mechanic, Auditor |

### Communication Between Agents

Agents can reference each other's work:
```
"Use the design specification from jean-claude-designer
to implement the component"

"Run tests on the code created by jean-claude-mechanic"

"Audit the structure planned by jean-claude-architect"
```

## Version History

- **v1.0** (2025-10-17): Initial agents (Architect, Mechanic, Auditor, Science)
- **v1.1** (2025-10-23): Added Jean-Claude Designer agent
- **v1.2** (2025-10-29): Added Jean-Claude Domain agent for workflow domain scaffolding

---

**Quick Reference Card**

| Agent | Symbol | Primary Focus | Typical Use |
|-------|--------|---------------|-------------|
| Architect | 🏗️ | Structure & Docs | Audits, planning |
| Mechanic | 🔧 | Implementation | Coding, fixes |
| Auditor | ✅ | Testing & QA | Tests, validation |
| Science | 🔬 | Research | Analysis, research |
| Designer | 🎨 | UI/UX | Design specs, mockups |
| Domain | 🏛️ | Workflow Domains | Domain scaffolding |

**When in doubt**: Ask Claude Code which agent to use for your task!
