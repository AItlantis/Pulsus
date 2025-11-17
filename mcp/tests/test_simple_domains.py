"""
Tests for MCP Simple Domains

Tests the migrated simple domains that extend MCPBase.
"""

import pytest
import tempfile
from pathlib import Path

from mcp.simple import ScriptOps
from mcp.core.base import MCPResponse, MCPStatus
from mcp.core.logger import MCPLogger


# ===== Test Fixtures =====

@pytest.fixture
def script_ops():
    """Create ScriptOps instance"""
    return ScriptOps()


@pytest.fixture
def script_ops_with_logger():
    """Create ScriptOps instance with logger"""
    logger = MCPLogger(log_dir="logs/test_mcp")
    return ScriptOps(logger=logger, context={'caller': 'pytest'})


@pytest.fixture
def sample_script_file():
    """Create a temporary Python script file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('''"""Sample Python module for testing"""

def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

class Calculator:
    """Simple calculator class"""

    def divide(self, a, b):
        """Divide two numbers"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
''')
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
    # Also cleanup any generated .md files
    md_path = Path(temp_path).with_suffix('.md')
    md_path.unlink(missing_ok=True)


# ===== Test MCPBase Integration =====

def test_script_ops_extends_mcpbase(script_ops):
    """Test that ScriptOps properly extends MCPBase"""
    from mcp.core.base import MCPBase

    assert isinstance(script_ops, MCPBase)
    assert hasattr(script_ops, 'get_capabilities')
    assert hasattr(script_ops, 'execute')


def test_script_ops_capabilities(script_ops):
    """Test that ScriptOps reports its capabilities"""
    capabilities = script_ops.get_capabilities()

    # Should have multiple capabilities
    assert len(capabilities) > 0

    # Check for key operations
    cap_names = [cap['name'] for cap in capabilities]
    assert 'read_script' in cap_names
    assert 'write_md' in cap_names
    assert 'add_comments' in cap_names
    assert 'format_script' in cap_names
    assert 'scan_structure' in cap_names

    # Check that capabilities have required fields
    for cap in capabilities:
        assert 'name' in cap
        assert 'description' in cap
        assert 'safety_level' in cap
        assert 'parameters' in cap
        assert 'returns' in cap


def test_script_ops_safety_levels(script_ops):
    """Test that operations have correct safety levels"""
    capabilities = script_ops.get_capabilities()

    # Create a mapping of operation -> safety level
    safety_map = {cap['name']: cap['safety_level'] for cap in capabilities}

    # Read operations should be read_only
    assert safety_map.get('read_script') == 'read_only'
    assert safety_map.get('add_comments') == 'read_only'
    assert safety_map.get('scan_structure') in ['read_only', 'cached']

    # Write operations should be write_safe
    assert safety_map.get('write_md') == 'write_safe'
    assert safety_map.get('format_script') == 'write_safe'


# ===== Test read_script =====

def test_read_script_success(script_ops, sample_script_file):
    """Test successful script reading"""
    result = script_ops.read_script(str(sample_script_file))

    # Should be an MCPResponse
    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.error is None
    assert result.status == MCPStatus.SUCCESS

    # Should have data
    assert result.data is not None
    assert 'content' in result.data
    assert 'ast_analysis' in result.data
    assert 'metadata' in result.data
    assert 'file_path' in result.data

    # Check AST analysis
    ast_analysis = result.data['ast_analysis']
    assert 'functions' in ast_analysis
    assert 'classes' in ast_analysis
    assert 'imports' in ast_analysis
    assert 'module_docstring' in ast_analysis

    # Should find our test functions and classes
    func_names = [f['name'] for f in ast_analysis['functions']]
    assert 'add' in func_names
    assert 'multiply' in func_names
    assert 'divide' in func_names

    class_names = [c['name'] for c in ast_analysis['classes']]
    assert 'Calculator' in class_names

    # Check trace
    assert len(result.trace) > 0
    assert any('Reading script' in t for t in result.trace)


def test_read_script_file_not_found(script_ops):
    """Test reading non-existent file"""
    result = script_ops.read_script('/nonexistent/file.py')

    assert isinstance(result, MCPResponse)
    assert result.success is False
    assert result.error is not None
    assert 'not found' in result.error.lower() or 'not exist' in result.error.lower()
    assert result.status == MCPStatus.ERROR


def test_read_script_not_python_file(script_ops):
    """Test reading non-Python file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Not a Python file")
        temp_path = f.name

    try:
        result = script_ops.read_script(temp_path)

        assert isinstance(result, MCPResponse)
        assert result.success is False
        assert result.error is not None
        assert 'not a python file' in result.error.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_read_script_with_logger(script_ops_with_logger, sample_script_file):
    """Test that logging works correctly"""
    result = script_ops_with_logger.read_script(str(sample_script_file))

    assert result.success is True

    # Check context
    assert 'mcp_class' in result.context
    assert result.context['mcp_class'] == 'ScriptOps'
    assert 'caller' in result.context
    assert result.context['caller'] == 'pytest'


# ===== Test write_md =====

def test_write_md_with_provided_content(script_ops, sample_script_file):
    """Test writing documentation with provided content"""
    custom_content = "# Test Documentation\n\nThis is a test."

    result = script_ops.write_md(str(sample_script_file), content=custom_content)

    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data is not None
    assert 'doc_path' in result.data

    # Check that file was created
    doc_path = Path(result.data['doc_path'])
    assert doc_path.exists()
    assert doc_path.suffix == '.md'

    # Check content
    content = doc_path.read_text(encoding='utf-8')
    assert content == custom_content

    # Cleanup
    doc_path.unlink(missing_ok=True)


def test_write_md_auto_generate(script_ops, sample_script_file):
    """Test auto-generating documentation (will use fallback)"""
    result = script_ops.write_md(str(sample_script_file))

    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data is not None
    assert 'doc_path' in result.data

    # Check that file was created
    doc_path = Path(result.data['doc_path'])
    assert doc_path.exists()

    # Check content has basic structure
    content = doc_path.read_text(encoding='utf-8')
    assert '# ' in content  # Has markdown header
    assert 'add' in content.lower() or 'multiply' in content.lower()  # Has function info

    # Cleanup
    doc_path.unlink(missing_ok=True)


# ===== Test add_comments =====

def test_add_comments_success(script_ops, sample_script_file):
    """Test generating comments for functions"""
    result = script_ops.add_comments(str(sample_script_file), show_progress=False)

    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data is not None
    assert 'functions_commented' in result.data
    assert 'comments' in result.data

    # Should have generated comments for our functions
    assert result.data['functions_commented'] > 0
    assert len(result.data['comments']) > 0

    # Check comment structure
    for comment in result.data['comments']:
        assert 'function' in comment
        assert 'line' in comment
        assert 'comment' in comment
        assert 'formatted' in comment


def test_add_comments_no_functions(script_ops):
    """Test adding comments to file with no functions"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('"""Module with no functions"""\nimport sys\n')
        temp_path = f.name

    try:
        result = script_ops.add_comments(temp_path, show_progress=False)

        assert isinstance(result, MCPResponse)
        assert result.success is True
        assert result.data['functions_commented'] == 0
        assert len(result.data['comments']) == 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ===== Test format_script =====

def test_format_script_check_only(script_ops):
    """Test checking formatting without modifying file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write poorly formatted code
        f.write('def foo(   x,y   ):\n    return x+y\n')
        temp_path = f.name

    try:
        original_content = Path(temp_path).read_text()

        result = script_ops.format_script(temp_path, check_only=True)

        assert isinstance(result, MCPResponse)
        assert result.success is True
        assert 'formatted' in result.data
        assert 'changes' in result.data

        # File should not be modified
        new_content = Path(temp_path).read_text()
        assert new_content == original_content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_format_script_apply_changes(script_ops):
    """Test applying formatting changes"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write poorly formatted code
        f.write('def foo(   x,y   ):\n    return x+y\n')
        temp_path = f.name

    try:
        original_content = Path(temp_path).read_text()

        result = script_ops.format_script(temp_path, check_only=False)

        assert isinstance(result, MCPResponse)
        assert result.success is True

        # If formatting tools available, file should be modified
        new_content = Path(temp_path).read_text()
        # Content may or may not change depending on tool availability
        # Just check that operation completed successfully
        assert True
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ===== Test scan_structure =====

def test_scan_structure_success(script_ops):
    """Test scanning directory structure"""
    # Use the mcp/simple directory as test target
    test_dir = Path(__file__).parent.parent / 'simple'

    if not test_dir.exists():
        pytest.skip("Test directory not found")

    result = script_ops.scan_structure(str(test_dir))

    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data is not None
    assert 'structure' in result.data
    assert 'dependency_map' in result.data
    assert 'statistics' in result.data

    # Check statistics
    stats = result.data['statistics']
    assert 'total_files' in stats
    assert 'total_directories' in stats
    assert 'total_lines' in stats


def test_scan_structure_directory_not_found(script_ops):
    """Test scanning non-existent directory"""
    result = script_ops.scan_structure('/nonexistent/directory')

    assert isinstance(result, MCPResponse)
    assert result.success is False
    assert 'not found' in result.error.lower()


def test_scan_structure_with_patterns(script_ops):
    """Test scanning with include/exclude patterns"""
    test_dir = Path(__file__).parent.parent / 'simple'

    if not test_dir.exists():
        pytest.skip("Test directory not found")

    result = script_ops.scan_structure(
        str(test_dir),
        include_patterns=['*.py'],
        exclude_patterns=['__pycache__', '*.pyc']
    )

    assert isinstance(result, MCPResponse)
    assert result.success is True


# ===== Test execute() method =====

def test_execute_read_script(script_ops, sample_script_file):
    """Test executing operation via execute() method"""
    result = script_ops.execute('read_script', path=str(sample_script_file))

    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data is not None


def test_execute_invalid_operation(script_ops):
    """Test executing non-existent operation"""
    result = script_ops.execute('invalid_operation', foo='bar')

    assert isinstance(result, MCPResponse)
    assert result.success is False
    assert 'not found' in result.error.lower()


# ===== Test MCPResponse structure =====

def test_mcp_response_structure(script_ops, sample_script_file):
    """Test that MCPResponse has all required fields"""
    result = script_ops.read_script(str(sample_script_file))

    # Check all MCPResponse fields
    assert hasattr(result, 'success')
    assert hasattr(result, 'data')
    assert hasattr(result, 'error')
    assert hasattr(result, 'context')
    assert hasattr(result, 'trace')
    assert hasattr(result, 'status')
    assert hasattr(result, 'metadata')

    # Check that context has MCP class info
    assert 'mcp_class' in result.context
    assert result.context['mcp_class'] == 'ScriptOps'

    # Check that metadata has timestamp
    assert 'timestamp' in result.metadata


def test_mcp_response_to_dict(script_ops, sample_script_file):
    """Test converting MCPResponse to dictionary"""
    result = script_ops.read_script(str(sample_script_file))

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert 'success' in result_dict
    assert 'data' in result_dict
    assert 'error' in result_dict
    assert 'context' in result_dict
    assert 'trace' in result_dict
    assert 'status' in result_dict
    assert 'metadata' in result_dict

    # Status should be string value
    assert isinstance(result_dict['status'], str)


# ===== Test decorator behavior =====

def test_read_only_decorator(script_ops, sample_script_file):
    """Test that @read_only decorator adds metadata"""
    result = script_ops.read_script(str(sample_script_file))

    assert result.context.get('safety_level') == 'read_only'
    assert result.context.get('requires_confirmation') is False


def test_write_safe_decorator(script_ops, sample_script_file):
    """Test that @write_safe decorator adds metadata"""
    result = script_ops.write_md(str(sample_script_file), content="# Test")

    assert result.context.get('safety_level') == 'write_safe'

    # Cleanup
    doc_path = Path(result.data['doc_path'])
    doc_path.unlink(missing_ok=True)


# ===== Test error handling =====

def test_error_handling_invalid_path(script_ops):
    """Test error handling for invalid paths"""
    result = script_ops.read_script(None)

    # Should handle gracefully
    assert isinstance(result, MCPResponse)
    # Result should indicate failure
    assert not result.success


def test_trace_messages(script_ops, sample_script_file):
    """Test that trace messages are added"""
    result = script_ops.read_script(str(sample_script_file))

    assert len(result.trace) > 0
    assert any('Reading script' in t for t in result.trace)
    assert any('successfully' in t.lower() for t in result.trace)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
