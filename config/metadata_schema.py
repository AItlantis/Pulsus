from dataclasses import dataclass, asdict
from typing import Dict, Any
import json

METADATA_JSON_SCHEMA = {
  '$schema': 'https://json-schema.org/draft/2020-12/schema',
  'title': 'Pulsus Promotion Metadata',
  'type': 'object',
  'properties': {
    'id': {'type':'string'},
    'run_id': {'type':'string'},
    'route_id': {'type':'string'},
    'name': {'type':'string'},
    'domain': {'type':'string'},
    'action': {'type':'string'},
    'description': {'type':'string'},
    'status': {'type':'string'},
    'created_by': {'type':'string'},
    'created_at': {'type':'string', 'format':'date-time'},
    'version': {'type':'string'},
    'tool_hash': {'type':'string'},
    'tokens_estimate': {'type':'number'},
    'model': {'type':'object'},
    'rag': {'type':'object'}
  },
  'required': ['id','name','domain','action','created_at','version','tool_hash']
}

@dataclass
class MetadataRecord:
    id: str
    run_id: str
    route_id: str
    name: str
    domain: str
    action: str
    description: str
    status: str
    created_by: str
    created_at: str
    version: str
    tool_hash: str
    tokens_estimate: int = 0
    model: Dict[str, Any] = None
    rag: Dict[str, Any] = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
