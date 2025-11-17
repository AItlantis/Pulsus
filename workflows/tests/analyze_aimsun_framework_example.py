"""
Quick Start: Analyze Aimsun Framework
======================================

This example shows how to analyze the Aimsun Python framework
at: C:\Users\jean-noel.diltoer\software\sources\aimsun-python-scripts\FW_Abu_Dhabi\workflow

Usage:
    python analyze_aimsun_framework_example.py
"""

import sys
import json
from pathlib import Path

# Add testudo to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.shared.tools import (
    mcp_analyze_repository,
    mcp_generate_repository_report
)


def main():
    """Analyze the Aimsun framework and generate comprehensive report."""

    # Configuration
    AIMSUN_FRAMEWORK_PATH = r"C:\Users\jean-noel.diltoer\software\sources\aimsun-python-scripts\FW_Abu_Dhabi\workflow"
    OUTPUT_REPORT_PATH = "Aimsun_FW_Abu_Dhabi_Analysis.xlsx"

    print("="*70)
    print("AIMSUN FRAMEWORK ANALYZER")
    print("="*70)
    print(f"\nRepository: {AIMSUN_FRAMEWORK_PATH}")
    print(f"Output Report: {OUTPUT_REPORT_PATH}")
    print("\nStarting analysis...")

    # Step 1: Quick analysis (JSON output)
    print("\n[1/2] Performing repository analysis...")

    analysis_result_json = mcp_analyze_repository.invoke({
        "repo_path": AIMSUN_FRAMEWORK_PATH,
        "ignore_patterns": ["project", "old", "test", "tests", "__pycache__", ".venv"]
    })

    analysis_result = json.loads(analysis_result_json)

    if not analysis_result.get("success"):
        print(f"\n❌ Analysis failed: {analysis_result.get('error')}")
        return 1

    # Display summary statistics
    stats = analysis_result["statistics"]
    print(f"\n✓ Analysis complete!")
    print(f"\nREPOSITORY STATISTICS:")
    print(f"  Files analyzed:        {stats['total_files']}")
    print(f"  Total functions:       {stats['total_functions']}")
    print(f"  Total classes:         {stats['total_classes']}")
    print(f"  Total lines of code:   {stats['total_lines']:,}")
    print(f"  Files with issues:     {stats['files_with_issues']}")
    print(f"  Compliance rate:       {stats['compliance_rate']}")
    print(f"  Third-party imports:   {stats['third_party_imports']}")

    # Display issue summary
    issues = analysis_result["issues_summary"]
    print(f"\nISSUES SUMMARY:")
    print(f"  Total issues:          {issues['total_issues']}")
    for priority, count in issues.get('by_priority', {}).items():
        print(f"  {priority} priority:        {count}")

    # Display top issues
    if issues.get('top_issues'):
        print(f"\n  Top 5 issues:")
        for i, issue in enumerate(issues['top_issues'][:5], 1):
            print(f"    {i}. [{issue['priority']}] {issue['file']}")
            print(f"       {issue['issue']}")

    # Display reusability summary
    reuse = analysis_result["reusability_summary"]
    print(f"\nREUSABILITY METRICS:")
    print(f"  Total functions:       {reuse['total_functions']}")
    print(f"  Average score:         {reuse['average_score']}")
    print(f"  Max score achieved:    {reuse['max_score']}/15")

    # Display top reusable functions
    if reuse.get('top_reusable_functions'):
        print(f"\n  Top 10 reusable functions (candidates for shared utilities):")
        for i, fn in enumerate(reuse['top_reusable_functions'][:10], 1):
            print(f"    {i}. {fn['function']}")
            print(f"       Score: {fn['score']}/15 | Used in {fn['used_in']} files | File: {fn['file']}")

    # Step 2: Generate comprehensive Excel report
    print(f"\n[2/2] Generating Excel report...")

    report_result_json = mcp_generate_repository_report.invoke({
        "repo_path": AIMSUN_FRAMEWORK_PATH,
        "output_path": OUTPUT_REPORT_PATH,
        "ignore_patterns": ["project", "old", "test", "tests", "__pycache__", ".venv"]
    })

    report_result = json.loads(report_result_json)

    if not report_result.get("success"):
        error_msg = report_result.get('error', 'Unknown error')
        if "openpyxl not installed" in error_msg:
            print(f"\n⚠️  Excel report skipped: openpyxl not installed")
            print(f"    Install with: pip install openpyxl")
            print(f"\n✓ JSON analysis complete - see results above")
            return 0
        else:
            print(f"\n❌ Report generation failed: {error_msg}")
            return 1

    print(f"\n✓ Excel report generated!")
    print(f"\nREPORT DETAILS:")
    print(f"  File: {report_result['output_path']}")
    print(f"  Sheets included:")
    for sheet in report_result.get('sheets', []):
        print(f"    - {sheet}")

    # Check file size
    output_path = Path(OUTPUT_REPORT_PATH)
    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        size_mb = size_kb / 1024
        if size_mb >= 1:
            print(f"  File size: {size_mb:.2f} MB")
        else:
            print(f"  File size: {size_kb:.2f} KB")

    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    # Priority actions
    high_priority_count = issues.get('by_priority', {}).get('HIGH', 0)
    if high_priority_count > 0:
        print(f"\n🔴 HIGH PRIORITY ({high_priority_count} issues):")
        print("   1. Open the Excel report and go to 'Issues & Warnings' sheet")
        print("   2. Filter by 'HIGH' priority")
        print("   3. Focus on:")
        print("      - Adding missing #owner= headers")
        print("      - Fixing naming convention violations")

    medium_priority_count = issues.get('by_priority', {}).get('MEDIUM', 0)
    if medium_priority_count > 0:
        print(f"\n🟡 MEDIUM PRIORITY ({medium_priority_count} issues):")
        print("   1. Review 'Files Overview' sheet for missing descriptions")
        print("   2. Add docstring sections to undocumented files")

    # Reusability recommendations
    if reuse.get('top_reusable_functions'):
        highly_reusable = [fn for fn in reuse['top_reusable_functions'] if fn['score'] >= 8]
        if highly_reusable:
            print(f"\n🟢 REUSABILITY OPPORTUNITIES ({len(highly_reusable)} functions):")
            print("   1. Review 'Reusability Analysis' sheet")
            print("   2. Consider extracting functions with score >= 8 to shared utilities")
            print("   3. Top candidates:")
            for fn in highly_reusable[:5]:
                print(f"      - {fn['function']} (score: {fn['score']})")

    # Next steps
    print(f"\nNEXT STEPS:")
    print(f"  1. Open: {OUTPUT_REPORT_PATH}")
    print(f"  2. Review 'Summary & Actions' sheet for overview")
    print(f"  3. Address HIGH priority issues first")
    print(f"  4. Extract highly reusable functions to shared utilities")
    print(f"  5. Re-run this analysis monthly to track improvements")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
