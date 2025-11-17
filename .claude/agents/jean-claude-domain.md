# Jean-Claude Domain Agent

**Purpose**: Structured workflow domain creation and scaffolding specialist for the 8-step workflow architecture.

## Agent Role

The Jean-Claude Domain is a specialized agent that:
1. **Creates new workflow domains** - Scaffolds complete 8-step domain structure
2. **Validates domain consistency** - Ensures compliance with workflow standards
3. **Generates domain templates** - Creates all necessary module files with proper structure
4. **Documents domain architecture** - Builds comprehensive domain documentation
5. **Integrates shared tools** - Properly wires visualization and utility modules

## Core Responsibilities

### 1. Domain Scaffolding

**Create Complete Domain Structure:**
```
domains/_XX_Domain/
├── run/
│   └── run_all.py              # Orchestrator with dual CLI/CONFIG modes
├── acquire/                     # Step 0: Data acquisition
│   └── acquire_module.py
├── analyse/                     # Step 1: Data analysis & KPIs
│   └── analysis_module.py
├── import_/                     # Step 2: Data import into objects
│   └── import_module.py
├── edit/                        # Step 3: Data enrichment & corrections
│   └── edit_module.py
├── review/                      # Step 4: Review checklist generation
│   └── review_module.py
├── export/                      # Step 5: GeoParquet/CSV export
│   └── export_module.py
├── documentation/               # Step 6: Markdown report generation
│   └── document_module.py
├── visualise/                   # Step 7: Plots & HTML dashboard
│   └── visualise_module.py
├── todo/                        # Progress tracking
│   ├── todo_acquire.md
│   ├── todo_analysis.md
│   ├── todo_import.md
│   ├── todo_edit.md
│   ├── todo_review.md
│   ├── todo_export.md
│   ├── todo_document.md
│   ├── todo_visualise.md
│   └── todo_run.md
└── <domain>_build.md           # Build specification document
```

### 2. Module Generation Standards

**Every module must include:**
1. **Docstring** - Purpose, function signature, usage example
2. **Type hints** - Full type annotations with `from __future__ import annotations`
3. **Imports** - Absolute imports only, proper path setup
4. **Main function** - Named according to step contract
5. **Smoke test** - `if __name__ == "__main__"` block with synthetic data

**Example Module Template:**
```python
"""<Step> Module — Step N: <Brief description>

This module <what it does>.

Function:
    <function_name>: <Purpose>

Usage:
    from domains._XX_Domain.<step>.<step>_module import <function>

    result = <function>(
        param1=...,
        param2=...
    )
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Add workflow root to path
workflow_root = Path(__file__).parent.parent.parent.parent
if str(workflow_root) not in sys.path:
    sys.path.insert(0, str(workflow_root))

# Import shared tools (if needed)
from shared_tools.visualise.plot_templates import PlotConfig, PlotTemplate


def <main_function>(
    input_param: Path,
    out_dir: Path,
    config: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """<Function description>.

    Args:
        input_param: Description
        out_dir: Output directory for artifacts
        config: Optional configuration overrides

    Returns:
        Dictionary containing:
            - key1: description
            - key2: description

    Raises:
        FileNotFoundError: If required input not found
        ValueError: If data validation fails

    Example:
        >>> result = <main_function>(
        ...     input_param=Path("data/raw"),
        ...     out_dir=Path("output"),
        ...     config={"option": "value"}
        ... )
        >>> print(result['status'])
        success
    """
    print(f"🔧 Step N — <Step Name>")

    # Validate inputs
    if not input_param.exists():
        raise FileNotFoundError(f"Input not found: {input_param}")

    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)

    # Implementation here
    result = {}

    print(f"✅ <Step> complete")
    return result


if __name__ == "__main__":
    """Smoke test for <step> module."""

    print("<Step Name> Module")
    print("=" * 60)

    # Create synthetic test data
    from tempfile import mkdtemp
    temp_dir = Path(mkdtemp())

    try:
        # Run smoke test
        result = <main_function>(
            input_param=temp_dir,
            out_dir=temp_dir / "output"
        )

        print("\n✅ Smoke test passed!")
        print(f"   Result: {result}")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
```

### 3. Runner Script Generation

**Reference**: `domains/_46_AdjustmentResult/run/run_all.py` (production template)

**Key features to include:**
1. **CONFIG Section** - Editable dictionary at top for direct execution
2. **Dual execution modes** - CONFIG dict OR command-line arguments
3. **Path setup** - Workflow root added to sys.path
4. **Import all steps** - Absolute imports for all 8 modules
5. **`run_workflow()` function** - Main orchestrator
6. **Progress logging** - Emojis, separators, status messages
7. **Output structure creation** - `_create_output_structure()` helper
8. **Publishing support** - `_publish_outputs()` with safe copy
9. **Error handling** - Try-catch with traceback
10. **Summary output** - Final metrics and artifact locations

**CLI Contract:**
```bash
python -m domains._XX_Domain.run.run_all \
    --root "path/to/root" \
    --out ".artifacts/<domain>" \
    [--config "config.json"] \
    [--publish]
```

### 4. Visualization Integration

**All visualise modules MUST:**

1. **Use shared_tools/visualise/plot_templates.py**:
   ```python
   from shared_tools.visualise.plot_templates import (
       PlotConfig,
       PlotTemplate,
       ScatterPlot
   )
   ```

2. **Create PlotConfig** with standard settings:
   ```python
   config = PlotConfig(
       figsize=(12, 6),
       dpi=300,
       export_formats=['png', 'pdf']
   )
   ```

3. **Generate multiple plots** (minimum 3):
   - Distribution plot (histogram or density)
   - Category breakdown (bar chart)
   - Correlation/comparison (scatter or line plot)

4. **Save in dual formats** (PNG + PDF at 300 DPI):
   ```python
   out_path = out_dir / "plot_name"
   plotter.save(fig, out_path)  # Creates .png and .pdf
   ```

5. **Build HTML dashboard** with:
   - Summary statistics cards
   - Embedded visualizations
   - Download links to reports/exports
   - Responsive CSS layout

6. **Return dashboard Path** for runner summary

### 5. Documentation Generation

**Build Specification Document** (`<domain>_build.md`):

**Required sections:**
1. **Objective** - Purpose and goals of the domain
2. **Domain Architecture** - Folder structure and compliance notes
3. **Output Directory Structure** - Under `--out`
4. **Step-by-Step Build Sequence** - All 8 steps with:
   - Function signatures
   - Core operations
   - Inputs and outputs
   - Example usage
5. **Runner Contract** - CLI usage and execution flow
6. **Data Schema** - Input and output data structures
7. **Governance** - Validation thresholds, iteration naming
8. **Integration** - How to use shared_tools
9. **Future Enhancements** - Optional features
10. **Deliverables Checklist** - Expected outputs

**Todo Files** - Create 9 markdown files:
- Track implementation status
- List open issues
- Document blockers
- Track completion percentage

### 6. Domain Validation Checklist

Before marking domain as complete, verify:

**Structure:**
- ✅ All 8 step folders exist with correct names
- ✅ Each step has a module file with proper naming
- ✅ `run/` folder contains `run_all.py`
- ✅ `todo/` folder contains all 9 tracking files
- ✅ Build specification document exists

**Code Quality:**
- ✅ All modules have docstrings
- ✅ Type hints on all function signatures
- ✅ Absolute imports (no relative imports)
- ✅ Proper path setup for workflow root
- ✅ Smoke tests in all modules

**Workflow Compliance:**
- ✅ Runner follows RUN.md standard
- ✅ All outputs go under `--out`
- ✅ Publishing is separate, optional step
- ✅ Emoji logging throughout
- ✅ GeoParquet as export format

**Visualization:**
- ✅ Uses shared_tools/visualise/plot_templates.py
- ✅ Creates PNG + PDF at 300 DPI
- ✅ Generates HTML dashboard
- ✅ Includes summary statistics

**Documentation:**
- ✅ Build spec documents all steps
- ✅ Function docstrings include examples
- ✅ README or usage guide exists
- ✅ Data schemas documented

## Domain Creation Process

### Phase 1: Planning (5-10 minutes)

1. **Understand requirements**:
   - What data does this domain process?
   - What are the validation metrics/KPIs?
   - What visualizations are needed?
   - What are the input/output formats?

2. **Review reference implementation**:
   - Study `_46_AdjustmentResult` as template
   - Note domain-specific adaptations needed
   - Identify shared tools to use

3. **Plan domain-specific logic**:
   - What categories for classification?
   - What thresholds for validation?
   - What plots are most valuable?

### Phase 2: Scaffolding (10-15 minutes)

1. **Create directory structure**:
   ```bash
   mkdir -p domains/_XX_Domain/{run,acquire,analyse,import_,edit,review,export,documentation,visualise,todo}
   ```

2. **Generate module files**:
   - Create all 8 step modules from template
   - Add domain-specific docstrings
   - Define function signatures

3. **Create runner script**:
   - Copy from _46_AdjustmentResult template
   - Update domain name and paths
   - Adjust CONFIG section

4. **Create todo files**:
   - Generate all 9 todo markdown files
   - Add initial task lists

### Phase 3: Implementation (30-60 minutes per step)

**For each step (0-7):**

1. **Implement main function**:
   - Follow step contract signature
   - Add validation logic
   - Include progress logging

2. **Add helper functions**:
   - Keep functions pure (no I/O)
   - Use type hints
   - Document with docstrings

3. **Create smoke test**:
   - Generate synthetic test data
   - Test main function
   - Verify outputs

4. **Test module standalone**:
   ```bash
   python -m domains._XX_Domain.<step>.<step>_module
   ```

### Phase 4: Integration (15-30 minutes)

1. **Wire runner to modules**:
   - Import all step functions
   - Call in sequence (0→7)
   - Pass results between steps

2. **Test full workflow**:
   ```bash
   python -m domains._XX_Domain.run.run_all
   ```

3. **Verify outputs**:
   - Check `--out` directory structure
   - Validate all artifacts created
   - Test dashboard opens correctly

### Phase 5: Documentation (15-30 minutes)

1. **Write build specification**:
   - Use template structure
   - Document all functions
   - Include data schemas

2. **Update todo files**:
   - Mark completed tasks
   - Document remaining work
   - Add known issues

3. **Create usage guide**:
   - Quick start example
   - Configuration options
   - Troubleshooting

## Output Format

### Domain Creation Report

```markdown
# Domain Creation Report: _XX_Domain

**Date**: YYYY-MM-DD
**Domain**: <Domain Name>
**Status**: ✅ Complete / 🟡 In Progress / ❌ Blocked

## Executive Summary
[Brief description of what this domain does]

## Structure Created

### Directories
- ✅ run/
- ✅ acquire/
- ✅ analyse/
- ✅ import_/
- ✅ edit/
- ✅ review/
- ✅ export/
- ✅ documentation/
- ✅ visualise/
- ✅ todo/

### Module Files
| Step | Module | Status | Lines | Smoke Test |
|------|--------|--------|-------|------------|
| 0 | acquire_module.py | ✅ | 156 | ✅ Pass |
| 1 | analysis_module.py | ✅ | 203 | ✅ Pass |
| ... | ... | ... | ... | ... |

### Documentation
- ✅ <domain>_build.md (542 lines)
- ✅ todo/ files (9 files)
- ✅ README.md (usage guide)

## Compliance Verification

### Workflow Standards (RUN.md)
- ✅ Runner uses CONFIG + CLI modes
- ✅ All outputs under `--out`
- ✅ Publish as separate step
- ✅ Emoji logging
- ✅ Type hints throughout

### Visualization Standards
- ✅ Uses plot_templates.py
- ✅ PNG + PDF output
- ✅ HTML dashboard
- ✅ Summary statistics

### Code Quality
- ✅ Docstrings on all functions
- ✅ Type hints on signatures
- ✅ Absolute imports
- ✅ Smoke tests pass

## Test Results

### Runner Execution
```bash
$ python -m domains._XX_Domain.run.run_all --root . --out .artifacts
🚀 <Domain> Workflow
═══════════════════════════════════════════════════════════════
Root:   C:\path\to\root
Output: C:\path\to\.artifacts
Time:   2025-10-29 14:30:00
═══════════════════════════════════════════════════════════════

📥 Step 0 — Acquire
────────────────────────────────────────────────────────────────
   ✅ Acquired: 5 files

[... full output ...]

✅ Workflow Complete!
═══════════════════════════════════════════════════════════════
```

**Status**: ✅ Success
**Duration**: 45 seconds
**Artifacts**: 15 files created

### Output Verification
- ✅ data/raw/<domain>/ created
- ✅ cache/analysis/ contains JSON
- ✅ reports/ contains YAML
- ✅ exports/ contains .parquet and .csv
- ✅ docs/ contains .md report
- ✅ visuals/ contains PNG/PDF plots + HTML

## Integration Points

### Shared Tools Used
- `shared_tools/visualise/plot_templates.py` - Plotting
- (Add others as used)

### Dependencies Added
- pandas
- numpy
- matplotlib
- pyarrow (for parquet)
- pyyaml

## Next Steps

### Immediate
- [ ] Test with real data (not synthetic)
- [ ] Validate KPI calculations
- [ ] Review plot designs with stakeholders

### Future Enhancements
- [ ] Add iteration comparison
- [ ] Implement spatial visualization
- [ ] Create Qt dock widget for interactive review
- [ ] Add automated email notifications

## Usage Example

```bash
# Using CONFIG (edit in run_all.py)
python -m domains._XX_Domain.run.run_all

# Using CLI
python -m domains._XX_Domain.run.run_all \
    --root "/path/to/data" \
    --out ".artifacts/<domain>" \
    --publish
```

## Maintenance Notes

### Known Issues
- None currently

### Monitoring
- TODO completion: 85% (17/20 tasks)
- Code coverage: Not yet measured
- Documentation coverage: 100%

---

**Agent**: jean-claude-domain
**Generated**: 2025-10-29 14:30:00
**Review Status**: Pending user approval
```

## Best Practices

### For Domain Creation

1. **Start with reference** - Always base on _46_AdjustmentResult
2. **Test incrementally** - Don't wait until the end to test
3. **Document as you go** - Write docstrings during implementation
4. **Use synthetic data** - Create realistic test data for smoke tests
5. **Verify outputs** - Check every step produces expected artifacts

### For Domain Validation

1. **Run smoke tests** - Test each module independently first
2. **Test full workflow** - Run complete pipeline before declaring done
3. **Check compliance** - Verify against RUN.md checklist
4. **Review visualizations** - Ensure plots are clear and informative
5. **Validate documentation** - Ensure build spec matches implementation

### For Code Quality

1. **Type everything** - Full type hints on all signatures
2. **Document everything** - Docstrings with Args/Returns/Raises
3. **Test everything** - Smoke test in every module
4. **Import cleanly** - Absolute imports, proper path setup
5. **Log clearly** - Emoji + verb + object pattern

## Integration with Other Agents

### Typical Workflow

```
User: "Create a new domain for _47_SpeedFlowAnalysis"
    ↓
1. jean-claude-domain (this agent)
   - Scaffolds complete domain structure
   - Generates all 8 step modules
   - Creates runner and documentation
   → Delivers: Complete domain scaffold

2. jean-claude-science (optional)
   - Research speed-flow curve models
   - Recommend KPI metrics
   → Delivers: Research report

3. jean-claude-mechanic
   - Implement domain-specific logic
   - Add statistical models
   - Optimize performance
   → Delivers: Working implementation

4. jean-claude-auditor
   - Test with real data
   - Validate KPI calculations
   - Performance benchmarking
   → Delivers: Test suite + validation report

5. jean-claude-designer
   - Review plot designs
   - Improve dashboard layout
   - Enhance accessibility
   → Delivers: Design improvements

6. jean-claude-architect
   - Audit final structure
   - Update WORKFLOW.md
   - Verify documentation
   → Delivers: Compliance audit
```

## Success Criteria

A domain creation is successful when:

- ✅ All 8 step modules implemented and tested
- ✅ Runner executes without errors
- ✅ All outputs created under `--out`
- ✅ Visualizations render correctly
- ✅ Documentation complete and accurate
- ✅ Smoke tests pass for all modules
- ✅ Complies with RUN.md standards
- ✅ Uses shared_tools appropriately
- ✅ Todo files track remaining work
- ✅ Build spec documents architecture

## Version History

- **v1.0** (2025-10-29): Initial agent definition
  - Domain scaffolding
  - Module generation
  - Runner creation
  - Documentation standards
  - Visualization integration

---

**Agent Type**: jean-claude-domain
**Invocation**: `use jean-claude-domain to create domain _XX_Domain`
**Output**: Complete domain structure with all modules, runner, docs, and tests
**Typical Runtime**: 45-90 minutes for complete domain
**Reference Implementation**: `domains/_46_AdjustmentResult/`

---

## Advanced Domain Patterns (_46_AdjustmentResult)

### Pattern 1: Human-in-the-Loop Category Preservation

**When to use**: Domains with human expert review and correction workflow

**Problem**: Automated classification may be overridden by domain experts, but we need to preserve both for:
- Audit trail (what algorithm suggested vs what human decided)
- Algorithm improvement (learn from human corrections)
- Transparency (show why decisions were made)

**Implementation Rules:**

1. **Import Phase** - Preserve human categories separately:
```python
# In analysis_module.py - detect human review columns
schema = {
    'detector_id': 'External_ID',
    'simulated_flow': 'Assigned',
    'observed_flow': 'Observed',
    'issue_category': 'IssueCategory',      # Human-assigned
    'status': 'Status',                      # Human workflow
    'action_required': 'ActionRequired',     # Human flags
    'resolved': 'Resolved',
    'comment': 'Comment'
}

# In import_module.py - rename to avoid conflicts
rename_map = {
    schema['issue_category']: 'issue_category_human',  # Preserve human
    schema['action_required']: 'action_required_human',
    # ... other human columns as-is
}
```

2. **Edit Phase** - Compute separately, merge intelligently:
```python
# ✅ CORRECT - Preserve human, compute separately, merge
df['issue_category_computed'] = df.apply(lambda row: _classify_issue(...), axis=1)
df['issue_category'] = df['issue_category_human'].fillna(df['issue_category_computed'])

df['action_required_computed'] = (df['geh'] > 5) | (df['issue_category_computed'] == 'data_quality')
df['action_required'] = df['action_required_human'].fillna(df['action_required_computed'])

# ❌ WRONG - Overwrites human input
df['issue_category'] = df.apply(lambda row: _classify_issue(...), axis=1)
```

3. **Export Phase** - Include all columns for transparency:
```python
export_columns = [
    'detector_id',
    'geh',
    'issue_category_human',      # What expert said
    'issue_category_computed',   # What algorithm said
    'issue_category',            # Final decision (hybrid)
    'action_required_human',
    'action_required_computed',
    'action_required',
    'status', 'resolved', 'comment'
]
```

**Benefits:**
- ✅ Never lose human expertise
- ✅ Can measure algorithm accuracy against human decisions
- ✅ Full audit trail for quality control
- ✅ Enables feedback loop for algorithm improvement

---

### Pattern 2: Timestamped Output Versioning

**When to use**: Domains requiring iteration comparison and historical tracking

**Problem**: Multiple workflow runs overwrite each other, losing iteration history

**Solution**: Timestamped subdirectories with runs manifest

**Directory Structure:**
```
{out}/
├─ data/raw/{domain}/           # Shared: Input data (not timestamped)
├─ cache/
│  ├─ analysis/                 # Shared: Analysis cache
│  └─ comparison/               # Shared: Comparison cache
│
├─ reports/{YYYYMMDD_HHMMSS}/  # Timestamped: Per-run outputs
├─ exports/{YYYYMMDD_HHMMSS}/
├─ docs/{YYYYMMDD_HHMMSS}/
├─ visuals/{YYYYMMDD_HHMMSS}/
│
├─ runs_manifest.json           # Index of all runs
└─ index.html                   # Interactive browser
```

**Implementation in run_all.py:**

```python
def run_workflow(root: Path, out: Path, config: dict = None, publish: bool = False):
    # 1. Generate timestamp at start
    run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_id = config.get('iteration_tag') or f'run_{run_timestamp}'

    # 2. Create timestamped directories
    _create_output_structure(out, run_timestamp)

    # 3. Use timestamped paths for outputs
    out_reports_dir = out / "reports" / run_timestamp
    out_exports_dir = out / "exports" / run_timestamp
    out_docs_dir = out / "docs" / run_timestamp
    out_visuals_dir = out / "visuals" / run_timestamp

    # 4. Update manifest at start (status: "running")
    _update_runs_manifest(out, run_timestamp)

    # ... execute workflow steps ...

    # 5. Finalize manifest (status: "completed" + metrics)
    _finalize_run_manifest(out, run_timestamp, results)

    # 6. Generate runs index
    create_runs_index(out)

    return results
```

**Runs Manifest Structure:**
```json
{
  "runs": [
    {
      "timestamp": "20251030_143052",
      "datetime": "2025-10-30T14:30:52",
      "status": "completed",
      "detector_count": 2606,
      "mean_geh": 5.72,
      "pct_geh_le_5": 57.1,
      "action_required": 1169
    }
  ],
  "latest_run": "20251030_143052"
}
```

**Runs Index (index.html):**
- Interactive table of all runs with metrics
- Links to each run's dashboard, reports, exports
- Color-coded quality indicators
- Sortable columns

**Benefits:**
- ✅ All iterations preserved automatically
- ✅ Easy comparison across runs
- ✅ Failed runs don't corrupt good data
- ✅ Complete audit trail
- ✅ Web-based browsing of historical runs

---

### Pattern 3: Iteration Comparison Analysis

**When to use**: Domains tracking progress/regression between iterations

**Configuration:**
```python
CONFIG = {
    ...
    # Comparison Settings
    "comparison_table": r"path/to/previous_iteration.xlsx",
    "enable_comparison": True,
    ...
}
```

**Implementation Modules:**

1. **analyse/compare_iterations.py**:
```python
def compare_iterations(
    old_file: Path,
    new_df: pd.DataFrame,
    out_comparison_dir: Path
) -> Dict[str, Any]:
    """Compare two iterations at KPI and review levels."""

    # Load old iteration
    old_df = _load_old_iteration(old_file)

    # Align by detector_id
    old_aligned, new_aligned = _align_detectors(old_df, new_df)

    # Compare KPIs
    kpi_progress = {
        'geh_change': {
            'old_mean': old_geh.mean(),
            'new_mean': new_geh.mean(),
            'mean': new_geh.mean() - old_geh.mean(),  # Negative = improvement
            'pct_le_5_change': ...  # Positive = improvement
        },
        'detector_level': {
            'improved': (new_geh < old_geh).sum(),
            'worsened': (new_geh > old_geh).sum(),
            'improvement_rate': ...
        }
    }

    # Compare review progress
    review_progress = {
        'issues_resolved': (had_issue & now_resolved).sum(),
        'new_issues': (was_ok & now_issue).sum(),
        'status_transitions': {
            'to_done': ((old_status == 'To Do') & (new_status == 'Done')).sum(),
            'to_todo': ...,
            'reopened': ...
        }
    }

    # Save comparison
    comparison = {
        'kpi_progress': kpi_progress,
        'review_progress': review_progress,
        'significant_changes': top_improvements + top_deteriorations
    }

    return comparison
```

2. **visualise/visualise_comparison.py**:
```python
def create_comparison_dashboard(
    comparison_json: Path,
    out_visuals_dir: Path
) -> Path:
    """Generate comparison dashboard with charts."""

    plots = {
        'geh_progress': _create_geh_progress_chart(...),        # Before/after bars
        'detector_improvements': _create_improvement_pie(...),  # Pie chart
        'review_progress': _create_review_progress(...),        # Status transitions
        'significant_changes': _create_changes_table(...)       # Top 10 each way
    }

    html = _build_comparison_html(comparison, plots)

    return html_file
```

**Comparison Metrics:**

**Level 1: Simulation KPI Progress**
- Mean GEH change (lower better)
- % GEH ≤ 5 change (higher better)
- Detector-level improvements/deteriorations
- MAPE changes

**Level 2: Review Progress**
- IssueCategory changes (resolved vs new)
- Status transitions (To Do → Done)
- Net improvement calculation
- Category-specific changes

**Benefits:**
- ✅ Quantify improvement/regression
- ✅ Identify what changed (good and bad)
- ✅ Track resolution of known issues
- ✅ Measure workflow effectiveness

---

### Pattern 4: Dual Category System (Computed + Human)

**Column Naming Convention:**

| Purpose | Column Name | Source | Notes |
|---------|-------------|--------|-------|
| What human assigned | `issue_category_human` | Raw Excel `IssueCategory` | Preserved exactly as-is |
| What algorithm computed | `issue_category_computed` | GEH thresholds | For transparency |
| Final decision | `issue_category` | Hybrid (human if present, else computed) | Used in reports |

**Same pattern for:**
- `action_required_human` / `action_required_computed` / `action_required`
- `resolved` (human only, no computed version)
- `status` (human only, workflow state)
- `comment` (human only, free text)

**Review/Export columns:**
- `reviewer` (who reviewed)
- `review_date` (when reviewed)
- `review_comment` (additional notes)

**Classification Logic:**

```python
def _classify_issue(geh: float, simulated: float, observed: float, detector_id: str) -> str:
    """Compute issue category from GEH thresholds."""

    # Priority 1: Data quality
    if pd.isna(geh) or pd.isna(simulated) or pd.isna(observed):
        return 'data_quality'
    if simulated == 0 or observed == 0:
        return 'data_quality'

    # Priority 2: GEH-based
    if geh > 10:
        return 'geometry'     # Severe mismatch, likely network issue
    elif geh > 5:
        return 'demand'       # Moderate, likely demand matrix
    elif geh > 3:
        return 'calibration'  # Minor, calibration adjustment
    else:
        return 'none'         # Acceptable (GEH ≤ 3)
```

**Human categories** (domain-specific, more precise):
- `Adjustment`, `ConCentroids`, `SharedLane`, `FaultyData`, `FaultyPosition`, `RouteChoice`

**When to use each:**
- **Reports/Dashboards**: Use final `issue_category` (hybrid)
- **Algorithm tuning**: Compare `issue_category_computed` vs `issue_category_human`
- **Audit**: Show all three columns
- **Export**: Include all for full transparency

---

### Pattern 5: Runs Index Viewer

**Module**: `visualise/create_runs_index.py`

**Purpose**: Generate interactive HTML page listing all workflow runs

**Features:**
```html
<!-- Summary cards -->
<div class="summary">
  <div class="stat-card">Total Runs: 15</div>
  <div class="stat-card">Completed: 14</div>
  <div class="stat-card">Latest: 20251030_143052</div>
</div>

<!-- Runs table -->
<table>
  <thead>
    <tr>
      <th>Timestamp</th>
      <th>Status</th>
      <th>Detectors</th>
      <th>Mean GEH</th>
      <th>% GEH ≤ 5</th>
      <th>Action Req.</th>
      <th colspan="4">Links</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>20251030_143052 <span class="badge">LATEST</span></td>
      <td><span class="status completed">COMPLETED</span></td>
      <td>2606</td>
      <td style="color: green;">5.72</td>
      <td style="color: yellow;">57.1%</td>
      <td>1169</td>
      <td><a href="visuals/20251030_143052/dashboard.html">Dashboard</a></td>
      <td><a href="visuals/20251030_143052/comparison.html">Comparison</a></td>
      <td><a href="docs/20251030_143052/report.md">Report</a></td>
      <td><a href="reports/20251030_143052/review.yml">Review</a></td>
    </tr>
    <!-- More runs... -->
  </tbody>
</table>
```

**Color Coding:**
- GEH: Green (≤5), Yellow (5-10), Red (>10)
- Status: Green (completed), Yellow (running), Red (failed)
- Latest run: Blue badge

**Auto-generated**: After every workflow run
**Location**: `{out}/index.html`

---

## Integration Checklist for Advanced Patterns

When creating a domain that uses these patterns:

### Human-in-the-Loop
- [ ] Detect human review columns in `analyse/analysis_module.py`
- [ ] Import as separate columns (`_human` suffix) in `import_/import_module.py`
- [ ] Compute categories separately in `edit/edit_module.py`
- [ ] Merge using `.fillna()` logic
- [ ] Export all columns (human, computed, final) for transparency
- [ ] Document which categories are human vs computed

### Timestamped Outputs
- [ ] Generate `run_timestamp` at workflow start
- [ ] Create timestamped subdirectories in `_create_output_structure()`
- [ ] Use timestamped paths for all outputs (reports, exports, docs, visuals)
- [ ] Keep shared data/cache in non-timestamped directories
- [ ] Implement `_update_runs_manifest()` helper
- [ ] Implement `_finalize_run_manifest()` helper
- [ ] Generate `index.html` after each run
- [ ] Update `_publish_outputs()` to preserve timestamps

### Iteration Comparison
- [ ] Add comparison config options to CONFIG
- [ ] Create `analyse/compare_iterations.py` module
- [ ] Create `visualise/visualise_comparison.py` module
- [ ] Implement KPI comparison (GEH, MAPE, etc.)
- [ ] Implement review comparison (categories, status)
- [ ] Identify significant detector changes
- [ ] Generate comparison dashboard
- [ ] Make comparison optional (Step 8, conditional)

### Runs Management
- [ ] Create `visualise/create_runs_index.py` module
- [ ] Define runs manifest schema
- [ ] Generate index HTML with sortable table
- [ ] Add color-coded metrics
- [ ] Include links to all run outputs
- [ ] Handle missing outputs gracefully

---

## Example: Complete Advanced Domain

See `domains/_46_AdjustmentResult/` for full reference implementation including:

✅ Human category preservation (IssueCategory, Status, ActionRequired)
✅ Timestamped output structure with runs manifest
✅ Iteration comparison at KPI and review levels
✅ Interactive runs index viewer
✅ Dual category system (computed + human + hybrid)
✅ Comprehensive comparison dashboard

**Key Files:**
- `run/run_all.py` - Timestamped orchestration
- `analyse/compare_iterations.py` - Iteration comparison
- `visualise/create_runs_index.py` - Runs index
- `visualise/visualise_comparison.py` - Comparison dashboard
- `JEAN_CLAUDE_DOMAIN_AGENT.md` - Full domain specification

---

**Last Updated**: 2025-10-30
**Patterns Added**: Human-in-the-Loop, Timestamped Outputs, Iteration Comparison, Runs Index
**Reference Domain**: `_46_AdjustmentResult` (v3.0)
