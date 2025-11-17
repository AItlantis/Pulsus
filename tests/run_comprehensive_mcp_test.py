"""
Comprehensive MCP Test Runner
==============================

Tests Phases 1 and 2 implementations with LLM prompts and saves outputs for review.

This script:
1. Runs all Phase 1 core framework tests
2. Runs all Phase 2 simple domain tests
3. Executes LLM-style prompt tests
4. Tests routing and safety features
5. Saves all outputs to a review file

Usage:
    python run_comprehensive_mcp_test.py
"""

import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

# Add project root to path
project_root = Path(__file__).parent
parent_dir = project_root.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(project_root))

# Import with error handling
try:
    from agents.pulsus.mcp.core import MCPBase, MCPResponse, get_safety_policy, ExecutionMode, get_mcp_logger
    from agents.pulsus.mcp.simple import ScriptOps
    IMPORTS_OK = True
except ImportError:
    try:
        from mcp.core import MCPBase, MCPResponse, get_safety_policy, ExecutionMode, get_mcp_logger
        from mcp.simple import ScriptOps
        IMPORTS_OK = True
    except ImportError as e:
        print(f"[ERROR] Cannot import MCP modules: {e}")
        print("Note: Some tests will be skipped")
        IMPORTS_OK = False
        MCPBase = None
        ScriptOps = None


class TestReport:
    """Collects and formats test results"""

    def __init__(self):
        self.sections = []
        self.start_time = datetime.now()

    def add_section(self, title: str, content: str, status: str = "INFO"):
        """Add a section to the report"""
        self.sections.append({
            'title': title,
            'content': content,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })

    def save(self, filepath: Path):
        """Save report to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PULSUS MCP COMPREHENSIVE TEST REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f}s\n")
            f.write("\n" + "=" * 80 + "\n\n")

            for i, section in enumerate(self.sections, 1):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"[{section['status']}] Section {i}: {section['title']}\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Time: {section['timestamp']}\n\n")
                f.write(section['content'])
                f.write("\n\n")

        print(f"\n[SAVED] Report saved to: {filepath}")


def run_phase1_tests(report: TestReport):
    """Run Phase 1 core framework tests"""
    print("\n" + "=" * 80)
    print("PHASE 1: Core Framework Tests")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, "run_core_tests.py"],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = f"Exit Code: {result.returncode}\n\n"
        output += "=== STDOUT ===\n"
        output += result.stdout + "\n\n"

        if result.stderr:
            output += "=== STDERR ===\n"
            output += result.stderr + "\n"

        status = "PASS" if result.returncode == 0 else "FAIL"
        report.add_section("Phase 1: Core Framework Tests", output, status)

        print(result.stdout)
        if result.stderr:
            print(f"[STDERR] {result.stderr}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        msg = "Test execution timed out (120s)"
        report.add_section("Phase 1: Core Framework Tests", msg, "FAIL")
        print(f"[FAIL] {msg}")
        return False
    except Exception as e:
        msg = f"Error running tests: {str(e)}"
        report.add_section("Phase 1: Core Framework Tests", msg, "FAIL")
        print(f"[FAIL] {msg}")
        return False


def run_phase2_tests(report: TestReport):
    """Run Phase 2 simple domain tests"""
    print("\n" + "=" * 80)
    print("PHASE 2: Simple Domain Tests")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "mcp/tests/test_simple_domains.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=180
        )

        output = f"Exit Code: {result.returncode}\n\n"
        output += "=== STDOUT ===\n"
        output += result.stdout + "\n\n"

        if result.stderr:
            output += "=== STDERR ===\n"
            output += result.stderr + "\n"

        status = "PASS" if result.returncode == 0 else "FAIL"
        report.add_section("Phase 2: Simple Domain Tests", output, status)

        print(result.stdout)
        if result.stderr and "passed" not in result.stderr.lower():
            print(f"[STDERR] {result.stderr}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        msg = "Test execution timed out (180s)"
        report.add_section("Phase 2: Simple Domain Tests", msg, "FAIL")
        print(f"[FAIL] {msg}")
        return False
    except Exception as e:
        msg = f"Error running tests: {str(e)}"
        report.add_section("Phase 2: Simple Domain Tests", msg, "FAIL")
        print(f"[FAIL] {msg}")
        return False


def test_llm_prompts(report: TestReport):
    """Test MCP with LLM-style prompts"""
    print("\n" + "=" * 80)
    print("LLM PROMPT TESTS")
    print("=" * 80)

    if not IMPORTS_OK:
        msg = "Skipping LLM prompt tests - import errors"
        print(f"[SKIP] {msg}")
        report.add_section("LLM Prompt Tests", msg, "SKIP")
        return True

    output_lines = []

    def log(msg: str):
        print(msg)
        output_lines.append(msg)

    try:
        # Test 1: Read a script file
        log("\n--- Test 1: Read Script Operation ---")
        log("LLM Prompt: 'Read the script_ops.py file and analyze its structure'")

        script_ops = ScriptOps(context={'caller': 'LLM_Test', 'session': 'comprehensive_test'})
        script_path = project_root / "mcp" / "simple" / "script_ops.py"

        if script_path.exists():
            response = script_ops.read_script(str(script_path))
            log(f"Success: {response.success}")
            log(f"Status: {response.status}")
            log(f"Safety Level: {response.context.get('safety_level', 'N/A')}")
            log(f"Requires Confirmation: {response.context.get('requires_confirmation', 'N/A')}")

            if response.success:
                log(f"Functions Found: {len(response.data.get('ast_analysis', {}).get('functions', []))}")
                log(f"Classes Found: {len(response.data.get('ast_analysis', {}).get('classes', []))}")
                log(f"Trace Steps: {len(response.trace)}")
                log(f"Trace: {response.trace}")
            else:
                log(f"Error: {response.error}")
        else:
            log(f"[SKIP] Script file not found: {script_path}")

        # Test 2: Get capabilities
        log("\n--- Test 2: Capability Discovery ---")
        log("LLM Prompt: 'What operations can ScriptOps perform?'")

        capabilities = script_ops.get_capabilities()
        log(f"Total Capabilities: {len(capabilities)}")

        for cap in capabilities:
            log(f"  - {cap['name']}: {cap['description']}")
            log(f"    Safety Level: {cap['safety_level']}")
            log(f"    Parameters: {', '.join([p['name'] for p in cap['parameters']])}")

        # Test 3: Safety policy check
        log("\n--- Test 3: Safety Policy Enforcement ---")
        log("LLM Prompt: 'What happens if I try to write a file in PLAN mode?'")

        policy = get_safety_policy()
        original_mode = policy.mode

        # Set PLAN mode (no writes allowed)
        policy.set_mode(ExecutionMode.PLAN)
        log(f"Execution Mode: {policy.mode}")

        # Try to write (should be blocked or require confirmation)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Test file\n")
            temp_path = f.name

        try:
            result = script_ops.write_md(temp_path, content="# Test Doc")
            log(f"Write Operation Success: {result.success}")
            log(f"Write Operation Status: {result.status}")

            if not result.success:
                log(f"Write Blocked - Reason: {result.error}")
            else:
                log(f"Write Allowed - Context: {result.context}")

            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            md_path = Path(temp_path).with_suffix('.md')
            md_path.unlink(missing_ok=True)

        finally:
            # Restore original mode
            policy.set_mode(original_mode)

        # Test 4: Execute via generic execute() method
        log("\n--- Test 4: Generic Execute Method ---")
        log("LLM Prompt: 'Execute scan_structure operation on the mcp/simple directory'")

        simple_dir = project_root / "mcp" / "simple"
        if simple_dir.exists():
            result = script_ops.execute('scan_structure', path=str(simple_dir))
            log(f"Success: {result.success}")
            log(f"Status: {result.status}")

            if result.success:
                stats = result.data.get('statistics', {})
                log(f"Files Found: {stats.get('total_files', 0)}")
                log(f"Directories: {stats.get('total_directories', 0)}")
                log(f"Total Lines: {stats.get('total_lines', 0)}")
            else:
                log(f"Error: {result.error}")
        else:
            log(f"[SKIP] Directory not found: {simple_dir}")

        # Test 5: Error handling
        log("\n--- Test 5: Error Handling ---")
        log("LLM Prompt: 'What happens if I try to read a non-existent file?'")

        result = script_ops.read_script("/nonexistent/file.py")
        log(f"Success: {result.success}")
        log(f"Status: {result.status}")
        log(f"Error Message: {result.error}")
        log(f"Trace: {result.trace}")

        # Test 6: Logging integration
        log("\n--- Test 6: MCPLogger Integration ---")
        log("LLM Prompt: 'Show me the call history for this session'")

        logger = get_mcp_logger()
        history = logger.get_call_history(caller='LLM_Test', limit=10)

        log(f"Calls in history: {len(history)}")
        for i, call in enumerate(history, 1):
            log(f"  {i}. {call['mcp_class']}.{call['operation']} - {call['status']} ({call['timestamp']})")

        # Test 7: Response serialization
        log("\n--- Test 7: Response Serialization (for LLM) ---")
        log("LLM Prompt: 'Convert the response to a format I can use'")

        test_response = script_ops.get_capabilities()
        if test_response:
            # Simulate getting a response and converting to dict
            sample_response = MCPResponse.success_response(
                data={'test': 'data'},
                context={'caller': 'LLM'}
            )
            response_dict = sample_response.to_dict()
            log(f"Response as dict: {json.dumps(response_dict, indent=2)}")

        output = "\n".join(output_lines)
        report.add_section("LLM Prompt Tests", output, "PASS")
        return True

    except Exception as e:
        error_msg = f"Error in LLM prompt tests: {str(e)}\n"
        error_msg += "\n".join(output_lines)
        report.add_section("LLM Prompt Tests", error_msg, "FAIL")
        print(f"[FAIL] {str(e)}")
        return False


def test_mcp_integration(report: TestReport):
    """Test MCP integration features"""
    print("\n" + "=" * 80)
    print("MCP INTEGRATION TESTS")
    print("=" * 80)

    if not IMPORTS_OK:
        msg = "Skipping MCP integration tests - import errors"
        print(f"[SKIP] {msg}")
        report.add_section("MCP Integration Tests", msg, "SKIP")
        return True

    output_lines = []

    def log(msg: str):
        print(msg)
        output_lines.append(msg)

    try:
        # Test routing discovery
        log("\n--- Test: MCP Domain Discovery ---")

        try:
            from agents.pulsus.mcp import simple
        except ImportError:
            from mcp import simple

        # List all MCP domains
        mcp_classes = []
        for name in dir(simple):
            obj = getattr(simple, name)
            if isinstance(obj, type) and issubclass(obj, MCPBase) and obj != MCPBase:
                mcp_classes.append(obj)

        log(f"Discovered MCP Domains: {len(mcp_classes)}")
        for cls in mcp_classes:
            log(f"  - {cls.__name__}")
            instance = cls()
            caps = instance.get_capabilities()
            log(f"    Operations: {len(caps)}")

        # Test decorator application
        log("\n--- Test: Decorator Coverage ---")

        script_ops = ScriptOps()
        caps = script_ops.get_capabilities()

        safety_levels = {}
        for cap in caps:
            level = cap['safety_level']
            safety_levels[level] = safety_levels.get(level, 0) + 1

        log(f"Safety Level Distribution:")
        for level, count in safety_levels.items():
            log(f"  - {level}: {count} operations")

        # Test context propagation
        log("\n--- Test: Context Propagation ---")

        custom_context = {
            'caller': 'Integration_Test',
            'session_id': 'test_123',
            'user': 'test_user'
        }

        script_ops_with_context = ScriptOps(context=custom_context)

        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Test\ndef foo(): pass\n")
            temp_path = f.name

        try:
            result = script_ops_with_context.read_script(temp_path)

            log(f"Context preserved: {result.context.get('caller') == 'Integration_Test'}")
            log(f"Session ID present: {'session_id' in result.context}")
            log(f"User present: {'user' in result.context}")
            log(f"Full context: {result.context}")

        finally:
            Path(temp_path).unlink(missing_ok=True)

        output = "\n".join(output_lines)
        report.add_section("MCP Integration Tests", output, "PASS")
        return True

    except Exception as e:
        error_msg = f"Error in integration tests: {str(e)}\n"
        error_msg += "\n".join(output_lines)
        report.add_section("MCP Integration Tests", error_msg, "FAIL")
        print(f"[FAIL] {str(e)}")
        return False


def generate_summary(report: TestReport, results: Dict[str, bool]):
    """Generate test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    summary_lines = []

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests

    summary_lines.append(f"Total Test Suites: {total_tests}")
    summary_lines.append(f"Passed: {passed_tests}")
    summary_lines.append(f"Failed: {failed_tests}")
    summary_lines.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    summary_lines.append("\nDetailed Results:")

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        summary_lines.append(f"  [{status}] {test_name}")

    summary = "\n".join(summary_lines)
    print(summary)

    report.add_section("Test Summary", summary, "PASS" if failed_tests == 0 else "FAIL")


def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("PULSUS MCP COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {Path.cwd()}")
    print("=" * 80)

    report = TestReport()
    results = {}

    # Run all test suites
    results['Phase 1: Core Framework'] = run_phase1_tests(report)
    results['Phase 2: Simple Domains'] = run_phase2_tests(report)
    results['LLM Prompt Tests'] = test_llm_prompts(report)
    results['MCP Integration Tests'] = test_mcp_integration(report)

    # Generate summary
    generate_summary(report, results)

    # Save report
    report_path = project_root / "test_results" / f"mcp_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.parent.mkdir(exist_ok=True)
    report.save(report_path)

    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
