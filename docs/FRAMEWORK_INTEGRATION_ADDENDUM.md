# FRAMEWORK Integration Addendum — Pulsus MCP

**Version:** 1.0
**Date:** November 2025
**Parent Document:** `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md`
**Framework Reference:** `aimsun-python-scripts/FW_Abu_Dhabi/framework/FRAMEWORK.md` (v3.1)

---

## 🎯 Purpose

This addendum extends the Pulsus MCP Unified Integration Plan to explicitly support the **8-step domain framework** used in traffic modeling projects (Aimsun, Abu Dhabi Mobility, etc.).

**Framework Pattern:**
```
acquire → analysis → import → edit → review → export → document → visualise
```

---

## 🏗️ Architecture Adaptations

### 1. Domain-Specific MCP Organization

**Add Framework Domain Layer** to Tier 3 (Customizable MCP):

```
pulsus/config/frameworks/
├── domain_framework/              # NEW - 8-step domain framework
│   ├── schema/
│   │   └── domain_schema.json     # Domain metadata + 8-step config
│   ├── templates/
│   │   ├── export/
│   │   │   └── template_export.yml
│   │   ├── document/
│   │   │   └── template_doc.md
│   │   ├── review/
│   │   │   └── template_review.yml
│   │   └── visualise/
│   │       └── template_visual.html
│   ├── domains/                   # Per-domain configs
│   │   ├── 0300_Geometry.json
│   │   ├── 0800_Detectors.json
│   │   ├── 4600_AdjustmentResult.json
│   │   └── ...
│   └── shared_tools/              # Tool wrappers
│       ├── common_analyser.py
│       ├── auto_importer.py
│       ├── ui_editor.py
│       ├── review_check.py
│       ├── export_to_GeoParquet.py
│       ├── generate_docs.py
│       └── html_visualiser.py
└── ... (existing custom_workflows, etc.)
```

### 2. Domain Configuration Schema

**File:** `pulsus/config/frameworks/domain_framework/schema/domain_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Framework Domain Configuration",
  "type": "object",
  "required": ["domain_id", "owner", "steps"],
  "properties": {
    "domain_id": {
      "type": "string",
      "pattern": "^[0-9]{4}_[A-Za-z]+$",
      "description": "Domain identifier (e.g., 0300_Geometry)"
    },
    "owner": {
      "type": "string",
      "enum": ["Common", "Aimsun", "AbuDhabiMobility"],
      "description": "Responsible entity"
    },
    "description": {
      "type": "string",
      "description": "Domain purpose and scope"
    },
    "dependencies": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Required upstream domains"
    },
    "steps": {
      "type": "object",
      "properties": {
        "acquire": {"$ref": "#/definitions/step"},
        "analysis": {"$ref": "#/definitions/step"},
        "import": {"$ref": "#/definitions/step"},
        "edit": {"$ref": "#/definitions/step"},
        "review": {"$ref": "#/definitions/step"},
        "export": {"$ref": "#/definitions/step"},
        "document": {"$ref": "#/definitions/step"},
        "visualise": {"$ref": "#/definitions/step"}
      },
      "required": ["acquire", "analysis", "import", "edit", "review", "export", "document", "visualise"]
    },
    "output_config": {
      "type": "object",
      "properties": {
        "staging_dir": {"type": "string"},
        "publish_dirs": {
          "type": "object",
          "properties": {
            "exports": {"type": "string"},
            "docs": {"type": "string"},
            "visuals": {"type": "string"},
            "reports": {"type": "string"}
          }
        }
      }
    }
  },
  "definitions": {
    "step": {
      "type": "object",
      "required": ["enabled", "tool"],
      "properties": {
        "enabled": {
          "type": "boolean",
          "description": "Whether this step is active"
        },
        "tool": {
          "type": "string",
          "description": "MCP tool or shared tool to use"
        },
        "config": {
          "type": "object",
          "description": "Step-specific configuration"
        },
        "inputs": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Input paths or previous step outputs"
        },
        "outputs": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Output artifacts"
        },
        "validation": {
          "type": "object",
          "description": "Validation rules for this step"
        }
      }
    }
  }
}
```

### 3. Example Domain Configuration

**File:** `pulsus/config/frameworks/domain_framework/domains/0300_Geometry.json`

```json
{
  "domain_id": "0300_Geometry",
  "owner": "Common",
  "description": "Road network geometry (sections, nodes, lanes, turn movements)",
  "dependencies": ["0100_Model"],

  "steps": {
    "acquire": {
      "enabled": true,
      "tool": "GeometryDataFetcher",
      "config": {
        "sources": [
          "gis/road_network.geojson",
          "survey/lane_configurations.csv"
        ],
        "filters": {
          "road_class": ["motorway", "trunk", "primary", "secondary"]
        }
      },
      "inputs": [],
      "outputs": ["data/raw/0300_Geometry/"]
    },

    "analysis": {
      "enabled": true,
      "tool": "common_analyser",
      "config": {
        "checks": [
          "topology_validity",
          "missing_attributes",
          "duplicate_geometries"
        ],
        "thresholds": {
          "max_gap_meters": 5.0,
          "min_lane_width": 2.5
        }
      },
      "inputs": ["data/raw/0300_Geometry/"],
      "outputs": ["cache/analysis/0300_Geometry_analysis.json"]
    },

    "import": {
      "enabled": true,
      "tool": "auto_importer",
      "config": {
        "aimsun_model": "AbuDhabi_2025.ang",
        "layer": "GKSection",
        "mapping": {
          "road_id": "External_ID",
          "geometry": "GEOMETRY",
          "lanes": "Number_of_Lanes"
        }
      },
      "inputs": ["cache/analysis/0300_Geometry_analysis.json"],
      "outputs": ["aimsun://GKSection"]
    },

    "edit": {
      "enabled": true,
      "tool": "ui_editor",
      "config": {
        "mode": "interactive",
        "checklist": [
          "Verify connectivity at intersections",
          "Check lane configurations",
          "Validate speed limits"
        ]
      },
      "inputs": ["aimsun://GKSection"],
      "outputs": ["aimsun://GKSection (updated)"]
    },

    "review": {
      "enabled": true,
      "tool": "review_check",
      "config": {
        "template": "templates/review/template_review.yml",
        "checks": [
          "topology_integrity",
          "attribute_completeness",
          "visual_inspection"
        ]
      },
      "inputs": ["aimsun://GKSection"],
      "outputs": ["reports/0300_Geometry_review.yml"]
    },

    "export": {
      "enabled": true,
      "tool": "export_to_GeoParquet",
      "config": {
        "format": "geoparquet",
        "crs": "EPSG:4326",
        "template": "templates/export/template_export.yml",
        "compression": "snappy"
      },
      "inputs": ["aimsun://GKSection"],
      "outputs": ["exports/0300_Geometry.parquet"]
    },

    "document": {
      "enabled": true,
      "tool": "generate_docs",
      "config": {
        "template": "templates/document/template_doc.md",
        "sections": [
          "Overview",
          "Data Sources",
          "Processing Steps",
          "Assumptions",
          "Quality Metrics",
          "Known Issues"
        ]
      },
      "inputs": [
        "cache/analysis/0300_Geometry_analysis.json",
        "reports/0300_Geometry_review.yml"
      ],
      "outputs": ["docs/0300_Geometry.md"]
    },

    "visualise": {
      "enabled": true,
      "tool": "html_visualiser",
      "config": {
        "template": "templates/visualise/template_visual.html",
        "plots": [
          "network_map",
          "lane_distribution",
          "road_class_breakdown"
        ],
        "interactive": true
      },
      "inputs": [
        "exports/0300_Geometry.parquet",
        "docs/0300_Geometry.md"
      ],
      "outputs": ["visuals/0300_Geometry_dashboard.html"]
    }
  },

  "output_config": {
    "staging_dir": "--out",
    "publish_dirs": {
      "exports": "/exports",
      "docs": "/docs",
      "visuals": "/visuals",
      "reports": "/reports"
    }
  }
}
```

---

## 🔧 New MCP Domains for Framework Integration

### 1. FrameworkDomainExecutor

**Location:** `pulsus/workflows/framework/domain_executor.py`

**Purpose:** Execute 8-step domain workflows based on JSON configuration

```python
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import json

from pulsus.mcp.core.base import MCPBase, MCPResponse
from pulsus.workflows.base import WorkflowBase, WorkflowStep

class FrameworkDomainExecutor(WorkflowBase):
    """
    Execute 8-step framework domain workflows.

    Loads domain configuration and executes all enabled steps in sequence.
    """

    def execute_domain(
        self,
        domain_id: str,
        config_path: Path,
        output_dir: Path,
        publish: bool = False
    ) -> MCPResponse:
        """
        Execute complete domain workflow.

        Args:
            domain_id: Domain identifier (e.g., "0300_Geometry")
            config_path: Path to domain JSON config
            output_dir: Staging directory (--out)
            publish: Whether to publish outputs to canonical locations

        Returns:
            MCPResponse with execution summary
        """
        try:
            # Load domain config
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Validate
            self._validate_config(config)

            # Create workflow steps
            steps = self._build_steps(config, output_dir)

            # Execute
            results = {}
            for step_name, step in steps.items():
                if step.enabled:
                    print(f"🔧 Step: {step_name}")
                    result = step.execute()
                    results[step_name] = result

                    if not result.success:
                        return MCPResponse.error(
                            f"Step {step_name} failed: {result.message}"
                        )

            # Publish if requested
            if publish:
                self._publish_outputs(config, output_dir)

            return MCPResponse.success(
                data={
                    "domain_id": domain_id,
                    "steps_completed": len(results),
                    "outputs": self._collect_outputs(results)
                },
                message=f"Domain {domain_id} completed successfully"
            )

        except Exception as e:
            return MCPResponse.error(f"Domain execution failed: {e}")

    def _build_steps(
        self,
        config: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, WorkflowStep]:
        """Build workflow steps from config."""

        step_order = [
            "acquire", "analysis", "import", "edit",
            "review", "export", "document", "visualise"
        ]

        steps = {}
        for step_name in step_order:
            step_config = config["steps"][step_name]

            if step_config["enabled"]:
                steps[step_name] = WorkflowStep(
                    name=step_name,
                    tool=step_config["tool"],
                    config=step_config["config"],
                    inputs=step_config["inputs"],
                    outputs=step_config["outputs"]
                )

        return steps

    def _publish_outputs(
        self,
        config: Dict[str, Any],
        staging_dir: Path
    ) -> None:
        """Publish staged outputs to canonical locations."""

        publish_dirs = config["output_config"]["publish_dirs"]

        # Copy exports
        self._safe_copy(
            staging_dir / "exports",
            Path(publish_dirs["exports"])
        )

        # Copy docs
        self._safe_copy(
            staging_dir / "docs",
            Path(publish_dirs["docs"])
        )

        # Copy visuals
        self._safe_copy(
            staging_dir / "visuals",
            Path(publish_dirs["visuals"])
        )

        # Copy reports
        self._safe_copy(
            staging_dir / "reports",
            Path(publish_dirs["reports"])
        )
```

### 2. AimsunConnector

**Location:** `pulsus/mcp/simple/aimsun_connector.py`

**Purpose:** Bridge to Aimsun Next Python API via ConsoleManager

```python
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

from pulsus.mcp.core.base import MCPBase, MCPResponse
from pulsus.mcp.core.decorators import write_safe
from pulsus.mcp.execution.console_manager import ConsoleManager

class AimsunConnector(MCPBase):
    """
    Connect to Aimsun Next for model manipulation.

    Capabilities:
    - open_model: Open Aimsun model
    - execute_script: Run Python script in Aimsun context
    - query_layer: Query Aimsun layer data
    - modify_objects: Modify Aimsun objects
    - close_model: Close model and save
    """

    def __init__(self):
        super().__init__()
        self.console_manager = ConsoleManager()
        self.aimsun_path = self._detect_aimsun_installation()

    @write_safe
    def open_model(
        self,
        model_path: Path,
        console: bool = True
    ) -> MCPResponse:
        """
        Open Aimsun model.

        Args:
            model_path: Path to .ang file
            console: Whether to open in console mode (vs GUI)

        Returns:
            MCPResponse with model handle
        """
        try:
            if not model_path.exists():
                return MCPResponse.error(f"Model not found: {model_path}")

            # Launch Aimsun
            if console:
                # Console mode (headless)
                command = [
                    str(self.aimsun_path),
                    "-script",
                    "-model", str(model_path)
                ]
            else:
                # GUI mode
                command = [str(self.aimsun_path), str(model_path)]

            response = self.console_manager.launch_console(
                command=command,
                working_dir=model_path.parent,
                console_title=f"Aimsun - {model_path.name}"
            )

            if response.success:
                return MCPResponse.success(
                    data={
                        "model_path": str(model_path),
                        "pid": response.data['pid'],
                        "mode": "console" if console else "gui"
                    },
                    message=f"Aimsun model opened: {model_path.name}"
                )
            else:
                return MCPResponse.error("Failed to launch Aimsun")

        except Exception as e:
            return MCPResponse.error(f"Aimsun open failed: {e}")

    @write_safe
    def execute_script(
        self,
        model_path: Path,
        script_path: Path,
        args: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """
        Execute Python script in Aimsun context.

        Args:
            model_path: Path to .ang file
            script_path: Path to Python script
            args: Script arguments as JSON

        Returns:
            MCPResponse with script output
        """
        try:
            # Build command
            command = [
                str(self.aimsun_path),
                "-script",
                str(script_path),
                "-model", str(model_path)
            ]

            if args:
                # Pass args as JSON
                import json
                command.extend(["-args", json.dumps(args)])

            # Execute
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=model_path.parent
            )

            if result.returncode == 0:
                return MCPResponse.success(
                    data={
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    },
                    message="Script executed successfully"
                )
            else:
                return MCPResponse.error(
                    f"Script failed: {result.stderr}"
                )

        except Exception as e:
            return MCPResponse.error(f"Script execution failed: {e}")

    def _detect_aimsun_installation(self) -> Path:
        """Detect Aimsun installation path."""

        # Common installation paths
        candidates = [
            Path("C:/Program Files/Aimsun/Aimsun Next/Aimsun_Next.exe"),
            Path("C:/Program Files (x86)/Aimsun/Aimsun Next/Aimsun_Next.exe"),
            Path("/Applications/Aimsun Next.app/Contents/MacOS/Aimsun Next")
        ]

        for path in candidates:
            if path.exists():
                return path

        raise RuntimeError("Aimsun installation not found")
```

### 3. GeoParquetExporter

**Location:** `pulsus/mcp/simple/geoparquet_exporter.py`

**Purpose:** Canonical export to GeoParquet format

```python
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import geopandas as gpd
import pandas as pd

from pulsus.mcp.core.base import MCPBase, MCPResponse
from pulsus.mcp.core.decorators import write_safe

class GeoParquetExporter(MCPBase):
    """
    Export spatial data to GeoParquet format (canonical).

    Capabilities:
    - export_geoparquet: Export GeoDataFrame to GeoParquet
    - validate_schema: Validate against template schema
    - convert_crs: Transform coordinate system
    """

    @write_safe
    def export_geoparquet(
        self,
        data: gpd.GeoDataFrame,
        output_path: Path,
        crs: str = "EPSG:4326",
        compression: str = "snappy",
        template_path: Optional[Path] = None
    ) -> MCPResponse:
        """
        Export GeoDataFrame to GeoParquet.

        Args:
            data: GeoDataFrame to export
            output_path: Output .parquet file path
            crs: Target CRS (default: WGS84)
            compression: Compression algorithm
            template_path: Optional template schema for validation

        Returns:
            MCPResponse with export summary
        """
        try:
            # Transform CRS if needed
            if data.crs != crs:
                data = data.to_crs(crs)

            # Validate against template
            if template_path:
                validation = self._validate_against_template(data, template_path)
                if not validation["valid"]:
                    return MCPResponse.error(
                        f"Schema validation failed: {validation['errors']}"
                    )

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Export
            data.to_parquet(
                output_path,
                compression=compression,
                index=False
            )

            # Calculate statistics
            stats = {
                "row_count": len(data),
                "column_count": len(data.columns),
                "crs": crs,
                "file_size_mb": output_path.stat().st_size / (1024 * 1024),
                "geometry_type": data.geometry.geom_type.unique().tolist()
            }

            return MCPResponse.success(
                data=stats,
                message=f"Exported {len(data)} features to {output_path.name}"
            )

        except Exception as e:
            return MCPResponse.error(f"GeoParquet export failed: {e}")

    def _validate_against_template(
        self,
        data: gpd.GeoDataFrame,
        template_path: Path
    ) -> Dict[str, Any]:
        """Validate data against template schema."""

        import yaml

        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)

        errors = []

        # Check required columns
        required_cols = template.get("required_columns", [])
        missing_cols = set(required_cols) - set(data.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")

        # Check data types
        # ... (implementation)

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
```

---

## 🔗 Integration Points

### 1. Workflow JSON Definition

**File:** `pulsus/workflows/definitions/framework_domain.json`

```json
{
  "name": "framework_domain_workflow",
  "description": "Execute 8-step framework domain",
  "version": "1.0",
  "mcp_domain": "FrameworkDomainExecutor",
  "parameters": {
    "domain_id": {
      "type": "string",
      "description": "Domain identifier (e.g., 0300_Geometry)",
      "required": true
    },
    "config_path": {
      "type": "string",
      "description": "Path to domain JSON config",
      "required": true
    },
    "output_dir": {
      "type": "string",
      "description": "Staging directory (--out)",
      "default": ".artifacts"
    },
    "publish": {
      "type": "boolean",
      "description": "Publish outputs to canonical locations",
      "default": false
    }
  },
  "steps": [
    {
      "name": "validate_config",
      "tool": "ConfigValidator",
      "inputs": ["config_path"],
      "outputs": ["validation_result"]
    },
    {
      "name": "execute_domain",
      "tool": "FrameworkDomainExecutor",
      "inputs": ["domain_id", "config_path", "output_dir"],
      "outputs": ["execution_result"]
    },
    {
      "name": "publish_outputs",
      "tool": "OutputPublisher",
      "condition": "publish == true",
      "inputs": ["execution_result", "output_dir"],
      "outputs": ["published_paths"]
    }
  ]
}
```

### 2. LangChain Tool Adapter

```python
from langchain_core.tools import StructuredTool
from pulsus.workflows.framework.domain_executor import FrameworkDomainExecutor

# Convert to LangChain tool
framework_tool = StructuredTool(
    name="execute_framework_domain",
    description="Execute 8-step framework domain workflow for traffic modeling",
    func=FrameworkDomainExecutor().execute_domain,
    args_schema={
        "domain_id": str,
        "config_path": str,
        "output_dir": str,
        "publish": bool
    }
)
```

---

## 📋 Usage Examples

### Example 1: Execute Geometry Domain

```python
from pulsus.workflows.framework.domain_executor import FrameworkDomainExecutor
from pathlib import Path

executor = FrameworkDomainExecutor()

response = executor.execute_domain(
    domain_id="0300_Geometry",
    config_path=Path("pulsus/config/frameworks/domain_framework/domains/0300_Geometry.json"),
    output_dir=Path(".artifacts"),
    publish=True
)

if response.success:
    print(f"✅ Domain completed: {response.data['steps_completed']} steps")
    print(f"   Outputs: {response.data['outputs']}")
else:
    print(f"❌ Error: {response.message}")
```

### Example 2: CLI Invocation

```bash
# Execute single domain
pulsus execute-domain \
    --domain 0300_Geometry \
    --config pulsus/config/frameworks/domain_framework/domains/0300_Geometry.json \
    --out .artifacts \
    --publish

# Execute multiple domains in sequence
pulsus execute-domains \
    --domains 0100_Model,0300_Geometry,0800_Detectors \
    --config-dir pulsus/config/frameworks/domain_framework/domains \
    --out .artifacts \
    --publish
```

### Example 3: LangGraph Workflow

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class FrameworkState(TypedDict):
    domain_ids: list[str]
    current_domain: str
    results: dict

def execute_domain_node(state: FrameworkState):
    """Node that executes a framework domain."""

    executor = FrameworkDomainExecutor()

    response = executor.execute_domain(
        domain_id=state["current_domain"],
        config_path=Path(f"configs/{state['current_domain']}.json"),
        output_dir=Path(".artifacts")
    )

    state["results"][state["current_domain"]] = response.to_dict()
    return state

# Build graph
graph = StateGraph(FrameworkState)
graph.add_node("execute_domain", execute_domain_node)
# ... (continue graph definition)
```

---

## 🎯 Benefits of This Integration

### 1. **Seamless Framework Support**
- Pulsus natively understands the 8-step pattern
- Domain configs are declarative (JSON)
- No code changes needed for new domains

### 2. **Tool Reusability**
- Existing shared tools (common_analyser, auto_importer, etc.) wrapped as MCP domains
- Can be used standalone or in workflows
- LangChain compatible

### 3. **Safety & Observability**
- All framework operations logged to SafeNet
- Safety decorators prevent accidental data loss
- Approval workflows for write operations

### 4. **External Tool Integration**
- Aimsun can be launched and controlled via ConsoleManager
- UI editors can be invoked interactively
- Process status tracked

### 5. **Template Governance**
- Templates for exports, docs, reviews, visuals
- Schema validation ensures compliance
- Consistent output structure

---

## 📅 Implementation Roadmap

### Phase 1: Core Framework Integration (2 weeks)
- Implement FrameworkDomainExecutor
- Create domain configuration schema
- Build AimsunConnector
- Add GeoParquetExporter

**Agent:** Jean-Claude Mechanic + Jean-Claude MCP

### Phase 2: Shared Tool Wrappers (1 week)
- Wrap existing shared tools as MCP domains
- Add LangChain tool adapters
- Create workflow JSON definitions

**Agent:** Jean-Claude Mechanic

### Phase 3: Domain Configurations (1 week)
- Convert 40+ domains to JSON configs
- Validate against schema
- Test execution

**Agent:** Jean-Claude Domain + Jean-Claude MCP

### Phase 4: Testing & Validation (1 week)
- Integration tests with real domains
- Aimsun connectivity tests
- End-to-end workflow validation

**Agent:** Jean-Claude Auditor

**Total:** 5 weeks

---

## ✅ Compliance Checklist

- ✅ **8-step pattern supported** - FrameworkDomainExecutor implements all steps
- ✅ **Domain numbering** - Config schema includes domain_id validation
- ✅ **Owner tracking** - Config includes owner field
- ✅ **Staging vs publishing** - Explicit staging dir + publish flag
- ✅ **GeoParquet canonical** - GeoParquetExporter enforces standard
- ✅ **Template governance** - Templates referenced in configs
- ✅ **Shared tool integration** - Wrappers for all shared tools
- ✅ **Aimsun integration** - AimsunConnector for model manipulation
- ✅ **Dependencies tracked** - Config includes dependency list
- ✅ **I/O conventions** - Inputs/outputs explicit in step configs

---

## 📚 References

- **Framework Specification**: `aimsun-python-scripts/FW_Abu_Dhabi/framework/FRAMEWORK.md` (v3.1)
- **Parent Document**: `PULSUS_MCP_UNIFIED_INTEGRATION_PLAN.md` (v4.0)
- **Domain Template**: `pulsus/config/frameworks/domain_framework/domains/0300_Geometry.json`
- **Shared Tools**: `framework/shared_tools/`

---

**Status:** Active Integration
**Version:** 1.0
**Last Updated:** November 2025
**Next Review:** After Phase 1 completion
