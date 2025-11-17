import importlib.util, datetime
from pathlib import Path

def import_smoke(path: Path) -> dict:
    log_dir = Path('logs/validation') / datetime.date.today().isoformat()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'import_{path.stem}.log'
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # type: ignore
        ok = hasattr(mod, 'run') or hasattr(mod, 'main')
        log_file.write_text(f'import ok={ok}\n', encoding='utf-8')
        return {'ok': ok, 'log': str(log_file), 'summary': 'import smoke ok' if ok else 'entry not found'}
    except Exception as e:
        log_file.write_text(f'import error: {e}\n', encoding='utf-8')
        return {'ok': False, 'log': str(log_file), 'summary': 'import error'}
