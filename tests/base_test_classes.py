"""Base test classes with built-in isolation for client handler testing.

This module provides base classes that automatically handle test isolation,
ensuring that tests don't interfere with each other or access real config files.

Usage:
    class TestMyClientHandler(BaseClientHandlerTest):
        def test_something(self, isolated_temp_dir):
            # Test code here - isolation is automatic
            pass
"""

from pathlib import Path
from typing import Any, Generator

import pytest


class BaseClientHandlerTest:
    """Base class for all client handler tests with automatic isolation.

    This base class provides:
    - Automatic isolation from real configuration files
    - Clean temporary directory for each test
    - Comprehensive mocking of all client handlers
    - Automatic cleanup after tests

    Usage:
        class TestClaudeDesktopHandler(BaseClientHandlerTest):
            def test_load_config(self, handler):
                # handler is automatically isolated
                config = handler.load_config()
                assert config == {"mcpServers": {}}
    """

    @pytest.fixture(autouse=True)
    def setup_isolation(
        self, isolated_temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> Generator[None, None, None]:
        """Automatically isolate all client handlers for every test in this class.

        This fixture is autouse=True, so it runs automatically for every test method
        in classes that inherit from BaseClientHandlerTest.
        """
        # Import all client handlers
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler
        from src.mcp_config.clients.claude_code import ClaudeCodeHandler

        # Create separate subdirectories for each handler type to prevent cross-pollution
        claude_desktop_dir = isolated_temp_dir / "claude_desktop"
        claude_code_dir = isolated_temp_dir / "claude_code"
        claude_desktop_dir.mkdir(exist_ok=True)
        claude_code_dir.mkdir(exist_ok=True)

        # Mock Claude Desktop Handler
        def mock_claude_desktop_config_path(self: Any) -> Path:
            return claude_desktop_dir / "claude_desktop_config.json"

        monkeypatch.setattr(
            ClaudeDesktopHandler, "get_config_path", mock_claude_desktop_config_path
        )

        # Also patch at the module level to catch any direct imports
        from src.mcp_config.clients import claude_desktop

        monkeypatch.setattr(
            claude_desktop.ClaudeDesktopHandler,
            "get_config_path",
            mock_claude_desktop_config_path,
        )

        # Mock load_json_config to ensure temp path usage
        from src.mcp_config.clients import utils

        original_load_json_config = utils.load_json_config

        def patched_load_json_config(path: Any, default: Any = None) -> Any:
            """Force any claude_desktop_config.json access to use temp path."""
            if hasattr(path, "name") and path.name == "claude_desktop_config.json":
                # Redirect to claude_desktop subdirectory
                temp_config_path = claude_desktop_dir / "claude_desktop_config.json"
                return original_load_json_config(temp_config_path, default)
            return original_load_json_config(path, default)

        monkeypatch.setattr(utils, "load_json_config", patched_load_json_config)

        # Mock Claude Code Handler initialization
        from src.mcp_config.clients import claude_code

        original_claude_code_init = claude_code.ClaudeCodeHandler.__init__

        def mock_claude_code_init(self: Any, config_dir: Path | None = None) -> None:
            """Force Claude Code handler to use isolated subdirectory."""
            original_claude_code_init(self, config_dir=claude_code_dir)

        monkeypatch.setattr(
            claude_code.ClaudeCodeHandler, "__init__", mock_claude_code_init
        )

        # Try to mock VSCode and IntelliJ handlers if they exist
        try:
            from src.mcp_config.clients.vscode import VSCodeHandler

            def mock_vscode_config_path(self: Any) -> Path:
                return isolated_temp_dir / "vscode_settings.json"

            monkeypatch.setattr(
                VSCodeHandler, "get_config_path", mock_vscode_config_path
            )
        except (ImportError, AttributeError):
            pass

        try:
            from src.mcp_config.clients.intellij import IntelliJHandler

            def mock_intellij_config_path(self: Any) -> Path:
                return isolated_temp_dir / "intellij_config.json"

            monkeypatch.setattr(
                IntelliJHandler, "get_config_path", mock_intellij_config_path
            )
        except (ImportError, AttributeError):
            pass

        yield

        # Cleanup: ensure all temp files are removed
        import shutil

        if isolated_temp_dir.exists():
            try:
                shutil.rmtree(isolated_temp_dir, ignore_errors=True)
            except Exception:
                pass

    @pytest.fixture
    def temp_config_dir(self, isolated_temp_dir: Path) -> Path:
        """Provide temporary config directory for tests.

        This is an alias for isolated_temp_dir for backward compatibility
        with existing test code.
        """
        return isolated_temp_dir


class BaseClaudeDesktopTest(BaseClientHandlerTest):
    """Base class specifically for Claude Desktop handler tests.

    Provides additional fixtures and utilities specific to Claude Desktop testing.
    """

    @pytest.fixture
    def handler(self, isolated_temp_dir: Path) -> Any:
        """Create a Claude Desktop handler with isolated config path."""
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

        # The config path is already mocked by setup_isolation to use claude_desktop subdirectory
        handler = ClaudeDesktopHandler()

        # Ensure config file doesn't exist at start of test
        config_path = handler.get_config_path()
        if config_path.exists():
            config_path.unlink()

        # Clean up metadata file too
        try:
            from src.mcp_config.clients.constants import METADATA_FILE

            metadata_path = config_path.parent / METADATA_FILE
            if metadata_path.exists():
                metadata_path.unlink()
        except ImportError:
            pass

        # Also ensure no other config files in the directory
        if config_path.parent.exists():
            for file in config_path.parent.glob("*.json"):
                if file != config_path:
                    file.unlink()

        return handler

    @pytest.fixture
    def sample_config(self) -> dict[str, Any]:
        """Sample Claude Desktop configuration."""
        return {
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
        }

    @pytest.fixture
    def managed_server_config(self) -> dict[str, Any]:
        """Configuration for a managed server."""
        return {
            "command": "/usr/bin/python",
            "args": ["src/main.py", "--project-dir", "/test/project"],
            "env": {"PYTHONPATH": "/test/project"},
            "_managed_by": "mcp-config-managed",
            "_server_type": "mcp-code-checker",
        }


class BaseClaudeCodeTest(BaseClientHandlerTest):
    """Base class specifically for Claude Code handler tests.

    Provides additional fixtures and utilities specific to Claude Code testing.
    """

    @pytest.fixture
    def handler(self, isolated_temp_dir: Path) -> Any:
        """Create a Claude Code handler with isolated config directory."""
        from src.mcp_config.clients.claude_code import ClaudeCodeHandler

        # The config_dir is automatically set to claude_code subdirectory by setup_isolation
        claude_code_dir = isolated_temp_dir / "claude_code"

        # Ensure directory is completely clean
        if claude_code_dir.exists():
            for file in claude_code_dir.glob(".mcp*.json"):
                file.unlink()

        # Create handler - it will use claude_code_dir due to mocking in setup_isolation
        return ClaudeCodeHandler()

    @pytest.fixture
    def sample_config(self) -> dict[str, Any]:
        """Sample Claude Code configuration."""
        return {
            "mcpServers": {
                "test-server": {
                    "type": "stdio",
                    "command": "python",
                    "args": ["-m", "test"],
                }
            }
        }


class BaseIntegrationTest(BaseClientHandlerTest):
    """Base class for integration tests that involve multiple client handlers.

    This class provides enhanced isolation for tests that need to work with
    multiple client handlers simultaneously.
    """

    @pytest.fixture
    def all_handlers(self, isolated_temp_dir: Path) -> dict[str, Any]:
        """Provide all client handler instances with isolated configs."""
        from src.mcp_config.clients import get_client_handler

        handlers = {}

        # Create instances of all available handlers
        try:
            handlers["claude-desktop"] = get_client_handler("claude-desktop")
        except Exception:
            pass

        try:
            handlers["claude-code"] = get_client_handler("claude-code")
        except Exception:
            pass

        try:
            handlers["vscode-workspace"] = get_client_handler("vscode-workspace")
        except Exception:
            pass

        try:
            handlers["vscode-user"] = get_client_handler("vscode-user")
        except Exception:
            pass

        try:
            handlers["intellij"] = get_client_handler("intellij")
        except Exception:
            pass

        return handlers
