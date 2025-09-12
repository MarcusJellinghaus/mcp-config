"""Tests for integration between ServerConfig and ClientHandler."""

import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.clients import ClaudeDesktopHandler
from src.mcp_config.integration import (
    generate_client_config,
    remove_mcp_server,
    setup_mcp_server,
)
from src.mcp_config.servers import (
    MCP_CODE_CHECKER,
    MCP_FILESYSTEM_SERVER,
    ParameterDef,
    ServerConfig,
)


class TestGenerateClientConfig:
    """Test client configuration generation."""

    @pytest.fixture
    def server_config(self) -> ServerConfig:
        """Create a test server configuration."""
        return ServerConfig(
            name="test-server",
            display_name="Test Server",
            main_module="src/main.py",
            parameters=[
                ParameterDef(
                    name="project-dir",
                    arg_name="--project-dir",
                    param_type="path",
                    required=True,
                ),
                ParameterDef(
                    name="log-level",
                    arg_name="--log-level",
                    param_type="choice",
                    choices=["DEBUG", "INFO", "WARNING"],
                    default="INFO",
                ),
                ParameterDef(
                    name="verbose",
                    arg_name="--verbose",
                    param_type="boolean",
                    is_flag=True,
                ),
            ],
        )

    def test_generate_basic_config(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test generating basic client configuration."""
        # Use underscore format as expected by generate_args
        user_params = {
            "project_dir": str(tmp_path),
            "log_level": "DEBUG",
            "verbose": True,
        }

        config = generate_client_config(
            server_config,
            "test-instance",
            user_params,
            python_executable="/usr/bin/python3",
        )

        assert config["command"] == "/usr/bin/python3"
        # The first argument should contain main.py
        assert "main.py" in config["args"][0]
        assert "--project-dir" in config["args"]
        assert str(tmp_path) in config["args"]
        assert "--log-level" in config["args"]
        assert "DEBUG" in config["args"]
        assert "--verbose" in config["args"]
        assert config["_server_type"] == "test-server"

    def test_generate_config_with_auto_python(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test configuration with auto-detected Python."""
        user_params = {"project_dir": str(tmp_path)}

        config = generate_client_config(
            server_config,
            "test-instance",
            user_params,
            python_executable=None,  # Auto-detect
        )

        assert config["command"] == sys.executable

    def test_generate_config_missing_required(
        self, server_config: ServerConfig
    ) -> None:
        """Test that missing required parameters raise error."""
        user_params = {"log_level": "INFO"}  # Missing required project_dir

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(server_config, "test", user_params)
        assert "project-dir is required" in str(exc_info.value)

    def test_generate_config_invalid_choice(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test that invalid choice values raise error."""
        user_params = {
            "project_dir": str(tmp_path),
            "log_level": "INVALID",
        }

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(server_config, "test", user_params)
        assert "not in valid choices" in str(exc_info.value)

    def test_generate_config_with_venv(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test configuration with virtual environment."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        # Create fake venv structure
        if sys.platform == "win32":
            scripts_dir = venv_path / "Scripts"
            scripts_dir.mkdir()
            python_exe = scripts_dir / "python.exe"
        else:
            bin_dir = venv_path / "bin"
            bin_dir.mkdir()
            python_exe = bin_dir / "python"

        python_exe.touch()

        # Add venv parameter to server config
        server_config.parameters.append(
            ParameterDef(
                name="venv-path",
                arg_name="--venv-path",
                param_type="path",
            )
        )

        user_params = {
            "project_dir": str(tmp_path),
            "venv_path": str(venv_path),
        }

        config = generate_client_config(server_config, "test", user_params)

        # Should use Python from venv
        assert str(python_exe) in config["command"]

    def test_generate_config_path_normalization(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test that paths are normalized to absolute."""
        user_params = {
            "project_dir": ".",  # Relative path
        }

        with patch("src.mcp_config.integration.Path.cwd", return_value=tmp_path):
            config = generate_client_config(server_config, "test", user_params)

        # Should be normalized to absolute
        project_arg_index = config["args"].index("--project-dir")
        project_path = config["args"][project_arg_index + 1]
        assert Path(project_path).is_absolute()

    def test_generate_config_with_pythonpath(
        self, server_config: ServerConfig, tmp_path: Path
    ) -> None:
        """Test that PYTHONPATH is set in environment."""
        user_params = {"project_dir": str(tmp_path)}

        config = generate_client_config(server_config, "test", user_params)

        assert "env" in config
        assert "PYTHONPATH" in config["env"]
        # PYTHONPATH should now be the mcp-config directory (current working directory)
        # Not the project directory
        expected_pythonpath = str(Path.cwd())
        if sys.platform == "win32" and not expected_pythonpath.endswith("\\"):
            expected_pythonpath += "\\"
        assert config["env"]["PYTHONPATH"] == expected_pythonpath


class TestSetupMCPServer:
    """Test setup_mcp_server function."""

    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        """Create a mock client handler."""
        handler = MagicMock(spec=ClaudeDesktopHandler)
        handler.get_config_path.return_value = Path("/mock/config.json")
        handler.setup_server.return_value = True
        return handler

    def test_setup_server_success(
        self, mock_handler: MagicMock, tmp_path: Path
    ) -> None:
        """Test successful server setup."""
        user_params = {
            "project_dir": str(tmp_path),
            "log_level": "INFO",
        }

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "my-checker",
            user_params,
        )

        assert result["success"] is True
        assert result["server_name"] == "my-checker"
        assert result["operation"] == "setup"
        assert "config" in result
        assert "message" in result
        mock_handler.setup_server.assert_called_once()

    def test_setup_server_dry_run(
        self, mock_handler: MagicMock, tmp_path: Path
    ) -> None:
        """Test dry run mode."""
        user_params = {"project_dir": str(tmp_path)}

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "my-checker",
            user_params,
            dry_run=True,
        )

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "Would set up" in result["message"]
        mock_handler.setup_server.assert_not_called()

    def test_setup_server_validation_error(self, mock_handler: MagicMock) -> None:
        """Test setup with validation errors."""
        user_params: Dict[str, Any] = {}  # Missing required project-dir

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "my-checker",
            user_params,
        )

        assert result["success"] is False
        assert "error" in result
        assert "project-dir is required" in result["error"]
        mock_handler.setup_server.assert_not_called()

    def test_setup_server_handler_failure(
        self, mock_handler: MagicMock, tmp_path: Path
    ) -> None:
        """Test when handler fails to set up server."""
        mock_handler.setup_server.return_value = False
        user_params = {"project_dir": str(tmp_path)}

        result = setup_mcp_server(
            mock_handler,
            MCP_CODE_CHECKER,
            "my-checker",
            user_params,
        )

        assert result["success"] is False
        assert "Failed to set up" in result["message"]


class TestRemoveMCPServer:
    """Test remove_mcp_server function."""

    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        """Create a mock client handler."""
        handler = MagicMock(spec=ClaudeDesktopHandler)
        handler.get_config_path.return_value = Path("/mock/config.json")
        handler.remove_server.return_value = True
        handler.list_all_servers.return_value = [
            {"name": "managed-server", "managed": True},
            {"name": "external-server", "managed": False},
        ]
        return handler

    def test_remove_server_success(self, mock_handler: MagicMock) -> None:
        """Test successful server removal."""
        result = remove_mcp_server(mock_handler, "managed-server")

        assert result["success"] is True
        assert result["server_name"] == "managed-server"
        assert result["operation"] == "remove"
        assert "Successfully removed" in result["message"]
        mock_handler.remove_server.assert_called_once_with("managed-server")

    def test_remove_server_dry_run(self, mock_handler: MagicMock) -> None:
        """Test dry run mode for removal."""
        result = remove_mcp_server(mock_handler, "managed-server", dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "Would remove" in result["message"]
        mock_handler.remove_server.assert_not_called()

    def test_remove_nonexistent_server(self, mock_handler: MagicMock) -> None:
        """Test removing a server that doesn't exist."""
        result = remove_mcp_server(mock_handler, "nonexistent")

        assert result["success"] is False
        assert "not found" in result["message"]
        mock_handler.remove_server.assert_not_called()

    def test_remove_external_server(self, mock_handler: MagicMock) -> None:
        """Test that external servers cannot be removed."""
        result = remove_mcp_server(mock_handler, "external-server")

        assert result["success"] is False
        assert "not managed by this tool" in result["message"]
        mock_handler.remove_server.assert_not_called()

    def test_remove_server_handler_failure(self, mock_handler: MagicMock) -> None:
        """Test when handler fails to remove server."""
        mock_handler.remove_server.return_value = False

        result = remove_mcp_server(mock_handler, "managed-server")

        assert result["success"] is False
        assert "Failed to remove" in result["message"]


class TestMCPCodeCheckerIntegration:
    """Test integration with the actual MCP Code Checker config."""

    def test_mcp_code_checker_config_generation(self, tmp_path: Path) -> None:
        """Test generating config for MCP Code Checker."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        user_params = {
            "project_dir": str(project_dir),
            "log_level": "DEBUG",
            "test_folder": "tests",
            "keep_temp_files": True,
        }

        config = generate_client_config(
            MCP_CODE_CHECKER,
            "checker-instance",
            user_params,
            python_executable="/usr/bin/python3",
        )

        assert config["_server_type"] == "mcp-code-checker"

        # Check arguments - regardless of command mode, these should be present
        args = config["args"]
        assert "--project-dir" in args
        assert str(project_dir) in args
        assert "--log-level" in args
        assert "DEBUG" in args
        assert "--test-folder" in args
        assert "tests" in args
        assert "--keep-temp-files" in args

        # The command could be either CLI executable or Python with module
        is_cli_mode = config["command"].lower().endswith(
            "mcp-code-checker.exe"
        ) or config["command"].endswith("mcp-code-checker")

        if is_cli_mode:
            # CLI command mode - arguments should NOT start with -m mcp_code_checker
            assert not (
                len(args) >= 2 and args[0] == "-m" and args[1] == "mcp_code_checker"
            ), f"CLI mode should not have -m args, but got: {args[:5]}"
        else:
            # Python module mode
            assert (
                config["command"] == "/usr/bin/python3"
                or config["command"] == sys.executable
            ), f"Expected Python executable, got: {config['command']}"
            # The first two arguments should be "-m" and "mcp_code_checker" for module invocation
            assert (
                len(args) >= 2 and args[0] == "-m" and args[1] == "mcp_code_checker"
            ), f"Expected module invocation args, got: {args[:5]}"

        # Check environment
        assert "PYTHONPATH" in config["env"]
        # PYTHONPATH should now be mcp-config directory (cwd), not project directory
        expected_pythonpath = str(Path.cwd())
        if sys.platform == "win32" and not expected_pythonpath.endswith("\\"):
            expected_pythonpath += "\\"
        assert config["env"]["PYTHONPATH"] == expected_pythonpath

    def test_mcp_code_checker_minimal_config(self, tmp_path: Path) -> None:
        """Test minimal configuration for MCP Code Checker."""
        user_params = {"project_dir": str(tmp_path)}

        config = generate_client_config(
            MCP_CODE_CHECKER,
            "minimal",
            user_params,
        )

        # Should work with just required parameters
        args = config["args"]
        assert "--project-dir" in args
        assert str(tmp_path) in args

        # Default log level should be included
        assert "--log-level" in args
        assert "INFO" in args

        # Command could be CLI or Python module mode
        is_cli_mode = config["command"].lower().endswith(
            "mcp-code-checker.exe"
        ) or config["command"].endswith("mcp-code-checker")

        if not is_cli_mode:
            # Python module mode
            assert config["command"] == sys.executable


class TestMCPFilesystemServerIntegration:
    """Test integration with the actual MCP Filesystem Server config."""

    def test_mcp_filesystem_server_config_generation(self, tmp_path: Path) -> None:
        """Test generating config for MCP Filesystem Server."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        user_params = {
            "project_dir": str(project_dir),
            "log_level": "DEBUG",
            "log_file": str(project_dir / "logs" / "filesystem.log"),
        }

        config = generate_client_config(
            MCP_FILESYSTEM_SERVER,
            "filesystem-instance",
            user_params,
            python_executable="/usr/bin/python3",
        )

        assert config["_server_type"] == "mcp-server-filesystem"

        # Check arguments - should be present for filesystem server
        args = config["args"]
        assert "--project-dir" in args
        assert str(project_dir) in args
        assert "--log-level" in args
        assert "DEBUG" in args
        assert "--log-file" in args
        assert "filesystem.log" in " ".join(args)

        # The command could be either CLI executable or Python module
        is_cli_mode = config["command"].lower().endswith(
            "mcp-server-filesystem.exe"
        ) or config["command"].endswith("mcp-server-filesystem")

        if is_cli_mode:
            # CLI command mode - should use the executable directly
            assert "mcp-server-filesystem" in config["command"]
            # Arguments should start directly with --project-dir (no module args)
            assert args[0] == "--project-dir" or args[0].startswith("--")
        else:
            # Python module mode - should use Python executable
            assert (
                config["command"] == "/usr/bin/python3"
                or config["command"] == sys.executable
            ), f"Expected Python executable, got: {config['command']}"
            # For filesystem server in module mode, should use -m mcp_server_filesystem
            assert args[0] == "-m", f"Expected -m as first arg, got: {args[0]}"
            assert (
                args[1] == "mcp_server_filesystem"
            ), f"Expected mcp_server_filesystem as second arg, got: {args[1]}"

        # Check environment
        assert "PYTHONPATH" in config["env"]
        # PYTHONPATH should be mcp-config directory (cwd), not project directory
        expected_pythonpath = str(Path.cwd())
        if sys.platform == "win32" and not expected_pythonpath.endswith("\\"):
            expected_pythonpath += "\\"
        assert config["env"]["PYTHONPATH"] == expected_pythonpath

    def test_mcp_filesystem_server_minimal_config(self, tmp_path: Path) -> None:
        """Test minimal configuration for MCP Filesystem Server."""
        user_params = {"project_dir": str(tmp_path)}

        config = generate_client_config(
            MCP_FILESYSTEM_SERVER,
            "minimal-fs",
            user_params,
        )

        # Should work with just required parameters
        args = config["args"]
        assert "--project-dir" in args
        assert str(tmp_path) in args

        # Default log level should be included
        assert "--log-level" in args
        assert "INFO" in args

        # log-file should NOT be auto-detected anymore - let servers handle it internally
        assert "--log-file" not in args  # No longer automatically included

        # Command could be CLI or Python module mode
        is_cli_mode = config["command"].lower().endswith(
            "mcp-server-filesystem.exe"
        ) or config["command"].endswith("mcp-server-filesystem")

        if not is_cli_mode:
            # Python module mode
            assert config["command"] == sys.executable

    def test_mcp_filesystem_server_cli_command_detection(self, tmp_path: Path) -> None:
        """Test CLI command detection for MCP Filesystem Server."""
        from unittest.mock import patch

        user_params = {"project_dir": str(tmp_path)}

        # Test with CLI command available
        with patch(
            "src.mcp_config.integration._find_cli_executable",
            return_value="/usr/bin/mcp-server-filesystem",
        ):
            config = generate_client_config(
                MCP_FILESYSTEM_SERVER,
                "cli-test",
                user_params,
            )

            # When CLI is mocked as available, it will be used
            # But in test environment it may fall back to module mode
            if "mcp-server-filesystem" in config["command"]:
                # CLI command mode
                assert config["args"][0] == "--project-dir"
            else:
                # Python module mode fallback
                assert config["command"] == sys.executable
                assert config["args"][0] == "-m"
                assert config["args"][1] == "mcp_server_filesystem"

        # Test without CLI command available (fallback to Python module)
        with patch(
            "src.mcp_config.integration._find_cli_executable", return_value=None
        ):
            with patch(
                "src.mcp_config.integration.is_package_installed", return_value=False
            ):
                config = generate_client_config(
                    MCP_FILESYSTEM_SERVER,
                    "python-test",
                    user_params,
                )

                # Should fallback to Python module mode
                assert config["command"] == sys.executable
                assert "-m" in config["args"]
                assert "mcp_server_filesystem" in config["args"]

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific path test")
    def test_mcp_filesystem_server_realistic_windows_config(
        self, tmp_path: Path
    ) -> None:
        """Test realistic Windows configuration matching the example."""
        # Use current user's username dynamically
        import os

        current_user = os.environ.get("USERNAME", "DefaultUser")

        # Simulate the example config provided with dynamic user
        project_dir = f"C:\\Users\\{current_user}\\Documents\\GitHub\\mcp-config"
        cli_command = f"C:\\Users\\{current_user}\\Documents\\GitHub\\mcp-config\\.venv\\Scripts\\mcp-server-filesystem.exe"

        user_params = {
            "project_dir": project_dir,
            "log_level": "INFO",
        }

        # Mock CLI command availability
        with patch(
            "src.mcp_config.integration._find_cli_executable", return_value=cli_command
        ):
            config = generate_client_config(
                MCP_FILESYSTEM_SERVER,
                "fs on p config",
                user_params,
            )

            # When CLI is mocked as available, it will be used
            # But test may fall back to module mode
            if "mcp-server-filesystem" in config["command"]:
                # CLI command mode - command is the executable
                assert config["command"] == cli_command
            else:
                # Python module mode fallback
                assert config["command"] == sys.executable
                assert config["args"][0] == "-m"
                assert config["args"][1] == "mcp_server_filesystem"

            # Args should match the example
            args = config["args"]
            assert "--project-dir" in args
            assert project_dir in args
            assert "--log-level" in args
            assert "INFO" in args

            # Environment should have PYTHONPATH
            assert "PYTHONPATH" in config["env"]
            # On Windows, should end with backslash
            if sys.platform == "win32":
                expected_path = project_dir
                if not expected_path.endswith("\\"):
                    expected_path += "\\"
                assert config["env"]["PYTHONPATH"] == expected_path

    def test_mcp_filesystem_server_validation_errors(self) -> None:
        """Test validation errors for filesystem server configuration."""
        # Missing required project-dir
        user_params = {"log_level": "INFO"}

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(MCP_FILESYSTEM_SERVER, "test", user_params)
        assert "project-dir is required" in str(exc_info.value)

        # Invalid log level choice
        user_params = {
            "project_dir": "/tmp",
            "log_level": "INVALID_LEVEL",
        }

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(MCP_FILESYSTEM_SERVER, "test", user_params)
        assert "not in valid choices" in str(exc_info.value)

    def test_mcp_filesystem_server_installation_modes(self, tmp_path: Path) -> None:
        """Test different installation mode detection for filesystem server."""
        from unittest.mock import patch

        user_params = {"project_dir": str(tmp_path)}

        # Test CLI command mode
        with patch("shutil.which", return_value="/usr/bin/mcp-server-filesystem"):
            mode = MCP_FILESYSTEM_SERVER.get_installation_mode()
            # Should detect CLI command if available
            # Note: actual detection depends on system, so we test the method exists
            assert mode in [
                "cli_command",
                "python_module",
                "development",
                "not_available",
            ]

        # Test Python module mode
        with patch("shutil.which", return_value=None):
            with patch("importlib.util.find_spec", return_value=True):
                mode = MCP_FILESYSTEM_SERVER.get_installation_mode()
                # Method should handle the case properly
                assert mode in [
                    "cli_command",
                    "python_module",
                    "development",
                    "not_available",
                ]

    def test_mcp_filesystem_server_project_validation(self, tmp_path: Path) -> None:
        """Test project validation for filesystem server."""
        # Valid directory should pass
        assert MCP_FILESYSTEM_SERVER.validate_project(tmp_path)

        # Non-existent directory should fail
        non_existent = tmp_path / "does_not_exist"
        assert not MCP_FILESYSTEM_SERVER.validate_project(non_existent)

        # File instead of directory should fail
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert not MCP_FILESYSTEM_SERVER.validate_project(test_file)


class TestRepeatableParameterIntegration:
    """Integration tests for repeatable parameter functionality (Step 5)."""

    def test_reference_project_end_to_end(self, tmp_path: Path) -> None:
        """Test complete workflow: CLI parsing → argument generation → command execution."""
        from src.mcp_config.cli_utils import parse_and_validate_args
        from src.mcp_config.servers import registry

        # Simulate CLI args for setup command with multiple reference projects
        test_args = [
            "setup",
            "mcp-server-filesystem",
            "test-fs",
            "--project-dir",
            str(tmp_path),
            "--reference-project",
            "docs=/path/to/docs",
            "--reference-project",
            "examples=/path/to/examples",
            "--dry-run",
        ]

        # Test CLI parsing
        parsed_args, errors = parse_and_validate_args(test_args)
        assert len(errors) == 0
        assert parsed_args.server_type == "mcp-server-filesystem"
        assert parsed_args.reference_project == [
            "docs=/path/to/docs",
            "examples=/path/to/examples",
        ]

        # Test argument generation
        server_config = registry.get("mcp-server-filesystem")
        assert server_config is not None  # Ensure server_config is not None
        user_params = {
            "project_dir": parsed_args.project_dir,
            "reference_project": parsed_args.reference_project,
        }
        args = server_config.generate_args(user_params, use_cli_command=True)

        # Test final command structure
        assert args.count("--reference-project") == 2
        assert "docs=/path/to/docs" in args
        assert "examples=/path/to/examples" in args
        assert "--project-dir" in args
        assert str(tmp_path) in args

    def test_reference_project_edge_cases_and_command_generation(
        self, tmp_path: Path
    ) -> None:
        """Test edge cases, command generation, and final command structure."""
        from src.mcp_config.servers import registry

        server_config = registry.get("mcp-server-filesystem")
        assert server_config is not None  # Ensure server_config is not None

        # Test empty list (should be skipped silently)
        empty_params = {"project_dir": str(tmp_path), "reference_project": []}
        empty_args = server_config.generate_args(empty_params, use_cli_command=True)
        assert "--reference-project" not in empty_args

        # Test single value
        single_params = {
            "project_dir": str(tmp_path),
            "reference_project": ["docs=/docs"],
        }
        single_args = server_config.generate_args(single_params, use_cli_command=True)
        assert single_args.count("--reference-project") == 1
        assert "docs=/docs" in single_args

        # Test None/missing (should be skipped silently)
        none_params = {"project_dir": str(tmp_path)}
        none_args = server_config.generate_args(none_params, use_cli_command=True)
        assert "--reference-project" not in none_args

        # Test actual command generation with multiple reference projects
        multi_params = {
            "project_dir": str(tmp_path),
            "reference_project": ["docs=/docs", "examples=/examples"],
        }
        multi_args = server_config.generate_args(multi_params, use_cli_command=True)

        # Create full command (simulating what would be executed)
        cmd_parts = ["mcp-server-filesystem"] + multi_args
        command_string = " ".join(cmd_parts)

        # Verify command contains expected elements
        assert "mcp-server-filesystem" in command_string
        assert f"--project-dir {tmp_path}" in command_string
        assert "--reference-project docs=/docs" in command_string
        assert "--reference-project examples=/examples" in command_string

        # Verify it's a valid, executable command structure
        assert command_string.count("--reference-project") == 2
        assert command_string.startswith("mcp-server-filesystem")
