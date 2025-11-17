import shutil, subprocess, datetime
from pathlib import Path

def run(path: Path) -> dict:
    log_dir = Path('logs/validation') / datetime.date.today().isoformat()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'mypy_{path.stem}.log'
    if shutil.which('mypy') is None:
        log_file.write_text('mypy not installed; skipping type check.\n', encoding='utf-8')
        return {'ok': True, 'log': str(log_file), 'summary': 'mypy skipped'}
    try:
        out = subprocess.run(['mypy', str(path)], capture_output=True, text=True, timeout=20)
        log_file.write_text(out.stdout + '\n' + out.stderr, encoding='utf-8')
        return {'ok': out.returncode == 0, 'log': str(log_file), 'summary': f'mypy rc={out.returncode}'}
    except Exception as e:
        log_file.write_text(f'mypy error: {e}\n', encoding='utf-8')
        return {'ok': False, 'log': str(log_file), 'summary': 'mypy error'}
