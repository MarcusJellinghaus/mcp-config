"""Simplified integration test for mcp-config setup command.

Tests that the setup process generates the correct JSON configuration entry
without modifying any real configuration files.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import the modules we need to test
from src.mcp_config.integration import generate_client_config
from src.mcp_config.servers import registry


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
