"""
Quick demo of the wildcard removal feature for mcp-config.

This shows the key improvements:
1. Support for wildcard patterns (*, ?, [seq])
2. Batch removal of matching servers
3. Safety features (confirmation prompt, --force flag)
4. Requirement for explicit --client when using wildcards
"""

# Example commands that are now supported:

print("=== MCP-Config Wildcard Removal Feature Demo ===\n")

print("NEW SUPPORTED COMMANDS:\n")

commands = [
    (
        "Remove all checker servers:",
        "mcp-config remove 'checker*' --client claude-desktop",
    ),
    (
        "Remove dev servers from VSCode:",
        "mcp-config remove '*-dev' --client vscode-workspace",
    ),
    (
        "Skip confirmation with --force:",
        "mcp-config remove 'test-*' --client claude-desktop --force",
    ),
    (
        "Preview with dry-run:",
        "mcp-config remove 'checker*' --client claude-desktop --dry-run",
    ),
    (
        "Remove from all VSCode configs:",
        "mcp-config remove '*-old' --client vscode --force",
    ),
]

for desc, cmd in commands:
    print(f"{desc}")
    print(f"  $ {cmd}\n")

print("\nKEY FEATURES:\n")

print("1. Wildcard Support:")
print("   - '*' matches any sequence of characters")
print("   - '?' matches any single character")
print("   - '[seq]' matches any character in seq")
print("   - '[!seq]' matches any character not in seq\n")

print("2. Safety Features:")
print("   - Shows list of servers to be removed before proceeding")
print("   - Requires confirmation (y/N) for multiple removals")
print("   - Use --force to skip confirmation")
print("   - Creates backup before removal (use --no-backup to skip)\n")

print("3. Client Requirement:")
print("   - When using wildcards, --client must be explicitly specified")
print("   - This prevents accidental removal from wrong client")
print(
    "   - Single server removal still works without --client (defaults to claude-desktop)\n"
)

print("4. Example Workflow:")
print("   $ mcp-config remove 'checker*' --client claude-desktop")
print("   ")
print("   About to remove 3 server(s):")
print("     • checker-main (mcp-code-checker) - claude-desktop")
print("     • checker-dev (mcp-code-checker) - claude-desktop")
print("     • checker-test (mcp-code-checker) - claude-desktop")
print("   ")
print("   This action cannot be undone (backup will be created).")
print("   Do you want to proceed? (y/N): y")
print("   ")
print("   ✓ Successfully removed 3 server(s):")
print("     • checker-main (claude-desktop)")
print("     • checker-dev (claude-desktop)")
print("     • checker-test (claude-desktop)")
print("   Backup created: /path/to/backup.json\n")

print("=== Demo Complete ===")
