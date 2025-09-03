"""Test cases for PYTHONPATH and configuration fixes.

These tests specifically address the issues reported:
1. PYTHONPATH should be based on mcp-config environment, not project directory
2. mcp-server-filesystem should not have python-executable argument
3. log-file arguments should not be generated (allow auto-setting)
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.integration import generate_client_config
from src.mcp_config.servers import MCP_CODE_CHECKER, MCP_FILESYSTEM_SERVER


class TestPythonPathConfiguration:
    """Test that PYTHONPATH is correctly set to mcp-config directory, not project directory."""

    def test_pythonpath_should_use_mcp_config_dir_not_project_dir(self, tmp_path: Path) -> None:
        """Test that PYTHONPATH points to mcp-config directory where the virtual environment is."""
        # Setup paths
        project_dir = tmp_path / "mcp_coder_dummy"
        project_dir.mkdir()
        
        mcp_config_dir = tmp_path / "mcp-config"
        mcp_config_dir.mkdir()
        
        # Create a fake virtual environment in mcp-config
        venv_path = mcp_config_dir / ".venv"
        venv_path.mkdir()
        
        if sys.platform == "win32":
            scripts_dir = venv_path / "Scripts"
            scripts_dir.mkdir()
            python_exe = scripts_dir / "python.exe"
            checker_exe = scripts_dir / "mcp-code-checker.exe"
            filesystem_exe = scripts_dir / "mcp-server-filesystem.exe"
        else:
            bin_dir = venv_path / "bin"
            bin_dir.mkdir()
            python_exe = bin_dir / "python"
            checker_exe = bin_dir / "mcp-code-checker"
            filesystem_exe = bin_dir / "mcp-server-filesystem"
        
        python_exe.touch()
        checker_exe.touch()
        filesystem_exe.touch()
        
        # Test for MCP Code Checker
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
        }
        
        # Mock that we're running from mcp-config directory with its venv
        with patch("src.mcp_config.integration.Path.cwd", return_value=mcp_config_dir):
            with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
                mock_find.return_value = str(checker_exe)
                
                config = generate_client_config(
                    MCP_CODE_CHECKER,
                    "checker on p coder_dummy",
                    user_params,
                    python_executable=str(python_exe)
                )
                
                # PYTHONPATH should point to mcp-config directory, NOT project directory
                assert "env" in config
                assert "PYTHONPATH" in config["env"]
                
                pythonpath = config["env"]["PYTHONPATH"]
                
                # The current implementation incorrectly sets PYTHONPATH to project_dir
                # This test should FAIL with the current implementation
                expected_path = str(mcp_config_dir)
                if sys.platform == "win32" and not expected_path.endswith("\\"):
                    expected_path += "\\"
                    
                assert pythonpath == expected_path, (
                    f"PYTHONPATH should be mcp-config dir ({expected_path}), "
                    f"not project dir ({project_dir})"
                )

    def test_pythonpath_for_filesystem_server(self, tmp_path: Path) -> None:
        """Test PYTHONPATH for filesystem server should also use mcp-config dir."""
        # Setup paths  
        project_dir = tmp_path / "mcp_coder_dummy"
        project_dir.mkdir()
        
        mcp_config_dir = tmp_path / "mcp-config"
        mcp_config_dir.mkdir()
        
        # Test for MCP Filesystem Server
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
        }
        
        # Mock that we're running from mcp-config directory
        with patch("src.mcp_config.integration.Path.cwd", return_value=mcp_config_dir):
            config = generate_client_config(
                MCP_FILESYSTEM_SERVER,
                "fs on p coder_dummy",
                user_params,
            )
            
            # PYTHONPATH should point to mcp-config directory
            assert "env" in config
            assert "PYTHONPATH" in config["env"]
            
            pythonpath = config["env"]["PYTHONPATH"]
            
            # This test should FAIL with current implementation
            expected_path = str(mcp_config_dir)
            if sys.platform == "win32" and not expected_path.endswith("\\"):
                expected_path += "\\"
                
            assert pythonpath == expected_path, (
                f"PYTHONPATH should be mcp-config dir ({expected_path}), "
                f"not project dir ({project_dir})"
            )

    def test_pythonpath_with_explicit_venv(self, tmp_path: Path) -> None:
        """Test PYTHONPATH when venv is explicitly provided."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        
        mcp_config_dir = tmp_path / "mcp-config"
        mcp_config_dir.mkdir()
        
        venv_path = mcp_config_dir / ".venv"
        venv_path.mkdir()
        
        if sys.platform == "win32":
            scripts_dir = venv_path / "Scripts"
            scripts_dir.mkdir()
            python_exe = scripts_dir / "python.exe"
        else:
            bin_dir = venv_path / "bin"
            bin_dir.mkdir()
            python_exe = bin_dir / "python"
        
        python_exe.touch()
        
        user_params = {
            "project_dir": str(project_dir),
            "venv_path": str(venv_path),
        }
        
        with patch("src.mcp_config.integration.Path.cwd", return_value=mcp_config_dir):
            config = generate_client_config(
                MCP_CODE_CHECKER,
                "test",
                user_params,
            )
            
            # When venv is provided, PYTHONPATH should be based on venv's parent
            # (which is mcp-config dir in this case)
            assert "env" in config
            pythonpath = config["env"]["PYTHONPATH"]
            
            # The PYTHONPATH should be the parent of venv (mcp-config dir)
            expected_path = str(mcp_config_dir)
            if sys.platform == "win32" and not expected_path.endswith("\\"):
                expected_path += "\\"
            
            assert pythonpath == expected_path


class TestFilesystemServerArguments:
    """Test that mcp-server-filesystem doesn't get unnecessary arguments."""

    def test_filesystem_server_should_not_have_python_executable_arg(self, tmp_path: Path) -> None:
        """Test that filesystem server doesn't include --python-executable in its arguments."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
        }
        
        # Mock CLI command availability
        with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
            # Simulate CLI command is available
            if sys.platform == "win32":
                mock_find.return_value = r"C:\path\to\.venv\Scripts\mcp-server-filesystem.exe"
            else:
                mock_find.return_value = "/path/to/.venv/bin/mcp-server-filesystem"
            
            config = generate_client_config(
                MCP_FILESYSTEM_SERVER,
                "fs on p coder_dummy",
                user_params,
                python_executable="/usr/bin/python3"
            )
            
            # Check that --python-executable is NOT in the arguments
            # This test should FAIL with current implementation
            assert "--python-executable" not in config["args"], (
                "mcp-server-filesystem should not have --python-executable argument"
            )

    def test_code_checker_should_have_python_executable_arg(self, tmp_path: Path) -> None:
        """Test that code checker DOES include --python-executable in its arguments."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
        }
        
        # Mock CLI command availability
        with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
            # Simulate CLI command is available
            if sys.platform == "win32":
                mock_find.return_value = r"C:\path\to\.venv\Scripts\mcp-code-checker.exe"
            else:
                mock_find.return_value = "/path/to/.venv/bin/mcp-code-checker"
            
            config = generate_client_config(
                MCP_CODE_CHECKER,
                "checker on p coder_dummy",
                user_params,
                python_executable="/usr/bin/python3"
            )
            
            # Check that --python-executable IS in the arguments for code checker
            assert "--python-executable" in config["args"], (
                "mcp-code-checker should have --python-executable argument"
            )


class TestLogFileArguments:
    """Test that log-file arguments are not automatically generated."""

    def test_log_file_should_not_be_auto_generated_for_code_checker(self, tmp_path: Path) -> None:
        """Test that log-file is not automatically added to code checker arguments."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
            # Note: NOT providing log_file parameter
        }
        
        config = generate_client_config(
            MCP_CODE_CHECKER,
            "checker on p coder_dummy",
            user_params,
        )
        
        # This test should FAIL with current implementation
        # because auto_detect_log_file is called and adds log-file argument
        assert "--log-file" not in config["args"], (
            "log-file should not be auto-generated, let the server handle it"
        )

    def test_log_file_should_not_be_auto_generated_for_filesystem_server(self, tmp_path: Path) -> None:
        """Test that log-file is not automatically added to filesystem server arguments."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
            # Note: NOT providing log_file parameter
        }
        
        config = generate_client_config(
            MCP_FILESYSTEM_SERVER,
            "fs on p coder_dummy",
            user_params,
        )
        
        # This test should FAIL with current implementation
        assert "--log-file" not in config["args"], (
            "log-file should not be auto-generated for filesystem server"
        )

    def test_explicit_log_file_should_be_included(self, tmp_path: Path) -> None:
        """Test that explicitly provided log-file IS included in arguments."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        log_file = project_dir / "my_custom.log"
        
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "INFO",
            "log_file": str(log_file),  # Explicitly providing log file
        }
        
        config = generate_client_config(
            MCP_CODE_CHECKER,
            "checker",
            user_params,
        )
        
        # Explicitly provided log file SHOULD be included
        assert "--log-file" in config["args"]
        log_file_index = config["args"].index("--log-file")
        assert str(log_file) in config["args"][log_file_index + 1]


class TestCompleteConfigurationExamples:
    """Test complete configurations matching the examples from the issue report."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_configuration_example(self, tmp_path: Path) -> None:
        """Test that configuration matches the expected valid config from the issue."""
        # Simulate the paths from the example
        mcp_config_dir = Path(r"C:\Users\Marcu\Documents\GitHub\mcp-config")
        project_dir = Path(r"C:\Users\Marcu\Documents\GitHub\mcp_coder_dummy")
        
        # We'll use tmp_path to avoid actually creating these directories
        mock_mcp_config = tmp_path / "mcp-config"
        mock_project = tmp_path / "mcp_coder_dummy"
        mock_mcp_config.mkdir()
        mock_project.mkdir()
        
        venv_path = mock_mcp_config / ".venv"
        venv_path.mkdir()
        scripts_dir = venv_path / "Scripts"
        scripts_dir.mkdir()
        
        checker_exe = scripts_dir / "mcp-code-checker.exe"
        filesystem_exe = scripts_dir / "mcp-server-filesystem.exe"
        python_exe = scripts_dir / "python.exe"
        
        checker_exe.touch()
        filesystem_exe.touch()
        python_exe.touch()
        
        # Test Code Checker configuration
        user_params = {
            "project_dir": str(mock_project),
            "test_folder": "tests",
            "log_level": "INFO",
        }
        
        with patch("src.mcp_config.integration.Path.cwd", return_value=mock_mcp_config):
            with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
                with patch("src.mcp_config.integration.get_server_command_mode") as mock_mode:
                    mock_find.return_value = str(checker_exe)
                    mock_mode.return_value = "cli_command"  # Force CLI mode
                    
                    config = generate_client_config(
                        MCP_CODE_CHECKER,
                        "checker on p coder_dummy",
                        user_params,
                        python_executable=str(python_exe)
                    )
                    
                    # Verify command
                    assert str(checker_exe) in config["command"]
                
                # Verify arguments
                args = config["args"]
                assert "--project-dir" in args
                assert "--test-folder" in args
                assert "tests" in args
                assert "--log-level" in args
                assert "INFO" in args
                assert "--log-file" not in args  # Should not be auto-generated
                
                # Verify PYTHONPATH points to mcp-config, not project
                expected_pythonpath = str(mock_mcp_config) + "\\"
                assert config["env"]["PYTHONPATH"] == expected_pythonpath
        
        # Test Filesystem Server configuration
        user_params_fs = {
            "project_dir": str(mock_project),
            "log_level": "INFO",
        }
        
        with patch("src.mcp_config.integration.Path.cwd", return_value=mock_mcp_config):
            with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
                with patch("src.mcp_config.integration.get_server_command_mode") as mock_mode:
                    mock_find.return_value = str(filesystem_exe)
                    mock_mode.return_value = "cli_command"  # Force CLI mode
                    
                    config_fs = generate_client_config(
                        MCP_FILESYSTEM_SERVER,
                        "fs on p coder_dummy",
                        user_params_fs,
                        python_executable=str(python_exe)
                    )
                    
                    # Verify command
                    assert str(filesystem_exe) in config_fs["command"]
                
                # Verify arguments
                args_fs = config_fs["args"]
                assert "--project-dir" in args_fs
                assert "--log-level" in args_fs
                assert "INFO" in args_fs
                assert "--python-executable" not in args_fs  # Should not be present
                assert "--log-file" not in args_fs  # Should not be auto-generated
                
                # Verify PYTHONPATH
                assert config_fs["env"]["PYTHONPATH"] == expected_pythonpath

    def test_unix_configuration(self, tmp_path: Path) -> None:
        """Test configuration on Unix-like systems."""
        if sys.platform == "win32":
            pytest.skip("Unix-specific test")
        
        mcp_config_dir = tmp_path / "mcp-config"
        project_dir = tmp_path / "mcp_coder_dummy"
        mcp_config_dir.mkdir()
        project_dir.mkdir()
        
        venv_path = mcp_config_dir / ".venv"
        venv_path.mkdir()
        bin_dir = venv_path / "bin"
        bin_dir.mkdir()
        
        checker_exe = bin_dir / "mcp-code-checker"
        filesystem_exe = bin_dir / "mcp-server-filesystem"
        python_exe = bin_dir / "python"
        
        checker_exe.touch()
        filesystem_exe.touch()
        python_exe.touch()
        
        # Make executables actually executable on Unix
        checker_exe.chmod(0o755)
        filesystem_exe.chmod(0o755)
        python_exe.chmod(0o755)
        
        # Test configuration
        user_params = {
            "project_dir": str(project_dir),
            "log_level": "DEBUG",
        }
        
        with patch("src.mcp_config.integration.Path.cwd", return_value=mcp_config_dir):
            with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
                mock_find.return_value = str(filesystem_exe)
                
                config = generate_client_config(
                    MCP_FILESYSTEM_SERVER,
                    "fs on p coder_dummy",
                    user_params,
                    python_executable=str(python_exe)
                )
                
                # Verify PYTHONPATH (no trailing slash on Unix)
                expected_pythonpath = str(mcp_config_dir)
                assert config["env"]["PYTHONPATH"] == expected_pythonpath
                
                # Verify no python-executable for filesystem server
                assert "--python-executable" not in config["args"]
                
                # Verify no auto-generated log file
                assert "--log-file" not in config["args"]


class TestServerSpecificBehavior:
    """Test that different servers have appropriate different behaviors."""

    def test_code_checker_vs_filesystem_parameter_differences(self, tmp_path: Path) -> None:
        """Test that code checker and filesystem server have correct parameter differences."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        mcp_config_dir = tmp_path / "mcp-config"
        mcp_config_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
        }
        
        with patch("src.mcp_config.integration.Path.cwd", return_value=mcp_config_dir):
            # Generate config for code checker
            checker_config = generate_client_config(
                MCP_CODE_CHECKER,
                "checker",
                user_params,
            )
            
            # Generate config for filesystem server
            fs_config = generate_client_config(
                MCP_FILESYSTEM_SERVER,
                "fs",
                user_params,
            )
            
            # Both should have same PYTHONPATH (mcp-config dir)
            expected_pythonpath = str(mcp_config_dir)
            if sys.platform == "win32" and not expected_pythonpath.endswith("\\"):
                expected_pythonpath += "\\"
            
            assert checker_config["env"]["PYTHONPATH"] == expected_pythonpath
            assert fs_config["env"]["PYTHONPATH"] == expected_pythonpath
            
            # Code checker may have python-executable, filesystem should not
            # (when using CLI commands)
            with patch("src.mcp_config.integration._find_cli_executable") as mock_find:
                mock_find.return_value = "/usr/bin/mcp-server-filesystem"
                
                fs_config_cli = generate_client_config(
                    MCP_FILESYSTEM_SERVER,
                    "fs",
                    user_params,
                )
                
                assert "--python-executable" not in fs_config_cli["args"]

    def test_both_servers_no_auto_log_file(self, tmp_path: Path) -> None:
        """Test that neither server gets auto-generated log files."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        user_params = {
            "project_dir": str(project_dir),
        }
        
        checker_config = generate_client_config(
            MCP_CODE_CHECKER,
            "checker",
            user_params,
        )
        
        fs_config = generate_client_config(
            MCP_FILESYSTEM_SERVER,
            "fs",
            user_params,
        )
        
        # Neither should have auto-generated log files
        assert "--log-file" not in checker_config["args"]
        assert "--log-file" not in fs_config["args"]
