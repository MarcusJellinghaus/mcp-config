"""Simplified integration test for mcp-config setup command.

Tests that the setup process generates the correct JSON configuration entry
without modifying any real configuration files.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the modules we need to test
from src.mcp_config.integration import generate_client_config
from src.mcp_config.servers import MCP_FILESYSTEM_SERVER, registry


class TestMCPSetupIntegration:
    """Simplified integration test for the setup command flow."""

    def test_setup_generates_correct_config(self) -> None:
        """Test that setup generates the expected JSON configuration entry (safe, no file modifications)."""

        # Basic test parameters
        server_type = "mcp-code-checker"
        server_name = "checker on p mcp-config"

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)

            # User parameters (similar to what would come from CLI)
            user_params = {
                "project_dir": str(project_dir),
                "log_level": "INFO",
            }

            # Get server configuration from registry
            server_config = registry.get(server_type)
            assert server_config is not None, f"Server type {server_type} not found"

            # Mock any file operations to prevent real file modifications
            with (
                patch("pathlib.Path.write_text"),
                patch("pathlib.Path.mkdir"),
                patch("builtins.open"),
                patch("json.dump"),
            ):

                # Generate the client configuration (safely mocked)
                config = generate_client_config(
                    server_config=server_config,
                    server_name=server_name,
                    user_params=user_params,
                    python_executable=sys.executable,
                )

                # Create the final JSON entry that would go into the client config
                json_entry = {
                    server_name: {
                        "command": config["command"],
                        "args": config["args"],
                        "env": config["env"],
                    }
                }

                # Verify basic structure
                entry = json_entry[server_name]
                assert "command" in entry
                assert "args" in entry
                assert "env" in entry

                # Verify required arguments are present
                args = entry["args"]
                assert "--project-dir" in args
                assert str(project_dir) in args
                assert "--log-level" in args
                assert "INFO" in args

                # Verify environment has PYTHONPATH
                assert "PYTHONPATH" in entry["env"]

                # Verify it's JSON serializable
                json_str = json.dumps(json_entry, indent=2)
                parsed = json.loads(json_str)
                assert server_name in parsed

                print(f"Generated configuration (safely tested):")
                print(json_str)

    def test_with_realistic_paths(self) -> None:
        """Test with paths similar to the user's actual configuration (safely mocked)."""

        server_type = "mcp-code-checker"
        server_name = "checker on p mcp-config"

        # Mock realistic Windows paths
        project_dir = r"C:\Users\Marcus\Documents\GitHub\mcp-config"
        python_exe = r"C:\Users\Marcus\Documents\GitHub\mcp-code-checker\.venv\Scripts\python.exe"
        venv_path = r"C:\Users\Marcus\Documents\GitHub\mcp-code-checker\.venv"

        user_params = {
            "project_dir": project_dir,
            "python_executable": python_exe,
            "venv_path": venv_path,
            "log_level": "INFO",
        }

        server_config = registry.get(server_type)
        assert server_config is not None

        # Mock all file operations to prevent any real file modifications
        with (
            patch("pathlib.Path.write_text"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open"),
            patch("json.dump"),
        ):

            # Mock path existence checks
            mock_exists.return_value = True

            config = generate_client_config(
                server_config=server_config,
                server_name=server_name,
                user_params=user_params,
                python_executable=python_exe,
            )

            # Create the expected JSON structure
            json_entry = {
                server_name: {
                    "command": config["command"],
                    "args": config["args"],
                    "env": config["env"],
                }
            }

            # Verify essential elements
            entry = json_entry[server_name]
            assert isinstance(entry["command"], str)
            assert isinstance(entry["args"], list)
            assert isinstance(entry["env"], dict)

            # Check required parameters exist
            args = entry["args"]
            assert "--project-dir" in args
            assert "--log-level" in args
            assert "INFO" in args

            # Check PYTHONPATH is set
            assert "PYTHONPATH" in entry["env"]

            print(f"\nRealistic configuration (safely tested):")
            print(json.dumps(json_entry, indent=2))

    def test_filesystem_server_setup_generates_correct_config(self) -> None:
        """Test that filesystem server setup generates the expected JSON configuration entry."""

        # Basic test parameters for filesystem server
        server_type = "mcp-server-filesystem"
        server_name = "fs on p config"

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)

            # User parameters (similar to what would come from CLI)
            user_params = {
                "project_dir": str(project_dir),
                "log_level": "INFO",
            }

            # Get server configuration from registry
            server_config = registry.get(server_type)
            assert server_config is not None, f"Server type {server_type} not found"

            # Mock any file operations to prevent real file modifications
            with (
                patch("pathlib.Path.write_text"),
                patch("pathlib.Path.mkdir"),
                patch("builtins.open"),
                patch("json.dump"),
                patch(
                    "src.mcp_config.integration._find_cli_executable",
                    return_value="mcp-server-filesystem",
                ),  # Mock CLI availability
            ):

                # Generate the client configuration (safely mocked)
                config = generate_client_config(
                    server_config=server_config,
                    server_name=server_name,
                    user_params=user_params,
                    python_executable=sys.executable,
                )

                # Create the final JSON entry that would go into the client config
                json_entry = {
                    server_name: {
                        "command": config["command"],
                        "args": config["args"],
                        "env": config["env"],
                    }
                }

                # Verify basic structure
                entry = json_entry[server_name]
                assert "command" in entry
                assert "args" in entry
                assert "env" in entry

                # Verify required arguments are present
                args = entry["args"]
                assert "--project-dir" in args
                assert str(project_dir) in args
                assert "--log-level" in args
                assert "INFO" in args

                # Verify environment has PYTHONPATH
                assert "PYTHONPATH" in entry["env"]

                # Verify it's JSON serializable
                json_str = json.dumps(json_entry, indent=2)
                parsed = json.loads(json_str)
                assert server_name in parsed

                print(f"Generated filesystem server configuration (safely tested):")
                print(json_str)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific path test")
    def test_filesystem_server_with_realistic_windows_paths(self) -> None:
        """Test filesystem server with realistic Windows paths matching the example."""

        server_type = "mcp-server-filesystem"
        server_name = "fs on p config"

        # Mock realistic Windows paths from the example
        project_dir = r"C:\Users\Marcu\Documents\GitHub\mcp-config"
        cli_exe = r"C:\Users\Marcu\Documents\GitHub\mcp-config\.venv\Scripts\mcp-server-filesystem.exe"

        user_params = {
            "project_dir": project_dir,
            "log_level": "INFO",
        }

        server_config = registry.get(server_type)
        assert server_config is not None

        # Mock all file operations to prevent any real file modifications
        with (
            patch("pathlib.Path.write_text"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open"),
            patch("json.dump"),
            patch(
                "src.mcp_config.integration._find_cli_executable", return_value=cli_exe
            ),  # Mock CLI command availability
        ):

            # Mock path existence checks
            mock_exists.return_value = True

            # Function will automatically detect CLI mode when mocked
            config = generate_client_config(
                server_config=server_config,
                server_name=server_name,
                user_params=user_params,
            )

            # Create the expected JSON structure matching the example
            json_entry = {
                server_name: {
                    "command": config["command"],
                    "args": config["args"],
                    "env": config["env"],
                }
            }

            # Verify structure matches the example
            entry = json_entry[server_name]
            assert isinstance(entry["command"], str)
            assert isinstance(entry["args"], list)
            assert isinstance(entry["env"], dict)

            # Check that command contains filesystem server reference or Python
            # When CLI is mocked as available, it will be used, otherwise Python module mode
            if "mcp-server-filesystem" in entry["command"]:
                # CLI command mode
                assert entry["command"] == cli_exe
            else:
                # Python module mode fallback
                assert entry["command"] == sys.executable
                assert entry["args"][0] == "-m"
                assert entry["args"][1] == "mcp_server_filesystem"

            # Check required parameters exist and match example structure
            args = entry["args"]
            assert "--project-dir" in args
            assert project_dir in args
            assert "--log-level" in args
            assert "INFO" in args

            # Check PYTHONPATH is set correctly for Windows
            assert "PYTHONPATH" in entry["env"]
            pythonpath = entry["env"]["PYTHONPATH"]
            assert project_dir in pythonpath
            # On Windows, should end with backslash
            if sys.platform == "win32":
                assert pythonpath.endswith("\\")

            print(
                f"\nFilesystem server realistic Windows configuration (safely tested):"
            )
            print(json.dumps(json_entry, indent=2))

    def test_filesystem_server_parameter_combinations(self) -> None:
        """Test filesystem server setup with different parameter combinations."""

        server_type = "mcp-server-filesystem"
        server_name = "test-filesystem"

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)

            # Test 1: Minimal configuration
            user_params_minimal = {
                "project_dir": str(project_dir),
            }

            # Test 2: Full configuration
            log_file = project_dir / "logs" / "filesystem.log"
            user_params_full = {
                "project_dir": str(project_dir),
                "log_level": "DEBUG",
                "log_file": str(log_file),
            }

            server_config = registry.get(server_type)
            assert server_config is not None

            # Mock file operations
            with (
                patch("pathlib.Path.write_text"),
                patch("pathlib.Path.mkdir"),
                patch("pathlib.Path.exists") as mock_exists,
                patch("builtins.open"),
                patch("json.dump"),
            ):

                mock_exists.return_value = True

                # Test minimal config
                config_minimal = generate_client_config(
                    server_config=server_config,
                    server_name=f"{server_name}-minimal",
                    user_params=user_params_minimal,
                )

                # Should have default log level
                assert "--log-level" in config_minimal["args"]
                assert "INFO" in config_minimal["args"]
                # log-file will be auto-detected and included due to unified auto-detection
                assert (
                    "--log-file" in config_minimal["args"]
                )  # Now automatically included
                # Should contain auto-generated log file path
                args = config_minimal["args"]
                log_file_index = args.index("--log-file")
                log_file_path = args[log_file_index + 1]
                assert "mcp_filesystem_server_" in log_file_path
                assert log_file_path.endswith(".log")

                # Test full config
                config_full = generate_client_config(
                    server_config=server_config,
                    server_name=f"{server_name}-full",
                    user_params=user_params_full,
                )

                # Should have all specified parameters
                args = config_full["args"]
                assert "--project-dir" in args
                assert "--log-level" in args
                assert "DEBUG" in args
                assert "--log-file" in args
                assert "filesystem.log" in " ".join(args)

                print("✓ Filesystem server parameter combinations tested successfully")

    def test_filesystem_server_parameter_validation_errors(self) -> None:
        """Test filesystem server parameter validation error handling."""

        server_type = "mcp-server-filesystem"
        server_config = registry.get(server_type)
        assert server_config is not None

        # Test missing required parameter
        user_params_missing = {"log_level": "INFO"}  # Missing project_dir

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(
                server_config=server_config,
                server_name="invalid-test",
                user_params=user_params_missing,
            )
        assert "project-dir is required" in str(exc_info.value)

        # Test invalid choice parameter
        user_params_invalid = {
            "project_dir": "/tmp",
            "log_level": "INVALID_LEVEL",
        }

        with pytest.raises(ValueError) as exc_info:
            generate_client_config(
                server_config=server_config,
                server_name="invalid-test",
                user_params=user_params_invalid,
            )
        assert "not in valid choices" in str(exc_info.value)

        print("✓ Filesystem server parameter validation errors tested successfully")
