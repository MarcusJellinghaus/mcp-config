"""Test that mcp-server-filesystem doesn't include venv-path in CLI mode."""

from pathlib import Path
from unittest.mock import patch

from mcp_config.integration import (
    generate_client_config,  # type: ignore[import-untyped]
)
from mcp_config.servers import (  # type: ignore[import-untyped]
    MCP_CODE_CHECKER,
    MCP_FILESYSTEM_SERVER,
)


def test_filesystem_server_no_venv_path() -> None:
    """Verify filesystem server doesn't receive venv-path parameter."""
    with patch("shutil.which", return_value="/usr/local/bin/mcp-server-filesystem"):
        params = {
            "project_dir": "/test/project",
            "venv_path": "/test/project/.venv",
            "log_level": "INFO",
        }

        config = generate_client_config(MCP_FILESYSTEM_SERVER, "test-fs", params)

        # The fix: venv-path should NOT be in arguments
        assert "--venv-path" not in config["args"]


def test_code_checker_keeps_venv_path() -> None:
    """Verify code-checker still receives venv-path (regression test)."""
    with patch("shutil.which", return_value="/usr/local/bin/mcp-code-checker"):
        params = {
            "project_dir": "/test/project",
            "venv_path": "/test/project/.venv",
            "python_executable": "/usr/bin/python3",
            "log_level": "INFO",
        }

        config = generate_client_config(MCP_CODE_CHECKER, "test-checker", params)

        # Code-checker should still get venv-path
        assert "--venv-path" in config["args"]
