"""Quick test to verify imports work"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try importing
try:
    from agents.pulsus.mcp.simple import ScriptOps
    from agents.pulsus.mcp.core.base import MCPBase, MCPResponse
    print("[OK] Imports successful!")

    # Create instance
    ops = ScriptOps()
    print(f"[OK] Created ScriptOps instance: {ops}")

    # Check capabilities
    caps = ops.get_capabilities()
    print(f"[OK] Got {len(caps)} capabilities")

    # List capabilities
    for cap in caps:
        print(f"  - {cap['name']}: {cap['safety_level']}")

    print("\n[SUCCESS] All imports and basic tests passed!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
