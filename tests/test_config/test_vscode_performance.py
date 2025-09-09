"""Functionality tests for VSCode support with large configs."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.mcp_config.clients import VSCodeHandler


class TestVSCodeFunctionality:
    """Test functionality aspects of VSCode support with various config sizes."""

    def test_large_config_handling(self, tmp_path: Path) -> None:
        """Test handling of large configuration files."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Create a large config with many servers
                large_config = {
                    "servers": {
                        f"server-{i}": {
                            "command": "python",
                            "args": ["-m", f"module_{i}", "--arg", f"value_{i}"],
                            "env": {f"ENV_{i}": f"value_{i}"},
                        }
                        for i in range(100)
                    }
                }

                # Create metadata for half of them (50 managed, 50 external)
                metadata = {
                    f"server-{i}": {
                        "_managed_by": "mcp-config-managed",
                        "_server_type": "mcp-code-checker",
                    }
                    for i in range(0, 50)
                }

                # Save config and metadata
                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(large_config, f)

                with open(config_dir / ".mcp-config-metadata.json", "w") as f:
                    json.dump(metadata, f)

                # Test that all servers are listed correctly
                servers = handler.list_all_servers()
                assert len(servers) == 100

                # Test that managed servers are filtered correctly
                managed = handler.list_managed_servers()
                assert len(managed) == 50
                
                # Verify that all managed servers have the correct metadata
                for server_name in managed:
                    assert server_name.startswith("server-")
                    server_id = int(server_name.split("-")[1])
                    assert 0 <= server_id < 50

    def test_repeated_operations(self, tmp_path: Path) -> None:
        """Test that repeated operations work correctly."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Perform multiple setup operations
                for i in range(10):
                    server_config = {
                        "command": "python",
                        "args": ["-m", "test_module", f"--iteration", str(i)],
                        "_server_type": "test-server",
                    }

                    handler.setup_server(f"test-{i}", server_config)

                # Verify all servers were set up correctly
                servers = handler.list_all_servers()
                assert len(servers) == 10
                
                # Check that each server has the correct configuration
                for i in range(10):
                    server_name = f"test-{i}"
                    assert server_name in servers
                    
                    # Verify the server was actually configured
                    config = handler.load_config()
                    server_config = config["servers"][server_name]
                    assert server_config["command"] == "python"
                    assert "--iteration" in server_config["args"]
                    assert str(i) in server_config["args"]

    def test_complex_config_validation(self, tmp_path: Path) -> None:
        """Test that validation works correctly with complex configs."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Create a complex config with nested structures
                complex_config = {
                    "servers": {
                        f"complex-{i}": {
                            "command": "python",
                            "args": [
                                "-m",
                                f"module_{i}",
                                "--config",
                                json.dumps({"nested": {"data": i}}),
                                "--paths",
                                ",".join([f"/path/{j}" for j in range(10)]),
                            ],
                            "env": {f"VAR_{j}": f"value_{i}_{j}" for j in range(20)},
                        }
                        for i in range(20)
                    }
                }

                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(complex_config, f)

                # Test validation functionality
                errors = handler.validate_config()
                assert len(errors) == 0  # Config should be valid
                
                # Verify all servers are recognized
                servers = handler.list_all_servers()
                assert len(servers) == 20
                
                # Verify complex args are preserved correctly
                config = handler.load_config()
                for i in range(20):
                    server_name = f"complex-{i}"
                    server_config = config["servers"][server_name]
                    
                    # Check that JSON args are properly formatted
                    config_arg_index = server_config["args"].index("--config")
                    json_arg = server_config["args"][config_arg_index + 1]
                    parsed_json = json.loads(json_arg)
                    assert parsed_json["nested"]["data"] == i
                    
                    # Check environment variables
                    assert len(server_config["env"]) == 20
                    assert f"VAR_0" in server_config["env"]
                    assert server_config["env"][f"VAR_0"] == f"value_{i}_0"

    def test_file_operations_functionality(self, tmp_path: Path) -> None:
        """Test that file operations work correctly."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Setup initial config
                initial_config = {
                    "command": "python",
                    "args": ["-m", "initial"],
                    "_server_type": "test",
                }

                handler.setup_server("test-server", initial_config)

                # Test backup operation functionality
                backup_path = handler.backup_config()
                assert backup_path.exists()
                
                # Verify backup contains the correct data
                with open(backup_path) as f:
                    backup_config = json.load(f)
                assert "servers" in backup_config
                assert "test-server" in backup_config["servers"]
                assert backup_config["servers"]["test-server"]["command"] == "python"

                # Test that config can be read and parsed correctly
                with open(config_file_path) as f:
                    config = json.load(f)
                assert "servers" in config
                assert "test-server" in config["servers"]
                
                # Verify the parsed config matches what we set up
                server_config = config["servers"]["test-server"]
                assert server_config["command"] == "python"
                assert server_config["args"] == ["-m", "initial"]

    @pytest.mark.parametrize("num_servers", [10, 50, 100])
    def test_multiple_servers_functionality(self, tmp_path: Path, num_servers: int) -> None:
        """Test that operations work correctly with varying numbers of servers."""
        import tempfile
        import uuid
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            
            handler = VSCodeHandler(workspace=True)
            
            # Patch the get_config_path method directly
            with patch.object(handler, 'get_config_path', return_value=config_file_path):
                # Create config with varying number of servers
                config = {
                    "servers": {
                        f"server-{i}": {"command": "python", "args": [f"script_{i}.py"]}
                        for i in range(num_servers)
                    }
                }

                config_dir = temp_path / ".vscode"
                config_dir.mkdir()

                with open(config_file_path, "w") as f:
                    json.dump(config, f)

                # Test list operation functionality
                servers = handler.list_all_servers()
                assert len(servers) == num_servers
                
                # Verify all expected servers are present
                for i in range(num_servers):
                    expected_name = f"server-{i}"
                    assert expected_name in servers
                    
                # Verify server configurations are correct
                loaded_config = handler.load_config()
                for i in range(num_servers):
                    server_name = f"server-{i}"
                    server_config = loaded_config["servers"][server_name]
                    assert server_config["command"] == "python"
                    assert server_config["args"] == [f"script_{i}.py"]

    def test_concurrent_operations_data_integrity(self, tmp_path: Path) -> None:
        """Test that concurrent operations maintain data integrity."""
        import threading
        
        # Use a unique directory to avoid test interference
        import uuid
        import tempfile
        with tempfile.TemporaryDirectory(suffix=f"_{uuid.uuid4().hex[:8]}") as temp_dir:
            temp_path = Path(temp_dir)
            config_file_path = temp_path / ".vscode" / "mcp.json"
            metadata_path = temp_path / ".vscode" / ".mcp-config-metadata.json"
            
            # Create and setup initial config
            setup_handler = VSCodeHandler(workspace=True)
            
            # Ensure clean initial state
            if config_file_path.exists():
                config_file_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Create isolated load functions for the setup phase
            def isolated_load_metadata_setup() -> dict[str, Any]:
                if not metadata_path.exists():
                    return {}
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        result: dict[str, Any] = json.load(f)
                        return result
                except (json.JSONDecodeError, IOError):
                    return {}
            
            def isolated_load_config_setup() -> dict[str, Any]:
                if not config_file_path.exists():
                    return {"servers": {}}
                try:
                    with open(config_file_path, "r", encoding="utf-8") as f:
                        config: dict[str, Any] = json.load(f)
                        if "servers" not in config:
                            config["servers"] = {}
                        return config
                except (json.JSONDecodeError, IOError):
                    return {"servers": {}}
            
            # Patch the handler's methods for complete isolation during setup
            with patch.object(setup_handler, 'get_config_path', return_value=config_file_path), \
                 patch.object(setup_handler, 'load_config', side_effect=isolated_load_config_setup), \
                 patch('src.mcp_config.clients.utils.load_metadata', side_effect=isolated_load_metadata_setup):
                setup_handler.setup_server(
                    "initial",
                    {"command": "python", "args": ["-m", "initial"], "_server_type": "test"},
                )
                
                # Verify the setup worked
                initial_servers = setup_handler.list_all_servers()
                assert len(initial_servers) == 1

                # Create multiple handlers for concurrent access
                handlers = [VSCodeHandler(workspace=True) for _ in range(5)]

                results = []
                errors = []
                
                # Use a barrier to synchronize thread start
                barrier = threading.Barrier(5)

                def read_operation(handler: VSCodeHandler, index: int) -> None:
                    """Simulate read operation with synchronization."""
                    try:
                        # Create isolated metadata loading for this handler
                        def isolated_load_metadata() -> dict[str, Any]:
                            if not metadata_path.exists():
                                return {}
                            try:
                                with open(metadata_path, "r", encoding="utf-8") as f:
                                    result: dict[str, Any] = json.load(f)
                                    return result
                            except (json.JSONDecodeError, IOError):
                                return {}
                        
                        # Patch each handler's get_config_path method and metadata loading
                        with patch.object(handler, 'get_config_path', return_value=config_file_path), \
                             patch('src.mcp_config.clients.utils.load_metadata', side_effect=isolated_load_metadata):
                            # Wait for all threads to be ready
                            barrier.wait()
                            
                            # Read the configuration
                            servers = handler.list_all_servers()
                            results.append((index, len(servers), list(servers)))
                    except Exception as e:
                        errors.append((index, str(e)))

                # Create threads for concurrent reads
                threads = []
                for i, handler in enumerate(handlers):
                    thread = threading.Thread(target=read_operation, args=(handler, i))
                    threads.append(thread)

                # Start all threads
                for thread in threads:
                    thread.start()

                # Wait for completion
                for thread in threads:
                    thread.join(timeout=10.0)

                # Test that operations completed without errors
                assert len(errors) == 0, f"Errors occurred: {errors}"
                
                # All threads should complete
                assert len(results) == 5, f"Expected 5 results, got {len(results)}"

                # Test data integrity - all should see consistent data
                server_counts = [count for _, count, _ in results]
                server_lists = [server_list for _, _, server_list in results]
                
                # All should see the same number of servers
                assert all(count == 1 for count in server_counts), f"Inconsistent server counts: {server_counts}"
                
                # All should see the same server name
                assert all("initial" in server_list for server_list in server_lists), "Missing 'initial' server in some results"
                
                # Verify the server configuration is still intact after concurrent access
                final_config = setup_handler.load_config()
                assert "servers" in final_config
                assert "initial" in final_config["servers"]
                assert final_config["servers"]["initial"]["command"] == "python"
