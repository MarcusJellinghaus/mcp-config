"""Tests for Claude Code handler functionality."""

import pytest

from src.mcp_config.clients.claude_code import normalize_server_name


def test_normalize_server_name_valid():
    """Test that valid names pass through unchanged."""
    # Valid with hyphens
    normalized, was_modified = normalize_server_name("my-server")
    assert normalized == "my-server"
    assert was_modified is False

    # Valid with underscores
    normalized, was_modified = normalize_server_name("valid_name-123")
    assert normalized == "valid_name-123"
    assert was_modified is False

    # Valid with mixed case
    normalized, was_modified = normalize_server_name("MixedCase")
    assert normalized == "MixedCase"
    assert was_modified is False


def test_normalize_server_name_spaces():
    """Test that spaces are converted to underscores."""
    normalized, was_modified = normalize_server_name("my server")
    assert normalized == "my_server"
    assert was_modified is True

    # Multiple spaces
    normalized, was_modified = normalize_server_name("  spaces  ")
    assert normalized == "__spaces__"
    assert was_modified is True


def test_normalize_server_name_invalid_chars():
    """Test that invalid characters are removed."""
    # Special characters
    normalized, was_modified = normalize_server_name("my server!")
    assert normalized == "my_server"
    assert was_modified is True

    # Various invalid characters
    normalized, was_modified = normalize_server_name("my@server#123")
    assert normalized == "myserver123"
    assert was_modified is True


def test_normalize_server_name_length():
    """Test that names longer than 64 chars are truncated."""
    long_name = "a" * 100
    normalized, was_modified = normalize_server_name(long_name)
    assert len(normalized) == 64
    assert normalized == "a" * 64
    assert was_modified is True


def test_normalize_server_name_combined():
    """Test combination of transformations."""
    # Spaces + invalid chars + length (need valid chars to remain after cleanup)
    long_name_with_issues = "my server!" + "a" * 100 + "@@@"
    normalized, was_modified = normalize_server_name(long_name_with_issues)
    assert len(normalized) == 64
    assert normalized.startswith("my_server")
    assert normalized.endswith("a")
    assert was_modified is True


def test_normalize_server_name_empty_result():
    """Test that names with only invalid characters raise ValueError."""
    with pytest.raises(ValueError) as exc_info:
        normalize_server_name("!!!")
    assert "contains no valid characters" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        normalize_server_name("@#$%")
    assert "contains no valid characters" in str(exc_info.value)
