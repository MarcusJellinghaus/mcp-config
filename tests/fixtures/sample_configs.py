"""Centralized sample configurations for testing.

This module provides standard test configurations that can be reused across
different test files to ensure consistency and reduce duplication.
"""

from typing import Any


def get_empty_config() -> dict[str, Any]:
    """Get an empty MCP configuration."""
    return {"mcpServers": {}}


def get_empty_claude_config() -> dict[str, Any]:
    """Get an empty Claude Desktop configuration."""
    return {"mcpServers": {}}


def get_sample_claude_desktop_config() -> dict[str, Any]:
    """Get a sample Claude Desktop configuration with multiple servers."""
    return {
        "mcpServers": {
            "filesystem": {
                "command": "node",
                "args": ["filesystem-server.js"],
            },
            "calculator": {
                "command": "python",
                "args": ["calculator.py"],
                "env": {"PYTHONPATH": "/path/to/lib"},
            },
        }
    }


def get_sample_claude_code_config() -> dict[str, Any]:
    """Get a sample Claude Code configuration."""
    return {
        "mcpServers": {
            "test-server": {
                "type": "stdio",
                "command": "python",
                "args": ["-m", "test"],
            }
        }
    }


def get_managed_server_config() -> dict[str, Any]:
    """Get a sample managed server configuration with metadata."""
    return {
        "command": "/usr/bin/python",
        "args": ["src/main.py", "--project-dir", "/test/project"],
        "env": {"PYTHONPATH": "/test/project"},
        "_managed_by": "mcp-config-managed",
        "_server_type": "mcp-code-checker",
    }


def get_external_server_config() -> dict[str, Any]:
    """Get a sample external (non-managed) server configuration."""
    return {
        "command": "node",
        "args": ["external-server.js", "--port", "3000"],
        "env": {"NODE_ENV": "production"},
    }


def get_invalid_server_config_missing_command() -> dict[str, Any]:
    """Get an invalid server configuration (missing command)."""
    return {
        "args": ["test.py"],  # Missing command field
    }


def get_invalid_server_config_wrong_args_type() -> dict[str, Any]:
    """Get an invalid server configuration (wrong args type)."""
    return {
        "command": "python",
        "args": "should-be-list",  # Wrong type - should be list
    }


def get_invalid_server_config_wrong_env_type() -> dict[str, Any]:
    """Get an invalid server configuration (wrong env type)."""
    return {
        "command": "python",
        "env": ["should", "be", "dict"],  # Wrong type - should be dict
    }


def get_config_with_inline_metadata() -> dict[str, Any]:
    """Get a configuration with inline metadata (old format).

    This is used to test migration from old format to new format with
    separate metadata file.
    """
    return {
        "mcpServers": {
            "old-managed-server": {
                "command": "python",
                "args": ["old.py"],
                "_managed_by": "mcp-config-managed",
                "_server_type": "old-type",
            },
            "external-server": {
                "command": "node",
                "args": ["external.js"],
            },
        }
    }


def get_mixed_config() -> dict[str, Any]:
    """Get a configuration with both managed and external servers."""
    return {
        "mcpServers": {
            "managed-server-1": {
                "command": "/usr/bin/python",
                "args": ["managed1.py"],
                "env": {"KEY": "value"},
            },
            "external-server-1": {
                "command": "node",
                "args": ["external1.js"],
            },
            "managed-server-2": {
                "command": "/usr/bin/python",
                "args": ["managed2.py"],
            },
        }
    }


# Metadata mapping for mixed config
MIXED_CONFIG_METADATA = {
    "managed-server-1": {
        "_managed_by": "mcp-config-managed",
        "_server_type": "type-1",
    },
    "managed-server-2": {
        "_managed_by": "mcp-config-managed",
        "_server_type": "type-2",
    },
    # external-server-1 has no metadata (external)
}
