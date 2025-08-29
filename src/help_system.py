"""Help system for mcp-config CLI tool."""

from typing import Optional

from .servers import registry


def print_command_help(command: Optional[str] = None, verbose: bool = False) -> int:
    """Print help for a specific command or general overview."""
    if command is None or command == "all":
        print("MCP Configuration Helper")
        print("========================")
        print()
        print("Configure MCP servers for various clients like Claude Desktop and VSCode.")
        print()
        print("Available commands:")
        print("  setup     - Set up MCP server configuration")
        print("  remove    - Remove MCP server configuration") 
        print("  list      - List configured servers")
        print("  validate  - Validate server configuration")
        print("  help      - Show detailed help")
        print()
        print("Available server types:")
        for server_name in registry.list_servers():
            server_config = registry.get(server_name)
            if server_config:
                print(f"  {server_name} - {server_config.display_name}")
        print()
        print("Use 'mcp-config help <command>' for detailed command help.")
        print("Use 'mcp-config help <server-type>' for server-specific help.")
        return 0
    
    elif command == "setup":
        print("mcp-config setup - Set up MCP server configuration")
        print("=" * 50)
        print()
        print("Usage:")
        print("  mcp-config setup <server-type> <server-name> [options]")
        print()
        print("Examples:")
        print("  mcp-config setup mcp-code-checker my-checker --project-dir .")
        print("  mcp-config setup mcp-code-checker my-checker --client vscode --project-dir /path/to/project")
        print("  mcp-config setup mcp-code-checker my-checker --dry-run --project-dir .")
        print()
        return 0
    
    elif command == "remove":
        print("mcp-config remove - Remove MCP server configuration")
        print("=" * 50)
        print()
        print("Usage:")
        print("  mcp-config remove <server-name> [options]")
        print()
        print("Examples:")
        print("  mcp-config remove my-checker")
        print("  mcp-config remove my-checker --client vscode")
        print("  mcp-config remove my-checker --dry-run")
        print()
        return 0
    
    elif command == "list":
        print("mcp-config list - List configured servers")
        print("=" * 40)
        print()
        print("Usage:")
        print("  mcp-config list [options]")
        print()
        print("Examples:")
        print("  mcp-config list")
        print("  mcp-config list --client claude-desktop")
        print("  mcp-config list --managed-only")
        print("  mcp-config list --detailed")
        print()
        return 0
    
    else:
        print(f"Unknown command: {command}")
        return 1


def print_parameter_help(server_type: str, parameter: Optional[str] = None, verbose: bool = False) -> int:
    """Print help for server parameters."""
    server_config = registry.get(server_type)
    if not server_config:
        print(f"Unknown server type: {server_type}")
        return 1
    
    print(f"{server_config.display_name} Parameters")
    print("=" * 50)
    print()
    
    if parameter:
        # Show help for specific parameter
        param_def = server_config.get_parameter_by_name(parameter)
        if param_def:
            print(f"Parameter: {param_def.name}")
            print(f"Type: {param_def.param_type}")
            print(f"Required: {'Yes' if param_def.required else 'No'}")
            if param_def.default:
                print(f"Default: {param_def.default}")
            if param_def.choices:
                print(f"Choices: {', '.join(param_def.choices)}")
            print(f"Help: {param_def.help}")
        else:
            print(f"Unknown parameter: {parameter}")
            return 1
    else:
        # Show all parameters
        required_params = [p for p in server_config.parameters if p.required]
        optional_params = [p for p in server_config.parameters if not p.required]
        
        if required_params:
            print("Required parameters:")
            for param in required_params:
                print(f"  --{param.name}")
                print(f"    {param.help}")
                print()
        
        if optional_params:
            print("Optional parameters:")
            for param in optional_params:
                print(f"  --{param.name}")
                if param.default:
                    print(f"    Default: {param.default}")
                print(f"    {param.help}")
                print()
    
    return 0


def print_quick_reference(server_type: Optional[str] = None) -> int:
    """Print quick reference for server setup."""
    if server_type:
        server_config = registry.get(server_type)
        if not server_config:
            print(f"Unknown server type: {server_type}")
            return 1
        
        print(f"Quick Setup: {server_config.display_name}")
        print("=" * 40)
        print()
        
        required_params = [p for p in server_config.parameters if p.required]
        if required_params:
            args = " ".join([f"--{p.name} <value>" for p in required_params])
            print(f"mcp-config setup {server_type} my-server {args}")
        else:
            print(f"mcp-config setup {server_type} my-server")
        print()
        return 0
    else:
        print("Quick Reference - All Server Types")
        print("=" * 40)
        print()
        for server_name in registry.list_servers():
            server_config = registry.get(server_name)
            if server_config:
                required_params = [p for p in server_config.parameters if p.required]
                if required_params:
                    args = " ".join([f"--{p.name} <value>" for p in required_params])
                    print(f"mcp-config setup {server_name} my-server {args}")
                else:
                    print(f"mcp-config setup {server_name} my-server")
        print()
        return 0
