"""
Test script for Repository Analyzer MCP tools.

Tests:
1. Repository analysis
2. File validation
3. Report generation (if openpyxl available)
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parents[2]))

from agents.shared.tools import (
    mcp_analyze_repository,
    mcp_validate_python_file,
    mcp_generate_repository_report
)


def test_analyze_repository():
    """Test repository analysis."""
    print("\n" + "="*60)
    print("TEST 1: Repository Analysis")
    print("="*60)

    # Analyze the pulsus directory (not just routing)
    repo_path = str(Path(__file__).parents[1] / "pulsus")

    print(f"\nAnalyzing repository: {repo_path}")

    result_json = mcp_analyze_repository.invoke({
        "repo_path": repo_path,
        "ignore_patterns": ["__pycache__", ".venv", "venv"]
    })

    result = json.loads(result_json)

    if result.get("success"):
        print(f"[OK] Analysis successful")
        print(f"  Files analyzed: {result['files_analyzed']}")
        print(f"  Total functions: {result['statistics']['total_functions']}")
        print(f"  Total lines: {result['statistics']['total_lines']}")
        print(f"  Files with issues: {result['statistics']['files_with_issues']}")
        print(f"  Compliance rate: {result['statistics']['compliance_rate']}")

        # Show top issues
        issues = result.get('issues_summary', {})
        print(f"\n  Total issues: {issues.get('total_issues', 0)}")
        if issues.get('top_issues'):
            print("  Top 3 issues:")
            for issue in issues['top_issues'][:3]:
                print(f"    - [{issue['priority']}] {issue['file']}: {issue['issue']}")

        # Show reusability summary
        reuse = result.get('reusability_summary', {})
        print(f"\n  Average reusability score: {reuse.get('average_score', 0)}")
        if reuse.get('top_reusable_functions'):
            print("  Top reusable functions:")
            for fn in reuse['top_reusable_functions'][:3]:
                print(f"    - {fn['function']} (score: {fn['score']}, used in {fn['used_in']} files)")

        return True
    else:
        print(f"[FAIL] Analysis failed: {result.get('error')}")
        return False


def test_validate_file():
    """Test single file validation."""
    print("\n" + "="*60)
    print("TEST 2: File Validation")
    print("="*60)

    # Validate the mcp_router.py file
    file_path = str(Path(__file__).parents[1] / "pulsus" / "routing" / "mcp_router.py")

    print(f"\nValidating file: {file_path}")

    result_json = mcp_validate_python_file.invoke({
        "file_path": file_path
    })

    result = json.loads(result_json)

    if result.get("success"):
        print(f"[OK] Validation successful")
        print(f"  File: {result['file']}")
        print(f"  Naming valid: {result['naming_valid']}")
        print(f"  Lines: {result['statistics']['lines']}")
        print(f"  Functions: {result['statistics']['functions']}")
        print(f"  Classes: {result['statistics']['classes']}")
        print(f"  Total imports: {result['statistics']['imports_total']}")

        # Show metadata
        meta = result.get('metadata', {})
        print(f"\n  Metadata:")
        print(f"    Owner: {meta.get('owner', 'Not set')}")
        print(f"    Type: {meta.get('atype', 'Not set')}")
        print(f"    Category: {meta.get('category', 'Not set')}")

        # Show issues
        issues = result.get('issues', [])
        if issues:
            print(f"\n  Issues found ({len(issues)}):")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("\n  No issues found!")

        return True
    else:
        print(f"[FAIL] Validation failed: {result.get('error')}")
        return False


def test_generate_report():
    """Test Excel report generation."""
    print("\n" + "="*60)
    print("TEST 3: Excel Report Generation")
    print("="*60)

    repo_path = str(Path(__file__).parents[1] / "pulsus")
    output_path = str(Path(__file__).parent / "test_repository_report.xlsx")

    print(f"\nGenerating report for: {repo_path}")
    print(f"Output path: {output_path}")

    result_json = mcp_generate_repository_report.invoke({
        "repo_path": repo_path,
        "output_path": output_path,
        "ignore_patterns": ["__pycache__", ".venv", "venv"]
    })

    result = json.loads(result_json)

    if result.get("success"):
        print(f"[OK] Report generated successfully")
        print(f"  Output: {result['output_path']}")
        print(f"  Sheets included:")
        for sheet in result.get('sheets', []):
            print(f"    - {sheet}")

        # Check if file exists
        if Path(output_path).exists():
            size_kb = Path(output_path).stat().st_size / 1024
            print(f"\n  File size: {size_kb:.2f} KB")
        return True
    else:
        error = result.get('error', 'Unknown error')
        if "openpyxl not installed" in error:
            print(f"[SKIP] openpyxl not available - install with: pip install openpyxl")
        else:
            print(f"[FAIL] Report generation failed: {error}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("REPOSITORY ANALYZER TEST SUITE")
    print("="*60)

    results = []
    results.append(("Repository Analysis", test_analyze_repository()))
    results.append(("File Validation", test_validate_file()))
    results.append(("Report Generation", test_generate_report()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
