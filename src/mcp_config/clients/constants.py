"""Constants shared across MCP client handlers."""

from typing import Any, Dict

# Metadata constants
MANAGED_SERVER_MARKER = "mcp-config-managed"
METADATA_FILE = ".mcp-config-metadata.json"

# Default configuration structures
DEFAULT_CLAUDE_CONFIG: Dict[str, Dict[str, Any]] = {"mcpServers": {}}
DEFAULT_GENERIC_CONFIG: Dict[str, Dict[str, Any]] = {"servers": {}}
