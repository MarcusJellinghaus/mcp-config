"""CLI utilities for parsing arguments and validating setup."""

import argparse
from pathlib import Path
from typing import Any, Optional

from .servers import registry


def create_full_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="mcp-config",
        description="Configure MCP servers for various clients like Claude Desktop and VSCode",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up MCP server configuration")
    setup_parser.add_argument("server_type", help="Type of MCP server")
    setup_parser.add_argument("server_name", help="Name for the server instance")
    setup_parser.add_argument(
        "--client", "-c",
        choices=["claude-desktop", "vscode", "vscode-workspace", "vscode-user"],
        default="claude-desktop",
        help="Target client (default: claude-desktop)"
    )
    setup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    setup_parser.add_argument(
        "--use-workspace",
        action="store_true",
        default=True,
        help="Use workspace config for VSCode (default)"
    )
    
    # Add server-specific parameters
    for server_name, server_config in registry.get_all_configs().items():
        for param in server_config.parameters:
            arg_name = f"--{param.name}"
            if param.is_flag:
                setup_parser.add_argument(
                    arg_name,
                    action="store_true",
                    help=param.help
                )
            elif param.param_type == "choice":
                setup_parser.add_argument(
                    arg_name,
                    choices=param.choices,
                    default=param.default,
                    help=param.help
                )
            else:
                setup_parser.add_argument(
                    arg_name,
                    default=param.default,
                    help=param.help
                )
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove MCP server configuration")
    remove_parser.add_argument("server_name", help="Name of server to remove")
    remove_parser.add_argument(
        "--client", "-c",
        choices=["claude-desktop", "vscode", "vscode-workspace", "vscode-user"],
        default="claude-desktop",
        help="Target client (default: claude-desktop)"
    )
    remove_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    remove_parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before removing (default: true)"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List configured servers")
    list_parser.add_argument(
        "--client", "-c",
        choices=["claude-desktop", "vscode", "vscode-workspace", "vscode-user"],
        help="Show servers for specific client"
    )
    list_parser.add_argument(
        "--managed-only",
        action="store_true",
        help="Show only servers managed by mcp-config"
    )
    list_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed server information"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate server configuration")
    validate_parser.add_argument("server_name", nargs="?", help="Name of server to validate")
    validate_parser.add_argument(
        "--client", "-c",
        choices=["claude-desktop", "vscode", "vscode-workspace", "vscode-user"],
        default="claude-desktop",
        help="Target client (default: claude-desktop)"
    )
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show detailed help")
    help_parser.add_argument("topic", nargs="?", help="Help topic (command or server type)")
    help_parser.add_argument("--all", action="store_true", help="Show all available help")
    help_parser.add_argument("--quick", action="store_true", help="Show quick reference")
    help_parser.add_argument("--command", action="store_true", help="Topic is a command")
    help_parser.add_argument("--server", action="store_true", help="Topic is a server type")
    help_parser.add_argument("--parameter", help="Show help for specific parameter")
    
    return parser


def validate_setup_args(args: argparse.Namespace) -> list[str]:
    """Validate arguments for the setup command."""
    errors = []
    
    # Check if project-dir is provided for servers that need it
    server_config = registry.get(args.server_type)
    if server_config:
        for param in server_config.parameters:
            if param.required and param.name == "project-dir":
                project_dir = getattr(args, "project_dir", None)
                if not project_dir:
                    errors.append("project-dir is required")
                elif not Path(project_dir).exists():
                    errors.append(f"project-dir does not exist: {project_dir}")
    
    return errors
