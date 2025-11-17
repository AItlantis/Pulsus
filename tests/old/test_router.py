from testudo.agents.pulsus.routing.router import route

def test_route_generates_decision():
    decision = route("summarize this matrix for me", non_interactive=True)
    assert decision.policy in ("select", "compose", "generate")
    assert decision.route_id.startswith("route-")
    assert hasattr(decision, "reason")
