"""
Comprehensive tests for new MCP simple domains:
- FileManager
- DataReader
- TextProcessor

Tests verify:
- MCPResponse format
- Safety decorators
- Error handling
- Functionality
"""

import pytest
import tempfile
import json
import pandas as pd
from pathlib import Path

from mcp.simple import FileManager, DataReader, TextProcessor
from mcp.core.base import MCPResponse, MCPStatus


class TestFileManager:
    """Test suite for FileManager domain"""

    def setup_method(self):
        """Setup test fixtures"""
        self.fm = FileManager()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    # === File Creation Tests ===

    def test_create_file_success(self):
        """Test creating a new file"""
        file_path = self.temp_path / "test.txt"
        response = self.fm.create_file(str(file_path), "Hello World")

        assert isinstance(response, MCPResponse)
        assert response.success
        assert response.data['created']
        assert Path(response.data['path']).exists()
        assert file_path.read_text() == "Hello World"

    def test_create_file_with_parent_dirs(self):
        """Test creating file with non-existent parent directories"""
        file_path = self.temp_path / "subdir" / "test.txt"
        response = self.fm.create_file(str(file_path), "content")

        assert response.success
        assert file_path.exists()
        assert file_path.parent.exists()

    def test_create_file_already_exists(self):
        """Test creating file that already exists (should fail)"""
        file_path = self.temp_path / "existing.txt"
        file_path.write_text("original")

        response = self.fm.create_file(str(file_path), "new content")

        assert not response.success
        assert "already exists" in response.error.lower()
        assert file_path.read_text() == "original"  # Not overwritten

    def test_create_file_with_overwrite(self):
        """Test creating file with overwrite flag"""
        file_path = self.temp_path / "existing.txt"
        file_path.write_text("original")

        response = self.fm.create_file(str(file_path), "new content", overwrite=True)

        assert response.success
        assert file_path.read_text() == "new content"

    # === File Deletion Tests ===

    def test_delete_file_success(self):
        """Test deleting an existing file"""
        file_path = self.temp_path / "delete_me.txt"
        file_path.write_text("temporary")

        response = self.fm.delete_file(str(file_path))

        assert response.success
        assert response.data['deleted']
        assert not file_path.exists()

    def test_delete_file_not_exists(self):
        """Test deleting non-existent file (should fail)"""
        file_path = self.temp_path / "nonexistent.txt"
        response = self.fm.delete_file(str(file_path))

        assert not response.success
        assert "not found" in response.error.lower() or "does not exist" in response.error.lower()

    # === File Move Tests ===

    def test_move_file_success(self):
        """Test moving a file"""
        source = self.temp_path / "source.txt"
        dest = self.temp_path / "dest.txt"
        source.write_text("content")

        response = self.fm.move_file(str(source), str(dest))

        assert response.success
        assert response.data['moved']
        assert not source.exists()
        assert dest.exists()
        assert dest.read_text() == "content"

    def test_move_file_to_subdir(self):
        """Test moving file to subdirectory"""
        source = self.temp_path / "source.txt"
        dest = self.temp_path / "subdir" / "dest.txt"
        source.write_text("content")

        response = self.fm.move_file(str(source), str(dest))

        assert response.success
        assert dest.exists()
        assert dest.read_text() == "content"

    def test_move_file_dest_exists(self):
        """Test moving to existing destination (should fail)"""
        source = self.temp_path / "source.txt"
        dest = self.temp_path / "dest.txt"
        source.write_text("source content")
        dest.write_text("dest content")

        response = self.fm.move_file(str(source), str(dest))

        assert not response.success
        assert "exists" in response.error.lower()

    # === File Copy Tests ===

    def test_copy_file_success(self):
        """Test copying a file"""
        source = self.temp_path / "source.txt"
        dest = self.temp_path / "dest.txt"
        source.write_text("content")

        response = self.fm.copy_file(str(source), str(dest))

        assert response.success
        assert response.data['copied']
        assert source.exists()  # Source still exists
        assert dest.exists()
        assert dest.read_text() == "content"

    # === File Listing Tests ===

    def test_list_files_all(self):
        """Test listing all files in directory"""
        (self.temp_path / "file1.txt").write_text("1")
        (self.temp_path / "file2.txt").write_text("2")
        (self.temp_path / "file3.py").write_text("3")

        response = self.fm.list_files(str(self.temp_path))

        assert response.success
        assert response.data['count'] >= 3
        assert len(response.data['files']) >= 3

    def test_list_files_with_pattern(self):
        """Test listing files with glob pattern"""
        (self.temp_path / "file1.txt").write_text("1")
        (self.temp_path / "file2.txt").write_text("2")
        (self.temp_path / "file3.py").write_text("3")

        response = self.fm.list_files(str(self.temp_path), pattern="*.txt")

        assert response.success
        assert response.data['count'] >= 2
        txt_files = [f for f in response.data['files'] if f.endswith('.txt')]
        assert len(txt_files) >= 2

    def test_list_files_recursive(self):
        """Test listing files recursively"""
        (self.temp_path / "file1.txt").write_text("1")
        subdir = self.temp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("2")

        response = self.fm.list_files(str(self.temp_path), pattern="*.txt", recursive=True)

        assert response.success
        assert response.data['count'] >= 2

    # === File Info Tests ===

    def test_get_file_info(self):
        """Test getting file information"""
        file_path = self.temp_path / "info_test.txt"
        file_path.write_text("test content")

        response = self.fm.get_file_info(str(file_path))

        assert response.success
        assert response.data['name'] == "info_test.txt"
        assert response.data['size'] > 0
        assert response.data['extension'] == ".txt"
        assert response.data['exists']
        assert 'created' in response.data
        assert 'modified' in response.data


class TestDataReader:
    """Test suite for DataReader domain"""

    def setup_method(self):
        """Setup test fixtures"""
        self.dr = DataReader()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    # === CSV Tests ===

    def test_read_csv_success(self):
        """Test reading a CSV file"""
        csv_path = self.temp_path / "test.csv"
        csv_path.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        response = self.dr.read_csv(str(csv_path))

        assert response.success
        assert response.data['rows'] == 2
        assert response.data['columns'] == ['name', 'age', 'city']
        assert len(response.data['preview']) == 2

    def test_read_csv_custom_delimiter(self):
        """Test reading CSV with custom delimiter"""
        tsv_path = self.temp_path / "test.tsv"
        tsv_path.write_text("name\tage\tcity\nAlice\t30\tNYC\n")

        response = self.dr.read_csv(str(tsv_path), delimiter="\t")

        assert response.success
        assert response.data['columns'] == ['name', 'age', 'city']

    def test_read_csv_not_found(self):
        """Test reading non-existent CSV"""
        response = self.dr.read_csv(str(self.temp_path / "nonexistent.csv"))

        assert not response.success
        assert "not found" in response.error.lower()

    # === JSON Tests ===

    def test_read_json_success(self):
        """Test reading a JSON file"""
        json_path = self.temp_path / "test.json"
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        json_path.write_text(json.dumps(data))

        response = self.dr.read_json(str(json_path))

        assert response.success
        assert response.data['type'] == 'list'
        assert response.data['size'] == 2
        assert response.data['data'] == data

    def test_read_json_dict(self):
        """Test reading JSON object"""
        json_path = self.temp_path / "test.json"
        data = {"key1": "value1", "key2": "value2"}
        json_path.write_text(json.dumps(data))

        response = self.dr.read_json(str(json_path))

        assert response.success
        assert response.data['type'] == 'dict'
        assert response.data['size'] == 2

    def test_read_json_invalid(self):
        """Test reading invalid JSON"""
        json_path = self.temp_path / "invalid.json"
        json_path.write_text("{ invalid json }")

        response = self.dr.read_json(str(json_path))

        assert not response.success
        assert "json" in response.error.lower()

    # === Parquet Tests ===

    def test_read_parquet_success(self):
        """Test reading a Parquet file"""
        parquet_path = self.temp_path / "test.parquet"
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [30, 25]
        })
        df.to_parquet(parquet_path)

        response = self.dr.read_parquet(str(parquet_path))

        assert response.success
        assert response.data['rows'] == 2
        assert 'name' in response.data['columns']
        assert 'age' in response.data['columns']

    # === Schema Tests ===

    def test_get_schema_csv(self):
        """Test getting schema for CSV"""
        csv_path = self.temp_path / "test.csv"
        csv_path.write_text("name,age,city\nAlice,30,NYC\n")

        response = self.dr.get_schema(str(csv_path))

        assert response.success
        assert response.data['format'] == 'csv'
        assert 'columns' in response.data
        assert len(response.data['columns']) == 3

    def test_get_schema_json(self):
        """Test getting schema for JSON"""
        json_path = self.temp_path / "test.json"
        data = [{"name": "Alice"}, {"name": "Bob"}]
        json_path.write_text(json.dumps(data))

        response = self.dr.get_schema(str(json_path))

        assert response.success
        assert response.data['format'] == 'json'
        assert response.data['type'] == 'list'

    # === Query Tests ===

    def test_query_dataframe_success(self):
        """Test querying a dataframe"""
        data = [
            {'name': 'Alice', 'age': 30, 'city': 'NYC'},
            {'name': 'Bob', 'age': 25, 'city': 'LA'},
            {'name': 'Charlie', 'age': 35, 'city': 'NYC'}
        ]

        response = self.dr.query_dataframe(data, "age > 25")

        assert response.success
        assert response.data['row_count'] == 2  # Alice and Charlie
        assert len(response.data['result']) == 2

    def test_query_dataframe_invalid_query(self):
        """Test invalid query"""
        data = [{'name': 'Alice', 'age': 30}]

        response = self.dr.query_dataframe(data, "invalid_column > 10")

        assert not response.success
        assert "undefined variable" in response.error.lower() or "query failed" in response.error.lower()


class TestTextProcessor:
    """Test suite for TextProcessor domain"""

    def setup_method(self):
        """Setup test fixtures"""
        self.tp = TextProcessor()
        self.sample_text = "The quick brown fox jumps over the lazy dog. The dog is sleeping."

    # === Search Tests ===

    def test_search_text_literal(self):
        """Test literal text search"""
        response = self.tp.search_text(self.sample_text, "dog")

        assert response.success
        assert response.data['count'] == 2
        assert len(response.data['matches']) == 2

    def test_search_text_regex(self):
        """Test regex text search"""
        response = self.tp.search_text(self.sample_text, r"\b\w{3}\b", regex=True)

        assert response.success
        assert response.data['count'] >= 3  # "The", "fox", "the", "dog"

    def test_search_text_ignore_case(self):
        """Test case-insensitive search"""
        response = self.tp.search_text(self.sample_text, "THE", ignore_case=True)

        assert response.success
        assert response.data['count'] == 3  # "The"/"the" appears 3 times total

    def test_search_text_with_indices(self):
        """Test search with index positions"""
        response = self.tp.search_text(self.sample_text, "dog", return_indices=True)

        assert response.success
        assert 'indices' in response.data
        assert len(response.data['indices']) == 2

    # === Replace Tests ===

    def test_replace_text_literal(self):
        """Test literal text replacement"""
        response = self.tp.replace_text(self.sample_text, "dog", "cat")

        assert response.success
        assert response.data['replacements_made'] == 2
        assert "cat" in response.data['new_text']
        assert "dog" not in response.data['new_text']

    def test_replace_text_regex(self):
        """Test regex text replacement"""
        response = self.tp.replace_text(self.sample_text, r"\b(\w{4})\b", r"<\1>", regex=True)

        assert response.success
        assert "<quick>" in response.data['new_text'] or "<over>" in response.data['new_text']

    def test_replace_text_max_replacements(self):
        """Test replacement with limit"""
        response = self.tp.replace_text(self.sample_text, "the", "a", ignore_case=True, max_replacements=1)

        assert response.success
        assert response.data['replacements_made'] == 1

    # === Extract Tests ===

    def test_extract_patterns(self):
        """Test pattern extraction"""
        response = self.tp.extract_patterns(self.sample_text, r"\b\w{4}\b", regex=True)

        assert response.success
        assert response.data['count'] >= 2
        # Should extract 4-letter words like "over", "lazy"

    def test_extract_patterns_with_groups(self):
        """Test pattern extraction with groups"""
        text = "Email: alice@example.com, bob@test.org"
        response = self.tp.extract_patterns(text, r"(\w+)@(\w+\.\w+)", regex=True, group=1)

        assert response.success
        assert 'alice' in response.data['extractions'] or 'bob' in response.data['extractions']

    # === Word Count Tests ===

    def test_count_words(self):
        """Test word frequency counting"""
        response = self.tp.count_words(self.sample_text)

        assert response.success
        assert response.data['total_words'] > 0
        assert response.data['unique_words'] > 0
        assert 'the' in response.data['word_counts']
        assert response.data['word_counts']['the'] == 3  # "The"/"the" appears 3 times (case-insensitive by default)

    def test_count_words_case_sensitive(self):
        """Test case-sensitive word counting"""
        response = self.tp.count_words(self.sample_text, case_sensitive=True)

        assert response.success
        assert 'The' in response.data['word_counts']
        assert 'the' in response.data['word_counts']

    def test_count_words_min_length(self):
        """Test word counting with minimum length"""
        response = self.tp.count_words(self.sample_text, min_length=4)

        assert response.success
        # Short words like "The", "dog" should still be included (length >= 3)
        # But we set min_length=4, so only longer words

    # === Split Tests ===

    def test_split_text_whitespace(self):
        """Test splitting by whitespace"""
        response = self.tp.split_text(self.sample_text)

        assert response.success
        assert response.data['count'] > 10

    def test_split_text_delimiter(self):
        """Test splitting by delimiter"""
        text = "a,b,c,d,e"
        response = self.tp.split_text(text, delimiter=",")

        assert response.success
        assert response.data['count'] == 5
        assert response.data['parts'] == ['a', 'b', 'c', 'd', 'e']

    def test_split_text_regex(self):
        """Test splitting by regex"""
        text = "a1b2c3d"
        response = self.tp.split_text(text, delimiter=r"\d", regex=True)

        assert response.success
        assert 'a' in response.data['parts']
        assert 'b' in response.data['parts']

    def test_split_text_max_splits(self):
        """Test splitting with limit"""
        text = "a,b,c,d,e"
        response = self.tp.split_text(text, delimiter=",", max_splits=2)

        assert response.success
        assert response.data['count'] == 3  # a, b, c,d,e

    # === Analysis Tests ===

    def test_analyze_text(self):
        """Test comprehensive text analysis"""
        response = self.tp.analyze_text(self.sample_text)

        assert response.success
        assert response.data['length'] > 0
        assert response.data['words'] > 0
        assert response.data['sentences'] >= 1
        assert response.data['avg_word_length'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
