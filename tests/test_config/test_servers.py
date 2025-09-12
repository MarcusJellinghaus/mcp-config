"""Tests for the MCP server configuration data model."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_config.servers import (
    MCP_CODE_CHECKER,
    MCP_FILESYSTEM_SERVER,
    ParameterDef,
    ServerConfig,
    ServerRegistry,
    registry,
)


class TestParameterDef:
    """Test the ParameterDef class."""

    def test_valid_parameter_creation(self) -> None:
        """Test creating valid parameters."""
        # String parameter with new fields
        param = ParameterDef(
            name="test-param",
            arg_name="--test-param",
            param_type="string",
            help="Test parameter",
            auto_detect=False,
            validator=None,
        )
        assert param.name == "test-param"
        assert param.arg_name == "--test-param"
        assert param.param_type == "string"
        assert not param.required
        assert param.auto_detect is False
        assert param.validator is None

        # Boolean flag
        flag = ParameterDef(
            name="verbose",
            arg_name="--verbose",
            param_type="boolean",
            is_flag=True,
            default=False,
        )
        assert flag.is_flag
        assert flag.default is False

        # Choice parameter
        choice = ParameterDef(
            name="level",
            arg_name="--level",
            param_type="choice",
            choices=["low", "medium", "high"],
            default="medium",
        )
        assert choice.choices == ["low", "medium", "high"]
        assert choice.default == "medium"

    def test_invalid_parameter_type(self) -> None:
        """Test that invalid parameter types raise errors."""
        with pytest.raises(ValueError, match="Invalid param_type"):
            ParameterDef(name="test", arg_name="--test", param_type="invalid")

    def test_empty_name_validation(self) -> None:
        """Test that empty names are rejected."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            ParameterDef(name="", arg_name="--test", param_type="string")

        with pytest.raises(ValueError, match="must be a non-empty string"):
            ParameterDef(name="test", arg_name="", param_type="string")

    def test_choice_parameter_validation(self) -> None:
        """Test choice parameter validation."""
        # No choices provided
        with pytest.raises(ValueError, match="must have a non-empty choices list"):
            ParameterDef(name="level", arg_name="--level", param_type="choice")

        # Empty choices list
        with pytest.raises(ValueError, match="must have at least one choice"):
            ParameterDef(
                name="level", arg_name="--level", param_type="choice", choices=[]
            )

    def test_boolean_flag_validation(self) -> None:
        """Test boolean flag validation."""
        # Valid boolean flag with boolean default
        param = ParameterDef(
            name="flag",
            arg_name="--flag",
            param_type="boolean",
            is_flag=True,
            default=True,
        )
        assert param.default is True

        # Invalid non-boolean default for flag
        with pytest.raises(ValueError, match="must have a boolean default"):
            ParameterDef(
                name="flag",
                arg_name="--flag",
                param_type="boolean",
                is_flag=True,
                default="not_a_bool",
            )

    def test_parameter_def_with_repeatable(self) -> None:
        """Test ParameterDef supports repeatable=True and defaults to False."""
        # Test with repeatable=True
        param_true = ParameterDef(
            name="test-param",
            arg_name="--test-param", 
            param_type="string",
            repeatable=True
        )
        assert param_true.repeatable is True
        
        # Test default (repeatable=False)
        param_default = ParameterDef(
            name="test-param",
            arg_name="--test-param",
            param_type="string"
        )
        assert param_default.repeatable is False

    def test_parameter_def_existing_functionality(self) -> None:
        """Test existing ParameterDef creation still works."""
        # Test with existing parameters from MCP_CODE_CHECKER
        param = ParameterDef(
            name="project-dir",
            arg_name="--project-dir",
            param_type="path",
            required=True
        )
        assert param.repeatable is False  # Default value
        assert param.required is True


class TestServerConfig:
    """Test the ServerConfig class."""

    def test_mcp_code_checker_configuration(self) -> None:
        """Test that MCP Code Checker configuration is complete."""
        assert MCP_CODE_CHECKER.name == "mcp-code-checker"
        assert MCP_CODE_CHECKER.display_name == "MCP Code Checker"
        assert MCP_CODE_CHECKER.main_module == "src/main.py"
        assert len(MCP_CODE_CHECKER.parameters) == 7

        # Check all parameter names are present
        param_names = [p.name for p in MCP_CODE_CHECKER.parameters]
        expected_names = [
            "project-dir",
            "python-executable",
            "venv-path",
            "test-folder",
            "keep-temp-files",
            "log-level",
            "log-file",
        ]
        assert set(param_names) == set(expected_names)

    def test_mcp_filesystem_server_configuration(self) -> None:
        """Test that MCP Filesystem Server configuration is complete."""
        assert MCP_FILESYSTEM_SERVER.name == "mcp-server-filesystem"
        assert MCP_FILESYSTEM_SERVER.display_name == "MCP Filesystem Server"
        assert MCP_FILESYSTEM_SERVER.main_module == "src/mcp_server_filesystem/main.py"
        assert len(MCP_FILESYSTEM_SERVER.parameters) == 5

        # Check all parameter names are present
        param_names = [p.name for p in MCP_FILESYSTEM_SERVER.parameters]
        expected_names = [
            "project-dir",
            "python-executable",
            "venv-path",
            "log-level",
            "log-file",
        ]
        assert set(param_names) == set(expected_names)

        # Check project-dir is required
        project_dir_param = MCP_FILESYSTEM_SERVER.get_parameter_by_name("project-dir")
        assert project_dir_param is not None
        assert project_dir_param.required is True
        assert project_dir_param.param_type == "path"

        # Check log-level choices
        log_level_param = MCP_FILESYSTEM_SERVER.get_parameter_by_name("log-level")
        assert log_level_param is not None
        assert log_level_param.param_type == "choice"
        assert log_level_param.default == "INFO"
        assert log_level_param.choices == [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

        # Check log-file is optional path with auto-detect
        log_file_param = MCP_FILESYSTEM_SERVER.get_parameter_by_name("log-file")
        assert log_file_param is not None
        assert log_file_param.param_type == "path"
        assert log_file_param.required is False
        assert log_file_param.auto_detect is True

        # Check python-executable has auto-detect
        python_exe_param = MCP_FILESYSTEM_SERVER.get_parameter_by_name(
            "python-executable"
        )
        assert python_exe_param is not None
        assert python_exe_param.param_type == "path"
        assert python_exe_param.required is False
        assert python_exe_param.auto_detect is True

        # Check venv-path has auto-detect
        venv_param = MCP_FILESYSTEM_SERVER.get_parameter_by_name("venv-path")
        assert venv_param is not None
        assert venv_param.param_type == "path"
        assert venv_param.required is False
        assert venv_param.auto_detect is True

    def test_auto_detect_parameters(self) -> None:
        """Test that auto-detect is set for appropriate parameters."""
        # Test MCP Code Checker auto-detect parameters
        code_checker_auto = [
            p.name for p in MCP_CODE_CHECKER.parameters if p.auto_detect
        ]

        # These should have auto-detect for code checker
        assert "python-executable" in code_checker_auto
        assert "venv-path" in code_checker_auto
        assert (
            "log-file" in code_checker_auto
        )  # log-file now HAS auto-detect for code checker

        # These should NOT have auto-detect
        code_checker_non_auto = [
            p.name for p in MCP_CODE_CHECKER.parameters if not p.auto_detect
        ]
        assert "project-dir" in code_checker_non_auto
        assert "test-folder" in code_checker_non_auto
        assert "keep-temp-files" in code_checker_non_auto
        assert "log-level" in code_checker_non_auto
        # Note: log-file now HAS auto-detect for code checker too!

        # Test MCP Filesystem Server auto-detect parameters
        filesystem_auto = [
            p.name for p in MCP_FILESYSTEM_SERVER.parameters if p.auto_detect
        ]

        # These should have auto-detect for filesystem server
        assert "python-executable" in filesystem_auto
        assert "venv-path" in filesystem_auto
        assert (
            "log-file" in filesystem_auto
        )  # log-file IS auto-detect for filesystem server

        # These should NOT have auto-detect
        filesystem_non_auto = [
            p.name for p in MCP_FILESYSTEM_SERVER.parameters if not p.auto_detect
        ]
        assert "project-dir" in filesystem_non_auto
        assert "log-level" in filesystem_non_auto

    def test_generate_args_basic(self) -> None:
        """Test basic argument generation."""
        config = ServerConfig(
            name="test-server",
            display_name="Test Server",
            main_module="main.py",
            parameters=[
                ParameterDef(
                    name="input", arg_name="--input", param_type="string", required=True
                ),
                ParameterDef(name="output", arg_name="--output", param_type="string"),
            ],
        )

        args = config.generate_args({"input": "test.txt", "output": "out.txt"})
        assert args == ["main.py", "--input", "test.txt", "--output", "out.txt"]

    @patch("src.mcp_config.validation.auto_detect_python_executable")
    @patch("src.mcp_config.validation.auto_detect_venv_path")
    def test_generate_args_with_auto_detection(
        self, mock_venv: MagicMock, mock_python: MagicMock
    ) -> None:
        """Test argument generation with auto-detection."""
        # Setup mocks
        mock_python.return_value = Path("/auto/python")
        mock_venv.return_value = Path("/auto/venv")

        config = ServerConfig(
            name="test-server",
            display_name="Test Server",
            main_module="test.py",
            parameters=[
                ParameterDef(
                    name="project-dir",
                    arg_name="--project-dir",
                    param_type="path",
                    required=True,
                ),
                ParameterDef(
                    name="python-executable",
                    arg_name="--python-executable",
                    param_type="path",
                    auto_detect=True,
                ),
                ParameterDef(
                    name="venv-path",
                    arg_name="--venv-path",
                    param_type="path",
                    auto_detect=True,
                ),
            ],
        )

        # Only provide project-dir, let others auto-detect
        user_params = {"project_dir": "/test/project"}
        args = config.generate_args(user_params)

        # Check that auto-detected values are included
        assert "--python-executable" in args
        # Find the index and check the actual value (platform-agnostic)
        python_idx = args.index("--python-executable")
        assert "auto" in args[python_idx + 1] and "python" in args[python_idx + 1]

        assert "--venv-path" in args
        venv_idx = args.index("--venv-path")
        assert "auto" in args[venv_idx + 1] and "venv" in args[venv_idx + 1]

    def test_generate_args_with_flags(self) -> None:
        """Test argument generation with boolean flags."""
        config = ServerConfig(
            name="test",
            display_name="Test",
            main_module="test.py",
            parameters=[
                ParameterDef(
                    name="verbose",
                    arg_name="--verbose",
                    param_type="boolean",
                    is_flag=True,
                ),
                ParameterDef(
                    name="quiet", arg_name="--quiet", param_type="boolean", is_flag=True
                ),
            ],
        )

        # Only verbose flag set
        args = config.generate_args({"verbose": True, "quiet": False})
        assert args == ["test.py", "--verbose"]

        # Both flags set
        args = config.generate_args({"verbose": True, "quiet": True})
        assert "--verbose" in args
        assert "--quiet" in args

    def test_generate_args_with_defaults(self) -> None:
        """Test argument generation using default values."""
        config = ServerConfig(
            name="test",
            display_name="Test",
            main_module="test.py",
            parameters=[
                ParameterDef(
                    name="level",
                    arg_name="--level",
                    param_type="choice",
                    choices=["low", "high"],
                    default="low",
                )
            ],
        )

        # Use default
        args = config.generate_args({})
        assert args == ["test.py", "--level", "low"]

        # Override default
        args = config.generate_args({"level": "high"})
        assert args == ["test.py", "--level", "high"]

    def test_generate_args_mcp_code_checker(self) -> None:
        """Test argument generation for MCP Code Checker."""
        # Use a temporary directory to avoid permission issues
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            # Use underscore format as it comes from argparse
            params = {
                "project_dir": str(project_dir),
                "log_level": "DEBUG",
                "keep_temp_files": True,
                "test_folder": "custom_tests",
            }

            args = MCP_CODE_CHECKER.generate_args(params)

            # For MCP Code Checker, the first argument should be absolute path to main.py
            assert args[0].endswith("main.py")
            assert "--project-dir" in args
            # Path will be normalized on Windows
            proj_idx = args.index("--project-dir")
            assert str(project_dir) in args[proj_idx + 1] or args[proj_idx + 1] == str(
                project_dir
            )

            assert "--log-level" in args
            assert "DEBUG" in args
            assert "--keep-temp-files" in args
            assert "--test-folder" in args
            assert "custom_tests" in args

            # Auto-detected parameters should be present
            assert "--python-executable" in args  # auto-detected
            # log-file is no longer auto-detected, so it won't be present unless explicitly provided

    @patch("src.mcp_config.validation.auto_detect_python_executable")
    @patch("src.mcp_config.validation.auto_detect_venv_path")
    def test_generate_args_mcp_filesystem_server(
        self, mock_venv: MagicMock, mock_python: MagicMock
    ) -> None:
        """Test argument generation for MCP Filesystem Server with auto-detection."""
        # Setup mocks
        mock_python.return_value = Path("/auto/python")
        mock_venv.return_value = Path("/auto/venv")

        # Use underscore format as it comes from argparse
        params = {
            "project_dir": "/path/to/project",
            "log_level": "DEBUG",
        }

        args = MCP_FILESYSTEM_SERVER.generate_args(params)

        # Should include auto-detected values
        assert "--project-dir" in args
        proj_idx = args.index("--project-dir")
        assert (
            "path" in args[proj_idx + 1].lower()
            and "project" in args[proj_idx + 1].lower()
        )

        assert "--log-level" in args
        assert "DEBUG" in args

        # Auto-detected parameters should be present
        assert "--python-executable" in args
        python_idx = args.index("--python-executable")
        assert "auto" in args[python_idx + 1] and "python" in args[python_idx + 1]

        assert "--venv-path" in args
        venv_idx = args.index("--venv-path")
        assert "auto" in args[venv_idx + 1] and "venv" in args[venv_idx + 1]

        # log-file should NOT be auto-detected (only included when explicitly provided)
        assert "--log-file" not in args

        # Test with explicit log file
        params_with_log = {
            "project_dir": "/path/to/project",
            "log_level": "DEBUG",
            "log_file": "/path/to/log.log",
        }

        args_with_log = MCP_FILESYSTEM_SERVER.generate_args(params_with_log)
        assert "--log-file" in args_with_log
        log_idx = args_with_log.index("--log-file")
        assert "log.log" in args_with_log[log_idx + 1]

    def test_mcp_filesystem_server_minimal_config(self) -> None:
        """Test minimal configuration for MCP Filesystem Server."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            params = {
                "project_dir": str(project_dir),
            }

            args = MCP_FILESYSTEM_SERVER.generate_args(params)

            # Should include required parameter
            assert "--project-dir" in args

            # Should include default log level
            assert "--log-level" in args
            assert "INFO" in args

            # Auto-detected parameters will be included if detection succeeds
            # This depends on the actual environment, so we just check the method works
            assert isinstance(args, list)
            assert len(args) > 0

    def test_get_required_params(self) -> None:
        """Test getting required parameters."""
        config = ServerConfig(
            name="test",
            display_name="Test",
            main_module="test.py",
            parameters=[
                ParameterDef(
                    name="required1",
                    arg_name="--required1",
                    param_type="string",
                    required=True,
                ),
                ParameterDef(
                    name="optional",
                    arg_name="--optional",
                    param_type="string",
                    required=False,
                ),
                ParameterDef(
                    name="required2",
                    arg_name="--required2",
                    param_type="string",
                    required=True,
                ),
            ],
        )

        required = config.get_required_params()
        assert set(required) == {"required1", "required2"}
        assert "optional" not in required

    def test_validate_project_mcp_code_checker(self) -> None:
        """Test project validation for MCP Code Checker."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # The validation should pass if:
            # 1. CLI command is available, OR
            # 2. Package is installed, OR
            # 3. Development structure exists
            # In test environment, may not have package installed,
            # so create development structure for validation
            if not MCP_CODE_CHECKER.validate_project(project_dir):
                # Create development structure
                src_dir = project_dir / "src"
                src_dir.mkdir(exist_ok=True)
                main_file = src_dir / "main.py"
                main_file.write_text("# Main module")
            else:
                # If validation already passes, ensure src directory exists for the next check
                src_dir = project_dir / "src"
                if not src_dir.exists():
                    src_dir.mkdir(exist_ok=True)
                    main_file = src_dir / "main.py"
                    main_file.write_text("# Main module")

            # Now it should validate
            assert MCP_CODE_CHECKER.validate_project(project_dir)

    def test_validate_project_mcp_filesystem_server(self) -> None:
        """Test enhanced project validation for MCP Filesystem Server."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Basic validation should pass for readable directory
            assert MCP_FILESYSTEM_SERVER.validate_project(project_dir)

            # Create some test content
            test_file = project_dir / "test.txt"
            test_file.write_text("test content")

            # Should still validate with content
            assert MCP_FILESYSTEM_SERVER.validate_project(project_dir)

            # Test with non-existent directory
            non_existent = project_dir / "does_not_exist"
            assert not MCP_FILESYSTEM_SERVER.validate_project(non_existent)

            # Test with file instead of directory
            assert not MCP_FILESYSTEM_SERVER.validate_project(test_file)

    def test_get_parameter_by_name(self) -> None:
        """Test parameter lookup by name."""
        param = MCP_CODE_CHECKER.get_parameter_by_name("project-dir")
        assert param is not None
        assert param.name == "project-dir"
        assert param.required is True

        param = MCP_CODE_CHECKER.get_parameter_by_name("log-level")
        assert param is not None
        assert param.param_type == "choice"
        assert param.default == "INFO"

        # Non-existent parameter
        param = MCP_CODE_CHECKER.get_parameter_by_name("non-existent")
        assert param is None


class TestServerRegistry:
    """Test the ServerRegistry class."""

    def test_register_and_get(self) -> None:
        """Test server registration and retrieval."""
        registry_test = ServerRegistry()

        config = ServerConfig(
            name="test-server", display_name="Test Server", main_module="test.py"
        )

        registry_test.register(config)
        retrieved = registry_test.get("test-server")

        assert retrieved is not None
        assert retrieved.name == "test-server"
        assert retrieved.display_name == "Test Server"

    def test_duplicate_registration(self) -> None:
        """Test that duplicate registrations are rejected."""
        registry_test = ServerRegistry()

        config1 = ServerConfig(
            name="duplicate", display_name="First", main_module="first.py"
        )
        config2 = ServerConfig(
            name="duplicate", display_name="Second", main_module="second.py"
        )

        registry_test.register(config1)

        with pytest.raises(ValueError, match="already registered"):
            registry_test.register(config2)

    def test_list_servers(self) -> None:
        """Test listing registered servers."""
        registry_test = ServerRegistry()

        # Empty registry
        assert registry_test.list_servers() == []

        # Add servers
        for name in ["zebra", "alpha", "beta"]:
            config = ServerConfig(
                name=name,
                display_name=f"{name.title()} Server",
                main_module=f"{name}.py",
            )
            registry_test.register(config)

        # Should be sorted
        assert registry_test.list_servers() == ["alpha", "beta", "zebra"]

    def test_get_all_configs(self) -> None:
        """Test getting all configurations."""
        registry_test = ServerRegistry()

        config1 = ServerConfig(
            name="server1", display_name="Server 1", main_module="s1.py"
        )
        config2 = ServerConfig(
            name="server2", display_name="Server 2", main_module="s2.py"
        )

        registry_test.register(config1)
        registry_test.register(config2)

        all_configs = registry_test.get_all_configs()
        assert len(all_configs) == 2
        assert "server1" in all_configs
        assert "server2" in all_configs
        assert all_configs["server1"].display_name == "Server 1"

    def test_empty_registry(self) -> None:
        """Test empty registry behavior."""
        registry_test = ServerRegistry()

        assert registry_test.get("non-existent") is None
        assert registry_test.list_servers() == []
        assert registry_test.get_all_configs() == {}

    def test_is_registered(self) -> None:
        """Test checking if a server is registered."""
        registry_test = ServerRegistry()

        # Initially not registered
        assert not registry_test.is_registered("test-server")

        # Register a server
        config = ServerConfig(
            name="test-server", display_name="Test Server", main_module="test.py"
        )
        registry_test.register(config)

        # Now it should be registered
        assert registry_test.is_registered("test-server")

        # Other servers still not registered
        assert not registry_test.is_registered("other-server")


class TestGlobalRegistry:
    """Test the global registry instance."""

    def test_mcp_code_checker_registered(self) -> None:
        """Test that MCP Code Checker is registered in global registry."""
        config = registry.get("mcp-code-checker")
        assert config is not None
        assert config.name == "mcp-code-checker"
        assert len(config.parameters) == 7

    def test_mcp_filesystem_server_registered(self) -> None:
        """Test that MCP Filesystem Server is registered in global registry."""
        config = registry.get("mcp-server-filesystem")
        assert config is not None
        assert config.name == "mcp-server-filesystem"
        assert len(config.parameters) == 5

    def test_registry_completeness(self) -> None:
        """Test that the global registry has expected servers."""
        servers = registry.list_servers()
        assert "mcp-code-checker" in servers
        assert "mcp-server-filesystem" in servers
        assert len(servers) >= 2  # May have external servers

    def test_is_registered_with_global_registry(self) -> None:
        """Test is_registered method with global registry."""
        # Built-in servers should be registered
        assert registry.is_registered("mcp-code-checker")
        assert registry.is_registered("mcp-server-filesystem")

        # Non-existent server should not be registered
        assert not registry.is_registered("non-existent-server")
