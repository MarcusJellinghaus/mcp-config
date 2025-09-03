#!/usr/bin/env python
"""Manual test script for wildcard removal functionality.

This script demonstrates the new wildcard removal feature for mcp-config.
"""

import json
import sys
import tempfile
from pathlib import Path

from src.mcp_config.clients import ClaudeDesktopHandler
from src.mcp_config.utils import find_matching_servers, has_wildcard, match_pattern

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_wildcard_functions() -> None:
    """Test the wildcard utility functions."""
    print("\n=== Testing Wildcard Functions ===\n")

    # Test has_wildcard
    patterns = ["checker*", "*-dev", "test-?", "normal-name", "server[123]"]
    for pattern in patterns:
        result = has_wildcard(pattern)
        print(f"has_wildcard('{pattern}'): {result}")

    print("\n--- Pattern Matching ---\n")

    # Test match_pattern
    test_cases = [
        ("checker-main", "checker*", True),
        ("test-checker", "checker*", False),
        ("server-dev", "*-dev", True),
        ("development", "*-dev", False),
        ("test-1", "test-?", True),
        ("test-12", "test-?", False),
    ]

    for name, pattern, expected in test_cases:
        result = match_pattern(name, pattern)
        status = "✓" if result == expected else "✗"
        print(f"{status} match_pattern('{name}', '{pattern}'): {result}")

    print("\n--- Finding Matching Servers ---\n")

    # Test find_matching_servers
    servers = [
        {"name": "checker-main", "type": "mcp-code-checker"},
        {"name": "checker-dev", "type": "mcp-code-checker"},
        {"name": "checker-test", "type": "mcp-code-checker"},
        {"name": "filesystem-prod", "type": "mcp-server-filesystem"},
        {"name": "test-checker", "type": "mcp-code-checker"},
        {"name": "my-server", "type": "other"},
    ]

    patterns_to_test = ["checker*", "*-dev", "test-*", "*"]
    for pattern in patterns_to_test:
        matched = find_matching_servers(servers, pattern)
        print(f"\nPattern '{pattern}' matches {len(matched)} server(s):")
        for server in matched:
            print(f"  • {server['name']} ({server['type']})")


def test_cli_example() -> None:
    """Show example CLI commands for wildcard removal."""
    print("\n\n=== Example CLI Commands ===\n")

    examples = [
        (
            "Remove all servers starting with 'checker'",
            "mcp-config remove 'checker*' --client claude-desktop",
        ),
        (
            "Remove all development servers from VSCode",
            "mcp-config remove '*-dev' --client vscode-workspace",
        ),
        (
            "Remove test servers without confirmation",
            "mcp-config remove 'test-*' --client claude-desktop --force",
        ),
        (
            "Preview what would be removed (dry-run)",
            "mcp-config remove 'checker*' --client claude-desktop --dry-run",
        ),
        (
            "Remove from both VSCode workspace and user configs",
            "mcp-config remove '*-old' --client vscode --force",
        ),
    ]

    for description, command in examples:
        print(f"{description}:")
        print(f"  $ {command}\n")


def simulate_removal_workflow() -> None:
    """Simulate a removal workflow with dummy data."""
    print("\n=== Simulated Removal Workflow ===\n")

    # Create a temporary config file with test data
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config = {
            "mcpServers": {
                "checker-main": {
                    "command": "python",
                    "args": ["-m", "mcp_code_checker", "--project-dir", "/main"],
                    "_managed_by": "mcp-config",
                },
                "checker-dev": {
                    "command": "python",
                    "args": ["-m", "mcp_code_checker", "--project-dir", "/dev"],
                    "_managed_by": "mcp-config",
                },
                "checker-test": {
                    "command": "python",
                    "args": ["-m", "mcp_code_checker", "--project-dir", "/test"],
                    "_managed_by": "mcp-config",
                },
                "filesystem-server": {
                    "command": "python",
                    "args": ["-m", "mcp_server_filesystem", "--root", "/data"],
                    "_managed_by": "mcp-config",
                },
                "external-server": {
                    "command": "node",
                    "args": ["server.js"],
                    # No _managed_by tag - external server
                },
            }
        }
        json.dump(config, f, indent=2)
        config_path = Path(f.name)

    print(f"Created temporary config at: {config_path}\n")

    # Show current servers
    print("Current servers in config:")
    for name in config["mcpServers"]:
        managed = "_managed_by" in config["mcpServers"][name]
        status = "managed" if managed else "external"
        print(f"  • {name} ({status})")

    # Simulate pattern matching
    pattern = "checker*"
    print(f"\nPattern to match: '{pattern}'")

    managed_servers = [
        {"name": name, "type": "mcp-code-checker"}
        for name in config["mcpServers"]
        if "_managed_by" in config["mcpServers"][name]
    ]

    matched = find_matching_servers(managed_servers, pattern)
    print(f"Matched {len(matched)} managed server(s):")
    for server in matched:
        print(f"  • {server['name']}")

    print("\nUser would be prompted:")
    print(f"  About to remove {len(matched)} server(s). Continue? (y/N)")
    print("  (Use --force to skip this prompt)")

    print("\nAfter confirmation, servers would be removed and backup created.")

    # Clean up
    config_path.unlink()
    print(f"\nCleaned up temporary config")


def main() -> None:
    """Run all test demonstrations."""
    print("=" * 60)
    print("MCP-Config Wildcard Removal Feature Test")
    print("=" * 60)

    test_wildcard_functions()
    test_cli_example()
    simulate_removal_workflow()

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
