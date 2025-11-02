"""Tests for Claude Code handler functionality."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.clients.claude_code import ClaudeCodeHandler, normalize_server_name


# ============================================================================
# Normalization Tests
# ============================================================================


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


# ============================================================================
# ClaudeCodeHandler Tests
# ============================================================================


@pytest.fixture(scope="function")
def temp_config_dir(tmp_path):
    """Create a temporary directory for config testing."""
    # Ensure clean state - remove any existing .mcp.json
    config_file = tmp_path / ".mcp.json"
    if config_file.exists():
        config_file.unlink()
    return tmp_path


@pytest.fixture(scope="function")
def handler(temp_config_dir):
    """Create a ClaudeCodeHandler instance with temp directory."""
    return ClaudeCodeHandler(config_dir=temp_config_dir)


def test_get_config_path_default(temp_config_dir):
    """Test config path is config_dir/.mcp.json."""
    handler = ClaudeCodeHandler(config_dir=temp_config_dir)
    config_path = handler.get_config_path()
    assert config_path == temp_config_dir / ".mcp.json"


def test_get_config_path_cwd():
    """Test config path defaults to cwd/.mcp.json."""
    handler = ClaudeCodeHandler()
    config_path = handler.get_config_path()
    assert config_path == Path.cwd() / ".mcp.json"


def test_load_config_creates_default(handler):
    """Test loading non-existent config returns default structure."""
    config = handler.load_config()
    assert "mcpServers" in config
    assert isinstance(config["mcpServers"], dict)
    assert len(config["mcpServers"]) == 0


def test_load_config_existing(handler, temp_config_dir):
    """Test loading existing config returns the content."""
    # Create a config file
    config_path = temp_config_dir / ".mcp.json"
    test_config = {
        "mcpServers": {
            "test-server": {
                "type": "stdio",
                "command": "python",
                "args": ["-m", "test"],
            }
        }
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f)

    config = handler.load_config()
    assert config == test_config


def test_save_config_creates_file(handler, temp_config_dir):
    """Test saving config creates .mcp.json file."""
    config = {"mcpServers": {"my-server": {"type": "stdio", "command": "test"}}}
    handler.save_config(config)

    config_path = temp_config_dir / ".mcp.json"
    assert config_path.exists()

    # Verify content
    with open(config_path, "r", encoding="utf-8") as f:
        saved_config = json.load(f)
    assert saved_config == config


def test_setup_server_adds_type_field(handler, temp_config_dir):
    """Test that type: stdio is added to server config."""
    server_config = {"command": "python", "args": ["-m", "test"]}
    result = handler.setup_server("my-server", server_config)

    assert result is True

    # Load and verify
    config = handler.load_config()
    assert "my-server" in config["mcpServers"]
    assert config["mcpServers"]["my-server"]["type"] == "stdio"
    assert config["mcpServers"]["my-server"]["command"] == "python"


def test_setup_server_normalizes_name(handler, temp_config_dir, capsys):
    """Test that server names are normalized."""
    server_config = {"command": "python", "args": ["-m", "test"]}
    result = handler.setup_server("my server!", server_config)

    assert result is True

    # Check normalization message was printed
    captured = capsys.readouterr()
    assert "normalized" in captured.out.lower()
    assert "my_server" in captured.out

    # Verify normalized name in config
    config = handler.load_config()
    assert "my_server" in config["mcpServers"]
    assert "my server!" not in config["mcpServers"]


def test_setup_server_strips_metadata(handler, temp_config_dir):
    """Test that metadata fields like _server_type are stripped."""
    server_config = {
        "command": "python",
        "args": ["-m", "test"],
        "_server_type": "mcp-code-checker",
        "_managed_by": "some-tool",
    }
    result = handler.setup_server("my-server", server_config)

    assert result is True

    # Verify metadata fields are NOT in saved config
    config = handler.load_config()
    saved_server = config["mcpServers"]["my-server"]
    assert "_server_type" not in saved_server
    assert "_managed_by" not in saved_server
    assert saved_server["command"] == "python"


@patch("pathlib.Path.home")
def test_setup_server_warns_user_config(mock_home, handler, temp_config_dir, capsys):
    """Test warning printed if ~/.mcp.json exists."""
    # Create a fake home directory with user config
    fake_home = temp_config_dir / "home"
    fake_home.mkdir()
    mock_home.return_value = fake_home

    user_config = fake_home / ".mcp.json"
    user_config.write_text('{"mcpServers": {}}')

    server_config = {"command": "python", "args": ["-m", "test"]}
    result = handler.setup_server("my-server", server_config)

    assert result is True

    # Check warning was printed
    captured = capsys.readouterr()
    assert "warning" in captured.out.lower() or "note" in captured.out.lower()


def test_remove_server_success(handler, temp_config_dir):
    """Test removing existing server."""
    # Setup a server first
    server_config = {"command": "python", "args": ["-m", "test"]}
    handler.setup_server("my-server", server_config)

    # Verify it exists
    config = handler.load_config()
    assert "my-server" in config["mcpServers"]

    # Remove it
    result = handler.remove_server("my-server")
    assert result is True

    # Verify it's gone
    config = handler.load_config()
    assert "my-server" not in config["mcpServers"]


def test_remove_server_not_found(handler, temp_config_dir, capsys):
    """Test removing non-existent server fails gracefully."""
    result = handler.remove_server("nonexistent-server")
    assert result is False

    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


def test_list_managed_servers():
    """Test listing servers returns all servers as managed."""
    import tempfile
    # Create a completely fresh temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        handler = ClaudeCodeHandler(config_dir=temp_path)
    
        # Setup multiple servers
        handler.setup_server("server1", {"command": "python1"})
        handler.setup_server("server2", {"command": "python2"})

        servers = handler.list_managed_servers()
        assert len(servers) == 2, f"Expected 2 servers but found {len(servers)}: {[s['name'] for s in servers]}"

        # All servers should be marked as managed
        server_names = {s["name"] for s in servers}
        assert "server1" in server_names
        assert "server2" in server_names

        # Check structure
        for server in servers:
            assert "name" in server
            assert "type" in server
            assert "command" in server
            assert "managed" in server
            assert server["managed"] is True


def test_list_all_servers():
    """Test list_all_servers returns same as list_managed_servers."""
    import tempfile
    # Create a completely fresh temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        handler = ClaudeCodeHandler(config_dir=temp_path)
        
        handler.setup_server("server1", {"command": "python1"})
        handler.setup_server("server2", {"command": "python2"})

        managed = handler.list_managed_servers()
        all_servers = handler.list_all_servers()

        assert len(managed) == len(all_servers)
        assert set(s["name"] for s in managed) == set(s["name"] for s in all_servers)


def test_backup_config_creates_hidden_file(handler, temp_config_dir):
    """Test backup uses .mcp.backup_* pattern."""
    # Create initial config
    handler.setup_server("test-server", {"command": "python"})

    # Create backup
    backup_path = handler.backup_config()

    assert backup_path.exists()
    assert backup_path.name.startswith(".mcp.backup_")
    assert backup_path.suffix == ".json"


def test_validate_config_basic(handler, temp_config_dir):
    """Test basic configuration validation."""
    # Valid config
    handler.setup_server("test-server", {"command": "python", "args": []})
    errors = handler.validate_config()
    assert len(errors) == 0


def test_validate_config_invalid_structure(handler, temp_config_dir):
    """Test validation catches invalid config structure."""
    # Create invalid config
    config_path = temp_config_dir / ".mcp.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"invalid": "structure"}, f)

    errors = handler.validate_config()
    assert len(errors) > 0
    assert any("mcpServers" in err for err in errors)


def test_validate_config_missing_required_fields(handler, temp_config_dir):
    """Test validation catches missing required fields."""
    # Create config with server missing command
    config_path = temp_config_dir / ".mcp.json"
    config = {"mcpServers": {"bad-server": {"type": "stdio", "args": []}}}
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)

    errors = handler.validate_config()
    assert len(errors) > 0
    assert any("command" in err for err in errors)
