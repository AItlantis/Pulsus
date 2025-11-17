"""
Phase 3 Test Suite

Comprehensive tests for Phase 3 components:
- Advanced MCP domains (GitOps, WorkflowOps)
- Composition tools (chain, parallel, conditional)
- Monitoring (metrics, alerts)
- LangChain integration
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Test GitOps
def test_gitops_import():
    """Test that GitOps can be imported"""
    from mcp.advanced.git_ops import GitOps
    assert GitOps is not None


def test_gitops_initialization():
    """Test GitOps initialization"""
    from mcp.advanced.git_ops import GitOps
    git_ops = GitOps()
    assert git_ops is not None
    assert git_ops.__class__.__name__ == 'GitOps'


def test_gitops_capabilities():
    """Test GitOps capabilities"""
    from mcp.advanced.git_ops import GitOps
    git_ops = GitOps()
    capabilities = git_ops.get_capabilities()

    assert len(capabilities) > 0
    operation_names = [cap['name'] for cap in capabilities]
    assert 'get_status' in operation_names
    assert 'get_diff' in operation_names
    assert 'commit' in operation_names


# Test WorkflowOps
def test_workflow_ops_import():
    """Test that WorkflowOps can be imported"""
    from mcp.advanced.workflow_ops import WorkflowOps
    assert WorkflowOps is not None


def test_workflow_ops_initialization():
    """Test WorkflowOps initialization"""
    from mcp.advanced.workflow_ops import WorkflowOps
    workflow_ops = WorkflowOps()
    assert workflow_ops is not None


def test_workflow_validate():
    """Test workflow validation"""
    from mcp.advanced.workflow_ops import WorkflowOps

    workflow_ops = WorkflowOps()

    # Valid workflow
    valid_workflow = {
        'name': 'test_workflow',
        'steps': [
            {
                'name': 'step1',
                'domain': 'ScriptOps',
                'operation': 'read_script',
                'params': {'path': 'test.py'}
            }
        ]
    }

    result = workflow_ops.validate_workflow(valid_workflow)
    assert result.success
    assert result.data['valid'] is True
    assert result.data['error_count'] == 0


def test_workflow_validate_invalid():
    """Test workflow validation with invalid workflow"""
    from mcp.advanced.workflow_ops import WorkflowOps

    workflow_ops = WorkflowOps()

    # Invalid workflow (missing 'steps')
    invalid_workflow = {
        'name': 'test_workflow'
    }

    result = workflow_ops.validate_workflow(invalid_workflow)
    assert result.success
    assert result.data['valid'] is False
    assert result.data['error_count'] > 0


# Test OperationChain
def test_operation_chain_import():
    """Test that OperationChain can be imported"""
    from mcp.composition.chain import OperationChain
    assert OperationChain is not None


def test_operation_chain_initialization():
    """Test OperationChain initialization"""
    from mcp.composition.chain import OperationChain

    chain = OperationChain("test_chain")
    assert chain.name == "test_chain"
    assert len(chain.operations) == 0


def test_operation_chain_add():
    """Test adding operations to chain"""
    from mcp.composition.chain import OperationChain
    from mcp.simple.script_ops import ScriptOps

    chain = OperationChain("test_chain")
    script_ops = ScriptOps()

    chain.add(script_ops, 'get_capabilities')
    assert len(chain.operations) == 1


# Test ParallelOperations
def test_parallel_operations_import():
    """Test that ParallelOperations can be imported"""
    from mcp.composition.parallel import ParallelOperations
    assert ParallelOperations is not None


def test_parallel_operations_initialization():
    """Test ParallelOperations initialization"""
    from mcp.composition.parallel import ParallelOperations

    parallel = ParallelOperations(max_workers=4, name="test_parallel")
    assert parallel.name == "test_parallel"
    assert parallel.max_workers == 4
    assert len(parallel.operations) == 0


def test_parallel_operations_add():
    """Test adding operations to parallel"""
    from mcp.composition.parallel import ParallelOperations
    from mcp.simple.script_ops import ScriptOps

    parallel = ParallelOperations()
    script_ops = ScriptOps()

    parallel.add(script_ops, 'get_capabilities')
    assert len(parallel.operations) == 1


# Test ConditionalFlow
def test_conditional_flow_import():
    """Test that ConditionalFlow can be imported"""
    from mcp.composition.conditional import ConditionalFlow
    assert ConditionalFlow is not None


def test_conditional_flow_initialization():
    """Test ConditionalFlow initialization"""
    from mcp.composition.conditional import ConditionalFlow

    flow = ConditionalFlow()
    assert flow is not None


def test_conditional_flow_if_then():
    """Test if_then conditional"""
    from mcp.composition.conditional import ConditionalFlow
    from mcp.simple.script_ops import ScriptOps

    flow = ConditionalFlow()
    script_ops = ScriptOps()

    # Test with True condition
    result = flow.if_then(
        condition_fn=lambda: True,
        then_domain=script_ops,
        then_operation='get_capabilities'
    )
    assert result.success


# Test MCPMetrics
def test_metrics_import():
    """Test that MCPMetrics can be imported"""
    from mcp.monitoring.metrics import MCPMetrics
    assert MCPMetrics is not None


def test_metrics_initialization():
    """Test MCPMetrics initialization"""
    from mcp.monitoring.metrics import MCPMetrics

    metrics = MCPMetrics()
    assert metrics is not None
    assert len(metrics.metrics) == 0


def test_metrics_track_operation():
    """Test tracking operations"""
    from mcp.monitoring.metrics import MCPMetrics

    metrics = MCPMetrics()

    metrics.track_operation(
        domain='ScriptOps',
        operation='read_script',
        duration_ms=45.2,
        success=True
    )

    assert len(metrics.metrics) == 1
    assert metrics.metrics[0].domain == 'ScriptOps'
    assert metrics.metrics[0].success is True


def test_metrics_get_statistics():
    """Test getting statistics"""
    from mcp.monitoring.metrics import MCPMetrics

    metrics = MCPMetrics()

    # Add some metrics
    for i in range(10):
        metrics.track_operation(
            domain='ScriptOps',
            operation='read_script',
            duration_ms=50.0 + i,
            success=True
        )

    stats = metrics.get_statistics(domain='ScriptOps')
    assert stats['count'] == 10
    assert stats['success_count'] == 10
    assert 'duration_ms' in stats


# Test AlertManager
def test_alert_manager_import():
    """Test that AlertManager can be imported"""
    from mcp.monitoring.alerts import AlertManager
    assert AlertManager is not None


def test_alert_manager_initialization():
    """Test AlertManager initialization"""
    from mcp.monitoring.alerts import AlertManager

    alerts = AlertManager()
    assert alerts is not None
    assert len(alerts.conditions) == 0


def test_alert_manager_register():
    """Test registering alerts"""
    from mcp.monitoring.alerts import AlertManager, AlertSeverity

    alerts = AlertManager()

    alerts.register_alert(
        name='test_alert',
        condition=lambda: True,
        severity=AlertSeverity.INFO,
        message=lambda: "Test alert message"
    )

    assert 'test_alert' in alerts.conditions


def test_alert_manager_check():
    """Test checking alerts"""
    from mcp.monitoring.alerts import AlertManager, AlertSeverity

    alerts = AlertManager()

    # Register alert that always fires
    alerts.register_alert(
        name='test_alert',
        condition=lambda: True,
        severity=AlertSeverity.INFO,
        message=lambda: "Test alert"
    )

    triggered = alerts.check_all()
    assert len(triggered) == 1
    assert triggered[0].name == 'test_alert'


# Test LangChain integration
def test_langchain_adapter_import():
    """Test that LangChain adapter can be imported"""
    from langchain.tool_adapter import mcp_to_langchain_tool
    assert mcp_to_langchain_tool is not None


def test_langchain_registry_import():
    """Test that MCPToolRegistry can be imported"""
    from langchain.tool_adapter import MCPToolRegistry
    assert MCPToolRegistry is not None


def test_langchain_registry_initialization():
    """Test MCPToolRegistry initialization"""
    from langchain.tool_adapter import MCPToolRegistry

    registry = MCPToolRegistry()
    assert registry is not None
    assert len(registry.domains) == 0


def test_langchain_registry_register():
    """Test registering domains"""
    from langchain.tool_adapter import MCPToolRegistry
    from mcp.simple.script_ops import ScriptOps

    registry = MCPToolRegistry()
    registry.register_domain(ScriptOps)

    assert 'ScriptOps' in registry.domains


# Test LangGraph integration
def test_langgraph_state_import():
    """Test that PulsusState can be imported"""
    from langchain.graph_executor import PulsusState
    assert PulsusState is not None


def test_langgraph_create_graph():
    """Test creating Pulsus graph"""
    from langchain.graph_executor import create_pulsus_graph

    graph = create_pulsus_graph()
    assert graph is not None


# Integration tests
def test_full_workflow_chain():
    """Test complete workflow chain"""
    from mcp.composition.chain import OperationChain
    from mcp.simple.script_ops import ScriptOps

    script_ops = ScriptOps()
    chain = OperationChain("integration_test")

    # Add operations
    chain.add(script_ops, 'get_capabilities')

    # Execute
    result = chain.execute()
    assert result is not None


def test_full_parallel_execution():
    """Test complete parallel execution"""
    from mcp.composition.parallel import ParallelOperations
    from mcp.simple.script_ops import ScriptOps

    script_ops = ScriptOps()
    parallel = ParallelOperations(max_workers=2)

    # Add operations
    parallel.add(script_ops, 'get_capabilities')
    parallel.add(script_ops, 'get_capabilities')

    # Execute
    result = parallel.execute()
    assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
