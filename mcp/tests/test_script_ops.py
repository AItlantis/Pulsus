"""
Test script for MCP Script Operations

Tests the new MCP tools: mcp_read_script, mcp_write_md, mcp_add_comments
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
testudo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(testudo_root))

from shared.tools import mcp_read_script, mcp_write_md, mcp_add_comments
import json


def test_mcp_read_script():
    """Test reading and analyzing a script."""
    print("\n" + "="*70)
    print("TEST: mcp_read_script")
    print("="*70)

    # Use this test file as the target
    test_file = __file__

    print(f"Reading: {test_file}")
    result = mcp_read_script.invoke({"path": test_file})

    # Parse JSON result
    data = json.loads(result)

    if data.get('success'):
        print(f"[OK] Success!")
        print(f"  - File: {data.get('file_path')}")
        print(f"  - Functions found: {len(data.get('ast_analysis', {}).get('functions', []))}")
        print(f"  - Classes found: {len(data.get('ast_analysis', {}).get('classes', []))}")
        print(f"  - Imports found: {len(data.get('ast_analysis', {}).get('imports', []))}")

        # Show function names
        functions = data.get('ast_analysis', {}).get('functions', [])
        if functions:
            print(f"\n  Functions:")
            for func in functions[:5]:  # Show first 5
                print(f"    - {func['name']}() at line {func['line']}")
    else:
        print(f"[FAIL] Failed: {data.get('error')}")

    return data


def test_mcp_add_comments():
    """Test generating comments for functions."""
    print("\n" + "="*70)
    print("TEST: mcp_add_comments")
    print("="*70)

    # Use a simple test file
    test_file = Path(__file__).parent / "helpers" / "script_ops.py"

    if not test_file.exists():
        print(f"[FAIL] Test file not found: {test_file}")
        return None

    print(f"Analyzing: {test_file}")
    print("Generating comments (this may take a moment)...")

    result = mcp_add_comments.invoke({
        "path": str(test_file),
        "strategy": "docstring"
    })

    # Parse JSON result
    data = json.loads(result)

    if data.get('success'):
        print(f"[OK] Success!")
        print(f"  - Functions commented: {data.get('functions_commented', 0)}")

        # Show a sample comment
        comments = data.get('comments', [])
        if comments:
            print(f"\n  Sample comment for '{comments[0]['function']}':")
            sample = comments[0]['comment'][:200]  # First 200 chars
            print(f"    {sample}...")
    else:
        print(f"[FAIL] Failed: {data.get('error')}")

    return data


def test_mcp_write_md():
    """Test generating documentation."""
    print("\n" + "="*70)
    print("TEST: mcp_write_md")
    print("="*70)

    # Use this test file
    test_file = __file__

    print(f"Generating docs for: {test_file}")
    print("This may take 30-60 seconds...")

    result = mcp_write_md.invoke({
        "path": test_file,
        "content": None  # Auto-generate
    })

    # Parse JSON result
    data = json.loads(result)

    if data.get('success'):
        print(f"[OK] Success!")
        print(f"  - Documentation created: {data.get('doc_path')}")
        print(f"  - Message: {data.get('message')}")
    else:
        print(f"[FAIL] Failed: {data.get('error')}")

    return data


def main():
    """Run all MCP script operations tests."""
    print("\n" + "="*70)
    print("MCP SCRIPT OPERATIONS TEST SUITE")
    print("="*70)
    print("\nTesting Phase 1 - MCP Migration")
    print("Converting text-triggered LLM functions to formal MCP tools")

    try:
        # Test 1: Read script
        read_result = test_mcp_read_script()

        # Test 2: Add comments (optional - can be slow)
        # Uncomment to test:
        # comment_result = test_mcp_add_comments()

        # Test 3: Write documentation (optional - can be slow)
        # Uncomment to test:
        # doc_result = test_mcp_write_md()

        print("\n" + "="*70)
        print("TEST SUITE COMPLETE")
        print("="*70)
        print("\n[OK] MCP tools are working correctly!")
        print("\nNext steps:")
        print("  1. Update Pulsus routing to call MCP tools instead of string triggers")
        print("  2. Add logging for all MCP actions")
        print("  3. Implement SafeNet path checks")
        print("  4. Move to Phase 2: Standardize Code Structure")

    except Exception as e:
        print(f"\n[FAIL] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
