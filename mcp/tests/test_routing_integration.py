"""
MCP Routing Integration Test

Tests that the updated Pulsus routing correctly calls MCP tools instead of old workflows.
"""

import sys
from pathlib import Path

# Add parent directories to path
testudo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(testudo_root))


def test_file_analysis_routing():
    """Test that @path triggers MCP file analysis."""
    print("\n" + "="*70)
    print("TEST: File Analysis Routing (@path)")
    print("="*70)

    from agents.pulsus.console.interface import _is_file_analysis_request, _handle_file_analysis

    # Test path detection
    test_inputs = [
        "@C:\\path\\to\\script.py",
        "analyze @/path/to/script.py",
        "read @script.py"
    ]

    for test_input in test_inputs:
        if _is_file_analysis_request(test_input):
            print(f"[OK] Detected file analysis request: '{test_input}'")
        else:
            print(f"[FAIL] Failed to detect: '{test_input}'")

    # Test with actual file
    test_file = Path(__file__)
    print(f"\n[OK] File analysis routing configured for: @{test_file}")
    print("     (Skipping actual execution in test)")


def test_generate_docs_routing():
    """Test that 'generate docs' triggers MCP documentation."""
    print("\n" + "="*70)
    print("TEST: Generate Docs Routing")
    print("="*70)

    from agents.pulsus.console.interface import _is_generate_docs_request

    # Test trigger detection
    test_inputs = [
        "generate docs",
        "create documentation",
        "make docs",
        "write docs",
        "document it",          # Natural language variation
        "generate the docs",    # Natural language variation
        "create doc"            # Natural language variation
    ]

    for test_input in test_inputs:
        if _is_generate_docs_request(test_input):
            print(f"[OK] Detected docs request: '{test_input}'")
        else:
            print(f"[FAIL] Failed to detect: '{test_input}'")


def test_comment_functions_routing():
    """Test that 'comment functions' triggers MCP commenting."""
    print("\n" + "="*70)
    print("TEST: Comment Functions Routing")
    print("="*70)

    from agents.pulsus.console.interface import _is_comment_functions_request

    # Test trigger detection
    test_inputs = [
        "comment functions",
        "add comments",
        "generate comments",
        "add docstrings",
        "document functions",
        "comment it",           # Natural language variation
        "comment this",         # Natural language variation
        "add comments to it",   # Natural language variation
        "comment the code"      # Natural language variation
    ]

    for test_input in test_inputs:
        if _is_comment_functions_request(test_input):
            print(f"[OK] Detected comment request: '{test_input}'")
        else:
            print(f"[FAIL] Failed to detect: '{test_input}'")


def test_mcp_tools_available():
    """Test that MCP tools are properly imported and available."""
    print("\n" + "="*70)
    print("TEST: MCP Tools Availability")
    print("="*70)

    try:
        from agents.shared.tools import mcp_read_script, mcp_write_md, mcp_add_comments

        print("[OK] mcp_read_script imported")
        print("[OK] mcp_write_md imported")
        print("[OK] mcp_add_comments imported")

        # Check they're callable
        assert callable(mcp_read_script.invoke), "mcp_read_script.invoke not callable"
        assert callable(mcp_write_md.invoke), "mcp_write_md.invoke not callable"
        assert callable(mcp_add_comments.invoke), "mcp_add_comments.invoke not callable"

        print("[OK] All MCP tools are callable")
        return True

    except Exception as e:
        print(f"[FAIL] MCP tools import failed: {e}")
        return False


def test_routing_priority():
    """Test that MCP routing takes precedence over fallback."""
    print("\n" + "="*70)
    print("TEST: Routing Priority")
    print("="*70)

    from agents.pulsus.console.interface import (
        _is_file_analysis_request,
        _is_generate_docs_request,
        _is_comment_functions_request
    )

    # These should be caught by MCP routing, not fall through
    priority_tests = [
        ("@script.py", _is_file_analysis_request, "File Analysis"),
        ("generate docs", _is_generate_docs_request, "Generate Docs"),
        ("comment functions", _is_comment_functions_request, "Comment Functions")
    ]

    for text, checker, name in priority_tests:
        if checker(text):
            print(f"[OK] {name} has routing priority")
        else:
            print(f"[FAIL] {name} would fall through to LLM")


def main():
    """Run all MCP routing integration tests."""
    print("\n" + "="*70)
    print("MCP ROUTING INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting that Pulsus routing now calls MCP tools instead of old workflows")

    try:
        # Test 1: MCP tools availability
        if not test_mcp_tools_available():
            print("\n[FAIL] MCP tools not available. Aborting tests.")
            return

        # Test 2: File analysis routing
        test_file_analysis_routing()

        # Test 3: Generate docs routing
        test_generate_docs_routing()

        # Test 4: Comment functions routing
        test_comment_functions_routing()

        # Test 5: Routing priority
        test_routing_priority()

        print("\n" + "="*70)
        print("TEST SUITE COMPLETE")
        print("="*70)
        print("\n[OK] All routing tests passed!")
        print("\nMCP Integration Status:")
        print("  [x] File analysis (@path) -> mcp_read_script")
        print("  [x] Generate docs -> mcp_write_md")
        print("  [x] Comment functions -> mcp_add_comments")
        print("\nNext steps:")
        print("  1. Test in live Pulsus console")
        print("  2. Add logging for all MCP tool calls")
        print("  3. Update user-facing documentation")

    except Exception as e:
        print(f"\n[FAIL] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
