# Installation Guide for MCP Config

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- git (for development installation)

## Installation Methods

### Method 1: Install from PyPI (When Available)

```bash
# Install the latest release
pip install mcp-config

# Verify installation
mcp-config --version
mcp-config --help
```

### Method 2: Install from GitHub (Recommended)

```bash
# Install directly from the main branch
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git

# Or install a specific version/tag
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git@v1.0.0

# Verify installation
mcp-config --help
```

### Method 3: Development Installation

For contributors or when you need to modify the code:

```bash
# Clone the repository
git clone https://github.com/MarcusJellinghaus/mcp-config.git
cd mcp-config

# Create a virtual environment (recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Verify installation
mcp-config --help

# Run tests to ensure everything works
pytest
```

## Post-Installation Verification

### 1. Verify CLI Command

```bash
# Check if command is available
which mcp-config  # Unix/macOS
where mcp-config  # Windows

# Test the command
mcp-config --version
mcp-config --help
```

### 2. Verify Python Module

```bash
# Test as Python module
python -m mcp_config --help

# Verify import works
python -c "import mcp_config; print('✓ Package imported successfully')"
```

### 3. Verify Configuration Tool

```bash
# Check config tool is available
mcp-config --help

# Validate installation
mcp-config validate
```

## Installation in Virtual Environments

### Creating a Project-Specific Installation

```bash
# Navigate to your project
cd /path/to/your/project

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate      # Windows

# Install MCP Config
pip install mcp-config

# Configure your MCP server for your project
mcp-config setup my-server "My Project Server" --project-dir .
```

### Using with Poetry

```bash
# Add to your project
poetry add mcp-config

# Or add as development dependency
poetry add --dev mcp-config

# Verify in poetry shell
poetry shell
mcp-config --help
```

### Using with Pipenv

```bash
# Add to Pipfile
pipenv install mcp-config

# Or as dev dependency
pipenv install --dev mcp-config

# Verify in pipenv shell
pipenv shell
mcp-config --help
```

## Platform-Specific Instructions

### Windows

1. **Command Prompt (cmd.exe)**
   ```batch
   pip install mcp-config
   mcp-config --help
   ```

2. **PowerShell**
   ```powershell
   pip install mcp-config
   mcp-config --help
   
   # If you get execution policy errors:
   python -m mcp_config --help
   ```

3. **Adding to PATH**
   If the command isn't found after installation:
   ```batch
   REM Find Python Scripts directory
   python -c "import site; print(site.USER_BASE)"
   
   REM Add Scripts folder to PATH
   REM Replace USERNAME with your actual username
   setx PATH "%PATH%;C:\Users\USERNAME\AppData\Roaming\Python\Python311\Scripts"
   
   REM Restart terminal and try again
   ```

### macOS

1. **With Homebrew Python**
   ```bash
   # Ensure you're using Homebrew Python
   which python3
   # Should show: /opt/homebrew/bin/python3 or /usr/local/bin/python3
   
   python3 -m pip install mcp-config
   ```

2. **With System Python**
   ```bash
   # Use --user flag to avoid permission issues
   pip install --user mcp-config
   
   # Add user bin to PATH if needed
   export PATH="$HOME/.local/bin:$PATH"
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   ```

### Linux

1. **Ubuntu/Debian**
   ```bash
   # Install pip if needed
   sudo apt update
   sudo apt install python3-pip
   
   # Install MCP Config
   pip install --user mcp-config
   
   # Add to PATH if needed
   export PATH="$HOME/.local/bin:$PATH"
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   ```

2. **Fedora/RHEL**
   ```bash
   # Install pip if needed
   sudo dnf install python3-pip
   
   # Install MCP Config
   pip install --user mcp-config
   ```

## Troubleshooting Installation

### Command Not Found

If `mcp-config` command is not found after installation:

1. **Check installation location:**
   ```bash
   pip show mcp-config
   ```

2. **Check if scripts were installed:**
   ```bash
   ls $(python -m site --user-base)/bin/  # Unix/macOS
   dir $(python -m site --user-base)\Scripts\  # Windows
   ```

3. **Use Python module as fallback:**
   ```bash
   python -m mcp_config --help
   ```

### Permission Errors

If you get permission errors during installation:

```bash
# Option 1: Use --user flag
pip install --user mcp-config

# Option 2: Use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install mcp-config

# Option 3: Use pipx for isolated installation
pipx install mcp-config
```

### Import Errors

If you get import errors when running the command:

```bash
# Reinstall with all dependencies
pip install --force-reinstall mcp-config

# Check for conflicting packages
pip list | grep mcp

# In development mode, ensure you're in the right directory
cd /path/to/mcp-config
pip install -e .
```

## Uninstallation

To remove MCP Config:

```bash
# Uninstall the package
pip uninstall mcp-config

# Remove configuration backups (optional)
# Note: This will not remove actual MCP configurations, only backups
rm -rf ~/.mcp-config-backups  # Unix/macOS
rmdir /s ~/.mcp-config-backups  # Windows

# Clean up cache (optional)
pip cache purge
```

## Next Steps

After installation:

1. **Configure your first MCP server:**
   ```bash
   mcp-config setup my-server "My First Server" --project-dir /path/to/project
   ```

2. **Configure for specific clients:**
   ```bash
   # For Claude Desktop
   mcp-config setup my-server "My Server" --client claude --project-dir .
   
   # For VSCode workspace
   mcp-config setup my-server "My Server" --client vscode --project-dir .
   
   # For VSCode user profile (global)
   mcp-config setup my-server "My Server" --client vscode-user --project-dir .
   ```

3. **Validate your configuration:**
   ```bash
   mcp-config validate
   ```

4. **List configured servers:**
   ```bash
   mcp-config list
   ```

5. **Read the documentation:**
   - [User Guide](docs/config/USER_GUIDE.md)
   - [Troubleshooting](docs/config/TROUBLESHOOTING.md)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](docs/config/TROUBLESHOOTING.md)
2. Run validation: `mcp-config validate`
3. Check GitHub Issues: https://github.com/MarcusJellinghaus/mcp-config/issues
4. Ask for help with detailed error messages and system information

## Configuration Examples

### Quick Setup Examples

```bash
# Basic setup for Claude Desktop
mcp-config setup code-server "Code Analysis Server" \
  --project-dir ~/projects/my-app

# Setup with specific Python environment
mcp-config setup ml-server "ML Server" \
  --project-dir ~/ml-project \
  --python-executable ~/.pyenv/versions/3.11.5/bin/python \
  --venv-path ~/ml-project/.venv

# VSCode workspace setup with dry-run
mcp-config setup workspace-server "Development Server" \
  --client vscode \
  --project-dir . \
  --dry-run

# Global VSCode setup
mcp-config setup global-server "Global Utilities" \
  --client vscode-user \
  --project-dir ~/tools/mcp-servers
```

### Verification Commands

```bash
# Check what servers are configured
mcp-config list

# Validate all configurations
mcp-config validate

# Create a backup before making changes
mcp-config backup

# Test a specific configuration (dry-run)
mcp-config setup test-server "Test" --project-dir . --dry-run
```
