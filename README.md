# MCP Config

Configure MCP servers for Claude Desktop and VSCode with one command.

## Quick Start

```bash
# Install
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git

# Setup for Claude Desktop
mcp-config setup mcp-code-checker "My Project" --project-dir .

# Setup for VSCode (team projects)
mcp-config setup mcp-code-checker "My Project" --client vscode-workspace --project-dir .
```

## Built-in Help System

Get comprehensive help directly from the CLI:

```bash
# Tool overview and commands
mcp-config help

# Help for specific commands
mcp-config help setup
mcp-config help remove
mcp-config help list
mcp-config help validate

# Help for server parameters
mcp-config help mcp-code-checker
mcp-config help mcp-server-filesystem

# Quick reference
mcp-config help mcp-code-checker --quick
```

## Supported MCP Servers

- **mcp-code-checker** - Code analysis using pylint, pytest, and mypy
- **mcp-server-filesystem** - File system operations
- External servers via Python entry points

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - For developers enhancing mcp-config
- **[INTEGRATION.md](INTEGRATION.md)** - For MCP server developers

## Features

- Auto-detects Python environments and virtual environments
- Supports Claude Desktop and VSCode (workspace + user profile)
- Backs up configurations before changes
- Validates server setup with comprehensive checks
- Extensive CLI help system

## License

MIT - see [LICENSE](LICENSE) file.
