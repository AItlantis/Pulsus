from pathlib import Path
import datetime

def append_change(domain_dir: Path, message: str) -> None:
    path = domain_dir / 'CHANGELOG.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    with path.open('a', encoding='utf-8') as f:
        f.write(f'- {ts} {message}\n')
