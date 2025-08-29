"""Validation functions for MCP server configurations."""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


def validate_client_installation(client: str) -> List[str]:
    """Validate that the specified client is installed."""
    warnings = []
    
    if client == "claude-desktop":
        # Check if Claude Desktop might be installed
        home = Path.home()
        possible_paths = []
        
        if Path.home().name == "nt":  # Windows
            possible_paths.append(home / "AppData" / "Roaming" / "Claude")
        else:
            possible_paths.extend([
                home / "Library" / "Application Support" / "Claude",  # macOS
                home / ".config" / "claude"  # Linux
            ])
            
        if not any(p.exists() for p in possible_paths):
            warnings.append("Claude Desktop may not be installed")
            
    elif client.startswith("vscode"):
        if not shutil.which("code"):
            warnings.append("VSCode may not be installed or not in PATH")
    
    return warnings


def validate_parameter_combination(user_params: Dict[str, Any]) -> List[str]:
    """Validate parameter combinations."""
    errors = []
    
    # Check for conflicting parameters
    if user_params.get("console_only") and user_params.get("log_file"):
        errors.append("Cannot specify both --console-only and --log-file")
    
    return errors


def validate_server_configuration(
    server_name: str,
    server_type: str, 
    params: Dict[str, Any],
    client_handler: Any
) -> Dict[str, Any]:
    """Run comprehensive validation on a server configuration."""
    result: Dict[str, Any] = {
        "success": True,
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    # Basic configuration check
    checks = result["checks"]
    checks["config_file_exists"] = client_handler.get_config_path().exists()
    
    # Parameter validation
    if "project_dir" in params:
        project_path = Path(params["project_dir"])
        checks["project_dir_exists"] = project_path.exists()
        checks["project_dir_readable"] = project_path.is_dir()
    
    if "python_executable" in params:
        python_path = Path(params["python_executable"])
        checks["python_executable_exists"] = python_path.exists()
    
    if "venv_path" in params:
        venv_path = Path(params["venv_path"])
        checks["venv_path_exists"] = venv_path.exists()
    
    # Check for any failed checks
    failed_checks = [k for k, v in checks.items() if not v]
    if failed_checks:
        result["success"] = False
        errors = result["errors"]
        errors.extend([f"Check failed: {check}" for check in failed_checks])
    
    return result


def auto_detect_python_executable(project_dir: Path) -> Optional[Path]:
    """Auto-detect Python executable."""
    # Check for virtual environment
    venv_paths = [
        project_dir / ".venv",
        project_dir / "venv", 
        project_dir / "env"
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            python_exe = venv_path / "bin" / "python"
            if not python_exe.exists():
                python_exe = venv_path / "Scripts" / "python.exe"  # Windows
            if python_exe.exists():
                return python_exe
    
    # Fallback to system Python
    system_python = shutil.which("python")
    if system_python:
        return Path(system_python)
        
    return None


def auto_detect_venv_path(project_dir: Path) -> Optional[Path]:
    """Auto-detect virtual environment path."""
    venv_paths = [
        project_dir / ".venv",
        project_dir / "venv",
        project_dir / "env"
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists() and venv_path.is_dir():
            return venv_path
    
    return None


def normalize_path(path: str, base_dir: Path) -> Path:
    """Normalize a path relative to base directory."""
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    return (base_dir / path_obj).resolve()
