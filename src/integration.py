"""Integration between ServerConfig and ClientHandler."""

import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any

from .clients import ClientHandler, VSCodeHandler
from .servers import ServerConfig
from .utils import validate_required_parameters


def is_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH."""
    return shutil.which(command) is not None


def is_package_installed(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError):
        return False


def get_mcp_code_checker_command_mode() -> str:
    """Determine the best command mode for MCP Code Checker."""
    if is_command_available("mcp-code-checker"):
        return "cli_command"
    
    if is_package_installed("mcp_code_checker"):
        return "python_module"
    
    if Path("src/main.py").exists():
        return "development"
    
    return "not_available"


def build_server_config(
    server_config: ServerConfig,
    user_params: dict[str, Any],
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Build server configuration for preview/dry-run."""
    project_dir = Path(user_params.get("project_dir", ".")).resolve()

    normalized_params = {}
    for key, value in user_params.items():
        if key in ["project_dir", "test_folder", "log_file", "venv_path"] and value:
            normalized_params[key] = str(
                Path(value).resolve()
                if Path(value).is_absolute()
                else project_dir / value
            )
        else:
            normalized_params[key] = value

    config: dict[str, Any]
    if server_config.name == "mcp-code-checker":
        mode = get_mcp_code_checker_command_mode()
        
        if mode == "cli_command":
            args = server_config.generate_args(normalized_params, use_cli_command=True)
            config = {
                "command": "mcp-code-checker",
                "args": args,
            }
        elif mode == "python_module":
            args = server_config.generate_args(normalized_params, use_cli_command=True)
            config = {
                "command": python_executable or sys.executable,
                "args": ["-m", "mcp_code_checker"] + args,
            }
        else:
            args = server_config.generate_args(normalized_params)
            config = {
                "command": python_executable or sys.executable,
                "args": args,
            }
    else:
        args = server_config.generate_args(normalized_params)
        config = {
            "command": python_executable or sys.executable,
            "args": args,
        }

    if "project_dir" in normalized_params:
        pythonpath = str(normalized_params["project_dir"])
        if sys.platform == "win32" and not pythonpath.endswith("\\"):
            pythonpath += "\\"
        config["env"] = {"PYTHONPATH": pythonpath}

    return config


def generate_client_config(
    server_config: ServerConfig,
    server_name: str,
    user_params: dict[str, Any],
    python_executable: str | None = None,
    client_handler: ClientHandler | None = None,
) -> dict[str, Any]:
    """Generate client configuration from server config and user parameters."""
    errors = validate_required_parameters(server_config, user_params)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")

    project_dir = Path(user_params.get("project_dir", ".")).resolve()
    normalized_params = {}
    
    for param in server_config.parameters:
        param_key = param.name.replace("-", "_")
        if param_key in user_params:
            value = user_params[param_key]
            if param.param_type == "path" and value is not None:
                normalized_params[param_key] = str(Path(value).resolve())
            else:
                normalized_params[param_key] = value

    if python_executable is None:
        python_executable = sys.executable

    client_config: dict[str, Any]
    if server_config.name == "mcp-code-checker":
        mode = get_mcp_code_checker_command_mode()
        
        if mode == "cli_command":
            args = server_config.generate_args(normalized_params, use_cli_command=True)
            client_config = {
                "command": "mcp-code-checker",
                "args": args,
            }
        elif mode == "python_module":
            args = server_config.generate_args(normalized_params, use_cli_command=True)
            client_config = {
                "command": python_executable or sys.executable,
                "args": ["-m", "mcp_code_checker"] + args,
            }
        else:
            args = server_config.generate_args(normalized_params)
            client_config = {
                "command": python_executable or sys.executable,
                "args": args,
            }
    else:
        args = server_config.generate_args(normalized_params)
        client_config = {
            "command": python_executable or sys.executable,
            "args": args,
        }

    client_config["_server_type"] = server_config.name

    env = {}
    if "project_dir" in normalized_params:
        pythonpath = normalized_params["project_dir"]
        if sys.platform == "win32" and not pythonpath.endswith("\\"):
            pythonpath += "\\"
        env["PYTHONPATH"] = pythonpath

    if "venv_path" in normalized_params and normalized_params["venv_path"]:
        venv_path = Path(normalized_params["venv_path"])
        if venv_path.exists():
            if sys.platform == "win32":
                venv_python = venv_path / "Scripts" / "python.exe"
            else:
                venv_python = venv_path / "bin" / "python"

            if venv_python.exists():
                if client_config["command"] != "mcp-code-checker":
                    client_config["command"] = str(venv_python)

    if env:
        client_config["env"] = env

    return client_config


def setup_mcp_server(
    client_handler: ClientHandler,
    server_config: ServerConfig,
    server_name: str,
    user_params: dict[str, Any],
    python_executable: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """High-level function to set up an MCP server in a client."""
    result = {
        "success": False,
        "server_name": server_name,
        "operation": "setup",
        "dry_run": dry_run,
    }

    try:
        client_config = generate_client_config(
            server_config, server_name, user_params, python_executable, client_handler
        )

        result["config"] = client_config
        result["config_path"] = str(client_handler.get_config_path())

        if dry_run:
            result["success"] = True
            result["message"] = f"Would set up server '{server_name}'"
            return result

        success = client_handler.setup_server(server_name, client_config)

        if success:
            result["success"] = True
            result["message"] = f"Successfully set up server '{server_name}'"

            try:
                config_path = client_handler.get_config_path()
                backup_files = list(
                    config_path.parent.glob("claude_desktop_config_backup_*.json")
                )
                if backup_files:
                    latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                    result["backup_path"] = str(latest_backup)
            except Exception:
                pass

        else:
            result["message"] = f"Failed to set up server '{server_name}'"

    except Exception as e:
        result["error"] = str(e)
        result["message"] = f"Error setting up server: {e}"

    return result


def remove_mcp_server(
    client_handler: ClientHandler,
    server_name: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Remove an MCP server from client configuration."""
    result = {
        "success": False,
        "server_name": server_name,
        "operation": "remove",
        "dry_run": dry_run,
    }

    try:
        all_servers = client_handler.list_all_servers()
        server_info = None
        for server in all_servers:
            if server["name"] == server_name:
                server_info = server
                break

        if not server_info:
            result["message"] = f"Server '{server_name}' not found"
            return result

        if not server_info.get("managed", False):
            result["message"] = (
                f"Server '{server_name}' is not managed by this tool. "
                "Cannot remove external servers."
            )
            return result

        result["config_path"] = str(client_handler.get_config_path())

        if dry_run:
            result["success"] = True
            result["message"] = f"Would remove server '{server_name}'"
            return result

        success = client_handler.remove_server(server_name)

        if success:
            result["success"] = True
            result["message"] = f"Successfully removed server '{server_name}'"

            try:
                config_path = client_handler.get_config_path()
                backup_files = list(
                    config_path.parent.glob("claude_desktop_config_backup_*.json")
                )
                if backup_files:
                    latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                    result["backup_path"] = str(latest_backup)
            except Exception:
                pass

        else:
            result["message"] = f"Failed to remove server '{server_name}'"

    except Exception as e:
        result["error"] = str(e)
        result["message"] = f"Error removing server: {e}"

    return result
