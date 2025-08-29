# MCP Config

A CLI tool to configure MCP servers for various clients like Claude Desktop and VSCode.

## Overview

This CLI tool enables easy configuration and management of Model Context Protocol (MCP) servers across different AI clients. With mcp-config, you can:

- Configure MCP servers for Claude Desktop
- Set up MCP servers for VSCode 
- Validate server configurations
- Auto-detect Python environments and dependencies
- Manage server lifecycles (setup, list, remove, validate)

## Features

- **Multi-client support**: Configure for Claude Desktop, VSCode workspace, and VSCode user profiles
- **Auto-detection**: Automatically detect Python executables and virtual environments
- **Validation**: Comprehensive validation of server configurations and requirements  
- **Dry-run mode**: Preview changes before applying them
- **Backup management**: Automatic backup creation before configuration changes

## Documentation

- [**User Guide**](docs/config/USER_GUIDE.md) - Complete command reference and setup instructions
- [**Troubleshooting**](docs/config/TROUBLESHOOTING.md) - Common issues and solutions

## Main Configuration Commands

The mcp-config tool provides the following main commands:

| Command | Description |
|---------|-------------|
| `setup` | Set up an MCP server for a specific client |
| `list` | List all configured MCP servers |
| `remove` | Remove an MCP server configuration |
| `validate` | Validate existing server configurations |
| `backup` | Create backup of configuration files |
| `restore` | Restore configuration from backup |

### Setup Parameters

The setup command supports various parameters for customization:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--client` | string | "claude" | Target client (claude, vscode, vscode-user) |
| `--project-dir` | string | current dir | Project directory path |
| `--python-executable` | string | auto-detect | Python interpreter path |
| `--venv-path` | string | auto-detect | Virtual environment path |
| `--dry-run` | boolean | False | Preview changes without applying |
| `--backup` | boolean | True | Create backup before changes |

### Client Types

- **claude**: Configure for Claude Desktop application
- **vscode**: Configure for VSCode workspace (`.vscode/mcp.json`)
- **vscode-user**: Configure for VSCode user profile (global settings)

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

**Quick install:**

```bash
# Install from GitHub (recommended)
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git

# Verify installation
mcp-config --help
```

**Development install:**

```bash
# Clone and install for development
git clone https://github.com/MarcusJellinghaus/mcp-config.git
cd mcp-config
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
mcp-config --help
```

## Using as a Dependency

### In requirements.txt

Add this line to your `requirements.txt`:

```txt
mcp-config @ git+https://github.com/MarcusJellinghaus/mcp-config.git
```

### In pyproject.toml

Add to your project dependencies:

```toml
[project]
dependencies = [
    "mcp-config @ git+https://github.com/MarcusJellinghaus/mcp-config.git",
    # ... other dependencies
]

# Or as an optional dependency
[project.optional-dependencies]
dev = [
    "mcp-config @ git+https://github.com/MarcusJellinghaus/mcp-config.git",
]
```

### Installation Commands

After adding to requirements.txt or pyproject.toml:

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install from pyproject.toml
pip install .
# Or with optional dependencies
pip install ".[dev]"
```

## Basic Usage

### Configure MCP Server for Claude Desktop

```bash
# Set up a new MCP server
mcp-config setup server-name "My Server" --project-dir /path/to/project

# Set up with specific Python environment
mcp-config setup server-name "My Server" \
  --project-dir /path/to/project \
  --python-executable /path/to/python \
  --venv-path /path/to/venv
```

### Configure for VSCode

```bash
# Configure for current workspace
mcp-config setup server-name "My Server" \
  --client vscode \
  --project-dir .

# Configure globally for VSCode
mcp-config setup server-name "My Server" \
  --client vscode-user \
  --project-dir /path/to/project
```

### List and Manage Configurations

```bash
# List all configured servers
mcp-config list

# Validate configurations
mcp-config validate

# Remove a server
mcp-config remove server-name

# Create backup
mcp-config backup

# Restore from backup
mcp-config restore backup-file.json
```

### Using Python Module (Alternative)
You can also run the configuration tool as a Python module:

```bash
python -m mcp_config setup server-name "My Server" --project-dir /path/to/project

# Or for development (from source directory)
python -m src.mcp_config.main setup server-name "My Server" --project-dir /path/to/project
```

### Available Options

- `--client`: Target client (claude, vscode, vscode-user)
- `--project-dir`: **Required**. Path to the project directory
- `--python-executable`: Optional. Path to Python interpreter
- `--venv-path`: Optional. Path to virtual environment to activate
- `--dry-run`: Optional. Preview changes without applying them
- `--backup`: Optional. Create backup before making changes (default: true)
- `--log-level`: Optional. Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Optional. Path for structured JSON logs
- `--console-only`: Optional. Log only to console

Example with options:
```bash
mcp-config setup my-server "My Development Server" \
  --client claude \
  --project-dir /path/to/project \
  --venv-path /path/to/project/.venv \
  --dry-run \
  --log-level DEBUG
```

## Project Structure Support

The configuration tool automatically detects and works with standard project structures:

**Supported Project Types:**
- Standard Python packages with `src/` directory
- Simple Python projects with code in root
- Complex multi-module projects
- Virtual environment projects

**Configuration Detection:**
- Automatically finds `pyproject.toml`, `setup.py`, or `requirements.txt`
- Detects virtual environments (`.venv`, `venv`, `env`)
- Identifies Python executable paths
- Validates MCP server requirements

## Configuration File Locations

### Claude Desktop
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### VSCode
- **Workspace**: `.vscode/mcp.json` (in project root)
- **User Profile**: Platform-specific VSCode settings directory

## Structured Logging

The configuration tool provides comprehensive logging capabilities:

- **Standard human-readable logs** to console for development/debugging
- **Structured JSON logs** to file for analysis and monitoring
- **Operation tracking** with parameters, timing, and results
- **Automatic error context capture** with full stack traces
- **Configurable log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Default timestamped log files** in current directory

Example structured log entries:
```json
{
  "timestamp": "2025-08-05 14:30:15",
  "level": "info",
  "event": "Setting up MCP server",
  "server_name": "my-server",
  "client": "claude",
  "project_dir": "/path/to/project"
}
```

Use `--console-only` to disable file logging for simple operations.

## Configuration Examples

### Claude Desktop Configuration

After running the setup command, your `claude_desktop_config.json` will include:

```json
{
    "mcpServers": {
        "my-server": {
            "command": "python",
            "args": [
                "-m", "my_mcp_server.main",
                "--project-dir", "/path/to/project"
            ],
            "env": {
                "PYTHONPATH": "/path/to/project"
            }
        }
    }
}
```

### VSCode Workspace Configuration

The tool creates or updates `.vscode/mcp.json`:

```json
{
  "servers": {
    "my-server": {
      "command": "python",
      "args": ["-m", "my_mcp_server.main", "--project-dir", "."],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Security Features

- All operations are performed within specified project directories
- Configuration validation before applying changes
- Automatic backup creation before modifications
- Path validation and sanitization
- Safe handling of environment variables and executable paths

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/MarcusJellinghaus/mcp-config.git
cd mcp-config

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest tests/test_config/  # Run only config tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows reuse with minimal restrictions. It permits use, copying, modification, and distribution with proper attribution.

## Links

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Filesystem Tools](https://github.com/MarcusJellinghaus/mcp_server_filesystem)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
