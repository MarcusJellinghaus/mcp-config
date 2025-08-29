"""Validation utilities for MCP server configurations."""

import importlib.util
from pathlib import Path
from typing import Any

from .servers import ParameterDef, ServerConfig


def validate_parameter_value(param_def: ParameterDef, value: Any) -> list[str]:
    """Validate a parameter value against its definition."""
    errors: list[str] = []

    if value is None:
        return errors

    if param_def.param_type == "choice":
        if param_def.choices and value not in param_def.choices:
            errors.append(
                f"Parameter '{param_def.name}' value '{value}' is not in valid choices: "
                f"{', '.join(param_def.choices)}"
            )

    elif param_def.param_type == "boolean":
        if not isinstance(value, bool):
            errors.append(
                f"Parameter '{param_def.name}' must be a boolean value, got {type(value).__name__}"
            )

    elif param_def.param_type == "path":
        if not isinstance(value, (str, Path)):
            errors.append(
                f"Parameter '{param_def.name}' must be a path string or Path object, "
                f"got {type(value).__name__}"
            )

    elif param_def.param_type == "string":
        if value is not None and not isinstance(value, str):
            try:
                str(value)
            except (TypeError, ValueError) as e:
                errors.append(
                    f"Parameter '{param_def.name}' cannot be converted to string: {e}"
                )

    return errors


def validate_required_parameters(
    server_config: ServerConfig, user_params: dict[str, Any]
) -> list[str]:
    """Validate that all required parameters are provided."""
    errors: list[str] = []

    for param in server_config.parameters:
        if param.required:
            param_key = param.name.replace("-", "_")
            if param_key not in user_params or user_params[param_key] is None:
                errors.append(f"{param.name} is required")

    return errors


def normalize_path_parameter(value: str, base_path: Path) -> str:
    """Normalize a path parameter to absolute path."""
    path = Path(value)

    if path.is_absolute():
        return str(path)

    absolute_path = (base_path / path).resolve()
    return str(absolute_path)


def detect_mcp_installation(project_dir: Path) -> dict[str, Any]:
    """Detect MCP Code Checker installation details."""
    info: dict[str, Any] = {
        "installed_as_package": False,
        "source_path": None,
        "module_name": None,
        "version": None,
    }

    try:
        spec = importlib.util.find_spec("mcp_code_checker")
        if spec is not None:
            info["installed_as_package"] = True
            info["module_name"] = "mcp_code_checker"

            try:
                import mcp_code_checker  # type: ignore[import-not-found]
                if hasattr(mcp_code_checker, "__version__"):
                    info["version"] = mcp_code_checker.__version__
            except ImportError:
                pass
    except (ImportError, ModuleNotFoundError):
        pass

    main_py = project_dir / "src" / "main.py"
    if main_py.exists():
        info["source_path"] = str(main_py)

        try:
            with open(main_py, "r", encoding="utf-8") as f:
                content = f.read(1000)
                if "mcp" in content.lower() and "code" in content.lower():
                    info["likely_mcp_code_checker"] = True
        except Exception:
            pass

    return info


def recommend_command_format(
    client: str, server_type: str, installation_info: dict[str, Any]
) -> str:
    """Recommend the best command format for the given client and server."""
    if client.startswith("vscode"):
        if installation_info.get("installed_as_package"):
            return "Module invocation (python -m mcp_code_checker)"
        else:
            return "Direct script execution (python src/main.py)"
    elif client == "claude-desktop":
        return "Direct script execution with full paths"

    return "Default command format"
