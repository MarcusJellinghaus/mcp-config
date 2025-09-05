"""Main CLI entry point for MCP Configuration Helper."""

import argparse
import sys
from pathlib import Path
from typing import Any

from . import initialize_all_servers
from .cli_utils import create_full_parser, validate_setup_args
from .clients import get_client_handler
from .detection import detect_python_environment
from .integration import build_server_config, remove_mcp_server, setup_mcp_server
from .output import OutputFormatter
from .servers import registry
from .utils import find_matching_servers, has_wildcard, validate_required_parameters
from .validation import (
    validate_client_installation,
    validate_parameter_combination,
    validate_server_configuration,
)


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    # Use the enhanced parser from cli_utils
    return create_full_parser()


def extract_user_parameters(
    args: argparse.Namespace, server_config: Any
) -> dict[str, Any]:
    """Extract user-provided parameters from CLI args."""
    user_params = {}

    for param in server_config.parameters:
        # Convert parameter name to the arg name (replace - with _)
        arg_name = param.name.replace("-", "_")

        # Get value from args if it exists
        if hasattr(args, arg_name):
            value = getattr(args, arg_name)
            # Only include if value was actually provided (not None or default)
            if value is not None:
                user_params[arg_name] = value

    return user_params


def handle_setup_command(args: argparse.Namespace) -> int:
    """Handle the setup command with full validation and auto-detection."""
    try:
        # Re-initialize to catch any newly installed servers
        if args.verbose:
            print("Checking for server configurations...")
            initialize_all_servers(verbose=False)

        # Validate server type
        server_config = registry.get(args.server_type)
        if not server_config:
            OutputFormatter.print_error(f"Unknown server type '{args.server_type}'")
            print(f"Available types: {', '.join(registry.list_servers())}")
            return 1

        # Get client name directly (no more generic 'vscode' option)
        client = args.client

        # Get client handler
        client_handler = get_client_handler(client)

        # Check if client is installed
        client_warnings = validate_client_installation(client)
        if client_warnings and args.verbose:
            for warning in client_warnings:
                print(f"Warning: {warning}")

        # Extract user parameters from args
        user_params = extract_user_parameters(args, server_config)

        # Auto-detect Python environment if not provided
        auto_detected = {}
        if (
            "python_executable" not in user_params
            or not user_params["python_executable"]
        ):
            project_dir = Path(user_params.get("project_dir", "."))
            python_exe, venv_path = detect_python_environment(project_dir)
            if python_exe:
                user_params["python_executable"] = str(python_exe)
                auto_detected["python_executable"] = str(python_exe)
            if venv_path and "venv_path" not in user_params:
                user_params["venv_path"] = str(venv_path)
                auto_detected["venv_path"] = str(venv_path)

        # Validate required parameters
        validation_errors = validate_required_parameters(server_config, user_params)
        if validation_errors:
            OutputFormatter.print_validation_errors(validation_errors)
            return 1

        # Validate parameter combinations
        combination_errors = validate_parameter_combination(user_params)
        if combination_errors:
            OutputFormatter.print_validation_errors(combination_errors)
            return 1

        # Run additional validation from cli_utils
        cli_errors = validate_setup_args(args)
        if cli_errors:
            OutputFormatter.print_validation_errors(cli_errors)
            return 1

        # Show what will be done
        if args.dry_run:
            OutputFormatter.print_dry_run_header()

            # Show auto-detected parameters
            if auto_detected:
                OutputFormatter.print_auto_detected_params(auto_detected)
                print()

            # Build the server config that would be saved
            server_cfg = build_server_config(
                server_config,
                user_params,
                user_params.get("python_executable", sys.executable),
            )

            # Generate backup path based on client type
            backup_path = None
            use_backup = getattr(args, "backup", True)

            if use_backup:
                try:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    config_name = (
                        "mcp_config"
                        if client.startswith("vscode")
                        else "claude_desktop_config"
                    )
                    config_path = client_handler.get_config_path()
                    backup_path = (
                        config_path.parent / f"{config_name}.backup_{timestamp}.json"
                    )

                    # Ensure backup path parent directory exists for path operations
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    # If backup path operations fail, disable backup for dry-run
                    use_backup = False
                    backup_path = None

            # Create a preview config with name and type for display
            preview_config = {
                "name": args.server_name,
                "type": (
                    server_config.name
                    if hasattr(server_config, "name")
                    else args.server_type
                ),
                "command": server_cfg.get("command", ""),
                "args": server_cfg.get("args", []),
            }

            try:
                OutputFormatter.print_dry_run_config_preview(
                    preview_config,
                    client_handler.get_config_path(),
                    backup_path if use_backup else None,
                )
                return 0
            except Exception as e:
                # Handle preview errors gracefully without failing the dry-run
                print(f"\nError generating preview: {e}")
                if args.verbose:
                    import traceback

                    traceback.print_exc()

                # Still show basic info even if preview fails
                print("\nWould update configuration:")
                print(f"  Server: {args.server_name}")
                print(
                    f"  Type: {server_config.name if hasattr(server_config, 'name') else args.server_type}"
                )
                print(f"  File: {client_handler.get_config_path()}")
                if backup_path and use_backup:
                    print(f"  Backup: {backup_path}")
                # Use safe printing for success message
                try:
                    print(
                        f"\n{OutputFormatter.SUCCESS} Configuration valid. Run without --dry-run to apply."
                    )
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(
                        "\n[SUCCESS] Configuration valid. Run without --dry-run to apply."
                    )
                return 0
        elif args.verbose:
            OutputFormatter.print_configuration_details(
                args.server_name, server_config.name, user_params
            )

        # Perform setup
        result = setup_mcp_server(
            client_handler=client_handler,
            server_config=server_config,
            server_name=args.server_name,
            user_params=user_params,
            python_executable=user_params.get("python_executable", sys.executable),
            dry_run=False,
        )

        if result["success"]:
            try:
                print(f"✓ Successfully configured server '{args.server_name}'")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"[SUCCESS] Successfully configured server '{args.server_name}'")
            if "backup_path" in result:
                print(f"  Backup created: {result['backup_path']}")
            print(f"  Configuration saved to: {client_handler.get_config_path()}")
            return 0
        else:
            try:
                print(
                    f"✗ Failed to configure server: {result.get('error', 'Unknown error')}"
                )
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(
                    f"[ERROR] Failed to configure server: {result.get('error', 'Unknown error')}"
                )
            return 1

    except Exception as e:
        print(f"Setup failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def handle_remove_command(args: argparse.Namespace) -> int:
    """Handle the remove command with safety checks."""
    try:
        # Check if using wildcards
        is_wildcard = has_wildcard(args.server_name)

        # If using wildcards, client must be explicitly specified
        if (
            is_wildcard
            and args.client == "claude-desktop"
            and "--client" not in sys.argv
        ):
            OutputFormatter.print_error(
                "When using wildcards, --client must be explicitly specified"
            )
            print("Example: mcp-config remove 'checker*' --client claude-desktop")
            return 1

        # Get client name directly (no more generic 'vscode' option)
        client = args.client
        clients_to_process = [client]

        # Process all relevant clients
        total_removed = 0
        all_matched_servers = []

        for client_name in clients_to_process:
            try:
                # Get client handler
                client_handler = get_client_handler(client_name)

                # Skip if config doesn't exist
                if not client_handler.get_config_path().exists():
                    continue

                # Get managed servers
                managed_servers = client_handler.list_managed_servers()

                # Find matching servers
                if is_wildcard:
                    matched = find_matching_servers(managed_servers, args.server_name)
                    for server in matched:
                        server["client"] = client_name  # Track which client
                        all_matched_servers.append(server)
                else:
                    # Single server removal
                    managed_names = [s["name"] for s in managed_servers]

                    if args.server_name not in managed_names:
                        all_servers = client_handler.list_all_servers()
                        all_names = [s["name"] for s in all_servers]

                        if args.server_name in all_names:
                            OutputFormatter.print_error(
                                f"Server '{args.server_name}' exists but is not managed by mcp-config"
                            )
                            print("Only servers created by mcp-config can be removed")
                            return 1
                        else:
                            if len(clients_to_process) == 1:
                                OutputFormatter.print_error(
                                    f"Server '{args.server_name}' not found"
                                )
                                if managed_names:
                                    print(
                                        f"Managed servers: {', '.join(managed_names)}"
                                    )
                            continue

                    server_info = next(
                        s for s in managed_servers if s["name"] == args.server_name
                    )
                    server_info["client"] = client_name
                    all_matched_servers.append(server_info)

            except Exception as e:
                if args.verbose:
                    print(f"Error accessing {client_name}: {e}")
                continue

        # Check if we found any servers
        if not all_matched_servers:
            if is_wildcard:
                OutputFormatter.print_error(
                    f'No managed servers found matching pattern "{args.server_name}"'
                )
                print("\nTip: Use 'mcp-config list' to see available servers")
            else:
                OutputFormatter.print_error(f"Server '{args.server_name}' not found")
                print("\nTip: Use 'mcp-config list' to see available servers")
            return 1

        # Show what will be removed
        if args.dry_run:
            OutputFormatter.print_dry_run_header()

            if is_wildcard:
                print(f'\nPattern: "{args.server_name}"')
                print(f"Matched {len(all_matched_servers)} server(s):")
                for server in all_matched_servers:
                    print(
                        f"  • {server['name']} ({server['type']}) - {server['client']}"
                    )
            else:
                server_info = all_matched_servers[0]
                # Get other servers that will be preserved
                client_handler = get_client_handler(server_info["client"])
                all_servers = client_handler.list_all_servers()
                other_servers = [
                    s for s in all_servers if s["name"] != args.server_name
                ]

                # Generate backup path
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                config_name = (
                    "mcp_config"
                    if server_info["client"].startswith("vscode")
                    else "claude_desktop_config"
                )
                backup_path = (
                    client_handler.get_config_path().parent
                    / f"{config_name}.backup_{timestamp}.json"
                )

                OutputFormatter.print_dry_run_remove_preview(
                    args.server_name,
                    server_info,
                    other_servers,
                    client_handler.get_config_path(),
                    backup_path if args.backup else None,
                )
            return 0

        # For multiple servers, show confirmation unless --force is used
        if is_wildcard and len(all_matched_servers) > 0 and not args.force:
            print(f"\nAbout to remove {len(all_matched_servers)} server(s):")
            for server in all_matched_servers:
                print(f"  • {server['name']} ({server['type']}) - {server['client']}")

            # Ask for confirmation
            print(
                "\nThis action cannot be undone"
                + (" (backup will be created)" if args.backup else "")
                + "."
            )
            response = input("Do you want to proceed? (y/N): ")
            if response.lower() != "y":
                print("Operation cancelled.")
                return 0
        elif args.verbose:
            if is_wildcard:
                print(
                    f'Will remove {len(all_matched_servers)} server(s) matching "{args.server_name}"'
                )
            else:
                server_info = all_matched_servers[0]
                print(f"Will remove server '{server_info['name']}':")
                print(f"  Type: {server_info['type']}")
                print(f"  Command: {server_info['command']}")

        # Perform removal(s)
        failed_removals = []
        success_removals = []
        backup_paths = []

        # Group servers by client for efficient removal
        from collections import defaultdict

        servers_by_client = defaultdict(list)
        for server in all_matched_servers:
            servers_by_client[server["client"]].append(server)

        for client_name, servers in servers_by_client.items():
            client_handler = get_client_handler(client_name)

            for server in servers:
                result = remove_mcp_server(
                    client_handler=client_handler,
                    server_name=server["name"],
                    dry_run=False,
                )

                if result["success"]:
                    success_removals.append((server["name"], client_name))
                    if (
                        "backup_path" in result
                        and result["backup_path"] not in backup_paths
                    ):
                        backup_paths.append(result["backup_path"])
                else:
                    failed_removals.append(
                        (
                            server["name"],
                            client_name,
                            result.get("error", "Unknown error"),
                        )
                    )

        # Report results
        if success_removals:
            if len(success_removals) == 1:
                name, client = success_removals[0]
                try:
                    print(f"✓ Successfully removed server '{name}'")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(f"[SUCCESS] Successfully removed server '{name}'")
            else:
                try:
                    print(f"✓ Successfully removed {len(success_removals)} server(s):")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(
                        f"[SUCCESS] Successfully removed {len(success_removals)} server(s):"
                    )
                for name, client in success_removals:
                    print(f"  • {name} ({client})")

            if backup_paths:
                if len(backup_paths) == 1:
                    print(f"  Backup created: {backup_paths[0]}")
                else:
                    print("  Backups created:")
                    for path in backup_paths:
                        print(f"    • {path}")

        if failed_removals:
            try:
                print(f"\n✗ Failed to remove {len(failed_removals)} server(s):")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"\n[ERROR] Failed to remove {len(failed_removals)} server(s):")
            for name, client, error in failed_removals:
                print(f"  • {name} ({client}): {error}")
            return 1

        return 0 if success_removals else 1

    except Exception as e:
        print(f"Remove failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def handle_list_command(args: argparse.Namespace) -> int:
    """Handle the list command with detailed output."""
    try:
        # Get client handler(s)
        if args.client:
            # Get client name directly
            clients = [args.client]
        else:
            # List all clients when no specific client is specified
            clients = ["claude-desktop", "vscode-workspace", "vscode-user"]

        for client_name in clients:
            try:
                client_handler = get_client_handler(client_name)
                config_path = client_handler.get_config_path()

                # Skip if config doesn't exist (especially for VSCode configs)
                if not config_path.exists():
                    continue

                if args.managed_only:
                    servers = client_handler.list_managed_servers()
                else:
                    servers = client_handler.list_all_servers()

                # Only show if there are servers or if a specific client was requested
                if servers or args.client:
                    # Use enhanced output formatter
                    OutputFormatter.print_enhanced_server_list(
                        servers, client_name, config_path, args.detailed
                    )
            except Exception as e:
                if args.client:
                    # Only show errors if a specific client was requested
                    print(f"Error reading {client_name} configuration: {e}")
                # Otherwise silently skip non-existent configs

        return 0

    except Exception as e:
        print(f"List failed: {e}")
        if hasattr(args, "verbose") and args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def handle_help_command(args: argparse.Namespace) -> int:
    """Handle the help command to show detailed documentation."""
    try:
        from .help_system import (
            print_command_help,
            print_parameter_help,
            print_quick_reference,
        )

        # Handle --all flag
        if args.all:
            return print_command_help("all", verbose=True)

        # Determine what kind of help to show
        topic = args.topic

        # List of known commands
        commands = ["setup", "remove", "list", "validate", "help", "all"]

        # List of known server types
        server_types = registry.list_servers()

        # If no topic specified, show overview
        if not topic:
            if args.quick:
                # Show quick reference for all servers
                return print_quick_reference(None)
            else:
                # Show tool overview
                return print_command_help(None, args.verbose)

        # Determine topic type
        is_command = topic in commands or args.command
        is_server = topic in server_types or args.server

        # Handle conflicts
        if args.command and args.server:
            print("Error: Cannot use both --command and --server flags")
            return 1

        # If topic could be both, prefer command unless --server is specified
        if not is_command and not is_server:
            print(f"Unknown topic: {topic}")
            print(f"Available commands: {', '.join(commands)}")
            print(f"Available servers: {', '.join(server_types)}")
            return 1

        # Show command help
        if is_command and not args.server:
            if args.parameter:
                print("Error: --parameter flag is only for server help")
                return 1
            if args.quick:
                print("Error: --quick flag is only for server help")
                return 1
            return print_command_help(topic, args.verbose)

        # Show server help
        if is_server and not args.command:
            if args.quick:
                return print_quick_reference(topic)
            elif args.parameter:
                return print_parameter_help(topic, args.parameter, verbose=True)
            else:
                return print_parameter_help(topic, None, args.verbose)

        # Shouldn't reach here
        print(f"Could not determine help type for: {topic}")
        return 1

    except Exception as e:
        print(f"Failed to show help: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def handle_validate_command(args: argparse.Namespace) -> int:
    """Handle the validate command with comprehensive checks."""
    try:
        # Get client name directly (no more generic 'vscode' option)
        client = args.client

        # Get client handler
        client_handler = get_client_handler(client)

        # If no server name provided, show available types and configured servers
        if not args.server_name:
            configs = registry.get_all_configs()
            if configs:
                print("Available MCP server types:")
                for name, config in sorted(configs.items()):
                    print(f"  • {name}: {config.display_name}")
                print()

            # Also list configured servers for validation
            managed_servers = client_handler.list_managed_servers()
            if managed_servers:
                print("Configured servers:")
                for server in managed_servers:
                    print(f"  • {server['name']} ({server['type']})")
                print()
                print(
                    "Use: mcp-config validate <server-name> to check a configured server"
                )
            else:
                print("No servers configured yet.")
                print(
                    "Use: mcp-config setup <server-type> <server-name> to configure a server"
                )

            return 0

        # Get server configuration from client
        servers = client_handler.list_all_servers()
        server_info = None
        for server in servers:
            if server["name"] == args.server_name:
                server_info = server
                break

        if not server_info:
            OutputFormatter.print_error(
                f"Server '{args.server_name}' not found in {args.client} configuration"
            )
            managed_servers = client_handler.list_managed_servers()
            if managed_servers:
                print("\nAvailable managed servers:")
                for server in managed_servers:
                    print(f"  • {server['name']} ({server['type']})")
            return 1

        # Extract parameters from server configuration
        # This is a simplified extraction - in production, we'd parse the args
        params = {}
        if server_info.get("args"):
            args_list = server_info["args"]
            # Simple parsing of common parameters
            for i, arg in enumerate(args_list):
                if arg == "--project-dir" and i + 1 < len(args_list):
                    params["project_dir"] = args_list[i + 1]
                elif arg == "--python-executable" and i + 1 < len(args_list):
                    params["python_executable"] = args_list[i + 1]
                elif arg == "--venv-path" and i + 1 < len(args_list):
                    params["venv_path"] = args_list[i + 1]
                elif arg == "--test-folder" and i + 1 < len(args_list):
                    params["test_folder"] = args_list[i + 1]
                elif arg == "--log-file" and i + 1 < len(args_list):
                    params["log_file"] = args_list[i + 1]
                elif arg == "--log-level" and i + 1 < len(args_list):
                    params["log_level"] = args_list[i + 1]

        # Get the Python executable from command if not in args
        if "python_executable" not in params and server_info.get("command"):
            params["python_executable"] = server_info["command"]

        print(
            f"Validating '{args.server_name}' ({server_info.get('type', 'unknown')}):"
        )

        # Run comprehensive validation
        validation_result = validate_server_configuration(
            args.server_name, server_info.get("type", "unknown"), params, client_handler
        )

        # Print validation results
        OutputFormatter.print_validation_results(validation_result)

        return 0 if validation_result["success"] else 1

    except Exception as e:
        print(f"Validation failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def main() -> int:
    """Main CLI entry point."""
    try:
        parser = create_main_parser()
        args = parser.parse_args()

        # Dispatch to appropriate handler
        if args.command == "setup":
            return handle_setup_command(args)
        elif args.command == "remove":
            return handle_remove_command(args)
        elif args.command == "list":
            return handle_list_command(args)
        elif args.command == "validate":
            return handle_validate_command(args)
        elif args.command == "help":
            return handle_help_command(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if "args" in locals() and hasattr(args, "verbose") and args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
