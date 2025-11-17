"""
Simple test runner for MCP core framework tests.
Runs tests without pytest dependencies.
"""

import sys
from pathlib import Path

# Add Pulsus root directory to path for imports
pulsus_root = Path(__file__).parent.parent  # Go up from tests to Pulsus root
if str(pulsus_root) not in sys.path:
    sys.path.insert(0, str(pulsus_root))

# Now run the tests manually
from mcp.core import (
    MCPBase,
    MCPResponse,
    MCPStatus,
    read_only,
    write_safe,
    restricted_write,
    transactional,
    cached,
    SafetyPolicy,
    ExecutionMode,
    SafetyLevel,
    get_safety_policy,
    MCPLogger,
    get_mcp_logger
)

import tempfile
import shutil

# Test counter
tests_run = 0
tests_passed = 0
tests_failed = 0


def test(name):
    """Decorator to mark test functions"""
    def decorator(func):
        def wrapper():
            global tests_run, tests_passed, tests_failed
            tests_run += 1
            try:
                func()
                tests_passed += 1
                print(f"[PASS] {name}")
                return True
            except AssertionError as e:
                tests_failed += 1
                print(f"[FAIL] {name}: {e}")
                return False
            except Exception as e:
                tests_failed += 1
                print(f"[ERROR] {name}: Unexpected error: {e}")
                return False
        return wrapper
    return decorator


# ========== MCPResponse Tests ==========

@test("MCPResponse: success_response creation")
def test_success_response():
    response = MCPResponse.success_response(
        data={'result': 'test'},
        context={'caller': 'Pulse'}
    )
    assert response.success is True
    assert response.data == {'result': 'test'}
    assert response.context == {'caller': 'Pulse'}
    assert response.status == MCPStatus.SUCCESS
    assert 'timestamp' in response.metadata


@test("MCPResponse: error_response creation")
def test_error_response():
    response = MCPResponse.error_response(
        error='Test error',
        context={'operation': 'test'}
    )
    assert response.success is False
    assert response.error == 'Test error'
    assert response.status == MCPStatus.ERROR


@test("MCPResponse: add_trace")
def test_add_trace():
    response = MCPResponse.success_response()
    response.add_trace('Step 1')
    response.add_trace('Step 2')
    assert len(response.trace) == 2
    assert 'Step 1' in response.trace


@test("MCPResponse: set_error")
def test_set_error():
    response = MCPResponse.success_response()
    response.set_error('Something went wrong')
    assert response.success is False
    assert response.error == 'Something went wrong'


@test("MCPResponse: to_dict")
def test_to_dict():
    response = MCPResponse.success_response(data={'test': 'value'})
    result_dict = response.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict['success'] is True
    assert result_dict['data'] == {'test': 'value'}


# ========== MCPBase Tests ==========

class TestHelper(MCPBase):
    """Test helper class"""

    @read_only
    def get_data(self, item_id: str) -> MCPResponse:
        """Get data by ID"""
        return MCPResponse.success_response(
            data={'id': item_id, 'name': 'Test Item'}
        )

    @write_safe
    def update_data(self, item_id: str, value: str) -> MCPResponse:
        """Update data"""
        return MCPResponse.success_response(
            data={'id': item_id, 'value': value, 'updated': True}
        )


@test("MCPBase: initialization")
def test_helper_init():
    helper = TestHelper()
    assert isinstance(helper, MCPBase)
    assert helper.context == {}


@test("MCPBase: initialization with context")
def test_helper_with_context():
    context = {'caller': 'Shell', 'mode': 'execute'}
    helper = TestHelper(context=context)
    assert helper.context == context


@test("MCPBase: get_capabilities")
def test_get_capabilities():
    helper = TestHelper()
    capabilities = helper.get_capabilities()
    assert len(capabilities) >= 2
    cap_names = [cap['name'] for cap in capabilities]
    assert 'get_data' in cap_names
    assert 'update_data' in cap_names


@test("MCPBase: execute operation")
def test_execute_operation():
    helper = TestHelper()
    result = helper.execute('get_data', item_id='123')
    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.data['id'] == '123'


@test("MCPBase: execute invalid operation")
def test_execute_invalid():
    helper = TestHelper()
    result = helper.execute('invalid_operation')
    assert isinstance(result, MCPResponse)
    assert result.success is False
    assert 'not found' in result.error.lower()


# ========== Decorator Tests ==========

@test("Decorator: @read_only")
def test_read_only_decorator():
    helper = TestHelper()
    result = helper.get_data('test-id')
    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.context.get('safety_level') == 'read_only'


@test("Decorator: @write_safe")
def test_write_safe_decorator():
    helper = TestHelper()
    result = helper.update_data('test-id', 'new-value')
    assert isinstance(result, MCPResponse)
    assert result.success is True
    assert result.context.get('safety_level') == 'write_safe'


@test("Decorator: @cached")
def test_cached_decorator():
    class CachedHelper(MCPBase):
        def __init__(self):
            super().__init__()
            self.call_count = 0

        @read_only
        @cached(ttl=10)
        def expensive_operation(self, param: str) -> MCPResponse:
            self.call_count += 1
            return MCPResponse.success_response(
                data={'param': param, 'count': self.call_count}
            )

    helper = CachedHelper()

    # First call - not cached
    result1 = helper.expensive_operation('test')
    assert result1.success is True
    assert result1.data['count'] == 1
    assert result1.context.get('cached') is False

    # Second call - should be cached
    result2 = helper.expensive_operation('test')
    assert result2.success is True
    assert result2.data['count'] == 1  # Same count
    assert result2.context.get('cached') is True


# ========== SafetyPolicy Tests ==========

@test("SafetyPolicy: initialization")
def test_policy_init():
    policy = SafetyPolicy()
    assert policy.current_mode == ExecutionMode.EXECUTE


@test("SafetyPolicy: set_mode")
def test_set_mode():
    policy = SafetyPolicy()
    policy.set_mode(ExecutionMode.PLAN)
    assert policy.current_mode == ExecutionMode.PLAN


@test("SafetyPolicy: register_operation")
def test_register_operation():
    policy = SafetyPolicy()
    policy.register_operation('test_op', SafetyLevel.READ_ONLY)
    op_policy = policy.get_policy('test_op')
    assert op_policy is not None
    assert op_policy.safety_level == SafetyLevel.READ_ONLY


@test("SafetyPolicy: validate operation allowed")
def test_validate_allowed():
    policy = SafetyPolicy()
    policy.register_operation('read_op', SafetyLevel.READ_ONLY)
    is_allowed, reason = policy.validate_operation('read_op', mode=ExecutionMode.PLAN)
    assert is_allowed is True
    assert reason is None


@test("SafetyPolicy: validate operation not allowed")
def test_validate_not_allowed():
    policy = SafetyPolicy()
    policy.register_operation('write_op', SafetyLevel.WRITE_SAFE)
    is_allowed, reason = policy.validate_operation('write_op', mode=ExecutionMode.PLAN)
    assert is_allowed is False
    assert 'not allowed' in reason.lower()


@test("SafetyPolicy: check_type_safety")
def test_check_type_safety():
    policy = SafetyPolicy()
    is_safe, error = policy.check_type_safety("test_string", platform='python')
    assert is_safe is True


@test("SafetyPolicy: requires_confirmation")
def test_requires_confirmation():
    policy = SafetyPolicy()
    policy.register_operation('safe_write', SafetyLevel.WRITE_SAFE)
    assert policy.requires_confirmation('safe_write') is True


# ========== MCPLogger Tests ==========

@test("MCPLogger: initialization")
def test_logger_init():
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = MCPLogger(log_dir=tmp_dir)
        assert Path(tmp_dir).exists()


@test("MCPLogger: log_call")
def test_log_call():
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = MCPLogger(log_dir=tmp_dir)
        call_id = logger.log_call(
            caller='Pulse',
            mcp_class='TestHelper',
            operation='test_op',
            params={'param1': 'value1'},
            result={'success': True},
            success=True
        )
        assert call_id is not None
        assert len(logger.call_history) == 1
        assert logger.call_history[0]['caller'] == 'Pulse'


@test("MCPLogger: get_history")
def test_get_history():
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = MCPLogger(log_dir=tmp_dir)
        logger.log_call('Pulse', 'Helper1', 'op1', {}, {}, True)
        logger.log_call('Shell', 'Helper2', 'op2', {}, {}, True)
        logger.log_call('Pulse', 'Helper1', 'op3', {}, {}, False)

        history = logger.get_history()
        assert len(history) == 3

        pulse_history = logger.get_history(caller='Pulse')
        assert len(pulse_history) == 2


@test("MCPLogger: get_summary")
def test_get_summary():
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = MCPLogger(log_dir=tmp_dir)
        logger.log_call('Pulse', 'Helper1', 'op1', {}, {}, True)
        logger.log_call('Pulse', 'Helper1', 'op2', {}, {}, True)
        logger.log_call('Shell', 'Helper2', 'op1', {}, {}, False)

        summary = logger.get_summary()
        assert summary['total_calls'] == 3
        assert summary['successful'] == 2
        assert summary['failed'] == 1


# ========== Run All Tests ==========

def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*60)
    print("MCP Core Framework Test Suite")
    print("="*60 + "\n")

    # Get all test functions
    test_functions = [
        obj for name, obj in globals().items()
        if callable(obj) and hasattr(obj, '__name__') and obj.__name__ == 'wrapper'
    ]

    # Run tests
    for test_func in test_functions:
        test_func()

    # Summary
    print("\n" + "="*60)
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    if tests_run > 0:
        print(f"Success rate: {(tests_passed/tests_run*100):.1f}%")
    print("="*60 + "\n")

    return tests_failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
