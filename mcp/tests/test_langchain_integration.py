"""
LangChain Integration Tests for MCP Domains

Tests verify that MCP domains can be converted to LangChain StructuredTools
and function correctly within the LangChain ecosystem.
"""

import pytest
import tempfile
import json
from pathlib import Path

from mcp.simple import ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor
from langchain.tool_adapter import (
    mcp_to_langchain_tool,
    discover_and_convert_mcp_domains,
    MCPToolRegistry
)


class TestLangChainToolConversion:
    """Test conversion of MCP domains to LangChain tools"""

    def test_convert_file_manager_to_tool(self):
        """Test converting FileManager to LangChain tool"""
        tool = mcp_to_langchain_tool(FileManager)

        assert tool is not None
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert tool.name == 'FileManager'
        assert 'FileManager' in tool.description

    def test_convert_data_reader_to_tool(self):
        """Test converting DataReader to LangChain tool"""
        tool = mcp_to_langchain_tool(DataReader)

        assert tool is not None
        assert tool.name == 'DataReader'
        assert hasattr(tool, 'func')

    def test_convert_text_processor_to_tool(self):
        """Test converting TextProcessor to LangChain tool"""
        tool = mcp_to_langchain_tool(TextProcessor)

        assert tool is not None
        assert tool.name == 'TextProcessor'
        assert hasattr(tool, 'args_schema')

    def test_convert_specific_operation_to_tool(self):
        """Test converting specific operation to tool"""
        # Convert FileManager.list_files to a tool
        tool = mcp_to_langchain_tool(FileManager, 'list_files')

        assert tool is not None
        assert 'FileManager_list_files' in tool.name
        assert hasattr(tool, 'func')

    def test_converted_tool_has_args_schema(self):
        """Test that converted tools have Pydantic args schema"""
        tool = mcp_to_langchain_tool(FileManager)

        assert hasattr(tool, 'args_schema')
        # Should have operation and params fields
        schema_fields = tool.args_schema.__fields__
        assert 'operation' in schema_fields
        assert 'params' in schema_fields


class TestLangChainToolExecution:
    """Test execution of LangChain tools"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_execute_file_manager_tool(self):
        """Test executing FileManager tool via LangChain"""
        tool = mcp_to_langchain_tool(FileManager)

        # Create a test file
        test_file = self.temp_path / "test.txt"
        result = tool.func(
            operation='create_file',
            params={'path': str(test_file), 'content': 'Hello LangChain'}
        )

        assert result['success']
        assert 'data' in result
        assert test_file.exists()

    def test_execute_data_reader_tool(self):
        """Test executing DataReader tool via LangChain"""
        tool = mcp_to_langchain_tool(DataReader)

        # Create a test CSV
        csv_file = self.temp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\n")

        result = tool.func(
            operation='read_csv',
            params={'path': str(csv_file)}
        )

        assert result['success']
        assert result['data']['rows'] == 2

    def test_execute_text_processor_tool(self):
        """Test executing TextProcessor tool via LangChain"""
        tool = mcp_to_langchain_tool(TextProcessor)

        result = tool.func(
            operation='search_text',
            params={
                'text': 'The quick brown fox',
                'pattern': 'quick'
            }
        )

        assert result['success']
        assert result['data']['count'] == 1

    def test_execute_specific_operation_tool(self):
        """Test executing specific operation tool"""
        # Get list_files as a specific tool
        tool = mcp_to_langchain_tool(FileManager, 'list_files')

        # Create some test files
        (self.temp_path / "file1.txt").write_text("1")
        (self.temp_path / "file2.txt").write_text("2")

        # Execute via LangChain
        result = tool.func(directory=str(self.temp_path))

        assert result['success']
        assert result['data']['count'] >= 2


class TestMCPToolDiscovery:
    """Test automatic discovery of MCP domains"""

    def test_discover_mcp_domains(self):
        """Test automatic discovery of all MCP domains"""
        tools = discover_and_convert_mcp_domains(
            search_paths=['mcp.simple'],
            verbose=False
        )

        # Should find at least 5 domains: ScriptOps, RepositoryOps, FileManager, DataReader, TextProcessor
        assert len(tools) >= 5

        # Check that all expected domains are discovered
        tool_names = [t.name for t in tools]
        assert 'FileManager' in tool_names
        assert 'DataReader' in tool_names
        assert 'TextProcessor' in tool_names

    def test_discover_domains_verbose(self):
        """Test discovery with verbose output"""
        import io
        import sys

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            tools = discover_and_convert_mcp_domains(
                search_paths=['mcp.simple'],
                verbose=True
            )
            output = buffer.getvalue()

            # Should print discovered domains
            assert 'Discovered:' in output or len(tools) > 0

        finally:
            sys.stdout = old_stdout


class TestMCPToolRegistry:
    """Test MCPToolRegistry functionality"""

    def test_create_registry(self):
        """Test creating a tool registry"""
        registry = MCPToolRegistry()

        assert registry is not None
        assert len(registry.list_domains()) == 0

    def test_register_domain(self):
        """Test registering a domain"""
        registry = MCPToolRegistry()
        registry.register_domain(FileManager)

        assert 'FileManager' in registry.list_domains()
        assert 'FileManager' in registry.list_tools()

    def test_register_multiple_domains(self):
        """Test registering multiple domains"""
        registry = MCPToolRegistry()
        registry.register_domain(FileManager)
        registry.register_domain(DataReader)
        registry.register_domain(TextProcessor)

        domains = registry.list_domains()
        assert len(domains) == 3
        assert 'FileManager' in domains
        assert 'DataReader' in domains
        assert 'TextProcessor' in domains

    def test_register_specific_operation(self):
        """Test registering specific operations"""
        registry = MCPToolRegistry()
        registry.register_operation(FileManager, 'list_files')
        registry.register_operation(DataReader, 'read_csv')

        tools = registry.list_tools()
        assert 'FileManager_list_files' in tools
        assert 'DataReader_read_csv' in tools

    def test_get_tool(self):
        """Test getting a tool by name"""
        registry = MCPToolRegistry()
        registry.register_domain(FileManager)

        tool = registry.get_tool('FileManager')
        assert tool is not None
        assert tool.name == 'FileManager'

    def test_get_all_tools(self):
        """Test getting all tools"""
        registry = MCPToolRegistry()
        registry.register_domain(FileManager)
        registry.register_domain(DataReader)

        tools = registry.get_all_tools()
        assert len(tools) == 2

    def test_get_domain_capabilities(self):
        """Test getting domain capabilities"""
        registry = MCPToolRegistry()
        registry.register_domain(FileManager)

        capabilities = registry.get_domain_capabilities('FileManager')
        assert len(capabilities) > 0
        assert isinstance(capabilities, list)

        # Check that capabilities have expected structure
        assert all('name' in cap for cap in capabilities)
        assert all('description' in cap for cap in capabilities)


class TestLangChainIntegrationScenarios:
    """Test realistic integration scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.registry = MCPToolRegistry()

    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_multi_domain_workflow(self):
        """Test workflow using multiple domains"""
        # Register domains
        self.registry.register_domain(FileManager)
        self.registry.register_domain(DataReader)
        self.registry.register_domain(TextProcessor)

        # Get tools
        file_tool = self.registry.get_tool('FileManager')
        data_tool = self.registry.get_tool('DataReader')
        text_tool = self.registry.get_tool('TextProcessor')

        # Workflow: Create CSV → Read CSV → Process text from data
        # Step 1: Create CSV
        csv_file = self.temp_path / "data.csv"
        result1 = file_tool.func(
            operation='create_file',
            params={
                'path': str(csv_file),
                'content': 'name,description\nAlice,Quick learner\nBob,Fast worker'
            }
        )
        assert result1['success']

        # Step 2: Read CSV
        result2 = data_tool.func(
            operation='read_csv',
            params={'path': str(csv_file)}
        )
        assert result2['success']
        assert result2['data']['rows'] == 2

        # Step 3: Process text from description column
        descriptions = "Quick learner Fast worker"
        result3 = text_tool.func(
            operation='count_words',
            params={'text': descriptions}
        )
        assert result3['success']
        assert result3['data']['total_words'] == 4

    def test_tool_error_handling(self):
        """Test that LangChain tools properly handle errors"""
        self.registry.register_domain(FileManager)
        tool = self.registry.get_tool('FileManager')

        # Try to read non-existent file
        result = tool.func(
            operation='get_file_info',
            params={'path': '/nonexistent/file.txt'}
        )

        # Should return MCPResponse with error
        assert not result['success']
        assert 'error' in result
        assert result['error'] is not None

    def test_registry_with_all_classic_domains(self):
        """Test registry with all classic MCP domains"""
        # Register all 5 classic domains
        self.registry.register_domain(ScriptOps)
        self.registry.register_domain(RepositoryOps)
        self.registry.register_domain(FileManager)
        self.registry.register_domain(DataReader)
        self.registry.register_domain(TextProcessor)

        # Verify all registered
        domains = self.registry.list_domains()
        assert len(domains) == 5
        assert all(d in domains for d in [
            'ScriptOps', 'RepositoryOps', 'FileManager', 'DataReader', 'TextProcessor'
        ])

        # Get all tools
        tools = self.registry.get_all_tools()
        assert len(tools) == 5

    def test_operation_specific_tools_workflow(self):
        """Test workflow using operation-specific tools"""
        # Register specific operations instead of entire domains
        self.registry.register_operation(FileManager, 'create_file')
        self.registry.register_operation(FileManager, 'list_files')
        self.registry.register_operation(TextProcessor, 'analyze_text')

        # Verify tools created
        assert 'FileManager_create_file' in self.registry.list_tools()
        assert 'FileManager_list_files' in self.registry.list_tools()
        assert 'TextProcessor_analyze_text' in self.registry.list_tools()

        # Execute workflow
        create_tool = self.registry.get_tool('FileManager_create_file')
        test_file = self.temp_path / "test.txt"

        result = create_tool.func(
            path=str(test_file),
            content="The quick brown fox jumps over the lazy dog."
        )

        assert result['success']
        assert Path(result['data']['path']).exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
