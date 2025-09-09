"""Basic CLI integration tests for IntelliJ client support (Step 4C).

Tests verify that CLI setup/remove commands work with the IntelliJ client.
Focus on happy path testing - edge cases will be handled later.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.cli_utils import SUPPORTED_CLIENTS, parse_and_validate_args
from src.mcp_config.main import (
    handle_list_command,
    handle_remove_command,
    handle_setup_command,
)


class TestIntelliJCLIBasic:
    """Basic IntelliJ CLI integration tests (Step 4C)."""

    def test_intellij_in_supported_clients(self) -> None:
        """Test that intellij is included in supported clients."""
        assert "intellij" in SUPPORTED_CLIENTS

    def test_intellij_cli_argument_parsing(self) -> None:
        """Test that CLI properly parses --client intellij argument."""
        # Test setup command with intellij client
        args, errors = parse_and_validate_args(
            [
                "setup",
                "mcp-code-checker",
                "test-server",
                "--project-dir",
                ".",
                "--client",
                "intellij",
            ]
        )

        assert len(errors) == 0
        assert args.command == "setup"
        assert args.client == "intellij"
        assert args.server_name == "test-server"
        assert args.server_type == "mcp-code-checker"

        # Test remove command with intellij client
        args, errors = parse_and_validate_args(
            ["remove", "test-server", "--client", "intellij"]
        )

        assert len(errors) == 0
        assert args.command == "remove"
        assert args.client == "intellij"
        assert args.server_name == "test-server"

        # Test list command with intellij client
        args, errors = parse_and_validate_args(["list", "--client", "intellij"])

        assert len(errors) == 0
        assert args.command == "list"
        assert args.client == "intellij"

    @patch("src.mcp_config.main.get_client_handler")
    @patch("src.mcp_config.main.registry")
    @patch("src.mcp_config.main.detect_python_environment")
    @patch("src.mcp_config.main.validate_required_parameters")
    @patch("src.mcp_config.main.validate_parameter_combination")
    @patch("src.mcp_config.main.validate_setup_args")
    @patch("src.mcp_config.main.setup_mcp_server")
    def test_intellij_setup_command_basic(
        self,
        mock_setup: MagicMock,
        mock_validate_setup: MagicMock,
        mock_validate_combo: MagicMock,
        mock_validate: MagicMock,
        mock_detect: MagicMock,
        mock_registry: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test that setup command works with intellij client."""
        # Setup mocks for successful operation
        mock_config = MagicMock()
        mock_config.name = "mcp-code-checker"
        mock_config.parameters = []
        mock_registry.get.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get_config_path.return_value = Path("/mock/config.json")
        mock_get_client.return_value = mock_client

        mock_detect.return_value = (Path("/usr/bin/python"), None)
        mock_validate.return_value = []
        mock_validate_combo.return_value = []
        mock_validate_setup.return_value = []
        mock_setup.return_value = {"success": True, "backup_path": "/backup"}

        # Parse arguments for intellij setup
        args, errors = parse_and_validate_args(
            [
                "setup",
                "mcp-code-checker",
                "test-server",
                "--project-dir",
                ".",
                "--client",
                "intellij",
            ]
        )

        assert len(errors) == 0

        # Execute setup command
        result = handle_setup_command(args)

        # Verify successful execution
        assert result == 0
        mock_get_client.assert_called_once_with("intellij")
        mock_setup.assert_called_once()

        # Verify setup was called with correct arguments (keyword arguments)
        setup_call_args = mock_setup.call_args
        assert setup_call_args is not None
        # Check that client_handler keyword argument is correct
        assert "client_handler" in setup_call_args.kwargs
        assert setup_call_args.kwargs["client_handler"] == mock_client

    @patch("src.mcp_config.main.get_client_handler")
    @patch("src.mcp_config.main.remove_mcp_server")
    def test_intellij_remove_command_basic(
        self,
        mock_remove: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test that remove command works with intellij client."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.list_managed_servers.return_value = [
            {
                "name": "test-server",
                "type": "mcp-code-checker",
                "command": "python",
                "managed": True,
            }
        ]
        mock_get_client.return_value = mock_client
        mock_remove.return_value = {"success": True, "backup_path": "/backup"}

        # Parse arguments for intellij remove
        args, errors = parse_and_validate_args(
            ["remove", "test-server", "--client", "intellij"]
        )

        assert len(errors) == 0

        # Execute remove command
        result = handle_remove_command(args)

        # Verify successful execution
        assert result == 0
        # get_client_handler is called multiple times in remove command
        assert mock_get_client.call_count >= 1
        mock_get_client.assert_any_call("intellij")
        mock_remove.assert_called_once()

    @patch("src.mcp_config.main.get_client_handler")
    def test_intellij_list_command_basic(
        self,
        mock_get_client: MagicMock,
    ) -> None:
        """Test that list command works with intellij client."""
        # Setup mocks
        mock_client = MagicMock()
        mock_config_path = MagicMock()
        mock_config_path.exists.return_value = True  # Config file exists
        mock_client.get_config_path.return_value = mock_config_path
        mock_client.list_all_servers.return_value = [
            {
                "name": "server1",
                "type": "mcp-code-checker",
                "command": "python",
                "managed": True,
            },
            {
                "name": "server2",
                "type": "custom-server",
                "command": "node",
                "managed": False,
            },
        ]
        mock_get_client.return_value = mock_client

        # Parse arguments for intellij list
        args, errors = parse_and_validate_args(["list", "--client", "intellij"])

        assert len(errors) == 0

        # Execute list command
        result = handle_list_command(args)

        # Verify successful execution
        assert result == 0
        mock_get_client.assert_called_once_with("intellij")
        mock_client.list_all_servers.assert_called_once()

    def test_intellij_help_text_includes_client(self) -> None:
        """Test that help text mentions intellij client support."""
        from src.mcp_config.cli_utils import create_full_parser

        parser = create_full_parser()
        help_text = parser.format_help()

        # Should mention intellij in client choices
        assert "intellij" in help_text
        # Should mention GitHub Copilot
        assert "GitHub Copilot" in help_text

    @patch("src.mcp_config.main.get_client_handler")
    def test_intellij_dry_run_setup(
        self,
        mock_get_client: MagicMock,
    ) -> None:
        """Test that dry-run works with intellij client."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.get_config_path.return_value = Path("/mock/config.json")
        mock_get_client.return_value = mock_client

        with (
            patch("src.mcp_config.main.registry") as mock_registry,
            patch("src.mcp_config.main.detect_python_environment") as mock_detect,
            patch("src.mcp_config.main.validate_required_parameters") as mock_validate,
            patch(
                "src.mcp_config.main.validate_parameter_combination"
            ) as mock_validate_combo,
            patch("src.mcp_config.main.validate_setup_args") as mock_validate_setup,
            patch("src.mcp_config.main.build_server_config") as mock_build_config,
        ):

            # Setup mocks for successful dry-run
            mock_config = MagicMock()
            mock_config.name = "mcp-code-checker"
            mock_config.parameters = []
            mock_registry.get.return_value = mock_config

            mock_detect.return_value = (Path("/usr/bin/python"), None)
            mock_validate.return_value = []
            mock_validate_combo.return_value = []
            mock_validate_setup.return_value = []
            mock_build_config.return_value = {
                "command": "/usr/bin/python",
                "args": ["--project-dir", "/test"],
                "_managed_by": "mcp-config-managed",
                "_server_type": "mcp-code-checker",
            }

            # Parse arguments for intellij dry-run setup
            args, errors = parse_and_validate_args(
                [
                    "setup",
                    "mcp-code-checker",
                    "test-server",
                    "--project-dir",
                    ".",
                    "--client",
                    "intellij",
                    "--dry-run",
                ]
            )

            assert len(errors) == 0
            assert args.dry_run is True

            # Execute setup command in dry-run mode
            result = handle_setup_command(args)

            # Verify successful execution
            assert result == 0
            mock_get_client.assert_called_once_with("intellij")
            # In dry-run mode, actual setup should not be called
            mock_build_config.assert_called_once()

    def test_intellij_validation_errors_handled(self) -> None:
        """Test that validation errors are properly handled for intellij client."""
        # Test missing required parameter - argparse will raise SystemExit
        with pytest.raises(SystemExit):
            parse_and_validate_args(
                [
                    "setup",
                    "mcp-code-checker",
                    "test-server",
                    "--client",
                    "intellij",
                    # Missing required --project-dir
                ]
            )

        # Test that with valid args, there are no validation errors
        args, errors = parse_and_validate_args(
            [
                "setup",
                "mcp-code-checker",
                "test-server",
                "--client",
                "intellij",
                "--project-dir",
                ".",
            ]
        )
        assert len(errors) == 0

    def test_intellij_with_all_global_options(self) -> None:
        """Test intellij client with all global CLI options."""
        # Test with verbose, no-backup, etc.
        args, errors = parse_and_validate_args(
            [
                "setup",
                "mcp-code-checker",
                "test-server",
                "--project-dir",
                ".",
                "--client",
                "intellij",
                "--dry-run",
                "--verbose",
                "--no-backup",
            ]
        )

        assert len(errors) == 0
        assert args.client == "intellij"
        assert args.dry_run is True
        assert args.verbose is True
        assert args.backup is False

    def test_intellij_remove_with_wildcards(self) -> None:
        """Test intellij remove command supports wildcards."""
        # Test wildcard removal (basic argument parsing)
        args, errors = parse_and_validate_args(
            ["remove", "test-*", "--client", "intellij", "--force"]
        )

        assert len(errors) == 0
        assert args.client == "intellij"
        assert args.server_name == "test-*"
        assert args.force is True

    def test_intellij_list_with_options(self) -> None:
        """Test intellij list command with various options."""
        # Test list with detailed output
        args, errors = parse_and_validate_args(
            ["list", "--client", "intellij", "--detailed", "--managed-only"]
        )

        assert len(errors) == 0
        assert args.client == "intellij"
        assert args.detailed is True
        assert args.managed_only is True


class TestIntelliJCLIIntegrationEnd2End:
    """End-to-end integration tests for IntelliJ CLI (happy path only)."""

    @patch("src.mcp_config.clients.intellij.IntelliJHandler.get_config_path")
    @patch("src.mcp_config.main.detect_python_environment")
    def test_intellij_full_setup_workflow(
        self,
        mock_detect: MagicMock,
        mock_get_config_path: MagicMock,
    ) -> None:
        """Test complete setup workflow with real file operations."""
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp.json"
            mock_get_config_path.return_value = config_path
            mock_detect.return_value = (Path("/usr/bin/python"), None)

            # Parse setup arguments
            args, errors = parse_and_validate_args(
                [
                    "setup",
                    "mcp-code-checker",
                    "test-server",
                    "--project-dir",
                    temp_dir,
                    "--client",
                    "intellij",
                ]
            )

            assert len(errors) == 0

            # Execute setup command
            result = handle_setup_command(args)

            # Should succeed
            assert result == 0

            # Config file should be created
            assert config_path.exists()

            # Should contain proper JSON structure
            import json

            with open(config_path, "r") as f:
                config = json.load(f)

            assert "servers" in config
            assert "test-server" in config["servers"]

            server = config["servers"]["test-server"]
            assert "command" in server
            assert "args" in server
            # Metadata should NOT be in main config
            assert "_managed_by" not in server
            assert "_server_type" not in server

    @patch("src.mcp_config.clients.intellij.IntelliJHandler.get_config_path")
    def test_intellij_remove_after_setup(
        self,
        mock_get_config_path: MagicMock,
    ) -> None:
        """Test removing a server after setting it up."""
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp.json"
            mock_get_config_path.return_value = config_path

            # Setup a server first (simplified setup)
            from src.mcp_config.clients import get_client_handler

            handler = get_client_handler("intellij")

            server_config = {
                "command": "python",
                "args": ["-m", "test_server"],
                "_server_type": "test-server",
            }

            success = handler.setup_server("test-server", server_config)
            assert success

            # Verify it was created
            servers = handler.list_all_servers()
            server_names = [s["name"] for s in servers]
            assert "test-server" in server_names

            # Now test remove command
            args, errors = parse_and_validate_args(
                ["remove", "test-server", "--client", "intellij"]
            )

            assert len(errors) == 0

            # Execute remove command
            result = handle_remove_command(args)
            assert result == 0

            # Verify server was removed
            servers = handler.list_all_servers()
            server_names = [s["name"] for s in servers]
            assert "test-server" not in server_names

    @patch("src.mcp_config.clients.intellij.IntelliJHandler.get_config_path")
    def test_intellij_list_after_setup(
        self,
        mock_get_config_path: MagicMock,
    ) -> None:
        """Test listing servers after setting them up."""
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp.json"
            mock_get_config_path.return_value = config_path

            # Setup multiple servers
            from src.mcp_config.clients import get_client_handler

            handler = get_client_handler("intellij")

            server1_config = {
                "command": "python",
                "args": ["-m", "server1"],
                "_server_type": "mcp-code-checker",
            }

            server2_config = {
                "command": "node",
                "args": ["server2.js"],
                "_server_type": "custom-server",
            }

            handler.setup_server("server1", server1_config)
            handler.setup_server("server2", server2_config)

            # Test list command
            args, errors = parse_and_validate_args(["list", "--client", "intellij"])

            assert len(errors) == 0

            # Execute list command
            result = handle_list_command(args)
            assert result == 0

            # Verify servers are listed
            servers = handler.list_all_servers()
            server_names = [s["name"] for s in servers]
            assert "server1" in server_names
            assert "server2" in server_names


class TestIntelliJCLIErrorHandling:
    """Test basic error handling for IntelliJ CLI (minimal coverage)."""

    def test_invalid_client_name(self) -> None:
        """Test error handling for invalid client name."""
        with pytest.raises(SystemExit):
            parse_and_validate_args(
                [
                    "setup",
                    "mcp-code-checker",
                    "test-server",
                    "--project-dir",
                    ".",
                    "--client",
                    "invalid-client",
                ]
            )

    def test_intellij_missing_server_name(self) -> None:
        """Test error handling for missing server name in remove."""
        args, errors = parse_and_validate_args(["remove", "", "--client", "intellij"])

        # Should have validation errors
        assert len(errors) > 0
        assert any("Server name is required" in error for error in errors)

    @patch("src.mcp_config.main.get_client_handler")
    def test_intellij_client_handler_error(
        self,
        mock_get_client: MagicMock,
    ) -> None:
        """Test error handling when client handler fails."""
        # Mock client handler to raise error
        mock_get_client.side_effect = Exception("IntelliJ not found")

        args, errors = parse_and_validate_args(["list", "--client", "intellij"])

        assert len(errors) == 0

        # Execute should handle the error gracefully and print error message
        result = handle_list_command(args)
        # For specific client requests, list command shows error but returns 0
        assert result == 0


# Test Configuration
pytest_plugins: list[str] = []  # No additional plugins needed for basic tests
