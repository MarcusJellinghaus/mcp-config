# Usage

## Supported Servers
- **mcp-code-checker** - Code analysis and testing server
- External servers via Python entry points (see `mcp-config validate`)

## Commands
- `setup` - Configure MCP server
- `list` - Show configured servers  
- `remove` - Remove server
- `validate` - Check configuration and show available servers

## Basic Setup
```bash
# Claude Desktop (default)
mcp-config setup mcp-code-checker "My Project" --project-dir .

# VSCode workspace (.vscode/mcp.json)
mcp-config setup mcp-code-checker "My Project" --client vscode --project-dir .

# VSCode user profile (global)
mcp-config setup mcp-code-checker "My Project" --client vscode-user --project-dir .
```

## Management
```bash
# List all servers
mcp-config list

# Remove a server
mcp-config remove my-server

# Show available servers and validate setup
mcp-config validate
```

## Common Options
- `--dry-run` - Preview changes without applying
- `--project-dir PATH` - Project directory (required)
- `--python-executable PATH` - Custom Python path
- `--backup` / `--no-backup` - Control backups (default: on)

## Get Help
```bash
mcp-config --help
mcp-config help setup
mcp-config help <command>
```
