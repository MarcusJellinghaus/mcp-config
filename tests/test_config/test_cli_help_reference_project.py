"""Test CLI help text for reference-project parameter."""

import subprocess
import sys
from pathlib import Path

import pytest

from src.mcp_config.servers import registry


def test_reference_project_parameter_in_help() -> None:
    """Test that --reference-project parameter appears in setup help text."""
    # Test with direct CLI call
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.mcp_config.main",
            "setup",
            "mcp-server-filesystem",
            "--help",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    help_text = result.stdout.lower()

    # Check that reference-project parameter is present
    assert "--reference-project" in help_text
    assert "reference project" in help_text

    # Check for key help information
    assert "format:" in help_text or "name=path" in help_text
    assert (
        "repeatable" in help_text
        or "multiple times" in help_text
        or "append" in help_text
    )
    assert "example" in help_text


def test_reference_project_parameter_definition() -> None:
    """Test that reference-project parameter definition is correct."""
    server_config = registry.get("mcp-server-filesystem")
    assert server_config is not None

    # Find the reference-project parameter
    ref_param = None
    for param in server_config.parameters:
        if param.name == "reference-project":
            ref_param = param
            break

    assert ref_param is not None, "reference-project parameter not found"

    # Verify parameter properties
    assert ref_param.arg_name == "--reference-project"
    assert ref_param.param_type == "string"
    assert ref_param.required is False
    assert ref_param.repeatable is True

    # Verify help text contains key information
    help_text = ref_param.help.lower()
    assert "format" in help_text or "name=path" in help_text
    assert "example" in help_text
    assert "multiple" in help_text or "repeatable" in help_text


def test_help_text_user_friendly() -> None:
    """Test that help text is clear and user-friendly."""
    server_config = registry.get("mcp-server-filesystem")
    assert server_config is not None

    # Find the reference-project parameter
    ref_param = None
    for param in server_config.parameters:
        if param.name == "reference-project":
            ref_param = param
            break

    assert ref_param is not None

    # Verify help text quality
    help_text = ref_param.help

    # Should be reasonably concise (not too long)
    assert len(help_text) < 300, "Help text should be concise"

    # Should contain practical example
    assert "docs=" in help_text or "examples=" in help_text or "path/to" in help_text

    # Should explain the format clearly
    assert "=" in help_text  # Shows the name=path format

    # Should indicate it can be repeated
    assert (
        "multiple" in help_text.lower()
        or "repeatable" in help_text.lower()
        or "times" in help_text.lower()
    )


def test_cli_parser_handles_multiple_reference_projects() -> None:
    """Test that CLI parser correctly handles multiple --reference-project arguments."""
    from src.mcp_config.cli_utils import create_full_parser

    parser = create_full_parser()

    # Test parsing multiple reference projects
    args = parser.parse_args(
        [
            "setup",
            "mcp-server-filesystem",
            "test-server",
            "--project-dir",
            "/test/path",
            "--reference-project",
            "docs=/path/to/docs",
            "--reference-project",
            "examples=/path/to/examples",
        ]
    )

    # Should have parsed into a list
    assert hasattr(args, "reference_project")
    assert args.reference_project == [
        "docs=/path/to/docs",
        "examples=/path/to/examples",
    ]


def test_cli_help_shows_metavar_for_reference_project() -> None:
    """Test that CLI help shows appropriate metavar for reference-project."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.mcp_config.main",
            "setup",
            "mcp-server-filesystem",
            "--help",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    help_text = result.stdout

    # Should show the parameter with appropriate metavar
    # Look for the pattern: --reference-project REFERENCE_PROJECT or similar
    assert "--reference-project" in help_text

    # Should show it can be specified multiple times (argparse usually shows this)
    # This might show as multiple lines or with "append" action indication
    lines = help_text.split("\n")
    ref_lines = [line for line in lines if "--reference-project" in line]
    assert len(ref_lines) > 0, "Should find reference-project in help output"
