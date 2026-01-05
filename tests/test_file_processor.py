"""Tests for file processor"""

import pytest
from pathlib import Path
from candidate_evaluator.utils.file_processor import FileProcessor


def test_process_txt_file():
    """Test processing a text file"""
    processor = FileProcessor()

    # Create a temporary text file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        result = processor.process_file(temp_path)

        assert result['content'] == "Test content"
        assert result['metadata']['file_type'] == '.txt'
        assert result['metadata']['filename'] == Path(temp_path).name

    finally:
        Path(temp_path).unlink()


def test_unsupported_format():
    """Test that unsupported formats raise an error"""
    processor = FileProcessor()

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported file format"):
            processor.process_file(temp_path)

    finally:
        Path(temp_path).unlink()


def test_file_not_found():
    """Test that missing files raise an error"""
    processor = FileProcessor()

    with pytest.raises(FileNotFoundError):
        processor.process_file("/nonexistent/file.txt")
