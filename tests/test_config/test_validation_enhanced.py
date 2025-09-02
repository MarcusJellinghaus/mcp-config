"""Tests for enhanced validation system."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.mcp_config.validation import (
    get_installation_instructions,
    validate_cli_command,
    validate_code_checker_project,
    validate_filesystem_server_directory,
    validate_server_configuration,
    validate_server_installation,
)


class TestServerInstallationValidation:
    """Test server installation validation."""

    @patch("shutil.which")
    def test_mcp_code_checker_cli_available(self, mock_which: Mock) -> None:
        """Test validation when MCP Code Checker CLI is available."""
        mock_which.return_value = "/usr/bin/mcp-code-checker"

        mode, check = validate_server_installation("mcp-code-checker")

        assert mode == "cli_command"
        assert check["status"] == "success"
        assert "CLI command 'mcp-code-checker' is available" in check["message"]

    @patch("shutil.which")
    def test_mcp_filesystem_server_cli_available(self, mock_which: Mock) -> None:
        """Test validation when MCP Filesystem Server CLI is available."""
        mock_which.return_value = "/usr/bin/mcp-server-filesystem"

        mode, check = validate_server_installation("mcp-server-filesystem")

        assert mode == "cli_command"
        assert check["status"] == "success"
        assert "CLI command 'mcp-server-filesystem' is available" in check["message"]

    def test_unknown_server_type(self) -> None:
        """Test validation for unknown server type."""
        mode, check = validate_server_installation("unknown-server")

        assert mode == "unknown"
        assert check["status"] == "unknown"
        assert "Unknown server type" in check["message"]


class TestFilesystemServerDirectoryValidation:
    """Test filesystem server directory validation."""

    def test_validate_filesystem_server_directory_success(self) -> None:
        """Test successful directory validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            errors = validate_filesystem_server_directory(project_dir)

            assert errors == []

    def test_validate_filesystem_server_directory_nonexistent(self) -> None:
        """Test validation with non-existent directory."""
        non_existent = Path("/does/not/exist")

        errors = validate_filesystem_server_directory(non_existent)

        assert len(errors) > 0
        assert "does not exist" in errors[0]


class TestCodeCheckerProjectValidation:
    """Test code checker project validation."""

    def test_validate_code_checker_project_with_tests(self) -> None:
        """Test validation with proper test folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create test folder
            test_dir = project_dir / "tests"
            test_dir.mkdir()

            # Create Python project structure
            setup_file = project_dir / "setup.py"
            setup_file.write_text("# Setup file")

            errors = validate_code_checker_project(project_dir)

            assert errors == []

    def test_validate_code_checker_project_missing_tests(self) -> None:
        """Test validation with missing test folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create Python project structure
            setup_file = project_dir / "setup.py"
            setup_file.write_text("# Setup file")

            errors = validate_code_checker_project(project_dir)

            assert len(errors) == 1
            assert "Test folder 'tests' not found" in errors[0]


class TestInstallationInstructions:
    """Test installation instruction generation."""

    def test_code_checker_not_available(self) -> None:
        """Test installation instructions for code checker when not available."""
        instructions = get_installation_instructions(
            "mcp-code-checker", "not_available"
        )

        assert "pip install mcp-code-checker" in instructions
        assert "From PyPI" in instructions

    def test_filesystem_server_not_available(self) -> None:
        """Test installation instructions for filesystem server when not available."""
        instructions = get_installation_instructions(
            "mcp-server-filesystem", "not_available"
        )

        assert "pip install mcp-server-filesystem" in instructions
        assert "From PyPI" in instructions
