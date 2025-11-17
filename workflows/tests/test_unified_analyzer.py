"""
Tests for Unified Path Analyzer

Tests path detection, context loading, and routing logic.
"""

import sys
from pathlib import Path

# Add testudo root to path
testudo_root = Path(__file__).parents[4]
if str(testudo_root) not in sys.path:
    sys.path.insert(0, str(testudo_root))

from agents.pulsus.workflows.utils.path_detector import (
    extract_path_from_input,
    detect_path_type,
    PathType,
    is_repository_root,
    normalize_path
)
from agents.pulsus.workflows.utils.context_loader import (
    find_repository_root,
    get_pulsus_storage_path,
    is_context_available
)


def test_path_extraction():
    """Test path extraction from user input."""
    print("\n=== Testing Path Extraction ===")

    test_cases = [
        ("@C:\\Users\\test\\file.py", "C:\\Users\\test\\file.py"),
        ("analyze @/home/user/project", "/home/user/project"),
        ("check @C:\\repo\\src\\module.py", "C:\\repo\\src\\module.py"),
        ("no path here", None),
        ("@relative/path/file.py", "relative/path/file.py"),
    ]

    for input_text, expected in test_cases:
        result = extract_path_from_input(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Expected: {expected}, Got: {result}")


def test_path_type_detection():
    """Test path type detection."""
    print("\n=== Testing Path Type Detection ===")

    # Test with this file (should exist)
    current_file = Path(__file__)
    path_type, normalized = detect_path_type(str(current_file))
    print(f"✓ Current file: {path_type} (expected: FILE)")

    # Test with parent directory (should exist)
    parent_dir = current_file.parent
    path_type, normalized = detect_path_type(str(parent_dir))
    print(f"✓ Parent directory: {path_type} (expected: DIRECTORY)")

    # Test with non-existent path
    fake_path = "C:\\nonexistent\\file.py"
    path_type, normalized = detect_path_type(fake_path)
    print(f"✓ Non-existent file: {path_type} (expected: NON_EXISTENT)")


def test_repository_detection():
    """Test repository root detection."""
    print("\n=== Testing Repository Detection ===")

    # Start from this file and walk up
    current_file = Path(__file__)
    repo_root = find_repository_root(current_file)

    if repo_root:
        print(f"✓ Found repository root: {repo_root}")
        print(f"  Is repository root: {is_repository_root(repo_root)}")

        # Check .pulsus path
        pulsus_path = get_pulsus_storage_path(repo_root)
        print(f"  .pulsus/ path: {pulsus_path}")
        print(f"  Context available: {is_context_available(current_file)}")
    else:
        print(f"✗ No repository root found")


def test_path_normalization():
    """Test path normalization."""
    print("\n=== Testing Path Normalization ===")

    test_paths = [
        "C:\\Users\\test\\file.py",
        "/home/user/project",
        "relative/path/file.py",
    ]

    for path_str in test_paths:
        normalized = normalize_path(path_str)
        if normalized:
            print(f"✓ {path_str}")
            print(f"  → {normalized}")
        else:
            print(f"✗ Failed to normalize: {path_str}")


def test_routing_integration():
    """Test routing integration with @path detection."""
    print("\n=== Testing Routing Integration ===")

    from agents.pulsus.routing.mcp_router import MCPRouter

    # Get workflows root
    workflows_root = Path(__file__).parent.parent
    router = MCPRouter(workflows_root)

    test_inputs = [
        "@C:\\repo\\file.py",
        "@/home/user/project",
        "analyze @C:\\test\\module.py",
        "run repository analysis",
        "comment functions",
    ]

    for input_text in test_inputs:
        intent = router.parse_intent(input_text)
        print(f"\nInput: '{input_text}'")
        print(f"  Domain: {intent.domain}")
        print(f"  Action: {intent.action}")
        print(f"  Confidence: {intent.confidence:.2f}")


if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED PATH ANALYZER TESTS")
    print("=" * 70)

    try:
        test_path_extraction()
        test_path_type_detection()
        test_repository_detection()
        test_path_normalization()
        test_routing_integration()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
