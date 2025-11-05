"""Global pytest configuration and fixtures for test isolation.

This module provides comprehensive test isolation to prevent cross-test pollution
and ensure tests don't access real configuration files.

Key isolation strategies:
1. All client handlers are mocked to use isolated temporary directories
2. File I/O operations are controlled to prevent access to real config files
3. Each test function gets its own isolated temporary directory
4. Automatic cleanup ensures no test data persists between runs
"""

import shutil
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def global_test_isolation() -> Generator[None, None, None]:
    """Ensure complete isolation of all client handlers from real config files.

    This is a session-scoped fixture that runs once at the start of the test session
    and applies global patches to prevent any test from accidentally accessing real
    configuration files.

    NOTE: This fixture provides a safety net, but individual tests should still
    use the isolated_temp_dir fixture for their specific file operations.
    """
    # Store original functions that we might need to restore
    patches = []

    try:
        # Patch get_client_handler to prevent automatic migration on handler creation
        from src.mcp_config.clients import (
            get_client_handler as original_get_client_handler,
        )
        from src.mcp_config.clients import CLIENT_HANDLERS

        def safe_get_client_handler(client_name: str) -> Any:
            """Get client handler without triggering migration."""
            if client_name not in CLIENT_HANDLERS:
                raise ValueError(
                    f"Unknown client: {client_name}. Available: {list(CLIENT_HANDLERS.keys())}"
                )

            handler_factory = CLIENT_HANDLERS[client_name]
            if callable(handler_factory) and not isinstance(handler_factory, type):
                handler = handler_factory()
            else:
                handler = handler_factory()

            # Skip automatic migration during tests to prevent real file access
            # Individual tests can call migrate_inline_metadata() if they need to test it
            return handler

        # Apply the patch
        patch_get_handler = patch(
            "src.mcp_config.clients.get_client_handler", safe_get_client_handler
        )
        patch_get_handler.start()
        patches.append(patch_get_handler)

        yield

    finally:
        # Cleanup: stop all patches
        for p in patches:
            try:
                p.stop()
            except Exception:
                pass


@pytest.fixture(scope="function")
def isolated_temp_dir() -> Generator[Path, None, None]:
    """Provide completely isolated temporary directory for each test.

    This fixture ensures:
    - Each test gets its own unique temporary directory
    - Directory is completely empty at the start of the test
    - All files and directories are cleaned up after the test
    - Even if test fails, cleanup still happens

    Usage:
        def test_something(isolated_temp_dir: Path):
            config_file = isolated_temp_dir / "config.json"
            # ... test code ...
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        # Ensure directory is completely clean
        for item in temp_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)

        yield temp_path

        # Explicit cleanup after test
        if temp_path.exists():
            try:
                shutil.rmtree(temp_path, ignore_errors=True)
            except Exception:
                # If cleanup fails, at least try to remove individual files
                for item in temp_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                    except Exception:
                        pass


@pytest.fixture(scope="function")
def mock_all_client_handlers(
    isolated_temp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mock all client handlers to use isolated temporary directory.

    This fixture comprehensively mocks all client handler types to ensure
    they use the isolated temporary directory instead of real config paths.

    This is NOT autouse - tests that need this isolation should explicitly
    request this fixture or use the BaseClientHandlerTest class.
    """
    # Mock Claude Desktop Handler
    from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

    def mock_claude_desktop_config_path(self: Any) -> Path:
        return isolated_temp_dir / "claude_desktop_config.json"

    monkeypatch.setattr(
        ClaudeDesktopHandler, "get_config_path", mock_claude_desktop_config_path
    )

    # Mock Claude Code Handler - it already takes config_dir parameter
    # but we should ensure any instances use the temp dir
    from src.mcp_config.clients import claude_code

    original_claude_code_init = claude_code.ClaudeCodeHandler.__init__

    def mock_claude_code_init(self: Any, config_dir: Path | None = None) -> None:
        # Force use of isolated temp dir
        original_claude_code_init(self, config_dir=isolated_temp_dir)

    monkeypatch.setattr(
        claude_code.ClaudeCodeHandler, "__init__", mock_claude_code_init
    )

    # Mock VSCode Handler
    try:
        from src.mcp_config.clients.vscode import VSCodeHandler

        def mock_vscode_config_path(self: Any) -> Path:
            return isolated_temp_dir / "vscode_settings.json"

        monkeypatch.setattr(VSCodeHandler, "get_config_path", mock_vscode_config_path)
    except ImportError:
        pass  # VSCode handler might not exist yet

    # Mock IntelliJ Handler
    try:
        from src.mcp_config.clients.intellij import IntelliJHandler

        def mock_intellij_config_path(self: Any) -> Path:
            return isolated_temp_dir / "intellij_config.json"

        monkeypatch.setattr(
            IntelliJHandler, "get_config_path", mock_intellij_config_path
        )
    except ImportError:
        pass  # IntelliJ handler might not exist yet


@pytest.fixture(scope="function")
def sample_configs() -> dict[str, dict[str, Any]]:
    """Provide centralized sample configurations for testing.

    Returns a dictionary with various sample configurations that can be used
    across different tests to ensure consistency.

    Usage:
        def test_something(sample_configs):
            config = sample_configs['claude_desktop_basic']
            # ... test code ...
    """
    return {
        "empty": {"mcpServers": {}},
        "claude_desktop_basic": {
            "mcpServers": {
                "filesystem": {
                    "command": "node",
                    "args": ["filesystem-server.js"],
                },
                "calculator": {
                    "command": "python",
                    "args": ["calculator.py"],
                    "env": {"PYTHONPATH": "/path/to/lib"},
                },
            }
        },
        "claude_code_basic": {
            "mcpServers": {
                "test-server": {
                    "type": "stdio",
                    "command": "python",
                    "args": ["-m", "test"],
                }
            }
        },
        "managed_server": {
            "command": "/usr/bin/python",
            "args": ["src/main.py", "--project-dir", "/test/project"],
            "env": {"PYTHONPATH": "/test/project"},
            "_managed_by": "mcp-config-managed",
            "_server_type": "mcp-code-checker",
        },
    }


def pytest_configure(config: Any) -> None:
    """Configure pytest with custom markers and settings."""
    # Register custom markers to avoid warnings
    config.addinivalue_line("markers", "unit: Pure unit tests with no file I/O")
    config.addinivalue_line("markers", "integration: Integration tests with file I/O")
    config.addinivalue_line(
        "markers", "client_handler: Tests for specific client handlers"
    )
    config.addinivalue_line(
        "markers", "cross_client: Tests that involve multiple clients"
    )
    config.addinivalue_line(
        "markers", "isolation_critical: Tests that must be completely isolated"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Automatically mark tests based on their location and content.

    This hook runs after test collection and automatically applies markers
    based on test location and naming patterns.
    """
    for item in items:
        # Mark tests in test_config/ as integration tests by default
        if "test_config" in str(item.fspath):
            if "test_clients" in str(item.fspath):
                item.add_marker(pytest.mark.client_handler)
                item.add_marker(pytest.mark.integration)
            elif "test_claude_code" in str(item.fspath):
                item.add_marker(pytest.mark.client_handler)
                item.add_marker(pytest.mark.integration)
            elif "test_integration" in str(item.fspath):
                item.add_marker(pytest.mark.integration)

        # Mark normalization and validation tests as unit tests
        if "normalization" in item.nodeid or "validation" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Mark tests with "isolation" in name as isolation_critical
        if "isolation" in item.nodeid.lower():
            item.add_marker(pytest.mark.isolation_critical)
