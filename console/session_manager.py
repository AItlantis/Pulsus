
from agents.pulsus.ui import display_manager as ui
def ping_agent():
    """Simple connectivity and sanity check."""
    ui.section("Pulsus Agent Health Check")
    ui.info("Performing heartbeat ping...")
    try:
        ui.heartbeat()
        ui.success("Pulsus agent is alive and ready.")
    except Exception as e:
        ui.error(f"Ping failed: {e}")
        raise SystemExit(1)
