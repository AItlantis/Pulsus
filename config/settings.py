from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class ModelConfig:
    """
    Configuration for the local Ollama model.
    """
    provider: str = "ollama"
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    # name: str = os.getenv("PULSUS_MODEL_NAME", "qwen3-coder:30b")
    name: str = os.getenv("PULSUS_MODEL_NAME", "qwen3:4b")
    temperature: float = float(os.getenv("PULSUS_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("PULSUS_MAX_TOKENS", "30720")) 
    timeout: int = int(os.getenv("PULSUS_TIMEOUT", "60"))  # seconds

@dataclass
class RankerConfig:
    threshold: float = 0.60
    weights: dict = field(default_factory=lambda: {'name':0.40,'doc':0.40,'history':0.20})

@dataclass
class SandboxConfig:
    max_seconds: int = 30
    max_mem_mb: int = 512
    network: str = 'off'  # 'off' | 'allowlist'

@dataclass
class Settings:
    workflows_root: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'workflows')
    framework_root: Path = Path(r'C:\Users\jean-noel.diltoer\software\sources\aimsun-python-scripts\FW_Abu_Dhabi\workflow')  # User-defined tools directory
    log_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'logs')
    tmp_dirname: str = 'route_tmp'  # Temporary generated modules (inside workflows_root)
    retention_days: int = 7

    model: ModelConfig = field(default_factory=ModelConfig)
    embeddings_enabled: bool = False

    ranker: RankerConfig = field(default_factory=RankerConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    cache_enabled: bool = True
    rag_enabled: bool = False

def load_settings() -> 'Settings':
    s = Settings()
    # Allow environment variable overrides
    if 'PULSUS_WORKFLOWS_ROOT' in os.environ:
        s.workflows_root = Path(os.getenv('PULSUS_WORKFLOWS_ROOT'))
    if 'PULSUS_FRAMEWORK_ROOT' in os.environ:
        s.framework_root = Path(os.getenv('PULSUS_FRAMEWORK_ROOT'))
    if 'PULSUS_LOG_DIR' in os.environ:
        s.log_dir = Path(os.getenv('PULSUS_LOG_DIR'))
    return s
