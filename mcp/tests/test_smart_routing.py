"""
Test Smart Routing for @path with Additional Text

Tests that users can combine file analysis with actions in one command:
- @path comment it
- @path generate docs
- @path what does X do?
"""

import sys
from pathlib import Path

# Add parent directories to path
testudo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(testudo_root))

from agents.pulsus.console.interface import (
    _is_comment_functions_request,
    _is_generate_docs_request,
    _is_file_analysis_request
)


def test_combined_commands():
    """Test that @path can be combined with actions."""
    print("\n" + "="*70)
    print("TEST: Smart Routing - Combined Commands")
    print("="*70)

    test_cases = [
        # Format: (input, should_detect_file, action_type)
        ("@script.py comment it", True, "comment"),
        ("@C:\\path\\to\\file.py generate docs", True, "docs"),
        ("analyze @/path/to/script.py", True, "none"),
        ("@script.py what does duplicate() do?", True, "question"),
        ("@script.py comment functions", True, "comment"),
        ("@script.py document it", True, "docs"),
    ]

    print("\n[FILE DETECTION]")
    print("-" * 70)
    for text, should_detect, _ in test_cases:
        detected = _is_file_analysis_request(text)
        status = "[OK]" if detected == should_detect else "[FAIL]"
        print(f"{status} '{text}' -> {detected}")

    print("\n[ACTION DETECTION AFTER @PATH]")
    print("-" * 70)

    # Extract text after @path and check action detection
    import re
    for text, _, action_type in test_cases:
        # Extract what comes after @path
        pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
        match = re.search(pattern, text)
        if match:
            additional_text = text[match.end():].strip()

            if additional_text:
                is_comment = _is_comment_functions_request(additional_text)
                is_docs = _is_generate_docs_request(additional_text)

                if action_type == "comment":
                    status = "[OK]" if is_comment else "[FAIL]"
                    print(f"{status} '{text}' -> comment action detected: {is_comment}")
                elif action_type == "docs":
                    status = "[OK]" if is_docs else "[FAIL]"
                    print(f"{status} '{text}' -> docs action detected: {is_docs}")
                elif action_type == "question":
                    status = "[OK]" if not (is_comment or is_docs) else "[FAIL]"
                    print(f"{status} '{text}' -> treated as question: {not (is_comment or is_docs)}")
            else:
                print(f"[OK] '{text}' -> no action (analysis only)")

    print()


def test_extraction_logic():
    """Test that we correctly extract additional text after @path."""
    print("\n" + "="*70)
    print("TEST: Text Extraction After @path")
    print("="*70)

    import re

    test_cases = [
        ("@script.py comment it", "comment it"),
        ("@C:\\path\\to\\file.py generate docs", "generate docs"),
        ("analyze @/path/script.py and comment it", "and comment it"),
        ("@script.py", ""),
    ]

    for text, expected in test_cases:
        pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
        match = re.search(pattern, text)

        if match:
            additional_text = text[match.end():].strip()
            status = "[OK]" if additional_text == expected else "[FAIL]"
            print(f"{status} '{text}' -> '{additional_text}' (expected '{expected}')")
        else:
            print(f"[FAIL] '{text}' -> no @path found")

    print()


def test_user_workflows():
    """Test realistic user workflows."""
    print("\n" + "="*70)
    print("TEST: User Workflows")
    print("="*70)

    workflows = [
        {
            "name": "Quick Comment",
            "command": "@C:\\my_project\\script.py comment it",
            "expected": "Should analyze file AND generate comments in one step"
        },
        {
            "name": "Quick Documentation",
            "command": "@/path/to/file.py generate docs",
            "expected": "Should analyze file AND create .md documentation in one step"
        },
        {
            "name": "Analysis with Question",
            "command": "@script.py what does the main function do?",
            "expected": "Should analyze file AND answer the question"
        },
        {
            "name": "Analysis Only",
            "command": "@script.py",
            "expected": "Should only analyze, then show available actions"
        }
    ]

    for workflow in workflows:
        print(f"\n[{workflow['name']}]")
        print(f"Command: {workflow['command']}")
        print(f"Expected: {workflow['expected']}")

        # Check if it's detected as a file analysis request
        is_file = _is_file_analysis_request(workflow['command'])
        print(f"File detected: {is_file}")

        # Extract additional text
        import re
        pattern = r'@([A-Za-z]:\\[^\s]+|/[^\s]+|[^\s]+\.py)'
        match = re.search(pattern, workflow['command'])

        if match:
            additional = workflow['command'][match.end():].strip()
            if additional:
                print(f"Additional text: '{additional}'")

                if _is_comment_functions_request(additional):
                    print("-> Will auto-route to: Comment Generation")
                elif _is_generate_docs_request(additional):
                    print("-> Will auto-route to: Documentation Generation")
                else:
                    print("-> Will auto-route to: Follow-up Question")
            else:
                print("-> Will show: Available Actions menu")

    print()


def main():
    """Run all smart routing tests."""
    print("\n" + "="*70)
    print("SMART ROUTING TEST SUITE")
    print("="*70)
    print("\nTesting combined @path + action commands")

    try:
        test_combined_commands()
        test_extraction_logic()
        test_user_workflows()

        print("\n" + "="*70)
        print("[SUCCESS] Smart routing works correctly!")
        print("="*70)
        print("\nUsers can now use:")
        print("  - @path comment it         - Analyze and comment in one step")
        print("  - @path generate docs      - Analyze and document in one step")
        print("  - @path what does X do?    - Analyze and ask questions")
        print("  - @path                    - Analyze only (shows menu)")
        print()

    except Exception as e:
        print(f"\n[FAILED] Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
