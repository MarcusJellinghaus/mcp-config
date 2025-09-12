# MCP Config User Guide

Complete documentation for configuring MCP servers with mcp-config.

## Installation

**Requirements:** Python 3.11+

```bash
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git
```

**Verify:** `mcp-config --help` (or `python -m mcp_config --help` if command not found)

## Quick Reference

```bash
# Setup (Claude Desktop default)
mcp-config setup <server-type> <n> --project-dir <path>

# Setup for VSCode workspace (shared project configuration)  
mcp-config setup <server-type> <n> --client vscode-workspace --project-dir <path>

# This creates .vscode/mcp.json in your project directory that can be:
# - Committed to Git for team collaboration
# - Shared across all developers working on the project
# - Version controlled alongside your code
# Alternative: Use vscode-user for personal-only configurations

# Setup for VSCode user (personal global)
mcp-config setup <server-type> <n> --client vscode-user --project-dir <path>

# Setup for IntelliJ/PyCharm (GitHub Copilot)
mcp-config setup <server-type> <n> --client intellij --project-dir <path>

# Management
mcp-config list [--client <client>] [--detailed]
mcp-config remove <n> [--client <client>]
mcp-config validate [<n>] [--client <client>]
mcp-config help [<topic>]
```

## Supported Clients

**All clients use identical parameters - only `--client` flag differs.**

### Claude Desktop (`claude-desktop`, default)
- **Config:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows), `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `~/.config/claude/claude_desktop_config.json` (Linux)
- **Use for:** Personal AI assistant
- **Paths:** Always absolute

### VSCode Workspace (`vscode-workspace`)  
- **Config:** `.vscode/mcp.json` in project
- **Use for:** Team projects, version control sharing
- **Paths:** Relative (portable)
- **Shareable:** Yes, commit to Git

### VSCode User (`vscode-user`)
- **Config:** `%APPDATA%\Code\User\mcp.json` (Windows), `~/Library/Application Support/Code/User/mcp.json` (macOS), `~/.config/Code/User/mcp.json` (Linux)
- **Use for:** Personal global settings
- **Paths:** Absolute
- **Shareable:** No

### IntelliJ/PyCharm (`intellij`)
- **Config:** `%LOCALAPPDATA%\github-copilot\intellij\mcp.json` (Windows), `~/Library/Application Support/github-copilot/intellij/mcp.json` (macOS), `~/.config/github-copilot/intellij/mcp.json` (Linux)
- **Use for:** GitHub Copilot integration in IntelliJ IDEA and PyCharm
- **Paths:** Absolute
- **Shareable:** No
- **Requires:** GitHub Copilot plugin installed

## Supported Servers

### MCP Code Checker (`mcp-code-checker`)
Code analysis server using pylint, pytest, and mypy.

**Key Parameters:**
- `--project-dir` (required) - Base directory
- `--python-executable` (auto-detected) - Python interpreter
- `--venv-path` (auto-detected) - Virtual environment
- `--test-folder` (default: "tests") - Test directory
- `--log-level` (default: "INFO") - Logging level
- `--keep-temp-files` - Keep temporary files

### MCP Filesystem Server (`mcp-server-filesystem`)  
File system operations server.

**Key Parameters:**
- `--project-dir` (required) - Directory to serve
- `--python-executable` (auto-detected) - Python interpreter
- `--log-level` (default: "INFO") - Logging level
- `--reference-project` (repeatable) - Additional project directories in format "name=path"

**Example with Reference Projects:**
```bash
mcp-config setup mcp-server-filesystem myfs \
  --project-dir /path/to/main/project \
  --reference-project docs=/path/to/documentation \
  --reference-project examples=/path/to/examples
```

**Parameter Help:** Use `mcp-config help <server-type>` for complete parameter documentation.

## IntelliJ/PyCharm Support

MCP Config Tool supports IntelliJ IDEA and PyCharm through GitHub Copilot:

```bash
# Setup server for IntelliJ
mcp-config setup mcp-code-checker "Description" --client intellij --project-dir .

# List IntelliJ servers  
mcp-config list --client intellij

# Remove IntelliJ server
mcp-config remove "server-name" --client intellij
```

### Configuration Format

All clients use standard JSON configuration:

```json
{
    "servers": {
        "my-server": {
            "command": "python",
            "args": ["-m", "my_server"]
        }
    }
}
```

## Auto-Detection & Safety

**Auto-Detection:** Python executable, virtual environment, project structure
**Safety Features:** Automatic backups, dry-run mode (`--dry-run`), validation
**Wildcard Removal:** `mcp-config remove "pattern*" --client <client>` (requires explicit client)

## CLI Help System

**Primary Interface:** Get comprehensive help without leaving terminal

```bash
mcp-config help                    # Tool overview
mcp-config help <command>          # Command details
mcp-config help <server-type>      # Server parameters
mcp-config help <server> --quick   # Quick reference
```

## Troubleshooting

### Installation Issues
- **Command not found:** Use `python -m mcp_config --help`, check PATH
- **Permission denied:** Fix config directory permissions

### Configuration Issues  
- **Project validation failed:** Check project structure, use `mcp-config validate`
- **Python not found:** Specify with `--python-executable`
- **Server exists:** Remove existing server first or use different name

### Client Integration
- **Claude Desktop:** Restart application after config changes
- **VSCode:** Requires version 1.102+, restart after changes
- **Path handling:** All clients use absolute paths internally for reliability across different working directories


### Server Installation Modes
1. **CLI Command** (best): `mcp-code-checker` command available
2. **Python Module** (fallback): `python -m mcp_code_checker`  
3. **Development** (source): `python src/main.py`

Check mode: `mcp-config validate "server-name"`

### Recovery
- **Restore backup:** Copy from `config.backup_TIMESTAMP.json`
- **Reset:** Remove all servers and reconfigure

**Get Help:** `mcp-config help`, gather info with `mcp-config --version` and `mcp-config list --detailed`
