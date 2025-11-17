from agents.pulsus.core.compose.selector import choose_policy
from agents.pulsus.core.types import ParsedIntent, ToolSpec
from pathlib import Path

def test_choose_select_policy():
    parsed = ParsedIntent("analysis", "summarise", "summarize this", 0.9)
    candidates = [
        ToolSpec(path=Path("a.py"), entry="run", args=[], doc="", score=0.8)
    ]
    policy, reason = choose_policy(parsed, candidates, threshold=0.6)
    assert policy == "select"
    assert "Top-1" in reason

def test_choose_compose_policy():
    parsed = ParsedIntent("analysis", "summarise", "summarize", 0.9)
    candidates = [
        ToolSpec(path=Path("a.py"), entry="run", args=[], doc="", score=0.62),
        ToolSpec(path=Path("b.py"), entry="run", args=[], doc="", score=0.61)
    ]
    policy, reason = choose_policy(parsed, candidates, threshold=0.6)
    assert policy == "compose"
