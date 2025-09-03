"""Test wildcard removal functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.mcp_config.utils import (
    find_matching_servers,
    has_wildcard,
    match_pattern,
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestWildcardPatterns:
    """Test wildcard pattern matching functions."""

    def test_has_wildcard(self) -> None:
        """Test wildcard detection."""
        assert has_wildcard("checker*") is True
        assert has_wildcard("*-dev") is True
        assert has_wildcard("test-?") is True
        assert has_wildcard("server[123]") is True
        assert has_wildcard("normal-name") is False
        assert has_wildcard("my-server") is False

    def test_match_pattern(self) -> None:
        """Test pattern matching."""
        # Asterisk wildcard
        assert match_pattern("checker-main", "checker*") is True
        assert match_pattern("checker", "checker*") is True
        assert match_pattern("test-checker", "checker*") is False

        # Ending wildcard
        assert match_pattern("server-dev", "*-dev") is True
        assert match_pattern("my-dev", "*-dev") is True
        assert match_pattern("development", "*-dev") is False

        # Question mark wildcard
        assert match_pattern("test-1", "test-?") is True
        assert match_pattern("test-a", "test-?") is True
        assert match_pattern("test-12", "test-?") is False

        # Character sets
        assert match_pattern("server1", "server[123]") is True
        assert match_pattern("server2", "server[123]") is True
        assert match_pattern("server4", "server[123]") is False

    def test_find_matching_servers(self) -> None:
        """Test finding servers by pattern."""
        servers = [
            {"name": "checker-main", "type": "mcp-code-checker"},
            {"name": "checker-dev", "type": "mcp-code-checker"},
            {"name": "filesystem-prod", "type": "mcp-server-filesystem"},
            {"name": "test-checker", "type": "mcp-code-checker"},
            {"name": "my-server", "type": "other"},
        ]

        # Pattern with asterisk
        matched = find_matching_servers(servers, "checker*")
        assert len(matched) == 2
        assert all(s["name"].startswith("checker") for s in matched)

        # Pattern with ending wildcard
        matched = find_matching_servers(servers, "*-dev")
        assert len(matched) == 1
        assert matched[0]["name"] == "checker-dev"

        # Pattern matching multiple
        matched = find_matching_servers(servers, "*-*")
        assert len(matched) == 5  # All have dashes

        # Exact match (no wildcards)
        matched = find_matching_servers(servers, "my-server")
        assert len(matched) == 1
        assert matched[0]["name"] == "my-server"

        # No matches
        matched = find_matching_servers(servers, "nonexistent*")
        assert len(matched) == 0


class TestRemoveCommandWithWildcards:
    """Test remove command with wildcard support."""

    @patch("src.mcp_config.main.get_client_handler")
    @patch("src.mcp_config.main.remove_mcp_server")
    def test_remove_single_server(
        self, mock_remove: Mock, mock_get_handler: Mock
    ) -> None:
        """Test removing a single server (no wildcards)."""
        from argparse import Namespace

        from src.mcp_config.main import handle_remove_command

        # Setup mocks
        mock_handler = MagicMock()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_handler.get_config_path.return_value = mock_path
        mock_handler.list_managed_servers.return_value = [
            {
                "name": "my-checker",
                "type": "mcp-code-checker",
                "command": "python",
                "managed": True,
            }
        ]
        mock_get_handler.return_value = mock_handler

        mock_remove.return_value = {"success": True}

        # Test args
        args = Namespace(
            server_name="my-checker",
            client="claude-desktop",
            dry_run=False,
            verbose=False,
            backup=True,
            force=False,
        )

        # Run command
        result = handle_remove_command(args)

        # Verify
        assert result == 0
        mock_remove.assert_called_once()
        assert mock_remove.call_args[1]["server_name"] == "my-checker"

    @patch("src.mcp_config.main.get_client_handler")
    @patch("src.mcp_config.main.remove_mcp_server")
    @patch("builtins.input")
    def test_remove_wildcard_with_confirmation(
        self, mock_input: Mock, mock_remove: Mock, mock_get_handler: Mock
    ) -> None:
        """Test removing multiple servers with wildcard and confirmation."""
        from argparse import Namespace

        from src.mcp_config.main import handle_remove_command

        # Setup mocks
        mock_handler = MagicMock()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_handler.get_config_path.return_value = mock_path
        mock_handler.list_managed_servers.return_value = [
            {
                "name": "checker-main",
                "type": "mcp-code-checker",
                "command": "python",
                "managed": True,
            },
            {
                "name": "checker-dev",
                "type": "mcp-code-checker",
                "command": "python",
                "managed": True,
            },
            {
                "name": "other-server",
                "type": "other",
                "command": "python",
                "managed": True,
            },
        ]
        mock_get_handler.return_value = mock_handler

        mock_remove.return_value = {"success": True}
        mock_input.return_value = "y"  # Confirm removal

        # Test args - need to simulate --client being in sys.argv
        args = Namespace(
            server_name="checker*",
            client="claude-desktop",
            dry_run=False,
            verbose=False,
            backup=True,
            force=False,
        )

        # Temporarily modify sys.argv to include --client
        original_argv = sys.argv
        try:
            sys.argv = [
                "mcp-config",
                "remove",
                "checker*",
                "--client",
                "claude-desktop",
            ]
            result = handle_remove_command(args)
        finally:
            sys.argv = original_argv

        # Verify
        assert result == 0
        assert mock_remove.call_count == 2  # Should remove 2 servers
        removed_names = [call[1]["server_name"] for call in mock_remove.call_args_list]
        assert "checker-main" in removed_names
        assert "checker-dev" in removed_names
        assert "other-server" not in removed_names

    @patch("src.mcp_config.main.get_client_handler")
    @patch("src.mcp_config.main.remove_mcp_server")
    def test_remove_wildcard_with_force(
        self, mock_remove: Mock, mock_get_handler: Mock
    ) -> None:
        """Test removing multiple servers with wildcard and --force flag."""
        from argparse import Namespace

        from src.mcp_config.main import handle_remove_command

        # Setup mocks
        mock_handler = MagicMock()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_handler.get_config_path.return_value = mock_path
        mock_handler.list_managed_servers.return_value = [
            {"name": "test-1", "type": "test", "command": "python", "managed": True},
            {"name": "test-2", "type": "test", "command": "python", "managed": True},
            {"name": "prod-1", "type": "test", "command": "python", "managed": True},
        ]
        mock_get_handler.return_value = mock_handler

        mock_remove.return_value = {"success": True}

        # Test args with force flag
        args = Namespace(
            server_name="test-*",
            client="claude-desktop",
            dry_run=False,
            verbose=False,
            backup=True,
            force=True,  # Skip confirmation
        )

        # Temporarily modify sys.argv to include --client
        original_argv = sys.argv
        try:
            sys.argv = [
                "mcp-config",
                "remove",
                "test-*",
                "--client",
                "claude-desktop",
                "--force",
            ]
            result = handle_remove_command(args)
        finally:
            sys.argv = original_argv

        # Verify - no input() should be called due to --force
        assert result == 0
        assert mock_remove.call_count == 2  # Should remove 2 servers
        removed_names = [call[1]["server_name"] for call in mock_remove.call_args_list]
        assert "test-1" in removed_names
        assert "test-2" in removed_names
        assert "prod-1" not in removed_names

    def test_wildcard_requires_explicit_client(self) -> None:
        """Test that wildcard removal requires explicit --client flag."""
        from argparse import Namespace

        from src.mcp_config.main import handle_remove_command

        # Test args without --client in sys.argv
        args = Namespace(
            server_name="checker*",
            client="claude-desktop",  # Default value
            dry_run=False,
            verbose=False,
            backup=True,
            force=False,
        )

        # Simulate command line without --client flag
        original_argv = sys.argv
        try:
            sys.argv = ["mcp-config", "remove", "checker*"]
            result = handle_remove_command(args)
        finally:
            sys.argv = original_argv

        # Should fail with error about requiring --client
        assert result == 1

    @patch("src.mcp_config.main.get_client_handler")
    def test_wildcard_with_dry_run(self, mock_get_handler: Mock) -> None:
        """Test wildcard removal with --dry-run flag."""
        from argparse import Namespace

        from src.mcp_config.main import handle_remove_command

        # Setup mocks
        mock_handler = MagicMock()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_handler.get_config_path.return_value = mock_path
        mock_handler.list_managed_servers.return_value = [
            {"name": "dev-1", "type": "test", "command": "python", "managed": True},
            {"name": "dev-2", "type": "test", "command": "python", "managed": True},
            {"name": "prod", "type": "test", "command": "python", "managed": True},
        ]
        mock_handler.list_all_servers.return_value = (
            mock_handler.list_managed_servers.return_value
        )
        mock_get_handler.return_value = mock_handler

        # Test args with dry-run
        args = Namespace(
            server_name="dev-*",
            client="claude-desktop",
            dry_run=True,  # Dry run mode
            verbose=False,
            backup=True,
            force=False,
        )

        # Temporarily modify sys.argv to include --client
        original_argv = sys.argv
        try:
            sys.argv = [
                "mcp-config",
                "remove",
                "dev-*",
                "--client",
                "claude-desktop",
                "--dry-run",
            ]
            result = handle_remove_command(args)
        finally:
            sys.argv = original_argv

        # Should succeed without actually removing anything
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
