"""Shared utilities for MCP client handlers."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import METADATA_FILE


def load_metadata(config_path: Path) -> dict[str, Any]:
    """Load metadata about managed servers.

    Args:
        config_path: Path to the client's configuration file

    Returns:
        Dictionary mapping server names to their metadata
    """
    metadata_path = config_path.parent / METADATA_FILE

    if not metadata_path.exists():
        return {}

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        # If there's an error reading metadata, start fresh
        return {}


def save_metadata(config_path: Path, metadata: dict[str, Any]) -> None:
    """Save metadata about managed servers.

    Args:
        config_path: Path to the client's configuration file
        metadata: Dictionary mapping server names to their metadata
    """
    metadata_path = config_path.parent / METADATA_FILE

    # Ensure parent directory exists
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    # Write metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_json_config(
    config_path: Path, default_config: dict[str, Any]
) -> dict[str, Any]:
    """Load JSON configuration file with error handling.

    Args:
        config_path: Path to the configuration file
        default_config: Default configuration to return if file doesn't exist or has errors

    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config: dict[str, Any] = json.load(f)
            return config
    except (json.JSONDecodeError, IOError) as e:
        # If there's an error reading/parsing, return default
        # but log warning if needed in production
        print(f"Warning: Error loading config from {config_path}: {e}")
        return default_config


def save_json_config(config_path: Path, config: dict[str, Any]) -> None:
    """Save JSON configuration with atomic write and proper formatting.

    Args:
        config_path: Path to save the configuration file
        config: Configuration dictionary to save
    """
    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first (atomic write)
    temp_path = config_path.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline

        # Replace the original file atomically
        temp_path.replace(config_path)

    except Exception:
        # Clean up temp file if something went wrong
        if temp_path.exists():
            temp_path.unlink()
        raise


def backup_config(config_path: Path, backup_prefix: str = "backup") -> Path:
    """Create a backup of the current configuration.

    Args:
        config_path: Path to the configuration file to backup
        backup_prefix: Prefix for the backup filename

    Returns:
        Path to the backup file
    """
    if not config_path.exists():
        # Nothing to backup
        return config_path

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{backup_prefix}_{timestamp}.json"
    backup_path = config_path.parent / backup_name

    # Copy the configuration file
    shutil.copy2(config_path, backup_path)

    return backup_path


def validate_server_config(name: str, server_config: dict[str, Any]) -> list[str]:
    """Validate a single server configuration.

    Args:
        name: Server name
        server_config: Server configuration dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(server_config, dict):
        errors.append(f"Server '{name}' configuration must be an object")
        return errors

    # Check required fields
    if "command" not in server_config:
        errors.append(f"Server '{name}' missing required 'command' field")

    if "args" in server_config and not isinstance(server_config["args"], list):
        errors.append(f"Server '{name}' 'args' field must be an array")

    if "env" in server_config and not isinstance(server_config["env"], dict):
        errors.append(f"Server '{name}' 'env' field must be an object")

    return errors
