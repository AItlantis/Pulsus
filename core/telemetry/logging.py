import json, datetime
from pathlib import Path

class Logger:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.date_dir = Path('logs/app') / datetime.date.today().isoformat()
        self.date_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = Path('logs/runs') / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def event(self, phase: str, payload: dict):
        record = {
            'ts': datetime.datetime.utcnow().isoformat() + 'Z',
            'run_id': self.run_id,
            'phase': phase,
            **payload
        }
        line = json.dumps(record, ensure_ascii=False)
        (self.date_dir / 'app.log').open('a', encoding='utf-8').write(line + '\n')
        (self.run_dir / 'steps.log').open('a', encoding='utf-8').write(line + '\n')

def get_logger(run_id: str) -> Logger:
    return Logger(run_id)
