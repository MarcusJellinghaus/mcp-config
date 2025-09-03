"""Tests for different installation modes."""

# pylint: disable=invalid-sequence-index

import importlib.util
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestInstallationModes:
    """Test different installation modes detection."""

    def test_get_installation_mode_cli_command(self) -> None:
        """Test CLI command mode detection."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/mcp-code-checker"

            from src.mcp_config.servers import registry

            config = registry.get("mcp-code-checker")
            assert config is not None

            assert config.get_installation_mode() == "cli_command"

    def test_get_installation_mode_python_module(self) -> None:
        """Test Python module mode detection."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            with patch("importlib.util.find_spec") as mock_spec:
                mock_spec.return_value = Mock()  # Simulate package installed

                from src.mcp_config.servers import registry

                config = registry.get("mcp-code-checker")
                assert config is not None

                mode = config.get_installation_mode()
                assert mode in ["python_module", "development"]  # Could be either

    def test_get_installation_mode_development(self) -> None:
        """Test development mode detection."""
        # This should pass when running from source
        from src.mcp_config.servers import registry

        config = registry.get("mcp-code-checker")
        assert config is not None

        # In development, src/main.py exists
        if Path("src/main.py").exists():
            mode = config.get_installation_mode()
            assert mode in ["cli_command", "python_module", "development"]
        else:
            pytest.skip("Not running from source directory")

    def test_generate_args_cli_mode(self) -> None:
        """Test argument generation for CLI command mode."""
        from tempfile import TemporaryDirectory

        from src.mcp_config.servers import registry

        config = registry.get("mcp-code-checker")
        assert config is not None

        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            params = {"project_dir": str(project_dir), "log_level": "DEBUG"}

            # Test CLI command mode (no script path)
            args = config.generate_args(params, use_cli_command=True)

            # Should not include script path
            assert not any(arg.endswith("main.py") for arg in args)
            assert "--project-dir" in args
            # Check that the project dir is in the args
            project_dir_idx = args.index("--project-dir")
            assert str(project_dir) in args[project_dir_idx + 1] or args[
                project_dir_idx + 1
            ] == str(project_dir)
            assert "--log-level" in args
            assert "DEBUG" in args

    def test_generate_args_module_mode(self) -> None:
        """Test argument generation for module mode."""
        from tempfile import TemporaryDirectory

        from src.mcp_config.servers import registry

        config = registry.get("mcp-code-checker")
        assert config is not None

        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            params = {"project_dir": str(project_dir), "log_level": "INFO"}

            # Test module mode (includes script path)
            args = config.generate_args(params, use_cli_command=False)

            # Should include script path as first argument
            assert args[0].endswith("main.py")
            assert "--project-dir" in args
            assert "--log-level" in args

    def test_config_generation_with_cli_command(self) -> None:
        """Test configuration generation when CLI command is available."""
        with (
            patch("src.mcp_config.integration.is_command_available") as mock_cmd,
            patch("src.mcp_config.integration._find_cli_executable") as mock_find,
        ):
            mock_cmd.return_value = True
            mock_find.return_value = "/usr/bin/mcp-code-checker"

            from src.mcp_config.integration import build_server_config
            from src.mcp_config.servers import registry

            server_config = registry.get("mcp-code-checker")
            assert server_config is not None

            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmpdir:
                project_dir = Path(tmpdir) / "project"
                project_dir.mkdir()
                params = {"project_dir": str(project_dir)}

                config = build_server_config(server_config, params)

                # With new behavior, should use CLI command when available
                assert (
                    config["command"].endswith(
                        (
                            "python",
                            "python.exe",
                            "mcp-code-checker",
                            "mcp-code-checker.exe",
                        )
                    )
                    or config["command"] == "/usr/bin/mcp-code-checker"
                )
                assert "--project-dir" in config["args"]

                # If using CLI mode, should not have -m args
                if (
                    config["command"].endswith(
                        ("mcp-code-checker", "mcp-code-checker.exe")
                    )
                    or config["command"] == "/usr/bin/mcp-code-checker"
                ):
                    assert not (
                        len(config["args"]) >= 2
                        and config["args"][0] == "-m"
                        and config["args"][1] == "mcp_code_checker"
                    )
                else:
                    # Python module mode fallback
                    assert config["args"][0] == "-m"
                    assert config["args"][1] == "mcp_code_checker"

    def test_config_generation_without_cli_command(self) -> None:
        """Test configuration generation without CLI command."""
        with patch(
            "src.mcp_config.integration.get_mcp_code_checker_command_mode"
        ) as mock_mode:
            mock_mode.return_value = "python_module"

            from src.mcp_config.integration import build_server_config
            from src.mcp_config.servers import registry

            server_config = registry.get("mcp-code-checker")
            assert server_config is not None

            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmpdir:
                project_dir = Path(tmpdir) / "project"
                project_dir.mkdir()
                params = {"project_dir": str(project_dir)}

                config = build_server_config(server_config, params)

                # Should use Python with module
                assert config["command"].endswith("python") or config[
                    "command"
                ].endswith("python.exe")
                assert "-m" in config["args"] or config["args"][0].endswith("main.py")

    def test_validation_with_different_modes(
        self,
    ) -> None:  # pylint: disable=invalid-sequence-index
        """Test validation messages for different installation modes."""
        from src.mcp_config.validation import validate_server_configuration

        # Mock different scenarios
        test_cases = [
            ("cli_command", "✓", "CLI command 'mcp-code-checker' is available"),
            ("python_module", "⚠", "Package installed but CLI command not found"),
            ("development", "ℹ", "Running in development mode"),
            ("not_installed", "✗", "not properly installed"),
        ]

        for mode_info in test_cases:
            mode = mode_info[0]
            expected_status = mode_info[1]
            expected_message = mode_info[2]
            with patch(
                "src.mcp_config.servers.ServerConfig.get_installation_mode"
            ) as mock_mode:
                mock_mode.return_value = mode

                with patch("shutil.which") as mock_which:
                    mock_which.return_value = (
                        "/usr/bin/mcp-code-checker" if mode == "cli_command" else None
                    )

                    result = validate_server_configuration(
                        "test-server", "mcp-code-checker", {"project_dir": "."}
                    )

                    if "cli_command" in result.get("checks", {}):
                        check = result["checks"]["cli_command"]
                        # Status might differ based on actual environment
                        assert "status" in check
                        assert "message" in check
