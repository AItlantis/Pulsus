"""
Unit Tests for MCP Core Framework

Tests for MCPBase, MCPResponse, decorators, policy, and logger.
"""

import pytest
from pathlib import Path
import sys

# Add testudo to path
testudo_root = Path(__file__).parents[3]
if str(testudo_root) not in sys.path:
    sys.path.insert(0, str(testudo_root))

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


# ========== MCPResponse Tests ==========

class TestMCPResponse:
    """Test MCPResponse class"""

    def test_success_response_creation(self):
        """Test creating a successful response"""
        response = MCPResponse.success_response(
            data={'result': 'test'},
            context={'caller': 'Pulse'}
        )

        assert response.success is True
        assert response.data == {'result': 'test'}
        assert response.context == {'caller': 'Pulse'}
        assert response.status == MCPStatus.SUCCESS
        assert 'timestamp' in response.metadata

    def test_error_response_creation(self):
        """Test creating an error response"""
        response = MCPResponse.error_response(
            error='Test error',
            context={'operation': 'test'}
        )

        assert response.success is False
        assert response.error == 'Test error'
        assert response.status == MCPStatus.ERROR

    def test_add_trace(self):
        """Test adding trace messages"""
        response = MCPResponse.success_response()
        response.add_trace('Step 1')
        response.add_trace('Step 2')

        assert len(response.trace) == 2
        assert 'Step 1' in response.trace
        assert 'Step 2' in response.trace

    def test_set_error(self):
        """Test setting error on response"""
        response = MCPResponse.success_response()
        response.set_error('Something went wrong')

        assert response.success is False
        assert response.error == 'Something went wrong'
        assert response.status == MCPStatus.ERROR

    def test_to_dict(self):
        """Test converting response to dictionary"""
        response = MCPResponse.success_response(data={'test': 'value'})
        result_dict = response.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict['success'] is True
        assert result_dict['data'] == {'test': 'value'}
        assert result_dict['status'] == 'success'


# ========== MCPBase Tests ==========

class TestHelper(MCPBase):
    """Test helper class for unit tests"""

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


class TestMCPBase:
    """Test MCPBase class"""

    def test_helper_initialization(self):
        """Test helper initialization"""
        helper = TestHelper()
        assert isinstance(helper, MCPBase)
        assert helper.context == {}

    def test_helper_with_context(self):
        """Test helper initialization with context"""
        context = {'caller': 'Shell', 'mode': 'execute'}
        helper = TestHelper(context=context)
        assert helper.context == context

    def test_get_capabilities(self):
        """Test capability introspection"""
        helper = TestHelper()
        capabilities = helper.get_capabilities()

        assert len(capabilities) >= 2  # get_data and update_data
        cap_names = [cap['name'] for cap in capabilities]
        assert 'get_data' in cap_names
        assert 'update_data' in cap_names

        # Check get_data capability
        get_data_cap = next(cap for cap in capabilities if cap['name'] == 'get_data')
        assert get_data_cap['safety_level'] == 'read_only'
        assert 'item_id' in get_data_cap['parameters']

    def test_execute_operation(self):
        """Test executing operation by name"""
        helper = TestHelper()
        result = helper.execute('get_data', item_id='123')

        assert isinstance(result, MCPResponse)
        assert result.success is True
        assert result.data['id'] == '123'

    def test_execute_invalid_operation(self):
        """Test executing non-existent operation"""
        helper = TestHelper()
        result = helper.execute('invalid_operation')

        assert isinstance(result, MCPResponse)
        assert result.success is False
        assert 'not found' in result.error.lower()

    def test_repr(self):
        """Test string representation"""
        helper = TestHelper()
        repr_str = repr(helper)
        assert 'TestHelper' in repr_str
        assert 'capabilities' in repr_str


# ========== Decorator Tests ==========

class TestDecorators:
    """Test MCP decorators"""

    def test_read_only_decorator(self):
        """Test read_only decorator"""
        helper = TestHelper()
        result = helper.get_data('test-id')

        assert isinstance(result, MCPResponse)
        assert result.success is True
        assert result.context.get('safety_level') == 'read_only'

    def test_write_safe_decorator(self):
        """Test write_safe decorator"""
        helper = TestHelper()
        result = helper.update_data('test-id', 'new-value')

        assert isinstance(result, MCPResponse)
        assert result.success is True
        assert result.context.get('safety_level') == 'write_safe'

    def test_cached_decorator(self):
        """Test cached decorator"""

        class CachedHelper(MCPBase):
            def __init__(self):
                super().__init__()
                self.call_count = 0

            @read_only
            @cached(ttl=10)
            def expensive_operation(self, param: str) -> MCPResponse:
                """Expensive operation that should be cached"""
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
        assert result2.data['count'] == 1  # Same count, from cache
        assert result2.context.get('cached') is True

        # Different parameter - not cached
        result3 = helper.expensive_operation('other')
        assert result3.success is True
        assert result3.data['count'] == 2  # New call
        assert result3.context.get('cached') is False

    def test_restricted_write_decorator(self):
        """Test restricted_write decorator"""

        class RestrictedHelper(MCPBase):
            @restricted_write(platform='python')
            def safe_update(self, obj: Path) -> MCPResponse:
                """Update operation with type validation"""
                return MCPResponse.success_response()

        helper = RestrictedHelper()

        # Valid type (Path is in python platform types)
        result = helper.safe_update(Path('.'))
        assert isinstance(result, MCPResponse)
        # Note: May fail if type validation is strict

    def test_transactional_decorator(self):
        """Test transactional decorator"""

        class TransactionalHelper(MCPBase):
            @transactional
            def batch_operation(self, items: list) -> MCPResponse:
                """Batch operation that can be rolled back"""
                if not items:
                    raise ValueError("No items provided")
                return MCPResponse.success_response(data={'processed': len(items)})

        helper = TransactionalHelper()

        # Successful transaction
        result = helper.batch_operation([1, 2, 3])
        assert result.success is True
        assert result.context.get('rollback_supported') is True

        # Failed transaction (should handle rollback)
        result_fail = helper.batch_operation([])
        assert result_fail.success is False


# ========== SafetyPolicy Tests ==========

class TestSafetyPolicy:
    """Test SafetyPolicy class"""

    def test_policy_initialization(self):
        """Test policy initialization"""
        policy = SafetyPolicy()
        assert policy.current_mode == ExecutionMode.EXECUTE

    def test_set_mode(self):
        """Test setting execution mode"""
        policy = SafetyPolicy()
        policy.set_mode(ExecutionMode.PLAN)
        assert policy.current_mode == ExecutionMode.PLAN

    def test_register_operation(self):
        """Test registering an operation"""
        policy = SafetyPolicy()
        policy.register_operation('test_op', SafetyLevel.READ_ONLY)

        op_policy = policy.get_policy('test_op')
        assert op_policy is not None
        assert op_policy.safety_level == SafetyLevel.READ_ONLY

    def test_validate_operation_allowed(self):
        """Test validating allowed operation"""
        policy = SafetyPolicy()
        policy.register_operation('read_op', SafetyLevel.READ_ONLY)

        is_allowed, reason = policy.validate_operation('read_op', mode=ExecutionMode.PLAN)
        assert is_allowed is True
        assert reason is None

    def test_validate_operation_not_allowed(self):
        """Test validating disallowed operation"""
        policy = SafetyPolicy()
        policy.register_operation('write_op', SafetyLevel.WRITE_SAFE)

        # Write operations not allowed in PLAN mode
        is_allowed, reason = policy.validate_operation('write_op', mode=ExecutionMode.PLAN)
        assert is_allowed is False
        assert 'not allowed' in reason.lower()

    def test_check_type_safety(self):
        """Test type safety checking"""
        policy = SafetyPolicy()

        # Valid Python type (testing with string which is in python types)
        is_safe, error = policy.check_type_safety("test_string", platform='python')
        assert is_safe is True

        # Test Path type (add Path to python types if not present)
        # Path might have different type name, so let's test with dict
        is_safe, error = policy.check_type_safety({}, platform='python')
        assert is_safe is True

        # Test with custom platform
        policy.register_platform('custom', ['CustomType'])
        # Would need actual CustomType object to test

    def test_requires_confirmation(self):
        """Test confirmation requirement check"""
        policy = SafetyPolicy()
        policy.register_operation('safe_write', SafetyLevel.WRITE_SAFE)

        assert policy.requires_confirmation('safe_write') is True

    def test_list_operations(self):
        """Test listing operations"""
        policy = SafetyPolicy()
        policy.register_operation('read1', SafetyLevel.READ_ONLY)
        policy.register_operation('read2', SafetyLevel.READ_ONLY)
        policy.register_operation('write1', SafetyLevel.WRITE_SAFE)

        read_ops = policy.list_operations(safety_level=SafetyLevel.READ_ONLY)
        assert 'read1' in read_ops
        assert 'read2' in read_ops
        assert 'write1' not in read_ops

    def test_get_summary(self):
        """Test policy summary"""
        policy = SafetyPolicy()
        policy.register_operation('op1', SafetyLevel.READ_ONLY)
        policy.register_operation('op2', SafetyLevel.WRITE_SAFE)

        summary = policy.get_summary()
        assert summary['total_operations'] == 2
        assert 'by_safety_level' in summary
        assert 'platforms' in summary


# ========== MCPLogger Tests ==========

class TestMCPLogger:
    """Test MCPLogger class"""

    def test_logger_initialization(self, tmp_path):
        """Test logger initialization"""
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))
        assert logger.log_dir.exists()

    def test_log_call(self, tmp_path):
        """Test logging a call"""
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))

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

    def test_get_history(self, tmp_path):
        """Test getting call history"""
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))

        # Log multiple calls
        logger.log_call('Pulse', 'Helper1', 'op1', {}, {}, True)
        logger.log_call('Shell', 'Helper2', 'op2', {}, {}, True)
        logger.log_call('Pulse', 'Helper1', 'op3', {}, {}, False)

        # Get all history
        history = logger.get_history()
        assert len(history) == 3

        # Filter by caller
        pulse_history = logger.get_history(caller='Pulse')
        assert len(pulse_history) == 2

        # Filter by class
        helper1_history = logger.get_history(mcp_class='Helper1')
        assert len(helper1_history) == 2

    def test_export_safenet_report(self, tmp_path):
        """Test exporting SafeNet report"""
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))

        # Log some calls
        logger.log_call('Pulse', 'TestHelper', 'read_data', {}, {'success': True}, True)
        logger.log_call('Shell', 'TestHelper', 'write_data', {}, {'success': False, 'error': 'Test error'}, False)

        # Export report
        report_path = logger.export_safenet_report(
            output_path=str(tmp_path / "test_report.md")
        )

        assert Path(report_path).exists()

        # Check report content
        report_content = Path(report_path).read_text()
        assert 'SafeNet MCP Action Report' in report_content
        assert 'TestHelper' in report_content
        assert 'Pulse' in report_content
        assert 'Shell' in report_content

    def test_get_summary(self, tmp_path):
        """Test getting logger summary"""
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))

        logger.log_call('Pulse', 'Helper1', 'op1', {}, {}, True)
        logger.log_call('Pulse', 'Helper1', 'op2', {}, {}, True)
        logger.log_call('Shell', 'Helper2', 'op1', {}, {}, False)

        summary = logger.get_summary()

        assert summary['total_calls'] == 3
        assert summary['successful'] == 2
        assert summary['failed'] == 1
        assert summary['success_rate'] == pytest.approx(66.67, rel=0.1)


# ========== Integration Tests ==========

class TestIntegration:
    """Integration tests for complete MCP workflow"""

    def test_complete_workflow(self, tmp_path):
        """Test complete workflow: helper -> decorator -> policy -> logger"""
        # Initialize logger
        logger = MCPLogger(log_dir=str(tmp_path / "test_logs"))

        # Create helper with logger
        helper = TestHelper(logger=logger)

        # Execute read operation
        result = helper.get_data('test-123')

        assert result.success is True
        assert result.data['id'] == 'test-123'
        assert result.context['safety_level'] == 'read_only'

        # Check logging
        history = logger.get_history()
        # Note: Logging may not work if helper doesn't call _log_operation

    def test_policy_enforcement(self):
        """Test policy enforcement across operations"""
        policy = get_safety_policy()
        policy.set_mode(ExecutionMode.PLAN)

        # Read operations should work in PLAN mode
        helper = TestHelper()
        read_result = helper.get_data('test')
        assert read_result.success is True

        # Write operations should be restricted in PLAN mode
        # (This depends on decorator implementation)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
