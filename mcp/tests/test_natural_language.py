"""
Test Natural Language Trigger Detection

This script tests that natural language variations like "comment it"
are properly detected and routed to MCP tools.
"""

import sys
from pathlib import Path

# Add parent directories to path
testudo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(testudo_root))

from agents.pulsus.console.interface import (
    _is_comment_functions_request,
    _is_generate_docs_request
)


def test_comment_variations():
    """Test various natural language comment requests."""
    print("\n" + "="*70)
    print("TESTING: Natural Language Comment Triggers")
    print("="*70)

    test_cases = [
        # Original exact matches
        ("comment functions", True),
        ("add comments", True),
        ("generate comments", True),

        # Natural language variations
        ("comment it", True),
        ("comment this", True),
        ("comment the code", True),
        ("add comments to it", True),
        ("document the functions", True),

        # Should NOT match
        ("what is a comment?", False),
        ("explain comments", False),
        ("show me comments", False),
    ]

    passed = 0
    failed = 0

    for text, expected in test_cases:
        result = _is_comment_functions_request(text)
        status = "[OK]" if result == expected else "[FAIL]"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} '{text}' -> {result} (expected {expected})")

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_docs_variations():
    """Test various natural language docs generation requests."""
    print("\n" + "="*70)
    print("TESTING: Natural Language Docs Triggers")
    print("="*70)

    test_cases = [
        # Original exact matches
        ("generate docs", True),
        ("create documentation", True),
        ("make docs", True),

        # Natural language variations
        ("document it", True),
        ("generate the docs", True),
        ("create doc", True),
        ("build documentation", True),

        # Should NOT match
        ("what are docs?", False),
        ("show documentation", False),
        ("find docs", False),
    ]

    passed = 0
    failed = 0

    for text, expected in test_cases:
        result = _is_generate_docs_request(text)
        status = "[OK]" if result == expected else "[FAIL]"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} '{text}' -> {result} (expected {expected})")

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all natural language trigger tests."""
    print("\n" + "="*70)
    print("NATURAL LANGUAGE TRIGGER DETECTION TEST SUITE")
    print("="*70)
    print("\nTesting that Pulsus recognizes natural language like 'comment it'")

    try:
        comment_ok = test_comment_variations()
        docs_ok = test_docs_variations()

        print("\n" + "="*70)
        if comment_ok and docs_ok:
            print("[SUCCESS] All natural language triggers work correctly!")
            print("="*70)
            print("\nYou can now use natural language in Pulsus:")
            print("  - 'comment it' instead of 'comment functions'")
            print("  - 'document it' instead of 'generate docs'")
            print("  - 'add comments to it' instead of 'add comments'")
        else:
            print("[FAILED] Some triggers did not work as expected")
            print("="*70)

    except Exception as e:
        print(f"\n[FAILED] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
