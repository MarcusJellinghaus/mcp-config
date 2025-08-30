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

## Supported MCP Servers

**MCP Code Checker** (`mcp-code-checker`)
- **Repository**: https://github.com/MarcusJellinghaus/mcp-code-checker
- **Purpose**: Code analysis and testing server using pylint, pytest, and mypy
- **Documentation**: [MCP Code Checker README](https://github.com/MarcusJellinghaus/mcp-code-checker/blob/main/README.md)

### Supported Parameters:
- `--project-dir` (required): Base directory for code checking operations
- `--python-executable`: Path to Python interpreter (auto-detected)
- `--venv-path`: Path to virtual environment (auto-detected)
- `--test-folder`: Path to test folder (defaults to "tests")
- `--keep-temp-files`: Keep temporary files after execution
- `--log-level`: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `--log-file`: Path for structured JSON logs

External servers can be added via Python entry points (see `mcp-config validate`).

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
