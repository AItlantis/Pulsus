from dataclasses import dataclass
from pathlib import Path

@dataclass
class SandboxPolicy:
    workflows_root: Path
    allow_network: bool = False
    max_seconds: int = 30
    max_mem_mb: int = 512
