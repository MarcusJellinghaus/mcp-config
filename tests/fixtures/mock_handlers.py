"""Mock handler utilities for testing.

This module provides mock handlers and utilities for testing client handler
functionality in isolation.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


def create_mock_handler(config_path: Path) -> MagicMock:
    """Create a mock client handler for testing.

    Args:
        config_path: Path to the configuration file

    Returns:
        MagicMock object configured as a client handler
    """
    mock = MagicMock()
    mock.get_config_path.return_value = config_path
    mock.load_config.return_value = {"mcpServers": {}}
    mock.save_config.return_value = True
    mock.setup_server.return_value = True
    mock.remove_server.return_value = True
    mock.list_managed_servers.return_value = []
    mock.list_all_servers.return_value = []
    mock.validate_config.return_value = []
    return mock


def create_mock_config_dict(server_count: int = 2) -> dict[str, Any]:
    """Create a mock configuration dictionary with specified number of servers.

    Args:
        server_count: Number of servers to include in the config

    Returns:
        Dictionary with mock MCP server configuration
    """
    config: dict[str, Any] = {"mcpServers": {}}

    for i in range(server_count):
        server_name = f"mock-server-{i+1}"
        config["mcpServers"][server_name] = {
            "command": "python",
            "args": [f"server{i+1}.py"],
        }

    return config


def mock_file_operations(monkeypatch: Any, temp_dir: Path) -> None:
    """Mock file operations to use a temporary directory.

    Args:
        monkeypatch: pytest monkeypatch fixture
        temp_dir: Temporary directory to use for file operations
    """
    import json

    # Store for mock file system
    mock_files: dict[Path, str] = {}

    def mock_read(path: Path) -> str:
        if path in mock_files:
            return mock_files[path]
        raise FileNotFoundError(f"No such file: {path}")

    def mock_write(path: Path, content: str) -> None:
        mock_files[path] = content

    def mock_exists(path: Path) -> bool:
        return path in mock_files

    # Apply mocks
    monkeypatch.setattr("pathlib.Path.read_text", mock_read)
    monkeypatch.setattr("pathlib.Path.write_text", mock_write)
    monkeypatch.setattr("pathlib.Path.exists", mock_exists)
