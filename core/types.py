from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal, Optional, Dict, Any

@dataclass
class ParsedIntent:
    domain: Optional[str]
    action: Optional[str]
    intent: str
    confidence: float

@dataclass
class ArgSpec:
    name: str
    type_hint: Optional[str]
    required: bool
    default: Optional[str]

@dataclass
class ToolSpec:
    path: Path
    entry: str
    args: List[ArgSpec]
    doc: str
    score: float

@dataclass
class RouteDecision:
    route_id: str
    policy: Literal['select','compose','generate']
    selected: List[ToolSpec]
    plan: Optional[Dict[str, Any]]
    reason: str
    tmp_path: Optional[Path] = None

@dataclass
class ValidationReport:
    ok: bool
    steps: List[str]
    duration_ms: int
    artifacts: List[Path]
    summary: str
