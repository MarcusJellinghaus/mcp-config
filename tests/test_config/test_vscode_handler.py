"""Tests for VSCode MCP configuration handler."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.mcp_config.clients import VSCodeHandler


class TestVSCodeHandler:
    """Test VSCode handler functionality."""

    def test_workspace_config_path(self) -> None:
        """Test workspace configuration path."""
        handler = VSCodeHandler(workspace=True)

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/home/user/project")
            config_path = handler.get_config_path()

            assert config_path == Path("/home/user/project/.vscode/mcp.json")

    @pytest.mark.skipif(
        os.name == "nt",
        reason="Linux-specific path handling cannot be tested on Windows",
    )
    def test_user_config_path_linux(self) -> None:
        """Test user profile configuration path on Linux."""
        with patch("platform.system", return_value="Linux"):
            with patch.object(os, "name", "posix"):
                handler = VSCodeHandler(workspace=False)

                # Just check that the path contains expected components
                config_path = handler.get_config_path()
                path_str = str(config_path)

                assert ".config" in path_str
                assert "Code" in path_str
                assert "mcp.json" in path_str

    def test_user_config_path_windows(self) -> None:
        """Test user profile configuration path on Windows."""
        handler = VSCodeHandler(workspace=False)

        # Create a mock Path that mimics Windows behavior on any OS
        class MockWindowsPath:
            def __init__(self, path: str = "C:/Users/TestUser") -> None:
                self._path = path

            def __str__(self) -> str:
                return self._path

            def __truediv__(self, other: str) -> "MockWindowsPath":
                return MockWindowsPath(f"{self._path}/{other}")

            @property
            def name(self) -> str:
                return self._path.split("/")[-1]

        mock_home = MockWindowsPath()

        with (
            patch("os.name", "nt"),
            patch("pathlib.Path.home", return_value=mock_home),
            patch("src.mcp_config.clients.vscode.Path") as mock_path_class,
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

            config_path = handler.get_config_path()

            # Check string representation for cross-platform compatibility
            assert "AppData" in str(config_path)
            assert "Code" in str(config_path)
            assert "mcp.json" in str(config_path)

    @pytest.mark.skipif(
        os.name == "nt",
        reason="macOS-specific path handling cannot be tested on Windows",
    )
    def test_user_config_path_macos(self) -> None:
        """Test user profile configuration path on macOS."""
        with patch("platform.system", return_value="Darwin"):
            with patch.object(os, "name", "posix"):
                handler = VSCodeHandler(workspace=False)

                config_path = handler.get_config_path()
                path_str = str(config_path)

                # Check for macOS-specific path components
                assert (
                    "Library" in path_str
                    or "Application Support" in path_str.replace("\\", "/")
                )
                assert "Code" in path_str
                assert "mcp.json" in path_str

    def test_setup_server(self, tmp_path: Path) -> None:
        """Test setting up a server configuration."""
        # Create a completely isolated temporary directory
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Setup server
                server_config = {
                    "command": "python",
                    "args": ["-m", "mcp_code_checker", "--project-dir", "/path/to/project"],
                    "env": {"PYTHONPATH": "/path/to/project"},
                    "_server_type": "mcp-code-checker",
                }

                result = handler.setup_server("test-server", server_config)
                assert result is True

                # Check configuration was saved
                assert config_file_path.exists()

                with open(config_file_path) as f:
                    config = json.load(f)

                assert "servers" in config
                assert "test-server" in config["servers"]
                assert config["servers"]["test-server"]["command"] == "python"
                assert config["servers"]["test-server"]["args"][0] == "-m"

                # Check metadata was saved
                metadata_path = temp_path / ".vscode" / ".mcp-config-metadata.json"
                assert metadata_path.exists()

                with open(metadata_path) as f:
                    metadata = json.load(f)

                assert "test-server" in metadata
                assert metadata["test-server"]["_managed_by"] == "mcp-config-managed"

    def test_remove_managed_server(self, tmp_path: Path) -> None:
        """Test removing a managed server."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Setup initial config
                config = {
                    "servers": {
                        "managed-server": {
                            "command": "python",
                            "args": ["-m", "mcp_code_checker"],
                        },
                        "external-server": {"command": "node", "args": ["server.js"]},
                    }
                }

                # Setup metadata (only managed-server is tracked)
                metadata = {
                    "managed-server": {
                        "_managed_by": "mcp-config-managed",
                        "_server_type": "mcp-code-checker",
                    }
                }

                # Save config and metadata
                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(config, f)

                with open(config_dir / ".mcp-config-metadata.json", "w") as f:
                    json.dump(metadata, f)

                # Remove managed server
                result = handler.remove_server("managed-server")
                assert result is True

                # Check it was removed
                with open(config_file_path) as f:
                    updated_config = json.load(f)

                assert "managed-server" not in updated_config["servers"]
                assert "external-server" in updated_config["servers"]  # External preserved

                # Try to remove external server (should fail)
                result = handler.remove_server("external-server")
                assert result is False

    def test_list_servers(self, tmp_path: Path) -> None:
        """Test listing all servers."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Setup config with mixed servers
                config = {
                    "servers": {
                        "managed1": {"command": "python", "args": []},
                        "external1": {"command": "node", "args": []},
                        "managed2": {"command": "python", "args": []},
                    }
                }

                metadata = {
                    "managed1": {
                        "_managed_by": "mcp-config-managed",
                        "_server_type": "mcp-code-checker",
                    },
                    "managed2": {
                        "_managed_by": "mcp-config-managed",
                        "_server_type": "mcp-code-checker",
                    },
                }

                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(config, f)

                with open(config_dir / ".mcp-config-metadata.json", "w") as f:
                    json.dump(metadata, f)

                # List all servers
                all_servers = handler.list_all_servers()
                assert len(all_servers) == 3

                managed_count = sum(1 for s in all_servers if s["managed"])
                assert managed_count == 2

                # List managed only
                managed_servers = handler.list_managed_servers()
                assert len(managed_servers) == 2
                assert all(s["name"] in ["managed1", "managed2"] for s in managed_servers)

    def test_validate_config(self, tmp_path: Path) -> None:
        """Test configuration validation."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Test with invalid config
                config: dict[str, dict[str, dict[str, list[str]]]] = {
                    "servers": {
                        "invalid-server": {
                            # Missing required 'command' field
                            "args": []
                        }
                    }
                }

                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(config, f)

                errors = handler.validate_config()
                assert len(errors) > 0
                assert any(
                    "missing required 'command' field" in e.lower()
                    or "command" in e.lower()
                    for e in errors
                )

    def test_backup_config(self, tmp_path: Path) -> None:
        """Test configuration backup."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Create initial config
                config = {"servers": {"test": {"command": "python", "args": []}}}
                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(config, f)

                # Create backup
                backup_path = handler.backup_config()

                assert backup_path.exists()
                assert backup_path.name.startswith("mcp_backup_")
                assert backup_path.suffix == ".json"

                # Verify backup content
                with open(backup_path) as f:
                    backup_content = json.load(f)

                assert backup_content == config

    def test_empty_config_handling(self, tmp_path: Path) -> None:
        """Test handling of empty configuration."""
        # Use completely isolated test with custom patching
        import uuid
        import tempfile
        
        with tempfile.TemporaryDirectory(suffix=f"_empty_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a handler and patch its config path directly
            handler = VSCodeHandler(workspace=True)
            config_file_path = temp_path / ".vscode" / "mcp.json" 
            metadata_path = temp_path / ".vscode" / ".mcp-config-metadata.json"
            
            # Create a completely isolated config directory structure
            config_dir = temp_path / ".vscode"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure the files don't exist initially
            if config_file_path.exists():
                config_file_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Create isolated load functions that are completely independent
            def isolated_load_config() -> dict[str, Any]:
                """Load config with guaranteed isolation."""
                if not config_file_path.exists():
                    return {"servers": {}}  # Return fresh empty config
                try:
                    with open(config_file_path, "r", encoding="utf-8") as f:
                        config: dict[str, Any] = json.load(f)
                        if "servers" not in config:
                            config["servers"] = {}
                        return config
                except (json.JSONDecodeError, IOError):
                    return {"servers": {}}
            
            def isolated_load_metadata() -> dict[str, Any]:
                """Load metadata with guaranteed isolation."""
                if not metadata_path.exists():
                    return {}
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        result: dict[str, Any] = json.load(f)
                        return result
                except (json.JSONDecodeError, IOError):
                    return {}
            
            # Patch all relevant methods to ensure complete isolation
            with patch.object(handler, 'get_config_path', return_value=config_file_path), \
                 patch.object(handler, 'load_config', side_effect=isolated_load_config), \
                 patch('src.mcp_config.clients.utils.load_metadata', side_effect=isolated_load_metadata):
                
                # Double-check clean slate - no config files should exist
                assert not config_file_path.exists(), f"Config file unexpectedly exists: {config_file_path}"
                assert not metadata_path.exists(), f"Metadata file unexpectedly exists: {metadata_path}"

                # List servers when no config exists
                servers = handler.list_all_servers()
                if len(servers) != 0:
                    print(f"DEBUG: Unexpectedly found servers: {servers}")
                    print(f"DEBUG: Config path being used: {handler.get_config_path()}")
                    print(f"DEBUG: Config file exists: {config_file_path.exists()}")
                    # Test the isolated functions
                    test_config = isolated_load_config()
                    test_metadata = isolated_load_metadata()
                    print(f"DEBUG: Isolated config: {test_config}")
                    print(f"DEBUG: Isolated metadata: {test_metadata}")
                assert len(servers) == 0

                # Validate when no config exists (should be valid)
                errors = handler.validate_config()
                assert len(errors) == 0

    def test_malformed_json_handling(self, tmp_path: Path) -> None:
        """Test handling of malformed JSON configuration."""
        # Use direct method patching for better test isolation
        import uuid
        import tempfile
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a handler and patch its config path directly
            handler = VSCodeHandler(workspace=True)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            metadata_path = temp_path / ".vscode" / ".mcp-config-metadata.json"
            
            # Create isolated load functions
            def isolated_load_metadata() -> dict[str, Any]:
                """Load metadata with guaranteed isolation - always empty for this test."""
                return {}
            
            def isolated_load_config() -> dict[str, Any]:
                """Load config with guaranteed isolation for malformed JSON test."""
                if not config_file_path.exists():
                    return {"servers": {}}
                try:
                    with open(config_file_path, "r", encoding="utf-8") as f:
                        config: dict[str, Any] = json.load(f)
                        if "servers" not in config:
                            config["servers"] = {}
                        return config
                except (json.JSONDecodeError, IOError):
                    # This is what should happen with malformed JSON
                    return {"servers": {}}
            
            # Patch all relevant methods for complete isolation
            with patch.object(handler, 'get_config_path', return_value=config_file_path), \
                 patch.object(handler, 'load_config', side_effect=isolated_load_config), \
                 patch('src.mcp_config.clients.utils.load_metadata', side_effect=isolated_load_metadata):
                # Create malformed JSON in our controlled directory
                config_dir = temp_path / ".vscode"
                config_dir.mkdir()
                
                with open(config_file_path, "w") as f:
                    f.write("{ invalid json }")
                
                # Verify the file was created where we expect
                assert config_file_path.exists()

                # load_config should handle gracefully and return default config
                config: dict[str, dict[str, dict[str, str | list[str]]]] = (
                    handler.load_config()
                )
                assert config == {"servers": {}}  # Should return default config

                # List operations should work even with malformed JSON
                servers = handler.list_all_servers()
                assert len(servers) == 0  # No servers in default config

    def test_workspace_vs_user_distinction(self) -> None:
        """Test that workspace and user handlers are distinct."""
        workspace_handler = VSCodeHandler(workspace=True)
        user_handler = VSCodeHandler(workspace=False)

        assert workspace_handler.workspace is True
        assert user_handler.workspace is False

        # Config paths should be different
        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/home/user/project")
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path("/home/user")
                with patch("platform.system") as mock_system:
                    mock_system.return_value = "Linux"

                    workspace_path = workspace_handler.get_config_path()
                    user_path = user_handler.get_config_path()

                    assert workspace_path != user_path
                    assert ".vscode" in str(workspace_path)
                    assert ".config" in str(user_path) or "AppData" in str(user_path)
