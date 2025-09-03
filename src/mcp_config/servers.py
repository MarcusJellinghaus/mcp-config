"""Core data model for MCP server configurations.

This module provides the data structures needed to represent, validate,
and generate command-line arguments for MCP servers.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class ParameterDef:
    """Definition of a server parameter for CLI and config generation.

    Attributes:
        name: CLI parameter name (e.g., "project-dir")
        arg_name: Server argument (e.g., "--project-dir")
        param_type: Type of parameter ("string", "boolean", "choice", "path")
        required: Whether the parameter is required
        default: Default value for the parameter
        choices: List of valid choices for "choice" type parameters
        help: Help text for CLI
        is_flag: True for boolean flags (action="store_true")
        auto_detect: True if value can be auto-detected
        validator: Optional validation function
    """

    name: str
    arg_name: str
    param_type: str
    required: bool = False
    default: Any = None
    choices: list[str] | None = None
    help: str = ""
    is_flag: bool = False
    auto_detect: bool = False
    validator: Callable[[Any, str], list[str]] | None = None

    def __post_init__(self) -> None:
        """Validate parameter definition after creation."""
        # Validate parameter type
        valid_types = {"string", "boolean", "choice", "path"}
        if self.param_type not in valid_types:
            raise ValueError(
                f"Invalid param_type '{self.param_type}'. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )

        # Validate name and arg_name
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Parameter 'name' must be a non-empty string")
        if not self.arg_name or not isinstance(self.arg_name, str):
            raise ValueError("Parameter 'arg_name' must be a non-empty string")

        # Validate choice parameters
        if self.param_type == "choice":
            if self.choices is None or not isinstance(self.choices, list):
                raise ValueError(
                    f"Parameter '{self.name}' of type 'choice' must have a non-empty choices list"
                )
            elif len(self.choices) == 0:
                raise ValueError(
                    f"Parameter '{self.name}' of type 'choice' must have at least one choice"
                )

        # Validate boolean flags
        if self.param_type == "boolean":
            if (
                self.is_flag
                and self.default is not None
                and not isinstance(self.default, bool)
            ):
                raise ValueError(
                    f"Boolean flag parameter '{self.name}' must have a boolean default value"
                )


@dataclass
class ServerConfig:
    """Complete configuration for an MCP server type.

    Attributes:
        name: Internal name of the server (e.g., "mcp-code-checker")
        display_name: Human-readable display name
        main_module: Path to the main module to execute
        parameters: List of all possible parameters for this server
    """

    name: str
    display_name: str
    main_module: str
    parameters: list[ParameterDef] = field(default_factory=list)

    def generate_args(
        self, user_params: dict[str, Any], use_cli_command: bool = False
    ) -> list[str]:
        """Generate command line args from user parameters.

        Args:
            user_params: Dictionary of parameter names to values
            use_cli_command: If True, generate args for CLI command (skip main module)

        Returns:
            List of command-line arguments
        """
        from .validation import (
            auto_detect_python_executable,
            auto_detect_venv_path,
            normalize_path,
        )

        # For CLI command mode, don't include the main module
        if use_cli_command:
            args = []
        else:
            # Get the absolute path to the main module
            # For both MCP servers, resolve main_module relative to project_dir if it exists
            if "project_dir" in user_params and self.main_module.startswith("src/"):
                proj_dir = Path(user_params["project_dir"]).resolve()
                main_module_path = proj_dir / self.main_module
                args = [str(main_module_path.resolve())]
            else:
                args = [self.main_module]

        # Process parameters with auto-detection
        processed_params = dict(user_params)

        # Auto-detect missing optional parameters
        project_dir: Path | None = None
        if "project_dir" in processed_params:
            project_dir = Path(processed_params["project_dir"])

        for param in self.parameters:
            param_key = param.name.replace("-", "_")

            # Skip if already has a value
            if (
                param_key in processed_params
                and processed_params[param_key] is not None
            ):
                continue

            # Auto-detect if possible
            if param.auto_detect and project_dir:
                if param.name == "python-executable":
                    # Don't auto-detect python-executable in CLI command mode
                    if not use_cli_command:
                        detected = auto_detect_python_executable(project_dir)
                        if detected:
                            processed_params[param_key] = str(detected)
                elif param.name == "venv-path":
                    detected = auto_detect_venv_path(project_dir)
                    if detected:
                        processed_params[param_key] = str(detected)
                elif param.name == "log-file":
                    # Don't auto-detect log file - let servers handle this internally
                    # Only include if explicitly provided by user
                    pass

        # Generate arguments
        for param in self.parameters:
            param_key = param.name.replace("-", "_")

            # Get value from processed params or use default
            value = processed_params.get(param_key, param.default)

            # Skip if no value provided
            if value is None:
                continue

            # Always include python-executable parameter for reliable execution
            # (Previously skipped in CLI command mode, but now we always want it)

            # Handle boolean flags
            if param.is_flag:
                if value:  # Only add flag if True
                    args.append(param.arg_name)
            else:
                # Normalize paths
                if param.param_type == "path" and project_dir:
                    value = str(normalize_path(value, project_dir))

                # Add parameter and value
                args.append(param.arg_name)
                args.append(str(value))

        return args

    def get_required_params(self) -> list[str]:
        """Get list of required parameter names.

        Returns:
            List of names of required parameters
        """
        return [param.name for param in self.parameters if param.required]

    def supports_cli_command(self) -> bool:
        """Check if this server supports CLI command mode.

        Returns:
            True if the server has a CLI command available
        """
        if self.name == "mcp-code-checker":
            import shutil

            return shutil.which("mcp-code-checker") is not None
        elif self.name == "mcp-server-filesystem":
            import shutil

            return shutil.which("mcp-server-filesystem") is not None
        # Add other servers with CLI commands here in the future
        return False

    def get_cli_command_name(self) -> str | None:
        """Get the CLI command name for this server.

        Returns:
            CLI command name if available, None otherwise
        """
        if self.name == "mcp-code-checker":
            return "mcp-code-checker"
        elif self.name == "mcp-server-filesystem":
            return "mcp-server-filesystem"
        # Add other servers here
        return None

    def get_installation_mode(self) -> str:
        """Get the current installation mode for this server.

        Returns:
            One of: 'cli_command', 'python_module', 'development', 'not_available'
        """
        import importlib.util
        import shutil

        if self.name == "mcp-code-checker":
            # Check for CLI command
            if shutil.which("mcp-code-checker"):
                return "cli_command"

            # Check if package is installed
            try:
                spec = importlib.util.find_spec("mcp_code_checker")
                if spec is not None:
                    return "python_module"
            except (ImportError, ModuleNotFoundError):
                pass

            # Check for development mode
            if Path("src/main.py").exists():
                return "development"

            return "not_available"
        elif self.name == "mcp-server-filesystem":
            # Check for CLI command
            if shutil.which("mcp-server-filesystem"):
                return "cli_command"

            # Check if package is installed
            try:
                spec = importlib.util.find_spec("mcp_server_filesystem")
                if spec is not None:
                    return "python_module"
            except (ImportError, ModuleNotFoundError):
                pass

            # Check for development mode (if we're in a filesystem server project)
            # Look for common filesystem server development patterns
            dev_indicators = [
                "setup.py",
                "pyproject.toml",
                "src/mcp_server_filesystem",
                "mcp_server_filesystem/__init__.py",
            ]
            if any(Path(indicator).exists() for indicator in dev_indicators):
                # Additional check: look for filesystem server specific files
                if (
                    Path("src").exists()
                    and any(Path("src").glob("*filesystem*"))
                    or Path("mcp_server_filesystem").exists()
                ):
                    return "development"

            return "not_available"

        # Default for other servers
        return "not_available"

    def validate_project(self, project_dir: Path) -> bool:
        """Check if project is compatible (server-specific logic).

        For MCP Code Checker, validates based on installation mode.
        For MCP Filesystem Server, validates directory structure and permissions.

        Args:
            project_dir: Path to the project directory

        Returns:
            True if the project is valid for this server
        """
        if self.name == "mcp-code-checker":
            # If using CLI command, just verify directory exists
            if self.supports_cli_command():
                return project_dir.exists() and project_dir.is_dir()

            # Check if package is installed (module mode)
            try:
                import importlib.util

                spec = importlib.util.find_spec("mcp_code_checker")
                if spec is not None:
                    # Package is installed, just need valid directory
                    return project_dir.exists() and project_dir.is_dir()
            except (ImportError, ModuleNotFoundError):
                pass

            # Development mode - check for expected structure
            main_path = project_dir / self.main_module
            src_path = project_dir / "src"

            # Both the main module and src directory should exist
            return main_path.exists() and src_path.exists()
        elif self.name == "mcp-server-filesystem":
            # Enhanced validation for filesystem server
            if not (project_dir.exists() and project_dir.is_dir()):
                return False

            # If using CLI command, just verify directory exists and is accessible
            if self.supports_cli_command():
                try:
                    # Test basic read access
                    list(project_dir.iterdir())
                    return True
                except (OSError, PermissionError):
                    return False

            # Check if package is installed (module mode)
            try:
                import importlib.util

                spec = importlib.util.find_spec("mcp_server_filesystem")
                if spec is not None:
                    # Package is installed, just need valid directory
                    try:
                        list(project_dir.iterdir())
                        return True
                    except (OSError, PermissionError):
                        return False
            except (ImportError, ModuleNotFoundError):
                pass

            # Development mode - check for expected structure
            main_path = project_dir / self.main_module
            src_path = project_dir / "src"

            # Check if main module exists or if we have a filesystem server development structure
            if main_path.exists():
                return True
            elif src_path.exists() and any(src_path.glob("*filesystem*")):
                return True

            # Basic directory validation for unknown modes
            try:
                list(project_dir.iterdir())
                return True
            except (OSError, PermissionError):
                return False

        # Default validation for other servers
        return True

    def get_parameter_by_name(self, name: str) -> ParameterDef | None:
        """Get parameter definition by name.

        Args:
            name: Name of the parameter to find

        Returns:
            ParameterDef if found, None otherwise
        """
        for param in self.parameters:
            if param.name == name:
                return param
        return None


class ServerRegistry:
    """Registry for server configurations."""

    def __init__(self) -> None:
        """Initialize the server registry."""
        self._servers: dict[str, ServerConfig] = {}

    def register(self, config: ServerConfig) -> None:
        """Register a server configuration.

        Args:
            config: ServerConfig to register

        Raises:
            ValueError: If a server with the same name is already registered
        """
        if config.name in self._servers:
            raise ValueError(f"Server '{config.name}' is already registered")
        self._servers[config.name] = config

    def get(self, name: str) -> ServerConfig | None:
        """Get server configuration by name.

        Args:
            name: Name of the server to retrieve

        Returns:
            ServerConfig if found, None otherwise
        """
        return self._servers.get(name)

    def list_servers(self) -> list[str]:
        """Get list of registered server names.

        Returns:
            Sorted list of server names
        """
        return sorted(self._servers.keys())

    def get_all_configs(self) -> dict[str, ServerConfig]:
        """Get all registered configurations.

        Returns:
            Copy of the internal server configurations dictionary
        """
        return self._servers.copy()

    def is_registered(self, name: str) -> bool:
        """Check if a server is registered.

        Args:
            name: Name of the server to check

        Returns:
            True if the server is registered, False otherwise
        """
        return name in self._servers


# Global registry instance
registry = ServerRegistry()

# MCP Code Checker built-in config - COMPLETE PARAMETER SET
MCP_CODE_CHECKER = ServerConfig(
    name="mcp-code-checker",
    display_name="MCP Code Checker",
    main_module="src/main.py",
    parameters=[
        # Required parameters
        ParameterDef(
            name="project-dir",
            arg_name="--project-dir",
            param_type="path",
            required=True,
            help="Base directory for code checking operations (required)",
        ),
        # Python execution parameters
        ParameterDef(
            name="python-executable",
            arg_name="--python-executable",
            param_type="path",
            auto_detect=True,
            help="Path to Python interpreter to use for running tests. "
            "If not specified, auto-detects from project or uses current interpreter",
        ),
        ParameterDef(
            name="venv-path",
            arg_name="--venv-path",
            param_type="path",
            auto_detect=True,
            help="Path to virtual environment to activate for running tests. "
            "Auto-detects common venv patterns (.venv, venv, env) if not specified",
        ),
        # Test configuration parameters
        ParameterDef(
            name="test-folder",
            arg_name="--test-folder",
            param_type="string",
            default="tests",
            help="Path to the test folder (relative to project_dir). Defaults to 'tests'",
        ),
        ParameterDef(
            name="keep-temp-files",
            arg_name="--keep-temp-files",
            param_type="boolean",
            is_flag=True,
            help="Keep temporary files after test execution. "
            "Useful for debugging when tests fail",
        ),
        # Logging parameters
        ParameterDef(
            name="log-level",
            arg_name="--log-level",
            param_type="choice",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set logging level (default: INFO)",
        ),
        ParameterDef(
            name="log-file",
            arg_name="--log-file",
            param_type="path",
            auto_detect=True,
            help="Path for structured JSON logs. "
            "Auto-generates timestamped log file in project_dir/logs/ if not specified",
        ),
    ],
)

# MCP Filesystem Server built-in config
MCP_FILESYSTEM_SERVER = ServerConfig(
    name="mcp-server-filesystem",
    display_name="MCP Filesystem Server",
    main_module="src/mcp_server_filesystem/main.py",
    parameters=[
        # Required parameters
        ParameterDef(
            name="project-dir",
            arg_name="--project-dir",
            param_type="path",
            required=True,
            help="Directory to serve files from (required)",
        ),
        # Python execution parameters (for consistency with tests)
        ParameterDef(
            name="python-executable",
            arg_name="--python-executable",
            param_type="path",
            auto_detect=True,
            help="Path to Python interpreter to use. "
            "If not specified, auto-detects from project or uses current interpreter",
        ),
        ParameterDef(
            name="venv-path",
            arg_name="--venv-path",
            param_type="path",
            auto_detect=True,
            help="Path to virtual environment to activate. "
            "Auto-detects common venv patterns (.venv, venv, env) if not specified",
        ),
        # Logging parameters
        ParameterDef(
            name="log-level",
            arg_name="--log-level",
            param_type="choice",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set logging level (default: INFO)",
        ),
        ParameterDef(
            name="log-file",
            arg_name="--log-file",
            param_type="path",
            auto_detect=True,
            help="Path for structured JSON logs. "
            "Auto-generates timestamped log file in project_dir/logs/ if not specified",
        ),
    ],
)

# Register the built-in servers
registry.register(MCP_CODE_CHECKER)
registry.register(MCP_FILESYSTEM_SERVER)
