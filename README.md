# MCP Config

Configure MCP servers for Claude Desktop and VSCode with one command.

## Install
```bash
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git
```

## Usage
```bash
# Setup for Claude Desktop
mcp-config setup mcp-code-checker "My Project" --project-dir .

# Setup for VSCode
mcp-config setup mcp-code-checker "My Project" --client vscode --project-dir .

# List servers
mcp-config list

# Remove server
mcp-config remove my-server
```

## Features
- Auto-detects Python environments
- Backs up configurations
- Validates server setup
- Supports multiple clients

## Help
```bash
mcp-config --help
mcp-config help setup
```

## Links
[Install](INSTALL.md) • [Usage](USAGE.md) • [Contributing](CONTRIBUTING.md) • [Issues](https://github.com/MarcusJellinghaus/mcp-config/issues)

## License
MIT - see [LICENSE](LICENSE) file.
