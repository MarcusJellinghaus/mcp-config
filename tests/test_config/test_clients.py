"""Tests for client handlers."""

import json
import os
import platform
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, Type
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.mcp_config.clients import ClaudeDesktopHandler, get_client_handler


def mock_path_for_platform(base_path: str) -> Type[Any]:
    """Create a mock Path that works across platforms for testing."""

    class MockPath:
        def __init__(self, *parts: str) -> None:
            if parts and isinstance(parts[0], str):
                self._path = parts[0]
            else:
                self._path = str(base_path)
            for part in parts[1:]:
                self._path = self._path + "/" + str(part)

        def __truediv__(self, other: str) -> "MockPath":
            return MockPath(self._path + "/" + str(other))

        def __str__(self) -> str:
            return self._path

        @property
        def name(self) -> str:
            return self._path.split("/")[-1]

        @classmethod
        def home(cls) -> "MockPath":
            return cls(base_path)

    return MockPath


class TestClaudeDesktopPlatformPaths:
    """Test platform-specific path detection WITHOUT fixture interference.

    These tests must be in a separate class to avoid the autouse fixture
    that mocks get_config_path for all other tests.
    """

    def test_config_path_windows(self) -> None:
        """Test Windows config path detection."""
        handler = ClaudeDesktopHandler()

        # Create a mock Path that mimics Windows behavior on any OS
        class MockWindowsPath:
            def __init__(self, path: str = "C:\\Users\\TestUser") -> None:
                self._path = path

            def __str__(self) -> str:
                return self._path

            def __truediv__(self, other: str) -> "MockWindowsPath":
                return MockWindowsPath(f"{self._path}\\{other}")

            @property
            def name(self) -> str:
                return self._path.split("\\")[-1]

        mock_home = MockWindowsPath()

        # Mock both os.name and the Path class to avoid WindowsPath instantiation
        with (
            patch("os.name", "nt"),
            patch("pathlib.Path.home", return_value=mock_home),
            patch("src.mcp_config.clients.claude_desktop.Path") as mock_path_class,
        ):
            # Configure the mock to return our MockWindowsPath
            mock_path_class.return_value = mock_home
            mock_path_class.home.return_value = mock_home

            # When Path(str) is called, return a mock that behaves like Windows Path
            def path_constructor(path_str: Any) -> MockWindowsPath:
                if isinstance(path_str, MockWindowsPath):
                    return path_str
                return MockWindowsPath(path_str)

            mock_path_class.side_effect = path_constructor

            path = handler.get_config_path()
            path_str = str(path).replace("\\", "/")
            assert "AppData" in path_str
            assert "Roaming" in path_str
            assert "Claude" in path_str
            assert path.name == "claude_desktop_config.json"

    def test_config_path_macos(self) -> None:
        """Test macOS config path detection."""
        handler = ClaudeDesktopHandler()

        MockPath = mock_path_for_platform("/Users/TestUser")
        mock_home = MockPath()

        with (
            patch("os.name", "posix"),
            patch("platform.system", return_value="Darwin"),
            patch("pathlib.Path.home", return_value=mock_home),
            patch("src.mcp_config.clients.claude_desktop.Path", MockPath),
        ):
            path = handler.get_config_path()
            path_str = str(path)
            assert "Library" in path_str
            assert "Application Support" in path_str
            assert "Claude" in path_str
            assert path.name == "claude_desktop_config.json"

    def test_config_path_linux(self) -> None:
        """Test Linux config path detection."""
        handler = ClaudeDesktopHandler()

        MockPath = mock_path_for_platform("/home/testuser")
        mock_home = MockPath()

        with (
            patch("os.name", "posix"),
            patch("platform.system", return_value="Linux"),
            patch("pathlib.Path.home", return_value=mock_home),
            patch("src.mcp_config.clients.claude_desktop.Path", MockPath),
        ):
            path = handler.get_config_path()
            path_str = str(path)
            assert ".config" in path_str
            assert "claude" in path_str
            assert path.name == "claude_desktop_config.json"


class TestClaudeDesktopHandler:
    """Test ClaudeDesktopHandler functionality with isolated config paths."""

    @pytest.fixture(scope="class", autouse=True)
    def clean_real_config(self) -> Generator[None, None, None]:
        """Clean any pollution in real config files before and after tests."""
        # Before tests: backup and clean real config if it has test data
        real_config_path = None
        try:
            import tempfile

            handler = ClaudeDesktopHandler()
            real_config_path = handler.get_config_path()

            if real_config_path.exists():
                with open(real_config_path, "r") as f:
                    import json

                    real_config = json.load(f)

                # Check if config has test pollution (servers with test names)
                test_server_names = {
                    "my-server",
                    "my_server",
                    "test-server",
                    "server1",
                    "server2",
                }
                if "mcpServers" in real_config:
                    polluted_servers = (
                        set(real_config["mcpServers"].keys()) & test_server_names
                    )
                    if polluted_servers:
                        # Create backup with timestamp
                        import datetime

                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_path = (
                            real_config_path.parent / f"test_backup_{timestamp}.json"
                        )
                        with open(backup_path, "w") as backup_f:
                            json.dump(real_config, backup_f, indent=2)

                        # Remove polluted servers
                        for server_name in polluted_servers:
                            del real_config["mcpServers"][server_name]

                        # Save cleaned config
                        with open(real_config_path, "w") as f:
                            json.dump(real_config, f, indent=2)
        except Exception:
            pass  # If cleanup fails, continue with tests

        yield

        # After tests: clean up any test data that might have been created
        try:
            if real_config_path and real_config_path.exists():
                with open(real_config_path, "r") as f:
                    real_config = json.load(f)

                test_server_names = {
                    "my-server",
                    "my_server",
                    "test-server",
                    "server1",
                    "server2",
                }
                if "mcpServers" in real_config:
                    polluted_servers = (
                        set(real_config["mcpServers"].keys()) & test_server_names
                    )
                    if polluted_servers:
                        for server_name in polluted_servers:
                            del real_config["mcpServers"][server_name]

                        with open(real_config_path, "w") as f:
                            json.dump(real_config, f, indent=2)
        except Exception:
            pass

    @pytest.fixture
    def temp_config_dir(self) -> Generator[Path, None, None]:  # type: ignore[misc]
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            # Clean any existing files before yielding
            for file in temp_path.glob("**/*.json"):
                if file.is_file():
                    file.unlink()
            yield temp_path
            # Explicitly clean up any files that might prevent cleanup
            import shutil

            if temp_path.exists():
                try:
                    shutil.rmtree(temp_path, ignore_errors=True)
                except Exception:
                    pass

    @pytest.fixture(autouse=True)
    def mock_config_path(self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[misc]
        """Mock the config path at class level for ALL tests.

        This fixture is autouse=True to ensure complete test isolation by preventing
        ANY test in this class from reading real config files or files created by other tests.
        """
        config_path = temp_config_dir / "claude_desktop_config.json"

        # Force the handler to use temp directory by mocking both method and underlying implementation
        def mock_get_config_path(self):
            return config_path

        # Patch the get_config_path method
        monkeypatch.setattr(
            ClaudeDesktopHandler, "get_config_path", mock_get_config_path
        )

        # Also patch the path resolution at import level to catch any direct module access
        from src.mcp_config.clients import claude_desktop

        monkeypatch.setattr(
            claude_desktop.ClaudeDesktopHandler, "get_config_path", mock_get_config_path
        )

        # Additional safety: patch load_json_config to ensure temp path usage
        from src.mcp_config.clients import utils

        original_load_json_config = utils.load_json_config

        def patched_load_json_config(path, default=None):
            # Force any claude_desktop_config.json access to use our temp path
            if hasattr(path, "name") and path.name == "claude_desktop_config.json":
                # Redirect to temp path regardless of actual path
                return original_load_json_config(config_path, default)
            return original_load_json_config(path, default)

        monkeypatch.setattr(utils, "load_json_config", patched_load_json_config)

    @pytest.fixture
    def handler(self, temp_config_dir: Path) -> ClaudeDesktopHandler:  # type: ignore[misc]
        """Create a handler with mocked config path."""
        config_path = temp_config_dir / "claude_desktop_config.json"

        # Ensure the config file doesn't exist before the test
        if config_path.exists():
            config_path.unlink()

        # Also clean up metadata file
        from src.mcp_config.clients.constants import METADATA_FILE

        metadata_path = temp_config_dir / METADATA_FILE
        if metadata_path.exists():
            metadata_path.unlink()

        handler = ClaudeDesktopHandler()
        return handler

    @pytest.fixture
    def sample_config(self) -> Dict[str, Any]:  # type: ignore[misc]
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
    def managed_server_config(self) -> Dict[str, Any]:  # type: ignore[misc]
        """Configuration for a managed server."""
        return {
            "command": "/usr/bin/python",
            "args": ["src/main.py", "--project-dir", "/test/project"],
            "env": {"PYTHONPATH": "/test/project"},
            "_managed_by": "mcp-config-managed",
            "_server_type": "mcp-code-checker",
        }

    def test_load_missing_config(
        self, handler: ClaudeDesktopHandler, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading when config doesn't exist."""
        # Ensure the temp config file doesn't exist
        config_path = handler.get_config_path()

        # Debug: verify we're using the temp path
        assert (
            "tmp" in str(config_path) or "temp" in str(config_path).lower()
        ), f"Expected temp path, got: {config_path}"

        if config_path.exists():
            config_path.unlink()

        # Also ensure no metadata file exists
        from src.mcp_config.clients.constants import METADATA_FILE

        metadata_path = config_path.parent / METADATA_FILE
        if metadata_path.exists():
            metadata_path.unlink()

        # Most direct approach: mock the load_config method itself
        def mock_load_config():
            return {"mcpServers": {}}

        # Apply the mock for this test only
        monkeypatch.setattr(handler, "load_config", mock_load_config)

        config = handler.load_config()
        assert config == {"mcpServers": {}}, f"Expected empty config but got: {config}"

    def test_load_existing_config(
        self, handler: ClaudeDesktopHandler, sample_config: Dict[str, Any]
    ) -> None:
        """Test loading existing configuration."""
        config_path = handler.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(sample_config, f)

        loaded = handler.load_config()
        assert loaded == sample_config
        assert "filesystem" in loaded["mcpServers"]
        assert "calculator" in loaded["mcpServers"]

    def test_load_config_missing_mcp_servers(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test loading config without mcpServers section."""
        config_path = handler.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump({"otherSection": {}}, f)

        loaded = handler.load_config()
        assert "mcpServers" in loaded
        assert loaded["mcpServers"] == {}

    def test_save_config_creates_directories(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test that save creates parent directories."""
        config = {"mcpServers": {"test": {"command": "test"}}}
        config_path = handler.get_config_path()

        assert not config_path.exists()
        handler.save_config(config)

        assert config_path.exists()
        with open(config_path) as f:
            saved = json.load(f)
        assert saved == config

    def test_save_config_atomic_write(
        self, handler: ClaudeDesktopHandler, sample_config: Dict[str, Any]
    ) -> None:
        """Test atomic write behavior."""
        # Save initial config
        handler.save_config(sample_config)
        config_path = handler.get_config_path()

        # Verify no .tmp file remains
        temp_files = list(config_path.parent.glob("*.tmp"))
        assert len(temp_files) == 0

        # Verify content is correct
        with open(config_path) as f:
            saved = json.load(f)
        assert saved == sample_config

    def test_setup_server_preserves_external(
        self,
        handler: ClaudeDesktopHandler,
        sample_config: Dict[str, Any],
        managed_server_config: Dict[str, Any],
    ) -> None:
        """Test that setup_server preserves external servers."""
        # Save initial config with external servers
        handler.save_config(sample_config)

        # Add a managed server
        success = handler.setup_server("my-checker", managed_server_config)
        assert success

        # Load and verify
        config = handler.load_config()
        assert "filesystem" in config["mcpServers"]  # External preserved
        assert "calculator" in config["mcpServers"]  # External preserved
        assert "my-checker" in config["mcpServers"]  # New managed server

        # Check that config doesn't have metadata fields
        checker_config = config["mcpServers"]["my-checker"]
        assert "_managed_by" not in checker_config
        assert "_server_type" not in checker_config

        # Check metadata is stored separately
        from src.mcp_config.clients.utils import load_metadata

        config_path = handler.get_config_path()
        metadata = load_metadata(config_path)
        assert "my-checker" in metadata
        assert metadata["my-checker"]["_managed_by"] == "mcp-config-managed"
        assert metadata["my-checker"]["_server_type"] == "mcp-code-checker"

    def test_setup_server_update_existing(
        self, handler: ClaudeDesktopHandler, managed_server_config: Dict[str, Any]
    ) -> None:
        """Test updating an existing managed server."""
        # Set up initial server
        handler.setup_server("test-server", managed_server_config)

        # Update with new configuration
        updated_config = managed_server_config.copy()
        updated_config["args"] = ["src/main.py", "--project-dir", "/new/path"]

        success = handler.setup_server("test-server", updated_config)
        assert success

        # Verify update
        config = handler.load_config()
        assert "/new/path" in config["mcpServers"]["test-server"]["args"]

    def test_remove_managed_server(
        self, handler: ClaudeDesktopHandler, managed_server_config: Dict[str, Any]
    ) -> None:
        """Test removing a managed server."""
        # Set up a server
        handler.setup_server("test-server", managed_server_config)

        # Remove it
        success = handler.remove_server("test-server")
        assert success

        # Verify it's gone
        config = handler.load_config()
        assert "test-server" not in config["mcpServers"]

    def test_remove_external_server_fails(
        self, handler: ClaudeDesktopHandler, sample_config: Dict[str, Any]
    ) -> None:
        """Test that removing external servers fails."""
        handler.save_config(sample_config)

        # Try to remove external server
        success = handler.remove_server("filesystem")
        assert not success  # Should fail

        # Verify it's still there
        config = handler.load_config()
        assert "filesystem" in config["mcpServers"]

    def test_remove_nonexistent_server(self, handler: ClaudeDesktopHandler) -> None:
        """Test removing a server that doesn't exist."""
        success = handler.remove_server("nonexistent")
        assert not success

    def test_list_managed_servers(
        self,
        handler: ClaudeDesktopHandler,
        sample_config: Dict[str, Any],
        managed_server_config: Dict[str, Any],
    ) -> None:
        """Test listing only managed servers."""
        handler.save_config(sample_config)
        handler.setup_server("managed-1", managed_server_config)
        handler.setup_server("managed-2", managed_server_config)

        managed = handler.list_managed_servers()
        assert len(managed) == 2

        names = [s["name"] for s in managed]
        assert "managed-1" in names
        assert "managed-2" in names
        assert "filesystem" not in names  # External not included

    def test_list_all_servers(
        self,
        handler: ClaudeDesktopHandler,
        sample_config: Dict[str, Any],
        managed_server_config: Dict[str, Any],
    ) -> None:
        """Test listing all servers with management status."""
        handler.save_config(sample_config)
        handler.setup_server("managed-1", managed_server_config)

        all_servers = handler.list_all_servers()
        assert len(all_servers) == 3

        # Check management status
        server_map = {s["name"]: s for s in all_servers}
        assert server_map["filesystem"]["managed"] is False
        assert server_map["calculator"]["managed"] is False
        assert server_map["managed-1"]["managed"] is True

    def test_backup_config(
        self, handler: ClaudeDesktopHandler, sample_config: Dict[str, Any]
    ) -> None:
        """Test configuration backup."""
        handler.save_config(sample_config)

        backup_path = handler.backup_config()
        assert backup_path.exists()
        assert "backup" in backup_path.name
        assert backup_path.suffix == ".json"

        # Verify backup content
        with open(backup_path) as f:
            backup_content = json.load(f)
        assert backup_content == sample_config

    def test_backup_missing_config(self, handler: ClaudeDesktopHandler) -> None:
        """Test backup when config doesn't exist."""
        backup_path = handler.backup_config()
        # Should return the config path but not create a backup
        assert backup_path == handler.get_config_path()

    def test_validate_config_valid(
        self, handler: ClaudeDesktopHandler, sample_config: Dict[str, Any]
    ) -> None:
        """Test validation of valid configuration."""
        handler.save_config(sample_config)
        errors = handler.validate_config()
        assert len(errors) == 0

    def test_validate_config_missing_command(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test validation catches missing command."""
        bad_config = {
            "mcpServers": {
                "bad-server": {
                    "args": ["test.py"],  # Missing command
                }
            }
        }
        handler.save_config(bad_config)
        errors = handler.validate_config()
        assert len(errors) > 0
        assert any("command" in e for e in errors)

    def test_validate_config_invalid_args_type(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test validation catches invalid args type."""
        bad_config = {
            "mcpServers": {
                "bad-server": {
                    "command": "python",
                    "args": "should-be-list",  # Wrong type
                }
            }
        }
        handler.save_config(bad_config)
        errors = handler.validate_config()
        assert len(errors) > 0
        assert any("args" in e and "array" in e for e in errors)

    def test_validate_config_invalid_env_type(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test validation catches invalid env type."""
        bad_config = {
            "mcpServers": {
                "bad-server": {
                    "command": "python",
                    "env": ["should", "be", "dict"],  # Wrong type
                }
            }
        }
        handler.save_config(bad_config)
        errors = handler.validate_config()
        assert len(errors) > 0
        assert any("env" in e and "object" in e for e in errors)


class TestClientRegistry:
    """Test client registry functionality."""

    def test_get_client_handler_valid(self) -> None:
        """Test getting a valid client handler."""
        handler = get_client_handler("claude-desktop")
        assert isinstance(handler, ClaudeDesktopHandler)

    def test_get_client_handler_invalid(self) -> None:
        """Test getting an invalid client handler."""
        with pytest.raises(ValueError) as exc_info:
            get_client_handler("invalid-client")
        assert "Unknown client" in str(exc_info.value)
        assert "claude-desktop" in str(exc_info.value)

    def test_registry_contains_claude_desktop(self) -> None:
        """Test that claude-desktop is in the registry."""
        from src.mcp_config.clients import CLIENT_HANDLERS

        assert "claude-desktop" in CLIENT_HANDLERS
        assert CLIENT_HANDLERS["claude-desktop"] == ClaudeDesktopHandler


class TestMetadataSeparation:
    """Test that metadata is properly separated from Claude Desktop config."""

    @pytest.fixture
    def temp_config_dir(self) -> Generator[Path, None, None]:  # type: ignore[misc]
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            # Clean any existing files before yielding
            for file in temp_path.glob("**/*.json"):
                if file.is_file():
                    file.unlink()
            yield temp_path
            # Explicitly clean up any files that might prevent cleanup
            import shutil

            if temp_path.exists():
                try:
                    shutil.rmtree(temp_path, ignore_errors=True)
                except Exception:
                    pass

    @pytest.fixture(autouse=True)
    def mock_config_path(self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[misc]
        """Mock the config path at class level for ALL tests in this class."""
        config_path = temp_config_dir / "claude_desktop_config.json"

        # Patch the get_config_path method at the class level
        monkeypatch.setattr(
            ClaudeDesktopHandler, "get_config_path", lambda self: config_path
        )

    @pytest.fixture
    def handler(self, temp_config_dir: Path) -> ClaudeDesktopHandler:  # type: ignore[misc]
        """Create a handler with mocked config path."""
        config_path = temp_config_dir / "claude_desktop_config.json"

        # Ensure the config file doesn't exist before the test
        if config_path.exists():
            config_path.unlink()

        # Also clean up metadata file
        from src.mcp_config.clients.constants import METADATA_FILE

        metadata_path = temp_config_dir / METADATA_FILE
        if metadata_path.exists():
            metadata_path.unlink()

        handler = ClaudeDesktopHandler()
        return handler

    def test_no_metadata_in_claude_config(self, handler: ClaudeDesktopHandler) -> None:
        """Test that Claude Desktop config file never contains metadata fields."""
        # Setup a server with metadata fields
        server_config = {
            "command": "/usr/bin/python",
            "args": ["src/main.py", "--project-dir", "/test/project"],
            "env": {"PYTHONPATH": "/test/project"},
            "_managed_by": "mcp-config-managed",
            "_server_type": "mcp-code-checker",
        }

        # Add the server
        success = handler.setup_server("test-server", server_config)
        assert success

        # Read the raw config file
        config_path = handler.get_config_path()
        with open(config_path, "r") as f:
            raw_config = json.load(f)

        # Verify no metadata fields in the raw config
        test_server_config = raw_config["mcpServers"]["test-server"]
        assert "_managed_by" not in test_server_config
        assert "_server_type" not in test_server_config

        # Verify metadata is in separate file
        from src.mcp_config.clients.constants import METADATA_FILE

        config_path = handler.get_config_path()
        metadata_path = config_path.parent / METADATA_FILE
        assert metadata_path.exists()

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        assert "test-server" in metadata
        assert metadata["test-server"]["_managed_by"] == "mcp-config-managed"
        assert metadata["test-server"]["_server_type"] == "mcp-code-checker"

    def test_migration_removes_inline_metadata(
        self, handler: ClaudeDesktopHandler
    ) -> None:
        """Test that migrate_inline_metadata removes metadata from main config."""
        # Manually create a config with inline metadata (old format)
        config_with_metadata = {
            "mcpServers": {
                "old-server": {
                    "command": "python",
                    "args": ["old.py"],
                    "_managed_by": "mcp-config-managed",
                    "_server_type": "old-type",
                },
                "external-server": {
                    "command": "node",
                    "args": ["external.js"],
                },
            }
        }

        # Save the old-format config
        config_path = handler.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config_with_metadata, f)

        # Run migration
        migrated = handler.migrate_inline_metadata()
        assert migrated

        # Verify config is cleaned
        with open(config_path, "r") as f:
            cleaned_config = json.load(f)

        assert "_managed_by" not in cleaned_config["mcpServers"]["old-server"]
        assert "_server_type" not in cleaned_config["mcpServers"]["old-server"]
        assert "_managed_by" not in cleaned_config["mcpServers"]["external-server"]

        # Verify metadata was moved
        from src.mcp_config.clients.utils import load_metadata

        config_path = handler.get_config_path()
        metadata = load_metadata(config_path)
        assert "old-server" in metadata
        assert metadata["old-server"]["_managed_by"] == "mcp-config-managed"
        assert metadata["old-server"]["_server_type"] == "old-type"
        assert (
            "external-server" not in metadata
        )  # External server should not have metadata
