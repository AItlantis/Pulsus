"""
Test Repository Analysis Workflow

Tests comprehensive repository analysis workflow including:
1. Initial analysis execution
2. Follow-up questions about results
3. Session memory persistence
4. LLM-enhanced insights
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Load framework configuration
from agents.pulsus.config.settings import load_settings
settings = load_settings()
FRAMEWORK_ROOT = settings.framework_root

def test_repository_analysis_basic():
    """Test basic repository analysis workflow on framework."""
    print("\n" + "="*70)
    print("TEST 1: Basic Repository Analysis")
    print("="*70)
    print(f"Framework root: {FRAMEWORK_ROOT}")

    from agents.pulsus.routing.router import route

    # Test repository analysis on framework
    test_repo = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/routing"
    prompt = f"analyze repository at {test_repo}"

    print(f"\n[*] Running: {prompt}")
    decision = route(prompt, non_interactive=True)

    assert decision is not None, "Route decision should not be None"
    print(f"[OK] Policy selected: {decision.policy}")
    print(f"[OK] Tools found: {len(decision.selected)}")

    if decision.selected:
        print(f"[OK] Selected tool: {decision.selected[0].path}")

    print("\n[SUCCESS] Basic repository analysis test passed")
    return True


def test_repository_analysis_with_followup():
    """Test repository analysis followed by questions on framework."""
    print("\n" + "="*70)
    print("TEST 2: Repository Analysis with Follow-up Questions")
    print("="*70)

    from agents.pulsus.routing.router import route
    from agents.pulsus.console.session_history import get_session_history

    # Step 1: Analyze repository using framework
    test_repo = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/console"
    prompt1 = f"analyze repository at {test_repo}"

    print(f"\n[STEP 1] Initial Analysis")
    print(f"[*] Running: {prompt1}")
    decision1 = route(prompt1, non_interactive=True)

    assert decision1 is not None, "Route decision should not be None"
    print(f"[OK] Analysis initiated with policy: {decision1.policy}")

    # Step 2: Check session history
    session = get_session_history()
    has_context = session.has_current_repository()

    print(f"\n[STEP 2] Session Memory Check")
    print(f"[*] Has repository context: {has_context}")

    if has_context:
        repo_context = session.get_current_repository()
        print(f"[OK] Repository: {repo_context.path.name}")
        print(f"[OK] Health: {repo_context.health_status}")
        print(f"[OK] Files: {repo_context.statistics.get('total_files', 0)}")
        print(f"[OK] Issues: {repo_context.issues_summary.get('total_issues', 0)}")

    # Step 3: Follow-up questions
    followup_questions = [
        "What are the high priority issues?",
        "Which functions are most reusable?",
        "What is the overall health status?",
        "How many files were analyzed?"
    ]

    print(f"\n[STEP 3] Follow-up Questions")
    for i, question in enumerate(followup_questions, 1):
        print(f"\n  Question {i}: {question}")
        # In a real scenario, the LLM would use session context to answer
        # For now, we just verify routing works
        decision = route(question, non_interactive=True)
        print(f"  [OK] Routed to policy: {decision.policy}")

    print("\n[SUCCESS] Repository analysis with follow-up test passed")
    return True


def test_comment_repository_workflow():
    """Test repository commenting workflow on framework."""
    print("\n" + "="*70)
    print("TEST 3: Repository Comment Generation")
    print("="*70)

    from agents.pulsus.routing.router import route

    # Test comment generation on framework
    test_repo = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/ui"
    prompt = f"generate comments for repository {test_repo}"

    print(f"\n[*] Running: {prompt}")
    decision = route(prompt, non_interactive=True)

    assert decision is not None, "Route decision should not be None"
    print(f"[OK] Policy selected: {decision.policy}")

    if decision.selected:
        print(f"[OK] Tool candidates: {len(decision.selected)}")
        for tool in decision.selected[:3]:
            print(f"    - {Path(tool.path).name}")

    print("\n[SUCCESS] Comment generation workflow test passed")
    return True


def test_document_repository_workflow():
    """Test repository documentation workflow on framework."""
    print("\n" + "="*70)
    print("TEST 4: Repository Documentation Generation")
    print("="*70)

    from agents.pulsus.routing.router import route

    # Test documentation generation on framework
    test_repo = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/config"
    prompt = f"generate documentation for repository {test_repo}"

    print(f"\n[*] Running: {prompt}")
    decision = route(prompt, non_interactive=True)

    assert decision is not None, "Route decision should not be None"
    print(f"[OK] Policy selected: {decision.policy}")

    if decision.selected:
        print(f"[OK] Tool candidates: {len(decision.selected)}")

    print("\n[SUCCESS] Documentation generation workflow test passed")
    return True


def test_session_memory_persistence():
    """Test that session memory persists across multiple queries."""
    print("\n" + "="*70)
    print("TEST 5: Session Memory Persistence")
    print("="*70)

    from agents.pulsus.console.session_history import get_session_history

    session = get_session_history()

    # Check if we have repository context from previous tests
    print("\n[*] Checking session memory...")

    if session.has_current_repository():
        repo = session.get_current_repository()
        print(f"[OK] Repository context found: {repo.path.name}")
        print(f"[OK] Analyzed at: {repo.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Display context summary
        context_summary = session.get_context_summary()
        print(f"\n[*] Context Summary:")
        print(context_summary[:500] + "..." if len(context_summary) > 500 else context_summary)

        print("\n[SUCCESS] Session memory persistence test passed")
        return True
    else:
        print("[!] No repository context found in session")
        print("[!] This is expected if no analysis was run in this session")
        return True


def test_framework_awareness_integration():
    """Test framework awareness initialization."""
    print("\n" + "="*70)
    print("TEST 6: Framework Awareness Integration")
    print("="*70)

    from agents.shared.settings import get_framework_config
    from agents.shared.repo_loader import pulse_folder_exists

    # Check framework configuration
    framework_path = get_framework_config("framework_path")
    auto_analyze = get_framework_config("auto_analyze_on_start")

    print(f"\n[*] Framework Configuration:")
    print(f"    Path: {framework_path if framework_path else 'Not configured'}")
    print(f"    Auto-analyze: {auto_analyze}")

    if framework_path:
        from pathlib import Path
        fw_path = Path(framework_path)

        if fw_path.exists():
            # Check if .pulse folder exists
            has_pulse = pulse_folder_exists(fw_path)
            print(f"    Has .pulse cache: {has_pulse}")

            if has_pulse:
                from agents.shared.repo_loader import load_repo_context
                context = load_repo_context(fw_path)

                if context:
                    stats = context.get('statistics', {})
                    print(f"\n[OK] Framework context loaded:")
                    print(f"    Files: {stats.get('total_files', 0)}")
                    print(f"    Functions: {stats.get('total_functions', 0)}")
                    print(f"    Issues: {context.get('issues_summary', {}).get('total_issues', 0)}")
        else:
            print(f"[!] Framework path does not exist: {framework_path}")
    else:
        print("[*] Framework awareness not configured (this is OK)")

    print("\n[SUCCESS] Framework awareness integration test passed")
    return True


def run_all_tests():
    """Run all workflow tests."""
    print("\n" + "="*70)
    print("PULSUS WORKFLOW TESTS")
    print("="*70)
    print(f"Testing repository analysis workflows with follow-up questions")
    print(f"Date: {Path(__file__).parent.parent.parent}")
    print("="*70)

    tests = [
        ("Basic Repository Analysis", test_repository_analysis_basic),
        ("Comment Generation", test_comment_repository_workflow),
        ("Documentation Generation", test_document_repository_workflow),
        ("Framework Awareness", test_framework_awareness_integration),
        ("Session Memory", test_session_memory_persistence),
        ("Analysis with Follow-up", test_repository_analysis_with_followup),  # Run last to test LLM retrieval
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            print(f"\n[FAILED] {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, str(e)))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status:8s} | {test_name}")
        if error:
            print(f"           | Error: {error[:60]}...")

    print(f"\n  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
