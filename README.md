# MCP Config

Configure MCP servers for Claude Desktop, VSCode, and IntelliJ with one command.

## Quick Start

```bash
# Install
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git

# Setup for Claude Desktop
mcp-config setup mcp-code-checker "My Project" --project-dir .

# Setup for VSCode (team projects)
mcp-config setup mcp-code-checker "My Project" --client vscode-workspace --project-dir .

# Setup for IntelliJ/PyCharm (GitHub Copilot)
mcp-config setup mcp-code-checker "My Project" --client intellij --project-dir .
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

## Supported Clients

- **Claude Desktop** - claude_desktop_config.json
- **VSCode** - .vscode/mcp.json  
- **IntelliJ/PyCharm** - GitHub Copilot mcp.json

## Features

- 🔧 **Multi-Client**: Works with Claude Desktop, VSCode, and IntelliJ
- 🚀 **Cross-Platform**: Windows, macOS, and Linux support
- 📝 **Simple**: Standard JSON configuration
- Auto-detects Python environments and virtual environments
- Backs up configurations before changes
- Validates server setup with comprehensive checks
- Extensive CLI help system

## License

MIT - see [LICENSE](LICENSE) file.
