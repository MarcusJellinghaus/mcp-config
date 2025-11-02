"""Claude Code client handler for MCP server configuration."""

import re
from typing import Tuple


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
