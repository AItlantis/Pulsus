"""
Simplified MCP Test Runner with LLM Prompts
===========================================

Runs existing Phase 1 and Phase 2 tests and generates comprehensive report.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def run_command(cmd: list, description: str, timeout: int = 180):
    """Run a command and return (success, output)"""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent  # Run from Pulsus root, not tests dir
        )

        print(result.stdout)
        if result.stderr and "passed" not in result.stderr.lower():
            print(f"STDERR:\n{result.stderr}\n")

        success = result.returncode == 0
        return success, result.stdout + "\n" + result.stderr

    except subprocess.TimeoutExpired:
        msg = f"TIMEOUT: Command timed out after {timeout}s"
        print(msg)
        return False, msg

    except FileNotFoundError:
        msg = f"ERROR: Command not found: {cmd[0]}"
        print(msg)
        return False, msg

    except Exception as e:
        msg = f"ERROR: {str(e)}"
        print(msg)
        return False, msg


def main():
    """Main test runner"""
    start_time = datetime.now()

    print_section("PULSUS MCP TEST SUITE WITH LLM PROMPTS")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {Path.cwd()}")

    results = {}
    outputs = {}

    # Test 1: Phase 1 Core Framework
    print_section("TEST 1: Phase 1 - Core MCP Framework")
    success, output = run_command(
        [sys.executable, "tests/run_core_tests.py"],
        "Phase 1 Core Framework Tests"
    )
    results["Phase 1: Core Framework"] = success
    outputs["Phase 1: Core Framework"] = output

    # Test 2: Phase 2 Simple Domains
    print_section("TEST 2: Phase 2 - Simple Domains")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "mcp/tests/test_simple_domains.py", "-v", "--tb=short", "--import-mode=importlib", "--no-cov"],
        "Phase 2 Simple Domain Tests"
    )
    results["Phase 2: Simple Domains"] = success
    outputs["Phase 2: Simple Domains"] = output

    # Test 3: Script Operations Tests
    print_section("TEST 3: Script Operations (Detailed)")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "mcp/tests/test_script_ops.py", "-v", "--tb=short", "--import-mode=importlib", "--no-cov"],
        "Script Operations Tests"
    )
    results["Script Operations"] = success
    outputs["Script Operations"] = output

    # Test 4: Core Framework Tests (Detailed)
    print_section("TEST 4: Core Framework (Detailed)")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "mcp/tests/test_core_framework.py", "-v", "--tb=short", "--import-mode=importlib", "--no-cov"],
        "Core Framework Tests"
    )
    results["Core Framework"] = success
    outputs["Core Framework"] = output

    # Generate Summary
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"Total Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")

    print("Detailed Results:")
    for name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")

    # Save detailed report
    report_dir = Path(__file__).parent / "test_results"
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / f"mcp_test_report_{start_time.strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PULSUS MCP TEST REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {(datetime.now() - start_time).total_seconds():.2f}s\n")
        f.write(f"Python: {sys.version}\n")
        f.write("\n" + "=" * 80 + "\n\n")

        f.write(f"SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Test Suites: {total}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Success Rate: {(passed/total*100):.1f}%\n\n")

        for name, success in results.items():
            status = "PASS" if success else "FAIL"
            f.write(f"[{status}] {name}\n")

        f.write("\n" + "=" * 80 + "\n\n")

        # Write detailed outputs
        for name, output in outputs.items():
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"TEST SUITE: {name}\n")
            f.write("=" * 80 + "\n\n")
            f.write(output)
            f.write("\n\n")

    print(f"\nReport saved to: {report_path}")

    # LLM Prompt Examples
    print_section("LLM PROMPT EXAMPLES")

    prompts = [
        {
            "prompt": "Read and analyze the script_ops.py file",
            "mcp_operation": "ScriptOps.read_script(path='mcp/simple/script_ops.py')",
            "expected_output": "MCPResponse with AST analysis, functions, classes, imports",
            "safety_level": "read_only"
        },
        {
            "prompt": "Generate documentation for a Python file",
            "mcp_operation": "ScriptOps.write_md(path='script.py', content=None)",
            "expected_output": "MCPResponse with doc_path",
            "safety_level": "write_safe (requires confirmation)"
        },
        {
            "prompt": "Add comments to functions in a script",
            "mcp_operation": "ScriptOps.add_comments(path='script.py')",
            "expected_output": "MCPResponse with generated comments",
            "safety_level": "read_only (AI-powered)"
        },
        {
            "prompt": "Check code formatting",
            "mcp_operation": "ScriptOps.format_script(path='script.py', check_only=True)",
            "expected_output": "MCPResponse with formatting status",
            "safety_level": "write_safe (when not check_only)"
        },
        {
            "prompt": "Scan directory structure",
            "mcp_operation": "ScriptOps.scan_structure(path='mcp/simple/')",
            "expected_output": "MCPResponse with structure map and statistics",
            "safety_level": "read_only + cached"
        },
        {
            "prompt": "What can ScriptOps do?",
            "mcp_operation": "ScriptOps.get_capabilities()",
            "expected_output": "List of operations with parameters and safety levels",
            "safety_level": "N/A (metadata)"
        },
        {
            "prompt": "Execute an operation by name",
            "mcp_operation": "ScriptOps.execute('read_script', path='file.py')",
            "expected_output": "MCPResponse from the named operation",
            "safety_level": "Depends on operation"
        }
    ]

    print("\nSample LLM Prompts and Expected MCP Operations:\n")

    for i, example in enumerate(prompts, 1):
        print(f"{i}. LLM Prompt: '{example['prompt']}'")
        print(f"   MCP Operation: {example['mcp_operation']}")
        print(f"   Expected Output: {example['expected_output']}")
        print(f"   Safety Level: {example['safety_level']}")
        print()

    # Write prompts to report
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("LLM PROMPT EXAMPLES\n")
        f.write("=" * 80 + "\n\n")

        for i, example in enumerate(prompts, 1):
            f.write(f"{i}. LLM Prompt: '{example['prompt']}'\n")
            f.write(f"   MCP Operation: {example['mcp_operation']}\n")
            f.write(f"   Expected Output: {example['expected_output']}\n")
            f.write(f"   Safety Level: {example['safety_level']}\n\n")

    print(f"\nLLM prompts added to report: {report_path}")

    # Exit with appropriate code
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_section("TEST RUN COMPLETE")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'SUCCESS' if failed == 0 else 'FAILED'}")
    print(f"Report: {report_path}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
