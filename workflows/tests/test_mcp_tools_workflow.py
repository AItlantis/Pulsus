"""
Test MCP Tools Workflow

Tests MCP tools integration and workflow execution:
1. Script analysis (@path syntax)
2. Documentation generation
3. Code formatting
4. Structure scanning
5. Validation and quality checks
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


def test_script_analysis_workflow():
    """Test script analysis with @path syntax using framework files."""
    print("\n" + "="*70)
    print("TEST 1: Script Analysis (@path syntax)")
    print("="*70)
    print(f"Framework root: {FRAMEWORK_ROOT}")

    from agents.pulsus.routing.router import route

    # Find a Python file in the framework to analyze
    if FRAMEWORK_ROOT.exists():
        py_files = list(FRAMEWORK_ROOT.rglob("*.py"))
        if py_files:
            # Use absolute path since framework may be outside current working directory
            test_file = str(py_files[0].resolve())
            prompt = f"@{test_file}"

            print(f"\n[*] Running: {prompt}")
            decision = route(prompt, non_interactive=True)

            assert decision is not None, "Route decision should not be None"
            print(f"[OK] Policy selected: {decision.policy}")
        else:
            print("[!] No Python files found in framework")
    else:
        print(f"[!] Framework root does not exist: {FRAMEWORK_ROOT}")
        print("[*] Falling back to test file in agents directory")
        test_file = "agents/pulsus/routing/mcp_router.py"
        prompt = f"@{test_file}"
        decision = route(prompt, non_interactive=True)

    print("\n[SUCCESS] Script analysis workflow test passed")
    return True


def test_mcp_read_script():
    """Test mcp_read_script tool directly on framework files."""
    print("\n" + "="*70)
    print("TEST 2: MCP Read Script Tool")
    print("="*70)

    try:
        from agents.shared.tools import mcp_read_script
        import json

        # Use a file from framework if available
        if FRAMEWORK_ROOT.exists():
            py_files = list(FRAMEWORK_ROOT.rglob("*.py"))
            if py_files:
                # Use absolute path since framework may be outside current working directory
                test_file = str(py_files[0].resolve())
            else:
                test_file = "agents/pulsus/ui/display_manager.py"
        else:
            test_file = "agents/pulsus/ui/display_manager.py"

        print(f"\n[*] Reading script: {test_file}")

        result_json = mcp_read_script.invoke({"path": test_file})
        result = json.loads(result_json)

        assert result.get("success"), f"Tool failed: {result.get('error')}"

        print(f"[OK] Success: {result['success']}")
        print(f"[OK] File: {result['file_path']}")

        ast_analysis = result.get('ast_analysis', {})
        print(f"[OK] Functions found: {len(ast_analysis.get('functions', []))}")
        print(f"[OK] Classes found: {len(ast_analysis.get('classes', []))}")
        print(f"[OK] Imports found: {len(ast_analysis.get('imports', []))}")

        print("\n[SUCCESS] MCP read script test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_analyze_repository():
    """Test mcp_analyze_repository tool directly on framework."""
    print("\n" + "="*70)
    print("TEST 3: MCP Analyze Repository Tool")
    print("="*70)

    try:
        from agents.shared.tools import mcp_analyze_repository
        import json

        # Use framework root as test repository
        test_repo = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/console"
        print(f"\n[*] Analyzing repository: {test_repo}")

        result_json = mcp_analyze_repository.invoke({
            "repo_path": test_repo,
            "ignore_patterns": ["__pycache__", ".venv", "test"]
        })
        result = json.loads(result_json)

        assert result.get("success"), f"Tool failed: {result.get('error')}"

        print(f"[OK] Success: {result['success']}")

        stats = result.get('statistics', {})
        print(f"[OK] Files analyzed: {stats.get('total_files', 0)}")
        print(f"[OK] Total functions: {stats.get('total_functions', 0)}")
        print(f"[OK] Total classes: {stats.get('total_classes', 0)}")

        issues = result.get('issues_summary', {})
        print(f"[OK] Issues found: {issues.get('total_issues', 0)}")

        reuse = result.get('reusability_summary', {})
        print(f"[OK] Avg reusability: {reuse.get('average_score', 0):.2f}/15")

        print("\n[SUCCESS] MCP analyze repository test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_comment_repository():
    """Test mcp_comment_repository tool on framework."""
    print("\n" + "="*70)
    print("TEST 4: MCP Comment Repository Tool")
    print("="*70)

    try:
        from agents.shared.tools import mcp_comment_repository
        import json

        # Use a subdirectory of framework if available
        if FRAMEWORK_ROOT.exists():
            subdirs = [d for d in FRAMEWORK_ROOT.iterdir() if d.is_dir() and not d.name.startswith('.')]
            test_repo = str(subdirs[0]) if subdirs else str(FRAMEWORK_ROOT)
        else:
            test_repo = "agents/pulsus/ui"

        print(f"\n[*] Generating comments for: {test_repo}")

        result_json = mcp_comment_repository.invoke({
            "repo_path": test_repo,
            "strategy": "docstring"
        })
        result = json.loads(result_json)

        assert result.get("success"), f"Tool failed: {result.get('error')}"

        print(f"[OK] Success: {result['success']}")
        print(f"[OK] Files processed: {result.get('files_processed', 0)}")
        print(f"[OK] Total functions: {result.get('total_functions', 0)}")
        print(f"[OK] Strategy: {result.get('strategy', 'unknown')}")

        # Show sample comments
        comments = result.get('comments', {})
        if comments:
            sample_file = list(comments.keys())[0]
            sample_comments = comments[sample_file]
            print(f"\n[*] Sample comments from {sample_file}:")
            for func_name, comment in list(sample_comments.items())[:2]:
                print(f"    - {func_name}: {comment[:60]}...")

        print("\n[SUCCESS] MCP comment repository test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_scan_structure():
    """Test mcp_scan_structure tool on framework."""
    print("\n" + "="*70)
    print("TEST 5: MCP Scan Structure Tool")
    print("="*70)

    try:
        from agents.shared.tools import mcp_scan_structure
        import json

        # Use framework root for structure scanning
        test_dir = str(FRAMEWORK_ROOT) if FRAMEWORK_ROOT.exists() else "agents/pulsus/routing"
        print(f"\n[*] Scanning structure: {test_dir}")

        result_json = mcp_scan_structure.invoke({
            "base_dir": test_dir,
            "include_patterns": ["*.py"],
            "exclude_patterns": ["__pycache__", "test"]
        })
        result = json.loads(result_json)

        assert result.get("success"), f"Tool failed: {result.get('error')}"

        print(f"[OK] Success: {result['success']}")

        stats = result.get('statistics', {})
        print(f"[OK] Total files: {stats.get('total_files', 0)}")
        print(f"[OK] Total lines: {stats.get('total_lines', 0)}")
        print(f"[OK] Total imports: {stats.get('total_imports', 0)}")

        # Show top modules
        top_modules = stats.get('top_modules', [])
        if top_modules:
            print(f"\n[*] Top imported modules:")
            for module, count in top_modules[:5]:
                print(f"    - {module}: {count} times")

        print("\n[SUCCESS] MCP scan structure test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_validate_file():
    """Test mcp_validate_python_file tool on framework file."""
    print("\n" + "="*70)
    print("TEST 6: MCP Validate File Tool")
    print("="*70)

    try:
        from agents.shared.tools import mcp_validate_python_file
        import json

        # Use a file from framework if available
        if FRAMEWORK_ROOT.exists():
            py_files = list(FRAMEWORK_ROOT.rglob("*.py"))
            # Use absolute path since framework may be outside current working directory
            test_file = str(py_files[0].resolve()) if py_files else "agents/pulsus/routing/mcp_router.py"
        else:
            test_file = "agents/pulsus/routing/mcp_router.py"

        print(f"\n[*] Validating file: {test_file}")

        result_json = mcp_validate_python_file.invoke({"file_path": test_file})
        result = json.loads(result_json)

        assert result.get("success"), f"Tool failed: {result.get('error')}"

        print(f"[OK] Success: {result['success']}")

        issues = result.get('issues', [])
        print(f"[OK] Issues found: {len(issues)}")

        if issues:
            print(f"\n[*] Sample issues:")
            for issue in issues[:3]:
                print(f"    - {issue}")

        metadata = result.get('metadata', {})
        print(f"\n[*] Metadata:")
        if metadata.get('owner'):
            print(f"    - Owner: {metadata['owner']}")
        if metadata.get('atype'):
            print(f"    - Type: {metadata['atype']}")

        print("\n[SUCCESS] MCP validate file test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pulse_folder_generation():
    """Test that .pulse/ folder outputs are generated for framework."""
    print("\n" + "="*70)
    print("TEST 7: .pulse/ Folder Generation")
    print("="*70)

    try:
        from agents.shared.repo_loader import ensure_repo_context, get_pulse_folder
        from pathlib import Path

        # Use framework root for .pulse generation
        test_repo = FRAMEWORK_ROOT if FRAMEWORK_ROOT.exists() else Path("agents/pulsus/console")
        print(f"\n[*] Ensuring repository context: {test_repo}")

        # This will analyze and generate .pulse/ outputs
        context = ensure_repo_context(test_repo)

        assert context, "Context should not be None"
        print(f"[OK] Context generated successfully")

        # Check for .pulse/ folder
        pulse_folder = get_pulse_folder(test_repo)
        print(f"\n[*] Checking .pulse/ folder: {pulse_folder}")

        if pulse_folder.exists():
            print(f"[OK].pulse/ folder exists")

            # Check for key files
            expected_files = [
                "repo_index.json",
                "imports_graph.json",
                "functions_index.json"
            ]

            for filename in expected_files:
                file_path = pulse_folder / filename
                if file_path.exists():
                    size = file_path.stat().st_size / 1024
                    print(f"[OK]{filename} exists ({size:.1f} KB)")
                else:
                    print(f"[!] {filename} not found")

            # Check for cards directory
            cards_dir = pulse_folder / "cards"
            if cards_dir.exists():
                card_count = len(list(cards_dir.rglob("*.md")))
                print(f"[OK]cards/ directory exists ({card_count} cards)")
        else:
            print(f"[!] .pulse/ folder not found")

        print("\n[SUCCESS] .pulse/ folder generation test passed")
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all MCP tools workflow tests."""
    print("\n" + "="*70)
    print("PULSUS MCP TOOLS WORKFLOW TESTS")
    print("="*70)
    print(f"Testing MCP tools integration and execution")
    print("="*70)

    tests = [
        ("Script Analysis", test_script_analysis_workflow),
        ("MCP Read Script", test_mcp_read_script),
        ("MCP Analyze Repository", test_mcp_analyze_repository),
        ("MCP Comment Repository", test_mcp_comment_repository),
        ("MCP Scan Structure", test_mcp_scan_structure),
        ("MCP Validate File", test_mcp_validate_file),
        (".pulse/ Generation", test_pulse_folder_generation),
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
