import time, uuid
from ..core.types import RouteDecision
from ..config.settings import load_settings
from .mcp_router import MCPRouter
from ..core.compose.selector import choose_policy
from ..core.compose.composer import plan_composition, render_tmp_module
from ..core.compose.generator import generate_tmp_module
from ..core.validators import ruff_runner, mypy_runner, unit_runner
from ..core.sandbox.runner import dry_run
from ..core.telemetry.logging import get_logger
from ..console.interrupt_handler import is_interrupted
from pathlib import Path
import json

# Global MCP router instance (initialized on first use)
_mcp_router = None

def _get_mcp_router():
    """Get or create the global MCP router instance."""
    global _mcp_router
    if _mcp_router is None:
        s = load_settings()
        _mcp_router = MCPRouter(s.workflows_root)
    return _mcp_router


def find_workflow(domain, action):
    """
    Find a workflow by domain and action.
    Uses MCPRouter for workflow discovery.
    """
    router = _get_mcp_router()
    workflow = router.get_workflow(domain, action)
    if workflow:
        return {
            "id": workflow.id,
            "domain": workflow.domain,
            "action": workflow.action,
            "description": workflow.description,
            "steps": workflow.steps
        }
    return None


def route(user_text: str, non_interactive: bool=False, explain: bool=False) -> RouteDecision:
    run_id = f'run-{int(time.time())}-{uuid.uuid4().hex[:6]}'
    logger = get_logger(run_id)
    s = load_settings()

    # Use MCP router for parsing
    router = _get_mcp_router()
    parsed = router.parse_intent(user_text)
    route_id = f'route-{uuid.uuid4().hex[:6]}'
    logger.event('parse', dict(route_id=route_id, parsed=parsed.__dict__))

    # Check for interrupt
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    candidates = []
    plan = None
    policy = 'generate'
    reason = ''

    if parsed.domain and parsed.action:
        # Use MCP router for tool discovery
        candidates = router.discover_tools(parsed.domain, parsed.action, parsed.intent)
        logger.event('discover', dict(route_id=route_id, count=len(candidates),
                                      top=[(c.path.name, round(c.score,2)) for c in candidates[:5]]))

    # Check for interrupt
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    policy, reason = choose_policy(parsed, candidates, threshold=s.ranker.threshold)

    if policy == 'compose' and candidates:
        plan = plan_composition(parsed, candidates, threshold=s.ranker.threshold)
        tmp_path = render_tmp_module(plan, s.workflows_root / s.tmp_dirname, route_id)
    elif policy == 'select' and candidates:
        tmp_path = candidates[0].path
    else:
        tmp_path = generate_tmp_module(parsed, s.workflows_root / s.tmp_dirname, route_id)

    # Check for interrupt before validation
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    artifacts, steps, ok = [], [], True
    rr = ruff_runner.run(tmp_path); artifacts.append(rr['log']); steps.append('ruff'); ok = ok and rr['ok']
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    mr = mypy_runner.run(tmp_path); artifacts.append(mr['log']); steps.append('mypy'); ok = ok and mr['ok']
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    ur = unit_runner.import_smoke(tmp_path); artifacts.append(ur['log']); steps.append('import'); ok = ok and ur['ok']
    if is_interrupted():
        raise InterruptedError("Route execution interrupted by user (ESC)")

    dr = dry_run(tmp_path); artifacts.append(dr['log']); steps.append('dry_run'); ok = ok and dr['ok']

    logger.event('validate', dict(route_id=route_id, ok=ok, steps=steps, artifacts=artifacts))

    decision = RouteDecision(route_id=route_id, policy=policy, selected=candidates[:1] if candidates else [], plan=plan, reason=reason, tmp_path=tmp_path)
    return decision
