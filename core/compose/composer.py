from pathlib import Path

_TEMPLATE = '"""\nAuto-generated temporary composed module.\n"""\ndef run(**kwargs):\n    return {"ok": True, "message": "composition stub executed"}\n'

def plan_composition(parsed, candidates, threshold: float) -> dict:
    steps = []
    for i, c in enumerate(candidates[:2], start=1):
        steps.append({'id': f's{i}', 'tool': f'{c.path.name}::{c.entry}', 'inputs': {}, 'outputs': {}})
    plan = {'plan':{'description': f'Composed plan for {parsed.action}', 'steps': steps}, 'io':{'params': [], 'returns': []}}
    return plan

def render_tmp_module(plan: dict, tmp_root: Path, route_id: str) -> Path:
    tmp_root.mkdir(parents=True, exist_ok=True)
    path = tmp_root / f'tmp_compose_{route_id}.py'
    path.write_text(_TEMPLATE, encoding='utf-8')
    return path
