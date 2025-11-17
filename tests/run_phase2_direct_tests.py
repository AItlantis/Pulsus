"""
Phase 2 Direct Test Runner (No pytest dependency)
================================================

Runs Phase 2 simple domain tests directly without pytest to avoid pytest-qt issues.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

def run_test(test_name, test_func):
    """Run a single test and return pass/fail"""
    try:
        test_func()
        print(f"[PASS] {test_name}")
        return True
    except AssertionError as e:
        print(f"[FAIL] {test_name}: {str(e)}")
        return False
    except Exception as e:
        print(f"[ERROR] {test_name}: {str(e)}")
        return False


def test_script_ops_import():
    """Test that ScriptOps can be imported"""
    from mcp.simple import ScriptOps
    from mcp.core import MCPBase
    assert issubclass(ScriptOps, MCPBase)


def test_script_ops_initialization():
    """Test ScriptOps initialization"""
    from mcp.simple import ScriptOps
    ops = ScriptOps()
    assert ops is not None


def test_script_ops_capabilities():
    """Test ScriptOps capabilities"""
    from mcp.simple import ScriptOps
    ops = ScriptOps()
    caps = ops.get_capabilities()
    assert len(caps) > 0
    assert any(c['name'] == 'read_script' for c in caps)
    assert any(c['name'] == 'write_md' for c in caps)


def test_read_script():
    """Test read_script operation"""
    from mcp.simple import ScriptOps
    from mcp.core import MCPStatus

    ops = ScriptOps()

    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''"""Test module"""
def hello():
    """Say hello"""
    return "hello"
''')
        temp_path = f.name

    try:
        result = ops.read_script(temp_path)
        assert result.success is True
        assert result.status == MCPStatus.SUCCESS
        assert result.data is not None
        assert 'ast_analysis' in result.data
        assert len(result.trace) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_read_script_error():
    """Test read_script with non-existent file"""
    from mcp.simple import ScriptOps
    from mcp.core import MCPStatus

    ops = ScriptOps()
    result = ops.read_script('/nonexistent/file.py')
    assert result.success is False
    assert result.status == MCPStatus.ERROR
    assert result.error is not None


def test_write_md():
    """Test write_md operation"""
    from mcp.simple import ScriptOps

    ops = ScriptOps()

    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('def test(): pass\n')
        temp_path = f.name

    try:
        result = ops.write_md(temp_path, content="# Test Doc")
        assert result.success is True
        assert 'doc_path' in result.data

        # Check file was created
        doc_path = Path(result.data['doc_path'])
        assert doc_path.exists()

        # Cleanup
        doc_path.unlink(missing_ok=True)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_scan_structure():
    """Test scan_structure operation"""
    from mcp.simple import ScriptOps

    ops = ScriptOps()

    # Scan the mcp/core directory
    core_dir = Path(__file__).parent / 'mcp' / 'core'

    if core_dir.exists():
        result = ops.scan_structure(str(core_dir))
        assert result.success is True
        assert 'structure' in result.data
        assert 'statistics' in result.data


def test_safety_levels():
    """Test safety level metadata"""
    from mcp.simple import ScriptOps

    ops = ScriptOps()
    caps = ops.get_capabilities()

    # Create safety level map
    safety_map = {c['name']: c['safety_level'] for c in caps}

    # Check read operations
    assert safety_map.get('read_script') == 'read_only'

    # Check write operations
    assert safety_map.get('write_md') == 'write_safe'


def test_execute_method():
    """Test generic execute() method"""
    from mcp.simple import ScriptOps

    ops = ScriptOps()

    # Test with a read operation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('def test(): pass\n')
        temp_path = f.name

    try:
        result = ops.execute('read_script', path=temp_path)
        assert result.success is True
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_mcp_response_structure():
    """Test MCPResponse structure"""
    from mcp.simple import ScriptOps

    ops = ScriptOps()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('def test(): pass\n')
        temp_path = f.name

    try:
        result = ops.read_script(temp_path)

        # Check all required fields
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'error')
        assert hasattr(result, 'context')
        assert hasattr(result, 'trace')
        assert hasattr(result, 'status')
        assert hasattr(result, 'metadata')

        # Check context has MCP info
        assert 'mcp_class' in result.context
        assert result.context['mcp_class'] == 'ScriptOps'

    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_context_propagation():
    """Test context propagation"""
    from mcp.simple import ScriptOps

    custom_context = {
        'caller': 'DirectTest',
        'session': 'test123'
    }

    ops = ScriptOps(context=custom_context)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('def test(): pass\n')
        temp_path = f.name

    try:
        result = ops.read_script(temp_path)
        assert result.context.get('caller') == 'DirectTest'
        assert result.context.get('session') == 'test123'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def main():
    """Run all tests"""
    print("=" * 80)
    print("Phase 2: Simple Domains - Direct Test Runner")
    print("=" * 80)
    print()

    tests = [
        ("ScriptOps: import", test_script_ops_import),
        ("ScriptOps: initialization", test_script_ops_initialization),
        ("ScriptOps: capabilities", test_script_ops_capabilities),
        ("ScriptOps: read_script (success)", test_read_script),
        ("ScriptOps: read_script (error)", test_read_script_error),
        ("ScriptOps: write_md", test_write_md),
        ("ScriptOps: scan_structure", test_scan_structure),
        ("ScriptOps: safety levels", test_safety_levels),
        ("ScriptOps: execute method", test_execute_method),
        ("MCPResponse: structure", test_mcp_response_structure),
        ("Context: propagation", test_context_propagation),
    ]

    results = []
    for test_name, test_func in tests:
        passed = run_test(test_name, test_func)
        results.append((test_name, passed))

    # Summary
    print()
    print("=" * 80)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    print(f"Tests run: {total}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
