"""Handler for VSCode native MCP configuration (VSCode 1.102+)."""

import os
import platform
from pathlib import Path
from typing import Any

from .base import ClientHandler
from .constants import DEFAULT_GENERIC_CONFIG, MANAGED_SERVER_MARKER
from .utils import (
    backup_config,
    load_json_config,
    load_metadata,
    save_json_config,
    save_metadata,
    validate_server_config,
)


class VSCodeHandler(ClientHandler):
    """Handler for VSCode native MCP configuration (VSCode 1.102+)."""

    def __init__(self, workspace: bool = True):
        """Initialize VSCode handler.

        Args:
            workspace: If True, use workspace config (.vscode/mcp.json).
                      If False, use user profile config.
        """
        self.workspace = workspace

    def get_config_path(self) -> Path:
        """Get VSCode MCP config file path."""
        if self.workspace:
            # Workspace configuration in current directory
            return Path.cwd() / ".vscode" / "mcp.json"
        else:
            # User profile configuration
            home_str = str(Path.home())
            if os.name == "nt":  # Windows
                return (
                    Path(home_str)
                    / "AppData"
                    / "Roaming"
                    / "Code"
                    / "User"
                    / "mcp.json"
                )
            elif platform.system() == "Darwin":  # macOS
                return (
                    Path(home_str)
                    / "Library"
                    / "Application Support"
                    / "Code"
                    / "User"
                    / "mcp.json"
                )
            else:  # Linux
                return Path(home_str) / ".config" / "Code" / "User" / "mcp.json"

    def load_config(self) -> dict[str, Any]:
        """Load existing VSCode MCP configuration."""
        config_path = self.get_config_path()
        config = load_json_config(config_path, DEFAULT_GENERIC_CONFIG.copy())

        if "servers" not in config:
            config["servers"] = {}

        return config

    def save_config(self, config: dict[str, Any]) -> None:
        """Save VSCode MCP configuration."""
        config_path = self.get_config_path()
        save_json_config(config_path, config)

    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool:
        """Add server to VSCode MCP config."""
        try:
            self.backup_config()
            config = self.load_config()

            # Extract metadata fields
            metadata_fields = {
                "_managed_by": MANAGED_SERVER_MARKER,
                "_server_type": server_config.get("_server_type", "mcp-code-checker"),
            }

            # Clean config for VSCode format (no metadata in main config)
            clean_config = {
                "command": server_config["command"],
                "args": server_config["args"],
            }
            if "env" in server_config and server_config["env"]:
                clean_config["env"] = server_config["env"]

            # Update server configuration
            config["servers"][server_name] = clean_config

            # Save config and metadata
            self.save_config(config)

            config_path = self.get_config_path()
            metadata = load_metadata(config_path)
            metadata[server_name] = metadata_fields
            save_metadata(config_path, metadata)

            return True

        except Exception as e:
            print(f"Error setting up server '{server_name}': {e}")
            return False

    def remove_server(self, server_name: str) -> bool:
        """Remove server from VSCode config if managed by us."""
        try:
            config = self.load_config()
            config_path = self.get_config_path()
            metadata = load_metadata(config_path)

            if server_name not in config.get("servers", {}):
                print(f"Server '{server_name}' not found in configuration")
                return False

            if (
                server_name not in metadata
                or metadata[server_name].get("_managed_by") != MANAGED_SERVER_MARKER
            ):
                print(
                    f"Server '{server_name}' is not managed by this tool. Cannot remove external servers."
                )
                return False

            self.backup_config()

            del config["servers"][server_name]
            self.save_config(config)

            del metadata[server_name]
            save_metadata(config_path, metadata)

            return True

        except Exception as e:
            print(f"Error removing server '{server_name}': {e}")
            return False

    def list_managed_servers(self) -> list[dict[str, Any]]:
        """List only servers managed by this tool."""
        config = self.load_config()
        config_path = self.get_config_path()
        metadata = load_metadata(config_path)
        servers = []

        for name, server_config in config.get("servers", {}).items():
            if (
                name in metadata
                and metadata[name].get("_managed_by") == MANAGED_SERVER_MARKER
            ):
                servers.append(
                    {
                        "name": name,
                        "type": metadata[name].get("_server_type", "unknown"),
                        "command": server_config.get("command", ""),
                        "args": server_config.get("args", []),
                        "env": server_config.get("env", {}),
                    }
                )

        return servers

    def list_all_servers(self) -> list[dict[str, Any]]:
        """List all servers in configuration."""
        config = self.load_config()
        config_path = self.get_config_path()
        metadata = load_metadata(config_path)
        servers = []

        for name, server_config in config.get("servers", {}).items():
            is_managed = (
                name in metadata
                and metadata[name].get("_managed_by") == MANAGED_SERVER_MARKER
            )

            server_type = "unknown"
            if is_managed and name in metadata:
                server_type = metadata[name].get("_server_type", "unknown")

            servers.append(
                {
                    "name": name,
                    "managed": is_managed,
                    "type": server_type,
                    "command": server_config.get("command", ""),
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {}),
                }
            )

        return servers

    def backup_config(self) -> Path:
        """Create a backup of the current configuration."""
        config_path = self.get_config_path()
        return backup_config(config_path, "mcp_backup")

    def validate_config(self) -> list[str]:
        """Validate current configuration."""
        errors = []

        try:
            config = self.load_config()

            if "servers" not in config:
                errors.append("Configuration missing 'servers' section")
            elif not isinstance(config["servers"], dict):
                errors.append("'servers' must be an object")
            else:
                for name, server_config in config["servers"].items():
                    errors.extend(validate_server_config(name, server_config))

        except Exception as e:
            errors.append(f"Error reading configuration: {e}")

        return errors
