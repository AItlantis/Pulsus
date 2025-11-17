"""
Text Processor MCP Domain

Provides MCPBase-compliant operations for text manipulation:
- Searching text with regex
- Replacing text patterns
- Extracting patterns
- Word counting and text analysis
- Text splitting and joining

All operations are read-only (text manipulation returns new text).
"""

import re
from typing import Dict, Any, List, Optional, Pattern
from collections import Counter

from ..core.base import MCPBase, MCPResponse, MCPStatus
from ..core.decorators import read_only, cached


class TextProcessor(MCPBase):
    """
    Text processing operations domain for MCP.

    Provides core functionality for:
    - Searching text (@read_only)
    - Replacing text patterns (@read_only - returns new text)
    - Extracting patterns (@read_only)
    - Counting words (@read_only @cached)
    - Splitting text (@read_only)
    - Text analysis (@read_only)

    All methods return MCPResponse for standardized interaction.
    Operations are read-only (return new text instead of modifying).
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize the text processor domain.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        super().__init__(logger=logger, context=context)

    # ===== Pattern Compilation =====

    def _compile_pattern(self, pattern: str, regex: bool = False, ignore_case: bool = False) -> Pattern:
        """
        Compile a search pattern.

        Args:
            pattern: Search pattern (literal or regex)
            regex: Whether pattern is regex (default: False)
            ignore_case: Whether to ignore case (default: False)

        Returns:
            Compiled regex pattern
        """
        flags = re.IGNORECASE if ignore_case else 0

        if regex:
            return re.compile(pattern, flags)
        else:
            # Escape special characters for literal search
            escaped = re.escape(pattern)
            return re.compile(escaped, flags)

    # ===== Search Operations =====

    @read_only
    def search_text(
        self,
        text: str,
        pattern: str,
        regex: bool = False,
        ignore_case: bool = False,
        return_indices: bool = False
    ) -> MCPResponse:
        """
        Search for pattern in text.

        Args:
            text: Text to search
            pattern: Search pattern (literal or regex)
            regex: Whether pattern is regex (default: False)
            ignore_case: Whether to ignore case (default: False)
            return_indices: Whether to return match indices (default: False)

        Returns:
            MCPResponse with data containing:
            - pattern: Original pattern
            - regex: Whether regex was used
            - matches: List of matched strings
            - count: Number of matches
            - indices: List of (start, end) tuples (if return_indices=True)
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Searching text for pattern: {pattern}')

        try:
            # Compile pattern
            compiled_pattern = self._compile_pattern(pattern, regex, ignore_case)

            # Find matches
            matches = compiled_pattern.finditer(text)
            match_list = []
            indices_list = []

            for match in matches:
                match_list.append(match.group(0))
                if return_indices:
                    indices_list.append((match.start(), match.end()))

            response.data = {
                'pattern': pattern,
                'regex': regex,
                'ignore_case': ignore_case,
                'matches': match_list,
                'count': len(match_list)
            }

            if return_indices:
                response.data['indices'] = indices_list

            response.add_trace(f'Found {len(match_list)} matches')
            return response

        except re.error as e:
            response.set_error(f"Invalid regex pattern: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Search failed: {str(e)}")
            return response

    @read_only
    def replace_text(
        self,
        text: str,
        old: str,
        new: str,
        regex: bool = False,
        ignore_case: bool = False,
        max_replacements: Optional[int] = None
    ) -> MCPResponse:
        """
        Replace pattern in text with new string.

        Args:
            text: Original text
            old: Pattern to replace (literal or regex)
            new: Replacement string
            regex: Whether pattern is regex (default: False)
            ignore_case: Whether to ignore case (default: False)
            max_replacements: Maximum number of replacements (default: None = all)

        Returns:
            MCPResponse with data containing:
            - original_length: Length of original text
            - new_text: Text after replacements
            - new_length: Length of new text
            - replacements_made: Number of replacements made
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Replacing "{old}" with "{new}"')

        try:
            # Compile pattern
            compiled_pattern = self._compile_pattern(old, regex, ignore_case)

            # Count matches before replacement
            original_matches = len(compiled_pattern.findall(text))

            # Perform replacement
            count = max_replacements if max_replacements is not None else 0
            new_text = compiled_pattern.sub(new, text, count=count)

            # Count actual replacements
            if max_replacements is not None and max_replacements < original_matches:
                replacements_made = max_replacements
            else:
                replacements_made = original_matches

            response.data = {
                'original_length': len(text),
                'new_text': new_text,
                'new_length': len(new_text),
                'replacements_made': replacements_made
            }
            response.add_trace(f'Made {replacements_made} replacements')
            return response

        except re.error as e:
            response.set_error(f"Invalid regex pattern: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Replacement failed: {str(e)}")
            return response

    @read_only
    def extract_patterns(
        self,
        text: str,
        pattern: str,
        regex: bool = True,
        ignore_case: bool = False,
        group: Optional[int] = None
    ) -> MCPResponse:
        """
        Extract all matches of a pattern from text.

        Args:
            text: Text to extract from
            pattern: Extraction pattern (must be regex)
            regex: Whether pattern is regex (default: True)
            ignore_case: Whether to ignore case (default: False)
            group: Optional group number to extract (default: None = full match)

        Returns:
            MCPResponse with data containing:
            - pattern: Original pattern
            - extractions: List of extracted strings
            - count: Number of extractions
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Extracting pattern: {pattern}')

        try:
            # Compile pattern
            compiled_pattern = self._compile_pattern(pattern, regex, ignore_case)

            # Extract matches
            matches = compiled_pattern.finditer(text)
            extractions = []

            for match in matches:
                if group is not None:
                    extractions.append(match.group(group))
                else:
                    extractions.append(match.group(0))

            response.data = {
                'pattern': pattern,
                'extractions': extractions,
                'count': len(extractions)
            }
            response.add_trace(f'Extracted {len(extractions)} matches')
            return response

        except re.error as e:
            response.set_error(f"Invalid regex pattern: {str(e)}")
            return response
        except IndexError:
            response.set_error(f"Invalid group number: {group}")
            return response
        except Exception as e:
            response.set_error(f"Extraction failed: {str(e)}")
            return response

    # ===== Text Analysis =====

    @read_only
    @cached(ttl=300)
    def count_words(
        self,
        text: str,
        case_sensitive: bool = False,
        min_length: int = 1
    ) -> MCPResponse:
        """
        Count word frequencies in text.

        Args:
            text: Text to analyze
            case_sensitive: Whether to preserve case (default: False)
            min_length: Minimum word length to count (default: 1)

        Returns:
            MCPResponse with data containing:
            - total_words: Total word count
            - unique_words: Number of unique words
            - word_counts: Dict of word -> count
            - top_10: Top 10 most frequent words
        """
        response = MCPResponse.success_response()
        response.add_trace('Counting words in text')

        try:
            # Extract words (alphanumeric sequences)
            words = re.findall(r'\b\w+\b', text)

            # Apply case sensitivity
            if not case_sensitive:
                words = [w.lower() for w in words]

            # Filter by length
            words = [w for w in words if len(w) >= min_length]

            # Count frequencies
            word_counts = Counter(words)

            response.data = {
                'total_words': len(words),
                'unique_words': len(word_counts),
                'word_counts': dict(word_counts),
                'top_10': word_counts.most_common(10)
            }
            response.add_trace(f'Counted {len(words)} words ({len(word_counts)} unique)')
            return response

        except Exception as e:
            response.set_error(f"Word counting failed: {str(e)}")
            return response

    @read_only
    def split_text(
        self,
        text: str,
        delimiter: str = None,
        regex: bool = False,
        max_splits: Optional[int] = None
    ) -> MCPResponse:
        """
        Split text by delimiter.

        Args:
            text: Text to split
            delimiter: Delimiter (default: None = whitespace)
            regex: Whether delimiter is regex (default: False)
            max_splits: Maximum number of splits (default: None = all)

        Returns:
            MCPResponse with data containing:
            - delimiter: Delimiter used
            - parts: List of text parts
            - count: Number of parts
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Splitting text by: {delimiter}')

        try:
            # Split text
            if delimiter is None:
                # Split by whitespace
                parts = text.split(maxsplit=max_splits if max_splits else -1)
            elif regex:
                # Split by regex
                compiled_pattern = re.compile(delimiter)
                parts = compiled_pattern.split(text, maxsplit=max_splits if max_splits else 0)
            else:
                # Split by literal string
                parts = text.split(delimiter, maxsplit=max_splits if max_splits else -1)

            response.data = {
                'delimiter': delimiter if delimiter else '<whitespace>',
                'regex': regex,
                'parts': parts,
                'count': len(parts)
            }
            response.add_trace(f'Split into {len(parts)} parts')
            return response

        except re.error as e:
            response.set_error(f"Invalid regex delimiter: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Split failed: {str(e)}")
            return response

    @read_only
    def analyze_text(self, text: str) -> MCPResponse:
        """
        Perform comprehensive text analysis.

        Args:
            text: Text to analyze

        Returns:
            MCPResponse with data containing:
            - length: Total character count
            - lines: Number of lines
            - words: Number of words
            - sentences: Approximate number of sentences
            - avg_word_length: Average word length
            - avg_sentence_length: Average sentence length (in words)
        """
        response = MCPResponse.success_response()
        response.add_trace('Analyzing text')

        try:
            # Basic counts
            length = len(text)
            lines = text.count('\n') + 1

            # Word analysis
            words = re.findall(r'\b\w+\b', text)
            word_count = len(words)

            # Sentence analysis (approximate - split by . ! ?)
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_count = len(sentences)

            # Calculate averages
            avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

            response.data = {
                'length': length,
                'lines': lines,
                'words': word_count,
                'sentences': sentence_count,
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'whitespace_chars': len([c for c in text if c.isspace()])
            }
            response.add_trace('Text analysis complete')
            return response

        except Exception as e:
            response.set_error(f"Text analysis failed: {str(e)}")
            return response
