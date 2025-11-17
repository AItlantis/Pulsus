import shutil, subprocess, datetime
from pathlib import Path

def run(path: Path) -> dict:
    log_dir = Path('logs/validation') / datetime.date.today().isoformat()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'ruff_{path.stem}.log'
    if shutil.which('ruff') is None:
        log_file.write_text('ruff not installed; skipping lint.\n', encoding='utf-8')
        return {'ok': True, 'log': str(log_file), 'summary': 'ruff skipped'}
    try:
        out = subprocess.run(['ruff', 'check', str(path)], capture_output=True, text=True, timeout=5)
        log_file.write_text(out.stdout + '\n' + out.stderr, encoding='utf-8')
        return {'ok': out.returncode == 0, 'log': str(log_file), 'summary': f'ruff rc={out.returncode}'}
    except Exception as e:
        log_file.write_text(f'ruff error: {e}\n', encoding='utf-8')
        return {'ok': False, 'log': str(log_file), 'summary': 'ruff error'}
