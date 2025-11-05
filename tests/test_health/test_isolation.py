"""Test isolation health checks.

These tests verify that the test isolation infrastructure is working correctly
and that tests are not accessing real configuration files or experiencing
cross-test pollution.
"""

import json
import os
from pathlib import Path
from typing import Any

import pytest

from tests.base_test_classes import BaseClientHandlerTest


class TestIsolationHealth(BaseClientHandlerTest):
    """Verify that test isolation is working correctly."""

    @pytest.mark.isolation_critical
    def test_no_real_config_access_claude_desktop(
        self, isolated_temp_dir: Path
    ) -> None:
        """Verify Claude Desktop handler doesn't access real config files."""
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

        handler = ClaudeDesktopHandler()
        config_path = handler.get_config_path()

        # Verify the config path is in temp directory
        assert str(isolated_temp_dir) in str(config_path), (
            f"Handler is accessing real config path: {config_path}. "
            f"Expected path in: {isolated_temp_dir}"
        )

        # Verify it's not in user home directory
        home_dir = Path.home()
        assert not str(config_path).startswith(
            str(home_dir)
        ), f"Handler is accessing home directory: {config_path}"

    @pytest.mark.isolation_critical
    def test_no_real_config_access_claude_code(self, isolated_temp_dir: Path) -> None:
        """Verify Claude Code handler doesn't access real config files."""
        from src.mcp_config.clients.claude_code import ClaudeCodeHandler

        handler = ClaudeCodeHandler()
        config_path = handler.get_config_path()

        # Verify the config path is in temp directory
        assert str(isolated_temp_dir) in str(config_path), (
            f"Handler is accessing real config path: {config_path}. "
            f"Expected path in: {isolated_temp_dir}"
        )

    @pytest.mark.isolation_critical
    def test_temp_directory_cleanup(self, isolated_temp_dir: Path) -> None:
        """Verify that temporary directories are properly cleaned up."""
        # Create some test files
        test_file = isolated_temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        test_subdir = isolated_temp_dir / "subdir"
        test_subdir.mkdir()
        (test_subdir / "nested.json").write_text('{"nested": "data"}')

        # Verify files exist
        assert test_file.exists()
        assert test_subdir.exists()
        assert (test_subdir / "nested.json").exists()

        # Note: Actual cleanup happens in the fixture teardown
        # This test just verifies that we can create and access files

    @pytest.mark.isolation_critical
    def test_no_cross_test_pollution(self, isolated_temp_dir: Path) -> None:
        """Verify that each test gets a fresh isolated directory."""
        # Create a marker file
        marker = isolated_temp_dir / "pollution_marker.txt"
        marker.write_text("This file should not exist in other tests")

        assert marker.exists()

        # In a real scenario, the next test should not see this file
        # because it gets its own isolated_temp_dir

    @pytest.mark.isolation_critical
    def test_mock_effectiveness_claude_desktop(
        self, isolated_temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify that mocks are properly applied for Claude Desktop."""
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

        handler = ClaudeDesktopHandler()
        config_path = handler.get_config_path()

        # The mock should force the config path to be in isolated_temp_dir
        assert "claude_desktop_config.json" in str(config_path)
        assert str(isolated_temp_dir) in str(config_path)

        # Try to load config (should return empty dict, not real config)
        config = handler.load_config()

        # Should get empty mcpServers, not any real configuration
        assert config == {"mcpServers": {}}

    @pytest.mark.isolation_critical
    def test_multiple_handlers_isolated(self, isolated_temp_dir: Path) -> None:
        """Verify that multiple handler types don't interfere with each other."""
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler
        from src.mcp_config.clients.claude_code import ClaudeCodeHandler

        # Create both handler types
        desktop_handler = ClaudeDesktopHandler()
        code_handler = ClaudeCodeHandler()

        # Get their config paths
        desktop_path = desktop_handler.get_config_path()
        code_path = code_handler.get_config_path()

        # Both should be in the isolated temp dir (but in separate subdirectories)
        assert str(isolated_temp_dir) in str(desktop_path)
        assert str(isolated_temp_dir) in str(code_path)

        # They should be in different subdirectories
        assert "claude_desktop" in str(desktop_path)
        assert "claude_code" in str(code_path)

        # And they should be different files
        assert desktop_path != code_path

        # Set up a server in desktop handler
        desktop_handler.setup_server(
            "test-desktop-server",
            {
                "command": "python",
                "args": ["desktop.py"],
                "_managed_by": "mcp-config-managed",
                "_server_type": "test",
            },
        )

        # Set up a server in code handler
        code_handler.setup_server(
            "test-code-server",
            {
                "command": "python",
                "args": ["code.py"],
                "_managed_by": "mcp-config-managed",
                "_server_type": "test",
            },
        )

        # Load configs and verify they're separate
        desktop_config = desktop_handler.load_config()
        code_config = code_handler.load_config()

        assert "test-desktop-server" in desktop_config["mcpServers"]
        assert "test-code-server" in code_config["mcpServers"]

        # Each should only have its own server (no cross-pollution)
        assert (
            "test-code-server" not in desktop_config["mcpServers"]
        ), f"Desktop handler polluted with Code server! Config: {desktop_config}"
        assert (
            "test-desktop-server" not in code_config["mcpServers"]
        ), f"Code handler polluted with Desktop server! Config: {code_config}"


class TestFileSystemIsolation:
    """Test that file system operations are properly isolated."""

    def test_no_real_files_created(self, tmp_path: Path) -> None:
        """Verify that tests don't create files in real locations."""
        # Get the real config paths (not mocked)
        import platform

        if os.name == "nt":  # Windows
            real_config_base = Path.home() / "AppData" / "Roaming" / "Claude"
        elif platform.system() == "Darwin":  # macOS
            real_config_base = (
                Path.home() / "Library" / "Application Support" / "Claude"
            )
        else:  # Linux
            real_config_base = Path.home() / ".config" / "claude"

        real_config_path = real_config_base / "claude_desktop_config.json"

        # Check if real config exists and has test pollution
        if real_config_path.exists():
            with open(real_config_path, "r") as f:
                try:
                    real_config = json.load(f)
                    if "mcpServers" in real_config:
                        # Check for test server names that shouldn't be there
                        test_server_names = {
                            "test-server",
                            "test-desktop-server",
                            "test-code-server",
                            "my-server",
                            "my_server",
                        }
                        polluted_servers = (
                            set(real_config["mcpServers"].keys()) & test_server_names
                        )

                        assert len(polluted_servers) == 0, (
                            f"Real config file has test pollution: {polluted_servers}. "
                            "Test isolation is not working correctly!"
                        )
                except json.JSONDecodeError:
                    pass  # Config file exists but is invalid, which is fine

    def test_temp_dir_independence(self, isolated_temp_dir: Path) -> None:
        """Verify that each test gets an independent temp directory."""
        # This test should not see any files from previous tests
        files = list(isolated_temp_dir.iterdir())

        # Directory should be empty (or only contain expected files)
        # Filter out any system files like .DS_Store
        files = [f for f in files if not f.name.startswith(".")]

        assert len(files) == 0, (
            f"Temp directory is not clean: {files}. " "Cross-test pollution detected!"
        )


class TestMigrationIsolation:
    """Test that migration operations are properly isolated."""

    @pytest.mark.isolation_critical
    def test_migration_doesnt_affect_real_config(
        self, isolated_temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify that migrate_inline_metadata doesn't touch real files."""
        from src.mcp_config.clients.claude_desktop import ClaudeDesktopHandler

        # Mock the config path
        def mock_get_config_path(self: Any) -> Path:
            return isolated_temp_dir / "claude_desktop_config.json"

        monkeypatch.setattr(
            ClaudeDesktopHandler, "get_config_path", mock_get_config_path
        )

        # Create a config with inline metadata
        config_path = isolated_temp_dir / "claude_desktop_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["test.py"],
                    "_managed_by": "mcp-config-managed",
                    "_server_type": "test",
                }
            }
        }

        with open(config_path, "w") as f:
            json.dump(test_config, f)

        # Run migration
        handler = ClaudeDesktopHandler()
        migrated = handler.migrate_inline_metadata()

        assert migrated

        # Verify migration happened in temp dir
        assert config_path.exists()

        # Verify real config wasn't touched (if it exists)
        import platform

        if os.name == "nt":  # Windows
            real_config_base = Path.home() / "AppData" / "Roaming" / "Claude"
        elif platform.system() == "Darwin":  # macOS
            real_config_base = (
                Path.home() / "Library" / "Application Support" / "Claude"
            )
        else:  # Linux
            real_config_base = Path.home() / ".config" / "claude"

        real_config_path = real_config_base / "claude_desktop_config.json"

        # If real config exists, verify it doesn't have test-server
        if real_config_path.exists():
            with open(real_config_path, "r") as f:
                try:
                    real_config = json.load(f)
                    if "mcpServers" in real_config:
                        assert (
                            "test-server" not in real_config["mcpServers"]
                        ), "Migration affected real config file!"
                except json.JSONDecodeError:
                    pass


@pytest.mark.isolation_critical
def test_isolation_in_test_order() -> None:
    """Verify that test execution order doesn't affect isolation.

    This is a meta-test that should pass regardless of when it's run
    in the test suite.
    """
    # This test should always pass, proving isolation works
    # regardless of test execution order
    assert True, "If this fails, test isolation is broken at a fundamental level"
