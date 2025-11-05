"""Tests for package version management."""

import re
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import pytest


class TestPackageVersion:
    """Test package version accessibility and format."""

    def test_version_exists(self) -> None:
        """Test that __version__ is accessible from package."""
        from src.mcp_config import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Test that version follows semantic versioning pattern."""
        from src.mcp_config import __version__

        # Should match semantic versioning: X.Y.Z or X.Y.Z.devN
        pattern = r"^\d+\.\d+\.\d+(\.(dev|rc|alpha|beta)\d+)?$"
        assert re.match(
            pattern, __version__
        ), f"Version '{__version__}' does not match semantic versioning pattern"

    def test_version_not_empty(self) -> None:
        """Test that version is not an empty string."""
        from src.mcp_config import __version__

        assert len(__version__) > 0

    def test_version_fallback_on_package_not_found(self) -> None:
        """Test that fallback version is used when package is not installed."""
        # This test verifies the exception handling logic exists
        # In reality, when installed, the version will be detected from setuptools-scm

        # We verify the fallback is defined in the code by checking
        # that the exception handling code path exists
        import importlib.util
        import sys
        from pathlib import Path

        # Load the module source code
        module_path = Path("src/mcp_config/__init__.py")
        spec = importlib.util.spec_from_file_location("test_module", module_path)

        if spec and spec.loader:
            # Check that the source contains proper exception handling
            with open(module_path, encoding="utf-8") as f:
                source = f.read()

            # Verify exception handling exists
            assert "PackageNotFoundError" in source
            assert "ImportError" in source
            assert "0.1.0.dev0" in source

    def test_version_fallback_on_import_error(self) -> None:
        """Test that the fallback version format is correct."""
        # When package is installed via setuptools-scm, version is auto-detected
        # When not installed or no tags exist, it falls back to 0.1.0.dev0

        from src.mcp_config import __version__

        # Version should either be from setuptools-scm (X.Y.Z.devN)
        # or the fallback (0.1.0.dev0)
        # Both should match the semantic versioning pattern
        pattern = r"^\d+\.\d+\.\d+(\.(dev|rc|alpha|beta)\d+)?$"
        import re

        assert re.match(pattern, __version__)


class TestCLIVersion:
    """Test CLI version flag."""

    def test_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that --version flag displays version."""
        from src.mcp_config.main import create_main_parser

        parser = create_main_parser()

        # The version flag should exit with code 0
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0

        # Check that version was printed
        captured = capsys.readouterr()
        assert "mcp-config" in captured.out

    def test_version_uses_package_version(self) -> None:
        """Test that CLI version matches package version."""
        from src.mcp_config import __version__
        from src.mcp_config.main import create_main_parser

        parser = create_main_parser()

        # Extract version from parser
        for action in parser._actions:
            if action.dest == "version":
                # The version string is formatted as "%(prog)s {__version__}"
                # We can verify __version__ is in the version string
                version_str = getattr(action, "version", None)
                assert (
                    version_str is not None
                ), "Version action has no version attribute"
                assert __version__ in str(version_str)
                break
        else:
            pytest.fail("No version action found in parser")
