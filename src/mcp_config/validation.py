"""Simplified validation system for MCP server parameters."""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def validate_path(
    path: Path | str,
    param_name: str,
    must_exist: bool = False,
    must_be_dir: bool = False,
    must_be_file: bool = False,
    check_permissions: str | None = None,
) -> list[str]:
    """Unified path validation function.

    Args:
        path: Path to validate
        param_name: Parameter name for error messages
        must_exist: Whether path must exist
        must_be_dir: Whether path must be a directory
        must_be_file: Whether path must be a file
        check_permissions: Permission mode to check ('r', 'w', 'x')

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []
    path_obj = Path(path) if isinstance(path, str) else path

    # Existence check
    if must_exist and not path_obj.exists():
        errors.append(f"Path for '{param_name}' does not exist: {path}")
        return errors  # No point checking other properties if doesn't exist

    # Type checks (only if path exists)
    if path_obj.exists():
        if must_be_dir and not path_obj.is_dir():
            errors.append(f"Path for '{param_name}' is not a directory: {path}")
        elif must_be_file and not path_obj.is_file():
            errors.append(f"Path for '{param_name}' is not a file: {path}")

        # Permission checks
        if check_permissions:
            try:
                if check_permissions == "r" and not os.access(path_obj, os.R_OK):
                    errors.append(f"No read permission for '{param_name}': {path}")
                elif check_permissions == "w" and not os.access(path_obj, os.W_OK):
                    errors.append(f"No write permission for '{param_name}': {path}")
                elif check_permissions == "x" and not os.access(path_obj, os.X_OK):
                    errors.append(f"No execute permission for '{param_name}': {path}")
            except (OSError, PermissionError) as e:
                errors.append(f"Permission error for '{param_name}': {e}")

    return errors


def validate_python_executable(path: Path | str, param_name: str) -> list[str]:
    """Validate that a path points to a valid Python executable.

    Args:
        path: Path to Python executable
        param_name: Parameter name for error messages

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []
    path_str = str(path)
    path_obj = Path(path_str)

    # Check existence and executable permission
    path_errors = validate_path(
        path_obj, param_name, must_exist=True, must_be_file=True, check_permissions="x"
    )
    if path_errors:
        return path_errors

    # Try to run it and get version
    try:
        result = subprocess.run(
            [path_str, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            errors.append(f"Python executable for '{param_name}' failed to run: {path}")
    except (subprocess.SubprocessError, OSError) as e:
        errors.append(f"Failed to validate Python executable for '{param_name}': {e}")

    return errors


def validate_venv_path(path: Path | str, param_name: str) -> list[str]:
    """Validate that a path points to a valid virtual environment.

    Args:
        path: Path to virtual environment
        param_name: Parameter name for error messages

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []
    venv_path = Path(path) if isinstance(path, str) else path

    # Check basic path requirements
    path_errors = validate_path(
        venv_path, param_name, must_exist=True, must_be_dir=True
    )
    if path_errors:
        return path_errors

    # Check for venv structure
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        errors.append(
            f"Virtual environment for '{param_name}' missing Python executable: {python_exe}"
        )

    return errors


def validate_log_level(value: str, param_name: str) -> list[str]:
    """Validate log level value.

    Args:
        value: Log level value
        param_name: Parameter name for error messages

    Returns:
        List of validation errors (empty if valid)
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if value.upper() not in valid_levels:
        return [
            f"Invalid log level for '{param_name}': '{value}'. "
            f"Must be one of: {', '.join(valid_levels)}"
        ]
    return []


def normalize_path(path: Path | str, base_dir: Path | None = None) -> Path:
    """Normalize a path to absolute form.

    Args:
        path: Path to normalize
        base_dir: Base directory for relative paths (defaults to current directory)

    Returns:
        Normalized absolute path
    """
    path_obj = Path(path) if isinstance(path, str) else path
    if path_obj.is_absolute():
        return path_obj.resolve()
    if base_dir is None:
        base_dir = Path.cwd()
    return (base_dir / path_obj).resolve()


def auto_detect_python_executable(project_dir: Path) -> Path | None:
    """Auto-detect Python executable for a project.

    Args:
        project_dir: Project directory

    Returns:
        Path to Python executable, or None if not found
    """
    from .detection import detect_python_environment

    python_exe, _ = detect_python_environment(project_dir)
    return Path(python_exe) if python_exe else None


def auto_detect_venv_path(project_dir: Path) -> Path | None:
    """Auto-detect virtual environment path for a project.

    Args:
        project_dir: Project directory

    Returns:
        Path to virtual environment, or None if not found
    """
    from .detection import find_virtual_environments

    venvs = find_virtual_environments(project_dir)
    return venvs[0] if venvs else None


def auto_detect_log_file(project_dir: Path, server_type: str) -> Path | None:
    """Auto-detect or generate a log file path for any MCP server.

    Args:
        project_dir: Project directory
        server_type: Type of server (e.g., 'mcp-code-checker', 'mcp-server-filesystem')

    Returns:
        Path to log file, auto-generated if needed
    """
    # Check if logs directory exists and has existing server logs
    logs_dir = project_dir / "logs"
    if logs_dir.exists():
        # Look for existing log files for this server type
        # Convert server type to log file pattern
        if server_type == "mcp-code-checker":
            pattern = "mcp_code_checker_*.log"
        elif server_type == "mcp-server-filesystem":
            pattern = "mcp_filesystem_server_*.log"
        else:
            # Generic pattern for other servers
            safe_name = server_type.replace("-", "_")
            pattern = f"{safe_name}_*.log"
        
        existing_logs = list(logs_dir.glob(pattern))
        if existing_logs:
            # Return the most recent one
            return max(existing_logs, key=lambda p: p.stat().st_mtime)
    
    # Auto-generate a new log file path
    return auto_generate_log_file_path(project_dir, server_type)


def auto_detect_filesystem_log_file(project_dir: Path) -> Path | None:
    """Auto-detect or generate a log file path for MCP Filesystem Server.
    
    Deprecated: Use auto_detect_log_file(project_dir, 'mcp-server-filesystem') instead.

    Args:
        project_dir: Project directory

    Returns:
        Path to log file, auto-generated if needed
    """
    return auto_detect_log_file(project_dir, "mcp-server-filesystem")


def auto_generate_log_file_path(project_dir: Path, server_type: str = "mcp-code-checker") -> Path:
    """Auto-generate a log file path with timestamp.

    Args:
        project_dir: Project directory
        server_type: Type of server for log file naming

    Returns:
        Generated log file path
    """
    logs_dir = project_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Convert server type to safe filename
    if server_type == "mcp-code-checker":
        filename = f"mcp_code_checker_{timestamp}.log"
    elif server_type == "mcp-server-filesystem":
        filename = f"mcp_filesystem_server_{timestamp}.log"
    else:
        # Generic naming for other servers
        safe_name = server_type.replace("-", "_")
        filename = f"{safe_name}_{timestamp}.log"
    
    return logs_dir / filename


def validate_cli_command(command: str, server_type: str = "") -> list[str]:
    """Validate that a CLI command is available.

    Args:
        command: Command name to validate
        server_type: Type of server for better error messages

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not shutil.which(command):
        if server_type == "mcp-code-checker":
            errors.append(
                f"Command '{command}' not found. "
                f"Please install with 'pip install mcp-code-checker' "
                f"or 'pip install -e .' in development mode."
            )
        elif server_type == "mcp-server-filesystem":
            errors.append(
                f"Command '{command}' not found. "
                f"Please install with 'pip install mcp-server-filesystem'."
            )
        else:
            errors.append(
                f"Command '{command}' not found. "
                f"Please check installation instructions for this server."
            )

    return errors


def validate_filesystem_server_directory(project_dir: Path) -> list[str]:
    """Validate directory for MCP Filesystem Server.

    Args:
        project_dir: Project directory to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Basic existence and type check
    path_errors = validate_path(
        project_dir, "project_dir", must_exist=True, must_be_dir=True
    )
    if path_errors:
        return path_errors
    
    # Check permissions
    try:
        # Must be readable
        if not os.access(project_dir, os.R_OK):
            errors.append(f"Directory is not readable: {project_dir}")
            
        # Try to list contents
        try:
            list(project_dir.iterdir())
        except (OSError, PermissionError) as e:
            errors.append(f"Cannot list directory contents: {e}")
            
        # Test write capability for logs (optional)
        if os.access(project_dir, os.W_OK):
            # Try to create a test file
            test_file = project_dir / ".mcp_fs_test"
            try:
                test_file.touch()
                test_file.unlink()
            except (OSError, PermissionError) as e:
                errors.append(f"Write test failed (logs may not work): {e}")
                
    except (OSError, PermissionError) as e:
        errors.append(f"Permission error accessing directory: {e}")
        
    return errors


def validate_code_checker_project(project_dir: Path, test_folder: str = "tests") -> list[str]:
    """Validate project structure for MCP Code Checker.

    Args:
        project_dir: Project directory to validate
        test_folder: Name of test folder to check

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Basic directory validation
    path_errors = validate_path(
        project_dir, "project_dir", must_exist=True, must_be_dir=True
    )
    if path_errors:
        return path_errors
    
    # Check for test folder
    test_path = project_dir / test_folder
    if not test_path.exists():
        errors.append(f"Test folder '{test_folder}' not found in project directory")
    elif not test_path.is_dir():
        errors.append(f"Test folder '{test_folder}' exists but is not a directory")
    
    # Check for common Python project structure
    common_files = ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"]
    common_dirs = ["src", "lib", "app"]
    
    has_setup = any((project_dir / f).exists() for f in common_files)
    has_src = any((project_dir / d).exists() and (project_dir / d).is_dir() for d in common_dirs)
    
    if not (has_setup or has_src):
        errors.append(
            "No common Python project structure detected. "
            "Consider adding setup.py, pyproject.toml, or src/ directory."
        )
        
    return errors


def get_installation_instructions(server_type: str, mode: str) -> str:
    """Get installation instructions based on server type and current mode.

    Args:
        server_type: Type of server
        mode: Current installation mode

    Returns:
        Helpful installation instructions
    """
    if server_type == "mcp-code-checker":
        if mode == "not_available":
            return (
                "To install MCP Code Checker:\n"
                "  1. From PyPI: pip install mcp-code-checker\n"
                "  2. From source: git clone <repo> && cd mcp-code-checker && pip install -e .\n"
                "  3. Development: cd /path/to/mcp-code-checker && pip install -e ."
            )
        elif mode == "python_module":
            return (
                "CLI command not available. To enable it:\n"
                "  1. Reinstall: pip install --force-reinstall mcp-code-checker\n"
                "  2. Or in development: pip install -e .\n"
                "  3. Then verify: which mcp-code-checker (or 'where' on Windows)"
            )
        elif mode == "development":
            return (
                "Running in development mode. To install CLI command:\n"
                "  1. Navigate to project: cd /path/to/mcp-code-checker\n"
                "  2. Install in editable mode: pip install -e .\n"
                "  3. Verify: mcp-code-checker --help"
            )
    elif server_type == "mcp-server-filesystem":
        if mode == "not_available":
            return (
                "To install MCP Filesystem Server:\n"
                "  1. From PyPI: pip install mcp-server-filesystem\n"
                "  2. From source: git clone <repo> && cd mcp-server-filesystem && pip install -e .\n"
                "  3. Verify: mcp-server-filesystem --help"
            )
        elif mode == "python_module":
            return (
                "CLI command not available. To enable it:\n"
                "  1. Reinstall: pip install --force-reinstall mcp-server-filesystem\n"
                "  2. Then verify: which mcp-server-filesystem (or 'where' on Windows)"
            )
        elif mode == "development":
            return (
                "Running in development mode. To install CLI command:\n"
                "  1. Navigate to project: cd /path/to/mcp-server-filesystem\n"
                "  2. Install in editable mode: pip install -e .\n"
                "  3. Verify: mcp-server-filesystem --help"
            )

    return "Please check the documentation for installation instructions."


def validate_server_installation(server_type: str) -> tuple[str, dict[str, Any]]:
    """Validate server installation and return mode and check results.
    
    Args:
        server_type: Type of server to validate
        
    Returns:
        Tuple of (installation_mode, check_result)
    """
    check_result = {"status": "unknown", "message": "", "details": []}
    
    if server_type == "mcp-code-checker":
        # Check if CLI command is available
        if shutil.which("mcp-code-checker"):
            check_result.update({
                "status": "success",
                "message": "CLI command 'mcp-code-checker' is available",
                "details": ["Found CLI executable in system PATH"]
            })
            return "cli_command", check_result
        else:
            # Check if package is installed
            try:
                import importlib.util
                spec = importlib.util.find_spec("mcp_code_checker")
                if spec is not None:
                    check_result.update({
                        "status": "warning",
                        "message": "Package installed but CLI command not found. Run 'pip install -e .' to install command.",
                        "details": ["Python package found", "CLI command missing"]
                    })
                    return "python_module", check_result
                else:
                    raise ImportError("Package not found")
            except ImportError:
                # Development mode - check for source files
                current_dir = Path.cwd()
                package_path = current_dir / "src" / "main.py"
                if package_path.exists():
                    check_result.update({
                        "status": "info",
                        "message": "Running in development mode (source files)",
                        "details": ["Found source files in development structure"]
                    })
                    return "development", check_result
                else:
                    check_result.update({
                        "status": "error",
                        "message": "MCP Code Checker not properly installed",
                        "details": ["No CLI command found", "No Python package found", "No development files found"]
                    })
                    return "not_available", check_result
                    
    elif server_type == "mcp-server-filesystem":
        # Check if CLI command is available
        if shutil.which("mcp-server-filesystem"):
            check_result.update({
                "status": "success",
                "message": "CLI command 'mcp-server-filesystem' is available",
                "details": ["Found CLI executable in system PATH"]
            })
            return "cli_command", check_result
        else:
            # Check if package is installed
            try:
                import importlib.util
                spec = importlib.util.find_spec("mcp_server_filesystem")
                if spec is not None:
                    check_result.update({
                        "status": "warning",
                        "message": "Package installed but CLI command not found. Run 'pip install -e .' to install command.",
                        "details": ["Python package found", "CLI command missing"]
                    })
                    return "python_module", check_result
                else:
                    raise ImportError("Package not found")
            except ImportError:
                # For filesystem server, check for common installation patterns
                check_result.update({
                    "status": "error",
                    "message": "MCP Filesystem Server not properly installed",
                    "details": ["No CLI command found", "No Python package found", "Install with: pip install mcp-server-filesystem"]
                })
                return "not_available", check_result
    
    # Default for unknown server types
    check_result.update({
        "status": "unknown",
        "message": f"Unknown server type: {server_type}",
        "details": ["Cannot validate installation for unknown server type"]
    })
    return "unknown", check_result


def validate_server_configuration(
    server_name: str,
    server_type: str,
    params: dict[str, Any],
    client_handler: Any | None = None,
) -> dict[str, Any]:
    """Comprehensive validation of server configuration.

    Args:
        server_name: Name of the server
        server_type: Type of server (e.g., 'mcp-code-checker', 'mcp-server-filesystem')
        params: Server parameters
        client_handler: Optional client handler for config validation

    Returns:
        Dictionary with validation results
    """
    checks = []
    errors = []
    warnings = []

    # Validate server installation for both server types
    installation_mode, install_check = validate_server_installation(server_type)
    
    if install_check["status"] == "success":
        checks.append(install_check)
    elif install_check["status"] == "warning":
        checks.append(install_check)
        warnings.append(install_check["message"])
    elif install_check["status"] == "error":
        checks.append(install_check)
        errors.append(install_check["message"])
    else:
        checks.append(install_check)

    # Configuration existence check
    if client_handler:
        servers = client_handler.list_all_servers()
        server_names = [s["name"] for s in servers]
        if server_name in server_names:
            checks.append({"status": "success", "message": "Configuration found"})
        else:
            checks.append(
                {
                    "status": "error",
                    "message": f"Server '{server_name}' not found in configuration",
                }
            )
            errors.append(f"Server '{server_name}' not found")

    # Project directory validation
    if "project_dir" in params and params["project_dir"]:
        project_dir = Path(params["project_dir"])
        path_errors = validate_path(
            project_dir, "project_dir", must_exist=True, must_be_dir=True
        )

        if not path_errors:
            checks.append(
                {
                    "status": "success",
                    "message": f"Project directory exists: {project_dir}",
                }
            )
        else:
            checks.append({"status": "error", "message": path_errors[0]})
            errors.extend(path_errors)

    # Python executable validation
    if "python_executable" in params and params["python_executable"]:
        python_exe = Path(params["python_executable"])
        exe_errors = validate_python_executable(python_exe, "python_executable")

        if not exe_errors:
            checks.append(
                {
                    "status": "success",
                    "message": f"Python executable found: {python_exe.name}",
                }
            )
        else:
            checks.append({"status": "error", "message": exe_errors[0]})
            errors.extend(exe_errors)

    # Virtual environment validation (if specified)
    if "venv_path" in params and params["venv_path"]:
        venv_path = Path(params["venv_path"])
        venv_errors = validate_venv_path(venv_path, "venv_path")

        if not venv_errors:
            checks.append(
                {
                    "status": "success",
                    "message": f"Virtual environment found: {venv_path.name}",
                }
            )
        else:
            checks.append(
                {
                    "status": "warning",
                    "message": f"Virtual environment issue: {venv_path.name}",
                }
            )
            warnings.extend(venv_errors)

    # Server-specific validation checks
    if "project_dir" in params and params["project_dir"]:
        project_dir = Path(params["project_dir"])
        
        if server_type == "mcp-code-checker":
            # Test folder check for mcp-code-checker
            test_folder = params.get("test_folder", "tests")
            test_path = project_dir / test_folder

            if test_path.exists() and test_path.is_dir():
                checks.append(
                    {"status": "success", "message": f"Test folder exists: {test_folder}"}
                )
            else:
                checks.append(
                    {"status": "warning", "message": f"Test folder missing: {test_folder}"}
                )
                warnings.append(f"Test folder '{test_folder}' not found")
                
        elif server_type == "mcp-server-filesystem":
            # Filesystem-specific validation checks
            # Check directory permissions
            try:
                if os.access(project_dir, os.R_OK):
                    checks.append(
                        {"status": "success", "message": "Project directory is readable"}
                    )
                else:
                    checks.append(
                        {"status": "error", "message": "Project directory is not readable"}
                    )
                    errors.append(f"No read permission for project directory: {project_dir}")
                    
                if os.access(project_dir, os.W_OK):
                    checks.append(
                        {"status": "success", "message": "Project directory is writable"}
                    )
                else:
                    checks.append(
                        {"status": "warning", "message": "Project directory is not writable"}
                    )
                    warnings.append(f"No write permission for project directory: {project_dir}")
                    
            except (OSError, PermissionError) as e:
                checks.append(
                    {"status": "error", "message": f"Permission error: {e}"}
                )
                errors.append(f"Permission error for project directory: {e}")
                
            # Check for common filesystem patterns
            common_dirs = ["src", "docs", "tests", "scripts", "config"]
            found_dirs = []
            for dir_name in common_dirs:
                dir_path = project_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    found_dirs.append(dir_name)
                    
            if found_dirs:
                checks.append(
                    {"status": "info", "message": f"Found common directories: {', '.join(found_dirs)}"}
                )
            else:
                checks.append(
                    {"status": "info", "message": "No common project directories found (may be a simple directory)"}
                )
                
            # Check log directory creation ability
            logs_dir = project_dir / "logs"
            if not logs_dir.exists():
                try:
                    # Test if we can create the logs directory
                    logs_dir.mkdir(parents=True, exist_ok=True)
                    checks.append(
                        {"status": "success", "message": "Can create logs directory"}
                    )
                    # Clean up test directory if we created it
                    if logs_dir.exists() and not any(logs_dir.iterdir()):
                        logs_dir.rmdir()
                except (OSError, PermissionError) as e:
                    checks.append(
                        {"status": "warning", "message": f"Cannot create logs directory: {e}"}
                    )
                    warnings.append(f"May not be able to create log files: {e}")
            else:
                checks.append(
                    {"status": "success", "message": "Logs directory already exists"}
                )

    result = {
        "success": len(errors) == 0,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }

    # Add installation mode for all server types
    result["installation_mode"] = installation_mode

    return result


def validate_parameter_combination(params: dict[str, Any]) -> list[str]:
    """Validate parameter combinations and dependencies.

    Args:
        params: Dictionary of parameter values

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []

    # Project dir must exist if specified
    if params.get("project_dir"):
        project_dir = Path(params["project_dir"])
        if not project_dir.exists():
            errors.append(f"Project directory does not exist: {project_dir}")
        elif not project_dir.is_dir():
            errors.append(f"Project directory is not a directory: {project_dir}")

    return errors


def validate_client_installation(client: str) -> list[str]:
    """Check if the target client is installed.

    Args:
        client: Client name to check

    Returns:
        List of warnings (empty if client is detected)
    """
    warnings = []

    if client.startswith("vscode"):
        # Check if VSCode is installed
        vscode_commands = ["code", "code-insiders", "codium"]
        vscode_found = False

        for cmd in vscode_commands:
            if shutil.which(cmd):
                vscode_found = True
                break

        if not vscode_found:
            warnings.append(
                "VSCode not detected. Please ensure VSCode 1.102+ is installed "
                "for native MCP support."
            )

        # Check for workspace config location if using workspace mode
        if client in ["vscode", "vscode-workspace"]:
            if not Path(".vscode").exists():
                warnings.append(
                    "No .vscode directory found. It will be created for workspace configuration."
                )

    elif client == "claude-desktop":
        # Check for Claude Desktop (platform-specific checks could be added here)
        pass

    return warnings
