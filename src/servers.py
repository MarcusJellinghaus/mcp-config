"""Core data model for MCP server configurations."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class ParameterDef:
    """Definition of a server parameter for CLI and config generation."""

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
        valid_types = {"string", "boolean", "choice", "path"}
        if self.param_type not in valid_types:
            raise ValueError(
                f"Invalid param_type '{self.param_type}'. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )


@dataclass
class ServerConfig:
    """Complete configuration for an MCP server type."""

    name: str
    display_name: str
    main_module: str
    parameters: list[ParameterDef] = field(default_factory=list)

    def generate_args(self, user_params: dict[str, Any], use_cli_command: bool = False) -> list[str]:
        """Generate command line args from user parameters."""
        from .validation import (
            auto_detect_python_executable,
            auto_detect_venv_path,
            normalize_path,
        )

        if use_cli_command:
            args = []
        else:
            if self.name == "mcp-code-checker" and "project_dir" in user_params:
                proj_dir = Path(user_params["project_dir"]).resolve()
                main_module_path = proj_dir / self.main_module
                args = [str(main_module_path.resolve())]
            else:
                args = [self.main_module]

        processed_params = dict(user_params)
        project_dir: Path | None = None
        if "project_dir" in processed_params:
            project_dir = Path(processed_params["project_dir"])

        for param in self.parameters:
            param_key = param.name.replace("-", "_")

            if (
                param_key in processed_params
                and processed_params[param_key] is not None
            ):
                continue

            if param.auto_detect and project_dir:
                if param.name == "python-executable":
                    if not use_cli_command:
                        detected = auto_detect_python_executable(project_dir)
                        if detected:
                            processed_params[param_key] = str(detected)
                elif param.name == "venv-path":
                    detected = auto_detect_venv_path(project_dir)
                    if detected:
                        processed_params[param_key] = str(detected)

        for param in self.parameters:
            param_key = param.name.replace("-", "_")
            value = processed_params.get(param_key, param.default)

            if value is None:
                continue

            if use_cli_command and param.name == "python-executable":
                continue

            if param.is_flag:
                if value:
                    args.append(param.arg_name)
            else:
                if param.param_type == "path" and project_dir:
                    value = str(normalize_path(value, project_dir))

                args.append(param.arg_name)
                args.append(str(value))

        return args

    def get_required_params(self) -> list[str]:
        """Get list of required parameter names."""
        return [param.name for param in self.parameters if param.required]

    def supports_cli_command(self) -> bool:
        """Check if this server supports CLI command mode."""
        if self.name == "mcp-code-checker":
            import shutil
            return shutil.which("mcp-code-checker") is not None
        return False

    def get_cli_command_name(self) -> str | None:
        """Get the CLI command name for this server."""
        if self.name == "mcp-code-checker":
            return "mcp-code-checker"
        return None

    def get_parameter_by_name(self, name: str) -> ParameterDef | None:
        """Get parameter definition by name."""
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
        """Register a server configuration."""
        if config.name in self._servers:
            raise ValueError(f"Server '{config.name}' is already registered")
        self._servers[config.name] = config

    def get(self, name: str) -> ServerConfig | None:
        """Get server configuration by name."""
        return self._servers.get(name)

    def list_servers(self) -> list[str]:
        """Get list of registered server names."""
        return sorted(self._servers.keys())

    def get_all_configs(self) -> dict[str, ServerConfig]:
        """Get all registered configurations."""
        return self._servers.copy()

    def is_registered(self, name: str) -> bool:
        """Check if a server is registered."""
        return name in self._servers


# Global registry instance
registry = ServerRegistry()

# MCP Code Checker built-in config
MCP_CODE_CHECKER = ServerConfig(
    name="mcp-code-checker",
    display_name="MCP Code Checker",
    main_module="src/main.py",
    parameters=[
        ParameterDef(
            name="project-dir",
            arg_name="--project-dir",
            param_type="path",
            required=True,
            help="Base directory for code checking operations (required)",
        ),
        ParameterDef(
            name="python-executable",
            arg_name="--python-executable",
            param_type="path",
            auto_detect=True,
            help="Path to Python interpreter to use for running tests",
        ),
        ParameterDef(
            name="venv-path",
            arg_name="--venv-path",
            param_type="path",
            auto_detect=True,
            help="Path to virtual environment to activate for running tests",
        ),
        ParameterDef(
            name="test-folder",
            arg_name="--test-folder",
            param_type="string",
            default="tests",
            help="Path to the test folder (relative to project_dir)",
        ),
        ParameterDef(
            name="keep-temp-files",
            arg_name="--keep-temp-files",
            param_type="boolean",
            is_flag=True,
            help="Keep temporary files after test execution",
        ),
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
            auto_detect=False,
            help="Path for structured JSON logs",
        ),
        ParameterDef(
            name="console-only",
            arg_name="--console-only",
            param_type="boolean",
            is_flag=True,
            help="Log only to console, ignore --log-file parameter",
        ),
    ],
)

# Register the built-in server
registry.register(MCP_CODE_CHECKER)
