"""
Test script for MCP router functionality.

Tests:
1. MCPRouter initialization
2. Workflow loading
3. MCP tools loading
4. Intent parsing
5. Tool discovery
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parents[3]))

from agents.pulsus.routing.mcp_router import MCPRouter
from agents.pulsus.config.settings import load_settings


def test_router_initialization():
    """Test that the MCP router initializes correctly."""
    print("\n=== Test 1: Router Initialization ===")
    try:
        settings = load_settings()
        router = MCPRouter(settings.workflows_root)
        print(f"[OK] Router initialized successfully")
        print(f"  Workflows loaded: {len(router.workflows)}")
        print(f"  MCP tools loaded: {len(router.mcp_tools)}")
        return router
    except Exception as e:
        print(f"[FAIL] Router initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_workflow_loading(router):
    """Test that workflows are loaded correctly."""
    print("\n=== Test 2: Workflow Loading ===")
    try:
        workflows = router.list_workflows()
        print(f"[OK] Found {len(workflows)} workflows:")
        for wf in workflows:
            print(f"  - {wf.id}: {wf.domain}/{wf.action} - {wf.description}")
        return True
    except Exception as e:
        print(f"[FAIL] Workflow loading failed: {e}")
        return False


def test_mcp_tools_loading(router):
    """Test that MCP tools are loaded correctly."""
    print("\n=== Test 3: MCP Tools Loading ===")
    try:
        tools = router.list_mcp_tools()
        print(f"[OK] Found {len(tools)} MCP tools:")
        for name in sorted(tools.keys())[:10]:  # Show first 10
            tool = tools[name]
            desc = tool.description[:60] if hasattr(tool, 'description') and tool.description else "No description"
            print(f"  - {name}: {desc}...")
        if len(tools) > 10:
            print(f"  ... and {len(tools) - 10} more")
        return True
    except Exception as e:
        print(f"[FAIL] MCP tools loading failed: {e}")
        return False


def test_intent_parsing(router):
    """Test intent parsing with various inputs."""
    print("\n=== Test 4: Intent Parsing ===")

    test_cases = [
        "analyze this file",
        "comment the functions",
        "read script at path/to/file.py",
        "search aimsun documentation for GKSection",
        "format my python code",
        "hello there",
    ]

    results = []
    for text in test_cases:
        try:
            parsed = router.parse_intent(text)
            print(f"\nInput: '{text}'")
            print(f"  Domain: {parsed.domain}")
            print(f"  Action: {parsed.action}")
            print(f"  Confidence: {parsed.confidence:.2f}")
            results.append(True)
        except Exception as e:
            print(f"\n[FAIL] Failed to parse '{text}': {e}")
            results.append(False)

    success_rate = sum(results) / len(results) * 100
    print(f"\n[OK] Parsed {sum(results)}/{len(results)} inputs successfully ({success_rate:.0f}%)")
    return all(results)


def test_tool_discovery(router):
    """Test tool discovery for different domains/actions."""
    print("\n=== Test 5: Tool Discovery ===")

    test_cases = [
        ("analysis", "analyze_file", "analyze this file"),
        ("script_ops", "read_script", "read my python script"),
        ("documentation", "search_docs", "search for API documentation"),
    ]

    results = []
    for domain, action, intent in test_cases:
        try:
            tools = router.discover_tools(domain, action, intent)
            print(f"\nQuery: domain={domain}, action={action}")
            print(f"  Found {len(tools)} matching tools:")
            for tool in tools[:3]:  # Show top 3
                print(f"    - {tool.path.name} (score: {tool.score:.2f})")
            results.append(True)
        except Exception as e:
            print(f"\n[FAIL] Discovery failed for {domain}/{action}: {e}")
            results.append(False)

    success_rate = sum(results) / len(results) * 100
    print(f"\n[OK] Discovery succeeded for {sum(results)}/{len(results)} queries ({success_rate:.0f}%)")
    return all(results)


def test_workflow_retrieval(router):
    """Test retrieving specific workflows."""
    print("\n=== Test 6: Workflow Retrieval ===")

    # Try to get a known workflow
    workflow = router.get_workflow("analysis", "analyze_file")
    if workflow:
        print(f"[OK] Retrieved workflow: {workflow.id}")
        print(f"  Description: {workflow.description}")
        print(f"  Steps: {len(workflow.steps)}")
        return True
    else:
        print("[FAIL] Failed to retrieve workflow")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP ROUTER TEST SUITE")
    print("="*60)

    # Test 1: Initialize router
    router = test_router_initialization()
    if not router:
        print("\n[CRITICAL] Router initialization failed - cannot continue tests")
        return False

    # Test 2-6: Various functionality tests
    test_results = []
    test_results.append(test_workflow_loading(router))
    test_results.append(test_mcp_tools_loading(router))
    test_results.append(test_intent_parsing(router))
    test_results.append(test_tool_discovery(router))
    test_results.append(test_workflow_retrieval(router))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(test_results)
    total = len(test_results)
    success_rate = passed / total * 100

    if all(test_results):
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
        return True
    else:
        print(f"[WARNING] SOME TESTS FAILED ({passed}/{total} passed, {success_rate:.0f}%)")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
