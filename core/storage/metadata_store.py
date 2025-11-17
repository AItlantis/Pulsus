from pathlib import Path
import hashlib, json

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return 'sha256:' + h.hexdigest()

def append_jsonl(record: dict, jsonl_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    name = record.get('name')
    tool_hash = record.get('tool_hash')
    if jsonl_path.exists():
        for line in jsonl_path.read_text(encoding='utf-8').splitlines():
            try:
                obj = json.loads(line)
                if obj.get('name')==name and obj.get('tool_hash')==tool_hash:
                    return
            except Exception:
                continue
    with jsonl_path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
