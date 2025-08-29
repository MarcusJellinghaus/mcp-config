"""Python environment detection utilities."""

import shutil
from pathlib import Path
from typing import Optional, Tuple


def detect_python_environment(project_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """Detect Python executable and virtual environment for a project.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        Tuple of (python_executable, venv_path) as strings or None
    """
    python_exe = None
    venv_path = None
    
    # Common virtual environment directory names
    venv_names = [".venv", "venv", "env", ".env"]
    
    # Look for virtual environments
    for venv_name in venv_names:
        potential_venv = project_dir / venv_name
        if potential_venv.exists() and potential_venv.is_dir():
            # Check for Python executable in venv
            if Path.cwd().drive:  # Windows
                python_in_venv = potential_venv / "Scripts" / "python.exe"
                if not python_in_venv.exists():
                    python_in_venv = potential_venv / "Scripts" / "python3.exe"
            else:  # Unix-like systems
                python_in_venv = potential_venv / "bin" / "python"
                if not python_in_venv.exists():
                    python_in_venv = potential_venv / "bin" / "python3"
            
            if python_in_venv.exists():
                python_exe = str(python_in_venv)
                venv_path = str(potential_venv)
                break
    
    # If no venv found, try to find system Python
    if python_exe is None:
        system_python = shutil.which("python")
        if system_python is None:
            system_python = shutil.which("python3")
        if system_python:
            python_exe = system_python
    
    return python_exe, venv_path
