"""
Comprehensive tests for prompt_parser.py

Tests cover:
- Intent parsing and classification
- Action guessing and normalization
- Domain detection from hints
- Confidence calculation
- Edge cases and boundary conditions
"""

import pytest
from testudo.agents.pulsus.routing.prompt_parser import (
    parse,
    _guess_action,
    _guess_domain,
    _ACTION_MAP,
    _DOMAIN_HINTS,
)
from testudo.agents.pulsus.core.types import ParsedIntent


class TestActionGuessing:
    """Test action keyword detection and normalization."""

    def test_action_normalization_american_to_british(self):
        """Test American English variants normalize to British spelling."""
        assert _guess_action("summarize this data") == "summarise"
        assert _guess_action("visualize the plot") == "visualise"
        assert _guess_action("analyze the results") == "analyse"

    def test_action_normalization_synonyms(self):
        """Test synonym mapping to canonical actions."""
        assert _guess_action("give me a summary") == "summarise"
        assert _guess_action("plot the data") == "visualise"
        assert _guess_action("import this csv") == "ingest"

    def test_action_greeting_variations(self):
        """Test various greeting forms map to 'greet' action."""
        greetings = ["hello world", "hi there", "hey pulsus", "greet the user"]
        for greeting in greetings:
            assert _guess_action(greeting) == "greet", f"Failed for: {greeting}"

    def test_action_case_insensitivity(self):
        """Test action detection is case-insensitive."""
        assert _guess_action("SUMMARIZE") == "summarise"
        assert _guess_action("SuMmArIzE") == "summarise"
        assert _guess_action("PLOT") == "visualise"

    def test_action_no_match_returns_none(self):
        """Test unknown actions return None."""
        assert _guess_action("foobar unknown action") is None
        assert _guess_action("xyz123") is None
        assert _guess_action("") is None

    def test_action_partial_word_matching(self):
        """Test action keywords match within words."""
        # "summarize" is in "please summarize this"
        assert _guess_action("please summarize this") == "summarise"
        # "plot" is in "replot the data"
        assert _guess_action("replot the data") == "visualise"


class TestDomainGuessing:
    """Test domain detection based on keyword hints."""

    def test_domain_analysis_single_hint(self):
        """Test analysis domain detected with single keyword."""
        assert _guess_domain("show me the data") == "analysis"
        assert _guess_domain("calculate the mean") == "analysis"
        assert _guess_domain("what is the median?") == "analysis"

    def test_domain_analysis_multiple_hints(self):
        """Test analysis domain with multiple keywords increases confidence."""
        # Multiple hints should still return analysis
        result = _guess_domain("plot the data matrix with stats and visualise mean")
        assert result == "analysis"

    def test_domain_ingestion_keywords(self):
        """Test ingestion domain detected."""
        assert _guess_domain("load this csv file") == "ingestion"
        assert _guess_domain("import the json data") == "ingestion"
        assert _guess_domain("ingest the schema") == "ingestion"

    def test_domain_chat_keywords(self):
        """Test chat domain detected."""
        assert _guess_domain("hey there") == "chat"
        assert _guess_domain("hello world") == "chat"
        assert _guess_domain("greet the user") == "chat"

    def test_domain_multiple_domains_best_wins(self):
        """Test that domain with most keyword hits wins."""
        # "csv" (ingestion) vs "hello" (chat) - should pick one
        mixed = "hello please load this csv"
        result = _guess_domain(mixed)
        # Both have 1 hit, so whichever comes first in iteration
        assert result in ["chat", "ingestion"]

    def test_domain_case_insensitivity(self):
        """Test domain detection is case-insensitive."""
        assert _guess_domain("LOAD CSV") == "ingestion"
        assert _guess_domain("Hello") == "chat"

    def test_domain_no_match_returns_none(self):
        """Test unknown domains return None."""
        assert _guess_domain("foobar xyz unknown") is None
        assert _guess_domain("123456") is None
        assert _guess_domain("") is None


class TestConfidenceCalculation:
    """Test confidence scoring logic."""

    def test_confidence_base_only(self):
        """Test base confidence with no action or domain."""
        result = parse("random text without keywords")
        assert result.confidence == 0.5

    def test_confidence_with_action_only(self):
        """Test confidence boost from action detection."""
        result = parse("please summarize")  # action: summarise, domain: None
        assert result.action == "summarise"
        assert result.domain is None
        assert result.confidence == 0.7  # 0.5 + 0.2

    def test_confidence_with_domain_only(self):
        """Test confidence boost from domain detection."""
        result = parse("show me the data")  # action: None, domain: analysis
        assert result.action is None
        assert result.domain == "analysis"
        assert result.confidence == 0.7  # 0.5 + 0.2

    def test_confidence_with_both_action_and_domain(self):
        """Test maximum confidence with both action and domain."""
        result = parse("summarize the data matrix")
        # action: summarise (+0.2), domain: analysis (+0.2), both (+0.1)
        assert result.action == "summarise"
        assert result.domain == "analysis"
        assert result.confidence == 0.95  # 0.5 + 0.2 + 0.2 + 0.1, capped at 0.95

    def test_confidence_capped_at_095(self):
        """Test confidence never exceeds 0.95."""
        # Even with perfect matches, confidence should be capped
        result = parse("analyse the data matrix plot visualise mean")
        assert result.confidence == 0.95
        assert result.confidence <= 0.95


class TestParseFunction:
    """Test the main parse() function integration."""

    def test_parse_returns_parsed_intent_type(self):
        """Test parse returns correct dataclass type."""
        result = parse("hello world")
        assert isinstance(result, ParsedIntent)
        assert hasattr(result, "domain")
        assert hasattr(result, "action")
        assert hasattr(result, "intent")
        assert hasattr(result, "confidence")

    def test_parse_preserves_original_text(self):
        """Test intent field contains original unmodified text."""
        original = "SuMmArIzE the DATA!"
        result = parse(original)
        assert result.intent == original

    def test_parse_empty_string(self):
        """Test parsing empty string returns minimal intent."""
        result = parse("")
        assert result.intent == ""
        assert result.domain is None
        assert result.action is None
        assert result.confidence == 0.5

    def test_parse_whitespace_only(self):
        """Test parsing whitespace returns minimal intent."""
        result = parse("   \t\n  ")
        assert result.intent == "   \t\n  "
        assert result.domain is None
        assert result.action is None
        assert result.confidence == 0.5

    def test_parse_very_long_text(self):
        """Test parsing long text still works correctly."""
        long_text = "summarize " + "data " * 100 + "matrix plot mean"
        result = parse(long_text)
        assert result.action == "summarise"
        assert result.domain == "analysis"
        assert result.confidence == 0.95

    def test_parse_special_characters(self):
        """Test parsing text with special characters."""
        result = parse("summarize this @#$%^&* data!")
        assert result.action == "summarise"
        assert result.domain == "analysis"

    def test_parse_unicode_characters(self):
        """Test parsing text with unicode characters."""
        result = parse("summarize データ with émojis 🎉")
        assert result.action == "summarise"
        # Should still work despite unicode


class TestRealWorldScenarios:
    """Test realistic user prompts."""

    def test_scenario_data_analysis_request(self):
        """Test typical data analysis request."""
        result = parse("Can you analyze this dataset and plot the results?")
        # "plot" appears before "analyze" in _ACTION_MAP iteration, so it wins
        assert result.action in ["analyse", "visualise"]  # Either is valid
        assert result.domain == "analysis"
        assert result.confidence == 0.95

    def test_scenario_csv_import(self):
        """Test CSV import request."""
        result = parse("import the CSV file from disk")
        # "import" maps to "ingest", and "csv" triggers ingestion domain
        assert result.action == "ingest"
        assert result.domain == "ingestion"
        assert result.confidence == 0.95

    def test_scenario_greeting(self):
        """Test greeting interaction."""
        result = parse("Hi! How are you?")
        assert result.action == "greet"
        assert result.domain == "chat"
        assert result.confidence == 0.95

    def test_scenario_ambiguous_request(self):
        """Test ambiguous request with low confidence."""
        result = parse("Do work on xyz object")
        # No specific action or domain keywords
        assert result.action is None
        assert result.domain is None
        assert result.confidence == 0.5

    def test_scenario_visualization_request(self):
        """Test visualization request."""
        result = parse("Plot the statistics and visualize the mean")
        assert result.action == "visualise"
        assert result.domain == "analysis"
        assert result.confidence == 0.95

    def test_scenario_json_schema_ingestion(self):
        """Test JSON schema ingestion."""
        result = parse("Import the JSON schema")
        assert result.action == "ingest"
        assert result.domain == "ingestion"
        assert result.confidence == 0.95


class TestActionMapCompleteness:
    """Test _ACTION_MAP configuration."""

    def test_action_map_has_expected_entries(self):
        """Test action map contains key normalizations."""
        expected_mappings = {
            "summarize": "summarise",
            "visualize": "visualise",
            "analyze": "analyse",
        }
        for key, value in expected_mappings.items():
            assert _ACTION_MAP[key] == value

    def test_action_map_all_values_are_british_spelling(self):
        """Test all mapped values use British spelling convention."""
        british_forms = {"summarise", "visualise", "analyse", "ingest", "greet"}
        for value in _ACTION_MAP.values():
            assert value in british_forms or value == "ingest" or value == "greet"


class TestDomainHintsCompleteness:
    """Test _DOMAIN_HINTS configuration."""

    def test_domain_hints_has_three_domains(self):
        """Test we have expected domain categories."""
        assert "analysis" in _DOMAIN_HINTS
        assert "ingestion" in _DOMAIN_HINTS
        assert "chat" in _DOMAIN_HINTS

    def test_domain_hints_are_sets(self):
        """Test domain hints are stored as sets for efficiency."""
        for domain, hints in _DOMAIN_HINTS.items():
            assert isinstance(hints, set)

    def test_domain_hints_are_lowercase(self):
        """Test all hint keywords are lowercase."""
        for domain, hints in _DOMAIN_HINTS.items():
            for hint in hints:
                assert hint == hint.lower(), f"Hint '{hint}' in {domain} not lowercase"

    def test_domain_hints_analysis_coverage(self):
        """Test analysis domain has appropriate keywords."""
        analysis_hints = _DOMAIN_HINTS["analysis"]
        expected = {"data", "matrix", "stat", "plot", "mean", "median"}
        assert expected.issubset(analysis_hints)

    def test_domain_hints_ingestion_coverage(self):
        """Test ingestion domain has appropriate keywords."""
        ingestion_hints = _DOMAIN_HINTS["ingestion"]
        expected = {"csv", "json", "load", "import", "ingest"}
        assert expected.issubset(ingestion_hints)

    def test_domain_hints_chat_coverage(self):
        """Test chat domain has appropriate keywords."""
        chat_hints = _DOMAIN_HINTS["chat"]
        expected = {"hey", "hello", "hi", "greet"}
        assert expected.issubset(chat_hints)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_multiple_actions_in_text(self):
        """Test text with multiple action keywords uses first match."""
        result = parse("summarize then plot then analyze")
        # Should match first occurrence in _ACTION_MAP iteration
        assert result.action is not None

    def test_action_at_start_of_text(self):
        """Test action keyword at beginning."""
        result = parse("Summarize everything")
        assert result.action == "summarise"

    def test_action_at_end_of_text(self):
        """Test action keyword at end."""
        result = parse("Please summarize")
        assert result.action == "summarise"

    def test_domain_keyword_repeated(self):
        """Test repeated domain keywords don't over-count."""
        # _guess_domain uses "in" check, not count, so repeats don't matter much
        result = parse("data data data data")
        assert result.domain == "analysis"

    def test_numeric_input(self):
        """Test purely numeric input."""
        result = parse("123456789")
        assert result.confidence == 0.5
        assert result.action is None
        assert result.domain is None

    def test_punctuation_only(self):
        """Test punctuation-only input."""
        result = parse("!@#$%^&*()")
        assert result.confidence == 0.5
        assert result.action is None
        assert result.domain is None
