"""
Comprehensive tests for tool_discovery.py

Tests cover:
- Tool discovery from framework directory
- Scoring based on domain and action matching
- Module metadata introspection (__domain__, __action__, __doc__)
- Error handling for malformed modules
- Empty directory handling
- Score thresholding
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch
from agents.pulsus.routing.tool_discovery import discover
from agents.pulsus.core.types import ToolSpec
from agents.pulsus.config.settings import Settings


@pytest.fixture
def isolated_settings(tmp_path):
    """Create isolated settings for testing that won't find real tools."""
    from contextlib import contextmanager

    @contextmanager
    def _create_settings(framework_dir=None):
        with patch('agents.pulsus.routing.tool_discovery.load_settings') as mock_settings:
            settings = Settings()
            settings.framework_root = framework_dir if framework_dir else tmp_path
            # Create empty workflows directory to prevent finding real tools
            empty_workflows = tmp_path / "empty_workflows"
            empty_workflows.mkdir(exist_ok=True)
            settings.workflows_root = empty_workflows
            mock_settings.return_value = settings
            yield mock_settings
    return _create_settings


class TestBasicDiscovery:
    """Test basic tool discovery functionality."""

    def test_discover_with_exact_domain_match(self, tmp_path, isolated_settings):
        """Test discovering tool with exact domain match."""
        # Create a test tool file
        tool_file = tmp_path / "test_tool.py"
        tool_file.write_text('''
__domain__ = "analysis"
__action__ = "summarise"
"""Test analysis tool."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "summarise", "some text")

            assert len(results) == 1
            assert results[0].score == 1.0  # 0.5 domain + 0.5 action
            assert results[0].path == tool_file
            assert results[0].entry == "handle"

    def test_discover_with_domain_only_match(self, tmp_path, isolated_settings):
        """Test discovering tool with only domain match."""
        tool_file = tmp_path / "domain_tool.py"
        tool_file.write_text('''
__domain__ = "ingestion"
__action__ = "load"
"""Tool for data ingestion."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("ingestion", "different_action", "test")

            assert len(results) == 1
            assert results[0].score == 0.5  # 0.5 domain only
            assert results[0].path == tool_file

    def test_discover_with_action_only_match(self, tmp_path, isolated_settings):
        """Test discovering tool with only action match."""
        tool_file = tmp_path / "action_tool.py"
        tool_file.write_text('''
__domain__ = "different"
__action__ = "visualise"
"""Visualization tool."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("other_domain", "visualise", "test")

            assert len(results) == 1
            assert results[0].score == 0.5  # 0.5 action only

    def test_discover_with_no_match_returns_empty(self, tmp_path, isolated_settings):
        """Test discovering with no matching tools returns empty list."""
        tool_file = tmp_path / "nomatch_tool.py"
        tool_file.write_text('''
__domain__ = "xyz"
__action__ = "abc"
"""No match tool."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("different", "other", "test")

            assert len(results) == 0


class TestDocstringMatching:
    """Test domain/action matching via docstrings."""

    def test_discover_domain_in_docstring(self, tmp_path, isolated_settings):
        """Test domain match via docstring when metadata missing."""
        tool_file = tmp_path / "doc_domain_tool.py"
        tool_file.write_text('''
"""This tool is for analysis of data."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "something", "test")

            assert len(results) == 1
            assert results[0].score == 0.5  # Domain in doc

    def test_discover_action_in_docstring(self, tmp_path, isolated_settings):
        """Test action match via docstring."""
        tool_file = tmp_path / "doc_action_tool.py"
        tool_file.write_text('''
"""Tool to summarise data."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("other", "summarise", "test")

            assert len(results) == 1
            assert results[0].score == 0.5  # Action in doc

    def test_discover_both_in_docstring(self, tmp_path, isolated_settings):
        """Test both domain and action in docstring."""
        tool_file = tmp_path / "doc_both_tool.py"
        tool_file.write_text('''
"""Analysis tool to visualise data."""

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "visualise", "test")

            assert len(results) == 1
            assert results[0].score == 1.0  # Both in doc

    def test_discover_metadata_and_docstring_hybrid(self, tmp_path, isolated_settings):
        """Test matching with metadata + docstring combination."""
        tool_file = tmp_path / "hybrid_tool.py"
        tool_file.write_text('''
"""Tool to visualise data."""
__domain__ = "analysis"

def handle(**kwargs):
    pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "visualise", "test")

            # Domain matches metadata (0.5), action in doc (0.5)
            assert len(results) == 1
            assert results[0].score == 1.0


class TestMultipleTools:
    """Test discovery with multiple tools."""

    def test_discover_returns_all_matching_tools(self, tmp_path, isolated_settings):
        """Test multiple matching tools are all returned."""
        # Create multiple tools
        (tmp_path / "tool1.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        (tmp_path / "tool2.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        (tmp_path / "tool3.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert len(results) == 3

    def test_discover_filters_non_matching_tools(self, tmp_path, isolated_settings):
        """Test only matching tools are returned when mixed."""
        (tmp_path / "match1.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        (tmp_path / "nomatch.py").write_text('''
__domain__ = "other"
def handle(**kwargs): pass
''')
        (tmp_path / "match2.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert len(results) == 2

    def test_discover_scores_tools_differently(self, tmp_path, isolated_settings):
        """Test tools receive different scores based on match quality."""
        # Perfect match
        (tmp_path / "perfect.py").write_text('''
__domain__ = "analysis"
__action__ = "summarise"
def handle(**kwargs): pass
''')
        # Domain only
        (tmp_path / "domain_only.py").write_text('''
__domain__ = "analysis"
__action__ = "other"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "summarise", "text")

            # Sort by score descending
            results_sorted = sorted(results, key=lambda x: x.score, reverse=True)
            assert results_sorted[0].score == 1.0  # Perfect match
            assert results_sorted[1].score == 0.5  # Domain only


class TestErrorHandling:
    """Test error handling for malformed modules."""

    def test_discover_skips_syntax_error_files(self, tmp_path, isolated_settings):
        """Test discovery skips files with syntax errors."""
        # Good file
        (tmp_path / "good.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        # Bad syntax file
        (tmp_path / "bad.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs):  # Missing pass, invalid
    if True
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            # Should only find the good file
            assert len(results) == 1
            assert results[0].path.name == "good.py"

    def test_discover_skips_runtime_error_files(self, tmp_path, isolated_settings):
        """Test discovery skips files that raise exceptions during import."""
        # Good file
        (tmp_path / "good.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        # File with runtime error
        (tmp_path / "runtime_error.py").write_text('''
__domain__ = "analysis"
raise RuntimeError("Import error")
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            # Should only find the good file
            assert len(results) == 1
            assert results[0].path.name == "good.py"

    def test_discover_skips_init_file(self, tmp_path, isolated_settings):
        """Test discovery skips __init__.py files."""
        (tmp_path / "__init__.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')
        (tmp_path / "regular.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            # Should only find regular.py
            assert len(results) == 1
            assert results[0].path.name == "regular.py"


class TestEmptyDirectory:
    """Test handling of empty or non-existent directories."""

    def test_discover_empty_directory(self, tmp_path, isolated_settings):
        """Test discovery in empty directory returns empty list."""
        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert len(results) == 0

    def test_discover_directory_with_only_non_py_files(self, tmp_path, isolated_settings):
        """Test directory with only non-.py files returns empty."""
        (tmp_path / "readme.md").write_text("# Readme")
        (tmp_path / "config.json").write_text("{}")

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert len(results) == 0


class TestToolSpecGeneration:
    """Test ToolSpec object generation."""

    def test_tool_spec_contains_correct_path(self, tmp_path, isolated_settings):
        """Test ToolSpec has correct file path."""
        tool_file = tmp_path / "my_tool.py"
        tool_file.write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert results[0].path == tool_file

    def test_tool_spec_entry_is_handle(self, tmp_path, isolated_settings):
        """Test ToolSpec entry point is 'handle'."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert results[0].entry == "handle"

    def test_tool_spec_args_empty_for_now(self, tmp_path, isolated_settings):
        """Test ToolSpec args list is empty (future enhancement)."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert results[0].args == []

    def test_tool_spec_preserves_docstring(self, tmp_path, isolated_settings):
        """Test ToolSpec preserves module docstring."""
        (tmp_path / "tool.py").write_text('''
"""This is a comprehensive docstring for the tool."""
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert "comprehensive docstring" in results[0].doc

    def test_tool_spec_empty_doc_when_missing(self, tmp_path, isolated_settings):
        """Test ToolSpec has empty doc when module has no docstring."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "test", "text")

            assert results[0].doc == ""


class TestScoringLogic:
    """Test scoring algorithm details."""

    def test_score_zero_for_no_match(self, tmp_path, isolated_settings):
        """Test score of 0 doesn't get included in results."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "xyz"
__action__ = "abc"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("different", "other", "text")

            # Zero-score tools should not be in results
            assert len(results) == 0

    def test_score_05_for_domain_match(self, tmp_path, isolated_settings):
        """Test score of 0.5 for domain-only match."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
__action__ = "other"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "different", "text")

            assert results[0].score == 0.5

    def test_score_05_for_action_match(self, tmp_path, isolated_settings):
        """Test score of 0.5 for action-only match."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "other"
__action__ = "summarise"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("different", "summarise", "text")

            assert results[0].score == 0.5

    def test_score_10_for_both_matches(self, tmp_path, isolated_settings):
        """Test score of 1.0 for both domain and action match."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
__action__ = "summarise"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "summarise", "text")

            assert results[0].score == 1.0


class TestMetadataHandling:
    """Test handling of missing metadata."""

    def test_missing_domain_attribute(self, tmp_path, isolated_settings):
        """Test tool with missing __domain__ attribute."""
        (tmp_path / "tool.py").write_text('''
__action__ = "summarise"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            # Should not error, but won't match domain
            results = discover("analysis", "summarise", "text")

            # Should match on action only
            assert len(results) == 1
            assert results[0].score == 0.5

    def test_missing_action_attribute(self, tmp_path, isolated_settings):
        """Test tool with missing __action__ attribute."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "summarise", "text")

            # Should match on domain only
            assert len(results) == 1
            assert results[0].score == 0.5

    def test_missing_all_metadata(self, tmp_path, isolated_settings):
        """Test tool with no metadata attributes."""
        (tmp_path / "tool.py").write_text('''
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("analysis", "summarise", "text")

            # No match, should return empty
            assert len(results) == 0


class TestCaseSensitivity:
    """Test case sensitivity in matching."""

    def test_domain_matching_is_case_sensitive(self, tmp_path, isolated_settings):
        """Test domain matching is case-sensitive for metadata."""
        (tmp_path / "tool.py").write_text('''
__domain__ = "Analysis"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            # Lowercase "analysis" won't match "Analysis"
            results = discover("analysis", "test", "text")

            assert len(results) == 0

    def test_action_matching_is_case_sensitive(self, tmp_path, isolated_settings):
        """Test action matching is case-sensitive for metadata."""
        (tmp_path / "tool.py").write_text('''
__action__ = "Summarise"
def handle(**kwargs): pass
''')

        with isolated_settings(tmp_path):
            results = discover("test", "summarise", "text")

            assert len(results) == 0
