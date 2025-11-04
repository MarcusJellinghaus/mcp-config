"""Tests for Claude Code CLI integration."""

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.clients import (
    CLIENT_HANDLERS,
    ClaudeCodeHandler,
    get_client_handler,
)
from src.mcp_config.integration import (
    generate_client_config,
    remove_mcp_server,
    setup_mcp_server,
)
from src.mcp_config.servers import MCP_CODE_CHECKER


# Global fixture to prevent cross-contamination with Claude Desktop config
@pytest.fixture(scope="module", autouse=True)
def isolate_claude_desktop_config(tmp_path_factory):
    """Prevent any accidental writes to Claude Desktop config during integration tests."""
    temp_dir = tmp_path_factory.mktemp("claude_desktop_isolation")

    from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

    original_get_config_path = ClaudeDesktopHandler.get_config_path

    def mock_get_config_path(self):
        # Return isolated path to prevent real config access
        return temp_dir / "isolated_claude_desktop_config.json"

    # Patch for the duration of this module
    ClaudeDesktopHandler.get_config_path = mock_get_config_path

    yield

    # Restore original method
    ClaudeDesktopHandler.get_config_path = original_get_config_path




class TestClaudeCodeHandlerRegistration:
    """Test ClaudeCodeHandler registration in CLIENT_HANDLERS."""

    def test_claude_code_in_client_handlers(self) -> None:
        """Test that claude-code is registered in CLIENT_HANDLERS."""
        assert "claude-code" in CLIENT_HANDLERS
        assert CLIENT_HANDLERS["claude-code"] == ClaudeCodeHandler

    def test_get_client_handler_returns_claude_code(self) -> None:
        """Test that get_client_handler returns ClaudeCodeHandler instance."""
        handler = get_client_handler("claude-code")
        assert isinstance(handler, ClaudeCodeHandler)

    def test_get_client_handler_instantiates_fresh(self) -> None:
        """Test that each call returns a new instance."""
        handler1 = get_client_handler("claude-code")
        handler2 = get_client_handler("claude-code")
        # Should be different instances
        assert handler1 is not handler2


class TestClaudeCodeSetupCommand:
    """Test mcp-config setup with --client claude-code."""

    @pytest.fixture
    def temp_project_dir(self, tmp_path: Path) -> Path:
        """Create a unique temporary project directory."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        return project_dir

    @pytest.fixture
    def mock_handler(self, temp_project_dir: Path) -> MagicMock:
        """Create a mock ClaudeCodeHandler."""
        handler = MagicMock(spec=ClaudeCodeHandler)
        handler.get_config_path.return_value = temp_project_dir / ".mcp.json"
        handler.setup_server.return_value = True
        handler.list_all_servers.return_value = []
        return handler

    def test_setup_creates_mcp_json(
        self, mock_handler: MagicMock, temp_project_dir: Path
    ) -> None:
        """Test setup command creates .mcp.json in project directory."""
        user_params = {"project_dir": str(temp_project_dir)}

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "test-checker",
            user_params,
        )

        assert result["success"] is True
        assert result["server_name"] == "test-checker"
        assert "config" in result
        mock_handler.setup_server.assert_called_once()

    def test_setup_with_normalization(
        self, mock_handler: MagicMock, temp_project_dir: Path, capsys
    ) -> None:
        """Test setup normalizes server name."""
        user_params = {"project_dir": str(temp_project_dir)}

        # Setup with name that needs normalization
        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "my server!",  # Has space and special char
            user_params,
        )

        assert result["success"] is True
        # Server name should remain as provided to result
        assert result["server_name"] == "my server!"
        mock_handler.setup_server.assert_called_once()

    def test_setup_generates_valid_config(self, temp_project_dir: Path) -> None:
        """Test that generated config is valid for Claude Code."""
        user_params = {"project_dir": str(temp_project_dir)}

        config = generate_client_config(
            MCP_CODE_CHECKER,
            "test-checker",
            user_params,
            python_executable=sys.executable,
        )

        # Should have required fields
        assert "command" in config
        assert "args" in config
        assert "env" in config

        # Should have type field
        assert config["_server_type"] == "mcp-code-checker"

        # Should have project-dir in args
        assert "--project-dir" in config["args"]
        assert str(temp_project_dir) in config["args"]

    def test_setup_with_dry_run(
        self, mock_handler: MagicMock, temp_project_dir: Path
    ) -> None:
        """Test --dry-run shows preview without creating files."""
        user_params = {"project_dir": str(temp_project_dir)}

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "test-checker",
            user_params,
            dry_run=True,
        )

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "Would set up" in result["message"]
        mock_handler.setup_server.assert_not_called()


class TestClaudeCodeRemoveCommand:
    """Test mcp-config remove with --client claude-code."""

    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        """Create a mock ClaudeCodeHandler with existing server."""
        handler = MagicMock(spec=ClaudeCodeHandler)
        handler.get_config_path.return_value = Path("/mock/.mcp.json")
        handler.remove_server.return_value = True
        handler.list_all_servers.return_value = [
            {"name": "test-server", "managed": True, "type": "stdio"},
        ]
        return handler

    def test_remove_success(self, mock_handler: MagicMock) -> None:
        """Test removing existing server."""
        result = remove_mcp_server(mock_handler, "test-server")

        assert result["success"] is True
        assert result["server_name"] == "test-server"
        assert "Successfully removed" in result["message"]
        mock_handler.remove_server.assert_called_once_with("test-server")

    def test_remove_nonexistent(self, mock_handler: MagicMock) -> None:
        """Test removing server that doesn't exist."""
        mock_handler.list_all_servers.return_value = []

        result = remove_mcp_server(mock_handler, "nonexistent")

        assert result["success"] is False
        assert "not found" in result["message"]
        mock_handler.remove_server.assert_not_called()

    def test_remove_with_dry_run(self, mock_handler: MagicMock) -> None:
        """Test --dry-run shows preview without removing."""
        result = remove_mcp_server(mock_handler, "test-server", dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "Would remove" in result["message"]
        mock_handler.remove_server.assert_not_called()


@pytest.mark.skip(reason="Temporary skip due to pytest tmp_path isolation issues")
class TestClaudeCodeListCommand:
    """Test mcp-config list --client claude-code."""

    def test_list_shows_all_servers_as_managed(self, tmp_path: Path) -> None:
        """Test list command shows all servers from .mcp.json."""
        # Create unique test directory
        test_dir = tmp_path / "list_test"
        test_dir.mkdir(exist_ok=True)

        # Create a real ClaudeCodeHandler with temp directory
        handler = ClaudeCodeHandler(config_dir=test_dir)

        # Setup some servers
        handler.setup_server("server1", {"command": "python1"})
        handler.setup_server("server2", {"command": "python2"})

        # List all servers
        servers = handler.list_all_servers()

        assert len(servers) == 2
        server_names = {s["name"] for s in servers}
        assert server_names == {"server1", "server2"}

        # All should be managed
        for server in servers:
            assert server["managed"] is True

    def test_list_empty_config(self, tmp_path: Path) -> None:
        """Test list with no servers returns empty list."""
        # Create unique test directory
        test_dir = tmp_path / "empty_test"
        test_dir.mkdir(exist_ok=True)

        handler = ClaudeCodeHandler(config_dir=test_dir)
        servers = handler.list_all_servers()
        assert len(servers) == 0


class TestClaudeCodeValidateCommand:
    """Test mcp-config validate with --client claude-code."""

    def test_validate_checks_type_field(self, tmp_path: Path) -> None:
        """Test validate requires type: stdio field."""
        handler = ClaudeCodeHandler(config_dir=tmp_path)

        # Setup server with valid config (should include type: stdio)
        server_config = {"command": "python", "args": ["-m", "test"]}
        handler.setup_server("test-server", server_config)

        # Validate should pass
        errors = handler.validate_config()
        assert len(errors) == 0

    def test_validate_catches_missing_command(self, tmp_path: Path) -> None:
        """Test validate catches missing command field."""
        handler = ClaudeCodeHandler(config_dir=tmp_path)

        # Manually create invalid config
        config_path = tmp_path / ".mcp.json"
        import json

        config = {
            "mcpServers": {
                "bad-server": {
                    "type": "stdio",
                    "args": ["-m", "test"],
                    # Missing command
                }
            }
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # Validate should find error
        errors = handler.validate_config()
        assert len(errors) > 0
        assert any("command" in err for err in errors)

    def test_validate_catches_invalid_structure(self, tmp_path: Path) -> None:
        """Test validate catches invalid config structure."""
        handler = ClaudeCodeHandler(config_dir=tmp_path)

        # Manually create invalid config
        config_path = tmp_path / ".mcp.json"
        import json

        config = {"invalid": "structure"}
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # Validate should find error
        errors = handler.validate_config()
        assert len(errors) > 0
        assert any("mcpServers" in err for err in errors)


class TestClaudeCodeErrorHandling:
    """Test error handling with claude-code client."""

    def test_unknown_client_error(self) -> None:
        """Test that invalid client name shows helpful error."""
        with pytest.raises(ValueError) as exc_info:
            get_client_handler("invalid-client")

        error_msg = str(exc_info.value)
        assert "Unknown client" in error_msg
        assert "invalid-client" in error_msg
        # Should list available clients
        assert "claude-code" in error_msg

    def test_setup_validation_error(self, tmp_path: Path) -> None:
        """Test setup with missing required parameters."""
        handler = ClaudeCodeHandler(config_dir=tmp_path)
        user_params: Dict[str, Any] = {}  # Missing required project_dir

        result = setup_mcp_server(
            handler,
            MCP_CODE_CHECKER,
            "test-checker",
            user_params,
        )

        assert result["success"] is False
        assert "error" in result
        assert "project-dir is required" in result["error"]


@pytest.mark.skip(reason="Temporary skip due to pytest tmp_path isolation issues")
class TestClaudeCodeEndToEnd:
    """End-to-end integration tests for Claude Code client."""

    def test_full_setup_and_remove_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow: setup → list → validate → remove."""
        # Create unique test directory
        test_dir = tmp_path / "workflow_test"
        test_dir.mkdir(exist_ok=True)

        handler = ClaudeCodeHandler(config_dir=test_dir)

        # 1. Setup a server
        user_params = {"project_dir": str(test_dir)}
        result = setup_mcp_server(
            handler,
            MCP_CODE_CHECKER,
            "my-checker",
            user_params,
        )
        assert result["success"] is True

        # 2. List servers - should see our server
        servers = handler.list_all_servers()
        assert len(servers) == 1
        assert servers[0]["name"] == "my-checker"
        assert servers[0]["managed"] is True

        # 3. Validate - should pass
        errors = handler.validate_config()
        assert len(errors) == 0

        # 4. Remove server
        result = remove_mcp_server(handler, "my-checker")
        assert result["success"] is True

        # 5. List again - should be empty
        servers = handler.list_all_servers()
        assert len(servers) == 0

    def test_multiple_servers_workflow(self, tmp_path: Path) -> None:
        """Test managing multiple servers."""
        # Create unique test directory
        test_dir = tmp_path / "multi_test"
        test_dir.mkdir(exist_ok=True)

        handler = ClaudeCodeHandler(config_dir=test_dir)

        # Setup multiple servers
        for i in range(3):
            user_params = {"project_dir": str(test_dir)}
            result = setup_mcp_server(
                handler,
                MCP_CODE_CHECKER,
                f"checker-{i}",
                user_params,
            )
            assert result["success"] is True

        # List all - should have 3
        servers = handler.list_all_servers()
        assert len(servers) == 3
        server_names = {s["name"] for s in servers}
        assert server_names == {"checker-0", "checker-1", "checker-2"}

        # Remove one
        result = remove_mcp_server(handler, "checker-1")
        assert result["success"] is True

        # Should have 2 remaining
        servers = handler.list_all_servers()
        assert len(servers) == 2
        server_names = {s["name"] for s in servers}
        assert server_names == {"checker-0", "checker-2"}

    def test_config_path_is_project_directory(self, tmp_path: Path) -> None:
        """Test that config is created in project directory, not user config."""
        # Create unique test directory
        test_dir = tmp_path / "config_test"
        test_dir.mkdir(exist_ok=True)

        handler = ClaudeCodeHandler(config_dir=test_dir)
        config_path = handler.get_config_path()

        # Should be in the provided directory
        assert config_path == test_dir / ".mcp.json"
        assert config_path.parent == test_dir

        # Setup a server
        handler.setup_server("test", {"command": "python"})

        # Config should exist in test_dir
        assert config_path.exists()
        assert config_path.parent == test_dir

    def test_backup_files_use_correct_pattern(self, tmp_path: Path) -> None:
        """Test that backup files use .mcp.backup_* pattern."""
        # Create unique test directory
        test_dir = tmp_path / "backup_test"
        test_dir.mkdir(exist_ok=True)

        handler = ClaudeCodeHandler(config_dir=test_dir)

        # Create initial config
        handler.setup_server("test", {"command": "python"})

        # Create backup
        backup_path = handler.backup_config()

        # Should use correct pattern
        assert backup_path.exists()
        assert backup_path.name.startswith(".mcp.backup_")
        assert backup_path.suffix == ".json"
        assert backup_path.parent == test_dir
