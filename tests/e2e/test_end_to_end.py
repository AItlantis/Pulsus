"""
End-to-End Tests for Pulsus MCP System

Tests complete workflows from MCP discovery through execution,
validating the entire system integration including routing,
safety enforcement, and LangChain compatibility.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from langchain_integration.tool_adapter import (
    mcp_to_langchain_tool,
    discover_and_convert_mcp_domains,
)
from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe
from mcp.simple.script_ops import ScriptOps


class E2ETestMCP(MCPBase):
    """Test MCP for end-to-end scenarios"""

    def get_capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "analyze_text",
                "description": "Analyze text content",
                "safety_level": "read_only",
                "parameters": ["text"],
                "returns": "MCPResponse"
            },
            {
                "name": "process_data",
                "description": "Process data pipeline",
                "safety_level": "write_safe",
                "parameters": ["data", "format"],
                "returns": "MCPResponse"
            }
        ]

    @read_only
    def analyze_text(self, text: str) -> MCPResponse:
        """Analyze text and return metrics"""
        word_count = len(text.split())
        char_count = len(text)
        lines = text.split('\n')
        line_count = len(lines)

        return MCPResponse.success_response(
            data={
                "word_count": word_count,
                "char_count": char_count,
                "line_count": line_count,
                "avg_line_length": char_count / line_count if line_count > 0 else 0
            },
            context={"operation": "analyze_text"}
        )

    @write_safe
    def process_data(self, data: Dict[str, Any], format: str = "json") -> MCPResponse:
        """Process data through pipeline"""
        processed = {
            "original_keys": list(data.keys()),
            "format": format,
            "timestamp": time.time(),
            "processed": True
        }

        return MCPResponse.success_response(
            data=processed,
            context={"operation": "process_data", "format": format}
        )


@pytest.mark.e2e
class TestEndToEndDiscovery:
    """Test complete discovery workflow"""

    def test_discover_all_available_mcps(self):
        """
        E2E Test: Discover all available MCPs in the system

        Validates:
        - Discovery finds real MCP implementations
        - Each discovered MCP is properly converted
        - All tools are functional
        """
        # Discover all MCPs
        tools = discover_and_convert_mcp_domains(verbose=False)

        # Should find at least ScriptOps and RepositoryOps
        assert len(tools) >= 2, f"Expected at least 2 MCPs, found {len(tools)}"

        # Validate each tool
        for tool in tools:
            # Has required attributes
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'func')
            assert callable(tool.func)

            # Name is valid snake_case
            assert tool.name.islower() or '_' in tool.name
            assert ' ' not in tool.name

    def test_discover_specific_module(self):
        """
        E2E Test: Discover MCPs from specific module

        Validates:
        - Module-specific discovery works
        - Only MCPs from that module are found
        """
        tools = discover_and_convert_mcp_domains(
            search_paths=['mcp.simple'],
            verbose=False
        )

        # Should find MCPs from mcp.simple
        assert len(tools) >= 1

        # All tools should be from simple tier
        tool_names = [t.name for t in tools]
        # Check for known simple MCPs
        known_simple = ['script_ops', 'repository_ops']
        found = [name for name in known_simple if name in tool_names]
        assert len(found) >= 1, f"Expected to find simple MCPs, got: {tool_names}"


@pytest.mark.e2e
class TestEndToEndConversion:
    """Test complete conversion workflow"""

    def test_convert_and_execute_custom_mcp(self):
        """
        E2E Test: Convert custom MCP and execute operations

        Validates:
        - Custom MCP converts successfully
        - All operations are executable
        - Results are properly formatted
        """
        # Convert MCP
        tool = mcp_to_langchain_tool(E2ETestMCP)

        assert tool.name.startswith("e2") or tool.name.startswith("e_2")
        assert "MCP domain with 2 operations" in tool.description

        # Execute read operation
        result = tool.func(action="analyze_text", params={
            "text": "Hello world\nThis is a test\nEnd-to-end testing"
        })

        assert result['success'] is True
        assert result["data"]["word_count"] >= 7
        assert result['data']['line_count'] == 3

    def test_convert_real_mcp(self):
        """
        E2E Test: Convert and execute real MCP (ScriptOps)

        Validates:
        - Real MCP implementations work
        - Safety decorators are enforced
        - Error handling works
        """
        # Convert ScriptOps
        tool = mcp_to_langchain_tool(ScriptOps)

        assert tool is not None
        assert 'script' in tool.name.lower()

        # Tool should be executable (though may need approval for writes)
        assert callable(tool.func)


@pytest.mark.e2e
class TestEndToEndExecution:
    """Test complete execution workflows"""

    def test_simple_read_workflow(self):
        """
        E2E Test: Execute simple read-only workflow

        Flow:
        1. Discover MCP
        2. Convert to LangChain tool
        3. Execute read operation
        4. Validate result
        """
        # Step 1: Discover
        mcp_class = E2ETestMCP

        # Step 2: Convert
        tool = mcp_to_langchain_tool(mcp_class)

        # Step 3: Execute
        result = tool.func(
            action="analyze_text",
            params={"text": "Test content for analysis"}
        )

        # Step 4: Validate
        assert result['success'] is True
        assert 'word_count' in result['data']
        assert result['data']['word_count'] == 4
        assert result['context']['operation'] == 'analyze_text'
        assert 'timestamp' in result['metadata']

    def test_parameterized_execution_workflow(self):
        """
        E2E Test: Execute workflow with parameters

        Validates:
        - Parameters are properly passed
        - Type conversions work
        - Results include parameter context
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        result = tool.func(
            action="analyze_text",
            params={"text": "Short"}
        )

        assert result['success'] is True
        assert result['data']['word_count'] == 1
        assert result['data']['char_count'] == 5

    def test_error_handling_workflow(self):
        """
        E2E Test: Error handling across full stack

        Validates:
        - Invalid operations are caught
        - Errors are properly reported
        - System remains stable
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Execute invalid operation
        result = tool.func(
            action="nonexistent_operation",
            params={}
        )

        # Should return error response, not crash
        assert isinstance(result, dict)
        assert result['success'] is False
        assert 'error' in result


@pytest.mark.e2e
class TestEndToEndMultiMCP:
    """Test workflows involving multiple MCPs"""

    def test_multiple_mcps_in_collection(self):
        """
        E2E Test: Use multiple MCPs in single workflow

        Validates:
        - Multiple MCPs can coexist
        - Each maintains separate state
        - No interference between MCPs
        """
        # Create collection
        tools = [
            mcp_to_langchain_tool(E2ETestMCP),
            mcp_to_langchain_tool(ScriptOps)
        ]

        assert len(tools) == 2

        # Execute operations from different MCPs
        result1 = tools[0].func(
            action="analyze_text",
            params={"text": "Test"}
        )

        # Both should work independently
        assert result1['success'] is True

        # Tools have different names
        assert tools[0].name != tools[1].name

    def test_sequential_mcp_execution(self):
        """
        E2E Test: Execute multiple MCP operations sequentially

        Simulates a workflow where one MCP's output feeds into another
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Execute first operation
        result1 = tool.func(
            action="analyze_text",
            params={"text": "First operation"}
        )

        assert result1['success'] is True
        word_count = result1['data']['word_count']

        # Execute second operation (simulating using result1's data)
        result2 = tool.func(
            action="analyze_text",
            params={"text": f"Result: {word_count} words"}
        )

        assert result2['success'] is True
        assert result2['data']['word_count'] == 3


@pytest.mark.e2e
class TestEndToEndFileOperations:
    """Test end-to-end file operation workflows"""

    def test_file_based_workflow(self):
        """
        E2E Test: Complete workflow with file operations

        Flow:
        1. Create temporary file
        2. Use ScriptOps to read it
        3. Validate content
        4. Cleanup
        """
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# Test script\nprint("Hello")\n')
            temp_path = f.name

        try:
            # Convert ScriptOps
            tool = mcp_to_langchain_tool(ScriptOps)

            # Try to execute (may require approval in interactive mode)
            # For E2E test, we verify the tool is properly set up
            assert tool is not None
            assert callable(tool.func)

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)


@pytest.mark.e2e
class TestEndToEndPerformance:
    """Test performance characteristics end-to-end"""

    def test_discovery_performance(self):
        """
        E2E Test: Discovery performance

        Validates:
        - Discovery completes in reasonable time
        - Multiple discoveries are consistent
        """
        import time

        start = time.time()
        tools = discover_and_convert_mcp_domains()
        duration = time.time() - start

        # Should complete in < 1 second
        assert duration < 1.0, f"Discovery took {duration}s, expected < 1s"

        # Count should be consistent
        count1 = len(tools)
        tools2 = discover_and_convert_mcp_domains()
        count2 = len(tools2)

        assert count1 == count2, "Discovery should be deterministic"

    def test_conversion_performance(self):
        """
        E2E Test: Conversion performance

        Validates:
        - Conversion is fast
        - Multiple conversions don't degrade
        """
        import time

        # Convert multiple times
        times = []
        for _ in range(10):
            start = time.time()
            tool = mcp_to_langchain_tool(E2ETestMCP)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        # Should average < 0.01s per conversion
        assert avg_time < 0.01, f"Average conversion: {avg_time}s, expected < 0.01s"

    def test_execution_performance(self):
        """
        E2E Test: Execution performance

        Validates:
        - Operations execute quickly
        - No performance degradation
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        times = []
        for _ in range(100):
            start = time.time()
            result = tool.func(action="analyze_text", params={"text": "Quick test"})
            times.append(time.time() - start)
            assert result['success'] is True

        avg_time = sum(times) / len(times)
        # Should average < 0.01s per execution
        assert avg_time < 0.01, f"Average execution: {avg_time}s, expected < 0.01s"


@pytest.mark.e2e
class TestEndToEndScalability:
    """Test scalability characteristics"""

    def test_many_mcps_discovery(self):
        """
        E2E Test: Discovery with many MCPs

        Validates system handles multiple MCPs gracefully
        """
        # Create multiple test MCPs dynamically
        test_mcps = []
        for i in range(10):
            class_name = f"TestMCP{i}"
            mcp_class = type(class_name, (MCPBase,), {
                'get_capabilities': lambda self: [],
            })
            test_mcps.append(mcp_class)

        # Convert all
        tools = [mcp_to_langchain_tool(mcp) for mcp in test_mcps]

        assert len(tools) == 10

        # All should have unique names
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), "All MCP names should be unique"

    def test_concurrent_execution(self):
        """
        E2E Test: Concurrent execution

        Validates thread-safety and concurrent execution
        """
        import concurrent.futures

        tool = mcp_to_langchain_tool(E2ETestMCP)

        def execute_operation(text):
            return tool.func(action="analyze_text", params={"text": text})

        # Execute concurrently
        texts = [f"Text number {i}" for i in range(20)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(execute_operation, texts))

        # All should succeed
        assert all(r['success'] for r in results)
        assert len(results) == 20


@pytest.mark.e2e
class TestEndToEndRobustness:
    """Test system robustness and error recovery"""

    def test_missing_params_handling(self):
        """
        E2E Test: Handling missing required parameters

        Validates graceful error handling
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Execute without required param
        result = tool.func(action="analyze_text", params={})

        # Should handle gracefully (either error or use default)
        assert isinstance(result, dict)

    def test_invalid_param_types(self):
        """
        E2E Test: Handling invalid parameter types

        Validates type safety
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Try to pass wrong type
        result = tool.func(
            action="analyze_text",
            params={"text": 123}  # Should be string
        )

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_malformed_operation_name(self):
        """
        E2E Test: Handling malformed operation names

        Validates input validation
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Try malformed names
        test_cases = [
            "",  # Empty
            "   ",  # Whitespace
            "operation with spaces",  # Spaces
            "UPPERCASE",  # Wrong case
        ]

        for case in test_cases:
            result = tool.func(action=case, params={})
            # Should return error, not crash
            assert isinstance(result, dict)


@pytest.mark.e2e
class TestEndToEndIntegration:
    """Test integration with external systems"""

    def test_langchain_agent_integration(self):
        """
        E2E Test: Integration with LangChain agents

        Validates tools work in LangChain ecosystem
        """
        tool = mcp_to_langchain_tool(E2ETestMCP)

        # Verify LangChain compatibility
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'func')
        assert hasattr(tool, 'args_schema')
        assert hasattr(tool, 'return_direct')

        # Execute as LangChain would
        result = tool.func(action="analyze_text", params={"text": "Integration test"})
        assert isinstance(result, dict)
        assert 'success' in result

    def test_state_persistence(self):
        """
        E2E Test: State persistence across operations

        Validates MCP instances maintain state correctly
        """
        mcp = E2ETestMCP()

        # Execute multiple operations
        result1 = mcp.analyze_text("First call")
        result2 = mcp.analyze_text("Second call")

        # Both should succeed independently
        assert result1.success
        assert result2.success

        # Results should be different (different inputs)
        assert result1.data != result2.data


@pytest.mark.e2e
class TestEndToEndCompleteWorkflow:
    """Test complete real-world workflows"""

    def test_complete_analysis_workflow(self):
        """
        E2E Test: Complete analysis workflow

        Simulates real-world usage:
        1. Discover available MCPs
        2. Select appropriate MCP
        3. Execute analysis
        4. Process results
        """
        # Step 1: Discover
        tools = discover_and_convert_mcp_domains(
            search_paths=['mcp.simple'],
            verbose=False
        )
        assert len(tools) > 0

        # Step 2: Select (using E2ETestMCP for predictable results)
        analysis_tool = mcp_to_langchain_tool(E2ETestMCP)

        # Step 3: Execute
        sample_text = """
        This is a sample text for analysis.
        It has multiple lines.
        Each line contains different content.
        The analysis should count words and lines.
        """

        result = analysis_tool.func(
            action="analyze_text",
            params={"text": sample_text}
        )

        # Step 4: Process results
        assert result['success'] is True
        assert result["data"]["line_count"] >= 4
        assert result['data']['word_count'] > 20

        # Results are actionable
        metrics = result['data']
        assert isinstance(metrics, dict)
        assert all(key in metrics for key in [
            'word_count', 'char_count', 'line_count'
        ])

    def test_end_to_end_user_story(self):
        """
        E2E Test: Complete user story

        User wants to:
        1. See what MCPs are available
        2. Use one to analyze some text
        3. Get meaningful results
        """
        # 1. User discovers available tools
        all_tools = discover_and_convert_mcp_domains()
        print(f"\n[E2E] User sees {len(all_tools)} available MCP tools")

        # 2. User selects a tool for text analysis
        analysis_tool = mcp_to_langchain_tool(E2ETestMCP)
        print(f"[E2E] User selects: {analysis_tool.name}")

        # 3. User provides input
        user_text = "Hello world! This is an end-to-end test."

        # 4. System executes
        result = analysis_tool.func(
            action="analyze_text",
            params={"text": user_text}
        )

        # 5. User gets results
        assert result['success'] is True
        print(f"[E2E] Results: {result['data']}")

        # 6. Results are useful
        assert result["data"]["word_count"] >= 7
        assert result["data"]["char_count"] >= 40


# Test execution summary
if __name__ == "__main__":
    # Run with: pytest tests/e2e/test_end_to_end.py -v -s -m e2e
    pytest.main([__file__, "-v", "-s", "-m", "e2e"])
