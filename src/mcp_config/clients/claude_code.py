"""Claude Code client handler for MCP server configuration."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

from .base import ClientHandler
from .constants import DEFAULT_CLAUDE_CONFIG
from .utils import (
    load_json_config,
    save_json_config,
    validate_server_config,
)


def normalize_server_name(name: str) -> Tuple[str, bool]:
    """
    Normalize server name to meet Claude Code requirements.

    Claude Code requires server names matching pattern: ^[a-zA-Z0-9_-]{1,64}$

    Args:
        name: Original server name

    Returns:
        Tuple of (normalized_name, was_modified)

    Raises:
        ValueError: If the normalized name would be empty

    Examples:
        >>> normalize_server_name("my-server")
        ('my-server', False)
        >>> normalize_server_name("my server!")
        ('my_server', True)
        >>> normalize_server_name("a" * 100)
        ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', True)
    """
    original = name

    # Step 1: Replace spaces with underscores
    normalized = name.replace(" ", "_")

    # Step 2: Remove invalid characters (keep only a-zA-Z0-9_-)
    normalized = re.sub(r"[^a-zA-Z0-9_-]", "", normalized)

    # Step 3: Truncate to 64 chars maximum
    normalized = normalized[:64]

    # Step 4: Check for empty string after normalization
    if not normalized:
        raise ValueError(
            f"Server name '{original}' contains no valid characters after normalization. "
            "Server names must contain at least one letter, number, underscore, or hyphen."
        )

    # Step 5: Check if modified
    was_modified = normalized != original

    # Step 6: Return tuple
    return normalized, was_modified


class ClaudeCodeHandler(ClientHandler):
    """Handler for Claude Code project configuration (.mcp.json)."""

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize handler with optional config directory.

        Args:
            config_dir: Directory for .mcp.json (defaults to cwd)
        """
        self.config_dir = config_dir if config_dir is not None else Path.cwd()

    def get_config_path(self) -> Path:
        """Get path to .mcp.json in project root.

        Returns:
            Path to .mcp.json configuration file
        """
        return self.config_dir / ".mcp.json"

    def load_config(self) -> dict[str, Any]:
        """Load existing .mcp.json configuration.

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
        """Save .mcp.json with proper formatting.

        Args:
            config: Configuration dictionary to save
        """
        config_path = self.get_config_path()
        save_json_config(config_path, config)

    def _check_user_config_warning(self) -> None:
        """Check for user-level .mcp.json and print warning if exists."""
        user_config = Path.home() / ".mcp.json"
        if user_config.exists():
            print(
                f"Note: Found user-level configuration at {user_config}. "
                "This tool manages the project-level .mcp.json file. "
                "Be aware that both configurations may be used."
            )

    def _add_type_field(self, server_config: dict[str, Any]) -> dict[str, Any]:
        """Add 'type': 'stdio' to server configuration.

        Args:
            server_config: Server configuration dictionary

        Returns:
            Server configuration with type field added
        """
        config_copy = server_config.copy()
        config_copy["type"] = "stdio"
        return config_copy

    def _strip_metadata_fields(self, server_config: dict[str, Any]) -> dict[str, Any]:
        """Remove metadata fields like _server_type from config.

        Args:
            server_config: Server configuration dictionary

        Returns:
            Server configuration with metadata fields removed
        """
        config_copy = server_config.copy()
        # Remove internal metadata fields
        config_copy.pop("_server_type", None)
        config_copy.pop("_managed_by", None)
        return config_copy

    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool:
        """Add server to .mcp.json with type field and name normalization.

        Args:
            server_name: Name for the server instance
            server_config: Server configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Normalize server name
            normalized_name, was_modified = normalize_server_name(server_name)

            # 2. Print normalization message if name changed
            if was_modified:
                print(
                    f"Server name normalized: '{server_name}' -> '{normalized_name}'"
                )

            # 3. Check and warn about user-level config
            self._check_user_config_warning()

            # 4. Create backup of existing config
            self.backup_config()

            # 5. Load current configuration
            config = self.load_config()

            # 6. Strip metadata fields from server_config
            clean_config = self._strip_metadata_fields(server_config)

            # 7. Add "type": "stdio" to server_config
            clean_config = self._add_type_field(clean_config)

            # 8. Add server to config["mcpServers"]
            config["mcpServers"][normalized_name] = clean_config

            # 9. Save updated configuration
            self.save_config(config)

            # 10. Return True on success
            return True

        except Exception as e:
            print(f"Error setting up server '{server_name}': {e}")
            return False

    def remove_server(self, server_name: str) -> bool:
        """Remove server from .mcp.json (all servers removable).

        Args:
            server_name: Name of the server to remove

        Returns:
            True if removed successfully, False otherwise
        """
        try:
            # 1. Load current configuration
            config = self.load_config()

            # 2. Check if server exists in mcpServers
            if server_name not in config.get("mcpServers", {}):
                print(f"Server '{server_name}' not found in configuration")
                return False

            # 3. Create backup of existing config
            self.backup_config()

            # 4. Remove server from config["mcpServers"]
            del config["mcpServers"][server_name]

            # 5. Save updated configuration
            self.save_config(config)

            # 6. Return True on success
            return True

        except Exception as e:
            print(f"Error removing server '{server_name}': {e}")
            return False

    def list_managed_servers(self) -> list[dict[str, Any]]:
        """List all servers (all are managed in Claude Code).

        Returns:
            List of dictionaries with server information
        """
        config = self.load_config()
        servers = []

        for name, server_config in config.get("mcpServers", {}).items():
            # Infer server type from command or mark as unknown
            server_type = "unknown"
            command = server_config.get("command", "")

            # Try to infer type from command path
            if "mcp-code-checker" in command or "code-checker" in command:
                server_type = "mcp-code-checker"
            elif "filesystem" in command:
                server_type = "mcp-server-filesystem"
            # Add more inference logic as needed

            servers.append(
                {
                    "name": name,
                    "type": server_type,
                    "command": server_config.get("command", ""),
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {}),
                    "managed": True,  # All servers are managed in Claude Code
                }
            )

        return servers

    def list_all_servers(self) -> list[dict[str, Any]]:
        """List all servers (same as managed for Claude Code).

        Returns:
            List of dictionaries with server information
        """
        # For Claude Code, all servers are managed
        return self.list_managed_servers()

    def backup_config(self) -> Path:
        """Create backup with .mcp.backup_* pattern.

        Returns:
            Path to the backup file
        """
        config_path = self.get_config_path()

        if not config_path.exists():
            # Nothing to backup, return the config path
            return config_path

        # Generate backup filename with timestamp using hidden file pattern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f".mcp.backup_{timestamp}.json"
        backup_path = config_path.parent / backup_name

        # Copy the configuration file
        shutil.copy2(config_path, backup_path)

        return backup_path

    def validate_config(self) -> list[str]:
        """Validate config including type field requirement.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            config_path = self.get_config_path()
            
            # Check if config file exists
            if not config_path.exists():
                # No config file is valid (will use default)
                return errors
            
            # Try to load and parse the config
            import json
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in configuration: {e}")
                return errors

            # Check mcpServers section
            if "mcpServers" not in config:
                errors.append("Configuration missing 'mcpServers' section")
            elif not isinstance(config["mcpServers"], dict):
                errors.append("'mcpServers' must be an object")
            else:
                # Validate each server entry
                for name, server_config in config["mcpServers"].items():
                    errors.extend(validate_server_config(name, server_config))

        except Exception as e:
            errors.append(f"Error reading configuration: {e}")

        return errors
