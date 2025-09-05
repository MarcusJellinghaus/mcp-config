# MCP Server Integration Guide

Guide for MCP server developers integrating with mcp-config.

## Overview

Make your MCP server easily configurable via:
1. **Entry Points Integration** - Python package registration
2. **Documentation** - User setup guide

## Entry Points Integration

**setup.py:**
```python
setup(
    name="my-mcp-server",
    entry_points={
        "mcp.server_configs": [
            "my-server = my_mcp_server.config:get_server_config"
        ]
    }
)
```

**pyproject.toml:**
```toml
[project.entry-points."mcp.server_configs"]
my-server = "my_mcp_server.config:get_server_config"
```

**Configuration Function** (`my_mcp_server/config.py`):

```python
from mcp_config.servers import ServerConfig, ParameterDef

def get_server_config() -> ServerConfig:
    return ServerConfig(
        name="my-server",
        display_name="My Server",
        main_module="src/main.py",
        parameters=[
            ParameterDef(
                name="data-dir",
                arg_name="--data-dir",
                param_type="path", 
                required=True,
                help="Directory containing data files",
            ),
            ParameterDef(
                name="log-level",
                arg_name="--log-level",
                param_type="choice",
                default="INFO",
                choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                help="Logging level",
            ),
            ParameterDef(
                name="enable-auth",
                arg_name="--enable-auth", 
                param_type="boolean",
                is_flag=True,
                help="Enable authentication",
            ),
        ],
    )
```

## Parameter Types

- **`path`** - File/directory paths, auto-normalized by client
- **`string`** - Text values, numbers as strings  
- **`choice`** - Predefined options (must specify `choices` list)
- **`boolean` + `is_flag=True`** - On/off switches

**Auto-Detection:** Set `auto_detect=True` for common parameters:
- `python-executable` - Finds Python in venv or system
- `venv-path` - Finds `.venv`, `venv`, `env` directories

## Testing Integration

```bash
pip install -e .                      # Install your package
mcp-config validate                    # Should show your server
mcp-config help my-server              # Parameter help
mcp-config setup my-server "test" --data-dir /path --dry-run
```

## CLI Command Support

If your server provides a CLI command:

```python
def get_server_config() -> ServerConfig:
    config = ServerConfig(name="my-server", ...)
    
    def supports_cli_command(self) -> bool:
        import shutil
        return shutil.which("my-server") is not None
    
    config.supports_cli_command = supports_cli_command.__get__(config, ServerConfig)
    return config
```

This enables better UX: `{"command": "my-server"}` vs `{"command": "python", "args": ["-m", "my_server"]}`

## User Documentation Template

Create setup documentation for your users:

````markdown
# Configuring [Your Server] with mcp-config

## Installation
```bash
pip install my-mcp-server
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git
```

## Setup
```bash
# Claude Desktop
mcp-config setup my-server "name" --data-dir /path/to/data

# VSCode (team projects)  
mcp-config setup my-server "name" --client vscode-workspace --data-dir /path/to/data

# VSCode (personal)
mcp-config setup my-server "name" --client vscode-user --data-dir /path/to/data
```

## Parameters
Get complete help: `mcp-config help my-server`

### Required
- `--data-dir` - Directory containing data files

### Optional  
- `--port` - Port number (default: 8080)
- `--log-level` - Logging level (default: INFO)
- `--enable-auth` - Enable authentication

## Management
```bash
mcp-config list                    # List servers
mcp-config validate "name"         # Check configuration  
mcp-config remove "name"           # Remove server
```
````

**README Integration:** Add mcp-config section to your server's README linking to full setup guide.

## Best Practices

**Parameter Design:**
- Use descriptive names (`--data-dir` not `--dir`)
- Provide sensible defaults 
- Include helpful descriptions

**Error Handling:**
- Add custom validation functions for complex parameters
- Provide specific error messages

**Documentation:**
- Link to mcp-config in your README
- Provide working examples
- Keep parameter help current

The goal is making your server as easy to configure as possible while providing powerful customization options.
