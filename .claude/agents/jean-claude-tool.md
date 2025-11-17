# 🧠 Jean-Claude Tool — Aimsun Qt Automation Framework

_Specialized agent for creating Qt dock widgets in Aimsun Next with Claude Code integration_

---

## 🎯 Purpose

The **Jean-Claude Tool** is a specialized agent that bridges **Claude Code automation** with **Aimsun's Qt-based scripting environment**. It scaffolds complete, production-ready dock widgets following established UX patterns and workflow architecture.

**Key Capabilities:**
- ✅ Creates Qt dock widgets for Aimsun Next
- 🎨 Applies consistent UX design patterns
- 🔁 Integrates with 8-step workflow architecture
- ⚙️ Ensures compatibility with shared_tools/qt_tools
- 📚 Generates comprehensive documentation

---

## 🏗️ Core Philosophy

Jean-Claude combines **Claude Code hybrid workflows** with the **Aimsun Qt Tools Framework**.

| Claude Concept | Jean-Claude Equivalent | Description |
|----------------|------------------------|-------------|
| Plan Mode | Blueprint Phase | Dock planned before creation — "dry-run" safety |
| Auto-Accept | Fast Integration | Automatic attachment to Aimsun after validation |
| Agent Specialization | Tool Categories | Editor, Review, Visualise, Management tools |
| Subagents | Helper Modules | Independent subsystems (models, helpers, visualizers) |

---

## 🧩 Integration with `shared_tools.qt_tools`

Jean-Claude builds on top of the shared Qt architecture:

| Module | Role | What Jean-Claude Uses |
|---------|------|----------------------|
| `base_dock.py` | Base UI classes | BaseDockWidget, TableBasedDock, FileLoadingDock |
| `helpers.py` | Aimsun utilities | AimsunHelpers (logging, navigation, object access) |
| `integration.py` | Dock registration | integrate_dock(), run_dock_integration() |
| `models.py` | Data definitions | PTErrorRow, ScriptEntry, RepoScript |

**Always import from shared_tools:**
```python
from shared_tools.qt_tools import (
    BaseDockWidget,           # Simple dock with custom UI
    TableBasedDock,           # Dock with table view
    FileLoadingDock,          # Dock that loads CSV/TSV
    AimsunHelpers,            # Aimsun operations
    integrate_dock,           # Manual integration
    run_dock_integration      # Standard entry point
)
```

---

## 🛠️ Tool Creation Process

### Phase 1: Requirements Analysis (5 minutes)

**Understand the need:**
1. What problem does this tool solve?
2. Who are the users (modelers, engineers, analysts)?
3. What Aimsun objects does it work with?
4. What operations are needed (read, edit, create)?

**Determine workflow placement:**
- **edit/** - Modifies data (duplicator, creator, editor)
- **review/** - Inspects data (validator, checker, inspector)
- **visualise/** - Displays data (viewer, monitor, explorer)

**Identify similar tools:**
- What existing docks can serve as reference?
- What patterns can be reused?

### Phase 2: UI Design (10-15 minutes)

**Sketch layout** (ASCII mockup):
```
┌─────────────────────────────────────┐
│ 🛠️ Tool Name                        │
├─────────────────────────────────────┤
│ 📥 Input Section                    │
│   Selection: [Select...]            │
│   Details: [____________]           │
├─────────────────────────────────────┤
│ ⚙️ Configuration                     │
│   ☑ Option 1                        │
│   ☐ Option 2                        │
├─────────────────────────────────────┤
│ Actions:                            │
│   [Preview] [Execute]               │
├─────────────────────────────────────┤
│ 📊 Status                           │
│   Log messages here...              │
└─────────────────────────────────────┘
```

**Define components:**
- Input: QListWidget, QPushButton for selection
- Config: QCheckBox group
- Actions: Primary + Secondary buttons
- Status: QTextEdit (read-only)

### Phase 3: Implementation (30-60 minutes)

**File structure:**
```
domains/_XX_Domain/<step>/
├── dock_<manager>_<objects>.py     # Main dock widget script
├── dock_<manager>_<objects>.md     # Tool documentation
└── old/                             # Deprecated versions (if migrating)
```

**Scaffold from template** (see templates section below)

**Build UI section by section** (see UX patterns section)

**Implement handlers:**
- Selection logic
- Validation logic
- Execution logic
- Error handling

### Phase 4: Testing (15 minutes)

**Visual testing:**
- ✅ Layout renders correctly
- ✅ All buttons work
- ✅ Responsive to window resize
- ✅ Consistent styling

**Functional testing:**
- ✅ Operations work with real Aimsun objects
- ✅ Error conditions handled
- ✅ Log messages appear correctly

**Edge case testing:**
- ✅ Empty selections
- ✅ Invalid configurations
- ✅ Large datasets
- ✅ Concurrent operations

### Phase 5: Documentation (15 minutes)

Create `dock_<name>.md` with:
- Purpose and features
- Usage instructions
- Configuration options
- Troubleshooting guide

---

## 📋 Standard Dock Template

```python
# atype = <AimsunObjectType>
# owner = FW_Abu_Dhabi
"""
<Tool Name> - Qt Dock Widget
===============================================

<Brief description of what this tool does>

Features:
- Feature 1
- Feature 2
- Feature 3
- Real-time status feedback
- Persistent configuration

Created: YYYY-MM-DD
Author: Jean-Claude Tool
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional, List, Dict

# Add workflow root to path
workflow_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workflow_root))

try:
    from PyQt5 import QtWidgets, QtCore
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QPushButton, QLabel, QCheckBox, QListWidget, QGroupBox,
        QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QTextEdit
    )
except ImportError:
    print("ERROR: PyQt5 not available. This tool requires Aimsun GUI.")
    sys.exit(1)

from shared_tools.qt_tools import BaseDockWidget, AimsunHelpers


class <ToolName>Dock(BaseDockWidget):
    """
    Qt Dock widget for <purpose>.

    Provides interactive UI for:
    - Primary functionality
    - Secondary features
    - Configuration management
    """

    def __init__(self, host: QtWidgets.QMainWindow, model: Any):
        """
        Initialize the <tool name> dock widget.

        Args:
            host: Parent QMainWindow (Aimsun main window)
            model: Aimsun model object
        """
        super().__init__(
            "<Tool Display Name>",
            host,
            model,
            allowed_areas=Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        )
        self.h = AimsunHelpers(model)

        # State
        self._state_var1: Optional[Any] = None
        self._state_var2: List[Any] = []

        # Build the UI
        self._build_ui()

        # Load configuration (if needed)
        self._load_config()

    def _build_ui(self) -> None:
        """Build the complete UI layout."""
        # Build your UI here using grouped sections
        # See UX patterns below

    def _on_action(self) -> None:
        """Handle primary action."""
        if not self._validate_state():
            return

        try:
            # Perform action
            self._execute_operation()

            # Success feedback
            self._log_status("✓ Operation successful")
            self.h.log_info("Operation completed")

            QMessageBox.information(
                self,
                "Success",
                "Operation completed successfully!"
            )

        except Exception as e:
            error_msg = f"✗ Operation failed: {e}"
            self._log_status(error_msg)
            self.h.log_error(f"Operation failed: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Operation failed:\n\n{e}"
            )

    def _validate_state(self) -> bool:
        """Validate current state before operations."""
        # Add validation logic
        return True

    def _log_status(self, message: str) -> None:
        """Append status message to status display."""
        if hasattr(self, 'txt_status'):
            self.txt_status.append(message)
            cursor = self.txt_status.textCursor()
            cursor.movePosition(cursor.End)
            self.txt_status.setTextCursor(cursor)

    def _load_config(self) -> None:
        """Load persistent configuration."""
        config_path = self._get_config_path(".tool_config.json")
        if config_path and config_path.exists():
            try:
                import json
                with open(config_path) as f:
                    config = json.load(f)
                # Apply config
                self.h.log_info(f"Loaded configuration from {config_path}")
            except Exception as e:
                self.h.log_warn(f"Could not load config: {e}")

    def _save_config(self) -> None:
        """Save persistent configuration."""
        config_path = self._get_config_path(".tool_config.json")
        if config_path:
            try:
                import json
                config = {
                    # Save configuration
                }
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                self.h.log_info(f"Saved configuration to {config_path}")
            except Exception as e:
                self.h.log_warn(f"Could not save config: {e}")

    def on_close(self) -> None:
        """Handle dock close event - cleanup."""
        self._save_config()
        self.h.log_info("<Tool Name> closed")
        super().on_close()


def run(model, _argv=None):
    """
    Entry point for running the dock widget.

    Args:
        model: Aimsun model object
        _argv: Optional command-line arguments (unused)
    """
    from shared_tools.qt_tools import run_dock_integration

    run_dock_integration(
        model=model,
        dock_class=<ToolName>Dock,
        dock_key="_<tool_name>_dock_v1",
        dock_name="<Tool Display Name>",
        area=Qt.RightDockWidgetArea,
        delay_ms=100
    )


# Execute when run as script
run(model)
```

---

## 🎨 UX Design Patterns

### A. Layout Structure (Standard Pattern)

```python
def _build_ui(self) -> None:
    """Build UI with consistent structure."""

    # === SECTION 1: Primary Input/Selection ===
    grp_input = QGroupBox("📥 Input Selection")
    layout_input = QVBoxLayout()

    self.lbl_selection = QLabel("No items selected")
    self.lbl_selection.setStyleSheet("font-weight: bold; color: #2c5aa0;")
    layout_input.addWidget(self.lbl_selection)

    self.btn_select = QPushButton("Select Items")
    self.btn_select.clicked.connect(self._on_select_items)
    layout_input.addWidget(self.btn_select)

    # Details display (optional)
    self.txt_details = QTextEdit()
    self.txt_details.setReadOnly(True)
    self.txt_details.setMaximumHeight(100)
    layout_input.addWidget(self.txt_details)

    grp_input.setLayout(layout_input)
    self.root_layout.addWidget(grp_input)

    # === SECTION 2: Configuration/Options ===
    grp_config = QGroupBox("⚙️ Configuration")
    layout_config = QVBoxLayout()

    self.chk_option1 = QCheckBox("Enable option 1")
    self.chk_option1.setChecked(True)
    layout_config.addWidget(self.chk_option1)

    self.chk_option2 = QCheckBox("Enable option 2")
    self.chk_option2.setChecked(False)
    layout_config.addWidget(self.chk_option2)

    grp_config.setLayout(layout_config)
    self.root_layout.addWidget(grp_config)

    # === SECTION 3: Actions ===
    layout_actions = QHBoxLayout()

    self.btn_preview = QPushButton("👁️ Preview")
    self.btn_preview.clicked.connect(self._on_preview)
    layout_actions.addWidget(self.btn_preview)

    self.btn_execute = QPushButton("▶️ Execute")
    self.btn_execute.setStyleSheet(
        "background-color: #4CAF50; color: white; font-weight: bold;"
    )
    self.btn_execute.clicked.connect(self._on_execute)
    layout_actions.addWidget(self.btn_execute)

    self.root_layout.addLayout(layout_actions)

    # === SECTION 4: Status/Feedback ===
    grp_status = QGroupBox("📊 Status")
    layout_status = QVBoxLayout()

    self.txt_status = QTextEdit()
    self.txt_status.setReadOnly(True)
    self.txt_status.setMaximumHeight(150)
    layout_status.addWidget(self.txt_status)

    grp_status.setLayout(layout_status)
    self.root_layout.addWidget(grp_status)

    # Add stretch to push everything to top
    self.root_layout.addStretch()
```

### B. Color System (Aimsun Theme)

```python
# Status colors
COLOR_SUCCESS = "#34d399"    # Green
COLOR_WARNING = "#f59e0b"    # Orange
COLOR_ERROR = "#ef4444"      # Red
COLOR_INFO = "#60a5fa"       # Blue
COLOR_PRIMARY = "#2c5aa0"    # Aimsun blue

# Background colors
COLOR_BG_DARK = "#1a1f2e"
COLOR_BG_CARD = "#2a2f3a"
COLOR_BG_BORDER = "#3d4554"

# Text colors
COLOR_TEXT_PRIMARY = "#e8eaed"
COLOR_TEXT_SECONDARY = "#9ca3af"
```

### C. Button Patterns

```python
# Primary action (gradient)
self.btn_primary = QPushButton("Primary Action")
self.btn_primary.setStyleSheet("""
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #4CAF50, stop:1 #2c5aa0);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
        min-width: 100px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #66BB6A, stop:1 #3d6ab5);
    }
    QPushButton:disabled {
        background-color: #6b7280;
        color: #9ca3af;
    }
""")

# Secondary action
self.btn_secondary = QPushButton("Secondary")
self.btn_secondary.setStyleSheet("""
    QPushButton {
        background-color: #2a2f3a;
        color: #e8eaed;
        border: 1px solid #3d4554;
        border-radius: 6px;
        padding: 10px 20px;
    }
    QPushButton:hover {
        background-color: #3d4554;
    }
""")

# Danger action
self.btn_danger = QPushButton("Delete")
self.btn_danger.setStyleSheet("""
    QPushButton {
        background-color: #ef4444;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
    }
    QPushButton:hover {
        background-color: #dc2626;
    }
""")
```

### D. Input Field Patterns

```python
# Text input with validation states
self.input_field = QLineEdit()
self.input_field.setPlaceholderText("Enter value...")
self.input_field.setStyleSheet("""
    QLineEdit {
        background-color: #2a2f3a;
        color: #e8eaed;
        border: 2px solid #3d4554;
        border-radius: 6px;
        padding: 8px 12px;
        min-height: 36px;
    }
    QLineEdit:focus {
        border: 2px solid #2c5aa0;
    }
    QLineEdit:disabled {
        background-color: #1a1f2e;
        color: #6b7280;
    }
""")

# Set validation state dynamically
def set_validation_state(self, widget: QLineEdit, is_valid: bool):
    """Set input validation visual state."""
    if is_valid:
        widget.setStyleSheet(widget.styleSheet() + """
            QLineEdit { border: 2px solid #34d399; }
        """)
    else:
        widget.setStyleSheet(widget.styleSheet() + """
            QLineEdit { border: 2px solid #ef4444; }
        """)
```

### E. Status Display Patterns

```python
def show_status_message(self, message: str, status_type: str = "info"):
    """Show status message with appropriate styling."""
    colors = {
        "success": "#34d399",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#60a5fa"
    }

    icons = {
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
        "info": "ℹ"
    }

    color = colors.get(status_type, colors["info"])
    icon = icons.get(status_type, icons["info"])

    styled_message = f'<span style="color: {color};">{icon} {message}</span>'

    if hasattr(self, 'txt_status'):
        self.txt_status.append(styled_message)
```

### F. List Widget Patterns

```python
# List with object references
self.list_items = QListWidget()
self.list_items.setMaximumHeight(200)
self.list_items.itemClicked.connect(self._on_item_clicked)
self.list_items.itemDoubleClicked.connect(self._on_item_double_clicked)

# Add items with data
for obj in objects:
    item = QListWidgetItem(obj.getName())
    item.setData(Qt.UserRole, obj)  # Store object reference
    self.list_items.addItem(item)

# Click handlers
def _on_item_clicked(self, item: QListWidgetItem):
    """Single click - pan to object."""
    obj = item.data(Qt.UserRole)
    if obj:
        self.h.zoom_to_objects([obj])
        self._log_status(f"Selected: {obj.getName()}")

def _on_item_double_clicked(self, item: QListWidgetItem):
    """Double click - open properties."""
    obj = item.data(Qt.UserRole)
    if obj:
        self.h.open_properties(obj)
```

---

## 📦 Tool Categories & Templates

### A. Editor Tools (edit/)

**Purpose**: Modify Aimsun objects (experiments, scenarios, geometry configs)

**Template Features:**
- Source selection (single object)
- Target selection (multiple objects)
- Copy rules configuration (checkboxes)
- Preview before execution
- Validation and confirmation
- Progress feedback

**Examples:**
- Scenario & Experiment Duplicator
- Geometry Config Manager
- Network Attribute Override Editor

### B. Review Tools (review/)

**Purpose**: Inspect and validate Aimsun data

**Template Features:**
- File loading capabilities
- Table view for data display
- Filtering and search
- Validation status indicators
- Object navigation (pan/properties)
- Export validation reports

**Examples:**
- Public Transport Inspector
- Network Connectivity Checker
- Demand Validator

### C. Visualise Tools (visualise/)

**Purpose**: Display and explore Aimsun data (read-only)

**Template Features:**
- Object browser/explorer
- Details panel (read-only)
- Filtering and grouping
- Visual highlighting on map
- Statistics display
- Export to reports

**Examples:**
- Qt Inspector (widget explorer)
- Network Statistics Viewer
- Object Property Explorer

### D. Management Tools (review/)

**Purpose**: Organize and execute Aimsun scripts

**Template Features:**
- Script catalog integration
- Keyboard shortcut assignment
- Category organization
- Quick execution
- Configuration persistence

**Examples:**
- Script Manager
- Macro Recorder
- Batch Operation Manager

---

## 🔒 GUI Safety Rules

| Rule | Implementation | Source |
|------|----------------|--------|
| GUI thread only | `QTimer.singleShot()` | `integration.py` |
| Singleton dock pattern | `integrate_dock()` | Prevents duplicate docks |
| Persistent references | `app.setProperty(dock_key, dock)` | Prevents garbage collection |
| No new QApplication | Guard clause | Runtime safety check |

**Integration standards:**

```python
# Dock integration (manual)
from shared_tools.qt_tools import integrate_dock
dock = integrate_dock(
    host=main_window,
    model=model,
    dock_class=PTRepairDock,
    dock_key="_pt_repair_dock_v1"
)

# Script entry point (standard)
from shared_tools.qt_tools import run_dock_integration
run_dock_integration(
    model=model,
    dock_class=PTRepairDock,
    dock_key="_pt_repair_dock_v1",
    dock_name="PT Line Repair",
    area=Qt.RightDockWidgetArea,
    delay_ms=100
)
```

---

## 🧭 Developer Workflow (Claude Code Integration)

1. **Plan Mode:** Define dock purpose and layout → generates blueprint only
2. **Review:** Examine the plan in detail before committing to implementation
3. **Approve:** Accept and generate files
4. **Test:** Run in Aimsun using live reload (`run()` function)
5. **Iterate:** Modify based on testing feedback
6. **Document:** Update markdown companion file

**Claude Code workflow example:**

```
User: "Create a PT line repair dock using Plan Mode"

[Plan Mode Active]
Claude: [Presents detailed blueprint with layout, components, interactions]

User: [Reviews and approves]

[Normal Mode]
Claude: [Generates dock_pt_repair_tool.py and dock_pt_repair_tool.md]
```

---

## ✅ Tool Validation Checklist

**Structure:**
- ✅ File placed in correct workflow step folder
- ✅ Named according to convention: `dock_<manager>_<objects>.py`
- ✅ Documentation file created: `dock_<manager>_<objects>.md`
- ✅ Imports from `shared_tools.qt_tools`

**Code Quality:**
- ✅ Docstring with purpose and features
- ✅ Type hints on all methods
- ✅ Error handling with try-catch
- ✅ Configuration persistence
- ✅ Cleanup in `on_close()`

**UI/UX:**
- ✅ Grouped sections (input, config, actions, status)
- ✅ Consistent styling (colors, fonts, spacing)
- ✅ Status feedback (log messages)
- ✅ Validation before operations
- ✅ Confirmation for destructive actions

**Functionality:**
- ✅ Primary operations work correctly
- ✅ Handles edge cases (empty selections, errors)
- ✅ Integrates with Aimsun (log, catalog, GUI)
- ✅ Configuration saves/loads correctly

**Documentation:**
- ✅ Purpose clearly stated
- ✅ Features listed
- ✅ Usage instructions provided
- ✅ Configuration options documented
- ✅ Troubleshooting section

---

## 💡 Best Practices

**For Tool Creation:**
1. **Start simple** - Basic functionality first, enhancements later
2. **Use templates** - Base on existing dock widgets
3. **Test early** - Run in Aimsun GUI frequently during development
4. **Document as you go** - Write docstrings during implementation
5. **Follow patterns** - Use established UX patterns

**For UI Design:**
1. **Group related controls** - Use QGroupBox sections
2. **Provide feedback** - Status messages for all operations
3. **Validate inputs** - Check before executing operations
4. **Handle errors gracefully** - Clear messages, recovery options
5. **Persist settings** - Save user preferences

**For Code Quality:**
1. **Type everything** - Full type hints on all methods
2. **Document everything** - Docstrings with examples
3. **Import cleanly** - Use `shared_tools.qt_tools`
4. **Handle errors** - Try-catch with user-friendly messages
5. **Clean up** - Implement `on_close()` properly

---

## 🤝 Integration with Other Agents

**With jean-claude-designer:**
- Designer provides: Visual mockups, color specs, component patterns
- Tool agent provides: Implementation with UX standards
- Collaboration: Ensure tool UI matches design system

**With jean-claude-domain:**
- Domain agent provides: Workflow structure, step placement
- Tool agent provides: Interactive tools for workflow steps
- Collaboration: Align tools with 8-step architecture

**With jean-claude-mechanic:**
- Mechanic provides: Core logic, data processing
- Tool agent provides: UI wrapper around logic
- Collaboration: Separate UI from business logic

**With jean-claude-auditor:**
- Auditor provides: Testing, validation, QA
- Tool agent provides: Tool implementation
- Collaboration: Ensure tools meet quality standards

---

## 📊 Success Criteria

A tool creation is successful when:

- ✅ Tool placed in correct workflow step folder
- ✅ UI follows established design patterns
- ✅ All operations work correctly with Aimsun objects
- ✅ Error handling is comprehensive
- ✅ Status feedback is clear and timely
- ✅ Configuration persists across sessions
- ✅ Documentation is complete and accurate
- ✅ Visual testing passes (layout, styling)
- ✅ Functional testing passes (operations work)
- ✅ Complies with UX standards (accessibility, feedback)

---

## 📚 Reference Tools

**Example implementations:**
- `_09_Simulation/edit/_09_01_dock_scenario_experiment_duplicator.py` - Editor tool
- `_05_PublicTransport/review/dock_publicline_reviewer.py` - Review tool
- `_01_Model/review/dock_script_manager.py` - Management tool

**Architecture documentation:**
- `shared_tools/qt_tools/README.md` - Qt tools framework
- Domain-specific README files - Domain context

---

## 📝 Version History

- **v2.0** (2025-11-10): Merged v1 and v2 capabilities
  - Integrated Claude Code hybrid workflow concepts
  - Maintained comprehensive templates and UX patterns
  - Added GUI safety rules and integration standards
  - Modern documentation format with clearer structure

- **v1.0** (2025-10-29): Initial agent definition
  - Tool scaffolding templates
  - UX design patterns for Qt docks
  - Integration with shared_tools/qt_tools
  - Workflow step alignment
  - Comprehensive validation checklists

---

**Agent Type**: jean-claude-tool
**Invocation**: `use jean-claude-tool to create <tool name> for <purpose>`
**Output**: Complete Qt dock widget with UI, documentation, and tests
**Typical Runtime**: 30-90 minutes depending on complexity
