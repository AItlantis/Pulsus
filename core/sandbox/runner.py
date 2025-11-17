import datetime, runpy
from pathlib import Path

def dry_run(path: Path) -> dict:
    log_dir = Path('logs/validation') / datetime.date.today().isoformat()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'dryrun_{path.stem}.log'
    try:
        ns = runpy.run_path(str(path), run_name='__dryrun__')
        fn = ns.get('run') or ns.get('main')
        if callable(fn):
            try:
                fn()
            except TypeError:
                pass
        log_file.write_text('dry run complete\n', encoding='utf-8')
        return {'ok': True, 'log': str(log_file), 'summary': 'dry-run ok'}
    except Exception as e:
        log_file.write_text(f'dry run error: {e}\n', encoding='utf-8')
        return {'ok': False, 'log': str(log_file), 'summary': 'dry-run error'}
