"""CLI utilities for dynamic argument parser generation.

This module provides functions to dynamically generate command-line
argument parsers based on server configurations.
"""

import argparse
from pathlib import Path
from typing import Any

from .servers import ServerConfig, registry

# Supported MCP clients
SUPPORTED_CLIENTS = ["claude-desktop", "vscode-workspace", "vscode-user"]


def build_setup_parser(server_type: str | None = None) -> argparse.ArgumentParser:
    """Build setup command parser with server-specific parameters.

    Args:
        server_type: Optional server type to build parser for.
                    If None, builds a generic parser.

    Returns:
        ArgumentParser configured with server-specific options
    """
    parser = argparse.ArgumentParser(
        prog="mcp-config setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Setup an MCP server in Claude Desktop configuration",
    )

    # Positional arguments
    parser.add_argument(
        "server_type",
        help='Server type (currently only "mcp-code-checker" supported)',
        choices=(
            registry.list_servers() if registry.list_servers() else ["mcp-code-checker"]
        ),
    )
    parser.add_argument(
        "server_name",
        help="Name for this server instance",
    )

    # Global options
    add_global_options(parser)

    # Add server-specific options if server type is known
    if server_type:
        add_server_parameters(parser, server_type)
    else:
        # If no specific server, add parameters for all known servers
        # This allows argparse to handle --help properly
        for known_server in registry.list_servers():
            add_server_parameters(parser, known_server)

    return parser


def add_global_options(parser: argparse.ArgumentParser) -> None:
    """Add global CLI options that apply to all commands.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        "--client",
        default="claude-desktop",
        choices=SUPPORTED_CLIENTS,
        help="MCP client to configure. Options: claude-desktop, vscode-workspace (workspace config), vscode-user (user profile config)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before making changes (default: true)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="backup",
        help="Skip backup creation",
    )


def add_deduplicated_server_parameters(parser: argparse.ArgumentParser) -> None:
    """Add server parameters to parser, deduplicating by parameter name.

    When multiple servers have parameters with the same name (like --project-dir),
    we only add it once to avoid argparse conflicts.

    Args:
        parser: ArgumentParser to add parameters to
    """
    added_params = set()  # Track parameter names we've already added

    # Collect all parameters from all servers
    all_params = []
    for server_type in registry.list_servers():
        server_config = registry.get(server_type)
        if server_config:
            for param in server_config.parameters:
                if param.name not in added_params:
                    all_params.append((server_config, param))
                    added_params.add(param.name)

    # Group parameters by server for nice organization
    if all_params:
        # Create a general group for shared parameters
        group = parser.add_argument_group(
            "Server Options", "Parameters for configuring MCP servers"
        )

        for server_config, param in all_params:
            add_parameter_to_parser(group, param)


def add_server_parameters(parser: argparse.ArgumentParser, server_type: str) -> None:
    """Add server-specific parameters to argument parser.

    Args:
        parser: ArgumentParser to add parameters to
        server_type: Type of server to add parameters for
    """
    server_config = registry.get(server_type)
    if not server_config:
        return

    # Create argument group for server-specific options
    group = parser.add_argument_group(
        f"{server_config.display_name} Options",
        f"Parameters specific to {server_config.display_name}",
    )

    for param in server_config.parameters:
        add_parameter_to_parser(group, param)


def add_parameter_to_parser(
    parser: argparse.ArgumentParser | argparse._ArgumentGroup,
    param: Any,
) -> None:
    """Add a single parameter to an argument parser.

    Args:
        parser: ArgumentParser or ArgumentGroup to add parameter to
        param: ParameterDef object defining the parameter
    """
    option_name = f"--{param.name}"

    # Build kwargs for add_argument
    kwargs: dict[str, Any] = {
        "help": param.help,
        "dest": param.name.replace("-", "_"),  # Convert to valid Python identifier
    }

    # Handle required parameters
    if param.required:
        kwargs["required"] = True

    # Handle default values
    if param.default is not None and not param.is_flag:
        kwargs["default"] = param.default
        # Add default value to help text if not already there
        if "default:" not in param.help.lower():
            kwargs["help"] += f" (default: {param.default})"

    # Handle different parameter types
    if param.param_type == "boolean" and param.is_flag:
        kwargs["action"] = "store_true"
        if param.default is False:
            kwargs["default"] = False
    elif param.param_type == "choice":
        kwargs["choices"] = param.choices
        kwargs["metavar"] = "{" + ",".join(param.choices) + "}"
    elif param.param_type == "path":
        kwargs["type"] = Path
        kwargs["metavar"] = "PATH"
    elif param.param_type == "string":
        kwargs["type"] = str
        kwargs["metavar"] = "STRING"

    # Add auto-detection hint to help text
    if param.auto_detect and "auto-detect" not in param.help.lower():
        kwargs["help"] = (
            kwargs["help"].rstrip(".") + " (auto-detected if not specified)."
        )

    parser.add_argument(option_name, **kwargs)


def create_full_parser() -> argparse.ArgumentParser:
    """Create the complete argument parser with all commands and options.

    Returns:
        Complete ArgumentParser with all subcommands
    """
    parser = argparse.ArgumentParser(
        prog="mcp-config",
        description="MCP Configuration Helper - Automate MCP server setup for Claude Desktop and other clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=get_usage_examples(),
    )

    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Add setup command
    add_setup_subcommand(subparsers)

    # Add remove command
    add_remove_subcommand(subparsers)

    # Add list command
    add_list_subcommand(subparsers)

    # Add validate command
    add_validate_subcommand(subparsers)

    # Add help command
    add_help_subcommand(subparsers)

    return parser


def add_setup_subcommand(subparsers: Any) -> None:
    """Add the setup subcommand to the parser.

    Args:
        subparsers: Subparsers object to add command to
    """
    setup_parser = subparsers.add_parser(
        "setup",
        help="Setup an MCP server configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Setup an MCP server in Claude Desktop configuration",
        epilog=get_setup_examples(),
    )

    # Positional arguments
    setup_parser.add_argument(
        "server_type",
        help="Server type to configure",
        choices=(
            registry.list_servers() if registry.list_servers() else ["mcp-code-checker"]
        ),
    )
    setup_parser.add_argument(
        "server_name",
        help="Name for this server instance",
    )

    # Global options
    add_global_options(setup_parser)

    # Add parameters for all registered servers, but deduplicate by parameter name
    # This allows proper help display while avoiding conflicts
    add_deduplicated_server_parameters(setup_parser)


def add_remove_subcommand(subparsers: Any) -> None:
    """Add the remove subcommand to the parser.

    Args:
        subparsers: Subparsers object to add command to
    """
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an MCP server configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Remove an MCP server from Claude Desktop configuration",
        epilog=get_remove_examples(),
    )

    remove_parser.add_argument(
        "server_name",
        help="Name of the server to remove (supports wildcards: *, ?)",
    )

    remove_parser.add_argument(
        "--client",
        default="claude-desktop",
        choices=SUPPORTED_CLIENTS,
        help="MCP client to configure (required when using wildcards)",
    )
    remove_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    remove_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    remove_parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before making changes (default: true)",
    )
    remove_parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="backup",
        help="Skip backup creation",
    )
    remove_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt when removing multiple servers",
    )


def add_list_subcommand(subparsers: Any) -> None:
    """Add the list subcommand to the parser.

    Args:
        subparsers: Subparsers object to add command to
    """
    list_parser = subparsers.add_parser(
        "list",
        help="List MCP server configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="List all MCP servers in Claude Desktop configuration",
        epilog=get_list_examples(),
    )

    list_parser.add_argument(
        "--client",
        default=None,
        choices=SUPPORTED_CLIENTS,
        help="MCP client to query (default: all clients)",
    )
    list_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed server information",
    )
    list_parser.add_argument(
        "--managed-only",
        action="store_true",
        help="Show only mcp-config managed servers",
    )


def add_validate_subcommand(subparsers: Any) -> None:
    """Add the validate subcommand to the parser.

    Args:
        subparsers: Subparsers object to add command to
    """
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate MCP server configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Validate that an MCP server is properly configured and ready to use",
        epilog=get_validate_examples(),
    )

    validate_parser.add_argument(
        "server_name",
        nargs="?",
        help="Server name to validate (optional)",
    )

    validate_parser.add_argument(
        "--client",
        default="claude-desktop",
        choices=SUPPORTED_CLIENTS,
        help="MCP client to validate (claude-desktop, vscode-workspace, vscode-user)",
    )
    validate_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation information",
    )


def add_help_subcommand(subparsers: Any) -> None:
    """Add the help subcommand to the parser.

    Args:
        subparsers: Subparsers object to add command to
    """
    help_parser = subparsers.add_parser(
        "help",
        help="Show detailed parameter documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Show detailed documentation for server parameters",
        epilog=get_help_examples(),
    )

    help_parser.add_argument(
        "topic",
        nargs="?",
        help="Topic to show help for (command or server type)",
    )

    help_parser.add_argument(
        "--command",
        "-c",
        action="store_true",
        help="Treat topic as a command name",
    )

    help_parser.add_argument(
        "--server",
        "-s",
        action="store_true",
        help="Treat topic as a server type",
    )

    help_parser.add_argument(
        "--parameter",
        "-p",
        help="Show detailed help for a specific parameter",
        metavar="PARAM_NAME",
    )

    help_parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Show quick reference card instead of detailed help",
    )

    help_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show extended help with examples and details",
    )

    help_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Show comprehensive documentation for all commands",
    )


def get_usage_examples() -> str:
    """Get usage examples for the main help text.

    Returns:
        Formatted usage examples string
    """
    return """Examples:
  # Basic setup with auto-detection (Claude Desktop)
  mcp-config setup mcp-code-checker my-checker --project-dir .
  
  # Setup for VSCode workspace (recommended for team sharing)
  mcp-config setup mcp-code-checker my-project --project-dir . --client vscode-workspace
  
  # Setup for VSCode user profile (personal, all projects) 
  mcp-config setup mcp-code-checker global --project-dir ~/projects --client vscode-user
  
  # Setup with custom parameters
  mcp-config setup mcp-code-checker debug --project-dir . --log-level DEBUG --keep-temp-files
  
  # Full parameter specification
  mcp-config setup mcp-code-checker prod \\
    --project-dir /path/to/project \\
    --python-executable /usr/bin/python3.11 \\
    --venv-path /path/to/project/.venv \\
    --log-level INFO \\
    --log-file /var/log/mcp-checker.log
  
  # Remove a server from VSCode workspace
  mcp-config remove my-project --client vscode-workspace
  
  # List all servers across all clients
  mcp-config list --detailed
  
  # List VSCode servers
  mcp-config list --client vscode-workspace --detailed
  mcp-config list --client vscode-user --detailed"""


def get_setup_examples() -> str:
    """Get usage examples for the setup command.

    Returns:
        Formatted setup examples string
    """
    return """Examples:
  # Basic usage with auto-detection (Claude Desktop)
  mcp-config setup mcp-code-checker my-checker --project-dir .
  
  # Setup for VSCode workspace (recommended for team sharing)
  mcp-config setup mcp-code-checker team-project --project-dir . --client vscode-workspace
  
  # Setup for VSCode user profile (personal, all projects)
  mcp-config setup mcp-code-checker global --project-dir ~/projects --client vscode-user
  
  # Debug configuration
  mcp-config setup mcp-code-checker debug --project-dir . --log-level DEBUG --keep-temp-files
  
  # Custom Python executable
  mcp-config setup mcp-code-checker test --project-dir . --python-executable /usr/bin/python3.11
  
  # Using virtual environment
  mcp-config setup mcp-code-checker venv-test --project-dir . --venv-path .venv
  
  # Console-only logging
  mcp-config setup mcp-code-checker console --project-dir . --console-only
  
  # Dry run to preview changes
  mcp-config setup mcp-code-checker preview --project-dir . --dry-run"""


def get_remove_examples() -> str:
    """Get usage examples for the remove command.

    Returns:
        Formatted remove examples string
    """
    return """Examples:
  # Remove a single server from Claude Desktop
  mcp-config remove my-checker
  
  # Remove from VSCode workspace
  mcp-config remove my-project --client vscode-workspace
  
  # Remove from VSCode user profile
  mcp-config remove global --client vscode-user
  
  # Remove all servers starting with "checker" (client required)
  mcp-config remove "checker*" --client claude-desktop
  
  # Remove all test servers from VSCode workspace
  mcp-config remove "test-*" --client vscode-workspace --force
  
  # Remove servers ending with "-dev" from VSCode workspace
  mcp-config remove "*-dev" --client vscode-workspace
  
  # Dry run to preview removal
  mcp-config remove my-checker --dry-run
  
  # Remove without backup
  mcp-config remove my-checker --no-backup"""


def get_list_examples() -> str:
    """Get usage examples for the list command.

    Returns:
        Formatted list examples string
    """
    return """Examples:
  # List all servers across all clients
  mcp-config list
  
  # List servers for specific client
  mcp-config list --client claude-desktop
  mcp-config list --client vscode-workspace
  mcp-config list --client vscode-user
  
  # Show detailed information
  mcp-config list --detailed
  
  # Show only managed servers
  mcp-config list --managed-only"""


def get_validate_examples() -> str:
    """Get usage examples for the validate command.

    Returns:
        Formatted validate examples string
    """
    return """Examples:
  # Show available server types
  mcp-config validate
  
  # Validate a server configuration
  mcp-config validate my-checker
  
  # Validate with verbose output
  mcp-config validate my-checker --verbose
  
  # Validate for specific clients
  mcp-config validate my-checker --client claude-desktop
  mcp-config validate my-project --client vscode-workspace
  mcp-config validate global --client vscode-user"""


def get_help_examples() -> str:
    """Get usage examples for the help command.

    Returns:
        Formatted help examples string
    """
    return """Examples:
  # Show tool overview
  mcp-config help
  
  # Show help for a specific command
  mcp-config help setup
  mcp-config help remove --verbose
  
  # Show help for server parameters
  mcp-config help mcp-code-checker
  mcp-config help mcp-code-checker --verbose
  
  # Show help for a specific parameter
  mcp-config help mcp-code-checker --parameter project-dir
  
  # Show quick reference for a server
  mcp-config help mcp-code-checker --quick
  
  # Show comprehensive documentation
  mcp-config help --all
  
  # Disambiguate between command and server (if needed)
  mcp-config help setup --command
  mcp-config help mcp-code-checker --server"""


def parse_and_validate_args(
    args: list[str] | None = None,
) -> tuple[argparse.Namespace, list[str]]:
    """Parse command-line arguments and validate them.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Tuple of (parsed arguments, validation errors)
    """
    parser = create_full_parser()
    parsed_args = parser.parse_args(args)

    errors = []

    # Validate based on command
    if parsed_args.command == "setup":
        errors.extend(validate_setup_args(parsed_args))
    elif parsed_args.command == "remove":
        errors.extend(validate_remove_args(parsed_args))
    elif parsed_args.command == "list":
        errors.extend(validate_list_args(parsed_args))

    return parsed_args, errors


def validate_setup_args(args: argparse.Namespace) -> list[str]:
    """Validate setup command arguments.

    Args:
        args: Parsed arguments

    Returns:
        List of validation errors
    """
    errors = []

    # Check that server type is valid
    if args.server_type not in registry.list_servers():
        errors.append(
            f"Unknown server type '{args.server_type}'. "
            f"Available types: {', '.join(registry.list_servers())}"
        )
        return errors  # Can't validate further without valid server type

    # Get server config
    server_config = registry.get(args.server_type)
    if not server_config:
        errors.append(
            f"Could not load configuration for server type '{args.server_type}'"
        )
        return errors

    # Validate required parameters
    for param in server_config.parameters:
        if param.required:
            param_key = param.name.replace("-", "_")
            if not hasattr(args, param_key) or getattr(args, param_key) is None:
                errors.append(f"Required parameter '--{param.name}' is missing")

    # Validate parameter values if validators are defined
    for param in server_config.parameters:
        param_key = param.name.replace("-", "_")
        if hasattr(args, param_key):
            value = getattr(args, param_key)
            if value is not None and param.validator:
                param_errors = param.validator(value, param.name)
                errors.extend(param_errors)

    return errors


def validate_remove_args(args: argparse.Namespace) -> list[str]:
    """Validate remove command arguments.

    Args:
        args: Parsed arguments

    Returns:
        List of validation errors
    """
    errors = []

    # Check that server name is provided
    if not args.server_name:
        errors.append("Server name is required for remove command")

    return errors


def validate_list_args(_args: argparse.Namespace) -> list[str]:
    """Validate list command arguments.

    Args:
        _args: Parsed arguments (unused, kept for consistency)

    Returns:
        List of validation errors
    """
    # No specific validation needed for list command
    return []
