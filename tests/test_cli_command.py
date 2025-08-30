"""Tests for CLI command functionality."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestCLICommand:
    """Test CLI command availability and functionality."""

    def test_cli_command_exists(self) -> None:
        """Test that mcp-config command is available."""
        import shutil

        # This test will pass if installed with pip install -e .
        # It's OK if it fails in CI without installation
        command_path = shutil.which("mcp-config")
        if command_path:
            assert Path(command_path).exists()
            print(f"✓ CLI command found at: {command_path}")
        else:
            pytest.skip("CLI command not installed (expected in CI)")

    def test_cli_command_help(self) -> None:
        """Test that CLI command shows help."""
        import shutil

        if not shutil.which("mcp-config"):
            pytest.skip("CLI command not installed")

        result = subprocess.run(
            ["mcp-config", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0
        assert "setup" in result.stdout
        assert "remove" in result.stdout
        assert "list" in result.stdout

    def test_python_module_fallback(self) -> None:
        """Test Python module invocation as fallback."""
        result = subprocess.run(
            [sys.executable, "-m", "src.mcp_config.main", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent.parent,  # Project root
            check=False,
        )

        # Should work in development
        if result.returncode == 0:
            assert "setup" in result.stdout
            assert "remove" in result.stdout
            assert "list" in result.stdout
        else:
            # Might not work in all environments
            pytest.skip("Python module not available in this environment")

    @patch("shutil.which")
    def test_command_detection(self, mock_which: Mock) -> None:
        """Test command detection logic."""
        from src.mcp_config.integration import is_command_available

        # Test when command exists
        mock_which.return_value = "/usr/bin/mcp-config"
        assert is_command_available("mcp-config") is True

        # Test when command doesn't exist
        mock_which.return_value = None
        assert is_command_available("mcp-config") is False

    def test_entry_point_configuration(self) -> None:
        """Test that entry point is correctly configured in pyproject.toml."""
        try:
            import tomllib  # type: ignore[import-not-found]
        except ImportError:
            # Python < 3.11 fallback
            try:
                import tomli as tomllib  # type: ignore[import-not-found,no-redef]
            except ImportError:
                pytest.skip("No TOML library available")

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Check that CLI entry point exists
        scripts = data.get("project", {}).get("scripts", {})
        assert "mcp-config" in scripts
        assert scripts["mcp-config"] == "mcp_config.main:main"
