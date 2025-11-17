"""
LLM-Enhanced Repository Analyzer

This tool wraps the MCP repository analysis tools with LLM interpretation,
providing natural language summaries, insights, and recommendations.

__domain__ = "analysis"
__action__ = "analyze_repository"
"""

import json
from pathlib import Path
from typing import Dict, Any


def handle(repo_path: str = None, generate_report: bool = False, output_path: str = None,
           save_to_pulsus: bool = True, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Analyze a Python repository with LLM-enhanced insights.

    Args:
        repo_path: Path to repository (defaults to current working directory)
        generate_report: Whether to generate Excel report (default: False)
        output_path: Path for Excel report (default: auto-generated)
        save_to_pulsus: Save analysis to .pulsus/ directory (default: True)
        force_refresh: Force re-analysis even if cached results exist (default: False)

    Returns:
        Dictionary with analysis results and LLM insights
    """
    # Import with proper path handling
    import sys
    from pathlib import Path as PathLib

    # Add testudo root to path (parent of agents/)
    # File is at: testudo/agents/pulsus/workflows/tools/analyze/repository_analyzer_llm.py
    # We need: testudo/ (5 levels up)
    testudo_root = PathLib(__file__).parents[5]
    if str(testudo_root) not in sys.path:
        sys.path.insert(0, str(testudo_root))

    from agents.shared.tools import mcp_analyze_repository, mcp_generate_repository_report
    from agents.pulsus.workflows.utils.context_loader import (
        load_repository_context,
        save_repository_context,
        is_context_available,
        get_context_age
    )

    # Default to current directory if no path provided
    if not repo_path:
        repo_path = str(Path.cwd())

    repo_path_obj = PathLib(repo_path).resolve()

    # Check for cached analysis
    if not force_refresh and is_context_available(repo_path_obj):
        age_seconds = get_context_age(repo_path_obj)
        age_hours = age_seconds / 3600 if age_seconds else 0

        print(f"[*] Found cached analysis (age: {age_hours:.1f} hours)")
        print(f"[*] Loading from .pulsus/repository_analysis.json...")

        cached_context = load_repository_context(repo_path_obj)
        if cached_context:
            print(f"[*] Using cached analysis. To force refresh, use force_refresh=True")
            # Display cached summary
            if "llm_summary" in cached_context:
                print(cached_context["llm_summary"])
            return cached_context

    # Perform analysis
    print(f"[*] Analyzing repository: {repo_path}")
    print("[*] Please wait, this may take a moment...")

    analysis_json = mcp_analyze_repository.invoke({
        "repo_path": repo_path,
        "ignore_patterns": ["__pycache__", ".venv", "venv", ".git", "node_modules"]
    })

    analysis = json.loads(analysis_json)

    if not analysis.get("success"):
        return {
            "success": False,
            "error": analysis.get("error"),
            "llm_summary": f"[FAIL] Analysis failed: {analysis.get('error')}"
        }

    # Extract key metrics
    stats = analysis["statistics"]
    issues = analysis["issues_summary"]
    reuse = analysis["reusability_summary"]

    # Build natural language summary
    summary_parts = []

    # Overall health assessment
    compliance_rate = float(stats["compliance_rate"].rstrip("%"))
    if compliance_rate >= 80:
        health = "[EXCELLENT]"
    elif compliance_rate >= 60:
        health = "[GOOD]"
    elif compliance_rate >= 40:
        health = "[NEEDS IMPROVEMENT]"
    else:
        health = "[CRITICAL]"

    summary_parts.append(f"\n{'='*70}")
    summary_parts.append(f"REPOSITORY ANALYSIS COMPLETE")
    summary_parts.append(f"{'='*70}")
    summary_parts.append(f"\nOVERALL HEALTH: {health} (Compliance: {stats['compliance_rate']})")

    # Key statistics
    summary_parts.append(f"\nKEY STATISTICS:")
    summary_parts.append(f"   - Files analyzed:      {stats['total_files']:,}")
    summary_parts.append(f"   - Total functions:     {stats['total_functions']:,}")
    summary_parts.append(f"   - Total classes:       {stats['total_classes']:,}")
    summary_parts.append(f"   - Lines of code:       {stats['total_lines']:,}")
    summary_parts.append(f"   - Third-party deps:    {stats['third_party_imports']}")

    # Issues analysis with thinking
    summary_parts.append(f"\nQUALITY ANALYSIS:")
    summary_parts.append(f"   - Files with issues:   {stats['files_with_issues']}/{stats['total_files']}")
    summary_parts.append(f"   - Total issues found:  {issues['total_issues']}")

    if issues.get('by_priority'):
        for priority, count in sorted(issues['by_priority'].items(), key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x[0], 3)):
            marker = {'HIGH': '[!]', 'MEDIUM': '[*]', 'LOW': '[+]'}.get(priority, '[-]')
            summary_parts.append(f"     {marker} {priority}: {count}")

    # Provide thinking and interpretation
    summary_parts.append(f"\nANALYSIS INSIGHTS:")

    # Issue insights
    high_priority = issues.get('by_priority', {}).get('HIGH', 0)
    if high_priority > 0:
        summary_parts.append(f"   [!] {high_priority} HIGH priority issues require immediate attention")
        summary_parts.append(f"       These likely include missing ownership, naming violations")
    else:
        summary_parts.append(f"   [OK] No high priority issues - excellent!")

    # Code quality insights
    if stats['files_with_issues'] > stats['total_files'] * 0.5:
        summary_parts.append(f"   [NOTE] Over 50% of files have issues - suggests systemic quality gaps")
        summary_parts.append(f"       Recommend: Establish coding standards and review process")
    elif stats['files_with_issues'] > 0:
        summary_parts.append(f"   [+] Most files are compliant - spot issues to address")

    # Reusability insights
    avg_score = reuse.get('average_score', 0)
    summary_parts.append(f"\nREUSABILITY ASSESSMENT:")
    summary_parts.append(f"   - Average score:       {avg_score:.2f}/15")

    if avg_score < 3:
        summary_parts.append(f"   [INSIGHT] Low reusability - significant refactoring opportunity")
        summary_parts.append(f"       Many functions could benefit from better documentation")
        summary_parts.append(f"       and more generic naming patterns")
    elif avg_score < 6:
        summary_parts.append(f"   [INSIGHT] Moderate reusability - good foundation, room for improvement")
        summary_parts.append(f"       Focus on extracting high-scoring functions to shared utilities")
    else:
        summary_parts.append(f"   [EXCELLENT] Excellent reusability - well-structured codebase!")

    # Top reusable functions
    if reuse.get('top_reusable_functions'):
        top_funcs = reuse['top_reusable_functions'][:5]
        highly_reusable = [f for f in top_funcs if f['score'] >= 8]

        if highly_reusable:
            summary_parts.append(f"\nTOP REUSABLE FUNCTIONS ({len(highly_reusable)} candidates for extraction):")
            for i, fn in enumerate(highly_reusable, 1):
                summary_parts.append(f"   {i}. {fn['function']} (score: {fn['score']}/15)")
                summary_parts.append(f"      Used in {fn['used_in']} files - {fn['file']}")

    # Dependency insights
    if stats.get('top_imports'):
        summary_parts.append(f"\nTOP DEPENDENCIES:")
        for module, count in list(stats['top_imports'].items())[:5]:
            summary_parts.append(f"   - {module}: {count} imports")

    # Critical issues to address
    if issues.get('top_issues'):
        summary_parts.append(f"\nIMMEDIATE ACTIONS REQUIRED:")
        top_issues = issues['top_issues'][:5]

        for i, issue in enumerate(top_issues, 1):
            if issue['priority'] == 'HIGH':
                summary_parts.append(f"   {i}. [{issue['priority']}] {issue['file']}")
                summary_parts.append(f"      -> {issue['issue']}")

    # Recommendations
    summary_parts.append(f"\nRECOMMENDATIONS:")

    if high_priority > 0:
        summary_parts.append(f"   1. Address {high_priority} HIGH priority issues immediately")
        summary_parts.append(f"      - Add #owner= metadata to files")
        summary_parts.append(f"      - Fix naming convention violations")

    if stats['files_with_issues'] > 5:
        summary_parts.append(f"   2. Establish quality gates:")
        summary_parts.append(f"      - Pre-commit hooks for validation")
        summary_parts.append(f"      - Require docstrings for all files")

    if reuse.get('top_reusable_functions'):
        highly_reusable_count = len([f for f in reuse['top_reusable_functions'] if f['score'] >= 8])
        if highly_reusable_count > 0:
            summary_parts.append(f"   3. Extract {highly_reusable_count} highly reusable functions to shared utilities")
            summary_parts.append(f"      - Creates reusable library")
            summary_parts.append(f"      - Reduces code duplication")

    summary_parts.append(f"   4. Re-run this analysis monthly to track improvements")

    # Generate Excel report if requested
    report_path = None
    if generate_report:
        if not output_path:
            repo_name = Path(repo_path).name
            output_path = f"{repo_name}_analysis.xlsx"

        summary_parts.append(f"\nGenerating Excel report...")

        report_json = mcp_generate_repository_report.invoke({
            "repo_path": repo_path,
            "output_path": output_path,
            "ignore_patterns": ["__pycache__", ".venv", "venv", ".git", "node_modules"]
        })

        report = json.loads(report_json)

        if report.get("success"):
            report_path = report['output_path']
            summary_parts.append(f"   [OK] Report saved: {report_path}")
            summary_parts.append(f"   Sheets: {', '.join(report.get('sheets', []))}")
        else:
            summary_parts.append(f"   [WARN] Report generation failed: {report.get('error')}")

    summary_parts.append(f"\n{'='*70}")

    # Combine all parts
    llm_summary = "\n".join(summary_parts)

    # Print the summary
    print(llm_summary)

    # Store in session history for LLM access
    try:
        from agents.pulsus.console.session_history import get_session_history
        session = get_session_history()
        session.set_current_repository(
            path=Path(repo_path),
            llm_summary=llm_summary,
            health_status=health,
            statistics=stats,
            issues_summary=issues,
            reusability_summary=reuse,
            raw_analysis=analysis
        )
        print(f"\n[*] Repository analysis stored in session memory")
        print(f"[*] You can now ask follow-up questions about this analysis")
    except Exception as e:
        # Don't fail if session storage doesn't work
        print(f"\n[WARN] Could not store in session: {e}")

    # Save to .pulsus/ directory for persistent storage
    if save_to_pulsus:
        try:
            # Prepare analysis data for storage
            analysis_data = {
                "llm_summary": llm_summary,
                "health_status": health,
                "statistics": stats,
                "issues_summary": issues,
                "reusability_summary": reuse,
                "raw_analysis": analysis,
                "success": True
            }

            # Save analysis to .pulsus/ using our context loader
            if save_repository_context(repo_path_obj, analysis_data):
                print(f"\n[*] Analysis saved to .pulsus/repository_analysis.json")
                print(f"[*] This context will be used for file analysis within this repository")
            else:
                print(f"\n[WARN] Could not save to .pulsus/ directory")

        except Exception as e:
            # Don't fail if .pulsus/ storage doesn't work
            print(f"\n[WARN] Could not save to .pulsus/ directory: {e}")

    # Return structured result
    return {
        "success": True,
        "llm_summary": llm_summary,
        "repository": repo_path,
        "health_status": health,
        "statistics": stats,
        "issues_summary": issues,
        "reusability_summary": reuse,
        "report_path": report_path,
        "raw_analysis": analysis
    }


# For command-line testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        generate_report = "--report" in sys.argv
        result = handle(repo_path=repo_path, generate_report=generate_report)
        sys.exit(0 if result["success"] else 1)
    else:
        print("Usage: python repository_analyzer_llm.py <repo_path> [--report]")
        sys.exit(1)
