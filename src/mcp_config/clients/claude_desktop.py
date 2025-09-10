"""Handler for Claude Desktop client configuration."""

import os
import platform
from pathlib import Path
from typing import Any

from .base import ClientHandler
from .constants import DEFAULT_CLAUDE_CONFIG, MANAGED_SERVER_MARKER
from .utils import (
    backup_config,
    load_json_config,
    load_metadata,
    save_json_config,
    save_metadata,
    validate_server_config,
)


class ClaudeDesktopHandler(ClientHandler):
    """Handler for Claude Desktop client configuration."""

    def get_config_path(self) -> Path:
        """Get Claude Desktop config file path based on platform."""
        # Get home directory as string first to avoid Path type issues
        home_str = str(Path.home())

        if os.name == "nt":  # Windows
            return (
                Path(home_str)
                / "AppData"
                / "Roaming"
                / "Claude"
                / "claude_desktop_config.json"
            )
        elif os.name == "posix":
            if platform.system() == "Darwin":  # macOS
                return (
                    Path(home_str)
                    / "Library"
                    / "Application Support"
                    / "Claude"
                    / "claude_desktop_config.json"
                )
            else:  # Linux
                return (
                    Path(home_str) / ".config" / "claude" / "claude_desktop_config.json"
                )
        else:
            raise OSError(f"Unsupported operating system: {os.name}")

    def load_config(self) -> dict[str, Any]:
        """Load existing Claude Desktop configuration.

        Returns:
            Configuration dictionary, defaulting to {"mcpServers": {}} if not found
        """
        config_path = self.get_config_path()
        config = load_json_config(config_path, DEFAULT_CLAUDE_CONFIG.copy())

        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        return config

    def save_config(self, config: dict[str, Any]) -> None:
        """Save Claude Desktop configuration with proper formatting.

        Args:
            config: Configuration dictionary to save
        """
        config_path = self.get_config_path()
        save_json_config(config_path, config)

    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool:
        """Safely update Claude Desktop config.

        Args:
            server_name: Name for the server instance
            server_config: Server configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup before modification
            self.backup_config()

            # Load existing configuration
            config = self.load_config()

            # Extract metadata fields if present (for backward compatibility)
            metadata_fields = {}
            clean_config = server_config.copy()

            # Extract and remove metadata fields from the config
            if "_managed_by" in clean_config:
                metadata_fields["_managed_by"] = clean_config.pop("_managed_by")
            else:
                # Mark as managed by default
                metadata_fields["_managed_by"] = MANAGED_SERVER_MARKER

            if "_server_type" in clean_config:
                metadata_fields["_server_type"] = clean_config.pop("_server_type")
            else:
                metadata_fields["_server_type"] = "mcp-server"

            # Update only our specific server entry with clean config (no metadata)
            config["mcpServers"][server_name] = clean_config

            # Save the updated configuration
            self.save_config(config)

            # Update metadata separately
            config_path = self.get_config_path()
            metadata = load_metadata(config_path)
            metadata[server_name] = metadata_fields
            save_metadata(config_path, metadata)

            return True

        except Exception as e:
            print(f"Error setting up server '{server_name}': {e}")
            return False

    def remove_server(self, server_name: str) -> bool:
        """Remove only if it's managed by us.

        Args:
            server_name: Name of the server to remove

        Returns:
            True if removed successfully, False otherwise
        """
        try:
            config = self.load_config()
            config_path = self.get_config_path()
            metadata = load_metadata(config_path)

            # Check if server exists
            if server_name not in config.get("mcpServers", {}):
                print(f"Server '{server_name}' not found in configuration")
                return False

            # Check if it's managed by us (check metadata)
            if (
                server_name not in metadata
                or metadata[server_name].get("_managed_by") != MANAGED_SERVER_MARKER
            ):
                print(
                    f"Server '{server_name}' is not managed by this tool. "
                    "Cannot remove external servers."
                )
                return False

            # Create backup before modification
            self.backup_config()

            # Remove the server from config
            del config["mcpServers"][server_name]

            # Save the updated configuration
            self.save_config(config)

            # Remove from metadata
            del metadata[server_name]
            save_metadata(config_path, metadata)

            return True

        except Exception as e:
            print(f"Error removing server '{server_name}': {e}")
            return False

    def list_managed_servers(self) -> list[dict[str, Any]]:
        """List only servers we manage.

        Returns:
            List of dictionaries with server information
        """
        config = self.load_config()
        config_path = self.get_config_path()
        metadata = load_metadata(config_path)
        servers = []

        for name, server_config in config.get("mcpServers", {}).items():
            # Check if this server is in our metadata
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
        """List all servers, mark which ones we manage.

        Returns:
            List of dictionaries with server information
        """
        config = self.load_config()
        config_path = self.get_config_path()
        metadata = load_metadata(config_path)
        servers = []

        for name, server_config in config.get("mcpServers", {}).items():
            # Check if this server is managed
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
        """Create a backup of the current configuration.

        Returns:
            Path to the backup file
        """
        config_path = self.get_config_path()
        return backup_config(config_path, "claude_desktop_config_backup")

    def validate_config(self) -> list[str]:
        """Validate current configuration for basic correctness.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            config = self.load_config()

            # Check mcpServers section (config is always a dict from load_config)
            if "mcpServers" not in config:
                errors.append("Configuration missing 'mcpServers' section")
            elif not isinstance(config["mcpServers"], dict):
                errors.append("'mcpServers' must be an object")
            else:
                # Validate each server entry only if mcpServers is valid
                for name, server_config in config["mcpServers"].items():
                    errors.extend(validate_server_config(name, server_config))

        except Exception as e:
            errors.append(f"Error reading configuration: {e}")

        return errors

    def migrate_inline_metadata(self) -> bool:
        """Migrate any inline metadata fields to separate metadata file.

        This is for backward compatibility - removes _managed_by and _server_type
        fields from the main config and moves them to metadata file.

        Returns:
            True if migration was performed, False if not needed
        """
        try:
            config = self.load_config()
            config_path = self.get_config_path()
            metadata = load_metadata(config_path)
            modified = False

            for name, server_config in config.get("mcpServers", {}).items():
                if "_managed_by" in server_config or "_server_type" in server_config:
                    # Extract metadata fields
                    if name not in metadata:
                        metadata[name] = {}

                    if "_managed_by" in server_config:
                        metadata[name]["_managed_by"] = server_config.pop("_managed_by")
                        modified = True

                    if "_server_type" in server_config:
                        metadata[name]["_server_type"] = server_config.pop(
                            "_server_type"
                        )
                        modified = True

            if modified:
                # Save cleaned config and metadata
                self.save_config(config)
                save_metadata(config_path, metadata)
                return True

            return False

        except Exception:
            return False
